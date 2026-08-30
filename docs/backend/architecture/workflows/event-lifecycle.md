---
id: backend.workflow.event-lifecycle
class: architecture
authority: descriptive
canonical_for:
  - causal event envelope emission flow
status: living
owner: backend-governance
version: "0.9.1a1"
last_verified: 2026-08-30
---

# Event Lifecycle Workflow

This page tracks the creation, serialization, emission, and persistence of immutable `mhf.event/2` envelopes in the backend event store.

## Flow Diagram

```mermaid
flowchart LR
    A[Kernel Effect Receipt] --> B[Wrap mhf.event/2 Envelope]
    B --> C[Assign Writer Sequence & Digest]
    C --> D[Commit to SQLite WAL Store]
    D --> E[Broadcast to Event Listeners]
    D --> F[Fold into Agent Projection]
```

## Canonical Components & Owners
- **Events Reference**: [`docs/backend/reference/events.md`](../../reference/events.md)
- **Schemas Reference**: [`docs/backend/reference/schemas.md`](../../reference/schemas.md)
