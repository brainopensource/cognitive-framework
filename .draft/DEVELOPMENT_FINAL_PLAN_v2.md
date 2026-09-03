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
triad_role: architecture
lock_head: "66aa7a3c0c31"
lock_date: 2026-09-03
lda_freshness: FRESH
complements:
  - .draft/DEVELOPMENT_FINAL_PLAN.md
  - .draft/DEVELOPMENT_FINAL_PLAN_B.md
  - docs/reports/reviews/electroweak_v092/octopus/
  - docs/research/coding_harness/
historical_complements_snapshot_2026-09-03:
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
Complements: Plan A (law) + Plan B (ground truth, tickets 01-35). MERGED is absent / historical sibling.
Primary Objectives:
  1. Industrial SOTA Autonomous Coding Agent (100+ Turns, Long Context, Multi-File 2PC, Anti-Tamper)
  2. Composable Harness Builder Meta-Framework (16 Primitives, Dynamic Phenotypes, Outer-Loop Director)
Hexagonal Lattice Flow: domain ← ports ← kernel (TCB ≤ 1438 LOC) ← agency ← runtime → adapters
====================================================================================================
```

Historical banner claim (draft v2.0.0, 2026-09-03): `Complements: .draft/DEVELOPMENT_FINAL_PLAN_MERGED.md (Preserving Truth-Spine, Forensics & DAG 01-35)`. That file is **absent** at lock HEAD `66aa7a3c`. Authority is A + B; this file remains the architecture catalog.

---

## Locked triad roles

```text
A  = Program law: reliability identity, wave order, competency profiles,
     formal model, per-class evidence, non-goals, D-01–D-10
B  = Ground truth: live inventory, proven gaps, lattice placement,
     tickets 01–35, operator one-pager (01–13 first)
v2 = Architecture catalog: 16 primitives (map, not new cores),
     context economics, 2PC/tamper/dialect mechanics, later phenotypes
     (director / HYDRA / mutation) as [PROPOSAL]
```

Build order (locked, from B, aligned with the SOTA suggestion):

```text
cannot-lie → can-resume → can-see → can-change-many-files
  → qualify one EpisodeEngine coding agent
  → then meta / specialists / campaign / skills-memory
```

This triad **does not authorize** kernel AST, a second `EpisodeEngine`, or default HYDRA. Source outranks drafts. Kernel remains domain-blind (I-7). Coding semantics stay in `packs/code-default/`. CLI is a client of `ApplicationService`, not the brain.

## Epistemic legend (applies to every later claim)

| Tag | Meaning | Promotion rule |
|---|---|---|
| **FACT** | Observed in current source, tests executed this session, or an official primary source fetched on 2026-09-03 | May be treated as current truth for planning |
| **MECHANISM** | Code exists and unit/contract tests exist | Not a product or benchmark claim |
| **INFERENCE** | Reasonable engineering conclusion from FACT + MECHANISM | Must not be restated as evidence |
| **PROPOSAL** | Recommended next work | Requires a later ticket, falsifier, and WIP slot |
| **ASPIRATION** | Desired competitive position | Forbidden as a forecast of a specific score |
| **CONTRADICTION** | Two authorities disagree; source wins | Record both sides; do not silently pick the nicer one |
| **SUPERSEDED** | Attractive draft idea that current lattice or source rejects | Keep the text, mark `[PROPOSAL]`, cite the better location. Do not drop the insight. |

## Lock identity

- `lock_head`: `66aa7a3c0c31`
- `lock_date`: `2026-09-03`
- `lda_freshness`: `FRESH`
- Dual mission: closed-loop coding harness **and** composable agent framework (see §1.1). CLI (`vg` / `aether`) is the operator surface, not a second intelligence.
- Reliability identity:

$$
R = \prod_{t} \Pr(\text{honest progress}_t \mid \text{honest state}_{t-1})
$$

This file is a non-authoritative draft. It proposes work; it authorizes nothing. Current source and executable tests outrank this file, outrank Plan A, and outrank Plan B.

---

## 1. Executive Synthesis & Strategic Complementarity

### 1.1 The Dual Mission of Vanguard / AETHER
Vanguard is simultaneously two tightly integrated systems:
1. **The SOTA Autonomous Coding Agent (`Coding Max`)**: A world-class software engineering agent capable of autonomously executing multi-hour, multi-turn (50–200 turns) engineering tasks—including complex brownfield bug fixes, greenfield multi-file subsystem creation, multi-repo investigation, and atomic refactoring—with cryptographic verification, zero context amnesia, and fail-closed termination.
2. **The Harness Builder Meta-Framework (`Substrate Primitives`)**: A composable, modular framework providing the computational physics, workflow DAGs, memory hierarchies, and governance gates to rapidly build, evaluate, and evolve *arbitrary autonomous agents* (Coding, Review, Planning, Swarm Meta-Orchestration).

**Lock note.** The CLI is not either of those systems. It is a client of `ApplicationService` (`run` / `status` / `resume` / `evidence` / `cost`; presets `fast|balanced|max`). See §12.

### 1.2 Complementarity with Plan A + Plan B (MERGED is a historical sibling)

**FACT (lock HEAD `66aa7a3c`).** `.draft/DEVELOPMENT_FINAL_PLAN_MERGED.md` is **absent**. This document (`v2`) **does not compete with nor replace** Plan A or Plan B. Locked two-tier (now three-role) hierarchy:

- **Plan A remains program law**: reliability identity, wave order, competency profiles, formal model, per-class evidence, non-goals, D-01–D-10.
- **Plan B remains substrate ground truth and the critical-path DAG**: empirical contradiction audit, live inventory, lattice placement, and Tickets 01–35 (operator one-pager 01–13 first).
- **`DEVELOPMENT_FINAL_PLAN_v2.md` defines the System Architecture & Primitive Mechanics**: It synthesizes the extensive research in `docs/research/coding_harness/`, the outer-loop director in `docs/reports/reviews/electroweak_v092/octopus/`, and dynamic multi-agent topologies (`HYDRA`). It translates conceptual theory into typed protocols, concrete data models, and execution packages ready to be decomposed (in a *later* sprint) into [`milestones.md`](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/milestones.md), [`backlog.md`](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/backlog.md), [`docs/execution/spec.md`](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/spec.md) (current delta file; historical name `FEATURE_SPEC.md` is kept as a pointer), and [`tasks.md`](file:///home/rock-dev/Coding/cognitive-framework/docs/execution/tasks.md).

Historical claim (draft v2.0.0 §1.2, 2026-09-03): this document does not compete with nor replace `DEVELOPMENT_FINAL_PLAN_MERGED.md`; MERGED "remains the Substrate Ground Truth & Forensic Baseline" owning the empirical contradiction audit, the 3 headline metrics ($R_{\text{solve}}$, $C_{\text{turn}}$, $R_{\text{tamper}}$), and Tickets 01–35. **Keep that idea.** `[PROPOSAL]` if MERGED is restored as an optional historical sibling. It is **not** authority while absent. Critical-path numbering remains B tickets 01–35. v2 `SUB-*` / `M-HYD` inventory in §8 is `[PROPOSAL]` mapping, not a replacement DAG.

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
│         Plan A (law) + Plan B (substrate foundation & core DAG 01–35)                            │
│  - Empirical Evidence Audit & Forensic Contradiction Elimination                                 │
│  - Strict Hexagonal Boundaries (domain ← ports ← kernel ← agency ← runtime → adapters)            │
│  - Kernel TCB Line-of-Code Budget (≤ 1438 LOC Ceiling)                                           │
│  - Admission Gate & Verification Proof Spine (Tickets 01–08 Critical Path)                       │
│  - Control-First Single-Agent Benchmark Qualification (Tickets 09–35)                            │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Historical diagram target (draft v2.0.0): the lower box was labeled `DEVELOPMENT_FINAL_PLAN_MERGED.md (Substrate Foundation & Core DAG)`. Retargeted above to A + B. MERGED box copy kept as `[PROPOSAL]` historical sibling:

```text
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

