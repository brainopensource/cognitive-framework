---
id: execution.feature_spec
canonical_id: execution.feature_spec
class: execution
authority: execution
status: living
owner: repository-governance
canonical_for:
  - active-feature-delta-specification
version: "2.0.0"
date: "2026-09-04"
last_verified: 2026-09-04
lock_head: "66aa7a3c0c31"
derived_from:
  - .draft/DEVELOPMENT_FINAL_PLAN.md
  - .draft/DEVELOPMENT_FINAL_PLAN_B.md
  - .draft/DEVELOPMENT_FINAL_PLAN_v2.md
  - .draft/PHASE-0_DEVELOPMENT_FINAL_PLAN.md
normative_authority:
  - docs/architecture/boundaries.md
relationships:
  - execution.milestones
  - execution.backlog
  - execution.tasks
  - execution.technical
---

# Feature & Target Specification (execution)

This document is the authoritative specification and typed delta contract for the active execution runway and TARGET release predicates.
Lock SHA `66aa7a3c` is the forensic baseline. Implementation head for closed instrument work: `63b77116`. Resume closed at `8637db55` (MS-RESUME `CLOSED`).

Companion handbook: [`technical.md`](technical.md). Task IDs: [`tasks.md`](tasks.md).

## 0. Normative System Clauses (TARGET Law)

### 0.1 Identity and causal truth
- **`TC-E-001`** AETHER **MUST** remain a general event-sourced agentic-computation substrate, not a domain-specific harness, workflow engine, or certification system.
- **`TC-E-002`** The fundamental execution unit **MUST** be a typed causal operation within an execution lineage.
- **`TC-E-003`** Durable causal events **MUST** be authoritative facts; large content **MUST** be content-addressed artifacts; projections, indexes, caches, and telemetry **MUST NOT** become a second truth.
- **`TC-E-004`** Replay of persisted facts and probabilistic re-execution **MUST** remain distinct.
- **`TC-E-005`** An agent **MUST** be represented as identity, policy, event-derived projection, and execution boundary. No persistent in-memory Agent object may be required for semantic continuation.

### 0.2 Trusted execution
- **`TC-E-022`** The S0–S12 microkernel **MUST** remain a bounded, domain-blind reference monitor for admissibility, authority, generic budgets, and effect settlement.
- **`TC-E-023`** Capability grants constrain agents; isolation policy constrains plugin code. Neither authority system may substitute for the other.
- **`TC-E-029`** All privileged effects **MUST** preserve declared-versus-emitted identity, merge controls at the call site, persist intent before dispatch, and fail closed on forged or widened authority.
- **`TC-E-030`** Production replay parity **MUST** reconstruct durable storage in a fresh process.
- **`TC-E-031`** Evaluation authority **MUST** remain exterior, identity-separated, and cryptographically bound.
- **`TC-E-032`** Plugins **MUST** be untrusted by default and isolation claims **MUST** be measured rather than asserted.
- **`TC-E-033`** The kernel and domain **MUST** remain domain-blind and within the ratified Trusted Core budget.

### 0.3 Composition, turns, and extensibility
- **`TC-E-008`** Static composition declares available capabilities; the durable trajectory records what actually occurred. Neither graph may impersonate the other.
- **`TC-E-038`** The sole production chain **MUST** remain `mhf.manifest/2 -> CanonicalManifest -> FrozenComposition -> ActivationPlan -> RunPlan -> EpisodeEngine`.
- **`TC-E-039`** The canonical turn loop **MUST** remain unary and sequential except where a separately ratified, measured disposition explicitly authorizes a bounded case.
- **`TC-E-040`** Runtime profiles **MUST** be explicit and identity-bearing in `D_R`; unavailable requested containment **MUST** fail closed.
- **`TC-E-041`** Plugin activation **MUST** materialize a usable service or handle, or fail. Lifecycle metadata alone is not activation.
- **`TC-E-027`** JSON Schema, JCS, and golden vectors are the wire source of truth; generated readers SHOULD replace handwritten mirrors.
- **`TC-E-053`** Pure deterministic transforms, bounded protocol recovery with no silent execution, state-dependent tool policy, deterministic failure attribution, and fail-closed preflight are the accepted `ADR-0106` evolution seam.

