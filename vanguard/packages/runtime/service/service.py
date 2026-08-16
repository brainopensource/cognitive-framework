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

from ...domain.primitives.primitives import uuidv7
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


class RuntimeService:
    """Generic durable runtime service engine."""

    def __init__(
        self,
        inbox_store: ServiceInboxStore | None = None,
        *,
        authority: ApprovalAuthority | None = None,
        harness_runner: Callable[..., Any] | None = None,
    ) -> None:
        self.store = inbox_store or ServiceInboxStore(":memory:")
        self.authority = authority or ApprovalAuthority()
        self._harness_runner = harness_runner
        self._active_runs: dict[str, ActiveRunContext] = {}
        self._lock = threading.Lock()

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
        correction = payload.get("correction", {})
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
        return {"runId": run_id, "artifact": payload.get("artifactId", ""), "explanation": ""}

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
