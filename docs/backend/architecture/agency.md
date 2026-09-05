---
id: arch.agency.turns
canonical_id: arch.agency.turns
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: agency-turn-engine
canonical_for:
  - EpisodeEngine lifecycle
  - proposal and recovery semantics
  - context compilation
  - runtime handoff
purpose: Detail the sequential turn loop, context compiler layers, proposal recovery state machine, and runtime handoff.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: d639ec4bda5ea7d8836a182393498a31fc43ea1a
version: 0.9.2a2
last_verified: 2026-09-03
evidence:
  - E-B-010
  - E-B-019
  - E-B-020
  - E-B-026
relationships:
  - arch.system.overview
  - arch.trust.kernel
  - arch.state.causal
  - ref.manifests
reviewer: documentation-specialist
confidence: high
---

# Agency & Turn Engine Architecture

## Purpose
This document is the canonical architecture owner for the `EpisodeEngine` sequential turn loop, layered context compilation (L1–L4), proposal parsing and protocol recovery state machines, and runtime handoff boundaries.

## Scope
- Episode identity and lifecycle states.
- The step-by-step turn loop: Observe $	o$ Compile $	o$ Propose $	o$ Authorize $	o$ Dispatch $	o$ Ingest.
- Layered L1-L5 context compiler architecture (`ContextCompiler`) and compaction strategies.
- Protocol recovery mechanisms for malformed model outputs (`protocol_recovery.py`).
- Hand-off interface between `agency` and `kernel.dispatch`.

## Non-responsibilities
- Domain pack tool definitions and prompt templates (owned by [`ref.manifests`](../reference/manifests.md) and [`guide.compose-agent`](../guides/compose-an-agent.md)).
- Kernel effect mediation, leases, and budgets (owned by [`arch.trust.kernel`](kernel.md)).
- External evaluation scoring and verdicts (owned by [`arch.assurance.evaluation`](assurance-evaluation.md)).

## AS_BUILT Status
- `IMPLEMENTED` — The bounded sequential episode engine, L1-L5 compiler, injected protocol-recovery pipeline, generic completion-admission callback, and runtime meta-controller consultation are integrated on the canonical run path.
- `PARTIAL` — `CodingTaskState` and code-pack repository/context/verification middleware exist as mechanisms, but one end-to-end Coding Max composition does not yet integrate the complete durable plan, classified task recovery, multi-file/greenfield policy, and product qualification described in Section 6.

---

## 1. Episode Identity & Lifecycle

An **Episode** is the bounded execution scope for an agent cognition loop.
- **Identity**: Every episode carries a UUIDv7 `episode_id` and is bound to a parent `run_id` and lineage trace.
- **Self-Grading Separation (`INV-B-009`)**: An episode terminates; it does not evaluate or grade itself. Agency cannot import evaluators or mint evaluation verdicts.

```text
[ Initialized ] ---> [ Active Turn Loop ] ---> [ Terminal State ]
                            ^          |
                            +----------+
```

---

## 2. The Sequential Turn Loop (`EpisodeEngine`)

Each turn in `EpisodeEngine.step()` executes a sequential cognition cycle (`INV-B-008`):

1. **Context Compilation**: `ContextCompiler.compile()` generates a token-bounded `ContextBundle` from frozen composition layers and recent turn history.
2. **Model Sampling**: Invokes model provider adapter with compiled messages, active tool schemas, and sampling constraints.
3. **Proposal Parsing**: The raw model response is parsed into a structured `Proposal` (`ActionProposal`, `SpawnProposal`, `YieldProposal`, `CompleteProposal`).
4. **Proposal Recording**: The engine appends `ProposalProduced` to the local turn state.
5. **Kernel Dispatch Handoff**:
   - The engine builds an `EffectRequest` containing the action descriptor and principal credentials.
   - The engine invokes `Kernel.dispatch(request, grant)`.
   - The kernel executes the S0–S12 pipeline (authorization, lease reservation, physical dispatch, receipt emission).
6. **Receipt Ingestion**: The resulting `EffectReceipt` and observations are fed back into `ContextCompiler.ingest()`.
7. **Turn Advance / Termination**: The engine checks remaining budget, turn limits, and proposal disposition to decide whether to continue or terminate.

---

## 3. Layered Context Architecture (`ContextCompiler`)

The context compiler organizes prompt tokens into five layers ordered by mutation rate:

```text
+-------------------------------------------------------------+
| Layer 1 (L1): System Role & Output Contract                 | (Frozen at build)
+-------------------------------------------------------------+
| Layer 2 (L2): Active Tool Specifications                    | (Frozen at composition)
+-------------------------------------------------------------+
| Layer 3 (L3): Environment Conventions & Retrieved Priors    | (Frozen within task)
+-------------------------------------------------------------+
| Layer 4 (L4): Task Brief & Stable Task Notes                | (Stable within task)
+-------------------------------------------------------------+
| Layer 5 (L5): Turns, Results & Dynamic Notes                | (Compacted dynamically)
+-------------------------------------------------------------+
```

