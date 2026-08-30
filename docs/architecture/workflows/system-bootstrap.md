---
id: arch.workflow.system-bootstrap
class: architecture
authority: descriptive
canonical_for:
  - system bootstrap sequence
status: living
owner: architecture-governance
version: "0.9.1a1"
last_verified: 2026-08-30
---

# System Bootstrap Workflow

This page details the initialization sequence of the Vanguard substrate, from environment loading through port wiring, SQLite WAL initialization, and daemon startup.

## Flow Diagram

```mermaid
flowchart TD
    A[CLI / Process Invocation] --> B[Load Environment & Profiles]
    B --> C{Profile Selected?}
    C -- Valid --> D[Wire Hexagonal Ports]
    C -- Invalid --> E[Fail Closed / Abort]
    D --> F[Initialize SQLite WAL Ledger]
    F --> G[Reconstruct Unfinished Runs]
    G --> H[Bind RuntimeService Unix Socket]
    H --> I[Ready for Command Dispatch]
```

## Canonical Components & Owners
- **System Overview**: [`docs/architecture/overview.md`](../overview.md)
- **Data Flow**: [`docs/architecture/data-flow.md`](../data-flow.md)