### 0.4 Delegation, topology, and budgets
- **`TC-E-013`** `agent.spawn` **MUST** be the sole recursive-delegation primitive and re-enter the ordinary runtime through an attenuated child lineage.
- **`TC-E-014`** Child action, resource, constraint, depth, turn, and budget authority **MUST NOT** exceed the parent.
- **`TC-E-042`** Additive resources are exactly `usd_micros`, `millis`, `tokens`, and `bytes`; depth and turns are structural ceilings.
- **`TC-E-017`** Topology declarations carry no authority. Ready roles **MUST** execute as ordinary mediated children and exchange dependency context through authorized artifact references.
- **`TC-E-049`** The required direct, planner/executor/reviewer, and fork/read/merge topologies **MUST** demonstrate real effects and persisted artifact flow before acceptance.
- **`TC-E-052`** `mhf.topology/2` is an accepted workflow seam, not authority for a second runtime or unrestricted concurrent execution.

### 0.5 State, memory, learning, and evidence
- **`TC-E-018`** Memory retrieval **MUST** verify scoped, revocation-aware authorization before ranking and artifact dereference; retention never authorizes capture.
- **`TC-E-019`** Learned compositions **MUST** be immutable, content-addressed, evaluated on held-out workloads, promoted by authority distinct from generator/evaluator, and reversibly rolled back.
- **`TC-E-026`** `D_H`, `D_R`, and `D_X` **MUST** remain distinct identities and bind every behavior-affecting input at their respective planes.
- **`TC-E-035`** A completed trajectory **MUST** preserve invoked-turn attribution, explicit missingness, conserved cost, and the verified pre-crash prefix.
- **`TC-E-043`** New production event envelopes **MUST** use `mhf.event/2`; compatibility readers may accept frozen predecessors without rewriting historical identities.
- **`TC-E-046`** Facts, artifacts, projections, telemetry, and attestations **MUST** remain distinct. Only exact-subject, digest-addressed, independently verified receipts may close mandatory gates.

### 0.6 Context, completion, recovery, and coding-harness evidence
- **`TC-E-054`** Repository intelligence **MUST** remain an optional, authority-free projection above the substrate. A provider **MUST NOT** grant capabilities, propose or dispatch effects, replace canonical documentation or durable causal facts, or become a required dependency of the domain or kernel. Domain packs and adapters **SHOULD** consume it through the existing context and index seams and **MUST** preserve a deterministic source-level fallback.
- **`TC-E-055`** A bounded repository-context packet **MUST** identify the task, repository snapshot, provider and provider version, query, selected references, estimated token cost, and material omissions by stable identities or digests. It **MUST NOT** imply completeness, freshness, or authority merely because retrieval succeeded.
- **`TC-E-056`** Context selection **MUST** satisfy an explicit token budget. For selected items $S$ and context budget $B_C$, $\sum_{i \in S}\operatorname{tokens}(i) \le B_C$. Composition **MUST** reserve sufficient capacity for at least one bounded recovery or verification cycle; a non-compactable prefix and task state **MUST NOT** consume the entire usable context window.
- **`TC-E-057`** Compaction **MUST** retain the task identity and constraints, current plan or next action, modified resources, last material failure, latest applicable verification, settled effects, and remaining budgets. It **MUST** be identity-bearing and observable; it **MUST NOT** silently erase information required to determine whether completion or another effect is admissible.
- **`TC-E-058`** Model-requested finish **MUST NOT** by itself establish successful completion. Where task policy requires verification, completion **MUST** be admitted only by an applicable successful verification receipt bound to the current task and current post-effect subject. A receipt invalidated by a later relevant effect, a zero-test collection, or a mismatched subject **MUST NOT** admit completion.
- **`TC-E-059`** Harness-local verification and exterior evaluation **MUST** remain distinct. Local verification MAY govern operational completion; it **MUST NOT** self-certify benchmark success, assurance, promotion, or release evidence. Exterior evaluators remain subject to `TC-E-031` and `TC-E-046`.
- **`TC-E-060`** Recovery decisions **MUST** be typed, bounded by failure class, budget-aware, and durably attributable. A retry **MUST NOT** repeat an identical action with identical arguments against materially unchanged state unless the classified failure is transient and the policy explicitly admits another bounded attempt. Exhaustion **MUST** terminate or replan explicitly rather than loop silently.
- **`TC-E-061`** A successful patch effect **MUST** bind its input subject, verify the required preimage or anchors, apply every declared hunk within the authorized workspace, and record the resulting postimage identity. Ambiguous anchors, partial application, workspace escape, or a postimage mismatch **MUST** fail closed and **MUST NOT** be represented as patch success.
- **`TC-E-062`** A benchmark-qualifying run record **MUST** bind at minimum the run and task identities, repository snapshot, harness/configuration identity, provider/model identity, trajectory or event-log identity, terminal state and reason, produced patch identity when applicable, verification and evaluator receipt identities, and explicit token, cost, latency, turn, tool-call, and retry values or missingness. Repeated attempts **MUST NOT** be represented as independent task coverage, and a record lacking its immutable trajectory linkage **MUST NOT** support a capability claim.

