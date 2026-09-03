---
id: draft.development-final-plan-v2
class: planning
authority: non-canonical
truth_plane: PROPOSED
status: draft
owner: repository-governance
version: "2.0.0"
created: 2026-09-03
last_verified: 2026-09-03
complements:
  - .draft/DEVELOPMENT_FINAL_PLAN_MERGED.md
  - .draft/DEVELOPMENT_FINAL_PLAN.md
  - .draft/DEVELOPMENT_FINAL_PLAN_B.md
  - docs/reports/reviews/electroweak_v092/octopus/
  - docs/research/coding_harness/
supersedes: []
authorizes_nothing: true
navigation_mode: degraded-locator-plus-source
---

# AETHER / Vanguard: SOTA Autonomous Coding Agent & Harness Builder Meta-Framework
## Architecture, Composable Primitives, and Engineering Execution Masterplan (v2)

```text
====================================================================================================
Authority: Non-Canonical Strategic & Architectural Proposal
Complements: .draft/DEVELOPMENT_FINAL_PLAN_MERGED.md (Preserving Truth-Spine, Forensics & DAG 01-35)
Primary Objectives:
  1. Industrial SOTA Autonomous Coding Agent (100+ Turns, Long Context, Multi-File 2PC, Anti-Tamper)
  2. Composable Harness Builder Meta-Framework (16 Primitives, Dynamic Phenotypes, Outer-Loop Director)
Hexagonal Lattice Flow: domain ← ports ← kernel (TCB ≤ 1438 LOC) ← agency ← runtime → adapters
====================================================================================================
```

---

## 1. Executive Synthesis & Strategic Complementarity

### 1.1 The Dual Mission of Vanguard / AETHER
Vanguard is simultaneously two tightly integrated systems:
1. **The SOTA Autonomous Coding Agent (`Coding Max`)**: A world-class software engineering agent capable of autonomously executing multi-hour, multi-turn (50–200 turns) engineering tasks—including complex brownfield bug fixes, greenfield multi-file subsystem creation, multi-repo investigation, and atomic refactoring—with cryptographic verification, zero context amnesia, and fail-closed termination.
2. **The Harness Builder Meta-Framework (`Substrate Primitives`)**: A composable, modular framework providing the computational physics, workflow DAGs, memory hierarchies, and governance gates to rapidly build, evaluate, and evolve *arbitrary autonomous agents* (Coding, Review, Planning, Swarm Meta-Orchestration).

### 1.2 Complementarity with `DEVELOPMENT_FINAL_PLAN_MERGED.md`
This document (`v2`) **does not compete with nor replace** `DEVELOPMENT_FINAL_PLAN_MERGED.md`. Instead, it establishes a complementary two-tier hierarchy:
- **`DEVELOPMENT_FINAL_PLAN_MERGED.md` remains the Substrate Ground Truth & Forensic Baseline**: It owns the empirical contradiction audit, the foundational proof-of-truth invariants, the 3 headline metrics ($R_{\text{solve}}$, $C_{\text{turn}}$, $R_{\text{tamper}}$), and the immediate, critical-path 35-ticket DAG (`Tickets 01–35`) focused on substrate truth, admission repair, and control qualification.
- **`DEVELOPMENT_FINAL_PLAN_v2.md` defines the System Architecture & Primitive Mechanics**: It synthesizes the extensive research in `docs/research/coding_harness/`, the outer-loop director in `docs/reports/reviews/electroweak_v092/octopus/`, and dynamic multi-agent topologies (`HYDRA`). It translates conceptual theory into typed protocols, concrete data models, and execution packages ready to be decomposed into [`milestones.md`](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/milestones.md), [`backlog.md`](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/backlog.md), [`FEATURE_SPEC.md`](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/FEATURE_SPEC.md), and [`tasks.md`](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/tasks.md).

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                   DEVELOPMENT_FINAL_PLAN_v2 (This Master Plan)                                   │
│  - Composable Harness Builder Primitives (16 Primitives, Event-Sourced Node Types)               │
│  - Long-Horizon Agency & Context Economics (L1-L5 Prefix Stability, Result Distiller, Dead-Ends) │
│  - Multi-File Greenfield/Brownfield 2PC Transactions & 0.2ms AST Preflight                       │
│  - Anti-Tamper Test Shield, UID 10002 Evaluator & Fail-to-Pass Reproducer Protocol               │
│  - Model Dialect Recovery & Response Wrangling (DeepSeek, Claude, OpenAI)                        │
│  - Outer-Loop Director (OCT-* / ORCH-*) & Meta-Conductor Closed Supervisory Loop                 │
│  - Dynamic Bifurcation & Living Horizon Swarm Topologies (HYDRA)                                 │
└─────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                              │ Informs & Extends
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│             DEVELOPMENT_FINAL_PLAN_MERGED.md (Substrate Foundation & Core DAG)                   │
│  - Empirical Evidence Audit & Forensic Contradiction Elimination                                 │
│  - Strict Hexagonal Boundaries (domain ← ports ← kernel ← agency ← runtime → adapters)            │
│  - Kernel TCB Line-of-Code Budget (≤ 1438 LOC Ceiling)                                           │
│  - Admission Gate & Verification Proof Spine (Tickets 01–08 Critical Path)                       │
│  - Control-First Single-Agent Benchmark Qualification (Tickets 09–35)                            │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pillar I: The Harness Builder Framework & Meta-Framework Primitives