The **Target Package Placement** column is the original architecture sketch. Paths that do not exist at lock HEAD, or that violate current lattice owners, are `[PROPOSAL]` future packages — **do not delete**. The **Current owner (FACT)** column pins live code at HEAD `66aa7a3c`. These 16 primitives are a **map onto existing cores**, not a mandate to create 16 new packages.

| Primitive | Classification | Formal Responsibility & Behavioral Contract | Target Package Placement | Current owner (FACT) |
|---|---|---|---|---|
| **`OBSERVE`** | Sensory | Ingests environment/system states into typed evidence snapshots. Zero mutation. | `ports/environment.py` | `ports/environment.py` + `adapters/environment/` |
| **`REPRESENT`**| Cognitive | Projects raw bytes into content-addressed ASTs, symbols, embeddings, or maps. | `domain/transforms/` | `domain/transforms/` (`contracts.py` live `TransformSpec`) |
| **`PREDICT`**  | Epistemic | Generates testable hypotheses and expected future observations. | `agency/prediction/` **[PROPOSAL]** (MISSING in HEAD `66aa7a3c`) | MISSING — no `agency/prediction/` package |
| **`SELECT`**   | Attention | Bounded selection under constraints (token budgeting, tool routing). | `agency/context/` | `agency/context/compiler.py` |
| **`ACT`**      | Executive | 4-stage dispatch: `Proposal → Attenuate → Dispatch → Receipt`. | `kernel/dispatch.py` | `kernel/dispatch.py` (S0–S12) |
| **`STORE`**    | Memory | Persists content-addressed immutable records to SQLite WAL. | `runtime/event_store.py` **[PROPOSAL]** (MISSING as that path) | `adapters/stores/event_store.py` |
| **`RETRIEVE`** | Memory | Policy-bounded selection from storage (BM25 FTS5, AST adjacency). | `adapters/index/` **[PROPOSAL]** (MISSING as that path) | `adapters/stores/repo_index.py` + `ports/index.py` |
| **`COMMUNICATE`**| Social | Typed, content-addressed message passing preserving causal lineage. | `domain/topology/` **[PROPOSAL]** (MISSING in HEAD `66aa7a3c`) | MISSING — no `domain/topology/` package |
| **`ALLOCATE`** | Resource | Allocates 6D resource tensors (USD, time, tokens, bytes, turns, depth). | `kernel/budget.py` | `kernel/budget.py` |
| **`VERIFY`**   | Structural| Synchronous local checks: AST syntax, type linkage, schema validity. | `adapters/environment/` | `adapters/environment/` (post-write `ast.parse` in `git.py`; preflight 2PC MISSING) |
| **`EVALUATE`** | Exterior | Independent, out-of-process verification emitting signed receipts. | `adapters/evaluator/` | `adapters/evaluator/` |
| **`COMPOSE`**  | Structural| Assembles primitive instances into directed acyclic workflow graphs. | `runtime/wiring.py` | `runtime/wiring.py` / `runtime/compose.py` |
| **`VARY`**     | Evolutionary| Applies mutations, structural variations, or hyperparameter sweeps. | `agency/evolution/` **[PROPOSAL]** (MISSING in HEAD `66aa7a3c`) | MISSING — no `agency/evolution/` package |
| **`CONSOLIDATE`**| Learning | Distills multi-turn experiences into procedures, skills, or records. | `agency/memory/` **[PROPOSAL]** (MISSING as that path) | `runtime/memory.py` / `runtime/skill_lifecycle.py` / `skill_*` |
| **`REVISE`**   | Strategic | Meta-level strategy revision when marginal progress plateaus. | `runtime/outer_loop/` **[PROPOSAL]** (MISSING in HEAD `66aa7a3c`) | `runtime/meta_controller.py` (powerless advisor; no outer-loop package) |
| **`SCHEDULE`** | Temporal | Manages activation, concurrency, priority queues, and interruptions. | `runtime/session.py` | `runtime/session.py` |

Keep `agency/prediction/`, `agency/evolution/`, and `runtime/outer_loop/` as `[PROPOSAL]` future packages — do not delete those rows or the target paths.

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

**`[PROPOSAL]` alias sketch** (original v2 draft fields `name` / `input_type` / `output_type` / `timeout_ms`). Keep as a naming alias if a later adapter wants friendlier field names. It is **not** the live dataclass.

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

**FACT — live `TransformSpec` fields** from [`vanguard/packages/domain/transforms/contracts.py`](../vanguard/packages/domain/transforms/contracts.py) lines 20–31 (HEAD `66aa7a3c`):

```python
@dataclass(frozen=True, slots=True)
class TransformSpec:
    """Immutable specification declaring transform capabilities and resource bounds."""

    transform_id: str
    version: str
    input_schema: str
    output_schema: str
    config_digest: str = ""
    deterministic: bool = True
    max_input_bytes: int = 10_000_000
    max_output_bytes: int = 10_000_000
    timeout_seconds: float = 30.0
```

Live sibling types in the same module (FACT, not a replacement of the sketch above): `TransformInput` (`artifact_digest`, `schema_id`, `labels`); `TransformDiagnostic` (`code`, `severity`, `message`, `location`); `TransformOutput` (`status`, `payload`, `output_schema`, `diagnostics`, `confidence_ppm`); live `TransformResult` (`status: TransformStatus`, `output_digest: str | None`, `output_schema: str | None`, `diagnostics`, `confidence_ppm`). `TransformStatus` is `accepted | rejected | unchanged | retryable_error | fatal_error`.

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
To maximize provider prompt caching (Anthropic, DeepSeek, OpenAI) from 27% to **>72%** (**ASPIRATION** — desired competitive cache-hit position; forbidden as a forecast of a measured score at lock HEAD), context is assembled into 5 strict layers (`agency/context/compiler.py`):
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

