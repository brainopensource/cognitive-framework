````markdown
# VANGUARD / AETHER v0.6 — INDEPENDENT PRINCIPAL ARCHITECT CONCEPT LOCK REVIEW

## SYSTEM DIRECTIVE

Act as the **Principal Architect / Chief Software Architect** for Vanguard / AETHER.

This engagement is **ANALYSIS-ONLY**.

Multiple engineering teams are currently evaluating the same Vanguard/AETHER v0.6 transition using partially different architectural strategies.

Your role is to provide a **third, independent architecture-level assessment**, focused on long-term system integrity, conceptual minimalism, migration risk, extensibility, multi-agent evolution, operational viability, and preservation of useful existing code.

You MUST NOT modify the project.

You MUST produce exactly **ONE report**:

```text
docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/00_architect_concept_lock_plan_suggestion.md
````

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

DO NOT MODIFY EXISTING REVIEWS
DO NOT CREATE IMPLEMENTATION TASKS
DO NOT COMMIT CHANGES
```

The only repository artifact you may create is:

```text
docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/00_architect_concept_lock_plan_suggestion.md
```

You are evaluating **what the future Architecture & Concept Lock should establish**, not applying those decisions.

---

# 2. ARCHITECTURE MISSION

Investigate the repository, normative architecture, tests, CI, ADR history, implementation drift, previous architecture proposals, and competing recommendations.

Then answer:

> If you were the Principal Architect responsible for establishing a durable Vanguard / AETHER v0.6 foundation, what architecture and conceptual model would you recommend locking before development resumes?

Your analysis must optimize for:

```text
architectural coherence
minimal trusted core
conceptual simplicity
long-term evolvability
migration safety
reuse of mature implementation
domain independence
plugin extensibility
recursive multi-agent capability
event provenance
resource efficiency
security boundaries
testability
scientific measurability
operational simplicity
future polyglot compatibility
```

Do not optimize for architectural novelty.

Do not optimize for preserving existing code at all costs.

Do not optimize for matching another team's proposal.

Seek the smallest durable architecture that can evolve without repeated foundational rewrites.

---

# 3. INDEPENDENCE REQUIREMENT

This report exists as a **third architectural opinion**.

There are already at least:

```text
PRINCIPAL STAFF ENGINEER APPROACH

INDEPENDENT TECH LEAD APPROACH

PRINCIPAL ARCHITECT APPROACH  ← THIS REPORT
```

Read the other proposals carefully, but derive your conclusions independently.

Do NOT:

* automatically follow the Principal Staff Engineer;
* automatically follow the Tech Lead;
* manufacture disagreement merely to appear independent;
* average incompatible architectures into a compromise;
* assume the newest review is the most correct.

Instead:

```text
inspect evidence
→ understand constraints
→ evaluate alternatives
→ derive architecture
→ compare afterward
```

---

# 4. EVIDENCE & AUTHORITY MODEL

Maintain a strict separation between three kinds of truth.

## 4.1 AS-BUILT TRUTH

Executable code, tests, CI, repository history, schemas, generated artifacts, and observed runtime behavior establish:

> What exists today.

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

---

## 4.2 NORMATIVE INTENT

Inspect:

```text
docs/SPEC.md
docs/04_annex/
docs/05_adr/
```

These establish the currently intended architecture.

Implementation drift must not silently become architecture.

---

## 4.3 REVIEWS / PROPOSALS / PLANS

Treat as non-authoritative architectural inputs:

```text
docs/07_reviews/
docs/06_references/
docs/02_roadmap/
docs/03_sprints/
```

They may contain useful evidence, obsolete assumptions, strong recommendations, or contradictory models.

---

# 5. EVIDENCE LABELS

Classify significant conclusions as:

```text
[FACT]
[INFERENCE]
[ARCHITECTURAL RECOMMENDATION]
[UNKNOWN]
```

## `[FACT]`

Direct evidence from code, tests, CI, repository history, normative documentation, or reproducible commands.

## `[INFERENCE]`

Reasoned conclusion supported by facts but not directly proven.

## `[ARCHITECTURAL RECOMMENDATION]`

The architecture this Principal Architect recommends adopting during Concept Lock.

## `[UNKNOWN]`

Insufficient evidence. Requires experiment, spike, profiling, or later decision.

Never convert assumptions into facts.

---