### 2.1 The 16 Candidate Computational Substrate Primitives
Per `RESEARCH_META_FRAMEWORK_2408.md` and `RESEARCH_metaframework_2508_improved.md`, an autonomous agent framework must not treat high-level constructs ("Agent", "Planner", "Critic") as atomic primitives. Instead, it defines **16 pure computational primitives** from which all agentic behaviors emerge:

| Primitive | Classification | Formal Responsibility & Behavioral Contract | Target Package Placement |
|---|---|---|---|
| **`OBSERVE`** | Sensory | Ingests environment/system states into typed evidence snapshots. Zero mutation. | `ports/environment.py` |
| **`REPRESENT`**| Cognitive | Projects raw bytes into content-addressed ASTs, symbols, embeddings, or maps. | `domain/transforms/` |
| **`PREDICT`**  | Epistemic | Generates testable hypotheses and expected future observations. | `agency/prediction/` |
| **`SELECT`**   | Attention | Bounded selection under constraints (token budgeting, tool routing). | `agency/context/` |
| **`ACT`**      | Executive | 4-stage dispatch: `Proposal → Attenuate → Dispatch → Receipt`. | `kernel/dispatch.py` |
| **`STORE`**    | Memory | Persists content-addressed immutable records to SQLite WAL. | `runtime/event_store.py` |
| **`RETRIEVE`** | Memory | Policy-bounded selection from storage (BM25 FTS5, AST adjacency). | `adapters/index/` |
| **`COMMUNICATE`**| Social | Typed, content-addressed message passing preserving causal lineage. | `domain/topology/` |
| **`ALLOCATE`** | Resource | Allocates 6D resource tensors (USD, time, tokens, bytes, turns, depth). | `kernel/budget.py` |
| **`VERIFY`**   | Structural| Synchronous local checks: AST syntax, type linkage, schema validity. | `adapters/environment/` |
| **`EVALUATE`** | Exterior | Independent, out-of-process verification emitting signed receipts. | `adapters/evaluator/` |
| **`COMPOSE`**  | Structural| Assembles primitive instances into directed acyclic workflow graphs. | `runtime/wiring.py` |
| **`VARY`**     | Evolutionary| Applies mutations, structural variations, or hyperparameter sweeps. | `agency/evolution/` |
| **`CONSOLIDATE`**| Learning | Distills multi-turn experiences into procedures, skills, or records. | `agency/memory/` |
| **`REVISE`**   | Strategic | Meta-level strategy revision when marginal progress plateaus. | `runtime/outer_loop/` |
| **`SCHEDULE`** | Temporal | Manages activation, concurrency, priority queues, and interruptions. | `runtime/session.py` |

### 2.2 "Agent as a Compiled Phenotype"
In Vanguard, an **Agent is not an ontological base class**; it is an ephemeral **Compiled Phenotype**:
```python
@dataclass(frozen=True, slots=True)
class BoundedPhenotype:
    """An ephemeral, task-conditioned computational organization."""
    phenotype_id: str
    workflow_graph_digest: str
    state_boundary_scope: tuple[str, ...]
    capability_lease: CapabilityGrant
    budget_lease: BudgetTensor
    model_policy_digest: str
    mailbox_endpoint_id: str
```
Phenotypes are lazily compiled by an architecture compiler based on task requirements, executed to satisfy a specific proof obligation, and retired immediately after verification.

### 2.3 Event-Sourced Workflow Graph & Closed Node Kinds
Rather than running monolithic agent loops, complex workflows are modeled as **Event-Sourced Directed Acyclic Graphs (DAGs)** composed of 9 closed node kinds (`LLM_RESPONSE_WRANGLER.md` §3):
```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   WORKFLOW GRAPH NODE TAXONOMY                                   │
├─────────────────┬────────────────────────────────────────────────────────────────────────────────┤
│ 1. transform    │ Pure, deterministic in-memory computation (parsing, normalizing, ranking).     │
│ 2. model        │ Single constrained model inference call (one prompt -> one response).         │
│ 3. episode      │ Iterative model-tool loop (only invoked when open-ended feedback is required).  │
│ 4. effect       │ Authorized external privileged mutation passing through the Kernel.            │
│ 5. gate         │ Deterministic boundary acceptance or rejection of candidate evidence.          │
│ 6. router       │ Branch selection based on state predicates or classifier outputs.              │
│ 7. join         │ Synchronization barrier merging results from concurrent predecessor paths.     │
│ 8. interrupt    │ Execution pause awaiting operator approval, external webhook, or lease renewal.│
│ 9. evaluator    │ Independent, out-of-process test execution request.                            │
└─────────────────┴────────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Pure Artifact-Transform Algebra
All in-memory transformations (diff parsing, AST skeletonization, token estimation, linting) must implement the **Pure Transform Contract** (`domain/transforms/contracts.py`):
```python
@dataclass(frozen=True, slots=True)
class TransformSpec:
    name: str
    input_type: str
    output_type: str
    max_input_bytes: int
    max_output_bytes: int
    timeout_ms: int