**FACT (product bug, not the target design; B §4.4).** Current session puts `resume_state` and `repo_map` into env / L3: `runtime/session.py` dumps `task.resume_state` JSON into env_parts at construction (L619–622) and pulls `index.repo_map(token_budget=4000)` into the same environment prefix (L623+). That freezes σ and the map in the KV-cache prefix. Target remains: σ in L4, epoch-bound map **not** in the frozen prefix. See B ticket 12.

`ContextCompiler` **FACT**: L1–L3 freeze at construction (`agency/context/compiler.py`). Compile is **not** a step inside `EpisodeEngine`. Product loop is session + compiler + engine: observe → propose → `recover_proposal` → `Kernel.dispatch` → ingest (`agency/episode/engine.py`).

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
Touched Files: vanguard/packages/domain/task_state.py (2 hunks)  # MISSING in HEAD 66aa7a3c; illustrative [PROPOSAL]
Current Verification: FAILING — test_jcs_canonical: AssertionError: keys not sorted
Rejected Dead Ends:
  [Turn 04] Sorting keys with sorted(dict) — failed slots dataclass mapping
  [Turn 08] Relying on json.dumps(sort_keys=True) — violates RFC 8785 float format
Next Objective: Use vanguard.packages.domain.canonical.canonical_json() reducer
========================================================================================
```

**FACT.** `vanguard/packages/domain/task_state.py` is **MISSING** in HEAD `66aa7a3c`. Live fold is `runtime/task_state.py` (`CodingTaskState` + `fold_task_state`). B §6.12 wins over A's 17-type explosion for the merge. The working-set example above is kept as a sketch; do not read it as claiming the domain file exists.

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

**FACT.** `adapters/environment/transaction.py` is **MISSING** in HEAD `66aa7a3c`. No `WorkspaceEpoch` module. The 2PC protocol above is `[PROPOSAL]`. Correct lattice placement for any future transaction manager is this adapter section (§4.2), **not** the kernel.

**MECHANISM (live).** `GitEnvironment.apply` is sequential (`adapters/environment/git.py`). After write, `ast.parse` is a **post-write observation** (~853–900): syntax errors are appended to the receipt; they do **not** roll back the write. `packs/code-default/middleware/repository/multi_file_completeness.py` and `GreenfieldPolicy` already exist.

### 4.3 In-Process 0.2ms AST Syntax Pre-Flight Gate
Hooked into Kernel Dispatch Stage $S_7$ / $S_8$ (`surgical_patch_preflight`) — **`[PROPOSAL]` rejected by I-7; FACT after the snippet:**
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

**`[PROPOSAL]` rejected by I-7 / current `dispatch.py`.** Historical claim (this subsection title + first sentence): AST preflight is "Hooked into Kernel Dispatch Stage $S_7$ / $S_8$ (`surgical_patch_preflight`)". **CONTRADICTION** with §9.1 "ZERO AST in kernel" and with live dispatch:

```text
FACT Kernel S7 = RESERVE (governor.reserve)
FACT Kernel S8 = VERIFY (grant binds THIS descriptor and is unexpired)
```

Kernel must never import or reference AST, git, files, patches, tests, models, or agents (I-7). Keep the `ast.parse` snippet. Correct placement is §4.2 `adapters/environment/` (and B: observation already exists post-write in `git.py`). Pre-write blocking preflight remains `[PROPOSAL]` in the adapter, not the TCB.

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

**FACT.** `tamper_shield.py` is **MISSING** in HEAD `66aa7a3c`. The shield is `[PROPOSAL]` (see also B FEATURE_SPEC-module routing). Keep the design.

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

**I-1 universal signed finish is `[PROPOSAL]` and too strong** versus A §9.4 per-class evidence (A wins for completion policy) and versus the local vs exterior evaluator split (B §3.4). Keep this section as the bugfix-class protocol. Do not promote it to universal law for research/explanation/greenfield classes.

**FACT (live admission, not this protocol).** `VerificationReceipt.passed` = `exit_code == 0 and executed_test_count > 0` (`admission_gate.py` 22–37). Session `_observed_test_count` returns 0 if unparseable (363–375). Forge still sets `test_count = 1` on green-empty (`forge/engine.py` 309–311). `admission_required` exempts `vg-code-default` / `vg-code-lex`, else `"patch.apply" in verbs` (`runtime/session.py` 124–138). `ADMISSION_GATED_HARNESSES` is unused in runtime.

### 5.4 Type-Aware Mutation Testing (EvalPlus / LLMorpheus)
To defeat "tautological fixes" (hardcoding return values for known test cases):
- Synthesize syntactic mutants across modified diff lines (swap operators: `==` $\leftrightarrow$ `!=`, `<` $\leftrightarrow$ `<=`, boolean constants: `True` $\leftrightarrow$ `False`).
- Require Mutation Score:
  $$MS(Patch) = \frac{\sum_{m \in \mathcal{M}} \mathbb{I}(\text{Tests fail on mutant } m)}{|\mathcal{M}|} \ge 0.80$$
- Patches that pass tests even when their core logic is inverted are rejected as ungrounded.

**`[PROPOSAL]` optional treatment, not default admission.** Keep the full formula and section. Do not make $MS \ge 0.80$ a product-path gate until a successor baseline exists. Competing variant: A per-class evidence (A §9.4) remains completion law.

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

**MECHANISM.** `agency/episode/protocol_recovery.py` exists. `EpisodeEngine` is observe → propose → `recover_proposal` → `Kernel.dispatch` → ingest.

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

**`[PROPOSAL]`.** `runtime/outer_loop/` is MISSING in HEAD `66aa7a3c`. Director is a later phenotype, not default. See A waves 7–8 and B waves 7–8. Default swarm is rejected.

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

**FACT (live meta, distinct from this conductor).** `runtime/meta_controller.py`: a controller **cannot enlarge a budget**. `conclude` becomes an ordinary `finish` proposal (`session.py` `_lower_controller_directive`), still gated. Meta must not admit `completed`. See §20.

### 7.3 Dynamic Bifurcation Functional (HYDRA)
Avoids the twin traps of flat ReAct loops (which derail on complex features) and rigid multi-agent swarms (which waste tokens on simple fixes):
$$\mathcal{C} = 0.35 \cdot U_{\text{loc}} + 0.30 \cdot C_{\text{dep}} + 0.20 \cdot S_{\text{spec}} + 0.15 \cdot K_{\text{ctx}}$$
- **Threshold Rule**:
  - $\mathcal{C} < 0.38 \implies \mathbf{Mode\ A\ (Fluid\ ReAct\ Actor)}$: Single agent, direct read $\to$ patch $\to$ verify $\to$ finish in 2–3 turns ($< \$0.003$).
  - $\mathcal{C} \ge 0.38 \lor \text{failure\_streak} \ge 2 \implies \mathbf{Mode\ B\ (Attenuated\ Multi-Head\ DAG)}$.

**`[PROPOSAL]` later phenotype.** This triad does not authorize default HYDRA. Keep the heads, the functional, and the living-horizon rules.

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

**FACT.** Product implementer is **`EpisodeEngine` + coding pack** (`packs/code-default/`), not `ChimeraEngine`. `agency/chimera/engine.py` `ChimeraEngine` is a parallel loop that does **not** call `Kernel.dispatch` — `[PROPOSAL]` / reject-as-default (B §3.5). Keep the Head 3 topology label `CHIMERA IMPLEMENTER` as a historical / specialist-treatment name. Do not ship Chimera as the Coding Max synthesis head.

Forge likewise does not call `Kernel.dispatch` (B §3.5). Quarantine both from Coding Max scores.

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

**FACT.** `docs/execution/FEATURE_SPEC.md` may be stale naming; current delta file observed in the execution set is [`docs/execution/spec.md`](../docs/execution/spec.md). `docs/execution/active.md` is **absent**. Keep the runway-file names above. This lock pass does **not** rewrite those files.

### 8.1 Unified Capability Package Inventory

**`[PROPOSAL]` ID mapping.** Keep the table. These `SUB-*` / `PRG-*` / `TXN-*` / `M-HYD` identifiers are **not** a replacement DAG. Critical-path numbers remain **B tickets 01–35**. Do not restamp live execution IDs in this pass.

| Package ID | Capability Name | Primary Subsystem | Implementation Deliverables | Target Gate |
|---|---|---|---|---|
| **`SUB-01`** | **Substrate Admission Repair** | `agency/episode/` | Fix `AdmissionGate` kwargs, wire `session.py` to require verification on default pack. | `W-092-F0` |
| **`SUB-02`** | **Semantic Task State Vector** | `domain/task_state.py` **MISSING in HEAD `66aa7a3c`** `[PROPOSAL]` | `SemanticTaskState`, `TaskStep`, monotonic revision hashing, RFC 8785 JCS serialization. | `W-092-F1` |
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

**SUB-02 FACT.** `domain/task_state.py` is **MISSING** in HEAD `66aa7a3c`. Keep the row as `[PROPOSAL]`. Preferred merge is B §6.12 with live `CodingTaskState` in `runtime/task_state.py`.

**PRG-01 must not be a second `ContextCompiler`.** `[PROPOSAL]` is L4/L5 strategy on the **existing** compiler (`agency/context/compiler.py`), matching B §6.8: "do not fork a second ContextCompiler class hierarchy if a strategy suffices." Rollback: if progressive compiler duplicates `ContextCompiler` into a second loop, reject.

**TXN-01 / SHD-01 / OCT-\* / HYD-\* / VER-02:** MISSING modules at HEAD; keep as `[PROPOSAL]`. `WRN-01` overlays existing `protocol_recovery.py` (MECHANISM).

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

**FACT.** Kernel row "ZERO coding, AST, or agent concepts allowed" is the winning lattice rule (I-7). §4.3 kernel S7/S8 AST hook is `[PROPOSAL]` **rejected**; see that subsection. Agency row `ProgressiveContextCompiler` must not fork a second compiler class (PRG-01 / B §6.8). Domain `SemanticTaskState` path is `[PROPOSAL]`; `domain/task_state.py` is **MISSING**. Event store FACT owner is `adapters/stores/event_store.py`, not a `runtime/event_store.py` module.

No `KernelPort` symbol exists in `vanguard/packages/ports/` (FACT; keep A's `KernelPort` row as `[PROPOSAL]` — see A §2.1). Canonical composition path: `ApplicationService → Runtime → HarnessSession → EpisodeEngine → Kernel`. Campaign Service as an extra layer is A's `[PROPOSAL]`.

### 9.2 Invariant Matrix
| Invariant ID | Name | Statement & Enforcement Mechanism |
|---|---|---|
| **`I-1`** | **Fail-Closed Verification** | No task may terminate with `finish` without a valid, signed `VerificationReceipt`. Process exit codes alone are insufficient. **`[PROPOSAL]` too strong vs A §9.4 per-class evidence** (A wins) and vs local vs exterior evaluator split (B §3.4). Keep as bugfix-class aspiration. |
| **`I-2`** | **Monotonic Attenuation** | Child agent capabilities $\mathcal{G}_C \subseteq \mathcal{G}_P$ and child budgets $\mathcal{B}_C \le \mathcal{B}_P$. Privilege escalation is mathematically impossible. |
| **`I-6`** | **Process Isolation** | Agent mutations execute in rootless `bwrap` (UID 10001); test evaluation executes under exterior daemon (UID 10002). |
| **`I-7`** | **Kernel Domain Blindness** | The Kernel TCB must never import or reference domain concepts (AST, git, files, patches, tests, models, agents). |
| **`I-TCB`** | **TCB Line Budget** | Production kernel LOC must strictly remain $\le 1438$ LOC. Enforced in CI via `check_tcb_budget.py`. |
| **`I-STATE`**| **Zero Context Amnesia** | Settled invariants and falsified dead-ends are strictly non-evictable. They remain permanently pinned in prompt headers. |
| **`I-TXN`** | **Preflighted Recoverability**| Multi-file edits must pass 0.2ms AST syntax checks before touching disk. Any failure triggers total in-memory rollback. **`[PROPOSAL]`**; live MECHANISM is sequential apply + post-write `ast.parse` observation. |
| **`I-SHD`** | **Test Oracle Immutability** | Baseline test fixtures are hashed at Turn 0. Any write mutation to test fixtures triggers immediate fail-closed termination. **`[PROPOSAL]`** (`tamper_shield.py` MISSING). |
| **`I-MAIL`**| **Content-Addressed Handoff**| Inter-agent coordination occurs strictly via 64-character SHA-256 CAS digests ($O(1)$ token overhead). No raw transcript leakage. **`[PROPOSAL]`** (`domain/topology/` MISSING). |

---

## 10. Conclusion & Next Operational Steps

With the completion of this master plan (`DEVELOPMENT_FINAL_PLAN_v2`):
1. **The Research is Consolidated**: The best insights from `docs/reports/reviews/electroweak_v092/octopus/`, `docs/research/coding_harness/`, and `.draft/` are formally unified into a coherent, hexagonal-compliant architecture.
2. **The Substrate Baseline is Preserved**: Plan B remains the authoritative guide for immediate substrate truth and Tickets 01–35. Historical claim (draft v2.0.0): `DEVELOPMENT_FINAL_PLAN_MERGED.md` remains that guide — file **absent**; keep as `[PROPOSAL]` historical sibling.
3. **Execution Runway Ready** (later sprint; this lock pass does **not** edit `docs/execution/`):
   - **`milestones.md`** can now be updated with stable gates for `M-OCT` and `M-HYD`.
   - **`backlog.md`** can now be updated with the categorized packages (`SUB`, `PRG`, `TXN`, `SHD`, `WRN`, `VER`, `OCT`, `HYD`).
   - Active sprint **`FEATURE_SPEC.md`** / current **`docs/execution/spec.md`** contracts can be drawn directly from the formal schemas in Sections 3–7 and the appended SOTA pillars.
   - Dynamic **`tasks.md`** DAGs can sequence T0–T7 increments with exact test falsifiers.

**Do not add a competing ticket DAG in this file.** Implementation numbering: **B §18**.

The sections below append the user SOTA harness-loop suggestion **in full**. They do not replace Pillars I–VII.

---

## 11. Closed-loop controller vs chatbot (product loop)

A SOTA coding harness is a **closed-loop controller**, not a chatbot with files. Session success is roughly the product of every turn not failing mechanically, not losing the goal in context, and not “finishing” without proof. Tool friction and context rot dominate model IQ on long, multi-file work.

That is already the thesis in this repo: Vanguard owns the substrate (episode loop, kernel dispatch, ledger, budgets); the coding pack owns coding semantics (discover → patch → verify). The CLI (`vg` / `aether`) is a client of that loop, not a second intelligence.

### 11.1 The loop that everything else hangs on

Every competitive coding CLI (Claude Code, Cursor Agent, Codex, OpenHands, Aider, SWE-agent) is a variant of:

```text
observe workspace
  → compile bounded context (prefix-stable + rolling L5)
  → model proposes structured tool calls
  → authorize (caps, sandbox, budget)
  → effect (read / search / edit / shell / index / test)
  → ingest receipts (truncate, classify, fingerprint)
  → compact / checkpoint
  → admit completion only with fresh verification
