"""In-memory ledger store used by the sequential driver and replay tests."""

from __future__ import annotations

from layer0.spi.types_gen import EventEnvelope
from .emitter import InMemorySink, LedgerEmitter
from .envelope import EnvelopeFactory

__all__ = ["MemoryLedger"]


class MemoryLedger:
    def __init__(self, factory: EnvelopeFactory | None = None) -> None:
        self.factory = factory or EnvelopeFactory()
        self.sink = InMemorySink()
        self.emitter = LedgerEmitter(self.factory, self.sink)
        self.intents: list[object] = []

    def emit(self, event: object) -> None:
        self.emitter.emit(event)

    def append_intent(self, event: object) -> None:
        """K-47 durable intent. Emission is the EventSink's job (S12 / K-06)."""
        self.intents.append(event)

    @property
    def envelopes(self) -> tuple[EventEnvelope, ...]:
        return tuple(self.sink.envelopes)
