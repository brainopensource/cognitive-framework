````markdown
# VANGUARD / AETHER v0.6 — INDEPENDENT TECH LEAD CONCEPT LOCK PLAN REVIEW

## SYSTEM DIRECTIVE

Act as the **Senior/Principal Tech Lead and Project Lead** for Vanguard / AETHER.

This engagement is **ANALYSIS-ONLY**.

There are currently **two parallel versions of the same project being evaluated by different teams using different architectural approaches**.

Your purpose is to produce an **independent Tech Lead assessment** that can later be compared against the Principal Staff Engineer team's proposal.

You MUST NOT modify the project.

You MUST produce exactly **ONE report**:

`docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/tech_lead_concept_lock_plan_suggestion.md`

---

# 1. STRICT NON-MODIFICATION RULE

During this task:

```text
DO NOT EDIT CODE
DO NOT REFACTOR CODE
DO NOT MIGRATE CODE
DO NOT DELETE CODE
DO NOT UPDATE SPEC
DO NOT UPDATE ADRs
DO NOT UPDATE ANNEXES
DO NOT UPDATE ROADMAP
DO NOT UPDATE MILESTONES
DO NOT UPDATE BACKLOG
DO NOT UPDATE SPRINTS
DO NOT UPDATE EXISTING REVIEWS
DO NOT CREATE IMPLEMENTATION TASKS
DO NOT COMMIT CHANGES
````

The only repository artifact you may create is:

```text
docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/tech_lead_concept_lock_plan_suggestion.md
```

You are evaluating **what should eventually change**, not changing it now.

---

# 2. MISSION

Investigate the repository, documentation, tests, CI, architecture, historical decisions, and current proposals.

Then answer:

> If you were independently responsible for the Vanguard / AETHER v0.6 Architecture & Concept Lock, what would you preserve, change, remove, generalize, defer, or reconsider — and why?

Your report must provide an independent proposed direction that can later be compared with the Principal Staff Engineer team's plan.

Do not merely summarize existing reviews.

Do not automatically agree with the newest proposal.

Do not intentionally disagree for the sake of differentiation.

Reach your conclusions from evidence.

---

# 3. EVIDENCE & AUTHORITY MODEL

Maintain a strict distinction between:

## AS-BUILT TRUTH

Executable code, tests, CI, repository history, runtime behavior, schemas, and generated artifacts establish:

> What the system actually does today.

Inspect at minimum:

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
```

## NORMATIVE INTENT

Inspect:

```text
docs/SPEC.md
docs/04_annex/
docs/05_adr/
```

These describe what the current architecture is supposed to mean.

Implementation drift does not silently override normative intent.

## PROPOSALS / REVIEWS / PLANS

Treat these as evidence and candidate architectural directions, not automatic authority:

```text
docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/
docs/06_references/
docs/02_roadmap/
docs/03_sprints/
```

---

# 4. INDEPENDENCE REQUIREMENT

This report exists specifically so two teams can produce independently reasoned approaches.

Therefore:

* Read the Principal Staff Engineer material.
* Understand its reasoning.
* Extract useful evidence, standards, patterns, constraints, and architectural ideas.
* Do NOT treat it as the answer.
* Do NOT optimize your conclusions merely to match it.
* Do NOT deliberately construct an opposing plan.

Your conclusions must represent:

> **What this Tech Lead team would recommend after independently examining the same system.**

The later comparison between both proposals will determine the final combined Architecture & Concept Lock.

---

# 5. EVIDENCE LABELS

Classify significant conclusions as:

```text
[FACT]
[INFERENCE]
[RECOMMENDATION]
[UNKNOWN]
```

### [FACT]

Directly supported by code, tests, CI, repository history, normative documentation, or reproducible evidence.

### [INFERENCE]

Reasoned conclusion from facts that is not directly proven.

### [RECOMMENDATION]

What this Tech Lead team believes should be adopted during Concept Lock.