```

**FACT.** In this tree that is `EpisodeEngine`: observe → propose → `recover_proposal` → `Kernel.dispatch` → ingest receipt → repeat (`agency/episode/engine.py` ~371–740). Compile is `ContextCompiler` / session, **not** a step inside `EpisodeEngine`. Coding policy lives in `packs/code-default/` (fs, AST patch, repo map, verification gate, greenfield).

The product target loop is:

```text
INGEST → DISCOVER → PLAN → EDIT → VERIFY_TARGETED
                         ↑              │
                         └── RECOVER ←──┘
                                        → VERIFY_BROAD → COMPLETE
```

Transitions must follow **receipts**, not the model’s story. A patch that did not apply is not “in verification.” `finish` without a green receipt bound to the **current** workspace digest is not complete. That gate is `AdmissionGate` + `VerificationReceipt` (`exit_code == 0` **and** `executed_test_count > 0` **and** digest match).

**FACT.** `VerificationReceipt.passed` = `exit_code == 0 and executed_test_count > 0`. Digest-match binding of finish to current workspace is `[PROPOSAL]` relative to live admission.

If that gate is leaky, adding memory, RAG, skills, and swarms only **multiplies false completions**. Plan B’s ordering is correct: **truthful settlement first**, then context, then skills/memory, then specialists. An `AdmissionGate` leak multiplies swarms: HYDRA-first topologies in this file remain `[PROPOSAL]`, not the build order.

---

## 12. CLI as the operator surface (not the brain)

A SOTA coding CLI needs two modes:

| Mode | Job |
|---|---|
| **Interactive TTY** | Streaming turns, diffs, cost, interrupt, resume, approvals |
| **Headless / CI** | `run` / `resume` / `cancel`, NDJSON events, stable exit codes, `--non-interactive` |

Minimum command surface:

- `run` / `resume` / `cancel` / `status` / `evidence` / `cost`
- `doctor` (index + sandbox + model route)
- `checkpoint` (crash-safe)
- flags for budget, model, profile (`fast` / `balanced` / `max`), workspace, worktree isolation

The CLI should **not** assemble prompts, patch files, or grade success. It streams ledger events. Intelligence stays in agency + pack. The product PRD already says this: UNIX instrument, TUI optional, Ink out of the headless path. TUI visual design remains an A non-goal.

**MECHANISM.** `CodingMaxFacade` / `CodingMax` (`vanguard/packages/apps/coding_max/facade.py`) exposes `run` / `status` / `resume` / `evidence` / `cost`; presets `fast|balanced|max`. It is a client of `ApplicationService`.

**`[PROPOSAL]` extra commands:** `cancel`, `doctor`, `checkpoint`, NDJSON headless stream, `--non-interactive`. See also Plan A appended operator surface (canonical write-up for CLI law). This section is the architecture catalog copy so v2 is not a stub.

---

## 13. Small orthogonal toolkit (the agent’s hands)

SOTA is a **small orthogonal toolkit**. Overlapping tools raise schema error and the model shops among them.

| Primitive | Contract | Why it is load-bearing | Live verb / owner | Upgrade |
|---|---|---|---|---|
| **Read** | path + `offset`/`limit` (never dump 4k-line files) | Windowed observation; prefix cache stays small | **MECHANISM** `fs.read` (windowed) | keep windowing |
| **Search** | ripgrep-class, path-scoped, cap hits | Localization without ingesting the repo | **MECHANISM** `fs.search` | output caps `[PROPOSAL]` |
| **Glob / list** | workspace-rooted, path-escape fail-closed | Discovery | **MECHANISM** `fs.list` | — |
| **Edit** | search/replace **or** AST-anchored patch; fuzzy whitespace fallback | $\epsilon_{\text{tool}}$ killer | **MECHANISM** `patch.apply` | fuzzy apply `[PROPOSAL]` |
| **Write** | new files / full rewrite only when justified | Greenfield; forbidden as default brownfield | via environment write / patch | named rare verb `[PROPOSAL]` |
| **Multi-file txn / 2PC** | all-or-nothing 2PC, syntax preflight | No half-broken trees | **MISSING** `transaction.py` | atomic multi-file `[PROPOSAL]` |
| **Shell** | argv, cwd=workspace, timeout, truncated stdout | Tests, git, formatters | **MECHANISM** `proc.exec` | output caps `[PROPOSAL]` |
| **Index** | `repo_map` / symbol / callers, epoch-bound | Zoom, not grep-as-cognition | **MECHANISM** pack `IndexToolkit` (still verb `fs.read`) + `adapters/stores/repo_index.py` | epoch bind `[PROPOSAL]` |
| **Todo / plan** | durable steps in task state, not only chat | Long sessions | **MECHANISM** `CodingTaskState` fold | domain promotion `[PROPOSAL]` |
| **Skill load** | name in catalog; body only when invoked | Progressive disclosure | **MECHANISM** `runtime/skill_lifecycle.py` | product wiring `[PROPOSAL]` |
| **Memory** | query with grant; hits with provenance | Cross-session, not dump | **MECHANISM** authorize then recall (`prompt_assembler.py` 107–113) | four-tier product wiring `[PROPOSAL]` |
| **Test** | first-class parse (CTRF/JUnit), not raw pytest novels | Admission fuel | **MECHANISM** evaluator + `VerificationReceipt` | vacuity/mutation optional `[PROPOSAL]` |

You already have the skeleton: `fs.read` / `fs.search` / `fs.list`, `patch.apply` (AST + unified diff), `proc.exec`, index toolkit. SOTA upgrades on top of that are **resilient apply** (fuzzy match, indent-agnostic), **output caps**, and **atomic multi-file** — not 40 more verbs.

**Scripts beat the model for mechanics.** Format, lint, test, index refresh, “find callers of X” should be tools/scripts. The model decides *what* to run; deterministic code does *how*. That is harness engineering, not prompt engineering.

---

## 14. Reading and editing stack (where most harnesses die)

Failure cascade from the coding-harness treatise: 1-space mismatch → “target not found” → full-file overwrite → suite explodes → context fills with traceback → budget dies. The model looked dumb; the patcher was brittle.

SOTA editing stack (all `[PROPOSAL]` except the two MECHANISM bullets):

1. **Read-before-edit.** `[PROPOSAL]` Refuse patch if the file (or the hunk’s anchor digest) was not observed this episode, or if the workspace epoch moved.
2. **Surgical default.** `[PROPOSAL]` Search/replace or AST node replace. Full-file write is a named, rare verb.
3. **Multi-strategy apply.** `[PROPOSAL]` Exact → whitespace-normalized → indent-shift → fuzzy line window → unified diff. Hermes-style 9-strategy is the empirical pattern.
4. **AST / syntax preflight.** `[PROPOSAL]` in adapter, **rejected in kernel** (I-7 / §4.3). `ast.parse` (or tree-sitter) **before** disk. Fail in milliseconds, nudge immediately. Do not wait for pytest to discover `SyntaxError`.
5. **Workspace fingerprint.** `[PROPOSAL]` Hash the implicated tree. Cyclic $d_t = d_{t-2}$ ⇒ circuit breaker (“you reverted; change hypothesis”), not another identical edit. `WorkspaceEpoch` is MISSING in HEAD `66aa7a3c`.
6. **Two-phase multi-file.** `[PROPOSAL]` Stage all writes in memory → parse all → flush all or roll back all (`INV-DELTA-3` in FEATURE_SPEC). File 4 of 5 syntax-failing must not leave 1–3 on disk. Placement: `adapters/environment/` (§4.2).
7. **Completeness.** `[PROPOSAL]` product default / **MECHANISM** helper exists: public signature change ⇒ implicated call sites in the same transaction (`packs/code-default/middleware/repository/multi_file_completeness.py`). “I updated the definition” is not done.

**MECHANISM (live, keep):** sequential `GitEnvironment.apply` + post-write `ast.parse` observation (`git.py` ~853–900). Observation does not currently block or roll back the write.

For big files: read windows around the symbol (LDA `symbol` / `callers`), never the whole generated file unless the task is that file.

---

## 15. Context: rolling windows, compress, cache, progressive packets

Context is not “stuff the transcript until 200k.” It is a **compiler** with frozen prefix for KV-cache and a rolling working set.

The L1–L5 layout in §3.2 is the right SOTA shape. This section expands product mechanics; it does **not** replace Pillar II.

| Layer | Content | Mutation |
|---|---|---|
| **L1** | Role, constitution, output contract | Frozen at build |
| **L2** | Tool schemas | Frozen at composition |
| **L3** | Env conventions, retrieved priors | Frozen within task |
| **L4** | Goal, constraints, settled invariants | Stable within task |
| **L5** | Turns, tool bodies, dynamic notes | **Only** compacted layer |

**Cache.** Byte-identical L1–L3 across turns is how you get prefix/KV cache hits (Anthropic/OpenAI cache breakpoints). Do not put timestamps, random ids, or “turn 17 of 40” in L1. `stable_prefix_builder.py` exists for this. `vg-code-default` already uses recency-window + `evict_old_tool_results`. The 27% → >72% jump in §3.2 is **ASPIRATION**.

**FACT vs target.** Current session dumps `resume_state` JSON and `repo_map` into env/L3 (B §4.4, `session.py` 619–622+). That is a product bug. Target: σ in L4; epoch-bound map not in the frozen prefix.

**Rolling window.** Keep the last *N* turns (policy: 64 items is a start; token ceiling is the real constraint). Older **tool bodies** become receipts: “read `foo.py` 12kb at turn 4” — fact kept, bytes dropped (`ResultEvictionStrategy`).

**Compress (structured, not vibe-summary).** Naive LLM-summarize of history loses the bug. Compact **observations**; persist **semantic task state** outside the prompt:

- goal, constraints, current step
- hypotheses + dead ends
- inspected / modified files
- last failure class + last verification
- remaining budget

Fold that from the ledger on every compile (`CodingTaskState` / planned `SemanticTaskState`). Compaction may drop raw pytest logs; it must not drop “tests X,Y fail on digest Z.”

**Tool-output policy.** Cap at ~1–2k chars; keep assertion + first frames; drop the middle. Lost-in-the-middle is real: **goal at the head (L4) and a short goal echo at the tail of L5**.

**Progressive packets (Aider / LDA pattern).** Do not RAG the whole repo into L5. Budgeted slices:

- invariant anchor (goal + settled facts)
- negative memory (dead ends)
- active AST slice (open files, epoch-bound)
- symbol stubs + **explicit omissions** (“index truncated; 40 symbols omitted”)

**PRG-01** is this L4/L5 strategy on the existing `ContextCompiler`, not a second compiler (B §6.8).

After every write, **refresh index epoch**. Serving a pre-write repo map is silent corruption. `WorkspaceEpoch` is MISSING; `[PROPOSAL]`.

---

## 16. Index modes: structural map / lexical / graph zoom / docs RAG

Three retrieval modes, used in this order, plus docs RAG as a fourth channel:

1. **Structural map** — Aider-style repo map: important files/symbols under a token budget (PageRank / PPR on the import/call graph). Your `IndexToolkit.render(token_budget)` + LDA `repomap`.
2. **Lexical** — BM25 / ripgrep for exact APIs, error strings, TODOs.
3. **Graph zoom** — `symbol` → `callers` / `callees` / `references`. This is how you do blast-radius on a 200k-LOC tree without stuffing it in context.
4. **Docs RAG** — canonical owners, ADRs, SPEC. A **fourth** channel, not a substitute for the code graph.

**FACT.** Index owner is `adapters/stores/repo_index.py` + `ports/index.py`. There is no `adapters/index/` package. Event store owner is `adapters/stores/event_store.py`. Session currently injects a one-shot `repo_map(token_budget=4000)` into L3 (B §4.4) — target is epoch-bound L5 remainder, not frozen prefix.

Bind every packet to `WorkspaceEpoch { treeHash, indexDigest, sourceRevision }`. Stale epoch ⇒ reindex or fail closed. `WorkspaceEpoch` is **MISSING** in HEAD `66aa7a3c` — `[PROPOSAL]`.

For brownfield: traceback + symbol + callers beats “grep the ticket title.” For greenfield: the map is the **scaffold you are building**, not a search problem.

---

## 17. Four-tier memory (short-term vs long-term)

Do not put “memory” in one bucket. The four-tier model is the industry one. Plan A appends the operator-law copy; this is the architecture catalog copy.

| Tier | Lives | Goes into the prompt? |
|---|---|---|
| **Working** | Current turn scratch | Yes, ephemeral |
| **Episodic (short)** | This run’s receipts, plan, dead ends | As **folded state** + last N turns, not raw history |
| **Semantic (long, workspace)** | Facts: “auth lives in X”, “tests are pytest under test/” | Retrieved hits only, with provenance |
| **Procedural (skills)** | Promoted playbooks | Catalog always; body on demand |

Rules that separate SOTA from a sticky-note bot:

- **Authorize before retrieve** (`INV-B-010`). Child agents do not inherit parent memory grants.
- Every hit carries `event_id` / `run_id` / digest. No anonymous “the agent remembers.”
- Recall is **query + budget**, not “inject last 50 sessions.”
- Short-term durability is the **ledger + resume**, not a bigger window. Crash mid-episode must restore `episode_id`, prefix identity, and $\sigma$, not a frozen L3 dump of old files.

**MECHANISM.** `runtime/prompt_assembler.py` 107–113: authorize then `recall`. `runtime/memory.py` exists. Product four-tier wiring is `[PROPOSAL]`.

**FACT.** Resume synthesizes `episode_id=f"episode-{run_id}"` (`app_service.py` ~414). Session dumps `resume_state` into L3. Target: persist original `episode_id`; put `CodingTaskState` in L4/L5.

Long sessions are **many compacted turns over one durable $\sigma$**, optionally **many episodes in a campaign DAG**. One 400-turn transcript is how you get attention collapse.

---

## 18. Skills: progressive disclosure vs `skill_lifecycle.py`

Skills are **load-bearing procedures**, not flavor text in the system prompt.

SOTA pattern (Claude Code skills, this repo’s `skills/` manifests):

1. **Catalog in L2/L3:** name, when-to-use, 1-line trigger. Tiny.
2. **Invoke:** harness injects the SKILL.md / JSON card into L5 for that turn.
3. **Promote:** trajectory → candidate card → **exterior** eval → operator signature → immutable digest. Generator ≠ evaluator. One lucky run is not a skill.
4. **Rollback / blacklist** if a card regresses.

Examples that actually move SWE scores: `read-receipt-before-repatch`, `pytest-green`, `scaffold-python-api`, “run implicated tests before claiming done.” Decorative skills (`be a senior engineer`) do nothing.

Progressive disclosure is the same idea as context: **names are cheap; bodies are expensive.**

**MECHANISM.** `runtime/skill_lifecycle.py`: `SkillCandidate`, `EvaluationReport`, `PromotionEvidence`; generator, evaluator, and promoter are separate protocols; an agent has no method to promote itself. Product progressive-disclosure wiring (catalog in L2/L3, body on demand in L5) is `[PROPOSAL]`.

**CONSOLIDATE** current owner FACT remains `runtime/memory.py` / `skill_*`, not a new `agency/memory/` package (`agency/memory/` stays `[PROPOSAL]` in §2.1).

---

## 19. Loop engineering vs harness engineering

**Loop engineering** = control policy around the model.

- One vs parallel tool calls (parallel reads OK; parallel writes on one tree are not).
- Protocol recovery: bad JSON / unknown tool / missing field → schema nudge, bounded retries (`protocol_recovery.py`).
- Failure taxonomy with different recoveries: `PATCH_PREIMAGE_MISMATCH`, `TEST_COLLECTION_EMPTY`, `NO_PROGRESS`, `PREMATURE_FINISH`, `CONTEXT_STALE`, …
- Circuit breakers: same action+args+digest; cyclic workspace hash; same normalized traceback *k* times → strategy shift or escalate model.
- **Stop gate:** `finish` is a proposal the harness may reject with a nudge (“run tests; receipt stale”).
- Typed budgets (usd, tokens, turns, bytes). Exhaustion is a terminal state, not a vibe.

**Harness engineering** = everything that makes the loop cheap, replayable, and honest.

- Prefix-stable compiler (not string concat)
- Model **dialect** adapters (tool-call JSON vs XML vs markdown fences)
- Sandbox (bwrap) + path-escape
- Single-writer ledger, crash resume (`RF-25` style)
- Cassettes / LAM so you iterate the harness at $0
- Cost and model fingerprint on every turn (otherwise you cannot train or compare)
- Isolation: git worktrees for speculative patches; one writer per tree

The product of $(1-\epsilon)^T$ means a 5% patch-apply fail rate over 40 turns is catastrophic. Harness quality is the multiplier on the same weights.

Plan A appends the law-side split; this section is the architecture catalog copy.

---

## 20. Meta-cognition (keep it small and powerless)

Useful meta-cognition is a **bounded advisor**, not a second god-loop.

What it may do:

- Detect stuck (no progress, oscillating files, truncation storm)
- Suggest: re-localize, escalate model, spawn read-only investigator, compact harder, switch from write to reproduce
- Maintain an explicit plan / uncertainty list in $\sigma$

What it must **not** do (M-6.5 laws):

- Admit `completed`
- Enlarge budget
- Be inherited by children
- Grade its own work

Reflection-in-the-prompt (“think about whether you’re stuck”) is cheap and often enough. A `meta_controller` that can override admission is how you reintroduce premature finish. Turn it on only against a **single-agent control** with paired ablations.

**FACT (live `meta_controller`).** `runtime/meta_controller.py` raises if a directive requests more budget than remains: “a controller cannot enlarge a budget.” `session.py` `_lower_controller_directive`: `conclude` becomes an ordinary `finish` proposal (`{"kind": "finish", ...}`), still gated by admission / kernel. Advisory directives return `None` and enter L5. This function grants no authority.

§7.2 Meta-Conductor / OCT-04 remains `[PROPOSAL]` above this powerless advisor. Do not merge them into a second `EpisodeEngine`.

---

## 21. Long-session / brownfield fail-to-pass / greenfield oracle

Align with A §9–12 and B §10–11. Do **not** replace those write-ups. This section expands mechanics.

### 21.1 Long sessions (hours, resume, many files)

1. Durable $\sigma$ in domain values, folded from events — not “the conversation.”
2. Checkpoints every N turns / after successful verify.
3. Compaction preserves invariants; L1–L3 byte-identical for cache after resume.
4. Index epoch after writes.
5. Outer **campaign** only after inner episodes cannot lie: each node has its own admission; campaign success ≠ OR of summaries.
6. Operator interrupts: cancel, fork worktree, resume.

METR-style “50% time horizon” is a different metric; internally, staff-class means **resume ≥1**, 40–120 turns, blast-radius tests, Wilson intervals — not “the chat felt long.” See A competency profiles and B §7 / §16.

**FACT vs target.** Resume currently dumps σ into L3 and synthesizes `episode_id`. Target remains prefix-stable L1–L3 with σ in L4/L5 (B tickets 11–13).

### 21.2 Brownfield (bugfix / feature in a living tree)

Reproduce → map → localize (traceback + callers) → surgical 2PC patch → **fail-to-pass and pass-to-pass** → bind receipt to postimage digest. Do not mutate tests to match the story (tamper shield). Agentless-style localize-then-edit is a **pipeline over the same engine**, not a second runtime.

Completion policy: **A §9.4 per class wins**. This file’s I-1 universal signed finish (§5.3) is `[PROPOSAL]` for bugfix only.

### 21.3 Greenfield (new project, many files, empty src)

Different admission policy:

1. Extract requirements into immutable goal + non-goals
2. Types/ports/schemas first
3. File DAG (types → impl → tests)
4. Scaffold layout
5. **Oracle that fails on stubs** (vacuous tests are a fail)
6. Implement in topological order, 2PC
7. Smoke + oracle pass + documented entrypoint

`finish` on greenfield without files + failing-then-passing oracle is the analogue of finishing a bugfix without tests.

**MECHANISM.** `packs/code-default/middleware/repository/greenfield.py` (`GreenfieldPolicy`) exists. Full oracle workflow product wiring is `[PROPOSAL]`. See B §10.

---

## 22. Other pieces that actually matter

- **Verification as the objective.** Tests, typecheck, linters, smoke. Mutation/vacuity checks so the agent cannot delete assertions. Mutation $MS \ge 0.80$ stays `[PROPOSAL]` optional (§5.4).
- **Model routing.** Cheap localizer, coding implementer, rare escalation. Measure; do not hardcode “Sonnet reviews.”
- **Subagents.** Read-only localizer / test investigator with **clean context** and attenuated caps. Single writer. Merge by exterior tests, not LLM vote. Default HYDRA is not authorized.
- **Approvals.** Destructive git, network, secret files: Ed25519 / TTY confirm. Headless fails closed. **MECHANISM:** `runtime/governance/`.
- **Observability.** Per-turn cost, cache hit, tokens, elided labels, verification identity. You cannot improve what the ledger does not record.
- **Worktrees / sandbox.** Speculative patches off the user’s dirty tree.
- **MCP / user tools.** Extension point; still go through `Kernel.dispatch`.
- **Honest scoring.** Dry-run ≠ pass. Cassette ≠ lift. Official SWE/DeepSWE only on their harness.

---

## 23. One-picture architecture

How the pieces fit (suggestion §13), with FACT labels on existing boxes and `[PROPOSAL]` on 2PC / tamper / director:

```text
                    ┌──────────── CLI / TUI ────────────┐
                    │ run/resume/stream/cost/approvals  │
                    │ FACT: facade run/status/resume/   │
                    │   evidence/cost; presets          │
                    │ [PROPOSAL]: cancel/doctor/        │
                    │   checkpoint / NDJSON             │
                    └───────────────┬───────────────────┘
                                    ▼
                    ApplicationService   FACT
                                    ▼
         ┌──────────────── EpisodeEngine ────────────────┐  FACT product loop
         │  ContextCompiler (L1–L5, cache, compact)      │  FACT freeze L1–L3
         │       ▲  σ fold (goal, plan, dead ends)       │  FACT CodingTaskState
         │       │  memory hits (granted)                │  FACT authorize→recall
         │       │  skill bodies (on demand)             │  MECHANISM lifecycle
         │       │  repo map (epoch-bound, omitted*)     │  FACT index; L3 dump BUG
         │  propose → recover schema → Kernel.dispatch   │  FACT
         │  tools: read/search/edit/txn/shell/index/test │  txn = [PROPOSAL]
         │  ingest truncated receipts                    │
         │  AdmissionGate ← VerificationReceipt          │  FACT (exemption leak)
         │  meta: advise only                            │  FACT powerless
         │  2PC / tamper / director                      │  [PROPOSAL]
         └───────────────────────────────────────────────┘
              ledger + budgets + sandbox + index.db
              STORE FACT: adapters/stores/event_store.py
              RETRIEVE FACT: adapters/stores/repo_index.py
