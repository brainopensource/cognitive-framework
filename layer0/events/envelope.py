"""RFC 8785 envelope construction with prev_digest hash chaining."""

from __future__ import annotations

from typing import Mapping

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.wire.types_gen import EventEnvelope, EventKind, JsonObject

__all__ = ["EnvelopeClock", "EnvelopeFactory"]


class EnvelopeClock:
    """Injected; replay substitutes recorded timestamps keyed by (run_id, seq)."""

    def __init__(self, stamps: list[str] | None = None) -> None:
        self._stamps = list(stamps or [])
        self._n = 0

    def now(self) -> str:
        if self._n < len(self._stamps):
            stamp = self._stamps[self._n]
        else:
            stamp = f"1970-01-01T00:00:{self._n:02d}.000Z"
        self._n += 1
        return stamp


class EnvelopeFactory:
    def __init__(self, clock: EnvelopeClock | None = None) -> None:
        self._clock = clock or EnvelopeClock()
        self._seq = 0
        self._prev: str | None = None
        self._counter = 0

    def emit(
        self,
        kind: EventKind | str,
        *,
        run_id: str,
        principal: str,
        payload: Mapping[str, object] | None = None,
        episode_id: str | None = None,
        branch_id: str = "main",
        causation_id: str | None = None,
        correlation_id: str | None = None,
        idempotency_key: str | None = None,
        alertable: bool = False,
        event_id: str | None = None,
    ) -> EventEnvelope:
        kind_value = kind if isinstance(kind, EventKind) else EventKind(kind)
        occurred_at = self._clock.now()
        self._counter += 1
        ident = event_id or f"{run_id}:{self._seq}:{self._counter}"
        body: JsonObject = dict(payload or {})
        unsigned = {
            "schema_version": "mhf.event/1",
            "event_id": ident,
            "kind": kind_value.value,
            "seq": self._seq,
            "occurred_at": occurred_at,
            "run_id": run_id,
            "principal": principal,
            "payload": body,
            "episode_id": episode_id,
            "branch_id": branch_id,
            "prev_digest": self._prev,
            "causation_id": causation_id,
            "correlation_id": correlation_id,
            "idempotency_key": idempotency_key,
            "alertable": alertable,
        }
        # `chain_digest` (layer0/events/canonical.py, KILL at 2.2-B): the same
        # `digest(JCS({prev, envelope}))` formula, inlined -- the packages
        # emitter chains differently (`prev_digest` inside the envelope,
        # digest over the envelope alone), so this is not a call to that.
        digest = digest_of({"prev_digest": self._prev, "envelope": unsigned})
        envelope = EventEnvelope(
            schema_version="mhf.event/1",
            event_id=ident,
            kind=kind_value,
            seq=self._seq,
            occurred_at=occurred_at,
            run_id=run_id,
            principal=principal,
            payload=body,
            digest=digest,
            episode_id=episode_id,
            branch_id=branch_id,
            prev_digest=self._prev,
            causation_id=causation_id,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            alertable=alertable,
        )
        self._prev = digest
        self._seq += 1
        return envelope

    @property
    def seq(self) -> int:
        return self._seq

    @property
    def prev_digest(self) -> str | None:
        return self._prev
