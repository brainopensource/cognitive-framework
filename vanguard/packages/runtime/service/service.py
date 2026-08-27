"""Core RuntimeService implementing durable commands, event streaming, and approval coordination.

Owning contract: REQ-CLI-002, S6B-SA-001, DEC-6B-012, ADR-0062.
"""

from __future__ import annotations

import json
import queue
import threading
import time
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence

from ...adapters.stores.event_store import SqliteEventStore
from ...domain.ledger.events import VALID_SCOPES, EventEnvelope, parse_event_envelope
from ...domain.primitives.primitives import uuidv7
from ...domain.evidence.claim import Claim, ClaimError, parse_claim
from ...domain.wire.contracts import parse_wire
from ...ports.event_store import EventRange, EventStorePort, Result
from ..checkpoints import Checkpoint, CheckpointManager
from ..evaluation_listener import EvaluationListener
from ..explain import explain_artifact
from ..governance.approvals import (
    ApprovalAuthority,
    ApprovalChallenge,
    ApprovalDecision,
    ApprovalFlow,
    OperatorSigner,
)
from .contract import (
    APPROVAL_DECISION_ALLOWED_FIELDS,
    APPROVAL_DECISION_REQUIRED_FIELDS,
    ConflictError,
    ContractError,
    NotAvailableError,
    NotFoundError,
    PermissionDeniedError,
    UnauthenticatedError,
    error_code_for_exception,
    service_error,
    validate_command,
    validate_frame_envelope,
)
from .inbox import ServiceInboxStore


#: How long `Cancel` waits for a worker to settle before recording the outcome
#: as undeterminable rather than asserting a terminal state it did not observe.
CANCELLATION_GRACE_SECONDS = 10.0


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.")
        + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
    )


class CancellationRequested(Exception):
    """Raised inside a worker when the operator cancelled the run.

    Distinct from an ordinary failure: cancellation is an *intended* terminal
    state and must never be recorded as `failed`, nor an exception recorded as
    `completed`.
    """


@dataclass
class ActiveRunContext:
    run_id: str
    manifest_path: str
    repo_path: str
    brief: str
    thread: threading.Thread | None = None
    event_subscribers: list[queue.Queue[dict[str, Any] | None]] = field(default_factory=list)
    pending_approval: ApprovalChallenge | None = None
    approval_response_queue: queue.Queue[ApprovalDecision | None] = field(
        default_factory=queue.Queue
    )
    #: Cooperative cancellation token. An `Event` rather than a bool so the
    #: worker can both poll it at turn boundaries and block on it, and so the
    #: flag is visible across threads without the caller holding a lock.
    cancel_event: threading.Event = field(default_factory=threading.Event)
    status: str = "running"
    resumed_from_digest: str = ""
    lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def is_cancelled(self) -> bool:
        return self.cancel_event.is_set()

    def raise_if_cancelled(self) -> None:
        """Called by the worker at every turn boundary and before each effect."""
        if self.cancel_event.is_set():
            raise CancellationRequested(f"run {self.run_id} was cancelled")


@dataclass(frozen=True, slots=True)
class _EventView:
    """Envelope-shaped read of a stored event row, for the explain reducer."""

    record: Mapping[str, Any]

    @property
    def payload(self) -> Mapping[str, Any]:
        payload = self.record.get("payload")
        return payload if isinstance(payload, Mapping) else {}

    @property
    def occurred_at(self) -> Any:
        return self.record.get("occurredAt")

    @property
    def seq(self) -> Any:
        return self.record.get("seq")


