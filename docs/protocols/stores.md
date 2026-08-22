---
status: living
id: protocol-event-store-port
class: protocol-reference
authority: descriptive
canonical_for:
  - store-ports-protocol
source_of_truth:
  - docs/SPEC.md#2-ledger-as-truth
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
> **Status:** `AS_BUILT` · State Plane Storage Engine.

---

## Interface Definition

```python
class EventStorePort(Protocol):
    def append(self, event: EventEnvelope) -> int:
        """Append envelope atomically to SQLite WAL stream; returns sequence index."""
        ...
        
    def read_prefix(self, project_id: str, up_to_seq: int | None = None) -> Sequence[EventEnvelope]:
        """Read durable event prefix from disk."""
        ...
```
