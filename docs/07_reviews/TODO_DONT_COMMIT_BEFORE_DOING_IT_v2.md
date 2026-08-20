> **CLOSED as investigation.** Forensic discovery is complete
> (`docs/07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md`). Concept Lock is complete (`docs/SPEC.md`,
> ADRs `0069`–`0074`, GAMMA). Remaining engineering work lives in **one** register:
> `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`.
> Do not treat this file as a competing TODO or as authorization to start production coding.

# VANGUARD / AETHER v0.6 — FORENSIC DISCOVERY BEFORE ARCHITECTURE LOCK

## SYSTEM DIRECTIVE

Act as the **Senior/Principal Tech Lead and Project Lead** for the Vanguard / AETHER project.

This phase is strictly **pre-architecture-lock**.

You are NOT authorized in this phase to:
- design a new architecture;
- rewrite the SPEC;
- create a roadmap;
- create milestones;
- create waves;
- create backlog items;
- create sprint plans;
- begin structural refactoring;
- migrate code;
- delete either runtime;
- introduce Rust, distributed infrastructure, WASM, gRPC, or other major technologies;
- silently reconcile conflicting documents.

Your mission is to establish the **ground truth of the project**, identify exactly what is inconsistent or undecided, and then generate the **master prompt for the next phase: Architecture & Concept Lock v0.6**.

---

# 1. OBJECTIVE

Perform a forensic investigation of the repository, documentation, tests, CI, architecture, and existing proposals in order to:

1. establish what the system actually does today;
2. establish what the current normative documents say it should do;
3. separate facts from inference, proposals, stale assumptions, and unknowns;
4. identify architectural drift, duplication, contradictions, and false gates;
5. determine which decisions must be resolved before development resumes;
6. produce a decision-oriented forensic report;
7. only after completing the investigation, generate the exact prompt required for the Architecture & Concept Lock phase.

Do not inherit the framing of any review document automatically.

Do not assume that the newest document is correct.

Do not assume that the existing implementation is correct merely because it exists.

---

# 2. EVIDENCE & AUTHORITY MODEL

Use the following model throughout the investigation.

## 2.1 AS-BUILT TRUTH

Executable code, test execution, CI behavior, runtime behavior, schemas, generated artifacts, and repository history establish:

> **What the system actually does today.**

Primary areas include:

- `vanguard/packages/`
- `layer0/`
- `packs/`
- `test/`
- `vanguard/clients/cli/test/`
- `benchmarkings/`
- `lab/`
- `tools/`
- CI/CD workflows
- schemas and generated types

## 2.2 NORMATIVE AUTHORITY

The current normative documents establish:

> **What the system is currently supposed to do.**

At minimum inspect:

- `docs/SPEC.md`
- normative annexes
- active ADRs
- explicit authority/index documents

Do not allow implementation drift to silently supersede normative architecture.

## 2.3 PROPOSALS, REVIEWS, AND PLANS

Architecture reviews, Tech Lead proposals, Principal/Staff reviews, roadmaps, execution plans, and historical plans are:

> **Non-authoritative inputs until verified and formally adopted.**

They may contain:
- correct findings;
- outdated findings;
- contradictory recommendations;
- future proposals;
- assumptions not supported by current code.

## 2.4 CONFLICT RULE

Whenever:

```text
AS-BUILT != NORMATIVE
````

record the mismatch explicitly.

Do not silently choose either side.

Classify the mismatch as one of:

* implementation drift;
* obsolete normative rule;
* incomplete migration;
* duplicated architecture;
* intentional optimization;
* regression;
* unresolved contradiction;
* unknown.

---

# 3. EVIDENCE LABELS

Every material conclusion MUST be classified as exactly one of:

```text
[FACT]
[INFERENCE]
[PROPOSAL]
[UNKNOWN]
```

Definitions:

### `[FACT]`

Directly supported by:

* executable code;
* test execution;
* CI configuration;
* version-control history;
* normative source;
* reproducible command output.

### `[INFERENCE]`

A reasoned conclusion derived from facts, but not directly proven.

### `[PROPOSAL]`

A recommendation or candidate decision that has not yet been adopted.

### `[UNKNOWN]`

Insufficient evidence. Requires additional investigation, experiment, or human decision.

Never present an inference as fact.

---

# 4. PHASE 0 — PRE-ARCHITECTURE FREEZE

During this task:

```text
NO NEW ARCHITECTURE
NO STRUCTURAL REFACTOR
NO ROADMAP
NO BACKLOG
NO SPRINT
NO CODE MIGRATION
```

Minor exploratory commands, local experiments, test execution, repository comparison, and disposable technical spikes are permitted only when required to establish evidence.

Do not commit architectural changes.

---

# 5. PHASE 1 — REPOSITORY FORENSIC INVESTIGATION

Inspect the repository in depth.

At minimum map:

```text
vanguard/packages/
layer0/
packs/
test/
vanguard/clients/cli/test/
benchmarkings/
lab/
tools/
schemas/
.github/
docs/
```

Investigate the real implementation state of:

* event model;
* canonicalization;
* kernel;
* effect dispatch;
* authorization;
* capability attenuation;
* budgets;
* leases;
* scheduler;
* episode lifecycle;
* ledger;
* reducers;
* snapshots;
* CAS/blob storage;
* inbox/outbox;
* evaluator;
* verdict signing;
* plugin registry;
* plugin lifecycle;
* plugin execution;
* SPI/contracts;
* sandboxing;
* model providers;
* context management;
* memory;
* toolkits;
* selectors;
* CLI;
* orchestrator;
* harness composition;
* packs;
* telemetry;
* experiment infrastructure;
* any existing project or multi-agent implementation.

For each subsystem determine:

```text
EXISTS
PARTIAL
MOCK
DUPLICATED
DEAD
UNTESTED
TESTED
CI-GATED
NOT CI-GATED
```

---

# 6. TEST & CI REALITY

Execute the relevant test suites rather than trusting documentation.

Determine:

* which tests pass;
* which tests fail;
* which tests are skipped;
* which directories are ignored;
* which tests CI actually runs;
* which runtime CI actually protects;
* whether important production code is outside CI;
* whether gates verify behavior or merely structure/text.

Record:

* command;
* exit code;
* relevant output;
* affected subsystem.

Example evidence format:

```text
[FACT]
Command:
pytest ...

Result:
...

