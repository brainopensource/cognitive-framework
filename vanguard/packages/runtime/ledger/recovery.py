"""Recovery scanner and liveness lease controller outside the dying process.

Owning contract: VG-04 §12.4, GTS-13C T3.6.

Invariants:
- The terminal record (RunRecovered or RunAborted) is ALWAYS written by the
  external recovery controller, NEVER by the corpse / dying process.
- Heartbeats indicate liveness; absence past lease expiration triggers recovery.
- Scans are deterministic given a timestamp and lease bound.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional, Sequence

from ...domain.ledger.events import EventEnvelope, parse_event_envelope
from ...ports.event_store import EventRange, EventStorePort

__all__ = [
    "RecoveryScanner",
    "RecoveryRecord",
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

        # Check if already terminated
        is_terminated = False
        last_heartbeat_time: Optional[str] = None
        episode_id: Optional[str] = None
        tenant_id = last_event.tenant_id
        owner_id = last_event.owner_id

        for ev in events:
            if ev.episode_id:
                episode_id = ev.episode_id
            kind = ev.payload.get("kind", "")
            if kind in ("EpisodeCompleted", "RunRecovered", "RunAborted"):
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
            # Lease is still healthy
            return None

        # Lease has expired: corpse has died.
        # Write terminal record outside the dying process (T3.6).
        terminal_event_kind = "RunRecovered" if action == "recovered" else "RunAborted"
        terminal_seq_str = str(last_seq_int + 1)
        from ...domain.primitives.primitives import uuidv7
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
            raise RuntimeError(f"Recovery controller failed to append terminal event: {append_res.error}")

        return RecoveryRecord(
            run_id=run_id,
            action=action,
            reason=reason,
            controller_principal=self.controller_principal,
            terminal_event_id=terminal_event_id,
            terminal_seq=terminal_seq_str,
        )
