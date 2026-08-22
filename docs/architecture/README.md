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
| [`sequences.md`](sequences.md) | Verified dispatch/evaluation flows plus explicitly labelled RF-25 target flow | `MIXED — LABELLED PER SECTION` |
| [`state_machines.md`](state_machines.md) | Current episode mechanism plus ADR-0081 target plugin FSM | `MIXED — LABELLED PER SECTION` |
| [`glossary.md`](glossary.md) | Core concepts: A-B-C-D operating foundation, Three Planes, TCB, WAL, $D_H/D_R/D_X$, 6D tensor | `AS_BUILT` |
| [`traceability_matrix.md`](traceability_matrix.md) | Traceability with an explicit maturity column; queued rows are not implementation claims | `MIXED — LABELLED PER ROW` |

---

## The Hexagonal Lattice Flow

```text
domain ← ports ← kernel ← agency ← runtime → adapters
         (apps/ is a client slot of runtime)
```

1. **`domain/`**: Pure stdlib Python. Primitives, events, wire contracts, and selector algebra.
2. **`ports/`**: Hexagonal interfaces defining boundary contracts.
3. **`kernel/`**: Pure security core ($\le 1438$ LOC TCB budget). 13-stage dispatch pipeline (S0–S12).
4. **`agency/`**: Turn engine (`EpisodeEngine`), context compaction, and current child construction; mediated `agent.spawn` is M-6 work.
5. **`runtime/`**: Composition, wiring, single-writer ledger emitter, and event store.
6. **`adapters/`**: Concrete implementations of port protocols (Model providers, Bubblewrap sandbox, Evaluator daemon, SQLite WAL).
