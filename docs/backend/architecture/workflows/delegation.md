---
id: backend.workflow.delegation
class: architecture
authority: descriptive
canonical_for:
  - recursive agent delegation workflow
status: living
owner: backend-governance
version: "0.9.1a1"
last_verified: 2026-08-30
---

# Recursive Delegation Workflow

This page details how `agent.spawn` executes recursive delegation under strict monotonic capability attenuation.

## Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    participant Parent as Parent EpisodeEngine
    participant Kernel as Microkernel (S0-S12)
    participant Child as Attenuated Child Engine

    Parent->>Kernel: dispatch(agent.spawn, sub_budget)
    Kernel->>Kernel: Verify Monotonic Attenuation (Child <= Parent)
    Kernel->>Child: Instantiate Child Execution Lineage
    loop Child Turns
        Child->>Kernel: Action Dispatch
        Kernel-->>Child: Effect Receipt
    end
    Child-->>Parent: Final Artifact Digest & Result
```

## Canonical Components & Owners
- **Delegation Architecture**: [`docs/backend/architecture/delegation-topology.md`](../delegation-topology.md)
- **Port Contracts**: [`docs/backend/reference/ports.md`](../../reference/ports.md)
