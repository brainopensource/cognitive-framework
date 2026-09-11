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
| Layer 1 (L1): System Role, Output Contract, Capability Cards| (Frozen at composition)
+-------------------------------------------------------------+
| Layer 2 (L2): Active Tool Specifications (canonical order)  | (Frozen at composition)
+-------------------------------------------------------------+
| Layer 3 (L3): Environment Conventions & Retrieved Priors    | (Frozen at composition)
+-------------------------------------------------------------+
| Layer 4 (L4): Task Brief & Stable Task Notes                | (Stable within task)
+-------------------------------------------------------------+
| Layer 5 (L5): Turns, Results, Dynamic Notes, Goal Echo      | (Compacted dynamically)
+-------------------------------------------------------------+
```

The frozen prefix holds four declared regions in a fixed order: system
instructions, the capability-card prefix, the ordered canonical tool schemas,
and the environment/composition contract. The capability-card prefix is bounded
at 4,096 **characters** independently of token accounting (`NT-C05`); tool
schemas are emitted in a deterministic name order with canonical keys, so two
composition roots naming the same tools produce the same bytes.

### Prefix Stability, Composition Epoch & KV-Caching
`ContextCompiler.composition_epoch` is the digest of the frozen prefix bytes and
the resolved context policy, taken once at composition. It changes when the
system instructions, capability cards, tool schemas, environment contract or
context policy identity change, and never when dynamic state changes; a changed
epoch is the record that an earlier freeze — and any cache identity derived from
it — may not be reused (`NT-C01`). It is reported by `selection_identity()` as
`compositionEpoch`.

`NT-1.6` names members of behavior-affecting identity the compiler cannot
observe for itself: model dialect/route, serializer, token counter, recovery
policy and product preset. The optional `behavior_identity` constructor
argument binds them. The compiler never *uses* these values — declaring one
only makes a change to it produce a new epoch instead of silently reusing a
freeze taken under the old one. Declared members must be scalars, because they
reach a ledger fact and a structure would put unbounded material into a record
nothing can withdraw; they are sorted at the door, so two composition roots
declaring the same members in a different order share an epoch. Declaring
nothing leaves the epoch of an existing composition exactly where it was.

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

An authorization denial emitted by the kernel is a durable receipt, not a retried effect. The next bounded model turn may select a narrower permitted action, but an immediate `finish` after the denial is abandoned; completion may follow only a permitted subsequent action.

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

`MemoryView` (`aether.memory-view/1`) is the versioned, deeply immutable snapshot around that full
state; it binds cursor, lineage, reducer version, and digest-addressed evidence without introducing
a blackboard or second store. `ProtocolRecoveryState` (`aether.recovery-state/1`) is likewise
versioned and immutable, retains a maximum of 12 attempts, and explicitly migrates the supported
legacy dictionary without replaying settled effects. Its semantic policy decision is
`continue|wait|reground|replan|stop`; it is not the protocol-parser retry decision.

`ContextCompiler.compile_packet()` is the bounded packet path on the existing L1–L5 compiler.
It keeps the critical state and newest interaction, orders tools by name, omits stale evidence,
replaces oversize bodies with artifact receipts, and reserves output, safety, and recovery tokens
from the provider window. Irreducible overflow returns `CONTEXT_BUDGET_EXCEEDED` and performs no
inference. Provider-specific serialization and cache controls remain outside this compiler.

Its order of operations is contractual (`NT-C04`):

1. Item cardinality and body size are bounded **before** selection. Oversized
   tool and test output becomes a subject-bound artifact receipt at the door.
2. Only complete action/result interactions are admitted. An action whose
   result never arrived is recorded as `incomplete_interaction` and omitted;
   no orphan tool call or orphan result is ever retained.
3. Eviction triggers at the high watermark and targets the low watermark:
   stale evidence is removed, then bodies are elided into receipts, then
   low-priority evidence is dropped, then the oldest complete interactions.
   The newest complete interaction and the goal echo are never dropped — their
   bodies may be elided, their presence may not be.
4. Mandatory state may remain above the low watermark but never above hard
   usable; an irreducible vector raises `CONTEXT_BUDGET_EXCEEDED` before any
   inference, and the compiler makes no model call of its own.

**Eviction reclaims bodies, never identity.** A fragment carries `evictable`
to mean "a raw body is still present and eviction can still reclaim it", so a
fragment whose body has already become a receipt is not evictable: compaction
running a second time over its own output reclaims nothing further rather than
overwriting what the first pass promised to keep. Where a body is reclaimed,
the receipt retains the header line naming the action or finding and any
`artifact=` binding, each clipped to a bounded width — a receipt that named
neither what ran nor where the bytes went would make an eviction
indistinguishable from a deletion (`NT-C05`). A single-line block has no
header: its one line is the body, and retaining it would retain exactly what
eviction was asked to reclaim. When nothing remains to reclaim, the answer is
`CONTEXT_BUDGET_EXCEEDED` rather than a smaller prompt that has lost its
evidence.

### Verification receipts (`VerificationReceipt`)

`NT-C05` permits the raw verification log to be omitted and requires what it
attested to survive. `agency.context.distiller.verification_receipt_from()`
reads a verification identity out of a tool body and
`VerificationReceipt.render()` emits one bounded line carrying the command or
argv, environment identity, subject, collected and executed counts, exit status,
freshness and artifact digest. A body that is not a verification yields no
receipt: an invented identity would be a fabricated proof. The receipt carries
no derived verdict beyond the exit status the runner itself reported.

### Trailing goal echo (L5 tail)

`compile_packet()` appends the complete objective and every constraint as the
final L5 block, after all dynamic evidence, rendered from the durable task state
rather than from any message. The echo is not truncated and is not evictable, so
no quantity of untrusted tool output can replace the goal, alter the
constraints, widen a grant, or reach the frozen prefix; external text stays
content at L4/L5 where it arrived.

### Cache control and observation

The compiler marks candidate breakpoints (`L1`, `L3`, `L4`) and never writes a
wire-level cache control. Negotiation belongs to the T-105 `PromptCodec` at the
provider boundary: supported routes receive exactly one negotiated breakpoint
and unsupported routes receive byte-identical unmarked messages. Cache telemetry
is three-valued — an observed zero, an observed positive count, and explicit
missingness (`null`) for unsupported, unavailable or silent routes. Prefix
equality is a statement about bytes only: a hit is never inferred from stable
bytes, and no cached-token observation widens admission or any reservation.

Child completion is equally strict: `EpisodeEngine.spawn()` sets `SpawnResult.ok` only when the
child terminal is `completed`. An `abstained` child remains a non-success while preserving its raw
terminal; no task disposition is inferred from termination.

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

`EpisodeEngine` applies the NT-R01/R02 detector on the existing recovery branch: it retains at most twelve `(fingerprint, outcome, progress_key)` tuples, treats three unchanged signatures in a six-action window and repeated length-two/three cycles as stall, and allows progress only when the verified progress key changes. The policy emits `continue|wait|reground|replan|stop` (never `consult`); one reground and one replan are reserved per task, then stop. Permission, permanent, and budget failures stop with `delay_ms = 0` and never sleep into authorization. Retry counters, the last decision, deadlines, fingerprints, and remaining-budget references survive `aether.recovery-state/1` serialization.

Every recovery bound is configurable, versioned and reserved (`NT-R02`),
including the intervention ceiling: `ProtocolRecoveryState.max_interventions`
participates in the policy digest and is carried across restart, so a resumed
task is measured against the ceiling its own run was authorised under rather
than the running build's default. It is serialized only when it departs from
the contract default, so payloads written before the bound was configurable
still round trip byte-for-byte.

Pending-operation reservations survive the decisions taken around them
(`NT-R03`). A held reservation is never replaced by a new operation identity —
retargeting the poll would leave the original operation, which may already
have taken effect, unreachable and unreconciled — and stopping or intervening
does not release an unsettled occurrence, because an unknown external outcome
must be reconciled before replay or refund regardless of whether the task is
still chasing it. Only the operation whose fingerprint matches the settling
attempt clears its own reservation.

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
- **Tests**: `test/agency/test_episode.py`, `test/agency/test_context_compiler.py`, `test/agency/test_context_packet.py`, `test/agency/test_protocol_recovery.py`, `test/contracts/test_semantic_task_state.py`, `test/contracts/test_m5a_agent_view.py`.

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
