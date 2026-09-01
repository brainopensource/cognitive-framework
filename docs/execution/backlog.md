---
id: execution.backlog
canonical_id: execution.backlog
class: execution
authority: execution
status: living
owner: repository-governance
canonical_for:
  - repository-backlog
  - feature-lifecycle-tracking
version: 0.9.2a3
last_verified: 2026-08-31
purpose: Track proposed, approved, in-progress, blocked, and deferred capability packages and engineering work outside the active sprint WIP=1 constraint.
audience:
  - contributor
  - maintainer
  - release-owner
relationships:
  - execution.active
  - execution.milestones
  - spec.core
  - repo-root-vision
---

# AETHER / Vanguard: Feature & Capability Backlog

```text
====================================================================================================
Authority: Execution (Sequencing & Lifecycle Tracking)
Scope:     Capability Packages, Substrate Evolution, Tooling & Benchmarking Backlog
Lanes:     Lane A (Dev A — Senior Principal) | Lane B (Dev B — Independent Evaluator)
Invariant: Mechanism presence is not closure; state transitions require empirical receipts.
====================================================================================================
```

## 1. Lifecycle State Definitions

Every item in this backlog is managed through a strict predicate-driven lifecycle:

```mermaid
graph LR
    PROPOSED["PROPOSED<br/>(Candidate Idea / Hypothesis)"] -->|Architectural Review| APPROVED["APPROVED<br/>(Spec Ready / Awaiting WIP)"]
    APPROVED -->|Lane Capacity Available| IN_PROGRESS["IN_PROGRESS<br/>(Active in active.md)"]
    IN_PROGRESS -->|Evaluator Audit| REVIEWING["REVIEWING<br/>(Independent Verification)"]
    REVIEWING -->|Receipt Accepted| DONE["DONE<br/>(Verified & Merged)"]
    IN_PROGRESS -->|Unresolved Dependency| BLOCKED["BLOCKED<br/>(Prerequisite Missing)"]
    PROPOSED -->|Negative ROI / Lift| DEFERRED["DEFERRED<br/>(Rejected / Archived)"]
```

* **`PROPOSED`**: Candidate hypothesis, architectural proposal, or product feature under technical evaluation.
* **`APPROVED`**: Specification and falsifiers ratified; queued for active sprint execution once lane capacity (`WIP=1`) opens.
* **`IN_PROGRESS`**: Actively under implementation by the assigned lane owner in [`active.md`](active.md).
* **`REVIEWING`**: Code implemented; awaiting independent empirical evaluation and receipt production.
* **`BLOCKED`**: Execution halted due to prerequisite milestone gates (e.g., M-9 blocked on M-8).
* **`DONE`**: Implementation verified by passing tests, boundary checks, and frozen evidence receipts.
* **`DEFERRED`**: Candidate rejected or postponed due to lack of measured lift or architectural misalignment.

---

## 2. Capability Family Backlog

### 2.1 Substrate, Kernel & Event Sourcing (VISION.md §1–6)

| ID | Title & Focus | Subsystem | Lane | Status | Target Milestone | Description & Acceptance Gate |
|---|---|---|---|---|---|---|
| **SUB-01** | S0–S12 Monotonic Dispatch Pipeline | `kernel` | Lane A | `DONE` | M-0–M-3C | 13-stage dispatch pipeline, Typed Budget Governor, $\le 1438$ LOC budget. |
| **SUB-02** | Append-Only Event Store & JCS Ledger | `domain` / `runtime` | Lane A | `DONE` | M-5a | RFC 8785 JCS canonicalization, SQLite WAL ledger emitter, `mhf.event/2`. |
| **SUB-03** | Partial-Order Causal Graph & Concurrency | `runtime` | Lane A | `PROPOSED` | M-7+ | Transition physical sequence numbers to causal DAG dependency tracking. |
| **SUB-04** | Subprocess Sandbox PTY ShellPort | `adapters` | Lane A | `APPROVED` | M-9 | Persistent pseudo-terminal inside Bubblewrap with streaming and sub-200ms SIGINT. |