class RuntimeService:
    """Generic durable runtime service engine."""

    def __init__(
        self,
        inbox_store: ServiceInboxStore | None = None,
        *,
        event_store: EventStorePort | None = None,
        authority: ApprovalAuthority | None = None,
        harness_runner: Callable[..., Any] | None = None,
        claims: Sequence[Mapping[str, Any]] = (),
        blobs: Any | None = None,
    ) -> None:
        self.store = inbox_store or ServiceInboxStore(":memory:")
        if event_store is not None:
            self.event_store = event_store
        elif inbox_store is not None and inbox_store.db_path != ":memory:":
            self.event_store = SqliteEventStore(inbox_store.db_path)
        else:
            self.event_store = SqliteEventStore(":memory:")
        #: Evidence claims available to `vg why` (`S8-A-05`). Injected rather
        #: than read from disk: the service composes no store of its own.
        self.claims: tuple[Mapping[str, Any], ...] = tuple(claims)
        self.authority = authority or ApprovalAuthority()
        self._harness_runner = harness_runner
        self._active_runs: dict[str, ActiveRunContext] = {}
        self._lock = threading.Lock()
        #: Serializes sequence allocation and canonical append. Held only across
        #: the store write, never across subscriber notification, so a slow
        #: consumer cannot stall the writer.
        self._write_lock = threading.Lock()
        self._evaluation_store = _ServiceEventStore(self)
        self._evaluation_listener = EvaluationListener(self._evaluation_store)
        #: Checkpoint/resume need somewhere to put a folded state. A file-backed
        #: service gets one beside its database; a purely in-memory service does
        #: not, and then the capability is *unavailable* and says so rather than
        #: recording an empty checkpoint that resume cannot use.
        self._blobs = blobs if blobs is not None else _default_blob_store(self.store.db_path)
        self._checkpoints = CheckpointManager(self._blobs) if self._blobs is not None else None

    def execute_command(self, frame: Mapping[str, Any]) -> dict[str, Any]:
        """Execute a validated command frame and return a response frame."""
        # 1. Outer frame envelope validation
        try:
            validate_frame_envelope(frame)
        except ContractError as exc:
            frame_id = str(frame.get("frameId", uuidv7())) if isinstance(frame, Mapping) else uuidv7()
            return {
                "version": "vg.4",
                "frameType": "error",
                "frameId": uuidv7(),
                "inReplyTo": frame_id,
                "error": service_error(exc.code, exc.message, retryable=exc.retryable),
            }

        cmd_raw = frame.get("command")
        frame_id = str(frame.get("frameId", uuidv7()))

        # 2. Command validation
        try:
            val_cmd = validate_command(cmd_raw)
        except ContractError as exc:
            cmd_id = str(cmd_raw.get("commandId", uuidv7())) if isinstance(cmd_raw, Mapping) else uuidv7()
            run_id = str(cmd_raw.get("runId", "")) if isinstance(cmd_raw, Mapping) else ""
            err_receipt = {
                "commandId": cmd_id,
                "status": "error",
                "runId": run_id,
                "error": service_error(exc.code, exc.message, retryable=exc.retryable),
                "detail": exc.message,
            }
            return {
                "version": "vg.4",
                "frameType": "receipt",
                "frameId": uuidv7(),
                "inReplyTo": frame_id,
                "receipt": err_receipt,
            }

        name = val_cmd.name
        command_id = val_cmd.command_id
        idempotency_key = val_cmd.idempotency_key
        run_id = val_cmd.run_id
        actor = val_cmd.actor
        payload = dict(val_cmd.payload)
        now = _utc_now()

        # 3. Check idempotency inbox
        is_new, prior_receipt = self.store.record_command(
            command_id, idempotency_key, name, run_id, payload, actor=actor, now=now
        )
        if not is_new and prior_receipt is not None:
            return {
                "version": "vg.4",
                "frameType": "receipt",
                "frameId": uuidv7(),
                "inReplyTo": frame_id,
                "receipt": prior_receipt,
            }

        handler = getattr(self, f"_cmd_{name}", None)
        if handler is None:
            err_receipt = {
                "commandId": command_id,
                "status": "error",
                "runId": run_id,
                "error": service_error("invalid_request", f"unknown command {name!r}", retryable=False),
                "detail": f"unknown command {name!r}",
            }
            self.store.complete_command(command_id, "error", err_receipt, now=_utc_now())
            return {
                "version": "vg.4",
                "frameType": "receipt",
                "frameId": uuidv7(),
                "inReplyTo": frame_id,
                "receipt": err_receipt,
            }

        try:
            self._check_cas(run_id, payload)
            result = handler(run_id=run_id, payload=payload, actor=actor, command_id=command_id)
            receipt = {
                "commandId": command_id,
                "status": "completed",
                "runId": run_id,
                "result": result,
            }
            self.store.complete_command(command_id, "completed", receipt, now=_utc_now())
            return {
                "version": "vg.4",
                "frameType": "receipt",
                "frameId": uuidv7(),
                "inReplyTo": frame_id,
                "receipt": receipt,
            }
        except Exception as exc:
            code = error_code_for_exception(exc)
            retryable = getattr(exc, "retryable", code in ("conflict", "rate_limited", "not_available"))
            err_receipt = {
                "commandId": command_id,
                "status": "error",
                "runId": run_id,
                "error": service_error(code, str(exc), retryable=retryable),
                "detail": str(exc),
            }
            self.store.complete_command(command_id, "error", err_receipt, now=_utc_now())
            return {
                "version": "vg.4",
                "frameType": "receipt",
                "frameId": uuidv7(),
                "inReplyTo": frame_id,
                "receipt": err_receipt,
            }

    def _check_cas(self, run_id: str, payload: Mapping[str, Any]) -> None:
        if "expectedSeq" in payload and payload["expectedSeq"] is not None:
            expected = int(payload["expectedSeq"])
            current = self.get_latest_seq(run_id)
            if expected != current:
                raise ConflictError(
                    f"CAS conflict on run {run_id!r}: expectedSeq {expected} != current sequence {current}"
                )

    def get_latest_seq(self, run_id: str) -> int:
        """Highest committed sequence for a run, from the canonical store only."""
        res = self.event_store.read(EventRange(run_id=run_id))
        if res.ok and res.value:
            return int(res.value[-1].seq)
        return 0

    # -- Command Handlers ----------------------------------------------------

    def _cmd_StartRun(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        manifest_path = str(payload.get("manifestPath", ""))
        repo_path = str(payload.get("repoPath", "."))
        brief = str(payload.get("brief", ""))

        if not manifest_path or not brief:
            raise ContractError("invalid_request", "StartRun requires manifestPath and brief")

        with self._lock:
            if run_id in self._active_runs:
                raise ConflictError(f"run {run_id} is already active")
            ctx = ActiveRunContext(
                run_id=run_id,
                manifest_path=manifest_path,
                repo_path=repo_path,
                brief=brief,
            )
            self._active_runs[run_id] = ctx

        self.store.set_run_state(run_id, manifest_path, repo_path, "running", now=_utc_now())
        now = _utc_now()
        # Liveness producer event
        self.publish_event(
            run_id,
            {
                "eventId": uuidv7(),
                "scope": "run",
                "occurredAt": now,
                "principal": actor,
                "runId": run_id,
                "payload": {"kind": "Heartbeat", "producer": "RuntimeService"},
            },
        )

        # Spawn execution thread if runner provided or manifest exists
        if self._harness_runner is not None or (Path(manifest_path).exists() and Path(manifest_path).is_file()):
            t = threading.Thread(
                target=self._run_worker_thread,
                args=(ctx, payload),
                daemon=True,
            )
            ctx.thread = t
            t.start()

        return {
            "runId": run_id,
            "status": "started",
            "acceptedAt": now,
            "manifestPath": manifest_path,
            "repoPath": repo_path,
        }

    def _cmd_GetRun(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        state = self.store.get_run_state(run_id)
        if state is None:
            raise NotFoundError(f"run {run_id} not found")
        events = self._load_events(run_id, after_seq=0)
        as_of_seq = str(events[-1]["seq"]) if events else "0"
        return {
            "runId": run_id,
            "status": state["status"],
            "eventCount": len(events),
            "asOfSeq": as_of_seq,
            "manifestPath": state["manifest_path"],
            "repoPath": state["repo_path"],
            "createdAt": state.get("created_at", ""),
            "updatedAt": state.get("updated_at", ""),
        }

    def _cmd_ListRuns(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        limit = int(payload.get("limit", 50))
        offset = int(payload.get("offset", 0))
        runs = self.store.list_runs(limit=limit, offset=offset)
        return {"runs": runs, "total": len(runs)}

    def _cmd_GetCapabilities(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        return {
            "api": "aether.capabilities/1",
            "serverVersion": "0.7.3.dev0",
            "wireVersions": ["vg.4"],
            "capabilities": {
                "run.start": {
                    "implementation": "available",
                    "authorization": "enabled",
                    "contract": "runtime-service/vg.4",
                },
                "run.get": {
                    "implementation": "available",
                    "authorization": "enabled",
                    "contract": "runtime-service/vg.4",
                },
                "run.list": {
                    "implementation": "available",
                    "authorization": "enabled",
                    "contract": "runtime-service/vg.4",
                },
                "run.stream": {
                    "implementation": "available",
                    "authorization": "enabled",
                    "contract": "runtime-service/vg.4",
                },
                "run.cancel": {
                    "implementation": "available",
                    "authorization": "enabled",
                    "contract": "runtime-service/vg.4",
                },
                "run.checkpoint": {
                    "implementation": "available",
                    "authorization": "enabled",
                    "contract": "runtime-service/vg.4",
                },
                "run.resume": {
                    "implementation": "available",
                    "authorization": "enabled",
                    "contract": "runtime-service/vg.4",
                },
                "approval.resolve": {
                    "implementation": "available",
                    "authorization": "enabled",
                    "contract": "runtime-service/vg.4",
                },
                "correction.record": {
                    "implementation": "available",
                    "authorization": "enabled",
                    "contract": "runtime-service/vg.4",
                },
                "artifact.explain": {
                    "implementation": "available",
                    "authorization": "enabled",
                    "contract": "runtime-service/vg.4",
                },
                "topology.execute": {
                    "implementation": "partial",
                    "authorization": "disabled",
                    "reasonCode": "milestone_gate_open",
                    "requires": ["M-7 accepted work package"],
                },
                "memory.retrieve": {
                    "implementation": "prototype",
                    "authorization": "disabled",
                    "reasonCode": "m8_not_authorized",
                    "requires": ["M-8 accepted work package"],
                },
            },
        }

    def _cmd_ResolveApproval(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        """Record a decision only after verifying it against its pending challenge.

        The challenge -- not the request body -- is the authority on what is
        being approved. A decision that arrives without one, or whose signature
        covers different material, appends no fact at all.
        """
        decision = _parse_strict_approval_decision(payload.get("decision"))
        challenge = self._require_pending_challenge(run_id, decision.approval_id)

        # Registered key. An unknown key ID is unauthenticated, not merely
        # invalid: the runtime holds public keys only and cannot mint one.
        if decision.key_id not in self.authority.verifying_keys:
            raise UnauthenticatedError(
                f"approval key {decision.key_id!r} is not registered with this runtime"
            )

        # Correspondence. The signature binds these digests; if they are not the
        # challenge's digests then a valid signature authorises something else.
        for field, got, want in (
            ("argsDigest", decision.args_digest, challenge.args_digest),
            ("descriptorDigest", decision.descriptor_digest, challenge.descriptor_digest),
            ("expiresAt", decision.expires_at, challenge.expires_at),
        ):
            if got != want:
                raise PermissionDeniedError(
                    f"approval {field} does not bind challenge {decision.approval_id}"
                )

        now = _utc_now()
        if now >= challenge.expires_at:
            raise PermissionDeniedError(f"approval {decision.approval_id} has expired")

        if not self.authority.verify(decision):
            raise PermissionDeniedError(
                f"approval {decision.approval_id} signature is not valid for key "
                f"{decision.key_id!r}"
            )

        with self._lock:
            ctx = self._active_runs.get(run_id)

        now = _utc_now()
        seq = self.publish_event(
            run_id,
            {
                "eventId": uuidv7(),
                "scope": "run",
                "occurredAt": now,
                "principal": actor,
                "runId": run_id,
                "payload": {
                    "kind": "ApprovalResolved",
                    "decision": {
                        "approvalId": decision.approval_id,
                        "resolution": decision.resolution,
                        "reviewer": decision.reviewer,
                        "argsDigest": decision.args_digest,
                        "descriptorDigest": decision.descriptor_digest,
                        "expiresAt": decision.expires_at,
                        "signature": decision.signature,
                        "keyId": decision.key_id,
                    },
                },
            },
        )
        if ctx is not None:
            ctx.approval_response_queue.put(decision)
        return {"runId": run_id, "approvalId": decision.approval_id, "seq": seq, "status": "resolved"}

    def _cmd_Cancel(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        """Request cancellation, wait for the worker to settle, record the truth.

        Cancellation used to set an in-process boolean that the ordinary worker
        never read, so it could only unblock a waiting approval; a run could --
        and did -- complete after the service had already recorded it cancelled.
        The token is now observed by the worker, and the terminal fact is
        appended by whoever actually settles.
        """
        reason = str(payload.get("reason", "cancelled by operator"))
        with self._lock:
            ctx = self._active_runs.get(run_id)

        state = self.store.get_run_state(run_id)
        if ctx is None and state is None:
            raise NotFoundError(f"run {run_id} not found")

        # 1. Durable intent, before any attempt to interrupt.
        self.publish_event(
            run_id,
            {
                "eventId": uuidv7(),
                "scope": "run",
                "occurredAt": _utc_now(),
                "principal": actor,
                "runId": run_id,
                "payload": {"kind": "CancellationRequested", "reason": reason},
            },
        )

        if ctx is not None and ctx.thread is None:
            # A registered run with no worker (nothing was ever launched). It
            # settles immediately and deterministically.
            ctx.cancel_event.set()
            ctx.status = "cancelled"
            ctx.approval_response_queue.put(None)
            with self._lock:
                self._active_runs.pop(run_id, None)

        if ctx is None or ctx.thread is None:
            # Nothing is executing: settle it here and record the terminal fact.
            manifest = state["manifest_path"] if state else (ctx.manifest_path if ctx else "")
            repo = state["repo_path"] if state else (ctx.repo_path if ctx else ".")
            self.store.set_run_state(run_id, manifest, repo, "cancelled", now=_utc_now())
            self.publish_event(
                run_id,
                {
                    "eventId": uuidv7(),
                    "scope": "run",
                    "occurredAt": _utc_now(),
                    "principal": actor,
                    "runId": run_id,
                    "payload": {"kind": "RunCancelled", "reason": reason},
                },
            )
            return {"runId": run_id, "status": "cancelled", "settled": True}

        # 2. Cooperative interruption: set the token the worker polls, and
        #    unblock it if it is parked on an approval.
        ctx.cancel_event.set()
        ctx.approval_response_queue.put(None)

        # 3. Wait for the worker to append its own terminal fact.
        thread = ctx.thread
        if thread is not None:
            thread.join(timeout=CANCELLATION_GRACE_SECONDS)
        settled = thread is None or not thread.is_alive()

        if not settled:
            # Never claim a terminal state we did not observe.
            self.publish_event(
                run_id,
                {
                    "eventId": uuidv7(),
                    "scope": "run",
                    "occurredAt": _utc_now(),
                    "principal": actor,
                    "runId": run_id,
                    "payload": {
                        "kind": "CancellationUndeterminable",
                        "reason": reason,
                        "detail": (
                            f"worker did not settle within {CANCELLATION_GRACE_SECONDS}s"
                        ),
                    },
                },
            )
            return {"runId": run_id, "status": "cancelling", "settled": False}

        return {"runId": run_id, "status": ctx.status, "settled": True}

    def _cmd_RecordCorrection(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        correction = parse_wire("CorrectionRecord", payload.get("correction"))
        now = _utc_now()
        seq = self.publish_event(
            run_id,
            {
                "eventId": uuidv7(),
                "scope": "run",
                "occurredAt": now,
                "principal": actor,
                "runId": run_id,
                "payload": {"kind": "CorrectionRecorded", "correction": correction},
            },
        )
        return {"runId": run_id, "seq": seq, "status": "recorded"}

    def _cmd_Checkpoint(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        """Capture reconstructable state through the canonical checkpoint contract.

        The previous implementation stored ``state_json=None`` plus a ledger
        digest and called that a checkpoint. Nothing could be resumed from it,
        because nothing was in it -- a pointer to a state that was never
        captured is a dangling reference with a checkpoint's name on it.
        """
        state = self.store.get_run_state(run_id)
        if state is None:
            raise NotFoundError(f"run {run_id} not found")

        manager = self._checkpoint_manager()
        envelopes = self.canonical_envelopes(run_id)
        reconstruction = manager.reconstruct(envelopes)
        if reconstruction.state is None:
            raise NotAvailableError(
                f"run {run_id!r} has no foldable history to checkpoint"
            )

        checkpoint = manager.capture(reconstruction.state, required=True)
        if checkpoint is None:
            raise NotAvailableError(
                f"checkpoint capture was not stored for run {run_id!r}; "
                "retention or blob policy refused it"
            )

        seq = self.get_latest_seq(run_id)
        checkpoint_id = f"chk-{run_id}-{seq}"
        now = _utc_now()
        fact = checkpoint.to_fact()

        self.store.save_checkpoint(
            checkpoint_id, run_id, seq, checkpoint.state_digest,
            state_json=json.dumps(fact, sort_keys=True), now=now,
        )
        self.publish_event(
            run_id,
            {
                "eventId": uuidv7(),
                "scope": "run",
                "occurredAt": now,
                "principal": actor,
                "runId": run_id,
                "payload": {
                    "kind": "CheckpointRecorded",
                    "checkpointId": checkpoint_id,
                    "seq": str(seq),
                    "digest": checkpoint.state_digest,
                    "checkpoint": fact,
                },
            },
        )
        return {
            "runId": run_id,
            "status": state["status"],
            "checkpoint": checkpoint_id,
            "asOfSeq": str(seq),
            "digest": checkpoint.state_digest,
            "blobDigest": checkpoint.blob_digest,
            "eventCount": int(checkpoint.event_count),
        }

    def _cmd_Resume(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        """Reconstruct from durable history, verify, reconcile, and restart.

        Resume previously emitted ``RunResumed`` and flipped a mutable status
        row to ``"resumed"``. Nothing was verified, nothing was rebuilt, and no
        execution restarted -- the run reported a state it had not re-entered.
        """
        state = self.store.get_run_state(run_id)
        if state is None:
            raise NotFoundError(f"run {run_id} not found")

        checkpoint_id = payload.get("checkpointId")
        checkpoint = None
        if checkpoint_id:
            row = self.store.get_checkpoint(str(checkpoint_id))
            if row is None:
                raise NotFoundError(f"checkpoint {checkpoint_id} not found for run {run_id}")
            if row.get("run_id") != run_id:
                raise PermissionDeniedError(
                    f"checkpoint {checkpoint_id} belongs to another run"
                )
            raw_state = row.get("state_json")
            if not raw_state:
                raise NotAvailableError(
                    f"checkpoint {checkpoint_id} holds no reconstructable state"
                )
            checkpoint = Checkpoint.from_fact(json.loads(raw_state))

        manager = self._checkpoint_manager()
        envelopes = self.canonical_envelopes(run_id)
        # verify=True runs the cold fold as well and compares digests, so a
        # checkpoint that is not a prefix of this history loses to the events.
        reconstruction = manager.reconstruct(envelopes, checkpoint=checkpoint, verify=True)
        if reconstruction.state is None:
            raise NotAvailableError(f"run {run_id!r} could not be reconstructed")

        open_effects = self._reconcile_open_effects(reconstruction.state)
        now = _utc_now()
        seq = self.publish_event(
            run_id,
            {
                "eventId": uuidv7(),
                "scope": "run",
                "occurredAt": now,
                "principal": actor,
                "runId": run_id,
                "payload": {
                    "kind": "RunRecovered",
                    "checkpointId": checkpoint_id,
                    "asOfSeq": str(self.get_latest_seq(run_id)),
                    "stateDigest": reconstruction.state_digest,
                    "capability": reconstruction.capability,
                    "verification": reconstruction.verification,
                    "eventsReplayed": int(reconstruction.events_replayed),
                    "openEffects": list(open_effects),
                    **({"fallbackReason": reconstruction.fallback_reason}
                       if reconstruction.fallback_reason else {}),
                },
            },
        )

        restarted = self._restart_from_state(run_id, state, reconstruction)
        # "resumed" means the lineage was re-entered from verified durable
        # state; it does not by itself claim a worker is executing. `restarted`,
        # `capability` and `verification` carry that distinction explicitly
        # rather than letting one word imply all three.
        status = "running" if restarted else "resumed"
        self.store.set_run_state(
            run_id, state["manifest_path"], state["repo_path"], status, now=now,
        )
        return {
            "runId": run_id,
            "status": status,
            "asOfSeq": str(seq),
            "stateDigest": reconstruction.state_digest,
            "capability": reconstruction.capability,
            "verification": reconstruction.verification,
            "eventsReplayed": int(reconstruction.events_replayed),
            "openEffects": list(open_effects),
            "restarted": restarted,
        }

    def _checkpoint_manager(self) -> Any:
        """The service's checkpoint manager, built once against a durable blob store."""
        if self._checkpoints is None:
            raise NotAvailableError(
                "no blob store configured; checkpoint and resume are unavailable"
            )
        return self._checkpoints

    @staticmethod
    def _reconcile_open_effects(state: Any) -> tuple[str, ...]:
        """Effects that were started but never settled before the interruption.

        Reported, never silently retried: a privileged effect whose outcome is
        unknown is `UNDETERMINABLE`, and blind re-execution is how an
        at-least-once transport becomes an at-least-twice side effect.
        """
        effects = getattr(state, "effects", None)
        if not effects:
            return ()
        open_ids: list[str] = []
        for effect_id, record in dict(effects).items():
            status = str(getattr(record, "status", "") or "").lower()
            if status in ("started", "intent", "pending", "in_flight"):
                open_ids.append(str(effect_id))
        return tuple(sorted(open_ids))

    def _restart_from_state(
        self, run_id: str, state: Mapping[str, Any], reconstruction: Any
    ) -> bool:
        """Re-enter execution from reconstructed state, when execution is possible.

        Returns whether a worker was actually started. A run that cannot be
        restarted stays `recovered` rather than claiming `running`: the state was
        rebuilt and that is a real, useful outcome, but it is not execution.
        """
        manifest_path = str(state.get("manifest_path", ""))
        if self._harness_runner is None and not (
            manifest_path and Path(manifest_path).is_file()
        ):
            return False

        with self._lock:
            if run_id in self._active_runs:
                raise ConflictError(f"run {run_id} is already active")
            ctx = ActiveRunContext(
                run_id=run_id,
                manifest_path=manifest_path,
                repo_path=str(state.get("repo_path", ".")),
                brief=str(state.get("brief", "") or ""),
                resumed_from_digest=reconstruction.state_digest,
            )
            self._active_runs[run_id] = ctx

        thread = threading.Thread(
            target=self._run_worker_thread, args=(ctx, dict(state)), daemon=True
        )
        ctx.thread = thread
        thread.start()
        return True

    def _cmd_ExplainArtifact(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        artifact_id = str(payload.get("artifactId", ""))
        if not artifact_id:
            raise ContractError("invalid_request", "ExplainArtifact requires artifactId")
        explanation = explain_artifact(
            artifact_id,
            events=self._explain_events(run_id),
            claims=self._claims_for(artifact_id),
            substrate_profile=payload.get("substrateProfile"),
        )
        return {
            "runId": run_id,
            "artifact": artifact_id,
            "explanation": explanation.to_dict(),
        }

    def _require_pending_challenge(self, run_id: str, approval_id: str) -> ApprovalChallenge:
        """The unresolved challenge this decision claims to answer.

        Read from durable history rather than from in-process state, so a
        decision that arrives after a restart is still verified against the
        challenge that was actually issued -- and a decision naming a challenge
        nobody issued finds nothing.
        """
        pending: dict[str, ApprovalChallenge] = {}
        for record in self._load_events(run_id):
            payload = record.get("payload")
            if not isinstance(payload, Mapping):
                continue
            kind = payload.get("kind")
            if kind == "ApprovalRequested":
                body = payload.get("challenge") if isinstance(
                    payload.get("challenge"), Mapping) else payload
                try:
                    challenge = ApprovalChallenge(
                        approval_id=str(body["approvalId"]),
                        process_id=str(body.get("processId", "")),
                        action=str(body["action"]),
                        normalized_diff=str(body.get("normalizedDiff", "")),
                        args_digest=str(body["argsDigest"]),
                        descriptor_digest=str(body["descriptorDigest"]),
                        principal=str(body.get("principal", "operator")),
                        expires_at=str(body["expiresAt"]),
                    )
                except (KeyError, TypeError):
                    continue
                pending[challenge.approval_id] = challenge
            elif kind == "ApprovalResolved":
                body = payload.get("decision") if isinstance(
                    payload.get("decision"), Mapping) else payload
                if isinstance(body, Mapping):
                    pending.pop(str(body.get("approvalId", "")), None)

        challenge = pending.get(approval_id)
        if challenge is None:
            raise NotFoundError(
                f"no pending approval {approval_id!r} for run {run_id!r}"
            )
        return challenge

    def _explain_events(self, run_id: str) -> list[Any]:
        """Ledger events for the run, as envelope-shaped objects."""
        return [_EventView(record) for record in self._load_events(run_id)]

    def _claims_for(self, artifact_id: str) -> list[Claim]:
        """Claims naming this artifact. Unparseable claims are skipped, not guessed."""
        found: list[Claim] = []
        for raw in self.claims:
            try:
                claim = parse_claim(raw)
            except ClaimError:
                continue
            if claim.subject == artifact_id:
                found.append(claim)
        return found

    # -- Event Storage & Streaming -------------------------------------------

    def _load_events(self, run_id: str, after_seq: int = 0) -> list[dict[str, Any]]:
        """Read the canonical history. There is no second history to fall back to.

        The previous fallback to the inbox on an empty canonical result made
        truth state-dependent: the same query answered from a different store
        depending on whether the first one happened to be empty.
        """
        res = self.event_store.read(EventRange(run_id=run_id, after_seq=str(after_seq)))
        if not res.ok:
            raise NotAvailableError(
                f"canonical event store unavailable for run {run_id!r}: "
                f"{getattr(res, 'error', 'unknown store error')}"
            )
        return [env.to_dict() for env in (res.value or ())]

    def canonical_envelopes(self, run_id: str) -> list[EventEnvelope]:
        """Ordered canonical envelopes for a run, unmodified."""
        res = self.event_store.read(EventRange(run_id=run_id))
        if not res.ok:
            raise NotAvailableError(f"canonical event store unavailable for run {run_id!r}")
        return list(res.value or ())

    def stream_events(
        self, run_id: str, after_seq: int = 0
    ) -> Iterator[dict[str, Any]]:
        """Yield historical events followed by live events until terminal with gap detection."""
        last_seq = after_seq
        q: queue.Queue[dict[str, Any] | None] = queue.Queue()

        # 1. Subscribe to live queue first if run is active
        with self._lock:
            ctx = self._active_runs.get(run_id)
            if ctx is not None:
                ctx.event_subscribers.append(q)

        # 2. Replay historical events from store
        historical = self._load_events(run_id, after_seq=after_seq)
        for evt in historical:
            seq_val = int(evt.get("seq", 0))
            if seq_val <= last_seq:
                continue
            last_seq = seq_val
            yield {
                "version": "vg.4",
                "frameType": "event",
                "frameId": uuidv7(),
                "event": evt,
            }

        if ctx is None:
            return

        # 3. Stream live queue events, deduplicating against replayed events
        try:
            while True:
                item = q.get()
                if item is None:
                    break
                seq_val = int(item.get("seq", 0))
                if seq_val <= last_seq:
                    continue
                last_seq = seq_val
                yield {
                    "version": "vg.4",
                    "frameType": "event",
                    "frameId": uuidv7(),
                    "event": item,
                }
        finally:
            with self._lock:
                if ctx is not None and q in ctx.event_subscribers:
                    ctx.event_subscribers.remove(q)

    def publish_event(self, run_id: str, event_envelope: Mapping[str, Any]) -> int:
        """Append a service-authored fact to the one canonical history."""
        now = _utc_now()
        evt = dict(event_envelope)
        if not evt.get("occurredAt"):
            evt["occurredAt"] = now
        if not evt.get("runId"):
            evt["runId"] = run_id
        return self._append_canonical(run_id, _envelope_from_service_event(run_id, evt))

    def _append_canonical(self, run_id: str, envelope: EventEnvelope) -> int:
        """Allocate a sequence and commit, or raise having changed nothing.

        Sequence allocation and append happen under one lock and one store, so
        there is exactly one event truth. Previously the inbox allocated the
        sequence, the canonical store was written separately, and its `Result`
        was discarded -- so a canonical failure still returned a sequence and
        still notified subscribers, who could observe an event that is absent
        from history. Notification now happens strictly after commit: losing a
        notification costs a subscriber one cursor resume, while publishing an
        uncommitted event costs the ledger its meaning.
        """
        with self._write_lock:
            next_seq = self.get_latest_seq(run_id) + 1
            committed = replace(envelope, seq=str(next_seq))
            result = self.event_store.append([committed])
            if not result.ok:
                raise NotAvailableError(
                    f"canonical event append failed for run {run_id!r}: "
                    f"{getattr(result, 'error', 'unknown store error')}"
                )

        record = committed.to_dict()
        with self._lock:
            ctx = self._active_runs.get(run_id)
            if ctx is not None:
                for sub in list(ctx.event_subscribers):
                    sub.put(record)

        payload = committed.payload
        if isinstance(payload, Mapping) and payload.get("kind") == "EpisodeCompleted":
            self._evaluation_listener.process_envelope(committed)
        return next_seq

    # -- Internal Execution --------------------------------------------------

    def _handle_approver_callback(self, ctx: ActiveRunContext, challenge: Any) -> Any:
        ctx.pending_approval = challenge
        now = _utc_now()
        self.publish_event(
            ctx.run_id,
            {
                "eventId": uuidv7(),
                "scope": "run",
                "occurredAt": now,
                "principal": "runtime",
                "runId": ctx.run_id,
                "payload": {
                    "kind": "ApprovalRequested",
                    "approvalId": getattr(challenge, "approval_id", uuidv7()),
                    "processId": getattr(challenge, "process_id", ""),
                    "action": getattr(challenge, "action", ""),
                    # The material the reviewer's signature will cover. Without
                    # it a challenge cannot be reconstructed from history, and
                    # a decision arriving after a restart could not be checked.
                    "normalizedDiff": getattr(challenge, "normalized_diff", ""),
                    "argsDigest": getattr(challenge, "args_digest", ""),
                    "descriptorDigest": getattr(challenge, "descriptor_digest", ""),
                    "principal": getattr(challenge, "principal", "operator"),
                    "expiresAt": getattr(challenge, "expires_at", ""),
                },
            },
        )
        decision = ctx.approval_response_queue.get()
        if decision is None:
            raise RuntimeError("approval aborted: run was cancelled or interrupted")
        return decision

    def _run_worker_thread(self, ctx: ActiveRunContext, payload: Mapping[str, Any]) -> None:
        run_status = "completed"
        try:
            ctx.raise_if_cancelled()
            if self._harness_runner is not None:
                self._harness_runner(ctx, self)
            else:
                from ..compose import TaskContext
                from ..root import Runtime

                manifest_path = ctx.manifest_path
                repo_path = ctx.repo_path
                profile_id = str(payload.get("profileId", "code-default"))
                model = payload.get("model")

                task_context = TaskContext(
                    brief=ctx.brief,
                    repo_path=Path(repo_path),
                    run_id=ctx.run_id,
                    episode_id=str(payload.get("episodeId") or uuidv7()),
                    principal=str(payload.get("actor", "operator")),
                )

                Runtime.execute_profiled(
                    manifest_path=manifest_path,
                    task_context=task_context,
                    profile_id=profile_id,
                    model=model,
                    store=self._evaluation_store,
                    approver=lambda challenge: self._handle_approver_callback(ctx, challenge),
                )
            ctx.raise_if_cancelled()
            now = _utc_now()
            seq = self.get_latest_seq(ctx.run_id)
            digest_res = self.event_store.digest(ctx.run_id)
            digest = digest_res.value if digest_res.ok and digest_res.value else ""
            self.publish_event(
                ctx.run_id,
                {
                    "eventId": uuidv7(),
                    "scope": "run",
                    "occurredAt": now,
                    "principal": "runtime",
                    "runId": ctx.run_id,
                    "payload": {
                        "kind": "RunCompleted",
                        "finalSeq": str(seq),
                        "digest": digest,
                    },
                },
            )
            run_status = "completed"
        except CancellationRequested as exc:
            # An intended terminal state, not a failure.
            run_status = "cancelled"
            self.publish_event(
                ctx.run_id,
                {
                    "eventId": uuidv7(),
                    "scope": "run",
                    "occurredAt": _utc_now(),
                    "principal": "runtime",
                    "runId": ctx.run_id,
                    "payload": {"kind": "RunCancelled", "reason": str(exc)},
                },
            )
        except Exception as exc:
            # An exception is never a completion.
            run_status = "cancelled" if ctx.is_cancelled else "failed"
            kind = "RunCancelled" if ctx.is_cancelled else "RunFailed"
            body = (
                {"kind": kind, "reason": f"cancelled during: {exc}"}
                if ctx.is_cancelled
                else {"kind": kind, "error": str(exc)}
            )
            self.publish_event(
                ctx.run_id,
                {
                    "eventId": uuidv7(),
                    "scope": "run",
                    "occurredAt": _utc_now(),
                    "principal": "runtime",
                    "runId": ctx.run_id,
                    "payload": body,
                },
            )
        finally:
            ctx.status = run_status
            self.store.set_run_state(
                ctx.run_id, ctx.manifest_path, ctx.repo_path, run_status, now=_utc_now()
            )
            with self._lock:
                for sub in ctx.event_subscribers:
                    sub.put(None)
                self._active_runs.pop(ctx.run_id, None)

    @staticmethod
    def _error_frame(frame_id: str, code: str, message: str) -> dict[str, Any]:
        return {
            "version": "vg.4",
            "frameType": "error",
            "frameId": frame_id,
            "error": {"code": code, "message": message},
        }


def _parse_strict_approval_decision(raw: Any) -> ApprovalDecision:
    """Parse a wire decision with no defaulted field.

    Every previous default here was a forgery primitive: a caller who omitted
    ``signature`` got ``"dummy-sig-approved"``, and one who omitted a digest got
    a zero digest that matched nothing and was checked against nothing. A
    missing field is now ``invalid_request``.
    """
    if not isinstance(raw, Mapping):
        raise ContractError("invalid_request", "ResolveApproval requires a decision object")

    missing = [f for f in APPROVAL_DECISION_REQUIRED_FIELDS if not str(raw.get(f, "")).strip()]
    if missing:
        raise ContractError(
            "invalid_request",
            f"approval decision is missing required field(s): {', '.join(sorted(missing))}",
        )
    unknown = set(raw) - set(APPROVAL_DECISION_ALLOWED_FIELDS)
    if unknown:
        raise ContractError(
            "invalid_request",
            f"approval decision has unknown field(s): {', '.join(sorted(unknown))}",
        )

    resolution = str(raw["resolution"])
    if resolution not in ("approved", "rejected"):
        raise ContractError(
            "invalid_request", f"approval resolution {resolution!r} is not approved|rejected"
        )

    return ApprovalDecision(
        approval_id=str(raw["approvalId"]),
        resolution=resolution,
        reviewer=str(raw["reviewer"]),
        args_digest=str(raw["argsDigest"]),
        descriptor_digest=str(raw["descriptorDigest"]),
        expires_at=str(raw["expiresAt"]),
        key_id=str(raw["keyId"]),
        signature=str(raw["signature"]),
    )


def _default_blob_store(db_path: Any) -> Any:
    """A blob store beside the service database, when the service is durable.

    An in-memory service gets ``None``: checkpoints would have nowhere to live,
    and a checkpoint that points at bytes nobody kept is the dangling reference
    the artifact layer refuses to emit.
    """
    if db_path in (None, ":memory:"):
        return None
    try:
        from ...adapters.stores.blob_store import FileBlobStore

        return FileBlobStore(Path(str(db_path)).resolve().parent / "blobs")
    except Exception:  # noqa: BLE001 - absence degrades a capability, not the run
        return None


def _canonical_scope(has_run: bool, has_episode: bool) -> str:
    """The scope the canonical reader will accept for a service-authored fact.

    The domain's scope rules are conditional on identity, not on topic:

    ==============  ==============  ================
    scope           runId           episodeId
    ==============  ==============  ================
    ``episode``     required        required
    ``recovery``    required        forbidden
    ``governance``  forbidden       forbidden
    ``evolution``   forbidden       forbidden
    ==============  ==============  ================

    Every service fact is *about a run* and therefore carries a ``runId``, so
    only ``episode`` and ``recovery`` are admissible. The service previously
    wrote ``scope: "run"``, which is not a scope at all -- so each of its own
    events failed to parse on read and the old inbox fallback silently served
    them from the other store. That is exactly the state-dependent truth this
    package removes.
    """
    if has_run and has_episode:
        return "episode"
    if has_run:
        return "recovery"
    return "governance"


def _envelope_from_service_event(run_id: str, event: Mapping[str, Any]) -> EventEnvelope:
    payload = event.get("payload")
    if not isinstance(payload, Mapping):
        payload = {}
    now = str(event.get("occurredAt") or _utc_now())
    raw_episode = event.get("episodeId")
    episode_id = raw_episode if isinstance(raw_episode, str) and raw_episode else None
    resolved_run = str(event.get("runId") or run_id)
    raw_scope = str(event.get("scope") or "")
    scope = (
        raw_scope
        if raw_scope in VALID_SCOPES
        else _canonical_scope(bool(resolved_run), episode_id is not None)
    )
    return EventEnvelope(
        schema_version=str(event.get("schemaVersion", "vg.4")),
        event_id=str(event.get("eventId") or uuidv7()),
        scope=scope,
        seq=str(event.get("seq") or "0"),
        occurred_at=now,
        recorded_at=str(event.get("recordedAt") or now),
        principal=str(event.get("principal") or "runtime"),
        principal_role=str(event.get("principalRole") or "operator"),
        tenant_id=str(event.get("tenantId") or "tenant-default"),
        owner_id=str(event.get("ownerId") or "owner-platform"),
        confidentiality=str(event.get("confidentiality") or "internal"),
        retention_class=str(event.get("retentionClass") or "standard"),
        trainability=str(event.get("trainability") or "prohibited"),
        redaction_status=str(event.get("redactionStatus") or "none"),
        payload=dict(payload),
        # `governance`/`evolution` forbid a run identity; `episode`/`recovery`
        # require one. Only `episode` may carry an episode identity.
        run_id=resolved_run if scope in ("episode", "recovery") else None,
        episode_id=episode_id if scope == "episode" else None,
        trace_id=str(event.get("traceId") or "trace-service"),
        span_id=str(event.get("spanId") or "span-service"),
    )


class _ServiceEventStore(EventStorePort):
    """The runtime's view of the service's canonical store.

    Envelopes arrive here already canonical -- the runtime's own
    ``mhf.event/2`` values, carrying tenant, project, lineage, causation,
    idempotency, trace and authority provenance. They are persisted *unchanged*
    apart from the service-allocated sequence.

    This previously round-tripped every envelope through
    ``publish_event -> to_dict -> _envelope_from_service_event``, whose
    substituted defaults (``tenant-default``, ``owner-platform``,
    ``trace-service``, ``episode``) silently replaced exactly the fields that
    make an event attributable. The service is a transport for the runtime's
    facts, not a second author of them.
    """

    def __init__(self, service: RuntimeService) -> None:
        self._service = service

    def append(self, events: Sequence[EventEnvelope]) -> Result[None]:
        for envelope in events:
            run_id = envelope.run_id or ""
            try:
                self._service._append_canonical(run_id, envelope)
            except Exception as exc:  # noqa: BLE001 - reported through Result
                return Result.fail("unavailable", f"canonical append rejected: {exc}")
        return Result.success(None)

    def read(self, range_query: EventRange | None = None) -> Result[Sequence[EventEnvelope]]:
        return self._service.event_store.read(range_query)

    def digest(self, run_id: str | None = None) -> Result[str]:
        return self._service.event_store.digest(run_id)

    def count(self, run_id: str | None = None) -> int:
        return self._service.event_store.count(run_id)


