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
last_verified: 2026-09-03
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
- `PARTIAL` — Current composition exposes context/index seams, registered Coding Max presets, mediated completion admission for those presets, and semantic task-state continuation seams. Full task-state persistence and repository-scale qualification remain open gates.

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

The target `ContextPacket` records at minimum the task digest, repository snapshot digest, provider identity/version, query digest, selected documents/symbols/files/tests/dependency edges, estimated tokens, omissions, overall packet digest, and a product `WorkspaceEpoch` (`treeHash`, `indexDigest`, `sourceRevision`, `compiledAtTurn`). Epoch is the single authority for packet freshness: a write changes the tree hash; a stale or missing epoch MUST NOT justify `completed`. It is bounded by the manifest context budget and captured as evidence sufficient to reproduce selection.

The same composition path binds a generic completion-admission policy. `EpisodeEngine` asks whether completion is admissible; the code pack interprets coding verification, while runtime records the decision and its evidence reference. External evaluation remains a later, independent lifecycle stage.

Workspace verification freshness is bound to a material snapshot digest. For a
Git environment that digest covers the current HEAD and porcelain worktree
state; observation counters belong only to the snapshot identifier and MUST NOT
change the digest of an otherwise unchanged workspace. This permits a second
read to validate a receipt while still invalidating it immediately after a
material patch.

The backend facade exposes `vg code run`, `status`, `resume`, `evidence`, and
`cost`. These commands are thin clients of `ApplicationService`; preset names
resolve to `vg-code-fast`, `vg-code-balanced`, or `vg-code-max` manifests and
do not create a second runtime or persistence path. Coding Max completion is
admitted only after mediated patch and test facts have produced a fresh
verification receipt bound to the current task digest, frozen composition
digest, workspace postimage, exact verification command/test subject, and
receipt identity. Missing or foreign bindings fail closed; legacy receipt
readers remain available only when no current binding is requested.

`D_H` must change when component bindings or durable context/admission policy change. Runtime evidence must retain enough identity to distinguish control and treatment configurations in benchmark comparisons.

### 6.1 Truthful terminal projection

`project_terminal_outcome` in `runtime/app_service.py` is the single product projection used by
the generic entrypoint and `ApplicationService.run()`/`resume()`; the Coding Max facade receives
the same value transitively through `RunResult`. It preserves the normalized terminal, including
`abstained`, so refusal is never presented as completion. `project_trajectory_outcome` in
`runtime/trajectory.py` is a separate narrowing projection shared by `mhf.trajectory/1` and `/2`:
because their frozen enum has no `abstained` member, refusal projects to `aborted`, never
`completed`. Both mappings concern termination only; acceptance/disposition remains on verdict.

### 6.2 Environment patch apply (TC-E-061)

`GitEnvironment.apply` and `FakeEnvironment.apply` share one in-memory hunk algorithm (`adapters/environment/hunks.py`). Context lines are the preimage anchor; hunk start lines are relocation hints, while declared old/new line counts must exactly match the hunk body. A declared `expected_preimage` / `expected_preimages` digest that does not match the current file fails closed as `conflict`. Bare `@@` hunks that match more than one location, empty or edit-free hunks, false line counts, and malformed hunk bodies are refused before any write. Multi-file applies still go through `AtomicMultiFileTransactionManager`: syntax preflight or a later-file refusal restores every original byte and file mode. Single-file Python syntax remains an observation receipt (S8-B-09), not a rollback. The pack toolkit `mhf.toolkit.ast-patch` reuses the same hunk/preimage rules; it is not a second patcher. CAS workspace promotion is not part of this path.

### 6.3 Provider request accounting and cache observation

`adapters/models/prompt_codec.py` is the single final serialization boundary used by the OpenRouter adapter. It counts the exact bytes posted, including native tool schemas, after route-specific cache controls are negotiated. A route may inject its exact tokenizer; without one, the codec uses the deliberately pessimistic byte-level BPE ceiling of one token per UTF-8 byte. It does not use an average character/token density as a capacity proof. Output, safety, and recovery reservations are deducted before admission and observed cache reuse never widens the input window. Cache usage remains a provider observation with explicit missingness, not a hit-rate or performance claim.

The offline LAM adapter derives each scenario turn from actual tool-result fragments only. Context bookkeeping such as the goal echo does not advance a scenario. A scenario `finish` is validated against an advertised manifest finish schema when one exists; without such a schema it remains ordinary completion text for the generic proposal translator. This preserves deterministic read → patch → test → finish replay without granting an undeclared `agency.finish` verb.

Custom execution-profile overrides accept JSON or YAML mappings. YAML parsing is provided by the locked PyYAML runtime dependency; unreadable, malformed, or security-widening profile inputs raise `ExecutionProfileError` before a profile is used.

## 7. Semantic Continuation

Cold resume reconstructs safety/accounting state and reconciles effects. `SemanticTaskState` (`CodingTaskState` alias) in `vanguard/packages/domain/task_state.py` is the compact durable continuation value: task class, completion requirements, plan/discoveries/dead ends, implicated and modified files, route decisions, evidence-gated TODOs, latest verification, settled effects, next action, remaining budgets, monotonic revision, and backlog steps. Runtime `fold_task_state` is the only producer. Resume preserves the ledger `episode_id` and compiles σ into L4/L5; it must not dump `resume_state` JSON into frozen L3. This packet is derived state; missing evidence must fail explicitly or trigger regrounding rather than silently invent context.

---

## Implementation Evidence

- **Session Controller**: `vanguard/packages/runtime/session.py` (`HarnessSession`).
- **Composition Root**: `vanguard/packages/runtime/compose.py` (`compose_harness`, `RunPlan`).
- **Profile Resolution**: `vanguard/packages/runtime/profiles.py` (`resolve_profile`, `ExecutionProfile`).
- **Lifecycle Integration Tests**: `test/contracts/test_b2_lifecycle_integration.py`, `test/falsifiers/test_rf94_single_runtime_authority.py`, `test/runtime/test_harness_session.py`.
- **Terminal Projection Falsifiers**: `test/falsifiers/test_completion_gate_scope.py`, `test/apps/coding_max/test_coding_max_facade.py`, `test/contracts/test_trajectory_v2.py`.
- **Patch Apply Falsifiers**: `test/falsifiers/test_d6_patch_context_anchoring.py`, `test/packs/code_default/test_ast_patch.py`, `test/runtime/test_atomic_multi_file_transaction.py`.