### 2.2 Memory, Learning & Metacognition (VISION.md §14, §18)

| ID | Title & Focus | Subsystem | Lane | Status | Target Milestone | Description & Acceptance Gate |
|---|---|---|---|---|---|---|
| **MEM-01** | Governed Memory & Rollback Mechanisms | `runtime` | Lane A | `REVIEWING` | M-8 | Authorization, recovery, and rollback receipts in `governance/learning.py`. |
| **MEM-02** | M-8 Empirical Held-Out Canary Proof | `benchmarks` | Lane B | `BLOCKED` | M-8 | Held-out real-model canary demonstrating $\ge 0.05$ lift without synthetic metrics. |
| **MEM-03** | Adaptive Strategy & Meta-Controller | `agency` / `runtime` | Lane A | `APPROVED` | M-6.5 | Higher-order policy adjusting strategy upon failure without modifying history. |
| **MEM-04** | Trajectory-to-Skill Promotion Pipeline | `runtime` | Lane A | `PROPOSED` | M-8+ | Mining verified traces to propose reusable skills with explicit promotion receipts. |

### 2.3 Recursive Delegation & Topologies (VISION.md §12, §16)

| ID | Title & Focus | Subsystem | Lane | Status | Target Milestone | Description & Acceptance Gate |
|---|---|---|---|---|---|---|
| **DEL-01** | Monotonic Capability Attenuation | `kernel` / `agency` | Lane A | `DONE` | M-6 | Recursive budget attenuation $\mathcal{A}(B_{\text{parent}}, B_{\text{child}})$ and child spawning. |
| **DEL-02** | Multi-Role Topology Qualification | `runtime` | Lane A | `REVIEWING` | M-7 | Qualify existing topology/child-runtime/artifact-flow mechanisms with three bounded real-effect topologies, durable resume, cancellation, leases/backpressure, fairness, and explicit sequential-versus-parallel disposition. |
| **DEL-03** | Hardware-Aware Swarm Scheduler | `runtime` | Lane A | `DEFERRED` | M-7+ | No implementation until bounded topology qualification proves cost-adjusted lift and a hardware scheduler has a separate preregistered treatment. |

### 2.4 Code Intelligence, Verification & SOTA Tools (VISION.md §5, §8)

| ID | Title & Focus | Subsystem | Lane | Status | Target Milestone | Description & Acceptance Gate |
|---|---|---|---|---|---|---|
| **TLS-01** | AdmissionGate Closed-Loop Validation | `agency` | Lane A | `DONE` | W-092-2 | Fail-closed patch requirement and fresh workspace verification enforcement. |
| **TLS-02** | DeepSeek DSML / JSON Normalization | `agency` | Lane A | `DONE` | W-092-4 | Protocol recovery for malformed markdown tool calls and stream truncations. |
| **TLS-03** | Tree-Sitter / SBFL Fault-Localization Experiment | `ports` / `adapters`| Lane B | `PROPOSED` | M-8+ | Optional `IndexPort` treatment only; admit after localization accuracy and end-to-end solved-task lift beat deterministic search on held-out brownfield tasks. |
| **TLS-04** | AST Syntax Pre-Flight Gate | `adapters` | Lane A | `PROPOSED` | W-092-4 | In-process observation returning precise syntax diagnostics; latency and defect-catch claims require measured receipts and it never substitutes for tests. |
| **TLS-05** | Reconciled Workspace Checkpoints | `adapters` | Lane A | `DEFERRED` | W-092-4 | Prefer explicit preimage/postimage checkpoints and reconciliation; no automatic rollback until external effects, concurrent edits, and resume semantics are falsified. |
| **TLS-06** | AST Mutation Verification (Anti-Collusion)| `adapters` | Lane B | `PROPOSED` | M-8+ | Injects AST mutants to falsify ungrounded or no-op candidate test suites. |
| **TLS-07** | Composable Web Research Port (SSRF-Safe)| `ports` / `adapters`| Lane A | `PROPOSED` | M-9 | Egress-controlled web search and fetch tools with domain allowlists. |

