---
status: living
id: architecture-state-machines
class: architecture
authority: descriptive
canonical_for:
  - state-machines-fsm
source_of_truth:
  - docs/SPEC.md#1-layer-0--the-microkernel
derived_from:
  - vanguard/packages/agency/episode/engine.py
  - vanguard/packages/domain/ledger/reducer.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# State Machines & Lifecycle FSMs

> **Status:** Mixed descriptive view. The episode mechanism is current; the seven-state plugin FSM
> is `RATIFIED_NOT_IMPLEMENTED` until ADR-0081 lands in M-3.

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

## 2. Plugin Lifecycle Finite State Machine (ADR-0081 — `RATIFIED_NOT_IMPLEMENTED`)

```mermaid
stateDiagram-v2
    [*] --> Discovered: manifest scanned
    Discovered --> Verified: schemas & signatures valid
    Verified --> Resolved: dependencies satisfied
    Resolved --> Activated: resources bound & initialized
    Activated --> Quiesced: turn pause / drain
    Quiesced --> Activated: turn resume
    Quiesced --> Retired: session closed
    Activated --> Faulted: runtime exception
    Faulted --> Retired: cleanup
    Retired --> [*]
```

| State | Entering Event | Description & Guarantees |
|---|---|---|
| `Discovered` | `PluginDiscovered` | Target event; not yet present in the current event catalog |
| `Verified` | `PluginVerified` | Target event; not yet present in the current event catalog |
| `Resolved` | `PluginResolved` | Dependencies, capabilities, and port bindings resolved |
| `Activated` | `PluginActivated` | Plugin loaded into memory, UDS socket opened |
| `Quiesced` | `PluginQuiesced` | In-flight effects drained; safely paused |
| `Faulted` | `PluginFaulted` | Failure recorded in ledger; isolated |
| `Retired` | `PluginRetired` | Sockets closed, tmpfs workspace unmounted |
