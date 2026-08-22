---
status: living
id: architecture-index
class: architecture
authority: descriptive
canonical_for:
  - system-architecture-index
source_of_truth:
  - docs/SPEC.md
derived_from:
  - vanguard/packages/kernel/dispatch.py
  - vanguard/packages/runtime/compose.py
  - vanguard/packages/agency/episode/engine.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Vanguard / AETHER Architecture Index

> **Classification:** Descriptive Architecture.  
> **Authority:** Non-normative. Governing normative law lives in [`docs/SPEC.md`](../SPEC.md) and [`docs/04_annex/`](../04_annex/).

This directory contains verified architectural views, C4 models, sequence diagrams, state machines, and traceability mappings for the Vanguard / AETHER recursive agency substrate.

---

## Architecture Modules

| Module | Scope & Focus | Maturity |
|---|---|---|
| [`c4_context.md`](c4_context.md) | C4 Level 1: System boundary, operators, evaluators, model providers, and environment | `AS_BUILT` |
| [`c4_container.md`](c4_container.md) | C4 Level 2: Python control plane, CLI client, SQLite WAL store, sandbox container, evaluator daemon | `AS_BUILT` |
| [`c4_component.md`](c4_component.md) | C4 Level 3: Domain, Ports, Kernel (TCB), Agency, Runtime, and Adapters | `AS_BUILT` |
| [`sequences.md`](sequences.md) | Sequence flows: Compose, S0–S12 effect dispatch, signed evaluation, trajectory assembly, cold recovery | `AS_BUILT` |
| [`state_machines.md`](state_machines.md) | Finite state machines: Episode turn loop, plugin lifecycle FSM, and lease management | `AS_BUILT` |
| [`glossary.md`](glossary.md) | Core concepts: A-B-C-D operating foundation, Three Planes, TCB, WAL, $D_H/D_R/D_X$, 6D tensor | `AS_BUILT` |
| [`traceability_matrix.md`](traceability_matrix.md) | Full bidirectional traceability: Concept $\leftrightarrow$ Law $\leftrightarrow$ ADR $\leftrightarrow$ Schema $\leftrightarrow$ Symbol $\leftrightarrow$ Falsifier $\leftrightarrow$ Milestone | `AS_BUILT` |

---

## The Hexagonal Lattice Flow

```text
domain ← ports ← kernel ← agency ← runtime → adapters
         (apps/ is a client slot of runtime)
```

1. **`domain/`**: Pure stdlib Python. Primitives, events, wire contracts, and selector algebra.
2. **`ports/`**: Hexagonal interfaces defining boundary contracts.
3. **`kernel/`**: Pure security core ($\le 1438$ LOC TCB budget). 13-stage dispatch pipeline (S0–S12).
4. **`agency/`**: Recursive turn engine (`EpisodeEngine`), context compaction, and subagent spawn.
5. **`runtime/`**: Composition, wiring, single-writer ledger emitter, and event store.
6. **`adapters/`**: Concrete implementations of port protocols (Model providers, Bubblewrap sandbox, Evaluator daemon, SQLite WAL).
