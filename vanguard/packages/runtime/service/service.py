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

from ...domain.ledger.events import EventEnvelope
from ...domain.primitives.primitives import uuidv7
from ...domain.evidence.claim import Claim, ClaimError, parse_claim
from ...domain.wire.contracts import parse_wire
from ...ports.event_store import EventRange, Result
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
        authority: ApprovalAuthority | None = None,
        harness_runner: Callable[..., Any] | None = None,
        claims: Sequence[Mapping[str, Any]] = (),
    ) -> None:
        self.store = inbox_store or ServiceInboxStore(":memory:")
        #: Evidence claims available to `vg why` (`S8-A-05`). Injected rather
        #: than read from disk: the service composes no store of its own.
        self.claims: tuple[Mapping[str, Any], ...] = tuple(claims)
        self.authority = authority or ApprovalAuthority()
        self._harness_runner = harness_runner
        self._active_runs: dict[str, ActiveRunContext] = {}
        self._lock = threading.Lock()
        # Port only: never import IsolatedEvaluator here (AT-12).
        self._evaluation_store = _InboxEventStore(self.store)
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
        # T-08 HMAC authenticity is deferred; this is a liveness producer only.
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

        return {"runId": run_id, "status": "started", "manifest": manifest_path}

    def _cmd_GetRun(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        state = self.store.get_run_state(run_id)
        if state is None:
            raise ValueError(f"run {run_id} not found")
        events = self.store.get_events(run_id, after_seq=0)
        return {
            "runId": run_id,
            "status": state["status"],
            "eventCount": len(events),
            "manifestPath": state["manifest_path"],
            "repoPath": state["repo_path"],
        }

    def _cmd_ResolveApproval(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        decision_raw = payload.get("decision")
        if not isinstance(decision_raw, Mapping):
            raise ValueError("ResolveApproval requires decision object")

        decision = ApprovalDecision(
            approval_id=str(decision_raw["approvalId"]),
            resolution=str(decision_raw["resolution"]),
            reviewer=str(decision_raw["reviewer"]),
            args_digest=str(decision_raw["argsDigest"]),
            descriptor_digest=str(decision_raw["descriptorDigest"]),
            expires_at=str(decision_raw["expiresAt"]),
            key_id=str(decision_raw.get("keyId", "operator-key-default")),
            signature=str(decision_raw.get("signature", "")),
        )

        with self._lock:
            ctx = self._active_runs.get(run_id)

        if ctx is None:
            raise ValueError(f"no active run for {run_id}")

        now = _utc_now()
        self.publish_event(
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
        ctx.approval_response_queue.put(decision)
        return {"runId": run_id, "approvalId": decision.approval_id, "status": "submitted"}

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
        return {"runId": run_id, "status": "cancelled"}

    def _cmd_RecordCorrection(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        # `S8-A-04`. The wire contract already carries the reason-code enum and
        # `D-07`'s rule that a `style` or `architecture_preference` correction
        # may not be scoped wider than the people it came from. Appending an
        # unparsed payload meant none of that was enforced and the corpus could
        # hold corrections the normative reader rejects. `WireError` is a
        # `ValueError`, so a bad record surfaces as a command error frame.
        correction = parse_wire("CorrectionRecord", payload.get("correction"))
        now = _utc_now()
        seq = self.store.append_event(
            run_id,
            {
                "eventId": uuidv7(),
                "scope": "run",
                "occurredAt": now,
                "principal": actor,
                "runId": run_id,
                "payload": {"kind": "CorrectionRecorded", "correction": correction},
            },
            now=now,
        )
        return {"runId": run_id, "seq": seq, "status": "recorded"}

    def _cmd_Checkpoint(
        self, run_id: str, payload: Mapping[str, Any], actor: str, command_id: str
    ) -> dict[str, Any]:
        state = self.store.get_run_state(run_id)
        if state is None:
            raise ValueError(f"run {run_id} not found")
        return {"runId": run_id, "status": state["status"], "checkpoint": _utc_now()}

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
        """`vg why <artifact>` (`S10-A-04`).

        This returned `{"explanation": ""}` -- the command existed and answered
        nothing, which is worse than absent because it looks answered. It now
        derives all three answers from the ledger and the supplied claims, and
        says plainly when an artifact has no evidence rather than returning an
        empty section that reads like "nothing is wrong".
        """
        artifact_id = str(payload.get("artifactId", ""))
        if not artifact_id:
            raise ValueError("ExplainArtifact requires artifactId")
        explanation = explain_artifact(
            artifact_id,
            events=self._explain_events(run_id),
            claims=self._claims_for(artifact_id),
            substrate_profile=payload.get("substrateProfile"),
        )
        return {"runId": run_id, "artifact": artifact_id,
                "explanation": explanation.to_dict()}

    def _explain_events(self, run_id: str) -> list[Any]:
        """Ledger events for the run, as envelope-shaped objects."""
        return [_EventView(record) for record in self.store.get_events(run_id)]

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

    # -- Event Streaming -----------------------------------------------------

    def stream_events(
        self, run_id: str, after_seq: int = 0
    ) -> Iterator[dict[str, Any]]:
        """Yield historical events followed by live events until terminal."""
        # 1. Historical replay from outbox
        for evt in self.store.get_events(run_id, after_seq=after_seq):
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
        now = _utc_now()
        seq = self.store.append_event(run_id, event_envelope, now=now)
        evt_copy = dict(event_envelope)
        evt_copy["seq"] = str(seq)

        with self._lock:
            ctx = self._active_runs.get(run_id)
            if ctx is not None:
                for sub in list(ctx.event_subscribers):
                    sub.put(evt_copy)

        payload = event_envelope.get("payload")
        kind = payload.get("kind") if isinstance(payload, Mapping) else None
        if kind == "EpisodeCompleted":
            envelope = _envelope_from_service_event(run_id, evt_copy)
            self._evaluation_listener.process_envelope(envelope)
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


class _InboxEventStore:
    """EventStorePort over the service inbox. No evaluator adapter import."""

    def __init__(self, inbox: ServiceInboxStore) -> None:
        self._inbox = inbox

    def append(self, events: Sequence[EventEnvelope]) -> Result[None]:
        now = _utc_now()
        for envelope in events:
            run_id = envelope.run_id or ""
            self._inbox.append_event(run_id, envelope.to_dict(), now=now)
        return Result.success(None)

    def read(self, range_query: EventRange | None = None) -> Result[Sequence[EventEnvelope]]:
        return Result.success(())

    def digest(self, run_id: str | None = None) -> Result[str]:
        return Result.success("")

    def count(self, run_id: str | None = None) -> int:
        return 0


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
