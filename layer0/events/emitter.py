"""Ledger event emitter. Every production kind is emitted through this facade."""

from __future__ import annotations

from typing import Mapping, Protocol

from vanguard.packages.domain.wire.types_gen import EventEnvelope, EventKind
from .envelope import EnvelopeFactory
from .taxonomy import EVENT_KINDS

__all__ = ["InMemorySink", "LedgerEmitter"]


class _Sink(Protocol):
    def append(self, envelope: EventEnvelope) -> None: ...


class InMemorySink:
    def __init__(self) -> None:
        self.envelopes: list[EventEnvelope] = []

    def append(self, envelope: EventEnvelope) -> None:
        self.envelopes.append(envelope)


class LedgerEmitter:
    """Adapts kernel Event values onto hash-chained envelopes."""

    def __init__(self, factory: EnvelopeFactory, sink: _Sink) -> None:
        self._factory = factory
        self._sink = sink

    @property
    def envelopes(self) -> tuple[EventEnvelope, ...]:
        stored = getattr(self._sink, "envelopes", ())
        return tuple(stored)

    def emit(self, event: object) -> EventEnvelope:
        kind = str(getattr(event, "kind"))
        if kind not in EVENT_KINDS:
            raise ValueError(f"undeclared event kind {kind!r}")
        envelope = self._factory.emit(
            EventKind(kind),
            run_id=str(getattr(event, "run_id")),
            principal=str(getattr(event, "principal")),
            payload=dict(getattr(event, "payload")),
            alertable=bool(getattr(event, "alertable", False)),
        )
        self._sink.append(envelope)
        return envelope

    def emit_kind(
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
    ) -> EventEnvelope:
        envelope = self._factory.emit(
            kind,
            run_id=run_id,
            principal=principal,
            payload=payload,
            episode_id=episode_id,
            branch_id=branch_id,
            causation_id=causation_id,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            alertable=alertable,
        )
        self._sink.append(envelope)
        return envelope