### 0.7 Product and release boundary
- **`TC-E-047`** M-9 remains a TARGET operational beta: unified configuration and clients, packaged CLI/API/TUI/Studio, real plugin lifecycle, health/readiness, two real workflows, restart/resume, and offline-after-install behavior.
- **`TC-E-048`** M-10 remains a TARGET final release: supported migrations, backup/restore, deployment profiles, fault injection, security/performance qualification, reproducible artifacts, soak evidence, and an exact-subject signed release envelope.
- **`TC-E-050`** Every client start-run path **MUST** select a valid runtime profile consistently with the identity-bearing profile contract.
- **`TC-E-051`** Client surfaces SHOULD converge on a coherent command and configuration model without moving runtime authority into the clients.

### 0.8 Inviolable Architectural Refusals
AETHER does not authorize a second runtime, a domain-aware kernel, authoritative in-memory agent state, a workflow DAG with independent authority, self-certified promotion, silent containment downgrade, or evidence backfill. Any reversal requires current normative amendment and the required falsifiers; implementation convenience is not authority.

## 0. Invariants

- **I-7.** AST preflight SHALL NOT enter `kernel/dispatch.py` S7/S8. Syntax checks: `adapters/environment/`.
- **I-TCB.** Kernel LOC ≤ 1438 (live 1386 at last A linter pass).
- **INV-DELTA-1.** Domain state schemas: stdlib + JCS only.
- **INV-DELTA-2.** This program SHALL NOT grow kernel past the TCB ceiling.
- **INV-DELTA-3.** Multi-file writes are all-or-nothing. Preflight in the adapter. MECHANISM this-branch (T-17). Product MS-CHANGE remains `OPEN` (T-47–T-49 `[PROPOSAL]`). T-18–T-20 are MECHANISM.
- **INV-DELTA-4.** Agents SHALL NOT mutate tests during implementation. Tamper shield MECHANISM this-branch (T-18). Enumerate via IndexPort, not `Path.glob("test/**")`. Product MS-CHANGE remains `OPEN` (T-47–T-49). Session `_tamper_shield.evaluate(...)` still unwired (B owns the admission call).
- **INV-DELTA-5.** L1–L3 prefix-stable. Compaction SHALL NOT drop settled invariants or falsified hypotheses.
- **I-STATE.** σ is a ledger fold (`fold_task_state`). One schema: `SemanticTaskState` with alias `CodingTaskState`. Lock: `domain/task_state.py` MISSING. Branch: LIVE `8637db55`. MS-RESUME `CLOSED`.
- **I-TXN.** 2PC lives in `adapters/environment/transaction.py`. This branch LIVE (T-17 MECHANISM). Lock `66aa7a3c` MISSING. Not kernel.
- **Single-writer.** One writer per workspace.
- **Authorize-before-retrieve.** Memory recall requires grant.