### 2.5 Documentation Plane & Developer Tools

| ID | Title & Focus | Subsystem | Lane | Status | Target Milestone | Description & Acceptance Gate |
|---|---|---|---|---|---|---|
| **DOC-01** | MkDocs + Native Mermaid + Strict Gate | `docs` | Lane A | `DONE` | P0 | `pymdownx.superfences` Mermaid rendering and MkDocs strict build. |
| **DOC-02** | Deterministic Knowledge Base (.jsonl) | `tools` | Lane A | `DONE` | P0 | Machine-generated `catalog`, `code-map`, `symbols`, and `ownership` files. |
| **DOC-03** | Structured RAG V0 (Deterministic) | `tools` | Lane A | `DONE` | P0 | Exact-ID and authority-weighted context query tool (`tools/docs_rag_v0.py`). |
| **DOC-04** | Griffe & mkdocstrings Python API Docs | `docs` / `tools` | Lane A | `APPROVED` | P1 | Auto-generated API documentation for ports and public runtime contracts. |
| **DOC-05** | AST-Grep Structural Repository Indexer | `tools` | Lane B | `PROPOSED` | P1 | Structural AST queries for callers, adapters, and deprecated APIs. |
| **DOC-06** | SCIP Language-Agnostic Symbol Index | `tools` | Lane B | `PROPOSED` | P1 | SCIP indexer generating full cross-language symbol maps for Python & TS. |

### 2.6 Beta Delivery, SWE-Bench & Release Hardening (VISION.md §20)

| ID | Title & Focus | Subsystem | Lane | Status | Target Milestone | Description & Acceptance Gate |
|---|---|---|---|---|---|---|
| **REL-01** | Wave H0: Tooling Integrity & Exact Subject | `benchmarks` | Lane B | `DONE (hermetic)` | M-8 | Runtime/evaluator wiring and explicit empirical missingness pass; this makes no live capability claim. |
| **REL-02** | Wave H1: 10-Task Canary Validation | `benchmarks` | Both | `FROZEN (NOT_RUN)` | M-8 | Content-addressed single-attempt canary is frozen; live thresholds remain unsatisfied until an exact provider/evaluator run is independently accepted. |
| **REL-03** | Wave H2: Official SWE-Bench Container Bridge| `benchmarks` | Lane B | `APPROVED` | M-9 | Isolated official evaluation container passing pure unified diffs. |
| **REL-04** | Wave H3: Preregistered Hypothesis Ablations | `runtime` / `bench` | Both | `PROPOSED` | M-9 | Controlled A/B trials with $\ge 0.05$ lift threshold per treatment. |
| **REL-05** | Wave H4: Release Qualification & Signed Envelope| `ci` / `release` | Both | `BLOCKED` (on M-9) | Full 2348+ test suite, clean out-of-tree install, signed Ed25519 envelope. |

### 2.7 Specialized CLI Product Family (PRD Candidate Proposals)

