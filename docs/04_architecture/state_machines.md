---
status: living
id: architecture-state-machines
class: architecture
authority: descriptive
canonical_for:
  - state-machines-fsm
source_of_truth:
  - docs/SPEC.md#1-layer-0--the-microkernel
  - docs/02_decisions/0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md
derived_from:
  - vanguard/packages/agency/episode/engine.py
  - vanguard/packages/domain/ledger/reducer.py
applies_to:
  - v0.6.2
implementation_status: MIXED
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# State Machines & Lifecycle FSMs

> **Status:** Mixed descriptive view. The episode mechanism and packages-path seven-state plugin
> FSM are implemented; M-3 remains open for final falsifier and convergence closure.

---

## 1. Episode turn mechanism (`AS_BUILT` conceptual projection)

Implemented in [`EpisodeEngine`](../../vanguard/packages/agency/episode/engine.py):

```mermaid
stateDiagram-v2
    [*] --> Running: EpisodeEngine.run()
    Running --> ContextCompiled: context compiler
    ContextCompiled --> ProposalProduced: ModelPort.propose()
    ProposalProduced --> ChildEpisode: current spawn proposal path
    ProposalProduced --> KernelDispatch: effect proposal
    KernelDispatch --> TurnRecorded: receipt or authorization denial
    ChildEpisode --> TurnRecorded: typed SpawnResult
    TurnRecorded --> Running: turns remain and no terminal stop
    TurnRecorded --> EpisodeCompleted: terminal success
    Running --> EpisodeAborted: budget, instrument, malformed proposal, or no-progress terminal
    EpisodeCompleted --> [*]
    EpisodeAborted --> [*]
```

This is an explanatory projection of control flow, not a claim that these labels are a persisted
enum. Persisted truth is the event catalog and reducer.

---

## 2. Plugin Lifecycle Finite State Machine (ADR-0081 — `AS_BUILT`, M-3 closure active)

```mermaid
stateDiagram-v2
    [*] --> Discovered: manifest scanned
    Discovered --> Resolved: immutable ref and dependencies resolved
    Resolved --> Verified: schema, signature, interface, ceiling, and isolation verified
    Verified --> Activated: frozen resources bound and initialized
    Activated --> Quiescing: stop admission and drain leases
    Quiescing --> Retired: process stopped and cleanup complete
    Discovered --> Faulted: discovery failure
    Resolved --> Faulted: resolution or verification failure
    Verified --> Faulted: activation failure
    Activated --> Faulted: runtime exception
    Quiescing --> Faulted: shutdown failure
    Faulted --> Retired: cleanup
    Retired --> [*]
```

| State | Entering Event | Description & Guarantees |
|---|---|---|
| `Discovered` | `PluginDiscovered` | Target event; not yet present in the current event catalog |
| `Resolved` | `PluginResolved` | Dependencies, capabilities, and port bindings resolved |
| `Verified` | `PluginVerified` | Target event; schema, signature, interface, ceiling, and isolation evidence recorded |
| `Activated` | `PluginActivated` | Plugin loaded into memory, UDS socket opened |
| `Quiescing` | `PluginQuiesced` | New work denied while in-flight leases drain; no transition back to active |
| `Faulted` | `PluginFaulted` | Failure recorded in ledger; isolated |
| `Retired` | `PluginRetired` | Sockets closed, tmpfs workspace unmounted |