**Canonical path (FACT).** `ApplicationService → Runtime → HarnessSession → EpisodeEngine → Kernel.dispatch`.
Forge/Chimera SHALL NOT be the product path. Coding Max report arms SHALL be ⊆ `{vg-code-fast, vg-code-balanced, vg-code-max}` (T-23).

**Admission (FACT).** `admission_required`: exempt `vg-code-default` / `vg-code-lex`, else `"patch.apply" in verbs`. `ADMISSION_GATED_HARNESSES` unused. T-04 `[PROPOSAL]` until RF-25 successor baseline.

**VerificationReceipt.passed (FACT).** `exit_code == 0 and executed_test_count > 0`. Unknown → 0. Forge SHALL NOT set `test_count = 1` (T-06). Chimera SHALL NOT invent `executed = 1` on non-zero exit without a runner summary (`63b77116`).

**I-1** (v2) universal signed finish: `[PROPOSAL]` too strong. A §9.4 wins. Fail-to-pass = **bugfix** only (T-38).
**Mutation ≥ 0.80:** T-39 `[PROPOSAL]`.

## 1. Instrument (CLOSED — `63b77116` + T-01–T-03)

B20 discovery SHALL require `aether.b20.membership/1`. Directory names insufficient. `__pycache__` / hidden / tmp are not tasks. Missing oracle, duplicate ids, digest mismatch → fail closed. Digest is order-independent. Every empirical JSON / `BenchmarkReceipt` SHALL bind `subject_sha`. Missing SHA → refuse. `dry_run` ⇒ `pass`/`cost`/`oracle`/`oracle_passed` null. PASS without patch digest → refuse. Dispositions exactly `{passed, failed, undeterminable, not_run}`. Provider / harness / `DATASET_INVALID` ≠ task fail. Qualifying dirty tree → fail closed (`require_clean_subject`). BAAC SHALL require `aether.baac.challenge/1`; bare `TASK.md` is not a challenge.

## 2. Product thesis and non-goals

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

## 3. VerificationReceipt + counts

Session parser target (T-08): `collected`/`executed`/`passed`/`failed`/`skipped`; `Ran 0 tests` / `0 passed` → 0; unknown runner stays unknown. **B landed the session parser and pack `ParsedTestOutput.runner` on `8637db55` (T-08 `[x]`). Do not uncheck.**

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

**FACT.** Schema is `vanguard/packages/domain/task_state.py` (`SemanticTaskState` / `CodingTaskState` alias). The only fold remains `runtime/task_state.py` `fold_task_state`. A's 17 extra domain types stay `[PROPOSAL]` law-side targets; do not implement them here.

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

## 4. Task classes and per-class evidence

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

## 10. Prompt, policy, model, security

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

## 11. Stop, simplify, and rollback

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

## 12. Research, explanation, and benchmark taxonomy

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

## TransformSpec (proposal sketch + live fields)

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

## 9. CLI and verbs

MECHANISM: `run` / `status` / `resume` / `evidence` / `cost`. `[PROPOSAL]`: `cancel` / `doctor` / `checkpoint` / `--non-interactive`.

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

## WorkspaceEpoch (T-14)

Lock `66aa7a3c` **MISSING**. This branch **LIVE** — see §6 / §14.

```text
WorkspaceEpoch := { treeHash, indexDigest, sourceRevision, compiledAtTurn }
```

Stale epoch ⇒ refresh or fail closed. Do not put `repo_map` or σ into frozen L3.

## Dialect FACT split

Wire recovery: `adapters/models/dialect.py` T-21 MECHANISM. Truncated JSON, DeepSeek fence, and XML tool tags are classified; malformed never reports `ok`. Malformed → Proposal: `agency/episode/protocol_recovery.py`. Taxonomy in Appendix H §8.