# 6. REVIEW THE CURRENT SYSTEM AS A WHOLE

Do not review subsystems in isolation only.

Construct a whole-system model covering:

```text
Identity
Authority
State
Events
Effects
Scheduling
Plugins
Harness Composition
Evaluation
Storage
Resources
Agents
Projects
Artifacts
Models
Tools
Memory
Context
Experimentation
Learning
Operations
```

Determine whether these concepts currently form:

```text
ONE COHERENT ARCHITECTURE

MULTIPLE OVERLAPPING ARCHITECTURES

PARTIALLY MIGRATED ARCHITECTURE

ACCIDENTAL ARCHITECTURE
```

Explain why.

---

# 7. DUAL-RUNTIME ARCHITECTURE REVIEW

Independently analyze:

```text
vanguard/packages/
layer0/
```

Determine:

* historical relationship;
* duplication level;
* architectural divergence;
* implementation maturity;
* test maturity;
* operational completeness;
* boundaries;
* missing capabilities;
* duplicated defects;
* contract incompatibilities;
* migration cost;
* rewrite cost;
* convergence cost.

Evaluate architectural alternatives:

```text
PACKAGES CANONICAL
LAYER0 CANONICAL
SELECTIVE CONVERGENCE
FULL CONVERGENCE
REBUILD
THIRD CLEAN CORE
INCREMENTAL STRANGLER MIGRATION
OTHER
```

Do NOT perform any migration.

Recommend which model Concept Lock should establish and why.

Explicitly evaluate the risk of creating a **third runtime identity**.

---

# 8. ARCHITECTURAL MINIMALISM / MICROKERNEL REVIEW

Determine the smallest set of semantics that truly need to belong to the trusted substrate.

Evaluate candidates such as:

```text
event semantics
identity
authority
effect mediation
resource conservation
plugin lifecycle
scheduler mechanism
composition
```

Then evaluate whether:

```text
planning
memory
context
tools
models
skills
indexing
AST
reflection
routing
coordination strategies
self-improvement
domain logic
```

can remain outside the trusted core.

Ask:

> What must be simultaneously correct for the entire system to remain safe and coherent?

Recommend the minimum durable kernel boundary.

---

# 9. CONCEPTUAL MODEL REVIEW

Evaluate the future canonical meaning of:

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
Verdict

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

For each determine:

```text
KEEP
REFINE
GENERALIZE
MERGE
REMOVE
DEFER
UNRESOLVED
```

Pay particular attention to conceptual duplication.

Do not introduce new abstractions unless existing concepts genuinely cannot express the requirement.

---

# 10. RECURSIVE AGENCY / MULTI-AGENT ARCHITECTURE

Independently evaluate:

```text
Agent = Principal + HarnessInstance

SubAgent = ChildPrincipal + HarnessInstance
```

and whether the same primitive model can represent:

```text
root agent
specialist agent
subagent
meta-agent
critic
research agent
coding agent
swarm participant
```

without separate engines.

Evaluate:

```text
spawn(
    parent,
    harness,
    capabilities,
    budget
)
```

with candidate invariants:

```text
Capabilities(child) ⊆ Capabilities(parent)

Budget(child) <= RemainingBudget(parent)
```

Determine which semantics must exist early:

```text
project_id
principal_id
parent_principal_id
episode_id
parent_episode_id
harness identity
execution identity
causation_id
correlation_id
ownership
budget lineage
capability lineage
evaluation identity
```

Recommend which semantics should be locked now versus deferred.

Do not implement multi-agent.

---

# 11. ORCHESTRATOR ARCHITECTURE

Evaluate what the orchestrator should actually mean.

Distinguish:

```text
decision authority

state authority

resource scheduling

agent coordination

workflow planning

project supervision
```

Determine whether the orchestrator should be:

```text
a stateful authority
a disposable decision process
a scheduler extension
a project-level coordinator
a plugin
a separate engine
a composition of existing primitives
```

Evaluate carefully:

```text
Decision
→ Durable Event
→ Reducer
→ Effective State
```

versus mutable orchestrator-owned state.

Recommend the cleanest architecture.

---

# 12. EVENT SOURCING / LEDGER / STATE MODEL

Evaluate:

```text
State = fold(Events)
```

