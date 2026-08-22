---
status: living
id: architecture-state-machines
class: architecture
authority: descriptive
canonical_for:
  - state-machines-fsm
source_of_truth:
  - docs/SPEC.md#5-state-machines-and-lifecycle
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

> **Status:** `AS_BUILT` · Descriptive View.

---

## 1. Episode Turn Engine Lifecycle

Implemented in [`EpisodeEngine`](../../vanguard/packages/agency/episode/engine.py):

```mermaid
stateDiagram-v2
    [*] --> Initialized: compose()
    Initialized --> TurnStarted: start_turn()
    TurnStarted --> Observing: build_context()
    Observing --> Proposing: model.generate()
    Proposing --> Authorizing: kernel.dispatch()
    Authorizing --> EffectExecuting: grant valid
    Authorizing --> TurnFailed: grant denied
    EffectExecuting --> Receipting: effect completed
    Receipting --> TurnCompleted: receipt recorded
    TurnCompleted --> TurnStarted: budget & turns remain
    TurnCompleted --> EpisodeCompleted: task finished / stop requested
    TurnFailed --> EpisodeAborted: budget exhausted / unrecoverable error
    EpisodeCompleted --> [*]
    EpisodeAborted --> [*]
```

---

## 2. Plugin Lifecycle Finite State Machine (ADR-0081)

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
| `Discovered` | `PluginDiscovered` | Plugin manifest parsed from disk; paths validated |
| `Verified` | `PluginVerified` | Schema and signature verification passed |
| `Resolved` | `PluginResolved` | Dependencies, capabilities, and port bindings resolved |
| `Activated` | `PluginActivated` | Plugin loaded into memory, UDS socket opened |
| `Quiesced` | `PluginQuiesced` | In-flight effects drained; safely paused |
| `Faulted` | `PluginFaulted` | Failure recorded in ledger; isolated |
| `Retired` | `PluginRetired` | Sockets closed, tmpfs workspace unmounted |