### [UNKNOWN]

Evidence is insufficient and the issue should remain unresolved or require an experiment/spike.

---

# 6. REPOSITORY FORENSIC REVIEW

Investigate the real implementation state of:

* event model;
* canonicalization;
* kernel;
* effect dispatch;
* authorization;
* capabilities;
* attenuation;
* budgets;
* reservations;
* leases;
* scheduler;
* episode lifecycle;
* ledger;
* SQLite/WAL;
* reducers;
* snapshots;
* CAS/blob storage;
* inbox/outbox;
* recovery;
* evaluator;
* verdict signing;
* plugin registry;
* plugin lifecycle;
* plugin execution;
* SPI/contracts;
* sandbox;
* model providers;
* context;
* memory;
* toolkits;
* selectors;
* CLI;
* composition/root;
* orchestrator;
* packs;
* telemetry;
* experiments;
* project abstractions;
* multi-agent abstractions.

Determine what is:

```text
MATURE
PARTIAL
DUPLICATED
MOCK
DEAD
DOCUMENTED-ONLY
IMPLEMENTED-ONLY
TESTED
UNTESTED
CI-GATED
NOT CI-GATED
```

Do not change any implementation.

---

# 7. `vanguard/packages/` VS `layer0/`

Perform an independent forensic comparison between:

```text
vanguard/packages/
layer0/
```

Investigate:

* historical relationship;
* duplication;
* divergence;
* module equivalence;
* maturity;
* tests;
* features unique to each side;
* missing functionality;
* conflicting contracts;
* duplicated fixes;
* duplicated bugs;
* current CI protection.

Evaluate alternatives such as:

```text
KEEP PACKAGES AS CANONICAL
KEEP LAYER0 AS CANONICAL
PORT SELECTIVELY
CONVERGE
REBUILD
RESTRUCTURE BOTH
OTHER
```

Do NOT execute any choice.

Instead document which direction you would recommend for Concept Lock and why.

---

# 8. DOCUMENTATION FORENSICS

Review the current documentation structure:

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

Identify:

* normative documents;
* current decisions;
* obsolete decisions;
* proposals;
* historical documents;
* duplicate concepts;
* contradictions;
* documents that should eventually be updated;
* documents that should eventually be archived;
* documents that should eventually be merged;
* documents whose status is unclear.

Do NOT perform those changes.

Only recommend them in the report.

---

# 9. REVIEW THE PRINCIPAL STAFF ENGINEER MATERIAL

Read carefully:

```text
docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/principal_engineer_proposal.md

docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/vanguard-arquitetura-v4-parecer-e-plano.md

docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/Vanguard-substrate-060-full-refactor-v3-1.md

docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/vanguard-substrate-060-execution-plan.md

docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-v1-roadmap-waves.md
```

For each relevant idea classify it as:

```text
AGREE
AGREE WITH MODIFICATION
DISAGREE
DEFER
INSUFFICIENT EVIDENCE
```

Explain why.

Focus especially on extracting:

* useful engineering standards;
* architecture invariants;
* implementation patterns;
* migration lessons;
* quality gates;
* security constraints;
* naming/identity models;
* resource models;
* event semantics;
* plugin semantics;
* multi-agent semantics;
* experimental methodology.

---

# 10. CONCEPT LOCK REVIEW

Independently evaluate the concepts that should eventually become canonical for v0.6:

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

For each concept determine:

```text
KEEP AS-IS
REFINE
GENERALIZE
MERGE
REMOVE
DEFER
UNRESOLVED
```

Do NOT modify the actual definitions.

State what the future Concept Lock should do.

---

# 11. MULTI-AGENT & RECURSIVE AGENCY REVIEW

Independently evaluate the proposal:

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

should share one recursive execution abstraction.

Review the candidate operation:

```text
spawn(
    parent,
    harness,
    capabilities,
    budget
)
```

and candidate invariants:

```text
Capabilities(child) ⊆ Capabilities(parent)

Budget(child) <= RemainingBudget(parent)
```

Determine which semantics should be locked early to avoid future structural migration:

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

Also evaluate:

* logical agents vs execution workers;
* bounded workers;
* recursive delegation;
* heterogeneous harnesses;
* swarm policies;
* concurrency timing;
* shared resources.

Do NOT implement multi-agent.

Report what you believe Concept Lock should preserve now versus defer.

---

# 12. EVENT SOURCING, LEDGER, GRAPH, CAS, CACHE

Evaluate the architectural relationship between:

```text
Ledger
CAS
Reducers
Snapshots
Projections
Cache
Indexes
Memory
Telemetry
Execution Graph
```

Review the candidate principle:

```text
State = fold(Events)
```

and whether:

```text
Projection = f(Ledger)

Cache = g(Ledger, CAS)
```

is appropriate.

Evaluate whether execution graphs should be:

```text
CORE PRIMITIVE
STATIC WORKFLOW
DYNAMIC PLANNER STATE
EVENT-DERIVED PROJECTION
HYBRID
```

Review causal relationships including:

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

Do NOT create graph infrastructure.

Recommend what Concept Lock should establish.

---

# 13. PLUGIN ARCHITECTURE REVIEW

Evaluate the plugin-first direction independently.

Determine which capabilities should likely remain replaceable:

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
skills
model routing
reflection
evaluation gates
self-improvement strategies
Meta-Harness strategies
```

Determine what likely belongs below that boundary:

```text
identity
authority
effect mediation
event semantics
resource conservation
plugin lifecycle
core scheduling mechanism
```

Review:

```text
Python Protocol
in-process
subprocess
JSON-RPC
UDS
JSON Schema
JCS
generated bindings
Protobuf
gRPC
container
WASM
```

Recommend:

* semantic plugin boundary;
* physical isolation boundary;
* language strategy;
* Python-first vs alternatives;
* conditions that would justify Rust or other technologies later.

Do NOT implement any protocol.

---

# 14. AUTHORITY & SECURITY REVIEW

Evaluate the architecture of:

```text
Principal identity
Capabilities
Attenuation
Leases
Budgets
Effect mediation
Evaluator exteriority
Plugin trust
Cancellation
Revocation
Provenance
Artifact ownership
```

Separate recommendations into:

```text
SEMANTICS TO LOCK NOW
```

and:

```text
HARDENING TO DEFER
```

Do not turn future hardening into immediate architecture unless required.

---

# 15. RESOURCE & CONCURRENCY REVIEW

Evaluate the proposed distinction:

```text
Logical Agent != Execution Worker
```

and candidate scale model:

```text
K active workers << N logical agents
```

Review:

* worker pools;
* shared model runtime;
* immutable harness sharing;
* CAS reuse;
* copy-on-write workspaces;
* sparse agent activation;
* hierarchical budgets;
* bounded concurrency.

Determine what must be represented in v0.6 semantics even if execution initially remains sequential.

---

# 16. META-HARNESS & SELF-IMPROVEMENT REVIEW

Evaluate the proposed lifecycle:

```text
H0
→ Execution
→ Trajectory
→ Candidate
→ H1
→ Experiment
→ Exterior Evaluation
→ Promotion / Rejection
```

Review separately:

```text
runtime adaptation
memory adaptation
composition adaptation
plugin synthesis
model adaptation
core modification
```

Determine what should be anticipated architecturally now and what should remain explicitly future work.

Do not implement or design an autonomous release pipeline.

---

# 17. CI / GATE REVIEW

Review existing and proposed gates.

For each important gate ask:

> What is the laziest incorrect implementation that could still pass?

Classify gates as:

```text
STRONG BEHAVIORAL PROOF
VALID STRUCTURAL PROOF
WEAK PROXY
FALSE CONFIDENCE
UNKNOWN
```

Recommend what should eventually change.

Do NOT change CI.

---

# 18. DECISION CLASSIFICATION

Classify proposed Concept Lock decisions as:

## P0 — LOCK BEFORE DEVELOPMENT

Structural decisions likely to cause major rework if postponed.

## P1 — LOCK OR EXPLICITLY DEFER

Important architectural decisions where the lock must state either:

```text
LOCK NOW
```

or:

```text
DEFER DELIBERATELY
```

## P2 — SAFE TO DEFER

Implementation choices that should not block v0.6 architecture.

## P3 — RESEARCH / FUTURE

Advanced capabilities and hypotheses.

## UNKNOWN / NEEDS EXPERIMENT

Decisions where evidence is currently inadequate.

---

# 19. REQUIRED SINGLE DELIVERABLE

Create ONLY:

```text
docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/tech_lead_concept_lock_plan_suggestion.md
```

The report must contain:

```text
1. Executive Summary
2. Scope and Independence Statement
3. Evidence & Investigation Method
4. Repository As-Built Findings
5. Test & CI Findings
6. Documentation Authority Findings
7. `vanguard/packages/` vs `layer0/` Assessment
8. Current Architecture Conflict Matrix
9. Concept & Primitive Review
10. Recommended Concept Lock Model
11. Multi-Agent & Recursive Agency Assessment
12. Event Sourcing / Ledger / CAS / Graph Assessment
13. Plugin Architecture Assessment
14. Authority & Security Assessment
15. Resource & Concurrency Assessment
16. Meta-Harness / Self-Improvement Assessment
17. CI & Gate Assessment
18. Review of Principal Staff Engineer Proposals
19. What I Would Keep
20. What I Would Change
21. What I Would Remove or Avoid
22. What I Would Explicitly Defer
23. P0 Decisions
24. P1 Decisions
25. P2 Decisions
26. P3 / Research
27. Unknowns / Required Experiments
28. Recommended Architecture & Concept Lock Sequence
29. Suggested Documentation Changes — DO NOT APPLY
30. Suggested Roadmap Implications — DO NOT APPLY
31. Risks and Trade-offs
32. Final Independent Tech Lead Recommendation
```

---

# 20. CRITICAL COMPARISON REQUIREMENT

The final report must make it possible for another reviewer to compare:

```text
PRINCIPAL STAFF ENGINEER APPROACH
                VS
