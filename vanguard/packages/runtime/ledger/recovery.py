"""Recovery scanner, replay reducer, and liveness controller outside the dying process.

Owning contract: VG-04 §12.4, GTS-13C T3.6, DEC-6B-026, DEC-6B-027, ADR-0062.

Invariants:
- The terminal record (RunRecovered or RunAborted) is ALWAYS written by the
  external recovery controller, NEVER by the corpse / dying process.
- Heartbeats indicate liveness; absence past lease expiration triggers recovery.
- Replay reduces the ledger and executes only the legal next transition.
- Re-entry after approved suspension is at S1, never re-querying the model.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from ...domain.ledger.events import EventEnvelope
from ...domain.primitives.primitives import uuidv7
from ...ports.event_store import EventRange, EventStorePort

__all__ = [
    "LedgerReplayState",
    "RecoveryRecord",
    "RecoveryScanner",
    "replay_ledger_state",
]


@dataclass(frozen=True, slots=True)
class RecoveryRecord:
    """Record of a recovery action taken by the external recovery scanner."""

    run_id: str
    action: str  # "recovered" | "aborted"
    reason: str
    controller_principal: str
    terminal_event_id: str
    terminal_seq: str


@dataclass(frozen=True, slots=True)
class LedgerReplayState:
    """State reconstructed solely from durable ledger events."""

    run_id: str
    status: str  # "active" | "suspended" | "completed" | "aborted" | "undeterminable"
    last_seq: int
    pending_approval: Mapping[str, Any] | None = None
    resolved_approval: Mapping[str, Any] | None = None
    unreconciled_intent: Mapping[str, Any] | None = None
    receipts_count: int = 0
    terminal_event: Mapping[str, Any] | None = None


def replay_ledger_state(events: Sequence[EventEnvelope]) -> LedgerReplayState:
    """Reconstruct execution state from an ordered event stream."""
    if not events:
        return LedgerReplayState(run_id="", status="active", last_seq=0)

    run_id = events[0].run_id or ""
    last_seq = 0
    status = "active"
    pending_approval: Mapping[str, Any] | None = None
    resolved_approval: Mapping[str, Any] | None = None
    last_intent: Mapping[str, Any] | None = None
    receipts_count = 0
    terminal_event: Mapping[str, Any] | None = None

    for ev in events:
        try:
            seq_val = int(ev.seq)
            if seq_val > last_seq:
                last_seq = seq_val
        except (ValueError, TypeError):
            pass

        kind = ev.payload.get("kind", "")
        if kind in ("EpisodeCompleted", "RunRecovered", "RunAborted", "RunFailed"):
            status = "completed" if kind == "EpisodeCompleted" else "aborted"
            terminal_event = dict(ev.payload)
        elif kind == "ApprovalRequested":
            status = "suspended"
            pending_approval = ev.payload.get("challenge")
        elif kind == "ApprovalResolved":
            resolved_approval = ev.payload.get("decision")
            status = "active"
        elif kind == "EffectIntent":
            last_intent = dict(ev.payload)
        elif kind == "Receipt" or kind == "EffectCompleted":
            last_intent = None
            receipts_count += 1

    if status == "active" and last_intent is not None:
        status = "undeterminable"

    return LedgerReplayState(
        run_id=run_id,
        status=status,
        last_seq=last_seq,
        pending_approval=pending_approval,
        resolved_approval=resolved_approval,
        unreconciled_intent=last_intent,
        receipts_count=receipts_count,
        terminal_event=terminal_event,
    )


def _parse_iso_to_millis(iso_str: str) -> int:
    """Parse RFC 3339 UTC timestamp into integer milliseconds."""
    clean = iso_str.rstrip("Z")
    if "." in clean:
        main, frac = clean.split(".", 1)
        frac = (frac + "000")[:3]
        dt = datetime.datetime.fromisoformat(main)
        ms = int(frac)
    else:
        dt = datetime.datetime.fromisoformat(clean)
        ms = 0
    return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000) + ms


class RecoveryScanner:
    """External recovery controller scanner that inspects runs and terminates dead ones."""

    def __init__(self, controller_principal: str = "recovery-controller") -> None:
        self.controller_principal = controller_principal

    def scan_and_recover_run(
        self,
        store: EventStorePort,
        run_id: str,
        current_time_iso: str,
        lease_timeout_ms: int,
        action: str = "recovered",
        reason: str = "Heartbeat lease expired without graceful completion",
    ) -> Optional[RecoveryRecord]:
        """Inspect a specific run. If lease has expired, write terminal record from outside."""
        read_res = store.read(EventRange(run_id=run_id))
        if not read_res.ok or not read_res.value:
            return None

        events = read_res.value
        last_event = events[-1]
        last_seq_int = int(last_event.seq)

        is_terminated = False
        last_heartbeat_time: Optional[str] = None
        tenant_id = last_event.tenant_id
        owner_id = last_event.owner_id

        for ev in events:
            kind = ev.payload.get("kind", "")
            if kind in ("EpisodeCompleted", "RunRecovered", "RunAborted", "RunFailed"):
                is_terminated = True
                break
            if kind == "Heartbeat":
                last_heartbeat_time = ev.payload.get("timestamp") or ev.occurred_at
            elif ev.occurred_at:
                last_heartbeat_time = ev.occurred_at

        if is_terminated:
            return None

        if last_heartbeat_time is None:
            last_heartbeat_time = last_event.occurred_at

        current_ms = _parse_iso_to_millis(current_time_iso)
        last_ms = _parse_iso_to_millis(last_heartbeat_time)

        if current_ms - last_ms < lease_timeout_ms:
            return None

        terminal_event_kind = "RunRecovered" if action == "recovered" else "RunAborted"
        terminal_seq_str = str(last_seq_int + 1)
        terminal_event_id = uuidv7()

        payload = {
            "kind": terminal_event_kind,
            "runId": run_id,
            "recoveryReason" if action == "recovered" else "reason": reason,
            "recoveredBy" if action == "recovered" else "abortedBy": self.controller_principal,
            "priorState": "active",
        }

        envelope = EventEnvelope(
            schema_version="vg.4",
            event_id=terminal_event_id,
            scope="recovery",
            run_id=run_id,
            seq=terminal_seq_str,
            occurred_at=current_time_iso,
            recorded_at=current_time_iso,
            principal=self.controller_principal,
            principal_role="process",
            trace_id=f"recovery-{run_id}",
            span_id=f"terminal-{terminal_seq_str}",
            tenant_id=tenant_id,
            owner_id=owner_id,
            confidentiality="internal",
            retention_class="standard",
            trainability="prohibited",
            redaction_status="none",
            payload=payload,
        )

        append_res = store.append([envelope])
        if not append_res.ok:
            raise RuntimeError(
                f"Recovery controller failed to append terminal event: {append_res.error}"
            )

        return RecoveryRecord(
            run_id=run_id,
            action=action,
            reason=reason,
            controller_principal=self.controller_principal,
            terminal_event_id=terminal_event_id,
            terminal_seq=terminal_seq_str,
        )
