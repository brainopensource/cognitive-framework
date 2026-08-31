---
id: arch.runtime.execution
canonical_id: arch.runtime.execution
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: runtime-execution
canonical_for:
  - compose/activate/run lifecycle
  - profile bootstrap boundary
  - session ownership
  - recovery entry
purpose: Explain the end-to-end runtime execution lifecycle, HarnessSession ownership, RunPlan identity, and crash recovery entry points.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-009
  - E-B-019
  - E-B-020
  - E-B-021
  - E-B-022
  - E-B-023
  - E-B-024
  - E-B-025
  - E-B-026
  - E-B-028
  - E-B-029
  - E-B-030
  - E-B-052
relationships:
  - arch.system.overview
  - arch.trust.kernel
  - arch.agency.turns
  - arch.state.causal
  - ref.configuration
  - ref.commands
reviewer: documentation-specialist
confidence: high
---

# Runtime Execution Architecture

## Purpose
This document is the canonical architecture owner for the end-to-end runtime lifecycle: manifest composition, execution profile binding, `RunPlan` identity construction, `HarnessSession` lifecycle management, turn engine handoff, and cold recovery entry points (`RF-94`).

## Scope
- The unified construction pipeline: `compose` $	o$ `activate` $	o$ `begin_episode` $	o$ `execute_turns` $	o$ `teardown`.
- `RunPlan` immutable identity preimage and environment digest ($D_R$).
- `HarnessSession` session management and its relationship to the single ledger writer (`LedgerEmitter`).
- Process teardown, artifact capture, and terminal result synthesis.
- Compatibility seams and legacy entry points (`UNR-B-004`).