and the architectural roles of:

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
Inbox/Outbox
```

Determine which are:

```text
AUTHORITATIVE
DERIVED
ACCELERATION
COGNITIVE
ANALYTICAL
CONTENT STORAGE
```

Review replay semantics separately:

```text
state replay
schedule replay
real-world re-execution
deterministic fixture replay
```

Recommend the appropriate guarantees for each.

---

# 13. CAUSALITY & GRAPH ARCHITECTURE

Evaluate relationships such as:

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

Determine whether graph structure should be:

```text
fundamental execution model
static DAG
dynamic planner model
event-derived projection
hybrid
```

Evaluate whether a graph database is architecturally necessary.

Do not confuse causal structure with a workflow engine.

Recommend the minimum causal primitives necessary for future multi-agent execution.

---

# 14. IDENTITY ARCHITECTURE

Review whether a single digest is sufficient.

Evaluate the proposed separation:

```text
Harness Identity
Execution Identity
Experiment Cell Identity
```

and formulations such as:

```text
D_H
D_R
D_X
```

Determine which identities are required to support:

```text
reproducibility
attribution
A/B testing
plugin substitution
model changes
runtime changes
oracle changes
cross-domain experiments
self-improvement
```

Recommend the minimum identity model Concept Lock should establish.

---

# 15. PLUGIN ARCHITECTURE

Evaluate the plugin-first model.

Determine whether the same plugin architecture should support:

```text
planner
memory
context
compression
cache strategy
indexing
AST
heuristics
tools
scripts
skills
model routing
reflection
coordination policies
Meta-Harness strategies
```

while keeping foundational authority below the boundary.

Review whether existing SPIs are sufficient.

Do not proliferate SPIs without a stable semantic reason.

Evaluate whether the current five-SPIs model is appropriate.

---

# 16. PLUGIN CONTRACT / POLYGLOT ARCHITECTURE

Review:

```text
Python typing.Protocol
in-process invocation
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

Distinguish:

```text
semantic contract
wire contract
language binding
isolation mechanism
transport
```

Determine which should be stable and which should remain implementation choices.

Evaluate whether Python-first can coexist cleanly with future polyglot plugins.

Recommend conditions under which Rust, WASM, gRPC, or other technologies would become justified.

---

# 17. EVALUATOR / EVIDENCE ARCHITECTURE

Evaluate:

```text
agent
evaluation gate
external evaluator
oracle
verdict
promotion authority
```

Determine which component can:

```text
request evaluation
produce verdict
verify verdict
consume verdict
promote changes
```

Review the principle:

> The judge must remain unreachable from the judged.

Determine whether evaluator identity should remain exterior and independent from agent-selectable plugins.

---

# 18. RESOURCE ARCHITECTURE

Review:

```text
Budget
Reservation
Lease
Capability
Worker
Logical Agent
Model Runtime
Workspace
```

Evaluate the distinction:

```text
Logical Agent != Heavy Execution Worker
```

and:

```text
K workers << N logical agents
```

Analyze:

* shared models;
* worker pools;
* copy-on-write;
* immutable harness sharing;
* CAS deduplication;
* sparse activation;
* hierarchical budgets;
* bounded execution.

Determine what should be semantics versus optimization.

---

# 19. CONCURRENCY ARCHITECTURE

Evaluate what must be modeled now even if v0.6 executes sequentially.

Review:

```text
causality
read/write selectors
independence
cancellation
revocation
leases
conflict detection
effect reconciliation
```

Determine whether concurrency should remain disabled initially.

Evaluate whether vector clocks, distributed logs, Merkle DAGs, NATS, Kubernetes, or other distributed mechanisms are currently justified.

---

# 20. AUTHORITY & SECURITY ARCHITECTURE

Evaluate:

```text
Principal identity
Capability attenuation
Budget conservation
Plugin trust
Effect mediation
Sandbox
Evaluator exteriority
Cancellation
Revocation
Provenance
Artifact ownership
```

Separate:

```text
SECURITY SEMANTICS REQUIRED FOR CONCEPT LOCK
```

from:

```text
SECURITY HARDENING THAT CAN BE ADDED LATER
```

Avoid both under-design and premature security infrastructure.

---

# 21. META-HARNESS & SELF-IMPROVEMENT ARCHITECTURE

Evaluate whether the following can emerge from existing primitives:

```text
Harness H0
→ Execution
→ Trajectory
→ Candidate
→ Harness H1
→ Experiment
→ External Evaluation
→ Promotion / Rejection
```

