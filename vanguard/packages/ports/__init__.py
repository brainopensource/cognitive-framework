"""Ports package: runtime seams and interfaces (ICD §2)."""

from .event_store import (
    EventRange,
    EventStorePort,
    PortFailure,
    Result,
)
from .kernel import (
    Clock,
    EffectAdapter,
    EventSink,
    Ledger,
)

__all__ = [
    "EventRange",
    "EventStorePort",
    "PortFailure",
    "Result",
    "Clock",
    "EffectAdapter",
    "EventSink",
    "Ledger",
]