@dataclass(frozen=True, slots=True)
class TransformResult:
    success: bool
    output_digest: str
    output_payload: Mapping[str, Any]
    diagnostics: tuple[str, ...]
    execution_duration_ms: int
```
**Invariants on Transforms**:
- **I-TX-1 (Pure Stdlib & Zero I/O)**: Transforms must never execute filesystem writes, subprocess calls, network sockets, or system clocks.
- **I-TX-2 (Idempotency & Provenance)**: The same `(input_digest, config_digest)` must deterministically yield the exact same `output_digest`.
- **I-TX-3 (TCB Exemption)**: Transforms live in `domain/transforms/` and do not consume Kernel TCB lines of code.

---

## 3. Pillar II: SOTA Long-Horizon Agency & Context Economics (100+ Turns)

### 3.1 The 5 Root Problems of Context Economics
Long-horizon execution (50–200 turns) routinely collapses due to five distinct phenomena:
1. **P1: Turn-Level Bloat**: Raw tool outputs (large stack traces, 5,000-line pytest runs, full file reads) flood context.
2. **P2: Attention Dilution ("Lost in the Middle")**: 50,000 tokens present, but the model fails to attend to critical constraints.
3. **P3: KV-Cache Invalidation**: Changing system prompts or tool order destroys prompt cache, increasing latency and cost by 10×.
4. **P4: Cross-Episode & Inter-Turn Amnesia**: Re-trying hypotheses and patches that were already falsified 10 turns prior.
5. **P5: Large-Scale Repository Ingestion**: 10,000 files in the workspace, with budget for only 30.

### 3.2 L1–L5 Prefix-Stable Context Architecture
To maximize provider prompt caching (Anthropic, DeepSeek, OpenAI) from 27% to **>72%**, context is assembled into 5 strict layers (`agency/context/compiler.py`):
```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│ L1: SYSTEM      │ Constitutional law, core output schema      │ Mutation = 0     │
├─────────────────┼─────────────────────────────────────────────┼──────────────────┤
│ L2: TOOLS       │ Stable tool JSON schemas & definitions       │ Mutation = 0     │
├─────────────────┼─────────────────────────────────────────────┼──────────────────┤
│ L3: ENVIRONMENT │ OS conventions, repository map, skill cards  │ Mutation = 0     │
├─────────────────┴─────────────────────────────────────────────┴──────────────────┤
│ ─── [KV CACHE BARRIER: Ephemeral Cache Breakpoint Injected Here] ──────────────── │
├─────────────────┬─────────────────────────────────────────────┬──────────────────┤
│ L4: TASK        │ Problem brief, active step, invariants      │ Mutates per task │
├─────────────────┼─────────────────────────────────────────────┼──────────────────┤
│ L5: DIALOGUE    │ Recency window, working set, tool receipts  │ Mutates per turn │
└──────────────────────────────────────────────────────────────────────────────────┘
```
**Rule**: `PREFIX_LAYERS` (L1–L3) are byte-frozen at session startup. No turn dynamic data may enter L1–L3.

### 3.3 Distillation at the Effect Boundary (`ResultDistiller`)
Distillation occurs **at the moment the effect receipt is generated**, *before* reaching the context compaction buffer:
```python
class ResultDistiller(Protocol):
    def distill(self, verb: str, payload: Mapping[str, Any]) -> DistilledResult: ...

@dataclass(frozen=True, slots=True)
class DistilledResult:
    compact_text: str          # What enters L5 dialogue history (~150 tokens)
    full_artifact_digest: str  # Content-address of raw output (retrievable on demand)
    tokens_saved: int
```
- **`PytestDistiller`**: Extracts: exit code, failing test names, assertion line, and failure message. Drops: successful dots, stack frames below the assertion frame, collection warnings, and timing tables (1,200 tokens $\to$ 180 tokens).
- **Critical Invariant ("Never Destroy, Always Address")**: The raw output is saved to the blob store under `full_artifact_digest`. The agent can invoke `ctx.expand(digest)` if full stack traces are genuinely required.

### 3.4 Recency-Inverted Salience & Pinned Working-Set Header
To combat "Lost in the Middle" attention degradation, the prompt compiler pins an immutable **Working-Set Header (~80 tokens)** directly at the top of L5, adjacent to the latest turn:
```text
================================== ACTIVE WORKING SET ==================================
Goal: Implement SemanticTaskState vector and verify JCS canonicalization
Touched Files: vanguard/packages/domain/task_state.py (2 hunks)
Current Verification: FAILING — test_jcs_canonical: AssertionError: keys not sorted
Rejected Dead Ends:
  [Turn 04] Sorting keys with sorted(dict) — failed slots dataclass mapping
  [Turn 08] Relying on json.dumps(sort_keys=True) — violates RFC 8785 float format
