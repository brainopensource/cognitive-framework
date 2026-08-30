---
id: backend.workflow.agent-lifecycle
class: architecture
authority: descriptive
canonical_for:
  - agent projection lifecycle state machine
status: living
owner: backend-governance
version: "0.9.1a1"
last_verified: 2026-08-30
---

# Agent Lifecycle Workflow

This page documents the lifecycle state transitions of an agent projection over causal lineage.

## Flow Diagram

```mermaid
stateDiagram-v2
    [*] --> Uninitialized
    Uninitialized --> Active : Composition & Activation Plan
    Active --> Suspended : Turn Compaction / Checkpoint
    Suspended --> Active : Cold Process Continuation
    Active --> Terminated : Episode Completed / Budget Exhausted
    Terminated --> [*]
```

## Canonical Components & Owners
- **Delegation & Topology**: [`docs/backend/architecture/delegation-topology.md`](../delegation-topology.md)
- **Agent Substrate Theory**: [`docs/theory/agent-substrate.md`](../../../theory/agent-substrate.md)