| ID | Title & Focus | Subsystem | Lane | Status | Target Milestone | Description & Acceptance Gate |
|---|---|---|---|---|---|---|
| **CLI-01** | `vg-code` (Autonomous SWE Problem Solver) | `packs/code-default` | Lane A | `DONE` | M-4 | Autonomous bug fixing: Ingestion $\to$ Reproducer $\to$ Surgical Patch $\to$ Verification. |
| **CLI-02** | `vg-swarm` (Tiered Multi-Model Coding Swarm) | `agency/spawn` | Lane A | `DEFERRED` | M-7+ | Productization is rejected until bounded topology experiments beat the sequential control on cost-adjusted success without reliability regression. |
| **CLI-03** | `vg-fuzz` / `vg-verifier` (Formal CEGIS & SMT Falsifier) | `ports/evaluator` | Lane B | `PROPOSED` | M-5b+ | Formal verification: SMT spec $\to$ CEGIS inductive synthesis $\to$ Concolic fuzzing. |
| **CLI-04** | `vg-refactor` (Causal Slicing & Modernizer) | `ports/index` | Lane A | `PROPOSED` | M-9+ | AST call-graph causal slicing for atomic, regression-free codebase refactoring. |
| **CLI-05** | `vg-review` / `vg-arena` (Adversarial Multi-Model Reviewer)| `agency/spawn` | Lane A | `PROPOSED` | M-7+ | Zero-trust PR review: Competing reviewer personas (Security, Performance, Style) debate. |
| **CLI-06** | `vg-tutor` (Evidence-Graph Codebase Guide) | `packs/tutor` | Lane A | `TECHNICAL SLICE` | 1.0 horizon | Read-only reference composition exists; supported-product status requires install/run/resume and pedagogical completion-policy qualification through the public harness contract. |
| **CLI-07** | `vg-research` (Bounded Technical RFC & Web Corroborator)| `packs/research` | Lane A | `PROPOSED` | M-9 | Egress-controlled technical search $\to$ SSRF-safe fetch $\to$ Triangulated RFC generation. |
| **CLI-08** | `vg-rlvr` (Verifiable Trajectory & Dataset Generator) | `domain/evidence` | Lane B | `PROPOSED` | M-8+ | Mining verified traces (State, Action, Reward, Trace) for RL fine-tuning. |

### 2.8 Formal Reasoning & Algorithmic Engines (LIM Integration Proposals)

| ID | Title & Focus | Subsystem | Lane | Status | Target Milestone | Description & Acceptance Gate |
|---|---|---|---|---|---|---|
| **ALG-01** | SMT-Guided CEGIS Synthesis Loop | `ports/evaluator` | Lane B | `PROPOSED` | M-5b+ | Iterative counterexample synthesis loop: $\Phi(x, y) \to P \in \mathcal{L} \to \text{Z3 SMT Check}$. |
| **ALG-02** | SBFL Multi-Metric Fault Localization Suite | `ports/index` | Lane B | `PROPOSED` | M-8+ | Multi-metric suspiciousness scoring: DStar ($* = 2$), Tarantula, and Ochiai. |
| **ALG-03** | Formal State-Hash Anti-Thrashing FSM | `agency/episode` | Lane A | `ABSORBED` | BEP-03 | Extend the existing protocol-recovery/task-state/no-progress path with semantic attempt fingerprints; do not add a parallel recovery ledger. |

### 2.9 Coding Max Convergence Epic

This epic is the accepted planning disposition of the three Electroweak
solutions. It does not authorize copying executable prototypes from the report
tree. Production changes must be re-derived against current ports, boundaries,
source, and tests.

The architecture rule is **thin app, thick declarative composition**:
`apps/coding_max` owns request/result ergonomics and preset selection;
`packs/code-default` owns coding cognition and policy; runtime remains the only
composition/lifecycle authority; infrastructure stays behind generic ports.

