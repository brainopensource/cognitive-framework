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
from ...ports.event_store import EventRange, EventStorePort
from ..ledger_emitter import LedgerEmitter

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
    #: `ChildSpawned` with no matching `ChildReturned`. The subtree may have
    #: mutated the world before the process died, so it is neither a success
    #: nor a failure until something adjudicates it (`WP-A1`, `F-22`).
    open_children: tuple[Mapping[str, Any], ...] = ()


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
    spawned_children: dict[str, Mapping[str, Any]] = {}
    closed_children: set[str] = set()

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
        elif kind in ("EffectIntent", "EffectStarted"):
            last_intent = dict(ev.payload)
        elif kind in ("Receipt", "EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled"):
            last_intent = None
            if kind in ("Receipt", "EffectCompleted"):
                receipts_count += 1
        elif kind == "ChildSpawned":
            child_id = ev.payload.get("childEpisodeId")
            if child_id:
                spawned_children[str(child_id)] = dict(ev.payload)
        elif kind == "ChildReturned":
            child_id = ev.payload.get("childEpisodeId")
            if child_id:
                closed_children.add(str(child_id))

    open_children = tuple(
        payload for child_id, payload in spawned_children.items()
        if child_id not in closed_children
    )

    if status == "active" and last_intent is not None:
        status = "undeterminable"
    if status == "active" and open_children:
        # A subtree that started and never reported is exactly the case the
        # ordering of the two facts exists to make visible.
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
        open_children=open_children,
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

        emitter = LedgerEmitter(
            store,
            episode_id=last_event.episode_id or "recovery",
            project_id=last_event.project_id or "project-default",
            principal_id=self.controller_principal,
            harness_digest=last_event.harness_digest or "sha256:" + ("0" * 64),
            parent_principal_id=last_event.parent_principal_id,
            parent_episode_id=last_event.parent_episode_id,
            role="recovery",
            anchor=last_event,
        )
        terminal_event_kind = "RunRecovered" if action == "recovered" else "RunAborted"
        payload = {
            "kind": terminal_event_kind,
            "runId": run_id,
            "recoveryReason" if action == "recovered" else "reason": reason,
            "recoveredBy" if action == "recovered" else "abortedBy": self.controller_principal,
            "priorState": "active",
        }
        envelope = emitter.scheduler().emit_kind(
            terminal_event_kind,
            run_id=run_id,
            principal=self.controller_principal,
            payload=payload,
            episode_id=last_event.episode_id,
        )

        return RecoveryRecord(
            run_id=run_id,
            action=action,
            reason=reason,
            controller_principal=self.controller_principal,
            terminal_event_id=envelope.event_id,
            terminal_seq=str(envelope.seq),
        )

    def reconcile_open_intents(
        self,
        store: EventStorePort,
        *,
        occurred_at: str,
        project_id: str | None = None,
    ) -> Sequence[EventEnvelope]:
        """K-47 / F-14: EffectStarted without a terminal effect → undeterminable.

        `project_id` scopes the scan. Without it a shared store lets one
        project's terminal receipt close another project's open intent, which
        is the same cross-project idempotency defect `WP-A1` closes in
        `delegation._already_settled`; the two must stay scoped together or
        the isolation falsifier passes on one path and fails on the other.
        """
        read = store.read(EventRange(project_id=project_id))
        if not read.ok or not read.value:
            return []
        events = list(read.value)
        open_intents: list[EventEnvelope] = []
        closed: set[str] = set()
        for ev in events:
            kind = ev.payload.get("kind") or ev.mhf_kind
            key = ev.payload.get("idempotencyKey") or ev.event_id
            if kind == "EffectStarted":
                open_intents.append(ev)
            elif kind in ("EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled"):
                closed.add(ev.payload.get("idempotencyKey") or "")
                if ev.causation_id:
                    closed.add(ev.causation_id)
        reconciled: list[EventEnvelope] = []
        for intent in open_intents:
            intent_key = intent.payload.get("idempotencyKey") or intent.event_id
            if intent_key in closed or intent.event_id in closed:
                continue
            has_terminal = False
            started = False
            for ev in events:
                kind = ev.payload.get("kind") or ev.mhf_kind
                if ev.event_id == intent.event_id:
                    started = True
                    continue
                if started and kind in (
                    "EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled",
                ):
                    has_terminal = True
                    break
            if has_terminal:
                continue
            emitter = LedgerEmitter(
                store,
                episode_id=intent.episode_id or "recovery",
                project_id=intent.project_id or "project-default",
                principal_id=self.controller_principal,
                harness_digest=intent.harness_digest or "sha256:" + ("0" * 64),
                parent_principal_id=intent.parent_principal_id,
                parent_episode_id=intent.parent_episode_id,
                role="recovery",
                anchor=intent,
            )
            desc_digest = intent.payload.get("descriptorDigest") or intent.payload.get("descriptor_digest")
            payload = {
                "kind": "EffectReconciled",
                "status": "undeterminable",
                "occurrence": "undeterminable",
                "reason": "process death between S8a and S9",
            }
            if desc_digest:
                payload["descriptorDigest"] = desc_digest
            if intent_key:
                payload["idempotencyKey"] = intent_key
            out = emitter.recovery().emit_kind(
                "EffectReconciled",
                run_id=intent.run_id or "",
                principal=self.controller_principal,
                payload=payload,
                episode_id=intent.episode_id,
                occurred_at=occurred_at,
                causation_id=intent.event_id,
            )
            reconciled.append(out)
        return reconciled

    def reconcile_open_children(
        self,
        store: EventStorePort,
        *,
        occurred_at: str,
        project_id: str | None = None,
    ) -> Sequence[EventEnvelope]:
        """`WP-A1`: `ChildSpawned` without `ChildReturned` → undeterminable.

        Two design choices are load-bearing here.

        **The kind is `EffectReconciled`, not a child event.** `SpawnAdapter`
        is the sole legal writer of `ChildSpawned`/`ChildReturned`
        (`PRIVILEGED_KIND_OWNERS`), and that exclusivity is the ADR-0090
        claim. Recovery adjudicating a subtree must not require widening it,
        so recovery speaks in its own already-owned kind and binds the child
        by `idempotencyKey` and causation instead.

        **The verdict is undeterminable, never failed.** The child may have
        completed an irreversible effect before the process died. `failed`
        would license a retry that repeats it; `completed` would invent a
        result nobody observed.
        """
        read = store.read(EventRange(project_id=project_id))
        if not read.ok or not read.value:
            return []
        events = list(read.value)
        state = replay_ledger_state(events)
        if not state.open_children:
            return []

        # An open child already adjudicated in a previous recovery pass stays
        # adjudicated; reconciliation is idempotent, not cumulative.
        already: set[str] = set()
        for ev in events:
            if (ev.payload.get("kind") or ev.mhf_kind) != "EffectReconciled":
                continue
            key = ev.payload.get("idempotencyKey")
            if key:
                already.add(str(key))

        spawn_events = {
            str(ev.payload.get("childEpisodeId")): ev
            for ev in events
            if (ev.payload.get("kind") or ev.mhf_kind) == "ChildSpawned"
        }

        reconciled: list[EventEnvelope] = []
        for payload in state.open_children:
            child_id = str(payload.get("childEpisodeId") or "")
            intent_key = str(payload.get("settledIntentKey") or "")
            if not child_id or intent_key in already:
                continue
            anchor = spawn_events.get(child_id)
            if anchor is None:  # pragma: no cover -- derived from the same fold
                continue
            emitter = LedgerEmitter(
                store,
                episode_id=anchor.episode_id or child_id,
                project_id=anchor.project_id or project_id or "project-default",
                principal_id=self.controller_principal,
                harness_digest=anchor.harness_digest or "sha256:" + ("0" * 64),
                parent_principal_id=anchor.parent_principal_id,
                parent_episode_id=anchor.parent_episode_id,
                role="recovery",
                anchor=anchor,
            )
            out = emitter.recovery().emit_kind(
                "EffectReconciled",
                run_id=anchor.run_id or "",
                principal=self.controller_principal,
                payload={
                    "kind": "EffectReconciled",
                    "status": "undeterminable",
                    "occurrence": "undeterminable",
                    "childEpisodeId": child_id,
                    "idempotencyKey": intent_key,
                    "reason": "process death between ChildSpawned and "
                              "ChildReturned",
                },
                episode_id=anchor.episode_id,
                occurred_at=occurred_at,
                causation_id=anchor.event_id,
            )
            reconciled.append(out)
        return reconciled

    @staticmethod
    def settled_effect(
        store: EventStorePort,
        idempotency_key: str,
        *,
        project_id: str | None = None,
    ) -> EventEnvelope | None:
        """Return the durable terminal receipt for a key, if one already exists.

        Scoped by project: an idempotency key is unique *within* a project, so
        an unscoped lookup would let one project replay another's settlement.
        """
        read = store.read(EventRange(project_id=project_id))
        if not read.ok or not read.value:
            return None
        for event in reversed(list(read.value)):
            kind = event.payload.get("kind") or event.mhf_kind
            key = (event.payload.get("idempotencyKey")
                   or event.payload.get("idempotency_key") or event.idempotency_key)
            if key == idempotency_key and kind in {
                "EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled",
            }:
                return event
        return None

    @classmethod
    def continue_idempotent_effect(
        cls, store: EventStorePort, idempotency_key: str, execute: Any,
        *, project_id: str | None = None,
    ) -> tuple[bool, Any]:
        """Reuse a durable terminal receipt or execute exactly once if unsettled.

        The boolean is ``True`` when recovery reused persistence and therefore
        did not invoke the physical effector.
        """
        settled = cls.settled_effect(store, idempotency_key, project_id=project_id)
        if settled is not None:
            return True, settled
        return False, execute()