## 2PC / tamper placement

- 2PC: `adapters/environment/transaction.py` this-branch LIVE (T-17 MECHANISM). Lock `66aa7a3c` MISSING. Multi-file `GitEnvironment.apply` preflights `ast.parse` then all-or-nothing flush. Single-file sequential observation (S8-B-09) unchanged. T-18–T-20 MECHANISM; MS-CHANGE stays `OPEN` on T-47–T-49.
- Tamper: `runtime/governance/tamper_shield.py` this-branch LIVE (T-18 MECHANISM). Lock `66aa7a3c` MISSING. Enumerate via IndexPort; `Path.glob("test/**")` is insufficient. Session `_tamper_shield.evaluate(...)` still unwired (B owns the admission call).

---

## 5. Task state

Implementation merge is B §6.12: `SemanticTaskState` in `domain/`; `fold_task_state` in `runtime/`; unknown event kinds ignored; no `"test" in action.lower()`. A §6.2 extra types stay `[PROPOSAL]` in §16. `task_class` is a field on the projection (T-43).

Branch: `vanguard/packages/domain/task_state.py` defines `SemanticTaskState` and `CodingTaskState = SemanticTaskState` (`8637db55`).

## 6. Context packet and WorkspaceEpoch

Keep `ContextPacket`. FEATURE_SPEC 4-tier budget is L4/L5 **policy** on existing `ContextCompiler` (not `progressive.py` as a second compiler) — T-15 this-branch **LIVE**. `WorkspaceEpoch := {treeHash, indexDigest, sourceRevision, compiledAtTurn}` this branch **LIVE**; lock `66aa7a3c` **MISSING**. T-14. Product compile stamps epoch on the existing packet; write refreshes the index then rebinds (T-16); stale or missing epoch MUST NOT admit `completed`. Tool bodies are distilled at the effect boundary with a goal echo at L5 (T-36). Packet `omissions` is a ledger; truncated ≠ complete (T-37). IndexPort unbound/down binds epoch from the environment snapshot with explicit `index.port.unbound` or fail-closed `INDEX_UNBOUND` — never invents symbols (T-45). Legacy packets without epoch may still resume via identity fields. T-46 ranking stays `[PROPOSAL]`.

## 7. 2PC and tamper

Living rule: T-17–T-20 MECHANISM — 2PC, IndexPort tamper freeze, greenfield vacuous-oracle reject, brownfield implicated-set fail-closed this-branch LIVE; lock `66aa7a3c` MISSING. Product MS-CHANGE remains `OPEN` (T-47–T-49 `[PROPOSAL]`). Historical CMX-09 schemas remain in Appendix H.

## 8. Dialect

Wire recovery: `adapters/models/dialect.py` T-21 MECHANISM. Truncated JSON, DeepSeek fence, and XML tool tags are classified; malformed never reports `ok`. Proposal recovery remains `agency/episode/protocol_recovery.py`.

## 9. Electroweak v0.9.3 Wave 1–2 settlement and control delta

This section is the typed TARGET contract for the Electroweak Wave 1–2 package
set. It points to the product definition in §3.2 and does not replace the
historical Wave 0–10 capability recipes in [`technical.md`](technical.md).
Wave 1 is Settlement & Signal Truth; Wave 2 is Frozen Control, Honest
Instrument & Presets. Edit/retrieval, context/reliability, and outer-director
treatments remain outside this delta and MUST NOT be presented as Wave 1–2
next-code.

### 9.1 Two-axis settlement wire contract (TRUTH / T-72)

The settlement model SHALL preserve two orthogonal questions:

| Axis | Domain | Values | Existing ledger representation |
|---|---|---|---|
| run termination | `RunTermination` in `agency` | `completed`, `abstained`, `escalated`, `cancelled`, `budget_exhausted`, `instrument_error`, `runtime_error`, `abandoned` | `EpisodeCompleted` with `terminal_status` only |
| task evaluation | `TaskDisposition` in `domain/evidence` | `passed`, `failed`, `undeterminable`, `not_run` | `VerdictRecorded` with `schema: aether.settlement/1` |