Review separately:

```text
runtime adaptation
memory adaptation
composition adaptation
skill synthesis
plugin synthesis
model adaptation
core modification
```

Determine which require architecture now and which belong to future research.

Preserve governance separation between:

```text
candidate generation
measurement
evaluation
promotion
```

---

# 22. DOMAIN GENERALITY

Evaluate whether Vanguard should be able to support:

```text
coding
research
data analysis
structured environments
future unknown domains
```

without changing the core.

Evaluate the architectural falsification criterion:

```text
New Domain
→ Plugin / Pack / Composition
```

versus:

```text
New Domain
→ Core Modification
```

Recommend how Concept Lock should preserve domain independence.

---

# 23. SOTA VS NECESSARY COMPLEXITY

Review architecture choices against current engineering best practices and state-of-the-art patterns.

However:

> SOTA is evidence, not a requirement to adopt complexity.

For each major technology or mechanism ask:

```text
What problem does this solve now?

Is that problem currently measured?

Can a simpler mechanism preserve the future option?

What migration cost does adoption create?

What irreversible commitment does it introduce?
```

Prefer reversible decisions when evidence is weak.

---

# 24. MIGRATION ARCHITECTURE

Without producing a roadmap, evaluate the correct architectural migration philosophy.

Compare:

```text
rewrite
port
converge
strangler migration
incremental extraction
selective salvage
parallel runtimes
clean-slate core
```

Determine which approach minimizes:

```text
lost mature behavior
duplicate bugs
third-runtime risk
test invalidation
semantic drift
time without product progress
```

Recommend only the migration strategy, not implementation tasks.

---

# 25. CI / VERIFICATION ARCHITECTURE

Review whether current gates actually prove their claimed properties.

Ask for every significant gate:

> What is the cheapest incorrect implementation that could still pass?

Classify gates:

```text
STRONG BEHAVIORAL PROOF
VALID STRUCTURAL PROOF
WEAK PROXY
FALSE CONFIDENCE
UNKNOWN
```

Recommend which architectural invariants eventually need behavioral verification.

Do NOT modify CI.

---

# 26. REVIEW EXISTING PRINCIPAL / STAFF / TECH LEAD PROPOSALS

Read carefully:

```text
docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/principal_engineer_proposal.md

docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/vanguard-arquitetura-v4-parecer-e-plano.md

docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/Vanguard-substrate-060-full-refactor-v3-1.md

docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/vanguard-substrate-060-execution-plan.md
```

Also read the independent Tech Lead report if it already exists:

```text
docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/tech_lead_concept_lock_plan_suggestion.md
```

For major recommendations classify:

```text
AGREE
AGREE WITH MODIFICATION
DISAGREE
DEFER
INSUFFICIENT EVIDENCE
```

Explain the architectural reason.

---

# 27. DECISION CLASSIFICATION

Classify recommended Concept Lock decisions as:

## P0 — ARCHITECTURAL LOCK BEFORE DEVELOPMENT

Structural decisions where postponement would create substantial migration/rework risk.

## P1 — LOCK OR DELIBERATELY DEFER

Important architecture with a required explicit decision:

```text
LOCK NOW
```

or:

```text
DEFER DELIBERATELY
```

## P2 — IMPLEMENTATION CHOICE

Should remain replaceable and should not block Concept Lock.

## P3 — RESEARCH / FUTURE

Long-term mechanisms and hypotheses.

## UNKNOWN / NEEDS EXPERIMENT

Insufficient evidence for responsible architectural commitment.

---

# 28. REQUIRED SINGLE DELIVERABLE

Create ONLY:

```text
docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/00_architect_concept_lock_plan_suggestion.md
```

The report must contain:

```text
1. Executive Summary
2. Principal Architect Mandate & Independence Statement
3. Evidence and Architecture Evaluation Method
4. Current System Architecture As-Built
5. Normative Architecture Assessment
6. Dual-Runtime Assessment
7. Architectural Minimalism / Microkernel Assessment
8. Canonical Concept Model
9. Recommended Concept Lock
10. Recursive Agency / Multi-Agent Architecture
11. Orchestrator Architecture
12. Event Sourcing / Ledger / State Architecture
13. Causality / Execution Graph Architecture
14. Identity Architecture
15. Plugin Architecture
16. Plugin Contract / Polyglot Architecture
17. Evaluator / Evidence Architecture
18. Resource Architecture
19. Concurrency Architecture
20. Authority & Security Architecture
21. Meta-Harness / Self-Improvement Architecture
22. Domain Generality Assessment
23. Migration Architecture
24. CI / Verification Architecture
25. What Should Remain in the Trusted Core
26. What Should Become Replaceable / Plugin-Based
27. What I Would Preserve
28. What I Would Change
29. What I Would Remove / Reject
30. What I Would Explicitly Defer
31. P0 Architectural Decisions
32. P1 Lock-or-Defer Decisions
33. P2 Implementation Choices
34. P3 Research Topics
35. Unknowns / Experiments Required
36. Principal Staff Proposal Review
37. Independent Tech Lead Proposal Review
38. Three-Way Agreement / Disagreement Matrix
39. Recommended Concept Lock Sequence
40. Suggested SPEC / ADR Changes — DO NOT APPLY
41. Suggested Migration Implications — DO NOT APPLY
42. Suggested Roadmap Implications — DO NOT APPLY
43. Architecture Risks and Trade-offs
44. Architecture Falsification Criteria
45. Final Principal Architect Recommendation
```

---

# 29. THREE-WAY COMPARISON REQUIREMENT

The report must explicitly support comparison between:

```text
PRINCIPAL STAFF ENGINEER
          VS
INDEPENDENT TECH LEAD
          VS
PRINCIPAL ARCHITECT
```

Create a decision matrix covering at least:

```text
runtime target
packages vs layer0
Python vs Rust
microkernel boundary
plugin boundary
SPIs
wire protocol
event sourcing
ledger authority
orchestrator semantics
recursive agents
spawn semantics
multi-agent
project identity
graph semantics
identity digests
concurrency
resource model
evaluator
security
Meta-Harness
self-improvement
distribution
migration strategy
CI gates
```

For each identify:

```text
FULL AGREEMENT

PARTIAL AGREEMENT

ARCHITECT MODIFICATION

MATERIAL DISAGREEMENT

INSUFFICIENT EVIDENCE
```

Do not force consensus.

---

# 30. ARCHITECTURE FALSIFICATION REQUIREMENT

For every major architectural recommendation, state:

```text
WHAT EVIDENCE WOULD PROVE THIS DECISION WRONG?
```

Examples:

```text
If new domains repeatedly require Layer/Core changes,
the claimed domain-general boundary is insufficient.

If recursive subagents require a second runtime engine,
the recursive-agent abstraction is insufficient.

If wire-first plugins create material measured overhead with no portability benefit,
the boundary should be reconsidered.

If convergence destroys tested behavior faster than selective migration preserves it,
the migration strategy should be reconsidered.
```

Architecture decisions should be reversible where possible and falsifiable where meaningful.

---

# 31. GOLDEN RULE

Do not modify the project.

Do not implement your recommendations.

Do not rewrite normative documents.

Do not create another roadmap.

Do not average competing architectures into a compromise merely because multiple teams proposed them.

Do not assume architectural sophistication is architectural quality.

Prefer:

```text
SMALLER CORE
CLEARER AUTHORITY
FEWER FUNDAMENTAL CONCEPTS
MORE COMPOSITION
MEASURABLE BEHAVIOR
REVERSIBLE IMPLEMENTATION CHOICES
EXPLICIT CAUSALITY
EXPLICIT RESOURCE CONTROL
EVIDENCE-BASED EVOLUTION
```

Distinguish clearly:

```text
WHAT EXISTS

WHAT IS NORMATIVE

WHAT PRINCIPAL STAFF RECOMMENDS

WHAT TECH LEAD RECOMMENDS

WHAT PRINCIPAL ARCHITECT RECOMMENDS

WHAT EVIDENCE SUPPORTS EACH

WHAT REMAINS UNKNOWN
```

The central question is:

> What is the smallest, most coherent, evolvable, measurable, and operationally realistic architecture Vanguard/AETHER should lock in v0.6 so that coding agents, recursive multi-agent systems, domain packs, Meta-Harness evolution, and future self-improvement can grow primarily through composition rather than repeated reconstruction of the core?

Write the complete answer only to:

```text
docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/00_arch_concept_lock_plan_suggestion.md
```