| ID | Capability package | Primary owner | Status | Dependency | Acceptance gate |
|---|---|---|---|---|---|
| **CMX-01** | Current-mechanism delta and three presets | `packs/code-default`, manifests | `DONE (hermetic)` | EWK-Q disposition | `fast`, `balanced`, and `max` are data-selected compositions over one runtime; no duplicate store, coordinator, tool broker, or evaluator |
| **CMX-02** | Port-backed repository intelligence | `ports/index.py`, `adapters`, code-pack bindings | `DONE (hermetic)` | CMX-01 | Search, symbols, dependencies, test mapping, and repository map have provenance, path containment, deterministic fallback, and bounded output; adapters never import `apps` |
| **CMX-03** | Durable plan/context/recovery loop | code-pack policies + existing projections | `DONE (hermetic)` | CMX-01, CMX-02 | A cold-resumed task restores objective, constraints, discoveries, dead ends, modified files, latest verification, remaining budget, and next action without replaying settled effects |
| **CMX-04** | Multi-file and greenfield correctness | code-pack policies and fixtures | `DONE (hermetic)` | CMX-03 | Change-surface closure and affected-test selection pass multi-file fixtures; greenfield work uses an explicit scaffold/baseline/evidence policy and never silently bypasses admission |
| **CMX-05** | Coding Max application facade | `apps/coding_max`, shared application service, `vg` | `DONE (hermetic)` | CMX-03 | CLI and API invoke the same composition; run/status/resume/evidence/cost results agree; app owns no execution loop or provider HTTP |
| **CMX-06** | Conditional review and mediated specialist roles | manifests/topology/child runtime | `IMPLEMENTED (ABLATION PENDING)` | CMX-05 and accepted M-7 evidence | Reviewer/localizer/test-investigator roles exchange artifacts by digest, receive attenuated budgets, run sequentially by default, and cannot override the verifier |
| **CMX-07** | Repository-scale internal qualification proxy | benchmark program | `FROZEN (EXECUTION PENDING)` | CMX-04, CMX-05 | Internal frozen bugfix, multi-file, migration, and greenfield set; not an official SWE-bench result |
| **CMX-08** | First-party reference-agent portfolio | apps + independent packs/manifests | `TECHNICAL SLICE DONE` | M-10 and stable public composition contract | Coding Max plus two non-coding supported agents install, run, resume, and emit attributable evidence through the same public framework contract |

### 2.10 Backend evidence-hardening program

This program absorbs only the production-worthy conclusions of the v0.9.2
backend review. Report-tree prototypes remain dormant design evidence and are
not source owners.

| ID | Capability package | Primary owner | Status | Dependency | Acceptance gate |
|---|---|---|---|---|---|
| **BEP-01** | Subject-bound completion evidence | `agency/episode/admission_gate.py`, `runtime/run_plan.py`, runtime receipt producer | `TECHNICAL COMPLETE / REVIEWING` | Existing W-092-2 admission path | Production write completion supplies and verifies task, composition, workspace postimage, command/test subject, and receipt identities |
| **BEP-02** | Versioned model capabilities and dialect projection | model port + `adapters/models` registry/invocation | `TECHNICAL COMPLETE / REVIEWING` | BEP-01 and frozen control | One canonical intent is projected per provider; capability provenance/version is recorded and unknown models remain conservative |
| **BEP-03** | Unified typed recovery and anti-thrashing | existing protocol recovery + durable coding/task projection | `TECHNICAL COMPLETE / REVIEWING` | BEP-02 observations | Typed failures, bounded semantic retry, zero permission retry, and cold-resume recovery persistence |
| **BEP-04** | Bounded topology qualification | existing topology, child runtime, workflow scheduler, artifacts/events | `TECHNICAL SLICE / ABLATION PENDING` | BEP-03 and accepted M-7 mechanism evidence | Sequential control plus gated reviewer/parallel treatments with durable fairness, leases/backpressure, cancellation/resume and measured lift |
| **BEP-05** | General-agent reference compositions | packs + thin first-party apps | `TECHNICAL SLICE / RELEASE GATED` | BEP-01..04 as applicable, stable public harness contract | Coding Max, Research, and Tutor use one runtime and public contract; domain completion/evaluator vectors remain release-gated |

The aggregate validation campaign for this program stops at the first of
`$0.10` provider spend, `1,000,000` tokens, or `500` model calls. Limits are
cumulative across controls, treatments, retries, mock smoke tests, and live
diagnostics. Unknown usage is not zero and blocks further calls until
reconciled. LAM and easy live tasks validate instrumentation only; capability
claims require the frozen repository-scale and official benchmark programs.