### Prefix Stability & KV-Caching
Layers L1–L3 are deterministically hashed and remain byte-identical across turns. L4 is stable within the task; L5 is the only layer mutated each turn. Cache participation is observed through digests and receipts rather than assumed from layout alone. Product `ContextPacket` values bind `WorkspaceEpoch` (`tree_hash` ← treeHash, `index_digest` ← indexDigest, `source_revision` ← sourceRevision, `compiled_at_turn` ← compiledAtTurn). Epoch is a new field on the existing packet, not a second compiler; stale or missing epoch cannot admit `completed`.

### Context Compaction
When the context approaches the token budget ceiling, `CompactionEngine` applies structured compaction to L5 while preserving higher layers:
- Summarizes older observation blocks.
- Preserves the initial user brief and the $N$ most recent turn receipts.
- Emits a `ContextCompacted` event to ensure reproducibility.

---

## 4. Proposal Malformation & Protocol Recovery

LLMs may produce outputs that violate tool schema syntax or fail JSON parsing. Rather than crashing, `agency.episode.protocol_recovery` implements a deterministic recovery state machine:

| Malformation Category | Recovery Strategy | Escalation Threshold |
|---|---|---|
| Invalid JSON Syntax | Inject repair prompt with schema excerpt; retry proposal. | Max 2 retries per turn. |
| Unknown Tool Name | Inject valid tool list; request selection. | Max 2 retries per turn. |
| Missing Required Field | Inject missing parameter description. | Max 2 retries per turn. |
| Repeated Failure | Elevate to `RecoveryDecision.FAIL_TURN` with synthetic error receipt. | Halts turn after 3 attempts. |

---

## 5. Terminal Dispositions (`RunTermination`)

Episodes conclude with one of the following terminal states:

- **`COMPLETED`**: Agent submitted `CompleteProposal` indicating task satisfaction.
- **`BUDGET_EXHAUSTED`**: Additive budget (`usd_micros`, `millis`, `tokens`, `bytes`) or structural limits reached.
- **`MAX_TURNS_EXCEEDED`**: Step limit reached without completion.
- **`ESCALATED`**: Action halted awaiting operator approval.
- **`CANCELLED`**: Explicit cancellation command received from client.
- **`RUNTIME_ERROR`**: Unrecoverable kernel or adapter fault.

---

## 6. Coding Harness Control Loop

> **PARTIAL AS_BUILT / PRODUCT TARGET.** Generic completion admission,
> protocol recovery, context layering, meta-control, and mediated execution are
> integrated. The complete Coding Max product loop remains a staged code-pack
> and application composition, not a new agency engine.

Vanguard owns the generic bounded turn, dispatch, event-observation, budget, and completion-admission seams. Coding semantics remain above the substrate in the code pack/harness: repository discovery, patch state, test selection, test-result interpretation, and the definition of an applicable coding verification. No coding vocabulary or repository-intelligence dependency belongs in the domain-blind kernel.

The coding harness targets the following outcome-driven state machine:

```text
INGEST -> DISCOVER -> PLAN -> EDIT -> VERIFY_TARGETED
                         ^              |
                         |              +-> RECOVER --+
                         |                            |
                         +----------------------------+
                                        |
                                        +-> VERIFY_BROAD -> COMPLETE
                                                   |
                                                   +-> RECOVER | ABANDON
```

Transitions depend on observed receipts, not merely on the attempted verb. In particular, attempting a patch does not enter verification unless the complete patch was applied, and requesting completion does not enter `COMPLETE` unless the configured admission policy accepts fresh verification.

### 6.1 Durable coding task state

The code pack should maintain a replayable value equivalent to:

```text
SemanticTaskState / CodingTaskState (`domain/task_state.py`)
  task_identity
  repository_snapshot
  goal
  constraints
  current_plan
  hypotheses
  inspected_files
  relevant_symbols
  modified_files
  verification_plan
  last_verification
  classified_failure
  next_action
  settled_effects
  remaining_budgets
```

This is a coding-pack projection, not a new authoritative state store. Durable facts and referenced artifacts remain in the causal ledger; the value is reconstructed by folding them. Compaction must preserve the goal and constraints, current plan, modified files, latest relevant failure, latest verification, settled effects, next action, and remaining budgets. Raw old observations and duplicate reads may be summarized.

### 6.2 Completion admission and verification freshness

The framework may expose a generic completion-admission callback. The code pack supplies the coding policy. For a patch-producing task, the target rule is:

$$
\operatorname{CompletionAdmitted} =
\operatorname{FinishRequested}
\land \operatorname{RequirementsSatisfied}
\land \operatorname{VerificationApplicable}
\land \operatorname{VerificationExecuted}
\land \operatorname{VerificationPassed}
\land \operatorname{VerificationFresh}
$$

`VerificationFresh` means the successful receipt is bound to the current workspace/postimage digest and occurred after the most recent accepted edit. A zero-exit command that collected zero applicable tests is not a passing test verification. Analysis-only, documentation-only, greenfield, and repositories-without-tests require an explicit pack policy rather than an implicit bypass.

Local verification is an operational completion condition; it never replaces the independent evaluator/oracle owned by [`arch.assurance.evaluation`](assurance-evaluation.md).

### 6.3 Typed recovery policy

The initial coding failure taxonomy is:

```text
CONTEXT_INSUFFICIENT     CONTEXT_STALE
TOOL_SCHEMA_INVALID     TOOL_EXECUTION_FAILED
PATCH_PREIMAGE_MISMATCH PATCH_PARTIAL
TEST_COLLECTION_EMPTY   TEST_FAILED
VERIFICATION_STALE      PROVIDER_TRANSIENT
PROVIDER_PERMANENT      BUDGET_EXHAUSTED
NO_PROGRESS             PREMATURE_FINISH
```

Each class has a bounded retry limit and a recovery action. A retry is admissible only when the failure is retryable, budget remains, and the next action or information state differs materially. Repeating the same action with the same arguments against unchanged state is `NO_PROGRESS`, not recovery. Provider adapters may perform transport retries; the harness separately decides whether a failed turn or task action should be retried.

### 6.4 Current ownership, remaining integration and falsifiers

- **Generic framework seams (AS_BUILT)**: completion-admission result and typed
  protocol recovery in `vanguard/packages/agency/episode/`; L1-L5 compilation
  in `vanguard/packages/agency/context/`; guarded meta-control and manifest
  binding in `vanguard/packages/runtime/session.py`.
- **Coding mechanisms (AS_BUILT, not one accepted product loop)**:
  `CodingTaskState`, context ranking, symbol/import analysis, multi-file
  completeness, test-output parsing, and verification gating.
- **Coding Max ownership (TARGET)**: task classification, plan/TODO policy,
  repository context selection, domain failure interpretation, verification
  applicability, greenfield evidence policy, and fast/balanced/max presets in
  the code pack; a thin `apps/coding_max` facade selects and invokes the
  composition.
- **Required falsifiers**: premature finish, zero-test success, stale
  verification after edit, partial patch, repeated identical action, failed-test
  repair, path escape, adapter-to-app import, host subprocess bypass,
  multi-file omission, greenfield silent bypass, and fresh-process
  reconstruction of the next action.

---

## Implementation Evidence

- **Episode Engine**: `vanguard/packages/agency/episode/engine.py`, `state.py`, `protocol_recovery.py`.
- **Context Compiler**: `vanguard/packages/agency/context/compiler.py`, `compaction.py`, `layers.py`.
- **Harness Session Integration**: `vanguard/packages/runtime/session.py`.
- **Tests**: `test/agency/test_episode.py`, `test/agency/test_context_compiler.py`, `test/contracts/test_m5a_agent_view.py`.

---

## Architectural Decisions & Philosophical Rationale

### DEC-04 — Agent as Ephemeral Projection over Persistent Entity

- **Decision:** An agent is an ephemeral identity, policy, and causal projection boundary, not a long-running, stateful in-memory process.
- **Rationale:** Stateful agent processes leak memory, fail across process boundaries, and complicate multi-agent coordination. Reconstructing agent perspective on demand from event lineage guarantees stateless resumption and recovery.
- **Rejected alternative:** Persistent thread-per-agent or actor-per-agent daemons retaining in-memory cognitive state.
- **Reversal condition:** Evidence that cognitive streaming continuation requires low-latency in-memory state that cannot be reconstructed via prefix-cached token buffers.

### DEC-08 — Sequential Turn Simplicity until Concurrency Proves Value

- **Decision:** The canonical turn loop and topology execution remain strictly unary and sequential by default; concurrent dispatch is admitted only when justified by measured wall-time advantage on provably disjoint operations.
- **Rationale:** Unrestricted concurrency introduces non-determinism, race conditions in budget accounting, replay divergence, and complex recovery semantics without guaranteed performance improvement.
- **Rejected alternative:** Default asynchronous / multi-threaded turn dispatch across all agent nodes.
- **Reversal condition:** Preregistered empirical benchmark evidence demonstrating $\ge 20\%$ median wall-time reduction with byte-identical result ordering on disjoint, read-only operations.