Next Objective: Use vanguard.packages.domain.canonical.canonical_json() reducer
========================================================================================
```

### 3.5 The Dead-Ends Algebra (`StructuredRecord.dead_ends`)
In long-horizon debugging, **knowing what failed and why is 10× more valuable than knowing what succeeded**. 
- Whenever a test fails following a patch or a hypothesis is refuted, the failure signature and rationale are registered into `falsified_hypotheses`.
- Invariant: Compaction and eviction algorithms are strictly forbidden from evicting `falsified_hypotheses`. They remain pinned in L4/L5, preventing the dreaded "cyclical patching death spiral".

### 3.6 Repo-Scale Retrieval via Skeletonization, AST Callgraphs & Submodular Knapsack
For large repositories (100k+ LOC):
1. **3-Tier Skeletonization**:
   - `L0`: File path + single-line module docstring (~15 tokens).
   - `L1`: Tree-sitter AST skeletons: class names, method signatures, argument types, return types, decorators; function bodies elided (~150 tokens).
   - `L2`: Full file source (~500–5,000 tokens).
2. **Submodular Knapsack Packing**:
   Instead of naive Top-$K$ semantic similarity (which produces redundant file clusters), pack candidates by maximizing marginal symbol coverage:
   $$\text{Gain}(file) = \frac{\alpha \cdot \text{Relevance}(file) + (1 - \alpha) \cdot |\text{NewSymbolsCovered}|}{\max(\text{Tokens}(file), 1)}$$
   Greedy submodular optimization provides a provable $(1 - 1/e)$ approximation bound under strict token budgets.
3. **Spectrum-Based Fault Localization (SBFL Ochiai)**:
   For bug localization, map test coverage matrices to calculate suspicion scores:
   $$\text{Suspiciousness}(s) = \frac{e_f(s)}{\sqrt{n_f \cdot (e_f(s) + e_p(s))}}$$
   Inject the top 5 suspicious lines directly into the Turn 1 prompt, bypassing 5–10 manual exploratory turns.

---

## 4. Pillar III: Greenfield Multi-File Synthesis & Recoverable Transactions

### 4.1 The Greenfield Synthesis Challenge
When building new subsystems requiring multiple interdependent files (domain schemas, port interfaces, adapters, wiring, and tests), agents often fail due to:
- Writing implementations before interfaces exist;
- Cyclic imports and broken symbol exports;
- Cascading syntax errors discovered late during whole-suite runs.

### 4.2 Two-Phase Commit (2PC) Multi-File Transaction Protocol
All multi-file modifications must pass through an atomic **Two-Phase Commit Transaction Manager** (`adapters/environment/transaction.py`):
```text
Agent Proposes Transaction (Files: [A.py, B.py, C.py])
    │
    ▼
[PHASE 1: PRE-FLIGHT (In-Memory Shadow Workspace)]
    ├─ 1. In-Process AST Syntax Verification (ast.parse)
    ├─ 2. Cross-Module Symbol Linkage (all imported types resolve)
    └─ 3. Structural Boundary Verification (hexagonal layer check)
    │
    ├─► If ALL checks PASS:
    │     ▼
    │   [PHASE 2: COMMIT]
    │     ├─ Write staged files atomically to disk
    │     └─ Emit TransactionCommitted event with tree hash
    │
    └─► If ANY check FAILS:
          ▼
        [PHASE 2: ROLLBACK]
          ├─ Discard shadow buffer; disk untouched
          ├─ Record failure signature into dead_ends
          └─ Emit TransactionRejected with exact syntax line/column diagnostics
```

### 4.3 In-Process 0.2ms AST Syntax Pre-Flight Gate
Hooked into Kernel Dispatch Stage $S_7$ / $S_8$ (`surgical_patch_preflight`):
```python
def validate_syntax_preflight(file_path: str, proposed_content: str) -> tuple[bool, str | None]:
    if file_path.endswith(".py"):
        try:
            ast.parse(proposed_content, filename=file_path)
            return True, None
        except SyntaxError as exc:
            return False, f"SyntaxError at line {exc.lineno}, col {exc.offset}: {exc.msg}"
    return True, None
```
- Executes in **0.2 milliseconds**. Intercepts indentation errors and malformed ASTs before disk writes, eliminating 15–30 second timeout waits on external compiler subprocesses.

### 4.4 Speculative Branching & Git Checkpoint Rollbacks
- For complex multi-turn refactors, `SpeculativeBranchManager` generates a lightweight git checkpoint (`git stash create` or detached branch pointer).
- If the agent introduces regressions that cannot be resolved within 3 turns, the runtime triggers a clean rollback to the latest green state, preventing cumulative code degradation.

---

## 5. Pillar IV: Autonomous Verification, Tamper-Resistance & Reproducers

### 5.1 Separation of Authority Invariant
$$\mathbf{Candidate\ (Agent)} \neq \mathbf{Evaluator\ (Judge)} \neq \mathbf{Promotion\ Authority\ (Release\ Gate)}$$
- The coding agent runs under rootless Bubblewrap sandbox (`bwrap` UID `10001`).
- Verification suites run via `ExteriorEvaluatorClient` communicating with an isolated evaluator daemon under UID `10002`.
- Test suites, golden data fixtures, and grading scripts are mounted **read-only** (`ro-bind`).

### 5.2 The Cryptographic Test Tamper Shield (`TestTamperShield`)
To eliminate "reward hacking" (where an agent modifies test assertions, changes `assert x == 42` to `assert True`, or comments out tests):
```python
@dataclass(frozen=True, slots=True)
class TestTamperShield:
    frozen_test_digests: Mapping[str, str] # path -> sha256 at Turn 0

    def verify_workspace_integrity(self, workspace_root: Path) -> tuple[bool, str | None]:
        for test_path, expected_hash in self.frozen_test_digests.items():
            current_file = workspace_root / test_path
            if not current_file.exists():
                return False, f"TAMPERING DETECTED: Frozen test {test_path} was deleted!"
            current_hash = hashlib.sha256(current_file.read_bytes()).hexdigest()
            if current_hash != expected_hash:
                return False, f"TAMPERING DETECTED: Frozen test {test_path} was modified!"
        return True, None
