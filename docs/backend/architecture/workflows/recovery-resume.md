---
id: backend.workflow.recovery-resume
class: architecture
authority: descriptive
canonical_for:
  - cold process recovery and resume sequence
status: living
owner: backend-governance
version: "0.9.1a1"
last_verified: 2026-08-30
---

# Recovery & Resume Workflow

This page documents fresh-process cold recovery (RF-25) by folding causal events from the SQLite WAL store.

## Flow Diagram

```mermaid
flowchart TD
    A[Crash or Restart Event] --> B[Fresh Process Invocation]
    B --> C[Open SQLite WAL Event Store]
    C --> D[Fetch Monotonic Event Stream]
    D --> E[Reconstruct AgentView State via Fold]
    E --> F[Verify Pre-Crash Verified Prefix]
    F --> G[Resume EpisodeEngine Execution]
```

## Canonical Components & Owners
- **Events Reference**: [`docs/backend/reference/events.md`](../../reference/events.md)
- **Data Flow**: [`docs/architecture/data-flow.md`](../../../architecture/data-flow.md)