## Non-responsibilities
- Kernel TCB S0–S12 effect dispatch sequence (owned by [`arch.trust.kernel`](kernel.md)).
- Turn-level model context compilation and prompt layers (owned by [`arch.agency.turns`](agency.md)).
- Exact event envelope schemas and field definitions (owned by [`ref.events`](../reference/events.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Single runtime authority (`HarnessSession`) orchestrates all composition, activation, execution, and teardown across the substrate (`RF-94`).
- `PARTIAL` — Current composition exposes context/index seams, but manifest context-policy binding, optional repository-intelligence packets, coding completion admission, and semantic task-state continuation are **v0.9.2 targets** described below.

---

## 1. The Unified Execution Lifecycle

Execution follows a deterministic sequence from manifest parsing to final result emission:

```text
1. CLI / Daemon Command (StartRun / run)
       │
       ▼
2. Composition Compiler (vanguard.packages.runtime.compose)
   - Parses manifest.json -> FrozenComposition (D_H)
       │
       ▼
3. Execution Profile Resolution (vanguard.packages.runtime.profiles)
   - Resolves ExecutionProfile -> profile_digest (D_R)
   - Constructs RunPlan(run_id, D_H, D_R, budget)
       │
       ▼
4. HarnessSession Instantiation (vanguard.packages.runtime.session)
   - Initializes Kernel, Governor, Policy, LedgerEmitter
   - Emits RunStarted / EpisodeStarted
       │
       ▼
5. EpisodeEngine Execution (vanguard.packages.agency)
   - Executes sequential turn loop (Observe -> Propose -> Dispatch -> Ingest)
       │
       ▼
6. Teardown, Evidence & Evaluation (vanguard.packages.runtime.evaluator_gateway)
   - Emits EpisodeCompleted, captures Trajectory, records VerdictRecorded
   - Releases all leases, closes stores -> Synthesizes RunResult
```

---

## 2. Immutable Run Identity (`RunPlan` & $D_R$)

To ensure complete reproducibility and formal auditability (`RF-87`):
- **$D_H$ (Harness Composition Digest)**: Cryptographic hash of the compiled agent pack, tools, prompts, and SPI component bindings.
- **$D_R$ (Execution Profile Digest)**: Cryptographic hash of the resolved containment backend, workspace mode, approval policy, persistence mode, and retention rules.
- **`RunPlan`**: Combines `run_id`, $D_H$, $D_R$, initial task brief, and budget allocations into a single immutable root record emitted in `RunStarted`.

---

## 3. Session Ownership & Single Ledger Writer

`HarnessSession` acts as the single runtime authority (`RF-94`):
- **Sole Facade**: Components within a session interact exclusively through session-provided facades.
- **Single Emitter Ownership**: All events written to SQLite WAL flow through `HarnessSession.emitter` (`LedgerEmitter`), ensuring unbroken hash-chaining and strict writer role validation (`PRIVILEGED_KIND_OWNERS`).
- **Governor Coordination**: `HarnessSession` manages root budget leases and passes attenuated child leases to the kernel.

---

## 4. Crash Recovery Entry Point (`resume`)

When a run is resumed from disk (`vanguard resume --run-id <ID>`):
1. `HarnessSession.resume_from_ledger()` initializes store connections and reads the event range from SQLite WAL.
2. The domain reducers fold the event history to rebuild `LedgerState` and `AgentView` (`RF-25`).
3. Pending leases and uncommitted effects are reconciled.
4. `HarnessSession` re-enters `EpisodeEngine` at turn $K+1$, resuming execution seamlessly without data loss.

---

## 5. Compatibility Seam (`UNR-B-004`)

- `Runtime.execute_harness` (`vanguard/packages/runtime/compose.py`) is an obsolete legacy entry point that remains in the codebase for backwards compatibility and test verification. All production paths invoke `HarnessSession` directly.

---

## 6. Context and Completion Policy Binding

The existing single composition root remains authoritative. Code-pack preset overlays compile through the same composition path and only change bounded cognition/context ceilings; they do not widen capabilities or create a second runtime.

`HarnessSession` should bind the manifest-resolved context policy into `ContextCompiler` and optionally bind an `IContextManager` backed by `IndexPort`. Repository intelligence is provider-neutral and authority-free:

```text
Task + repository snapshot
        -> code-pack IContextManager
        -> optional IndexPort/provider adapter
        -> bounded ContextPacket
        -> existing ContextCompiler
```

LDA, SCIP-style indexes, and future providers are substitutable adapters/projections. Vanguard must not import or require LDA. A deterministic filesystem index remains the fallback when an external index is absent, empty, stale, or invalid. Provider output selects references; it cannot propose effects, grant capabilities, or override canonical documentation, source, tests, or ledger facts.

The target `ContextPacket` records at minimum the task digest, repository snapshot digest, provider identity/version, query digest, selected documents/symbols/files/tests/dependency edges, estimated tokens, omissions, and an overall packet digest. It is bounded by the manifest context budget and captured as evidence sufficient to reproduce selection.

The same composition path binds a generic completion-admission policy. `EpisodeEngine` asks whether completion is admissible; the code pack interprets coding verification, while runtime records the decision and its evidence reference. External evaluation remains a later, independent lifecycle stage.

`D_H` must change when component bindings or durable context/admission policy change. Runtime evidence must retain enough identity to distinguish control and treatment configurations in benchmark comparisons.

## 7. Semantic Continuation

Cold resume already reconstructs safety/accounting state and reconciles effects. `CodingTaskState` now provides the compact durable continuation value: task class, completion requirements, plan/discoveries/dead ends, implicated and modified files, route decisions, evidence-gated TODOs, latest verification, settled effects, next action, and remaining budgets. This packet is derived state; missing evidence must fail explicitly or trigger regrounding rather than silently invent context.

---

## Implementation Evidence

- **Session Controller**: `vanguard/packages/runtime/session.py` (`HarnessSession`).
- **Composition Root**: `vanguard/packages/runtime/compose.py` (`compose_harness`, `RunPlan`).
- **Profile Resolution**: `vanguard/packages/runtime/profiles.py` (`resolve_profile`, `ExecutionProfile`).
- **Lifecycle Integration Tests**: `test/contracts/test_b2_lifecycle_integration.py`, `test/falsifiers/test_rf94_single_runtime_authority.py`, `test/runtime/test_harness_session.py`.