Implication:
...
```

---

# 7. PHASE 2 — `vanguard/packages/` VS `layer0/` FORENSICS

Investigate the relationship between:

```text
vanguard/packages/
layer0/
```

Do NOT decide the migration strategy yet.

Determine:

1. historical origin of both trees;
2. whether one originated from copying/forking the other;
3. commit divergence where discoverable;
4. approximate functional overlap;
5. 1:1 module equivalents;
6. implementations unique to each side;
7. test coverage unique to each side;
8. defects duplicated across both sides;
9. behavior that diverged after the fork;
10. contracts/types that diverged;
11. features one plan intends to rebuild that already exist elsewhere.

Explicitly compare:

* selectors;
* canonicalization;
* effect requests;
* kernel;
* provenance;
* grants;
* budget;
* ledger;
* SQLite/WAL;
* reducers;
* recovery;
* inbox/outbox;
* evaluator;
* signatures;
* sandbox;
* plugin runtime;
* scheduler;
* model interfaces;
* composition/root;
* coding-specific code.

Produce a module equivalence matrix.

Example:

| Concern | `vanguard/packages/` | `layer0/` | Relationship | Evidence | Maturity |
| ------- | -------------------- | --------- | ------------ | -------- | -------- |

Do not assume any of the following before evidence exists:

```text
DELETE layer0
DELETE packages
REBUILD layer0
PORT packages into layer0
KEEP packages
CONVERGE both
REWRITE IN RUST
```

---

# 8. PHASE 3 — DOCUMENTARY AUTHORITY AUDIT

Catalogue the relevant documentation.

Classify every relevant document into:

```text
[NORMATIVE]
[CURRENT DECISION]
[PROPOSAL]
[REVIEW]
[HISTORICAL]
[SUPERSEDED]
[UNKNOWN]
```

Inspect at minimum:

```text
docs/SPEC.md
docs/01_executive/
docs/02_roadmap/
docs/03_sprints/
docs/04_annex/
docs/05_adr/
docs/06_references/
docs/07_reviews/
schemas/
```

Pay special attention to:

```text
docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/
```

including, where present:

```text
principal_engineer_proposal.md
tech_lead_proposal.md
vanguard-arquitetura-v4-parecer-e-plano.md
Vanguard-substrate-060-full-refactor-v3-1.md
vanguard-substrate-060-execution-plan.md
aether-v1-roadmap-waves.md
```

The descriptions of these documents are navigation hints only.

Do not infer authority from filename, directory placement, recency, or author seniority.

Explicitly identify contradictions such as:

```text
Document A says X
Document B says Y
Current code does Z
Current SPEC says W
```

---

# 9. PHASE 4 — SPEC × ADR × CODE × TESTS × PROPOSALS MATRIX

For every major architectural area, produce:

| Concept / Area | Current SPEC | Active ADRs | As-Built Code | Tests / Evidence | Tech Lead Proposal | Architecture Reviews | Conflict / Gap | Required Decision |
| -------------- | ------------ | ----------- | ------------- | ---------------- | ------------------ | -------------------- | -------------- | ----------------- |

At minimum include:

* runtime target;
* microkernel boundary;
* events;
* ledger;
* authority;
* scheduler;
* plugins;
* SPI;
* evaluator;
* storage;
* harness identity;
* execution identity;
* project identity;
* multi-agent;
* concurrency;
* replay;
* cache/projections;
* memory;
* orchestration;
* Meta-Harness;
* experimentation;
* distribution;
* Rust.

---

# 10. PHASE 5 — CONCEPT & PRIMITIVE INVENTORY

Investigate how the system currently defines or intends to define:

```text
Event
EffectRequest
Receipt
Artifact
ArtifactRef
Principal
Agent
Harness
FrozenHarness
HarnessInstance
Episode
Project
Task
Plugin
Skill
Memory
Context
Tool
Toolkit
Model
Evaluator
Ledger
CAS
Cache
Projection
Scheduler
Orchestrator
Lease
Reservation
Budget
Capability
Spawn
ChildPrincipal
Trajectory
Experiment
Promotion
Meta-Harness
```

For each classify:

```text
CANONICAL
DUPLICATED
PARTIAL
DOCUMENTED-ONLY
IMPLEMENTED-ONLY
AMBIGUOUS
MISSING
```

Identify:

* duplicated concepts;
* overloaded names;
* premature abstractions;
* concepts represented differently in the two runtimes;
* unnecessary new concepts;
* missing primitives likely to cause structural rework later.

Rule:

> Do not create a new concept when an existing concept can be corrected, generalized, composed, or removed.

---

# 11. PHASE 6A — MULTI-AGENT & RECURSIVE AGENCY INVESTIGATION

Investigate, without adopting it prematurely, the architectural thesis:

```text
Agent = Principal + HarnessInstance

SubAgent = ChildPrincipal + HarnessInstance
```

Evaluate whether:

```text
Agent
SubAgent
MetaAgent
Swarm Participant
```

can plausibly share one execution abstraction rather than require separate engines.

Investigate support for:

```text
spawn(
    parent,
    harness,
    capabilities,
    budget
)
```

and the candidate invariants:

```text
Capabilities(child) ⊆ Capabilities(parent)