INDEPENDENT TECH LEAD APPROACH
```

Therefore explicitly identify:

```text
WHERE BOTH APPROACHES AGREE

WHERE THEY PARTIALLY AGREE

WHERE THEY DISAGREE

WHERE THIS TECH LEAD WOULD MODIFY THE PRINCIPAL PROPOSAL

WHERE THE PRINCIPAL PROPOSAL APPEARS STRONGER

WHERE THIS TECH LEAD PROPOSAL APPEARS STRONGER

WHERE EVIDENCE IS INSUFFICIENT TO CHOOSE
```

Do not force convergence.

The purpose is to preserve two independently reasoned alternatives for later synthesis.

---

# 21. GOLDEN RULE

Do not modify the project.

Do not turn recommendations into implementation.

Do not rewrite normative documents.

Do not create a competing roadmap.

Do not silently adopt the Principal Staff Engineer plan.

Do not deliberately oppose it.

Investigate independently.

Use existing reviews as evidence and intellectual input.

Distinguish:

```text
WHAT EXISTS
WHAT IS NORMATIVE
WHAT OTHERS PROPOSE
WHAT YOU INDEPENDENTLY RECOMMEND
WHAT REMAINS UNKNOWN
```

The central question is:

> Based on the actual repository, current normative architecture, competing reviews, engineering constraints, and long-term Vanguard/AETHER objectives, what Architecture & Concept Lock would this independent Tech Lead recommend — and what specifically would it change, preserve, reject, or defer compared with the other team's proposal?

Write the complete answer only to:

`docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/tech_lead_concept_lock_plan_suggestion.md`
