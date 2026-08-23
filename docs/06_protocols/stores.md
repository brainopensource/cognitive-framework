---
status: living
id: protocol-event-store-port
class: protocol-reference
authority: descriptive
canonical_for:
  - store-ports-protocol
source_of_truth:
  - docs/SPEC.md
derived_from:
  - vanguard/packages/ports/event_store.py
  - vanguard/packages/adapters/stores/event_store.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Event Store Port Protocol (`EventStorePort`)

> **Source:** [`vanguard/packages/ports/event_store.py`](../../vanguard/packages/ports/event_store.py)  
> **Status:** `AS_BUILT` · Owning contract: VG-04 §13, ICD §4.

---

## Interface Definition

```python
class EventStorePort(Protocol):
    """EventStore port interface for append-only causal event storage."""

    def append(self, events: Sequence[EventEnvelope]) -> Result[None]:
        """Atomically append an ordered sequence of event envelopes."""
        ...

    def read(self, range_query: Optional[EventRange] = None) -> Result[Sequence[EventEnvelope]]:
        """Read an ordered sequence of event envelopes matching query."""
        ...

    def digest(self, run_id: Optional[str] = None) -> Result[str]:
        """Compute cumulative sha256 digest of stored events."""
        ...

    def count(self, run_id: Optional[str] = None) -> int:
        """Return the number of stored events."""
        ...
```