```

Director / HYDRA / mutation-0.80 / kernel AST hook stay off this product picture except as `[PROPOSAL]` side boxes. Chimera Head 3 is not the product implementer.

---

## 24. Build order (so this does not become a graveyard of features)

Adding all of the above at once is how harnesses get worse. The reliability identity is:

$$
R = \prod_t \Pr(\text{honest progress}_t \mid \text{honest state}_{t-1})
$$

Practical order, aligned with Plan B (locked; do not invert with HYDRA-first topologies in §7):

1. **Cannot lie** — no `completed` without bound tests; no zero-test green; Forge cannot invent counts
2. **Can resume** — semantic task state, prefix freeze, crash continuation
3. **Can see** — epoch-bound index, progressive L5, output caps, cache-stable prefix
4. **Can change many files safely** — 2PC, syntax preflight, implicated-set, tamper shield
5. **Qualify one agent** — frozen suite, Wilson CI, cost $\kappa$
6. **Then** meta, specialists, campaign director, promoted skills/memory

You already have most **mechanisms** (compiler, compaction, memory SPI, skills packs, AST patch, admission, LDA). The product gap is **one truthful Coding Max path** that composes them so a long greenfield or multi-file brownfield session cannot declare victory from a paragraph of prose.

**Implementation numbering: B §18.** This file does not carry a competing ticket DAG. `SUB-*` / `M-HYD` in §8 remain `[PROPOSAL]` mapping onto B tickets 01–35.

---

## Appendix: Cross-link matrix (locked triad)

Duplicated in A, B, and v2 so no file is a stub.

| Concern | Canonical write-up | Competing variants kept as `[PROPOSAL]` |
|---|---|---|
| Reliability order | A §0, B §8 | v2 HYDRA-first topologies |
| Live gaps / tickets | B §4, §18 | A §31 (less precise on exemption); v2 §8 IDs |
| Lattice placement | B §6.12 | A §6.2–6.3 port explosion; v2 new packages |
| L1–L5 + σ | v2 §3 + B §4.4 | dumping σ into L3 (current code, not target) |
| 2PC / AST | v2 §4.2 adapter | v2 §4.3 kernel hook (rejected) |
| Completion policy | A §9.4 per class | v2 I-1 universal signed finish |
| Forge/Chimera | B §3.5 quarantine | v2 Head 3 Chimera as product |
| Director / HYDRA | v2 §7, A waves 7–8, B waves 7–8 | default swarm |
| Mutation 0.80 | v2 §5.4 | as admission law |
| CLI | A appended operator surface | TUI visual design (A non-goal) |