## 2.10 Three-wave SOTA backend completion

The canonical next-up queue is dependency ordered and limited to SOTA-W1:

| Wave | Packages | Outcome |
|---|---|---|
| SOTA-W1 | SOTA-01..04 | Truth reconciliation, completion convergence, official benchmark bridge, frozen qualification |
| SOTA-W2 | SOTA-05..08 | Long-context/multi-file hardening, multi-model economy, measured optimization |
| SOTA-W3 | SOTA-09..12 | Qualified coordination, agent-builder integration, Hermes parity, release qualification |

| ID | Package | Depends on | Outcome |
|---|---|---|---|
| SOTA-01 | Truth reconciliation and activation falsifiers | BEP-01..03 | Real-session evidence and boundary truth |
| SOTA-02 | Completion-aware convergence | SOTA-01 | Redundant green verification converges to requested finish |
| SOTA-03 | Official benchmark protocol bridge | SOTA-01 | Normalized tasks, submissions, receipts, hermetic adapters |
| SOTA-04 | Frozen W1 qualification | SOTA-02, SOTA-03 | CMX-06/07 and FIN-A1 preflight; live missingness remains NOT_RUN |
| SOTA-05 | Long-context identity and retrieval | SOTA-04 | Selection identity, drift checks, bounded sections |
| SOTA-06 | Multi-file patch/resume hardening | SOTA-05 | Stale/partial/ambiguous/escaping patch falsifiers |
| SOTA-07 | Multi-model economy and escalation | SOTA-06 | Existing RouteDecision path with fail-closed pricing/usage |
| SOTA-08 | Frozen internal and Pro pilot campaigns | SOTA-07 | Preregistered attribution and kill criterion |
| SOTA-09 | Qualified coordination scheduler | SOTA-08 | Durable fairness, leases, backpressure, cancellation, joins |
| SOTA-10 | Agent-builder integration | SOTA-09 | Immutable compositions and separated skill promotion authority |
| SOTA-11 | Hermes, Research, and Tutor compositions | SOTA-10 | Same Runtime.compose path and bounded public capabilities |
| SOTA-12 | Matched comparison and release qualification | SOTA-11 | Exact-subject official evidence; M-9/M-10 gates preserved |

`OPEN-2` is `DONE`: observation digests are non-placeholder. Context packets,
role-aware routing, the meta-controller, scheduler, and skill lifecycle are
existing mechanisms, not duplicate implementation targets.

SOTA-01 adds real-session falsifiers, truthful observation digests, canonical
boundary cleanup, and one outbound schema per canonical verb. SOTA-02 makes
admissible completion converge after redundant green verification without
auto-finishing. SOTA-03 supplies normalized official-protocol task, submission,
and receipt contracts over existing runtime/port seams. SOTA-04 is preflight-only
until separate spend authority exists; missing live authority remains `NOT_RUN`.

The existing context packet, role-aware routing, meta-controller, bounded
scheduler, and signed skill lifecycle are mechanisms to integrate and qualify,
not new parallel authorities. Experimental SBFL, mutation, branch search,
swarm, and self-modification remain gated on measured lift.

### Next staged development: 1-forge

The next implementation packet is `FORGE-ADM-001..005` in the non-canonical
review material under `docs/reports/reviews/electroweak_v091/1_forge/`:
define the goal contract, compose it with the existing admission gate, and
make rejection model-visible. ToolScript, forks, mutation, and other later
forge mechanisms remain deferred until their own falsifiers and evidence gates
are authorized.

#### Preset contract

Presets change policy and ceilings, not runtime identity or authority. Numeric
ceilings are calibrated later; their behavioral meanings are locked now.