`TaskDisposition` is the shared four-state vocabulary. Only `passed` satisfies
an acceptance predicate. `undeterminable` and `not_run` are missingness, not a
negative task result. `disposition_to_outcome()` SHALL refuse `not_run` because
an evidence envelope binds a claim about an executed subject and therefore has
only `passed | failed | undeterminable` outcomes.

`SettlementReceipt` SHALL be a domain-pure, immutable value with this logical
shape; §3.2 of the Synthesis of Record owns the future module body and MUST NOT
be pasted into this specification:

```text
aether.settlement/1 := {
  taskId: non-empty string,
  disposition: TaskDisposition,
  terminalStatus?: string,
  oracleDigest?: digest,
  verificationSubjectDigest?: digest,
  executedTestCount: integer >= 0,
  envelopeDigest?: digest,
  undeterminableReason?: non-empty string
}
```

The value SHALL refuse all of the following:

- `passed` when `executedTestCount == 0`;
- `passed` without both `oracleDigest` and `verificationSubjectDigest`;
- `undeterminable` without `undeterminableReason`;
- `not_run` with any execution count, oracle digest, verification-subject
  digest, or envelope digest;
- an empty `taskId`, a negative test count, or an unknown disposition.

`terminalStatus` remains a plain string in the domain value: `domain` SHALL NOT
import `agency`, and neither axis SHALL be computed from the other. In
particular, oracle `passed` MUST NOT rewrite a run to `completed`.
`terminal_status=abandoned` with `disposition=passed` is legal and MUST replay
without contradiction. Conversely, `EpisodeCompleted` MUST NOT gain a
`disposition` field.

No new ledger event kind is allocated. The existing `EpisodeCompleted` and
`VerdictRecorded` owners SHALL carry the axes above. Adding an event kind still
requires its complete allocation package; this delta does not authorize one.
The benchmark vocabulary SHALL derive from `TaskDisposition`, and readers MUST
use its positive predicate rather than `disposition != failed`.

### 9.2 Wave 1 — Settlement & Signal Truth

Wave 1 is Route R repair work across **HAR-01**, **TRUTH**, **INS-01**, and
**BRG-01**. Its acceptance contract is:

| Package | Binding contract |
|---|---|
| HAR-01 | `NATIVE` tool calling is capability-bound. A production route may declare `ToolCallStyle.NATIVE` only after a provider-shape vector verifies native dispatch of both `patch.apply` and `finish`. Unknown or unverified routes retain the fail-closed degradation chain `NATIVE -> JSON_SCHEMA -> FENCED_JSON -> TEXT_GRAMMAR`; no registry-wide promotion is permitted. Manifest approval policy, the declared `finish` tool, minimum orientation commands, effect budgets, workspace initialization, and completion-tool restrictions SHALL reach the product path without hardcoded replacement. Fenced action notes MAY recover into candidate proposals, but unparsed invocations or a mutation-free unsolicited `finish` SHALL be rejected. |
| TRUTH | Record both settlement axes per §9.1. Before T-04 removes the product-default admission exemption, preserve the named RF-25 successor baseline. Mutating completion SHALL bind the mutation receipt, current postimage/epoch, relevant tests collected and executed, zero test exit, tamper evaluation against the frozen test set, and no unresolved omission or stale-index marker. Greenfield evidence SHALL distinguish structural from behavioral success and reject `pass` / `NotImplementedError` vacuity. The greenfield prompt SHALL not prohibit the scaffold -> red oracle -> atomic 2PC workflow. |
| INS-01 | Generate a unique run identity for each invocation; continuation is explicit `--resume <id>`. Product receipts SHALL carry actual model routes, token counts, verified step identities, and cost provenance. This package extends product-path integrity and MUST NOT reopen §1 or `MS-INSTRUMENT`. |
| BRG-01 | Local inference lifecycle is fail-closed: valid flash-attention flag, live child process, matching PID and `/props` identity before `ONLINE`, identity-scoped stop rather than blanket process killing, typed empty/max-token failures, and no retired provider alias on the supported route. |

