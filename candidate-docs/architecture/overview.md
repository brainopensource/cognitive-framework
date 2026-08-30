---
id: arch.system.overview
canonical_id: arch.system.overview
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: system-architecture
canonical_for:
  - system boundary
  - subsystem responsibility map
  - dependency direction
  - primary flow index
purpose: Provide the top-level architectural overview, subsystem boundary map, hexagonal dependency lattice, and primary execution flow.
audience:
  - newcomer
  - developer
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-002
  - E-B-007
  - E-B-011
  - E-B-017
  - E-B-021
  - E-B-022
  - E-B-023
  - E-B-024
  - E-B-025
  - E-B-026
  - E-B-042
  - E-B-043
  - E-B-047
relationships:
  - arch.system.boundaries
  - arch.system.data-flow
  - arch.runtime.execution
  - arch.trust.kernel
  - arch.agency.turns
  - arch.state.causal
  - arch.composition.extensibility
  - arch.orchestration.delegation
  - arch.memory.learning
  - arch.assurance.evaluation
  - arch.interfaces.clients
reviewer: documentation-specialist
confidence: high
---

# Vanguard System Architecture Overview

## Purpose
This document is the canonical architecture owner for the top-level Vanguard system boundary, the 12-subsystem responsibility map, the hexagonal dependency hierarchy, and the primary execution flow index across the codebase.

## Scope
- Substrate boundary and core operational model at analysis subject SHA `9fd444674bf3a97f2673ff36a5f5928ef046c574`.
- The 12 canonical subsystems (`SUB-B-01` through `SUB-B-12`).
- System-wide architecture boundaries and isolation perimeters (detailed in [`arch.system.boundaries`](boundaries.md)).
- Primary end-to-end execution flow and causal event propagation (detailed in [`arch.system.data-flow`](data-flow.md)).
- Hexagonal boundary lattice and dependency direction enforcement (`INV-B-001`).
- Summary of known partial, experimental, or obsolete implementation surfaces.

## Non-responsibilities
- Exact port and SPI signatures (owned by [`ref.ports`](../backend/reference/ports.md)).
- Specific CLI commands and options (owned by [`ref.commands`](../backend/reference/commands.md)).
- Detailed turn loop cognition mechanics (owned by [`arch.agency.turns`](../backend/architecture/agency.md)).

## AS_BUILT Status
- `IMPLEMENTED` — The substrate architecture operates as an event-sourced hexagonal runtime with strict dependency boundaries and single-session execution authority.

---

## 1. System Boundary & Operating Model

Vanguard is a Python-first recursive agency substrate with an interactive TypeScript/React/Ink CLI (`vg`). The architecture coordinates cognitive model planning, privileged effect mediation, immutable event-sourced persistence, and external assurance scoring into a unified, fail-closed runtime.

```text
+-------------------------------------------------------------+
|                    CLIENTS & TOOLS (CLI / UI)               |
|   Python vanguard CLI * TypeScript vg CLI * Studio          |
+------------------------------+------------------------------+
                               |
+------------------------------v------------------------------+
|                    RUNTIME COMPOSITION                      |
|   Manifest Loader * Profiles * HarnessSession (Single Auth) |
+--------------+-------------------------------+--------------+
               |                               |
+--------------v--------------+ +--------------v--------------+
|     AGENCY TURN ENGINE      | |       KERNEL TCB CORE       |
|  EpisodeEngine (Sequential) | |  13-Stage Dispatch (S0-S12) |
|  Layered Context (L1-L4)    | |  Capabilities & Typed Budget|
+--------------+--------------+ +--------------+--------------+
               |                               |
+--------------v-------------------------------v--------------+
|                HEXAGONAL PORTS & SPI PROTOCOLS              |
|   IPlanner * IContext * IToolkit * IMemory * IEvalGate      |
+------------------------------+------------------------------+
                               |
+------------------------------v------------------------------+
|               ADAPTERS & DURABLE PERSISTENCE                |
|   LLM Providers * SQLite WAL * Bubblewrap * Evaluator RPC   |
+-------------------------------------------------------------+
```

---

## 2. The 12 Canonical Subsystems