| Preset | Required behavior | Excluded by default |
|---|---|---|
| `fast` | One primary worker; cheap deterministic discovery; direct inspect/edit/targeted-verify loop; escalate while preserving discoveries and failed attempts | LLM planner, specialist children, branch search, full repository indexing |
| `balanced` | Explicit plan/TODO, progressive context, dependency/test mapping, targeted then affected verification, durable resume, conditional reviewer for declared risk | Swarm/concurrency, mutation, branch search, self-modification |
| `max` | All empirically accepted balanced mechanisms with larger bounded context/turn/model ceilings, broad verification, and optional mediated specialist roles when their gate is accepted | Unbounded compute, automatic authority expansion, mandatory swarm/SBFL/mutation |

Escalation is monotonic in compute but never in capability. The
`fast -> balanced -> max` path may spend a larger pre-authorized budget and add policy components, but it
cannot widen filesystem, network, command, evaluator, or child authority.

#### Task-specific completion policy

| Task class | Minimum completion evidence |
|---|---|
| Existing bug or failing test | Reproducer fails on the baseline when feasible, passes on the postimage, and affected regression checks pass |
| Multi-file feature/refactor/migration | Every implicated interface is inspected; change-surface closure is recorded; targeted and affected checks pass; migration compatibility is tested when applicable |
| Greenfield | Scaffold baseline is recorded; build/syntax succeeds; at least one executable smoke or contract test created for the requested behavior passes on the postimage |
| Repository without tests | The pack declares an explicit acceptance command or creates the smallest executable harness; successful syntax/build alone is insufficient for behavioral completion |
| Analysis/documentation/read-only | A read-only preset applies an explicit requirements checklist; no fabricated patch or test count is required |

Manual review may supplement these policies but cannot replace an applicable
automated check or an exterior evaluator verdict.

#### Explicitly deferred experiments

The following are not Coding Max prerequisites: swarm concurrency, beam/branch
search, ToolScript, SBFL, AST mutation testing, speculative auto-rollback,
trajectory distillation, capsule promotion, and self-modification. Each requires
a separate preregistered control/treatment experiment. It advances only when it
improves task success or cost-adjusted success without exceeding the declared
reliability regression budget.

#### Definition of Ready

A CMX package may enter `active.md` only when its exact source owner, public
contract, negative falsifier, migration impact, measurement subject, and rollback
path are named. A report-tree path or code snippet is never a production owner.

#### Definition of Done

A CMX package is done only when current-source unit and integration tests pass,
the boundary and TCB gates remain green, cold reconstruction is tested when
state changes, canonical docs and generated knowledge are synchronized, and any
capability or performance claim is supported by an exact-subject receipt.

---

## 3. Prioritized Next-Up Queue (Staging for active.md)

The dependency-ordered queue is:

1. **`REL-01` (H0 evidence integrity)** — remove direct provider HTTP and
   synthetic result metrics from the admissible path; use runtime adapters and
   an exterior oracle.
2. **`REL-02` (H1 frozen canary)** — freeze executable, content-addressed,
   single-attempt tasks and explicit missingness before any live run.
3. **`FIN-A1` / `W-092-5` disposition** — independently accept a valid M-8
   bundle or record a negative/undeterminable result without threshold changes.
4. **`CMX-01` through `CMX-05`** — deliver the Coding Max vertical slice in
   dependency order.
5. **`CMX-07`** — qualify the vertical slice before enabling optional
   orchestration.
6. **`CMX-06` and experimental features** — admit one treatment at a time only
   after a preregistered ablation.
7. **`CMX-08`** — qualify the supported first-party agent portfolio on the road
   to 1.0 after M-10.

`TLS-04` may be absorbed into CMX-04 if its measured latency and defect-catch
rate justify the seam. `DOC-04` remains approved but is not on the critical
product path.

---

## 4. Cross-References

* **Vision (Constitutional Law Zero)**: [`VISION.md`](../../VISION.md)
* **Target Milestone Gates**: [`milestones.md`](milestones.md)
* **Active Execution Board (WIP=1)**: [`active.md`](active.md)
* **Normative System Specification**: [`../SPEC.md`](../SPEC.md)
