"""Ports package: runtime seams and interfaces (ICD §2)."""

from .event_store import (
    Blob,
    BlobStorePort,
    EventRange,
    EventStorePort,
    PortFailure,
    Result,
)

__all__ = [
    "Blob",
    "BlobStorePort",
    "EventRange",
    "EventStorePort",
    "PortFailure",
    "Result",
]
