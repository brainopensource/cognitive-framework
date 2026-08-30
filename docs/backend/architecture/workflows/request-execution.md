---
id: backend.workflow.request-execution
class: architecture
authority: descriptive
canonical_for:
  - backend request execution flow
status: living
owner: backend-governance
version: "0.9.1a1"
last_verified: 2026-08-30
---

# Request Execution Workflow

This workflow illustrates how a single client command (`StartRun`, `Checkpoint`, `Resume`) is validated and dispatched across backend service boundaries.

## Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    participant IPC as RuntimeSocket (IPC)
    participant SVC as RuntimeService Daemon
    participant VAL as Validator / Policy
    participant DB as SQLite WAL Store

    IPC->>SVC: Command Frame (NDJSON)
    SVC->>VAL: Validate Idempotency & Auth
    alt Verification Failure
        VAL-->>SVC: Rejection Error
        SVC-->>IPC: Error Frame
    else Verification Success
        VAL-->>SVC: Validated Intent
        SVC->>DB: Persist Intent Fact
        SVC->>IPC: Command Receipt Frame
    end
```

## Canonical Components & Owners
- **Runtime Service Reference**: [`docs/backend/reference/runtime-service.md`](../../reference/runtime-service.md)
- **Delegation & Topology**: [`docs/backend/architecture/delegation-topology.md`](../delegation-topology.md)