```
**Rule**: Modifying frozen test files triggers immediate fail-closed termination with `TAMPER_VIOLATION`.

### 5.3 Gated Dual-Loop Reproducer Protocol (Fail-to-Pass Enforcement)
To guarantee bug fixes are real and not coincidental passes:
```text
Stage 1: LOCALIZATION    ──► Identify root cause.
Stage 2: REPRODUCER      ──► Write minimal reproducing test (test_repro.py).
Stage 3: PRE-VERIFY      ──► Execute reproducer on unpatched code. MUST FAIL.
                             (If it passes, reproducer is invalid: REJECT).
Stage 4: SURGICAL PATCH  ──► Apply code fix via 2PC transaction.
Stage 5: POST-VERIFY     ──► Execute reproducer on patched code. MUST PASS.
Stage 6: REGRESSION GATE ──► Execute full repository test suite. ZERO regressions.
Stage 7: CLEANUP         ──► Quarantine or promote reproducer into official test suite.
```
**Enforcement**: Invoking `finish` without a verified `Fail-to-Pass` receipt is rejected by the `AdmissionGate`.

### 5.4 Type-Aware Mutation Testing (EvalPlus / LLMorpheus)
To defeat "tautological fixes" (hardcoding return values for known test cases):
- Synthesize syntactic mutants across modified diff lines (swap operators: `==` $\leftrightarrow$ `!=`, `<` $\leftrightarrow$ `<=`, boolean constants: `True` $\leftrightarrow$ `False`).
- Require Mutation Score:
  $$MS(Patch) = \frac{\sum_{m \in \mathcal{M}} \mathbb{I}(\text{Tests fail on mutant } m)}{|\mathcal{M}|} \ge 0.80$$
- Patches that pass tests even when their core logic is inverted are rejected as ungrounded.

---

## 6. Pillar V: Model Dialect Wrangling & Response Recovery

### 6.1 Provider Dialect Realities
| Model Family | Tool Calling Dialect | Common Degenerations & Idiosyncrasies |
|---|---|---|
| **Claude (3.5 / 3.7 Sonnet)** | Native XML & JSON parameter blocks | Emits markdown unified diffs or search-and-replace text blocks into assistant text instead of calling `patch.apply`. |
| **DeepSeek (V3 / R1 / Coder)**| DSML (`<\|action_start\|>`) or fenced JSON | Emits `<think>...</think>` tags that must be cleanly stripped; truncates JSON arguments when hitting `max_tokens`. |
| **OpenAI (GPT-4o / o1 / o3)** | Structured Outputs / function calling | Rejects trailing commas or minor JSON schema deviations; strict typing. |
| **Local Models (Qwen 2.5 Coder)**| Inconsistent schema adherence | Outputs explanatory prose before/after tool JSON; missing closing brackets. |

### 6.2 Decoupled Protocol Recovery Pipeline
Provider adapters handle **only** raw network transport. Output normalization is handled by a model-agnostic **Protocol Recovery Pipeline** (`agency/episode/protocol_recovery.py`):
```text
Raw Model Output
    │
    ▼
