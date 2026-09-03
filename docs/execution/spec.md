---
id: execution.feature_spec
canonical_id: execution.feature_spec
class: specification
authority: execution
status: active
owner: repository-governance
canonical_for:
  - active-feature-delta-specification
version: "2.0.0"
date: "2026-09-03"
lock_head: "66aa7a3c0c31"
derived_from:
  - .draft/DEVELOPMENT_FINAL_PLAN.md
  - .draft/DEVELOPMENT_FINAL_PLAN_B.md
  - .draft/DEVELOPMENT_FINAL_PLAN_v2.md
  - .draft/PHASE-0_DEVELOPMENT_FINAL_PLAN.md
normative_authority:
  - docs/SPEC.md
  - docs/architecture/boundaries.md
relationships:
  - execution.milestones
  - execution.backlog
  - execution.tasks
  - execution.technical
---

# Feature Delta Specification (execution)

This file is the typed SHALL-contract for **all remaining backend work**. Upon a task merging, promote landed contracts into present-tense `docs/architecture/` / `docs/backend/` / `docs/SPEC.md`. Modules marked **MISSING** do not exist at lock HEAD `66aa7a3c`.

Companion handbook: [`technical.md`](technical.md). Task IDs: [`tasks.md`](tasks.md).

Historical CMX-09-only delta is preserved as [Appendix H](#appendix-h-historical-cmx-09-delta).

**Kernel (I-7).** AST preflight SHALL NOT enter `kernel/dispatch.py` S7/S8. S7/S8 remain RESERVE/VERIFY. Syntax checks belong in `adapters/environment/`.

**FACT canonical path.** `ApplicationService` → Runtime → `HarnessSession` → `EpisodeEngine` → `Kernel.dispatch`. ForgeEngine and ChimeraEngine SHALL NOT be the product path. Coding Max report arms SHALL be ⊆ `{vg-code-fast, vg-code-balanced, vg-code-max}` (T-23).

**Admission (FACT).** Live function is `admission_required` (`runtime/session.py`): exempt `vg-code-default` / `vg-code-lex`, else `"patch.apply" in verbs`. `ADMISSION_GATED_HARNESSES` is unused. T-04 is `[PROPOSAL]` and needs an RF-25 successor baseline.

**VerificationReceipt.passed (FACT).** `exit_code == 0 and executed_test_count > 0`. Unknown counts stay 0. Forge SHALL NOT set `test_count = 1` (T-06).

**I-1 universal signed finish** (v2): `[PROPOSAL]` too strong. Per-class evidence (A §9.4) wins. Fail-to-pass is the **bugfix** class (T-38).

**Mutation score ≥ 0.80** (v2 §5.4): `[PROPOSAL]` optional treatment T-39, not default admission.

**I-STATE.** σ is a ledger fold. Do not dump `resume_state` JSON into frozen L3 (FACT current bug; T-12). `domain/task_state.py` is **MISSING** until T-09.

**Single-writer.** One writer per workspace; children that write are sequential or isolated worktrees.

**Authorize-before-retrieve.** Memory recall requires grant (`runtime/prompt_assembler.py`).

**Instrument truth (T-01–T-03, T-24, T-25, T-40, T-41).** B20 task discovery SHALL require a schema-valid `membership.json` (`aether.b20.membership/1`); directory names are insufficient. `__pycache__`, hidden, and tmp names are not tasks. Missing oracle, duplicate ids, or task-set digest mismatch SHALL fail closed. The task-set digest is order-independent over admitted ids. Every empirical B20 JSON and `BenchmarkReceipt` SHALL bind `subject_sha` to the frozen candidate `git rev-parse HEAD`; a missing SHA SHALL refuse the receipt. `dry_run` SHALL emit `pass`, `cost`, `oracle`, and `oracle_passed` as null. A PASS row or PASS receipt without a patch digest SHALL be refused. Empirical dispositions SHALL be exactly `{passed, failed, undeterminable, not_run}`; provider, harness, and `DATASET_INVALID` outcomes SHALL NOT count as task fail. A qualifying empirical run on a dirty Git tree SHALL fail closed. BAAC discovery SHALL require a schema-valid `challenge.yaml` (`aether.baac.challenge/1`); a bare `TASK.md` or directory name is insufficient.

---

## From A — product thesis, SOTA definition, non-goals

## 3. Product thesis and non-goals

### 3.1 Product thesis

AETHER should become an event-sourced operating substrate for engineering campaigns.

The unit of truth is a typed causal operation within a lineage.

The unit of delivery is a verified task contract.

The unit of long-horizon coordination is a durable campaign graph of task contracts.

The unit of learning is a promoted policy or skill with held-out evidence and rollback identity.

### 3.2 Definition of a SOTA engineering agent

A SOTA agent is not one that emits impressive prose.

It is one that maximizes accepted engineering value under constraints:

$$
\pi^*
=
\arg\max_{\pi}
\mathbb{E}
\left[
Q_{\text{functional}}
+ \lambda_a Q_{\text{architecture}}
+ \lambda_m Q_{\text{maintainability}}
- \lambda_c C
- \lambda_r R
\right],
$$

subject to:

$$
\text{authority}(a_t)\subseteq\text{grant}_t,
\qquad
\mathbf{B}_{t+1}\preceq\mathbf{B}_t,
\qquad
\text{accept}(\tau)\Rightarrow V_{\text{exterior}}(\tau)=\text{pass}.
$$

The quality terms mean:

- functional correctness under independent tests;
- architectural conformance under repository-specific constraints;
- maintainability across future changes;
- measured money, token, latency, and effect cost;
- security, regression, uncertainty, and evidence risk.

### 3.3 Non-goals for the backend program

The following are explicitly deferred:

- TUI visual design;
- desktop visualization;
- animated topology graphs;
- a second mutable agent-state database;
- a second execution engine for swarms;
- kernel-level coding semantics;
- automatic self-certification;
- uncontrolled autonomous skill installation;
- benchmark-specific hidden-test guessing;
- hardcoded role classes for every engineering title;
- unbounded parallel agents;
- 90% leaderboard marketing before exact reproducible evidence.

---


---

## From A — domain values, ports, verification receipt, progressive packet, campaign, single-writer

`[PROPOSAL]` catalogs below are kept in full. Implementation merge for task state is B §6.12 (see [`technical.md`](technical.md)).

## 6. Target backend architecture

### 6.1 Architectural shape

```text
Campaign Service
  -> durable CampaignPlan projection
  -> OuterLoopPolicy
  -> Runtime application service
  -> HarnessSession
  -> EpisodeEngine
  -> Kernel S0-S12
  -> capability-scoped adapters
  -> immutable receipts
  -> exterior evaluator
  -> campaign reducer
```

**[PROPOSAL]** Campaign Service as an extra layer above runtime execution. Keep the diagram. Director as a runtime client: see B §6.2 `[PROPOSAL]`.

**FACT (HEAD `66aa7a3c`).** The canonical live path is `ApplicationService → Runtime → HarnessSession → EpisodeEngine → Kernel`. There is no live `CampaignService` type on that path.

**Historical claim.** The stack above treats Campaign Service as the top of the product. That remains the long-horizon outer-loop target (Wave 8). It is not present as a live type and is not a second `EpisodeEngine`.

The outer loop is above runtime execution.

It must not bypass `ApplicationService`, `Runtime`, `HarnessSession`, or the kernel.

**Lock note.** The next three sentences restate the Campaign Service FACT above. Keep both wordings; they are not two layers.

**[PROPOSAL]** Campaign Service as an extra layer above the live stack. Keep the diagram; it is the long-horizon outer-loop target, not a live type.

**FACT (HEAD `66aa7a3c`).** The canonical live path is `ApplicationService → Runtime → HarnessSession → EpisodeEngine → Kernel`. Director as a runtime client: see B §6.2 `[PROPOSAL]`.

**Historical claim.** The diagram treats Campaign Service as the top of the stack. That wording remains the wave-8 target shape.

### 6.2 Required new domain values

**[PROPOSAL]** The eventual implementation should define domain-pure values for:

- `GoalContract`;
- `AcceptancePredicate`;
- `TaskClass`;
- `TaskObligation`;
- `Hypothesis`;
- `EvidenceRef`;
- `VerificationLevel`;
- `RepositoryEpoch`;
- `ContextSelection`;
- `CampaignPlan`;
- `CampaignNode`;
- `CampaignEdge`;
- `PackageHandoff`;
- `DirectorDirective`;
- `EscalationReason`;
- `StrategyTreatment`;
- `BenchmarkSubject`.

These values contain no model provider, filesystem I/O, or runtime authority.

**FACT (HEAD `66aa7a3c`).** The current fold is `CodingTaskState` in `runtime/task_state.py` (`fold_task_state`). `vanguard/packages/domain/task_state.py` is **MISSING**. Preferred merge is B §6.12: promote schema to domain, keep the fold in runtime, do not run two authorities forever. Do not delete `GoalContract` / `CampaignPlan` / the rest of this 17-value list; they remain law-side targets.

**Historical claim.** This section read as if the 17 values were required next-code. They are `[PROPOSAL]` relative to the live fold.

### 6.3 Required ports

**[PROPOSAL]** Prefer small ports that express stable capabilities:

- `TaskStatePort` for reading durable task projection;
- `RepositoryIntelligencePort` by extending or composing `IndexPort`;
- `VerificationPort` for typed runner evidence;
- `CampaignStorePort` over the existing event store semantics;
- `OuterLoopPolicyPort` for next-action decisions;
- `DirectorReviewPort` for bounded supervisory judgments;
- `StrategyRegistryPort` for qualified treatments;
- `BenchmarkExecutorPort` for exact-subject attempts.

Avoid provider-shaped interfaces.

Avoid a `SeniorDeveloperAgent` class hierarchy.

**FACT.** Live ports that already cover adjacent jobs include `IndexPort`, evaluator, event-store, and memory SPI. This eight-port list is a competing design versus B §6.12 lattice placement. Keep both; do not explode ports before composing existing ones.

### 6.4 Typed verification receipt

A verification receipt should contain at least:

```text
receipt_id
run_id
episode_id
task_digest
composition_digest
workspace_before_digest
workspace_after_digest
repository_epoch
command_argv
runner_kind
runner_version
exit_code
tests_collected
tests_executed
tests_passed
tests_failed
tests_skipped
selected_test_ids_digest
coverage_scope_digest
changed_surface_digest
stdout_artifact
stderr_artifact
started_at
finished_at
effect_receipt_digest
evaluator_identity
signature
```

Unknown fields remain unknown.

They are never converted to a cheerful default.

### 6.5 Progressive context packet

Each turn should receive a packet with explicit sections:

```text
immutable system core
tool schemas
goal contract
repository authority constraints
semantic task state
current plan frontier
active hypothesis and alternatives
ranked repository evidence
latest effect receipts
latest verification receipt
omitted-items report
remaining budget
next-action affordances
```

The packet carries selection identity and repository epoch.

After every write, dependency-changing command, or generated-file update, the epoch changes.

Stale packets cannot justify completion.

### 6.6 Durable campaign state

The campaign reducer should derive:

- declared objective;
- plan versions;
- node readiness;
- leased node ownership;
- attempt identities;
- package artifacts;
- package verdicts;
- unresolved interfaces;
- risk register;
- budget allocations;
- operator interventions;
- next ready nodes;
- terminal disposition.

The reducer must be deterministic.

Checkpoints remain disposable caches with proof obligations.

### 6.7 Content-addressed handoffs

Agents should exchange artifact references, not transcript copies.

A package handoff should contain:

- goal digest;
- plan-node digest;
- relevant source revision;
- changed-surface digest;
- interface delta digest;
- verification receipt references;
- unresolved risks;
- next recommended action;
- explicit uncertainty;
- content digest.

This provides bounded communication and replayable provenance.

### 6.8 Director semantics

The director may emit only:

- `dispatch_ready_node`;
- `request_revision`;
- `request_investigation`;
- `request_integration`;
- `pause_for_operator`;
- `reallocate_budget` within its grant;
- `close_campaign` when predicates resolve;
- `mark_undeterminable`.

The director may not:

- forge verification;
- write around the worker grant;
- mutate historical events;
- promote its own skills;
- declare exterior acceptance;
- silently add scope.

### 6.9 Single-writer rule

Parallel agents may investigate disjoint questions.

Repository writes should default to one active writer per workspace.

Alternative branches may be used only with explicit merge ownership.

Every merge is a new effect with its own verification obligation.

This avoids shared-worktree races and invisible conflict resolution.

---


---

## From A — task classes and per-class evidence

Per-class evidence wins over v2 I-1. Fail-to-pass (v2 §5.3) applies to class `bugfix`.

### 9.3 Task classes

Completion policy must branch on declared task class, not prompt keyword guessing.

Supported classes:

- `bugfix`;
- `feature`;
- `greenfield`;
- `migration`;
- `refactor`;
- `documentation`;
- `explanation`;
- `research`;
- `benchmark`;
- `architecture_plan`.

### 9.4 Per-class evidence

Bugfix requires:

- reproduced failure or explicit non-reproducibility reason;
- focused regression test;
- changed implementation;
- passing focused falsifier;
- no applicable regression failure.

Feature requires:

- acceptance requirements mapped to tests;
- public interface behavior;
- negative paths;
- compatibility checks;
- documentation obligation classification.

Greenfield requires:

- scaffold baseline;
- declared entrypoint;
- structural checks;
- behavioral tests;
- installation or startup smoke test;
- required files and configuration.

Migration requires:

- enumerated consumers;
- compatibility policy;
- transformed call sites;
- old-path negative check;
- integration verification.

Explanation requires:

- evidence-linked claims;
- inspected-symbol references;
- no workspace mutation unless requested;
- uncertainty markers.

Research requires:

- source provenance;
- claim-to-source mapping;
- date and version boundaries;
- contradiction handling;
- no fabricated citations.

This per-class evidence matrix **wins** as program law over v2 §5.3 / I-1 “no finish without signed `VerificationReceipt`”. That universal signed-finish rule remains `[PROPOSAL]` and is too strong versus this matrix and versus the local vs exterior evaluator split (B §3.4). Fail-to-pass is required for **bugfix**; it is not a universal finish law for explanation or research. Bugfix admission SHALL require a failing pre-verify and a passing post-verify; a vacuous reproducer (pre-verify already passing) SHALL be refused (T-38). `true` and `echo 10 tests passed` SHALL NOT admit completion (T-42).


---

## From A — prompt/policy, model strategy, security/operator

## 21. Agent prompt and policy architecture

### 21.1 Stable system core

The stable core should teach:

- evidence hierarchy;
- authority limits;
- state and uncertainty semantics;
- tool grammar;
- completion protocol;
- concise communication requirements.

It should not contain a giant tutorial for every task class.

### 21.2 Task policy fragments

Inject small policy fragments based on declared task class:

- bugfix method;
- greenfield method;
- migration method;
- research method;
- explanation method;
- review method.

Fragments are versioned and independently ablatable.

### 21.3 Dynamic state

Render the semantic task state in a compact machine-readable form.

Do not ask the model to reconstruct the plan from raw dialogue.

### 21.4 Tool ergonomics

Follow the Agent-Computer Interface principle:

- concise commands;
- predictable output;
- bounded observations;
- stable error classes;
- explicit truncation;
- exact path and line references;
- atomic patches;
- easy targeted tests;
- no misleading success responses.

### 21.5 Prompt evaluation

Treat prompt modifications as code changes.

Require:

- version identity;
- regression corpus;
- token cost delta;
- protocol compliance;
- paired benchmark evidence;
- rollback path.

---

## 22. Model strategy

### 22.1 Model-neutral substrate

The framework should remain model-neutral.

Model-specific behavior belongs in capability profiles, dialect adapters, and routing policy.

### 22.2 Routing tiers

Candidate tiers:

- cheap fast model for classification and bounded localization;
- balanced coding model for normal implementation;
- frontier model for high-risk architecture, hard recovery, or final review;
- deterministic local or cassette models for protocol testing.

### 22.3 Escalation

Escalate only when grounded conditions hold:

- repeated distinct failures;
- unresolved high-risk ambiguity;
- change surface above threshold;
- architecture decision required;
- current model violates protocol repeatedly;
- expected value exceeds incremental cost.

### 22.4 Provider failure

Provider errors must preserve:

- request identity;
- partial usage if known;
- retry policy;
- idempotency;
- no false task verdict;
- resume state.

### 22.5 Routing experiments

Compare:

- one strong model throughout;
- cheap localizer plus strong implementer;
- strong planner plus cheap implementer;
- cheap worker plus strong reviewer;
- dynamic escalation.

Hold task set, tools, context, and verification fixed.

---

## 23. Security, control, and operator semantics

### 23.1 Least authority

Each role receives the minimum scope needed.

Read-only investigators do not receive patch or shell write capabilities.

Reviewers do not receive promotion authority.

The director does not receive arbitrary workspace write authority.

### 23.2 Budget attenuation

For parent budget vector $\mathbf{B}_p$ and child $\mathbf{B}_c$:

$$
\mathbf{B}_c\preceq\mathbf{B}_p.
$$

Across siblings:

$$
\sum_c \mathbf{B}_c + \mathbf{B}_{\text{reserved}}
\preceq
\mathbf{B}_p.
$$

### 23.3 Human control points

Require operator approval for configurable risk classes:

- external publication;
- credential or secret access;
- destructive data changes;
- dependency release;
- production deployment;
- scope expansion;
- high-cost budget increase;
- benchmark submission;
- skill promotion to default.

### 23.4 TUI-ready backend events

Although frontend work is deferred, backend events should expose:

- campaign state;
- ready/running/blocked nodes;
- active lineage;
- current goal and next action;
- budgets;
- recent effects;
- verification level;
- pending approval;
- uncertainty;
- artifact links;
- director directives.

The future TUI becomes a projection and command client.

It must not become another runtime authority.

---


---

## From A — stop, simplify, and rollback

## 28. Stop, simplify, and rollback rules

Stop a treatment when:

- false completion rises;
- cost per signed pass worsens beyond preregistered tolerance;
- confidence interval excludes useful lift;
- architecture boundaries are weakened;
- replay identity cannot be maintained;
- operator control becomes ambiguous.

Simplify when:

- two roles produce materially identical outputs;
- an LLM judgment can be replaced by deterministic evidence;
- a topology adds latency without lift;
- a new port duplicates an existing generic port;
- a cache cannot prove freshness.

Rollback when:

- promoted skill regresses held-out tasks;
- model route changes protocol reliability;
- new context policy loses mandatory facts;
- new scheduler produces non-deterministic effect ordering;
- external evaluator reports subject mismatch.

---


---

## From A — research and explanation agents; benchmark taxonomy

## 25. Benchmark task taxonomy

### 25.1 Scope axis

- single symbol;
- single file;
- small multi-file;
- subsystem;
- cross-subsystem;
- repository-wide;
- multi-repository campaign.

### 25.2 Horizon axis

- under 10 expert minutes;
- 10-60 minutes;
- 1-4 hours;
- 4-16 hours;
- 16-40 hours;
- multi-day.

Human duration estimates need provenance and uncertainty.

### 25.3 Work-type axis

- localization;
- bug repair;
- feature delivery;
- migration;
- refactor;
- test creation;
- performance;
- security;
- greenfield;
- architecture;
- research;
- explanation.

### 25.4 Environment axis

- hermetic;
- local toolchain;
- sandboxed;
- networked read-only;
- external service;
- operator-gated.

### 25.5 Failure attribution axis

- model cognitive error;
- context selection error;
- tool interface error;
- protocol error;
- harness error;
- evaluator error;
- dataset invalid;
- provider error;
- budget exhausted;
- policy denial;
- undeterminable.

---

## 26. Research and explanation agents

### 26.1 Shared substrate

Research and explanation should reuse:

- task contracts;
- context selection;
- source provenance;
- budget accounting;
- event sourcing;
- artifact graphs;
- exterior evaluation;
- campaign planning.

### 26.2 Research workflow

```text
scope question
  -> declare freshness requirements
  -> retrieve primary sources
  -> extract claims
  -> triangulate contradictions
  -> maintain claim-evidence graph
  -> synthesize with uncertainty
  -> citation audit
  -> publish artifact
```

### 26.3 Explanation workflow

```text
identify audience
  -> route to symbols and owners
  -> inspect causal slice
  -> build minimal mental model
  -> cite exact code evidence
  -> test explanation against questions
  -> disclose uncertainty
```

### 26.4 Research verification

Verify:

- every material factual claim has a source;
- sources support the claim directly;
- temporal claims include dates;
- primary sources are preferred;
- contradictions are not hidden;
- quotations respect limits;
- local repository claims bind to current source revision.

---


---

## From v2 — TransformSpec (proposal sketch + live fields)

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

**FACT — live `TransformSpec` fields** from [`vanguard/packages/domain/transforms/contracts.py`](../../vanguard/packages/domain/transforms/contracts.py) lines 20–31 (HEAD `66aa7a3c`):

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


---

## From B — live tool/verb inventory and product target loop

## 22. Live tool/verb inventory (lock HEAD `66aa7a3c`)

Appended at lock; does **not** replace §3. **FACT** from pack YAML and toolkit source on HEAD `66aa7a3c`.

Harness [`packs/code-default/harness.yaml`](../../packs/code-default/harness.yaml) declares:

| Verb | Pack source | Notes (FACT) |
|---|---|---|
| `fs.read` | `harness.yaml` capabilities; `plugins/fs.yaml`; `toolkits/fs_toolkit.py` | Windowed: optional `start_line` / `end_line` in schema; full-file digest if omitted |
| `fs.search` | `harness.yaml`; `plugins/fs.yaml`; `FsToolkit` | Pattern search over workspace files |
| `fs.list` | `plugins/fs.yaml` + `FsToolkit` (not listed on the harness.yaml capability block) | Glob list; kernel classifier treats `fs.list` as observation |
| `patch.apply` | `harness.yaml`; `plugins/ast-patch.yaml`; `toolkits/ast_patch.py` | Sequential `GitEnvironment.apply`; post-write `ast.parse` is observation-only |
| `proc.exec` | `harness.yaml`; `plugins/terminal.yaml`; `toolkits/terminal_runner.py` | Allowlisted `git,pytest,ruff,python3` |

**Index toolkit.** [`packs/code-default/plugins/index.yaml`](../../packs/code-default/plugins/index.yaml) still declares capability verb **`fs.read`**. `IndexToolkit` in `toolkits/repo_map.py` also exposes `index.refresh`. Ranking stays out of `IndexPort` (observation-only). Pack also has `multi_file_completeness.py` and `GreenfieldPolicy` (MECHANISM; see §3.4).

**Facade (MECHANISM).** `CodingMaxFacade`: `run` / `status` / `resume` / `evidence` / `cost`; presets `fast|balanced|max`.

**Still MISSING in HEAD `66aa7a3c` (keep as `[PROPOSAL]`).** `transaction.py` 2PC, `tamper_shield.py`, `progressive.py`, `WorkspaceEpoch`, `agency/prediction/`, `runtime/event_store.py`, `adapters/index/`. Event store owner is `adapters/stores/event_store.py`; index owner is `adapters/stores/repo_index.py`. Edit/2PC mechanics live in **v2**; law/profiles live in **A**.

---

## 23. Product target loop

Appended at lock; does **not** replace §3.2 / §6.1. Product stages (SOTA suggestion):

```text
INGEST → DISCOVER → PLAN → EDIT → VERIFY_TARGETED → RECOVER → VERIFY_BROAD → COMPLETE
```

**FACT.** Stage transitions follow receipts, not conversational `finish`. Live inner loop is `ContextCompiler` freeze of L1–L3 at construction, then `EpisodeEngine`: observe → propose → `recover_proposal` → `Kernel.dispatch` → ingest (`agency/episode/engine.py`). Compile is **not** a step inside `EpisodeEngine`.

**FACT.** `admission_required` exempts `vg-code-default` / `vg-code-lex`, else `"patch.apply" in verbs`. `ADMISSION_GATED_HARNESSES` is unused in runtime. `VerificationReceipt.passed` ⇔ `exit_code == 0 and executed_test_count > 0`. Session `_observed_test_count` returns 0 if unparseable. Forge `parse_test_output` and Chimera bare-exit-0 parsing leave unknown counts at 0 (T-06).

**Pointer.** Reliability order and competency profiles: A. Tickets 01–35 and lattice: this file. 2PC / AST / later phenotypes: v2 as `[PROPOSAL]` except sequential git apply + post-write `ast.parse` (MECHANISM).

---


---

## Progressive context packet (binding placement)

Keep `ContextPacket`. FEATURE_SPEC 4-tier budget is **L4/L5 policy on existing `ContextCompiler`**, not a second compiler class (`PRG-01` alias → T-15).

| FEATURE_SPEC tier | Existing layer | Content |
|---|---|---|
| 0 Invariant anchor | L1 + L4 head | goal, active step, settled invariants |
| 1 Negative memory | L4 | dead ends, falsified hypotheses |
| 2 Active AST slice | L5 | current files, epoch-bound |
| 3 Symbol stubs | L5 remainder | IndexPort stubs with omissions |

## WorkspaceEpoch `[PROPOSAL]` (T-14)

```text
WorkspaceEpoch := { treeHash, indexDigest, sourceRevision, compiledAtTurn }
```

Stale epoch ⇒ refresh or fail closed. Do not put `repo_map` or σ into frozen L3.

## Dialect FACT split

Wire recovery: `adapters/models/dialect.py`. Malformed → Proposal: `agency/episode/protocol_recovery.py`. Taxonomy in Appendix H §8.

## 2PC / tamper placement

- 2PC: create `adapters/environment/transaction.py` (**MISSING**). `GitEnvironment.apply` is sequential today; `ast.parse` is post-write observation.
- Tamper: create `runtime/governance/tamper_shield.py` (**MISSING**). Enumerate tests via IndexPort (T-18); `Path.glob("test/**")` is insufficient.

---

# Appendix H: Historical CMX-09 delta

The following is the pre-PHASE-0 `spec.md` body, preserved in full.

# Feature Delta Specification: W-092-F1 / CMX-09 (Canonical Coding Max Convergence)

## 1. Architectural Base & Invariant Topography

This document is the authoritative typed delta contract for the active execution ticket **`W-092-F1 / CMX-09`**. It defines the exact interfaces, data schemas, transaction protocols, and error matrices added to the codebase. Upon gate passage and PR merge, these contracts are promoted into canonical `docs/architecture/` and `docs/SPEC.md`.

- **Base Architecture Extended**:
  - `docs/architecture/boundaries.md` (Hexagonal boundary flow: `domain <- ports <- kernel <- agency <- runtime -> adapters`)
  - `docs/architecture/data-flow.md` (Monotonic capability dispatch and immutable event emission)
- **Target Subsystems Modified**:
  - `vanguard/packages/domain/task_state.py` (New: Semantic task state vector & DAG)
  - `vanguard/packages/adapters/environment/transaction.py` (New: Two-Phase Commit Multi-File Transaction Manager)
  - `vanguard/packages/runtime/governance/tamper_shield.py` (New: Cryptographic Test Tamper Shield)
  - `vanguard/packages/agency/context/progressive.py` (New: Multi-Tier Progressive Context Compiler)
  - `vanguard/packages/adapters/models/dialect.py` (Enhanced: Multi-pattern recovery & typed failure classes)

---

## 2. Invariants & Boundary Constraints

- **INV-DELTA-1 (Hexagonal Purity)**: All state schemas (`SemanticTaskState`, `TaskStep`) in `domain/` must use Python stdlib only, serialize deterministically via RFC 8785 JCS, and contain zero I/O or adapter imports.
- **INV-DELTA-2 (TCB Line Budget Limit)**: No changes in this feature wave may increase `vanguard/packages/kernel/` beyond the strict $\le 1438$ logical LOC ceiling.
- **INV-DELTA-3 (Two-Phase Commit Atomic Safety)**: No multi-file modification may write partially to disk. All candidate file mutations must pass in-memory AST syntax validation (`ast.parse`) before disk flush. Any syntax error triggers full rollback to pre-transaction content.
- **INV-DELTA-4 (Anti-Tampering Test Isolation)**: Autonomous agents are strictly prohibited from mutating test suites during implementation. All test files are hashed at turn 0; any modification to test baselines produces immediate fail-closed rejection.
- **INV-DELTA-5 (Deterministic Progressive Context)**: System prompts and immutable invariants must form a prefix-stable anchor. Compaction must never truncate `settled_invariants` or `falsified_hypotheses`.

---

## 3. Data Contracts & Domain Schemas

### 3.1 Semantic Task State Vector (`domain/task_state.py`)

```python
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

class StepState(str, Enum):
    PENDING = "pending"
    READY = "ready"
    ACTIVE = "active"
    VERIFIED = "verified"
    FAILED = "failed"

@dataclass(frozen=True, slots=True)
class TaskStep:
    step_id: str                          # Monotonic ID: e.g. "step-001"
    title: str                            # Human-readable objective
    target_files: tuple[str, ...]         # Target files for this step
    dependencies: tuple[str, ...] = ()    # Pre-requisite step IDs
    state: StepState = StepState.PENDING
    falsification_evidence: str | None = None
    verification_digest: str | None = None

@dataclass(frozen=True, slots=True)
class SemanticTaskState:
    run_id: str
    revision: int                         # Monotonically increasing state version
    overarching_goal: str                 # Top-level immutable objective
    active_step_id: str | None            # Currently executing step
    backlog: tuple[TaskStep, ...]         # Ordered task DAG steps
    falsified_hypotheses: tuple[str, ...] # Negative memory: failed attempts not to repeat
    settled_invariants: tuple[str, ...]   # Verified architectural truths
    changed_files_tree_hash: str          # Current working tree SHA-256
```

---

## 4. Multi-File Two-Phase Commit (`2PC`) Transaction Protocol

### 4.1 Interface Specification (`adapters/environment/transaction.py`)

```python
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence
from vanguard.packages.domain.results import Result

@dataclass(frozen=True, slots=True)
class FileMutation:
    path: str
    content: str
    action: Literal["create", "modify", "delete"]

@dataclass(frozen=True, slots=True)
class TransactionReceipt:
    transaction_id: str
    mutated_files: tuple[str, ...]
    tree_hash_before: str
    tree_hash_after: str

class AtomicMultiFileTransactionManager:
    """Two-Phase Commit transaction manager guaranteeing zero half-broken multi-file states."""
    
    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root

    def execute_transaction(
        self,
        mutations: Sequence[FileMutation],
    ) -> Result[TransactionReceipt]:
        """Phase 1: Preflight in-memory shadow tree & AST check.
        Phase 2: Atomic commit to disk, or full rollback on any failure."""
        ...
```

### 4.2 Preflight Validation Rules:
1. Every modified or created `.py` file is validated via `ast.parse(source, filename=path)`. Syntax errors abort immediately.
2. Every imported symbol from local modules within the transaction set must resolve.
3. If any step fails, all original file contents are restored from in-memory pre-image snapshots.

---

## 5. Synthetic Test Oracle Bootstrapping Protocol

For greenfield tasks where no test suite exists in the baseline repository:
1. **Stage 1 (Contract Synthesis)**: Agent authors pure port interfaces / protocols under `vanguard/packages/ports/` or domain types.
2. **Stage 2 (Oracle Synthesis)**: Agent creates a synthetic test suite under `test/` defining terminal behavioral assertions.
3. **Stage 3 (Falsifier Confirmation)**: Agent runs the synthetic test against empty/stub implementations. **The test MUST fail** with expected `NotImplementedError` or assertion failure. If it passes on stubs, it is vacuous and rejected.
4. **Stage 4 (Freeze Oracle)**: The test file SHA-256 is registered in `TestTamperShield`.
5. **Stage 5 (Implementation)**: Agent implements code until the synthetic oracle passes.

---

## 6. Cryptographic Test Tamper Shield (`runtime/governance/tamper_shield.py`)

```python
from __future__ import annotations
import hashlib
from pathlib import Path

class TestTamperShield:
    """Guarantees agents cannot manufacture green passes by altering test files."""
    
    def __init__(self, workspace: Path, test_patterns: tuple[str, ...] = ("test/**", "tests/**", "*_test.py")):
        self._workspace = workspace
        self._patterns = test_patterns
        self._baseline_hashes: dict[str, str] = self._snapshot_hashes()

    def _snapshot_hashes(self) -> dict[str, str]:
        hashes: dict[str, str] = {}
        for pattern in self._patterns:
            for p in self._workspace.glob(pattern):
                if p.is_file() and p.suffix in (".py", ".ts", ".js"):
                    hashes[str(p.relative_to(self._workspace))] = hashlib.sha256(p.read_bytes()).hexdigest()
        return hashes

    def verify_integrity(self) -> tuple[bool, str]:
        """Fails closed if any test file was modified or removed."""
        for rel_path, expected_hash in self._baseline_hashes.items():
            f = self._workspace / rel_path
            if not f.exists():
                return False, f"Test file deleted: {rel_path}"
            if hashlib.sha256(f.read_bytes()).hexdigest() != expected_hash:
                return False, f"Test file tampered with: {rel_path}"
        return True, "Test integrity verified"
```

---

## 7. Progressive Context Compiler (`agency/context/progressive.py`)

Context is budgeted across 4 strict mathematical tiers:

```
Total Turn Budget (e.g., 16,000 tokens)
├── Tier 0: Invariant Anchor [Priority 100, Immutable] (~800 tokens)
│   ├── Overarching Task Goal + System Invariants
│   └── Current Active Step Specification
├── Tier 1: Negative Memory [Priority 90, Prefix-Stable] (~1,200 tokens)
│   └── Falsified Hypotheses List (Past failed patches and error signatures)
├── Tier 2: Active Working Slice [Priority 80, AST Sliced] (~4,000 tokens)
│   └── Exact AST slice of target function/class being edited (not full file)
└── Tier 3: Symbol Topology Stubs [Priority 70, Token-Bounded] (~6,000 tokens)
    └── Signatures and docstrings of directly referenced dependencies
```

---

## 8. Self-Healing Model Dialect Engine (`adapters/models/dialect.py`)

### 8.1 Typed Failure Taxonomy & Corrective Actions

| Failure Class | Root Cause Signature | Corrective Action |
|---|---|---|
| `TRANSPORT` | Socket reset, timeout, HTTP 5xx | `RETRY_TRANSPORT` with exponential backoff |
| `PROTOCOL` | Unparseable JSON, malformed schema | `DEGRADE_DIALECT` to markdown fenced JSON |
| `TRUNCATION` | Premature `finish_reason: length` | `CONTINUE_OUTPUT` requesting remainder |
| `TOOL_CALL` | Invalid tool name or missing args | `REPAIR_TOOL_CALL` feeding schema definition back |
| `PATCH` | Pre-image mismatch, hunk reject | `RELOCATE_AND_RECOMPILE` re-reading target file slice |
| `VERIFICATION` | Test failed with non-zero exit | `RECORD_FALSIFICATION` adding hypothesis to Tier 1 |
| `PERMISSION` | Capability or budget denial | `ESCALATE_APPROVAL` requiring human signature |

---

## 9. CLI Arguments & Invocation Surface

```text
vg code [OPTIONS]

Options:
  --plan PATH              Path to existing task plan DAG JSON.
  --brief PATH             Task description Markdown file (default: TASK.md).
  --preset [fast|balanced|max]
                           Execution profile preset (default: balanced).
  --budget-micros INT      Maximum cost ceiling in USD microdollars.
  --dry-run                Validate preflight syntax and AST without disk mutation.
  --tamper-shield          Enforce strict read-only test suite hash verification (default: true).
  --json                   Stream newline-delimited JSON events to stdout.
```

### Exit Codes
- `0`: Completed successfully; all task steps verified and admission gate passed.
- `1`: Verification failed; reproducer or test assertions failed.
- `2`: Invalid arguments, schema violation, or unparseable task brief.
- `3`: Unavailable; budget exhausted or provider connection refused.
- `127`: Missing system dependencies (e.g., neither `patch` nor `git` available).