HAR-01 additionally requires reproduce-first handling for uncertain boundaries.
The streaming abort at T-70a MUST be captured by a failing regression before a
fix is selected and MUST NOT be closed as `no_defect` from an earlier hedge.
Duplicate `EffectStarted`, unpopulated effect budgets, autonomous-loop tool
restriction, and Git initialization SHALL likewise be re-verified at current
HEAD before their repair boundary is chosen. Any resulting kernel change would
require separate authorization and TCB accounting; this documentation delta
does not change the 1386-line TCB baseline.

Wave 1 acceptance requires the L0 public-CLI smoke triad to produce honest
end-to-end evidence. L0 may license only “Wave 1 landed”; it MUST NOT license a
capability or pass-rate claim.

### 9.3 Wave 2 — Frozen Control, Honest Instrument & Presets

Wave 2 establishes the content-addressed control used by later treatments. It
contains **CMX-01 (T-79)**, the Wave 2 portions of **INS-01**, and **EXP-01**:

- The product path SHALL select the existing `aether.code-preset/1` catalog.
  It SHALL preserve the declared `fast`, `balanced`, and `max` budgets rather
  than inventing new values: respectively `(usd_micros, millis, tokens, turns)`
  are `(50000, 300000, 16000, 8)`, `(150000, 900000, 40000, 20)`, and
  `(400000, 2400000, 96000, 40)`. The facade SHALL NOT impose a universal
  `max_turns=40` default. Additive reservation dimensions remain
  `usd_micros | millis | tokens | bytes`; `turns` and `depth` remain structural
  ceilings and MUST NOT be summed as reservations.
- The frozen subject SHALL execute through the public product path, including
  `runtime.entrypoint.execute`; a direct `Runtime.execute_profiled` benchmark
  is a different subject and cannot qualify what ships.
- The candidate SHA, dirty flag, suite membership/digest, task and oracle
  digests, manifest/preset/model identities, provider/server identities,
  sampling/prompt/tool-schema digests, and cost provenance SHALL be frozen.
- `MS-CONTROL` closes only for single-worker `vg-code-balanced` on the exact
  candidate SHA at L2 with `n >= 30`, Wilson lower bound `>= 0.40`, and
  false-completion rate exactly zero. The result SHALL be published when
  positive, negative, or undeterminable.

### 9.4 Measurement ladder and evidence row (EXP-01)

Rungs answer different questions and SHALL NOT be collapsed:

| Rung | Frozen subject | License |
|---|---|---|
| L0 | `P0-FIB`, `P0-CSV`, `P0-BUG`; three fresh workspaces through the public CLI | Wave 1 smoke only; no pass rate |
| L1 | 4 greenfield + 4 single-file bug + 4 data/CLI tasks | fixture/oracle/instrument readiness only; tasks tuned here MUST NOT be scored |
| L2 | exact-subject product-path multi-class suite, `n >= 30` | control qualification and preregistered single-variable Route L verdicts |
| L3 | immutable `(manifest x model x preset)` bundle, `n >= 30` per arm | relative, task-class-specific arm claims only |

After the first measured attempt at a rung, changing a prompt, tool, fixture,
oracle, model, server flag, sampling policy, or budget resets that rung. Each
rung opens only after the lower rung is green on the current subject SHA; L2
also requires INS-01 and BRG-01, and L3 requires closed `MS-CONTROL`.

The harness SHALL append one immutable evidence row per run and refuse a row
with absent required data. Missingness is an explicit value, never a blank:

```text
identity:     subject_sha, dirty_flag, suite_digest, n, task_id, task_digest,
              oracle_digest, run_id
arm:          manifest_digest, preset, model_id, provider, server_build,
              gguf_digest, quantization, context_size, sampling_digest,
              prompt_digest, tool_schema_digest
execution:    evidence_label, raw_response_digest, valid_tool_calls,
              malformed_tool_calls, recovery_attempts, turns,
              time_to_first_valid_action_s, latency_s
change:       patch_digest, postimage_digest, files_changed, no_op
verification: tests_discovered, tests_executed, tests_passed, tests_failed,
              tamper_digest, tamper_verdict
settlement:   terminal_status, disposition, undeterminable_reason
economics:    prompt_tokens, completion_tokens, cache_read_tokens,
              cache_write_tokens, cost_usd_micros | local_time_proxy_s
provenance:   hypothesis_id | "control", control_digest, varied_dimension
```

`REPLAY`, `LIVE-HISTORICAL`, `STATIC`, `UNDETERMINABLE`, `LIVE-LOCAL`, and
`LIVE-HOSTED` evidence SHALL be labeled. Replay or historical evidence MUST NOT
share a published capability table with current live evidence. Zero model calls
settle as `not_run`, never as model failure. Undeterminable rows require a
reason and are excluded from capability denominators. A result writer SHALL
refuse `pass_rate_pct` when the observed result count is smaller than the frozen
suite size. Every non-control mechanism SHALL bind to a preregistered hypothesis
and one varied dimension.

Every control and treatment report SHALL publish false-completion rate, live
oracle pass rate with Wilson lower bound, valid first-tool-call rate,
malformed-tool/recovery rate, no-op rate, time to first valid action, turn waste
`W`, and token efficiency `kappa`. False-completion rate `= 0` is a hard veto:
no pass rate, lift, latency, token, or cost advantage can override it. Only
`LIVE-*` current rows enter capability rates.

## 13. Stop-rollback / research-explanation remainder

SHALL text for stop/simplify/rollback and research/explanation lives in §§11–12 above. Do not treat handbook prose as HEAD architecture.

## 14. MISSING vs HEAD

| Module | Lock `66aa7a3c` | This branch |
|---|---|---|
| `domain/task_state.py` | MISSING | LIVE (`8637db55`) |
| `runtime/task_state.py` `fold_task_state` | LIVE (old schema) | Fold of domain type (`8637db55`) |
| `adapters/environment/transaction.py` | MISSING | LIVE (T-17 MECHANISM). Lock `66aa7a3c` still MISSING |
| `runtime/governance/tamper_shield.py` | MISSING | LIVE (T-18 MECHANISM). Lock `66aa7a3c` still MISSING |
| `agency/context/progressive.py` | MISSING | Do not add — policy on `ContextCompiler` |
| `runtime/event_store.py` | MISSING | Owner remains `adapters/stores/event_store.py` |
| `ADMISSION_GATE_EXEMPT` | FACT | Unchanged. T-04 not started |
| `domain/workspace_epoch.py` `WorkspaceEpoch` | MISSING | LIVE (T-14). Lock `66aa7a3c` still MISSING |
| Index refresh after write (T-16) | MISSING | LIVE (`33dc7c33`) |
| L4/L5 policy on `ContextCompiler` (T-15) | MISSING | LIVE (`2a4cdaad`); no `progressive.py` |
| ResultDistiller + L5 goal echo (T-36) | MISSING | LIVE (`179f5616`) |
| Packet omission ledger (T-37) | MISSING | LIVE (`81b7b572`) |
| No-index fallback (T-45) | MISSING | LIVE (`c7995195`); `INDEX_UNBOUND` typed |

## 15. Error / verification matrix

Living refusals: T-42 / T-38 / T-25 in §1 and §4. A §24 handbook matrix stays in [`technical.md`](technical.md).

## 16. `[PROPOSAL]` catalogs

A §6.2 17 types, extra ports, CampaignPlan, mutation 0.80 — tagged `[PROPOSAL]`. B §6.12 wins for what to implement.

---

*Historical CMX-09 draft. Living §§ 0–16 win.*

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
