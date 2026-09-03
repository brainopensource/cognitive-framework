"""EventStore port interface.

Owning contract: VG-04 §13, ICD §4.
Invariants:
- Ports accept and return domain types only.
- Failures are typed Result objects, not arbitrary unclassified exceptions.
- Zero concrete implementation in this package.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Optional, Protocol, Sequence, TypeVar

from ..domain.ledger.events import EventEnvelope

__all__ = [
    "Result",
    "PortFailure",
    "EventRange",
    "EventStorePort",
]

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class PortFailure:
    """Typed failure from a port invocation (ICD §4)."""

    kind: str  # "instrument_error" | "denied" | "not_found" | "conflict" | "unavailable" | "invalid_request"
    message: str
    retryable: bool = False


@dataclass(frozen=True, slots=True)
class Result(Generic[T]):
    """Generic Result container: either ok with value or failure with error."""

    ok: bool
    value: Optional[T] = None
    error: Optional[PortFailure] = None

    @classmethod
    def success(cls, value: T) -> Result[T]:
        return cls(ok=True, value=value, error=None)

    @classmethod
    def fail(cls, kind: str, message: str, retryable: bool = False) -> Result[T]:
        return cls(ok=False, value=None, error=PortFailure(kind=kind, message=message, retryable=retryable))


@dataclass(frozen=True, slots=True)
class EventRange:
    """Query range for reading ledger events."""

    run_id: Optional[str] = None
    episode_id: Optional[str] = None
    scope: Optional[str] = None
    after_seq: Optional[str] = None
    limit: Optional[int] = None
    project_id: Optional[str] = None


class EventStorePort(Protocol):
    """EventStore port interface (ICD §4, VG-04 §13)."""

    def append(self, events: Sequence[EventEnvelope]) -> Result[None]:
        """Atomically append an ordered sequence of event envelopes."""
        ...

    def read(self, range_query: Optional[EventRange] = None) -> Result[Sequence[EventEnvelope]]:
        """Read an ordered sequence of event envelopes matching query."""
        ...

    def digest(self, run_id: Optional[str] = None) -> Result[str]:
        """Compute the cumulative sha256 digest of stored events."""
        ...

    def count(self, run_id: Optional[str] = None) -> int:
        """Return the number of stored events."""
        ...
