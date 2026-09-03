"""One durable ledger behind both the episode loop and the process engine.

`S3-INT-001`. The kernel writes intent through a `Ledger` and outcomes through
an `EventSink` (`ports/kernel.py`); the process engine reads `EventEnvelope`s
through an `EventStorePort` (`ports/event_store.py`). Those are two roles, not
two stores — a second store is how a trajectory ends up with two
irreconcilable accounts of the same run. `SharedLedger` adapts both roles onto
a single `EventStorePort`, which is the composition root's job and no one
else's (`ICD §3`).

The `Ledger`/`EventSink` failure contracts are preserved, because they are
what the kernel's exits are built on:

* `append_intent` either durably persists or raises — `F-21a` depends on the
  difference, and a store failure swallowed here would let an effect start
  with no record that it was attempted (`K-47`).
* `emit` never raises. `F-25` is log-not-fail, and the lease is already
  released by the time anything is emitted (`K-06`).
"""

from __future__ import annotations

from typing import Any, Mapping

from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
from vanguard.packages.domain.ledger.events import EventEnvelope
from vanguard.packages.ports.event_store import EventRange, EventStorePort

__all__ = ["SharedLedger"]

#: Classification defaults for a Phase 0 single-tenant run. They are explicit
#: rather than absent: an unlabelled event is not a cheaper event, it is an
#: event no retention or trainability rule can be applied to.
_CLASSIFICATION = {
    "schema_version": "vg.4",
    "tenant_id": "tenant-default",
    "owner_id": "owner-platform",
    "confidentiality": "internal",
    "retention_class": "extended",
    "trainability": "prohibited",
    "redaction_status": "none",
}


class SharedLedger:
    """`Ledger` + `EventSink` for the kernel, `EventStorePort` for everyone else."""

    def __init__(self, store: EventStorePort | None = None, *,
                 episode_id: str = "episode-1", fails: bool = False) -> None:
        self.store: EventStorePort = store or InMemoryEventStore()
        self.episode_id = episode_id
        self._seq = 0
        self._fails = fails

    # -- kernel-facing roles --------------------------------------------

    def append_intent(self, event: Any) -> None:
        """Durable or raising, never "probably written" (`F-21a`)."""
        if self._fails:
            raise OSError("fsync failed")
        self._write(self._envelope(event, scope="episode", role="episode"))

    def emit(self, event: Any) -> None:
        """`F-25`: an emission failure never fails the effect it describes."""
        try:
            self._write(self._envelope(event, scope="episode", role="episode"))
        except Exception:
            pass

    # -- governance-facing role -----------------------------------------

    def append_governance(self, kind: str, *, process_id: str,
                          principal: str = "approval-process",
                          occurred_at: str = "2026-08-15T10:00:00.000Z",
                          **payload: Any) -> EventEnvelope:
        """Append one governance event to the same ledger the episode uses."""
        envelope = self._build(
            scope="governance", role="process", principal=principal,
            occurred_at=occurred_at, run_id=None, episode_id=None,
            payload={"kind": kind, "processId": process_id, **payload})
        self._write(envelope)
        return envelope

    # -- reading ---------------------------------------------------------

    def events(self, **query: Any) -> list[EventEnvelope]:
        result = self.store.read(EventRange(**query) if query else None)
        if not result.ok:
            raise AssertionError(result.error.message if result.error else "read failed")
        return list(result.value or ())

    def kinds(self, **query: Any) -> list[str]:
        return [str(event.payload.get("kind")) for event in self.events(**query)]

    def digest(self) -> str:
        result = self.store.digest()
        return str(result.value)

    # -- internals -------------------------------------------------------

    def _write(self, envelope: EventEnvelope) -> None:
        result = self.store.append([envelope])
        if not result.ok:
            raise OSError(result.error.message if result.error else "append rejected")

    def _envelope(self, event: Any, *, scope: str, role: str) -> EventEnvelope:
        payload: Mapping[str, Any] = {
            "kind": event.kind,
            "reason": event.reason,
            "alertable": bool(getattr(event, "alertable", False)),
            **dict(event.payload),
        }
        return self._build(scope=scope, role=role, principal=event.principal,
                           occurred_at=event.at, run_id=event.run_id,
                           episode_id=self.episode_id, payload=payload)

    def _build(self, *, scope: str, role: str, principal: str, occurred_at: str,
               run_id: str | None, episode_id: str | None,
               payload: Mapping[str, Any]) -> EventEnvelope:
        self._seq += 1
        return EventEnvelope(
            event_id=f"018f3a2b-7c4d-7e1f-9a2b-{self._seq:012x}",
            scope=scope,
            seq=str(self._seq),
            occurred_at=occurred_at,
            recorded_at=occurred_at,
            principal=principal,
            principal_role=role,
            run_id=run_id,
            episode_id=episode_id,
            payload=dict(payload),
            **_CLASSIFICATION,
        )