Budget(child) <= RemainingBudget(parent)
```

Determine whether the current system already contains relevant machinery.

Investigate which semantics may need to exist early to prevent future structural migration:

```text
project_id
principal_id
parent_principal_id
episode_id
parent_episode_id
harness_digest
causation_id
correlation_id
ownership
budget lineage
capability lineage
evaluation identity
```

Do NOT implement multi-agent.

Classify each semantic requirement as:

```text
NEEDED FOR CONCEPT LOCK
NEEDED IN EARLY IMPLEMENTATION
CAN BE DEFERRED
RESEARCH ONLY
```

---

# 12. PHASE 6B — EXECUTION GRAPH & CAUSALITY

Investigate whether execution relationships should be represented as:

```text
A. Core graph primitive
B. Static workflow / DAG
C. Dynamic planner state
D. Projection derived from events
E. Hybrid
```

Examine relations including:

```text
spawned_by
caused_by
depends_on
produced
consumed
evaluated_by
derived_from
invalidated_by
```

Determine whether a graph naturally emerges from event causality.

Do not assume a graph database is required.

Do not assume task dependencies require a workflow engine.

Identify the minimum causal semantics needed now.

---

# 13. PHASE 6C — EVENT SOURCING & STATE

Investigate the real and intended roles of:

```text
Ledger
CAS
Snapshots
Reducers
Projections
Cache
Indexes
Memory
Telemetry
Inbox/Outbox
```

Evaluate the intended invariant:

```text
State = fold(Events)
```

and whether derived systems should follow a model such as:

```text
Projection = f(Ledger)
Cache = g(Ledger, CAS)
```

Investigate:

* append durability;
* blob durability ordering;
* snapshots;
* replay;
* recovery;
* branching;
* causation;
* correlation;
* ordering;
* project-local ordering;
* global ordering assumptions;
* effect reconciliation.

Explicitly distinguish:

```text
STATE REPLAY
SCHEDULE REPLAY
REAL-WORLD RE-EXECUTION
BYTE-DETERMINISTIC FIXTURE
```

Do not treat them as equivalent.

---

# 14. PHASE 6D — PLUGIN-FIRST ARCHITECTURE

Investigate which capabilities can naturally be modular/substitutable:

```text
planner
memory
context
compression
cache strategy
indexing
AST processing
heuristics
tools
scripts
model routing
skills
reflection
evaluation gates
self-improvement strategies
Meta-Harness strategies
```

Also identify what likely belongs below the plugin boundary because it governs authority or fundamental mechanism:

```text
identity
authority
effect mediation
event semantics
resource conservation
plugin lifecycle
core scheduling mechanism
```

Do not automatically classify everything as a plugin.

Do not automatically classify every in-process component as core.

---

# 15. PHASE 6E — PLUGIN BOUNDARY & POLYGLOT PROTOCOL

Investigate existing and proposed plugin interfaces.

Compare:

```text
Python typing.Protocol
in-process calls
subprocess
JSON-RPC
UDS
framed JSON
JSON Schema
JCS
generated bindings
Protobuf
gRPC
container
WASM
```

Determine:

* what exists today;
* what is tested;
* what is only proposed;
* which choices are required for v0.6;
* which are implementation details that can remain replaceable.

Evaluate both:

```text
semantic boundary
```

and:

```text
physical isolation boundary
```

Do not assume they must be identical.

---

# 16. PHASE 6F — RESOURCE EFFICIENCY & CONCURRENCY

Investigate how future multi-agent execution could scale without assuming:

```text
N logical agents = N heavyweight processes
```

Analyze the distinction between:

```text
Logical Agent
Execution Worker
```

and the candidate scaling property:

```text
K active workers << N logical agents
```

Investigate:

* shared immutable harnesses;
* model runtime sharing;
* worker pools;
* copy-on-write workspaces;
* CAS reuse;
* context references;
* bounded concurrency;
* sparse agent activation;
* hierarchical budgets;
* scheduling overhead.

Do not claim multi-agent is more resource-efficient by definition.

Identify where swarm execution can be substantially more expensive than single-agent execution.

---

# 17. PHASE 6G — META-HARNESS & SELF-IMPROVEMENT READINESS

Investigate the candidate lifecycle:

```text
Harness H0
→ Execution
→ Trajectory
→ Candidate Mutation
→ Harness H1
→ Controlled Experiment
→ External Evaluation
→ Promotion / Rejection
```

Determine whether existing primitives can support this without introducing a second execution engine.

Analyze separately:

```text
Runtime Adaptation
Memory Adaptation
Composition Adaptation
Plugin Synthesis
Model Adaptation
Core Modification
```

Determine what must be structurally anticipated now versus explicitly deferred.

Do not design a self-updating release pipeline.

---

# 18. PHASE 6H — AUTHORITY & SECURITY SEMANTICS

Investigate the minimum structural semantics required early for:

```text
Principal identity
Capabilities
Attenuation
Leases
Reservations
Budgets
Effect mediation
Exterior evaluation
Plugin trust
Cancellation
Revocation
Provenance
Artifact ownership
```

Separate conclusions into:

```text
SECURITY SEMANTICS REQUIRED NOW
```

and:

```text
SECURITY HARDENING THAT CAN COME LATER
```

Examples of hardening that MUST NOT automatically become immediate blockers:

```text
WASM
remote attestation
distributed trust
multi-host isolation
complex supply-chain infrastructure
hardware security
```

---

# 19. PHASE 6I — GATE & GOODHART AUDIT

Audit existing architectural and CI gates.

For every gate ask:

> What is the laziest incorrect implementation that could pass this gate?

Investigate:

* lexical gates used as behavioral proof;
* synthetic evaluator paths;
* declared-but-unemitted events;
* test-count proxies;
* coverage proxies;
* mutation-score proxies;
* impossible determinism requirements;
* arbitrary benchmark sample counts;
* CI targeting the wrong runtime;
* false-positive conformance.

Classify each gate:

```text
VALID BEHAVIORAL PROOF
VALID STRUCTURAL PROOF
WEAK PROXY
FALSE CONFIDENCE
UNKNOWN
```

---

# 20. PHASE 7 — DECISION REGISTRY

After completing the investigation, classify every unresolved decision.

## P0 — MUST BE RESOLVED DURING ARCHITECTURE / CONCEPT LOCK AND BEFORE DEVELOPMENT RESUMES

Fundamental decisions whose ambiguity would cause structural rework or incompatible implementation.

## P1 — MUST BE CONSIDERED DURING EARLY WAVES

Important decisions that may remain partially open if the architecture explicitly preserves their future evolution.

The next phase must explicitly determine:

```text
LOCK NOW
or
DEFER DELIBERATELY
```

for each P1.

## P2 — CAN BE DEFERRED

Decisions that can safely remain unresolved without breaking the initial contracts.

## P3 — RESEARCH / FUTURE

Long-horizon hypotheses and advanced mechanisms.

## UNKNOWN / NEEDS EXPERIMENT

Questions that cannot responsibly be decided from present evidence.

For each decision record:

```text
ID
Question
Why It Matters
Evidence
Current Alternatives
Required By
Risk of Wrong Early Decision
Classification
```

---

# 21. DELIVERABLE 1

Create:

```text
VANGUARD_V060_FORENSIC_DISCOVERY.md
```

Required structure:

```text
1. Executive Summary
2. Investigation Method
3. Repository As-Built
4. Test & CI Reality
5. Documentation Authority Map
6. `vanguard/packages/` vs `layer0/` Forensics
7. SPEC × ADR × Code × Tests × Proposals Matrix
8. Concept & Primitive Inventory
9. Multi-Agent & Recursive Agency Readiness
10. Execution Graph & Causality Analysis
11. Ledger / Event-Sourcing Analysis
12. Plugin Architecture Analysis
13. Plugin Boundary / Polyglot Analysis
14. Resource & Concurrency Analysis
15. Authority & Security Boundary Analysis
16. Meta-Harness / Self-Improvement Readiness
17. Gate & Goodhart Audit
18. Critical Technical Debt
19. P0 Decision Registry
20. P1 Decision Registry
21. P2 Deferred Decisions
22. P3 Research Topics
23. Unknowns / Required Experiments
24. Recommended Decision Sequence
25. Final Forensic Conclusions
```

Every important conclusion MUST carry one of:

```text
[FACT]
[INFERENCE]
[PROPOSAL]
[UNKNOWN]
```

Use evidence anchors whenever possible:

```text
file:line
command
test output
commit/history evidence
normative citation
```

---

# 22. DELIVERABLE 2 — NEXT-PHASE MASTER PROMPT

ONLY AFTER completing `VANGUARD_V060_FORENSIC_DISCOVERY.md`, create:

```text
PROMPT_ARCHITECTURE_CONCEPT_LOCK_V060.md
```

This must be a project-specific, evidence-derived execution prompt.

Do NOT use a generic architecture template.

The prompt must instruct the next Tech Lead / Project Lead phase to:

1. resolve every P0 decision;
2. determine explicitly which P1 decisions must be locked now and which are deliberately deferred;
3. consolidate the canonical domain and execution concepts;
4. eliminate architectural contradictions;
5. establish the canonical runtime/migration strategy;
6. establish authority boundaries;
7. establish multi-agent semantics required for future evolution;
8. establish plugin boundaries;
9. establish state/event semantics;
10. create or update the required ADRs;
11. update the normative SPEC to v0.6;
12. define the final Concept Lock exit gate.

The next-phase prompt MUST NOT yet ask for:

```text
roadmap
milestones
waves
backlog
sprints
production implementation
```

Those come only after the Concept Lock and normative documentation are complete.

---

# 23. REQUIRED GLOBAL SEQUENCE

The project must intentionally follow:

```text
FORENSIC DISCOVERY
        ↓