[Dialect Detection & Stripping]
    ├─ Extract and isolate reasoning tokens (<think>...</think>)
    └─ Detect markup syntax (DSML, XML tags, fenced ```json codeblocks)
    │
    ▼
[JSON Argument Repair]
    ├─ Strip trailing commas
    ├─ Quote unquoted object keys
    └─ Balance missing closing braces/brackets from truncated streams
    │
    ▼
[Proposal Classification & Validation]
    ├─ Validate against tool JSON schema
    └─ Check action authorization against active capability grant
```

### 6.3 Bounded Protocol Recovery State Machine
Replaces immediate episode crashes with structured, actionable retry loops:
1. **Truncated Output Recovery**:
   - If response ends mid-stream due to `max_tokens`: preserve partial JSON, compute continuation token offset, and issue a continuation request retaining full prefix.
2. **Markdown Patch Emitted in Prose**:
   - If the model writes a valid unified diff inside assistant text without calling `patch.apply`: parse the diff block, calculate artifact digest, and return structured retry feedback:
     `RetryModel(reason="PATCH_EMITTED_AS_TEXT", feedback={"required_tool": "patch.apply", "candidate_digest": digest})`.
   - **Invariant**: The engine *never* silently executes raw text as an effect; the model must formally submit the authorized proposal.
3. **Head/Tail Output Paging**:
   - When test runners emit 50,000+ characters of output, page automatically: retain the **first 25 lines** (environment and discovery), elide middle passing noise with `[... N lines elided; raw digest sha256:... ...]`, and retain the **last 60 lines** (the exact stack trace, assertion failure, and summary).

---

## 7. Pillar VI: Outer-Loop Meta-Orchestration & Multi-Agent Topologies

### 7.1 The Director Layer (Program-Scale Orchestration)
While the inner loop (`EpisodeEngine` / Kernel S0–S12) solves *one task well*, the **Outer-Loop Director** (`OCT-03` / `ORCH-*`) executes *entire multi-package roadmaps* (`SOTA-01..11`):
- **Lifecycle**: Sequences tasks according to dependency DAGs, spans multiple days, manages cross-episode memory, and handles fresh-process restarts via SQLite WAL checkpoints.
- **Strict Boundary**: The Director has **zero mutating tools** (no `fs.write`, no `proc.exec`). It directs, decomposes, reviews, and gates; the Dispatcher executes.

### 7.2 The Meta-Conductor: Higher-Order Supervisory Loop
The **Meta-Conductor** (`OCT-04`) operates as an exterior pilot *above* AETHER, reasoning about the execution attempt itself:
$$\mathbf{measure} \longrightarrow \mathbf{diagnose} \longrightarrow \mathbf{intervene} \longrightarrow \mathbf{re\text{-}measure}$$

#### The Non-LLM `ProgressVector`
Computed deterministically from append-only ledger events with zero model calls:
```python
@dataclass(frozen=True, slots=True)
class ProgressVector:
    verification_delta: float  # (tests passing now - tests passing at checkpoint) [-1.0..1.0]
    novelty: float             # 1 - (repeated action signatures / total actions) [0.0..1.0]
    scope_fidelity: float      # |touched_files ∩ declared_scope| / |touched_files| [0.0..1.0]
    evidence_freshness: int    # Turns elapsed since last verification receipt
    budget_burn: float         # spent_budget / total_allocated [0.0..1.0]
    convergence: float         # 1 - (distinct failure fingerprints / total attempts)
```

#### Closed Vocabulary of 8 Pathologies & Ordered Interventions
1. **`THRASHING`** (`novelty < 0.3` over 3 turns) $\to$ **Level 0 (NOTE)**: Inject dead-ends block into context.
2. **`SCOPE_DRIFT`** (`scope_fidelity < 0.8`) $\to$ **Level 2 (REBRIEF)**: Halt and reinforce scope boundaries.
3. **`BLIND`** (`evidence_freshness > 3` with edits) $\to$ **Level 1 (RESTRICT)**: Restrict tools to test verification only.
4. **`WON_BUT_UNAWARE`** (`verification_delta > 0` $\land$ passing $\land$ no `finish`) $\to$ **Level 1 (RESTRICT)**: Restrict tools to `{finish, read}`. (Eliminates the "Abandoned Paradox" where 18/26 green runs looped until budget exhaustion).
5. **`STALLED`** (`verification_delta == 0` over 5 turns) $\to$ **Level 4 (ESCALATE_BAND)**: Escalate model tier or bisect task.
6. **`DIVERGENT`** (`convergence < 0.3`) $\to$ **Level 5 (BISECT)**: Split task into two sequential sub-tasks.
7. **`BUDGET_RISK`** (`budget_burn > 0.8` $\land$ unverified) $\to$ **Level 8 (TERMINATE)**: Graceful stop, persist partial diff.
8. **`INTERVENTION_INEFFECTIVE`** (2 failed interventions) $\to$ **Level 7 (ESCALATE_HUMAN)**: Pause, request human directive.

### 7.3 Dynamic Bifurcation Functional (HYDRA)
Avoids the twin traps of flat ReAct loops (which derail on complex features) and rigid multi-agent swarms (which waste tokens on simple fixes):
$$\mathcal{C} = 0.35 \cdot U_{\text{loc}} + 0.30 \cdot C_{\text{dep}} + 0.20 \cdot S_{\text{spec}} + 0.15 \cdot K_{\text{ctx}}$$
- **Threshold Rule**:
  - $\mathcal{C} < 0.38 \implies \mathbf{Mode\ A\ (Fluid\ ReAct\ Actor)}$: Single agent, direct read $\to$ patch $\to$ verify $\to$ finish in 2–3 turns ($< \$0.003$).
  - $\mathcal{C} \ge 0.38 \lor \text{failure\_streak} \ge 2 \implies \mathbf{Mode\ B\ (Attenuated\ Multi-Head\ DAG)}$.

### 7.4 The 5 Specialized Heads & Living Horizon Planning
```text
[Head 1: LIVING PLANNER]       Emits plan.horizon/1 digest (15% budget share, 3 turns)
          │
          ▼
[Head 2: SEMANTIC LOCALIZER]   Emits context.bundle/1 AST slice digest (10% budget share, 2 turns)
          │
          ▼
[Head 3: CHIMERA IMPLEMENTER]  Synthesizes diff, validates AST syntax (50% budget share, 8 turns)
          │
          ▼
[Head 4: CLEAN-ARCH REVIEWER]  Audits hexagonal boundaries, emits review.verdict/1 (10% budget share)
          │
          ▼
[Head 5: MILESTONE EVALUATOR]  Hermetic sandbox execution (UID 10001), emits VerificationReceipt
```
- **Living Horizon Planning**: Bounded horizons: $|m_{\text{active}}| \equiv 1$ (strictly one active sub-milestone), $|\mathcal{Q}_{\text{horizon}}| \le 2$ (at most two queued). The plan is amended dynamically via event-sourced `HydraPlanAmended` events as new facts emerge.
- **Content-Addressed Mailboxes (`OCT-01`)**: Sub-agents pass information **strictly via 64-character SHA-256 CAS digests** (`sha256:[a-f0-9]{64}`). Handing off a 4,000-token diff costs exactly **$O(1)$ token overhead**, eliminating context inflation across agents.

---

## 8. Pillar VII: Unified Package Inventory & Operational Runway Mapping

To transition these architectural pillars into delivery without documentation sprawl, packages are organized into 8 stable capability tracks mapped to the authoritative runway files:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             MAPPING TO THE 4 RUNWAY FILES                                        │
├───────────────────┬──────────────────────────────────────────────────────────────────────────────┤
│ milestones.md     │ Tracks stable release gates: M-0 through M-10, M-OCT, and M-HYD.            │
│ backlog.md        │ Tracks capability package inventory (SUB, PRG, TXN, SHD, WRN, OCT, HYD).     │
│ FEATURE_SPEC.md   │ Active sprint delta specification (typed Pydantic schemas, error matrices).  │
│ tasks.md          │ Active dynamic execution work DAG (WIP=1, T0–T7 checkboxes, test falsifiers).│
└───────────────────┴──────────────────────────────────────────────────────────────────────────────┘
```

### 8.1 Unified Capability Package Inventory

| Package ID | Capability Name | Primary Subsystem | Implementation Deliverables | Target Gate |
|---|---|---|---|---|
| **`SUB-01`** | **Substrate Admission Repair** | `agency/episode/` | Fix `AdmissionGate` kwargs, wire `session.py` to require verification on default pack. | `W-092-F0` |
| **`SUB-02`** | **Semantic Task State Vector** | `domain/task_state.py` | `SemanticTaskState`, `TaskStep`, monotonic revision hashing, RFC 8785 JCS serialization. | `W-092-F1` |
| **`TXN-01`** | **2PC Multi-File Transaction** | `adapters/environment/`| `AtomicMultiFileTransactionManager`, shadow tree, preflight syntax and symbol validator. | `W-092-F1` |
| **`SHD-01`** | **Cryptographic Tamper Shield**| `runtime/governance/` | `TestTamperShield`, Turn-0 test hashing, fail-closed rejection on test mutation. | `W-092-F1` |
| **`PRG-01`** | **Progressive Context Compiler**| `agency/context/` | L1–L5 prefix-stable compiler, ephemeral cache markers, working-set header with dead ends. | `W-092-F1` |
| **`PRG-02`** | **Boundary Result Distillation**| `agency/context/` | `ResultDistiller` protocol, `PytestDistiller`, content-addressed `full_digest` expansion. | `W-092-F2` |
| **`WRN-01`** | **Model Dialect Recovery** | `adapters/models/` | `ProtocolRecoveryPipeline`, DeepSeek think stripping, markdown diff prose extraction. | `W-092-F1` |
| **`WRN-02`** | **Token-Aware Output Pager** | `agency/context/` | Head/tail output compressor (first 25 lines + last 60 lines), middle passing elision. | `W-092-F2` |
| **`VER-01`** | **Fail-to-Pass Reproducer Gate**| `agency/episode/` | Gated reproducer loop: requires failing pre-verify and passing post-verify receipts. | `W-092-F2` |
| **`VER-02`** | **Mutation Testing Oracle** | `agency/mutation/` | Syntactic mutant generator (operator and boolean swaps), 0.80 mutation score gate. | `W-092-F3` |
| **`OCT-01`** | **Content-Addressed Mailbox** | `domain/topology/` | CAS message digests, $O(1)$ token inter-agent handoffs, zero shared-memory leakage. | `M-OCT-1` |
| **`OCT-02`** | **Declarative Coordination DAG**| `domain/topology/` | `CoordinationPlan` DAG, budget shares ($\sum \le 1000$), merge policies. | `M-OCT-2` |
| **`OCT-03`** | **Outer-Loop Multi-Day Director**| `runtime/outer_loop/`| Roadmap Director above `EpisodeEngine`, SQLite-WAL state continuation across restarts. | `M-OCT-3` |
| **`OCT-04`** | **Meta-Conductor Pilot** | `runtime/outer_loop/`| Closed supervisory loop (`ProgressVector`, 8 pathologies, 9-level intervention ladder). | `M-OCT-4` |
| **`HYD-01`** | **Dynamic Bifurcation Classifier**| `agency/topology/` | Complexity functional $\mathcal{C}$, Mode A (Fluid ReAct) vs Mode B (Multi-Head DAG). | `M-HYD-1` |
| **`HYD-02`** | **Living Horizon Planning Engine**| `agency/topology/` | Bounded horizon ($|m_{\text{active}}| \equiv 1$, $|\mathcal{Q}| \le 2$), event-sourced plan amendments. | `M-HYD-2` |

---

## 9. Lattice Placement, Invariant Matrix & TCB Budget Accounting

### 9.1 Hexagonal Dependency Lattice Placement
All proposed primitives strictly adhere to Vanguard's unidirectional dependency lattice:
```text
domain ← ports ← kernel ← agency ← runtime → adapters
         (apps/ is a thin client slot of runtime)
```

```text
┌──────────────────┬─────────────────────────────┬─────────────────────────────────────────────────┐
│ Layer            │ Directory                   │ Authorized Primitive Additions                  │
├──────────────────┼─────────────────────────────┼─────────────────────────────────────────────────┤
│ **Domain**       │ `vanguard/packages/domain/` │ - `SemanticTaskState`, `TaskStep`, `StepState`  │
│                  │                             │ - Pure transforms (`domain/transforms/`)        │
│                  │                             │ - Mailbox message contracts (`domain/topology/`)│
├──────────────────┼─────────────────────────────┼─────────────────────────────────────────────────┤
│ **Ports**        │ `vanguard/packages/ports/`  │ - `ResultDistiller`, `TransactionManagerPort`   │
│                  │                             │ - `OuterLoopPolicy`, `EvaluatorPort` SPI        │
├──────────────────┼─────────────────────────────┼─────────────────────────────────────────────────┤
│ **Kernel (TCB)** │ `vanguard/packages/kernel/` │ - Strictly domain-blind capability dispatch.    │
│                  │                             │ - ZERO coding, AST, or agent concepts allowed.  │
│                  │                             │ - Budget headroom: 52 LOC (1386/1438 LOC used). │
├──────────────────┼─────────────────────────────┼─────────────────────────────────────────────────┤
│ **Agency**       │ `vanguard/packages/agency/` │ - `ProgressiveContextCompiler` (L1–L5)          │
│                  │                             │ - `ProtocolRecoveryPipeline`, `ResultDistiller` │
│                  │                             │ - `DynamicBifurcationClassifier`, Living Plan   │
├──────────────────┼─────────────────────────────┼─────────────────────────────────────────────────┤
│ **Runtime**      │ `vanguard/packages/runtime/`│ - `TestTamperShield` (governance engine)        │
│                  │                             │ - `OuterLoopDirector`, `MetaConductor` pilot    │
│                  │                             │ - SQLite-WAL event projections (mem.*, orch.*)  │
├──────────────────┼─────────────────────────────┼─────────────────────────────────────────────────┤
│ **Adapters**     │ `vanguard/packages/adapters`│ - `AtomicMultiFileTransactionManager`           │
│                  │                             │ - Concrete LLM dialect recovery parsers         │
│                  │                             │ - Isolated evaluator client (UID 10002)         │
│                  │                             │ - Tree-sitter & SBFL Ochiai adapters            │
└──────────────────┴─────────────────────────────┴─────────────────────────────────────────────────┘
```

### 9.2 Invariant Matrix
| Invariant ID | Name | Statement & Enforcement Mechanism |
|---|---|---|
| **`I-1`** | **Fail-Closed Verification** | No task may terminate with `finish` without a valid, signed `VerificationReceipt`. Process exit codes alone are insufficient. |
| **`I-2`** | **Monotonic Attenuation** | Child agent capabilities $\mathcal{G}_C \subseteq \mathcal{G}_P$ and child budgets $\mathcal{B}_C \le \mathcal{B}_P$. Privilege escalation is mathematically impossible. |
| **`I-6`** | **Process Isolation** | Agent mutations execute in rootless `bwrap` (UID 10001); test evaluation executes under exterior daemon (UID 10002). |
| **`I-7`** | **Kernel Domain Blindness** | The Kernel TCB must never import or reference domain concepts (AST, git, files, patches, tests, models, agents). |
| **`I-TCB`** | **TCB Line Budget** | Production kernel LOC must strictly remain $\le 1438$ LOC. Enforced in CI via `check_tcb_budget.py`. |
| **`I-STATE`**| **Zero Context Amnesia** | Settled invariants and falsified dead-ends are strictly non-evictable. They remain permanently pinned in prompt headers. |
| **`I-TXN`** | **Preflighted Recoverability**| Multi-file edits must pass 0.2ms AST syntax checks before touching disk. Any failure triggers total in-memory rollback. |
| **`I-SHD`** | **Test Oracle Immutability** | Baseline test fixtures are hashed at Turn 0. Any write mutation to test fixtures triggers immediate fail-closed termination. |
| **`I-MAIL`**| **Content-Addressed Handoff**| Inter-agent coordination occurs strictly via 64-character SHA-256 CAS digests ($O(1)$ token overhead). No raw transcript leakage. |

---

## 10. Conclusion & Next Operational Steps

With the completion of this master plan (`DEVELOPMENT_FINAL_PLAN_v2`):
1. **The Research is Consolidated**: The best insights from `docs/reports/reviews/electroweak_v092/octopus/`, `docs/research/coding_harness/`, and `.draft/` are formally unified into a coherent, hexagonal-compliant architecture.
2. **The Substrate Baseline is Preserved**: `DEVELOPMENT_FINAL_PLAN_MERGED.md` remains the authoritative guide for immediate substrate truth and Tickets 01–35.
3. **Execution Runway Ready**:
   - **`milestones.md`** can now be updated with stable gates for `M-OCT` and `M-HYD`.
   - **`backlog.md`** can now be updated with the categorized packages (`SUB`, `PRG`, `TXN`, `SHD`, `WRN`, `VER`, `OCT`, `HYD`).
   - Active sprint **`FEATURE_SPEC.md`** contracts can be drawn directly from the formal schemas in Sections 3–7.
   - Dynamic **`tasks.md`** DAGs can sequence T0–T7 increments with exact test falsifiers.
