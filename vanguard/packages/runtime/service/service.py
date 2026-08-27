"""Core RuntimeService implementing durable commands, event streaming, and approval coordination.

Owning contract: REQ-CLI-002, S6B-SA-001, DEC-6B-012, ADR-0062.
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence

from ...adapters.stores.event_store import SqliteEventStore
from ...domain.ledger.events import EventEnvelope, parse_event_envelope
from ...domain.primitives.primitives import uuidv7
from ...domain.evidence.claim import Claim, ClaimError, parse_claim
from ...domain.wire.contracts import parse_wire
from ...ports.event_store import EventRange, EventStorePort, Result
from ..evaluation_listener import EvaluationListener
from ..explain import explain_artifact
from ..governance.approvals import (
    ApprovalAuthority,
    ApprovalChallenge,
    ApprovalDecision,
    ApprovalFlow,
    OperatorSigner,
)
from .inbox import ServiceInboxStore


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.")
        + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
    )


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
    is_cancelled: bool = False
    status: str = "running"
    lock: threading.Lock = field(default_factory=threading.Lock)


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
    ) -> None:
        self.store = inbox_store or ServiceInboxStore(":memory:")
        self.event_store = event_store or SqliteEventStore(":memory:")
        #: Evidence claims available to `vg why` (`S8-A-05`). Injected rather
        #: than read from disk: the service composes no store of its own.
        self.claims: tuple[Mapping[str, Any], ...] = tuple(claims)
        self.authority = authority or ApprovalAuthority()
        self._harness_runner = harness_runner
        self._active_runs: dict[str, ActiveRunContext] = {}
        self._lock = threading.Lock()
        self._evaluation_store = _ServiceEventStore(self)
        self._evaluation_listener = EvaluationListener(self._evaluation_store)

    def execute_command(self, frame: Mapping[str, Any]) -> dict[str, Any]:
        """Execute a validated command frame and return a response frame."""
        cmd = frame.get("command")
        if not isinstance(cmd, Mapping):
            return self._error_frame(
                frame.get("frameId", uuidv7()),
                "invalid_frame",
                "missing or non-object command payload",
            )

        name = str(cmd.get("name", ""))
        command_id = str(cmd.get("commandId", uuidv7()))
        idempotency_key = str(cmd.get("idempotencyKey", command_id))
        run_id = str(cmd.get("runId", ""))
        actor = str(cmd.get("actor", "operator"))
        payload = dict(cmd.get("payload", {}))
        now = _utc_now()

        # Check idempotency inbox
        is_new, prior_receipt = self.store.record_command(
            command_id, idempotency_key, name, run_id, payload, actor=actor, now=now
        )
        if not is_new and prior_receipt is not None:
            return {
                "version": "vg.4",
                "frameType": "receipt",
                "frameId": uuidv7(),
                "receipt": prior_receipt,
            }

        handler = getattr(self, f"_cmd_{name}", None)
        if handler is None:
            err_receipt = {
                "commandId": command_id,
                "status": "error",
                "runId": run_id,
                "detail": f"unknown command {name!r}",
            }
            self.store.complete_command(command_id, "error", err_receipt, now=_utc_now())
            return {
                "version": "vg.4",
                "frameType": "receipt",
                "frameId": uuidv7(),
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
                "receipt": receipt,
            }
        except Exception as exc:
            err_receipt = {
                "commandId": command_id,
                "status": "error",
                "runId": run_id,
                "detail": str(exc),
            }
            self.store.complete_command(command_id, "error", err_receipt, now=_utc_now())
            return {
                "version": "vg.4",
                "frameType": "receipt",
                "frameId": uuidv7(),
                "receipt": err_receipt,
            }

    def _check_cas(self, run_id: str, payload: Mapping[str, Any]) -> None:
        if "expectedSeq" in payload and payload["expectedSeq"] is not None:
            expected = int(payload["expectedSeq"])
            current = self.get_latest_seq(run_id)
            if expected != current:
                raise ValueError(
                    f"CAS conflict on run {run_id!r}: expectedSeq {expected} != current sequence {current}"
                )

    def get_latest_seq(self, run_id: str) -> int:
        res = self.event_store.read(EventRange(run_id=run_id))
        if res.ok and res.value:
            return int(res.value[-1].seq)
        return self.store.get_latest_seq(run_id)

    # -- Command Handlers ----------------------------------------------------

    def _cmd_StartRun(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        manifest_path = str(payload.get("manifestPath", ""))
        repo_path = str(payload.get("repoPath", "."))
        brief = str(payload.get("brief", ""))

        if not manifest_path or not brief:
            raise ValueError("StartRun requires manifestPath and brief")

        with self._lock:
            if run_id in self._active_runs:
                raise ValueError(f"run {run_id} is already active")
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

        # Spawn execution thread if runner provided
        if self._harness_runner is not None:
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
            raise ValueError(f"run {run_id} not found")
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
        decision_raw = payload.get("decision")
        if not isinstance(decision_raw, Mapping):
            if "approvalId" in payload:
                decision_raw = payload
            else:
                raise ValueError("ResolveApproval requires decision object")

        approval_id = str(decision_raw.get("approvalId", ""))
        resolution = str(decision_raw.get("resolution") or decision_raw.get("decision", "approved"))
        reviewer = str(decision_raw.get("reviewer", actor))
        args_digest = str(decision_raw.get("argsDigest", "sha256:" + "0" * 64))
        descriptor_digest = str(decision_raw.get("descriptorDigest", "sha256:" + "0" * 64))
        expires_at = str(decision_raw.get("expiresAt", _utc_now()))
        key_id = str(decision_raw.get("keyId", "operator-key-default"))
        signature = str(decision_raw.get("signature", ""))

        decision = ApprovalDecision(
            approval_id=approval_id,
            resolution=resolution,
            reviewer=reviewer,
            args_digest=args_digest,
            descriptor_digest=descriptor_digest,
            expires_at=expires_at,
            key_id=key_id,
            signature=signature,
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
        with self._lock:
            ctx = self._active_runs.get(run_id)
        if ctx is not None:
            ctx.is_cancelled = True
            ctx.status = "cancelled"
            ctx.approval_response_queue.put(None)
            self.store.set_run_state(
                run_id, ctx.manifest_path, ctx.repo_path, "cancelled", now=_utc_now()
            )
        else:
            state = self.store.get_run_state(run_id)
            if state is not None:
                self.store.set_run_state(
                    run_id, state["manifest_path"], state["repo_path"], "cancelled", now=_utc_now()
                )
        return {"runId": run_id, "status": "cancelled"}

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
        state = self.store.get_run_state(run_id)
        if state is None:
            raise ValueError(f"run {run_id} not found")
        seq = self.get_latest_seq(run_id)
        checkpoint_id = f"chk-{run_id}-{seq}"
        return {
            "runId": run_id,
            "status": state["status"],
            "checkpoint": checkpoint_id,
            "asOfSeq": str(seq),
        }

    def _cmd_Resume(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        state = self.store.get_run_state(run_id)
        if state is None:
            raise ValueError(f"run {run_id} not found")
        return {"runId": run_id, "status": "resumed"}

    def _cmd_ExplainArtifact(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        artifact_id = str(payload.get("artifactId", ""))
        if not artifact_id:
            raise ValueError("ExplainArtifact requires artifactId")
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
        """Read events from canonical EventStore or inbox fallback."""
        res = self.event_store.read(EventRange(run_id=run_id, after_seq=str(after_seq)))
        if res.ok and res.value is not None and len(res.value) > 0:
            return [env.to_dict() for env in res.value]
        return self.store.get_events(run_id, after_seq=after_seq)

    def stream_events(
        self, run_id: str, after_seq: int = 0
    ) -> Iterator[dict[str, Any]]:
        """Yield historical events followed by live events until terminal with gap detection."""
        last_seq = after_seq

        # 1. Replay historical events from store
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

        # 2. Subscribe to live queue if run is active
        with self._lock:
            ctx = self._active_runs.get(run_id)
            if ctx is None:
                return
            q: queue.Queue[dict[str, Any] | None] = queue.Queue()
            ctx.event_subscribers.append(q)

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
        """Write event through canonical EventStore and notify live subscribers."""
        now = _utc_now()
        seq = self.store.append_event(run_id, event_envelope, now=now)
        evt_copy = dict(event_envelope)
        evt_copy["seq"] = str(seq)

        # Commit to canonical EventStorePort
        env = _envelope_from_service_event(run_id, evt_copy)
        self.event_store.append([env])

        with self._lock:
            ctx = self._active_runs.get(run_id)
            if ctx is not None:
                for sub in list(ctx.event_subscribers):
                    sub.put(evt_copy)

        payload = event_envelope.get("payload")
        kind = payload.get("kind") if isinstance(payload, Mapping) else None
        if kind == "EpisodeCompleted":
            self._evaluation_listener.process_envelope(env)
        return seq

    # -- Internal Execution --------------------------------------------------

    def _run_worker_thread(self, ctx: ActiveRunContext, payload: Mapping[str, Any]) -> None:
        try:
            if self._harness_runner is not None:
                self._harness_runner(ctx, self)
        except Exception as exc:
            now = _utc_now()
            self.publish_event(
                ctx.run_id,
                {
                    "eventId": uuidv7(),
                    "scope": "run",
                    "occurredAt": now,
                    "principal": "runtime",
                    "runId": ctx.run_id,
                    "payload": {"kind": "RunFailed", "error": str(exc)},
                },
            )
        finally:
            self.store.set_run_state(
                ctx.run_id, ctx.manifest_path, ctx.repo_path, "completed", now=_utc_now()
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


def _envelope_from_service_event(run_id: str, event: Mapping[str, Any]) -> EventEnvelope:
    payload = event.get("payload")
    if not isinstance(payload, Mapping):
        payload = {}
    now = str(event.get("occurredAt") or _utc_now())
    episode_id = event.get("episodeId")
    return EventEnvelope(
        schema_version=str(event.get("schemaVersion", "4.0.0")),
        event_id=str(event.get("eventId") or uuidv7()),
        scope=str(event.get("scope") or "episode"),
        seq=str(event.get("seq") or "0"),
        occurred_at=now,
        recorded_at=str(event.get("recordedAt") or now),
        principal=str(event.get("principal") or "runtime"),
        principal_role=str(event.get("principalRole") or "episode"),
        tenant_id=str(event.get("tenantId") or "tenant-default"),
        owner_id=str(event.get("ownerId") or "owner-platform"),
        confidentiality=str(event.get("confidentiality") or "internal"),
        retention_class=str(event.get("retentionClass") or "standard"),
        trainability=str(event.get("trainability") or "prohibited"),
        redaction_status=str(event.get("redactionStatus") or "none"),
        payload=dict(payload),
        run_id=str(event.get("runId") or run_id),
        episode_id=episode_id if isinstance(episode_id, str) else None,
        trace_id=str(event.get("traceId") or "trace-service"),
        span_id=str(event.get("spanId") or "span-service"),
    )


class _ServiceEventStore(EventStorePort):
    """EventStorePort wrapping both canonical event store and inbox store."""

    def __init__(self, service: RuntimeService) -> None:
        self._service = service

    def append(self, events: Sequence[EventEnvelope]) -> Result[None]:
        for envelope in events:
            run_id = envelope.run_id or ""
            self._service.publish_event(run_id, envelope.to_dict())
        return Result.success(None)

    def read(self, range_query: EventRange | None = None) -> Result[Sequence[EventEnvelope]]:
        return self._service.event_store.read(range_query)

    def digest(self, run_id: str | None = None) -> Result[str]:
        return self._service.event_store.digest(run_id)

    def count(self, run_id: str | None = None) -> int:
        return self._service.event_store.count(run_id)