ARCHITECTURE / CONCEPT LOCK
        ↓
ADR + SPEC v0.6
        ↓
AS-BUILT GAP / MIGRATION CLASSIFICATION
        ↓
ROADMAP + MILESTONES
        ↓
EXECUTION PLAN + WAVES
        ↓
BACKLOG
        ↓
SPRINTS
        ↓
CODE
```

Do not skip stages.

Do not allow stages to become infinite research programs.

The purpose of this process is to restore a single coherent engineering authority and unblock development on the correct v0.6 architecture.

---

# 24. NAVIGATION MAP

The following paths are provided only to guarantee investigation coverage.

Their descriptions are contextual hints and MUST NOT determine authority, correctness, or precedence.

## Principal Staff Engineer Reviews

```text
docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/
```

Potentially relevant files include:

```text
principal_engineer_proposal.md
tech_lead_proposal.md
vanguard-arquitetura-v4-parecer-e-plano.md
Vanguard-substrate-060-full-refactor-v3-1.md
vanguard-substrate-060-execution-plan.md
aether-v1-roadmap-waves.md
```

## Normative / Architectural Documentation

```text
docs/SPEC.md
docs/04_annex/
docs/05_adr/
```

## Planning Documentation

```text
docs/01_executive/
docs/02_roadmap/
docs/03_sprints/
```

## Research / References

```text
docs/06_references/
```

## Reviews / Historical Material

```text
docs/07_reviews/
```

The investigator MUST independently classify the authority and validity of every document.

---

# 25. GOLDEN RULE

Do not guess.

Do not reconcile conflicting documents through rhetorical compromise.

Do not treat implementation drift as silent architecture.

Do not treat review seniority as authority.

Do not invent new concepts merely to reconcile old ones.

Establish:

```text
AS-BUILT TRUTH
```

from executable code, tests, CI, repository history, and observed behavior.

Establish:

```text
NORMATIVE INTENT
```

from the SPEC and active ADRs.

Treat:

```text
REVIEWS
PROPOSALS
ROADMAPS
PLANS
```

as non-authoritative inputs until verified and formally adopted.

Record every material conclusion as:

```text
[FACT]
[INFERENCE]
[PROPOSAL]
[UNKNOWN]
```

The question of this phase is NOT:

> Which architecture sounds best?

The question is:

> What actually exists, what is actually normative, where do they conflict, what remains genuinely unknown, and exactly which decisions must be made before development can safely resume?

---

# 🎯 CRITICAL INVESTIGATION FOCUS: `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/`
> This directory contains the conceptual proposals, architectural evaluations, hybrid verdicts, and review frameworks under investigation:

* `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/principal_engineer_proposal.md`  
  *`[PROPOSAL]` Architectural proposal covering authority separation (§4), single recursive machine (`Agent = Principal + HarnessInstance`), identity levels ($D_H/D_R/D_X$), and scaling invariants.*
* `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/vanguard-arquitetura-v4-parecer-e-plano.md`  
  *`[REVIEW / PROPOSAL]` Architecture review v4: empirical diagnosis, code evidence, canonical core convergence (`vanguard/packages/`), and Phase -1 CI truth.*
* `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/Vanguard-substrate-060-full-refactor-v3-1.md`  
  *`[PROPOSAL]` Detailed Substrate 0.6.0 full refactor proposal v3.1.*
* `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/vanguard-substrate-060-execution-plan.md`  
  *`[PROPOSAL]` Substrate 0.6.0 execution plan proposal.*
* `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-v1-roadmap-waves.md`  
  *`[PROPOSAL]` High-level Aether v1 wave roadmap proposal.*

---

### 📂 Repository Documentation Structure Map

#### 1. Normative Root
* `docs/SPEC.md` *(Current living normative specification)*

#### 2. `docs/07_reviews/` (Audits, Reviews & Historical Proposals)
* `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/` *(The 5 proposal & review documents above)*
* `docs/07_reviews/TODO_DONT_COMMIT_BEFORE_DOING_IT.md` *(Commit/merge restriction directives)*
* `docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/` *(Archived previous reviews)*

#### 3. `docs/06_references/` (Research & Theoretical Synthesis)
* `docs/06_references/WAVE_6_SOTA_RESEARCH_AND_THEORETICAL_SYNTHESIS.md`
* `docs/06_references/WAVE_6_SOTA_RESEARCH_AND_THEORETICAL_SYNTHESIS_B.md`
* `docs/06_references/research_Harness_Builder_Framework.md`
* `docs/06_references/deepseek-harness_algorithms-ideas.md`
* `docs/06_references/vanguard_body_detailed.md`
* `docs/06_references/guidelines.md`

#### 4. `docs/05_adr/` (Architectural Decision Records)
* `docs/05_adr/INDEX.md` *(ADR registry and status)*
* `docs/05_adr/DRIFT_REGISTER_v045.md` *(Architectural drift register)*
* `docs/05_adr/DEFERRED_REJECTED.md` *(Deferred / rejected decisions)*
* `docs/05_adr/0000-*.md` through `docs/05_adr/0068-*.md` and `docs/05_adr/ADR-M0-*.md` *(84 total ADR files)*

#### 5. `docs/04_annex/` (Normative Annexes)
* `docs/04_annex/KERNEL.md` *(Low-level normative kernel specification)*
* `docs/04_annex/MEASUREMENT.md` *(Measurement, gates, and verification criteria)*

#### 6. `docs/01_executive/`, `docs/02_roadmap/`, and `docs/03_sprints/`
* `docs/01_executive/vision.md` *(Product & business vision)*
* `docs/02_roadmap/milestones.md` *(Legacy roadmap milestones)*
* `docs/02_roadmap/backlog.md` *(Legacy backlog pending reconciliation)*
* `docs/03_sprints/sprint_active.md` *(Active/historical sprint board)*
* `docs/03_sprints/plans/` *(Historical sprint plans)*

---

# EXECUTION BEGINS NOW