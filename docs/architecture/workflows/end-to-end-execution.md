---
id: arch.workflow.end-to-end-execution
class: architecture
authority: descriptive
canonical_for:
  - end-to-end execution workflow
status: living
owner: architecture-governance
version: "0.9.1a1"
last_verified: 2026-09-03
---

# End-to-End Execution Workflow

This page provides the canonical explanatory diagram and sequence for an end-to-end Vanguard run, from composition through S0–S12 microkernel dispatch, ledger emission, and evaluator reconciliation.

## Flow Diagram

```mermaid
sequenceDiagram
    autonumber
    participant Client as Client / vg CLI
    participant Runtime as RuntimeService
    participant Engine as EpisodeEngine
    participant Kernel as Kernel (S0–S12)
    participant Ledger as SQLite Ledger

    Client->>Runtime: StartRun(manifest, profile)
    Runtime->>Runtime: Build ActivationPlan
    Runtime->>Engine: Initialize Episode
    loop Turn Execution Loop
        Engine->>Engine: Compile Context & Action
        Engine->>Kernel: dispatch(intent, budget)
        Note over Kernel: Monotonic budget attenuation (S0-S12)
        Kernel-->>Engine: ActionReceipt / Effect
        Engine->>Ledger: Emit mhf.event/2
        Engine->>Client: Stream Event Frame
    end
    Engine->>Runtime: Reconcile Verdict
    Runtime-->>Client: Final Run Receipt
```

## Canonical Components & Owners
- **System Overview & Boundaries**: [`docs/architecture/overview.md`](../overview.md)
- **Data Flow & Boundaries**: [`docs/architecture/boundaries.md`](../boundaries.md)
- **Normative Contract**: [`docs/execution/spec.md`](../../execution/spec.md)