| Subsystem ID | Name | Status | Primary Architectural Responsibility | Detailed Reference |
|---|---|---|---|---|
| `SUB-B-01` | Domain contracts & projections | `IMPLEMENTED` | Pure values, JCS canonicalization, event contracts, deterministic reducers. | [`arch.state.causal`](../backend/architecture/causal-state.md) |
| `SUB-B-02` | Ports and SPIs | `IMPLEMENTED` | Hexagonal port protocols and 5 frozen SPI contracts. | [`ref.ports`](../backend/reference/ports.md) |
| `SUB-B-03` | Kernel trusted core | `IMPLEMENTED` | Generic effect mediation, 13-stage dispatch, capability grants, typed budgets (<= 1438 LOC). | [`arch.trust.kernel`](../backend/architecture/kernel.md) |
| `SUB-B-04` | Agency turn engine | `IMPLEMENTED` | Sequential turn loop, prompt layers (L1-L4), protocol recovery. | [`arch.agency.turns`](../backend/architecture/agency.md) |
| `SUB-B-05` | Causal state & artifacts | `IMPLEMENTED` | Append-only event ledger, content-addressed blobs, verified checkpoints. | [`arch.state.causal`](../backend/architecture/causal-state.md) |
| `SUB-B-06` | Runtime composition | `IMPLEMENTED` | Manifest compilation, profile binding, `HarnessSession` lifecycle. | [`arch.runtime.execution`](../backend/architecture/runtime-execution.md) |
| `SUB-B-07` | Delegation & topology | `PARTIAL` | Mediated child spawning, `mhf.topology/1` lowering to sequential turns. | [`arch.orchestration.delegation`](../backend/architecture/delegation-topology.md) |
| `SUB-B-08` | Memory & governed learning | `IMPLEMENTED` | Scoped retrieval authorization, skill extraction, immutable promotion. | [`arch.memory.learning`](../backend/architecture/memory-learning.md) |
| `SUB-B-09` | Evaluation & assurance | `IMPLEMENTED` | Trajectory capture, exterior evaluation daemon (UID 10002), signed verdicts. | [`arch.assurance.evaluation`](../backend/architecture/assurance-evaluation.md) |
| `SUB-B-10` | Packs & manifests | `IMPLEMENTED` | Domain pack layout, tool schemas, plugin lifecycle state machine. | [`arch.composition.extensibility`](../backend/architecture/composition-extensibility.md) |
| `SUB-B-11` | Application interfaces | `PARTIAL` | Python CLI, TypeScript `vg`, `vg.4` daemon protocol, Studio gateway. | [`arch.interfaces.clients`](../backend/architecture/application-interfaces.md) |
| `SUB-B-12` | Schemas & wire contracts | `IMPLEMENTED` | JSON schemas, typed code generation, test vectors, compatibility readers. | [`ref.schemas`](../backend/reference/schemas.md) |

---

## 3. Hexagonal Dependency Lattice (`INV-B-001`)

The production codebase strictly enforces a unidirectional layer hierarchy:

$$\\text{domain} \\leftarrow \\text{ports} \\leftarrow \\text{kernel} \\leftarrow \\text{agency} \\leftarrow \\text{runtime} \\rightarrow \\text{adapters}$$

- Lower layers never import higher layers.
- Kernel and Domain are strictly domain-blind (`INV-B-002`).
- Concrete Adapters implement Port protocols and never import Kernel or Agency.
- Apps slot (`vanguard/packages/apps/`) is reserved as a client slot of runtime.

---

## 4. Primary Execution Flow

A typical task execution flows through the architecture as follows:

1. **Invocation**: Operator runs `vanguard run "<task>"` or `vg run "<task>"`.
2. **Composition & Identity**: `runtime.compose` parses the pack manifest and resolves `ExecutionProfile`, constructing the immutable `RunPlan` ($D_H, D_R$).
3. **Session Activation**: `HarnessSession` starts, opens the SQLite WAL event store, binds `LedgerEmitter`, and emits `RunStarted`.
4. **Turn Cognition**: `agency.EpisodeEngine` compiles context layers L1-L4 and prompts the LLM via `ModelPort`.
5. **Kernel Dispatch**: Proposed tool effects pass to `Kernel.dispatch()`. The kernel resolves adapters, verifies capabilities, reserves budgets, commits `EffectStarted` (fsync), executes the physical adapter, commits budget, releases leases, and appends `EffectCompleted`.
6. **Ingestion & Loop**: Receipts are ingested into context; the turn loop repeats until completion.
7. **Exterior Assurance**: `EvidenceCaptureService` packages the trajectory, calls `vanguard-evaluator` over RPC, and writes `VerdictRecorded` with the evaluator signature.
8. **Teardown**: Stores flush, leases close, and final `RunResult` returns to the client.

---

## 5. Known Implementation Realities & Non-Blocking Findings

- **`UNR-B-001` (StartRun Profile Default)**: TypeScript CLI omits `profileId` by default, triggering an unsupported legacy default in `RuntimeService` unless explicitly specified.
- **`UNR-B-002` (Isolated Workflow Scheduler)**: `mhf.topology/2` workflow schedulers are unit-tested in isolation but not yet wired into the canonical runtime harness.
- **`UNR-B-003` (CLI Command Asymmetry)**: Python and TypeScript CLIs provide distinct, non-identical command subsets without a unified registry.
- **`UNR-B-004` (Legacy Compatibility Seam)**: `Runtime.execute_harness` remains public for legacy tests though retired from production paths.
- **`UNR-B-008` (Empty `apps/` Slot)**: `vanguard/packages/apps/` contains only an empty package marker.

---

## Implementation Evidence

- **Hexagonal Boundary Enforcement**: `tools/linters/check_boundaries.py` (checked across 453 files).
- **TCB Budget Linter**: `tools/linters/check_tcb_budget.py` (1384 LOC <= 1438).
- **Lifecycle Integration Tests**: `test/contracts/test_b2_lifecycle_integration.py`, `test/falsifiers/test_rf94_single_runtime_authority.py`.
