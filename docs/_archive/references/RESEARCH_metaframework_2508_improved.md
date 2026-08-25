# RESEARCH Meta-Framework 2508 — Improved Final Delta Report

**Research date:** 25 August 2026  
**Artifact:** `RESEARCH_metaframework_2508_improved.md`  
**Purpose:** Final PhD-level synthesis of the research completed on 25 August 2026, focused specifically on findings that materially extend the preceding Harness / Meta-Framework reports rather than repeating their established foundation.

---

# 1. Date and Scope

This report is a **delta-focused technical supplement** to the previous Meta-Framework research.

The broader program investigates the construction of a computational substrate for evolvable intelligent systems:

```text
Immutable Kernel
→ Primitive Runtime
→ Composition / Phenotype Plane
→ Adaptation / Meta-Control
→ Evolution
→ Learning
→ Independent Evaluation
```

The objective is not to design a larger monolithic agent. It is to identify the smallest operational substrate from which agents, strategies, planners, memory systems, specialists, hierarchies, teams, and learning procedures can be composed, evaluated, mutated, selected, consolidated, and evolved.

The research completed today materially changes the implementation thesis in four areas:

1. **strategy revision is distinct from execution competence;**
2. **architecture should increasingly be compiled from task structure rather than fixed globally;**
3. **skill accumulation must be distinguished from genuine consolidation and abstraction;**
4. **safe evolution requires explicit responsibility and mutation boundaries.**

The research therefore moves the design one level above "self-improving harnesses" toward a framework that can detect **which level of organization is failing** and mutate the appropriate layer.

---

# 2. Executive Summary

The strongest new evidence is that current autonomous systems can improve execution while remaining strategically rigid.

A recent empirical study of autonomous post-training agents reports that systems can operate complex training pipelines, debug implementations, retry failures, and improve local metrics while continuing to use the same high-level strategy chosen near the start of the run. The reported experience scaffolding improves execution substantially on some benchmarks, but does not reliably trigger strategy revision.

This establishes a critical distinction:

```text
Execution improvement
≠
Strategic improvement
```

A system may optimize:

```text
actions
parameters
tool usage
local plans
retry policies
```

while failing to reconsider:

```text
problem representation
solution family
objective decomposition
training regime
architecture
search method
```

This creates a **meta-level local optimum**.

The resulting architectural requirement is to make strategy and revision explicit, measurable, versioned objects.

A second major result comes from task-conditioned orchestration work such as Eureka. Instead of using one universal architecture for every long-horizon task, the system derives local obligations and instantiates specialized structures only where they are justified. This supports the design principle:

```text
Agent = compiled phenotype
```

rather than:

```text
Agent = substrate primitive
```

The Meta-Framework should increasingly behave like a **runtime architecture compiler**.

A third result comes from continual skill-learning evaluation. Sequential experience often helps, but explicit skill libraries are not always the causal source of improvement. In some settings, simple in-context adaptation performs comparably to explicit skill maintenance. Therefore:

```text
skill count
≠
learning
```

The scientifically important operation is **consolidation**:

```text
experience
→ recurring invariant
→ abstraction
→ compact procedure
→ held-out validation
→ durable promotion
```

A fourth result concerns safety. Safety Harness Evolution demonstrates that evolvable safety components become more tractable when responsibility is decomposed across explicit artifacts and trajectory evidence is used to localize failures. This strengthens the architecture rule:

> An artifact is safely evolvable only when its authority, responsibility, mutation scope, and evaluation contract are explicit.

The revised candidate primitive set is therefore:

```text
OBSERVE
REPRESENT
PREDICT
SELECT
ACT
STORE
RETRIEVE
COMMUNICATE
ALLOCATE
VERIFY
EVALUATE
COMPOSE
VARY
CONSOLIDATE
REVISE
SCHEDULE
```

`CONSOLIDATE` and `REVISE` are new explicit interfaces motivated by today's evidence.

They should be implemented now as observable first-class operations, but not yet declared irreducible constitutional primitives.

---

# 3. Evidence Model

Claims use the following evidence grades:

```text
A — strong / replicated empirical evidence
B — published experimental evidence
C — engineering evidence / primary-source system evidence
D — plausible architectural hypothesis
E — speculation / long-range hypothesis
```

Today's strongest claims are primarily **B/C**.

Important caution:

```text
paper result
≠
universal law
```

Every result should be treated as evidence for a falsifiable architectural hypothesis.

---

# 4. New Finding 1 — Strategic Intelligence Is Not Execution Intelligence

## Observation

Autonomous systems can exhibit sophisticated local optimization while failing to invalidate an increasingly implausible global strategy.

## Evidence

Recent empirical analysis of autonomous post-training trajectories reports:

```text
experience scaffolding
→ better execution
→ better local outcomes
→ little strategic reconsideration
```

Human intervention can alter the initial strategy, after which the system again tends toward local refinement.

**Evidence grade: B.**

## Mechanism

Current loops frequently resemble:

```text
choose S0

repeat:
    execute(S0)
    observe
    debug
    tune
    retry
```

The missing operation is:

```text
if evidence_against(S0) accumulates:
    generate alternative strategies
    compare
    branch / switch / abandon
```

The optimization landscape is hierarchical.

Let:

```text
x = local execution parameters
S = strategy
A = architecture
L = learning procedure
```

Most current systems predominantly search:

```text
argmax_x U(x | S, A, L)
```

while deeper adaptation requires eventually searching:

```text
S
A
L
```

as well.

This is the difference between local optimization and structural self-revision.

---

# 5. Strategy Must Become a First-Class Scientific Artifact

Strategy should not exist only as model prose.

Proposed schema:

```text
StrategyDefinition {
    id
    problem_representation
    assumptions
    objective_decomposition
    method_family
    constraints
    predicted_observations
    falsification_conditions
    resource_model
    lineage
}
```

Runtime strategy state:

```text
StrategyState {
    strategy_id
    selected_at
    commitment_age
    evidence_for
    evidence_against
    prediction_errors
    marginal_gain_history
    alternatives_considered
    switching_cost
}
```

This allows the trajectory to answer:

```text
What strategy was active?
Why was it selected?
What assumptions were made?
What observations contradicted it?
Were alternatives generated?
Why was switching rejected?
How much budget was consumed after contradiction appeared?
```

Without this, strategy lock-in is invisible.

---

# 6. Candidate Primitive — REVISE

Today's evidence justifies an explicit `REVISE` interface.

Conceptual interface:

```text
RevisionDecision revise(
    current_strategy,
    evidence,
    alternatives,
    self_model,
    remaining_budget,
    switching_cost
)
```

Possible outputs:

```text
CONTINUE
MODIFY
BRANCH
SWITCH
ABANDON
ESCALATE
```

Possible triggers:

```text
diminishing marginal improvement
persistent prediction error
repeated same-family interventions
high evaluator disagreement
low confidence
failure recurrence
unexpected observations
excessive commitment age
sufficient exploration budget
```

The current hypothesis is:

```text
REVISION
=
meta-level control over strategy selection
```

But its irreducibility remains unproven.

It may ultimately reduce to:

```text
PREDICT
+ EVALUATE
+ SELECT
+ VARY
+ REPRESENT
```

Therefore its status is:

```text
failure-mode evidence: B
primitive irreducibility: D
```

---

# 7. Strategic Revision as Value of Computation

Revision consumes resources and should not occur continuously.

A rational controller approximates:

```text
EVR =
ExpectedUtility(search_alternatives)
− ExpectedUtility(continue_current_strategy)
− RevisionCost
− SwitchingCost
```

Revision is justified when:

```text
EVR > threshold
```

This connects the Meta-Framework to:

```text
bounded rationality
value of computation
value of information
Bayesian model comparison
bandit theory
sequential decision processes
change-point detection
```

A practical early implementation can use deterministic heuristics while preserving the data required for later learned policies.

---

# 8. Strategy Portfolios Instead of Redundant Worker Populations

Multi-agent evidence already shows that more agents can reduce performance.

Today's strategy-lock result suggests a better use for populations.

Instead of:

```text
worker_1(strategy_A)
worker_2(strategy_A)
worker_3(strategy_A)
```

use:

```text
candidate_1(strategy_A)
candidate_2(strategy_B)
candidate_3(strategy_C)
```

This shifts the population objective from:

```text
execution redundancy
```

toward:

```text
hypothesis diversity
```

The important metric becomes:

```text
strategic diversity per unit compute
```

This can be managed using:

```text
bandits
tournaments
Pareto selection
novelty search
Bayesian evidence
Quality Diversity
```

The resulting architecture is closer to a **scientific hypothesis portfolio** than a conventional swarm.

---

# 9. New Finding 2 — Architecture Should Be Compiled Lazily

## Evidence

Eureka introduces task-conditioned orchestration based on obligation graphs and local Macro-Agent formation.

Reported results include:

```text
170 / 170 recursive tasks completed
3,948 acceptance certificates
median model-input context:
9,490 → 4,005 tokens
65.38% repeated dependency processing avoided
```

**Evidence grade: B for the paper's experiments; C for architectural generalization until independently reproduced.**

## Mechanism

Instead of:

```text
instantiate universal architecture
→ force task through fixed structure
```

use:

```text
task evidence
→ derive obligations
→ detect architecture hotspot
→ instantiate minimal local structure
→ execute
→ verify
→ retire/recompile
```

This suggests:

```text
architecture = task-conditioned phenotype
```

---

# 10. Agent Should Remain a Derived Phenotype

The stronger abstraction is not `Agent`.

It is:

```text
BoundedComputationalOrganization {
    composition_graph
    state_boundary
    capability_lease
    resource_lease
    model_policy
    communication_endpoints
}
```

An "agent" is one possible compiled form.

A task may require:

```text
one sequential graph
temporary verifier
multiple specialists
market-like arbitration
no explicit agent boundary at all
```

Therefore the kernel and primitive runtime should not constitutionally depend on the `Agent` abstraction.

---

# 11. ArchitectureGenome Must Include Development

The previous static genome model should be extended:

```text
ArchitectureGenome {
    primitive_genomes
    graph_constraints
    routing_policies
    memory_topology
    communication_topology
    resource_policies

    development_program
    compilation_triggers
    specialization_rules
    retirement_rules

    strategy_policy
    revision_policy
    consolidation_policy

    lineage
}
```

Example developmental rules:

```text
IF independent branches > threshold
THEN instantiate specialists

IF uncertainty high
AND effect risk high
THEN attach verifier

IF repeated dependency detected
THEN create shared intermediate artifact

IF strategic stagnation detected
THEN spawn alternative-strategy branch
```

This creates two different evolutionary representations.

### Direct encoding

```text
Genome
→ final graph
```

### Developmental encoding

```text
Genome
→ construction rules
→ inspect task/environment
→ runtime phenotype
```

The second may scale better, but that is a testable hypothesis.

---

# 12. New Finding 3 — Skill Accumulation Is Not Equivalent to Learning

ContinualSkillBench introduces an important negative control.

Across sequential tasks, systems often improve.

But the reported ablation shows that:

```text
in-context adaptation
≈
explicit skill maintenance
```

on average in some settings.

Therefore three mechanisms must be separated:

```text
contextual adaptation
episodic reuse
procedural abstraction
```

Only the third constitutes robust skill consolidation.

---

# 13. Mandatory Skill-Learning Baselines

Every claimed skill-learning experiment should compare:

```text
B0 isolated execution
B1 full-history / in-context adaptation
B2 episodic retrieval
B3 summarized memory
B4 explicit skill
B5 consolidated skill + evidence
```

Only if:

```text
B4/B5 > B1/B2
```

on held-out transfer, context efficiency, or robustness does the skill system demonstrate independent value.

This avoids attributing ordinary context effects to "learning."

---

# 14. Candidate Primitive — CONSOLIDATE

The deeper operation is:

```text
many experiences
→ identify invariant
→ remove incidental details
→ encode compact reusable structure
→ estimate applicability
→ validate
```

This deserves an explicit interface:

```text
ConsolidationCandidate consolidate(
    evidence_set,
    existing_knowledge,
    target_scope,
    compression_budget
)
```

Possible output categories:

```text
NO_PERSISTENCE
EPISODE
SEMANTIC_FACT
PROCEDURE
SKILL
POLICY_UPDATE
WORLD_MODEL_UPDATE
```

Not every episode should survive.

Selective forgetting is part of intelligent consolidation.

---

# 15. Consolidation Quality

A useful conceptual objective:

```text
ConsolidationUtility =
FutureUtilityGain
− PersistenceCost
− RetrievalCost
− InterferenceCost
− NegativeTransferRisk
```

Track:

```text
compression ratio
cross-task transfer
cross-environment transfer
activation precision
activation recall
reuse
negative transfer
redundancy
evidence quality
```

A long skill reused once may be worse than re-solving.

A compact procedure used across hundreds of tasks may be highly valuable.

---

# 16. Skill Fragmentation as a Failure Mode

Weaker systems can accumulate many narrow procedures.

Define:

```text
SkillFragmentationIndex
```

using:

```text
skill count
mean reuse
median reuse
semantic overlap
procedural overlap
conflict rate
cross-domain transfer
description length
```

A healthy consolidation process should tend toward:

```text
experience ↑
reuse ↑
transfer ↑
while
persistent complexity grows sublinearly
```

If:

```text
skills ≈ tasks
```

the system is likely memorizing rather than abstracting.

---

# 17. New Finding 4 — Responsibility Is a Requirement for Safe Evolvability

Safety Harness Evolution decomposes safety across explicit artifacts and uses trajectory evidence to localize failures.

The important systems lesson is broader than safety.

Every evolvable component should expose:

```text
ResponsibilityContract {
    intended_responsibilities
    allowed_effects
    prohibited_effects
    security_properties
    resource_contract
    expected_failure_classes
    mutation_scope
    verification_requirements
}
```

This enables:

```text
failure
→ attribution
→ scoped mutation
→ targeted evaluation
```

rather than global rewrites.

---

# 18. Evolvable Safety Policy vs Immutable Security Authority

Potentially evolvable:

```text
risk heuristics
safety memories
warning rules
tool-selection policy
verification strategy
context filters
```

Immutable:

```text
capability enforcement
sandbox
filesystem/network authority
resource ceilings
audit integrity
artifact provenance
evaluator authority
promotion authority
```

Thus:

```text
evolvable safety
≠
evolvable security law
```

---

# 19. New Finding 5 — Harness Evolution Has Capability Ceilings

Hierarchical Self-Improvement reports gains on some BALROG tasks but no improvement on NLE tasks beyond the frozen model's capability.

This supports:

```text
Harness improvement can expose latent capability.
Harness improvement cannot guarantee creation of absent capability.
```

The Meta-Harness therefore needs a:

```text
CapabilityCeilingDetector
```

Signals include:

```text
many independent harness variants fail similarly
strategy diversity fails
marginal gain approaches zero
failure signature remains invariant
stronger model succeeds under same harness
new tool changes outcome sharply
```

Possible escalation:

```text
switch model
add tool
change representation
retrieve external knowledge
train model
request human input
```

This prevents endless scaffold search.

---

# 20. Frozen Outer Anchor

Recursive improvement requires an evaluation frame that the candidate cannot rewrite.

General rule:

```text
mutable object
is evaluated by
less mutable / externally governed object
```

Examples:

```text
M0–M3 architecture evolution
→ fixed Meta-Harness evaluator

M4–M6 learning evolution
→ fixed experimental protocol

M7 mutation-policy evolution
→ external scientific governance
```

The system must never simultaneously control:

```text
candidate
metric
evaluator
promotion rule
evidence interpretation
```

because scientific attribution collapses.

---

# 21. Revised Primitive Ontology

Current candidate runtime primitives:

| Primitive | Role |
|---|---|
| OBSERVE | acquire typed external/internal evidence |
| REPRESENT | transform/compress state |
| PREDICT | generate testable future-state expectations |
| SELECT | bounded choice |
| ACT | effect proposal/execution |
| STORE | persistence |
| RETRIEVE | contextual selection from persistence |
| COMMUNICATE | typed information transfer |
| ALLOCATE | scarce resource assignment |
| VERIFY | local obligation/contract checking |
| EVALUATE | candidate fitness measurement |
| COMPOSE | graph formation |
| VARY | mutation/recombination/synthesis |
| CONSOLIDATE | evidence-to-durable-abstraction |
| REVISE | higher-level strategic reconsideration |
| SCHEDULE | temporal/concurrent activation |

These are still hypotheses.

The ontology should remain evolvable by evidence, not dogma.

---

# 22. Immutable Kernel

The kernel remains smaller than the cognitive substrate.

```text
Identity
Authority
Capability Algebra
Resource Accounting
Canonical Event Integrity
Artifact Identity
Provenance
Sandbox Isolation
Rollback
Evaluator Separation
Promotion Separation
```

The kernel should not know:

```text
planner
critic
skill
agent
swarm
strategy
memory architecture
```

That preserves future design-space freedom.

---

# 23. Revised Event Model

New strategic events:

```text
StrategyProposed
StrategySelected
StrategyEvidenceAdded
StrategyChallenged
RevisionTriggered
RevisionDecision
StrategySwitched
```

New consolidation events:

```text
PatternDetected
ConsolidationCandidateCreated
ConsolidationEvaluated
SkillPromoted
SkillRejected
MemoryPromoted
```

New architecture events:

```text
ArchitectureNeedDetected
SubgraphCompiled
SubgraphActivated
SubgraphRetired
```

New capability events:

```text
CapabilityCeilingSuspected
CapabilityEscalationRequested
```

Each event should preserve:

```text
event_id
run_id
parent_event_ids
actor/process
artifact refs
resource delta
authority context
evidence refs
logical time
```

---

# 24. Failure Taxonomy

Before mutating, classify failure.

```text
F0 infrastructure
F1 execution
F2 tool/interface
F3 retrieval/context
F4 tactical plan
F5 strategy
F6 architecture
F7 knowledge
F8 model capability
F9 evaluator
F10 security
F11 consolidation
F12 coordination
```

The mutation engine should receive:

```text
failure_class
+
responsible_component_set
```

and restrict candidate mutation accordingly.

This sharply reduces search entropy.

---

# 25. Revised Meta-Harness

```text
Evidence Collector
        ↓
Failure Classifier
        ↓
Stagnation / Opportunity Detector
        ↓
Hypothesis Generator
        ↓
Alternative Strategy Generator
        ↓
Mutation-Surface Selector
        ↓
Mutation Generator
        ↓
Experiment Designer
        ↓
Candidate / Phenotype Compiler
        ↓
Benchmark Runner
        ↓
Independent Evaluator
        ↓
Statistical + Causal Comparator
        ↓
Promotion Authority
        ↓
Registries / Lineage
```

This is not a privileged super-agent.

It is an automated experimental control system.

---

# 26. Mutation Power Becomes Two-Dimensional

Existing mutation levels:

```text
M0 runtime parameters
M1 runtime policies
M2 skills
M3 topology
M4 learning configuration
M5 model parameters
M6 learning algorithms
M7 evolutionary mechanisms
M8 experimental methodology
```

Add scope:

```text
S0 local
S1 component
S2 subgraph
S3 architecture
S4 population
S5 evolutionary process
```

Approximate risk:

```text
Risk ∝
MutationPower
× Scope
× Irreversibility
× AuthorityProximity
× Uncertainty
```

This produces more precise authorization.

---

# 27. StrategyGenome vs ArchitectureGenome

A strategy describes:

```text
how the problem is conceptualized
```

Architecture describes:

```text
what computational organization executes it
```

They should eventually be separable.

Potential future representation:

```text
StrategyGenome
ArchitectureGenome
```

Cross experiment:

```text
S1 + A1
S1 + A2
S2 + A1
S2 + A2
```

This reveals whether gains arise from better strategy or better execution organization.

---

# 28. Causal Attribution

Overall performance delta is not sufficient.

Use:

```text
same-seed replay
multi-seed replication
held-out tasks
component ablation
component swap
cross-model test
cross-environment test
```

For interaction effects:

```text
remove X
replace X
freeze X
swap X
sample component coalitions
```

Full Shapley attribution may be too expensive, but Shapley-inspired marginal analysis is practical.

---

# 29. Fitness Must Include Meta-Capability

Extend `FitnessVector`:

```text
correctness
generalization
robustness
reliability
autonomy
latency
tokens
cost
compute
memory
recovery
safety
reproducibility
adaptability
learning efficiency

strategy adaptability
consolidation efficiency
architecture efficiency
capability-ceiling detection accuracy
```

Conceptually:

```text
StrategyAdaptability
=
quality of evidence-triggered strategy switching

ConsolidationEfficiency
=
future utility gained / durable complexity added

ArchitectureEfficiency
=
task utility / active architecture cost

CeilingDetectionAccuracy
=
correct stop/escalate decisions
```

These measure higher-order competence.

---

# 30. Emergence Requires Null Models

A phenomenon should not be labeled emergent unless it is:

```text
not explicitly prescribed
reproducible
functionally useful
causally beneficial
transferable
robust to null controls
```

Examples:

```text
spontaneous specialization
novel communication protocol
new reusable abstraction
adaptive topology
strategy diversification
exaptation
```

Controls:

```text
remove role labels
randomize identities
scramble messages
freeze topology
equalize compute
repeat across seeds
```

Emergence is an empirical claim.

---

# 31. Persistent Adaptation Is a Security Surface

Any artifact capable of changing future behavior should include:

```text
provenance
creator
evidence
scope
confidence
security state
promotion state
expiry/decay
compatibility
```

Persistent artifacts need:

```text
quarantine
revocation
rollback
supersession
conflict tracking
```

Repeated model-generated content is not validated knowledge.

---

# 32. Revised Minimum Viable Meta-Framework

The MVP is an **experimental operating system for evolvable computation**.

Required modules:

```text
Primitive Registry
Composition Graph
Canonical Event System
Trajectory DAG
Artifact Store
Model Gateway
Sandbox
Budget Ledger

Hypothesis Registry
Experiment Registry
Evaluator Registry

Strategy Registry
Revision Interface

Memory Registry
Skill Registry
Consolidation Interface

ArchitectureGenome
Architecture Compiler

Mutation Engine
Population Registry
Selection Engine
Lineage Graph

Promotion Controller
Observability
```

Initial autonomous mutation:

```text
M0–M3
```

Protected:

```text
kernel
security enforcement
evaluator authority
promotion authority
model weights
learning algorithms
experimental methodology
```

---

# 33. Top 10 Experiments

## E1 — Strategy Lock-In

Construct problems with deceptive local optima.

Compare:

```text
ordinary replanning
reflection
periodic revision
stagnation-triggered revision
strategic population
```

Primary metric:

```text
strategic regret
```

## E2 — Strategy Diversity vs Worker Count

Equal total compute.

Compare one strategy with N workers against N competing strategies.

## E3 — Minimal Architecture Compilation

Compare:

```text
universal architecture
static template routing
runtime architecture compilation
```

## E4 — Direct vs Developmental Genome

Compare:

```text
final graph evolution
vs
graph-construction-rule evolution
```

## E5 — Skill Reality Test

Compare:

```text
isolated
history-only
episodic memory
summary
explicit skill
consolidated skill
```

## E6 — Skill Compression Frontier

Measure:

```text
persistent complexity
vs
held-out utility
```

## E7 — Capability Ceiling Detection

Mix tasks solvable by harness changes with tasks requiring new model/tool capability.

## E8 — Responsibility-Guided Safety Evolution

Inject localized failures and test scoped repair.

## E9 — Causal Mutation Attribution

Compare naïve candidate deltas against component ablation and swaps.

## E10 — Meta-Evolution with Frozen Anchor

Allow mutation-policy adaptation while evaluator, promotion, and security remain immutable.

---

# 34. Falsification Matrix

| Hypothesis | Supporting evidence | Falsification |
|---|---|---|
| explicit revision improves strategic adaptation | post-training strategy-lock evidence | no gain over ordinary replanning |
| dynamic architecture compilation improves efficiency | Eureka | static templates dominate after overhead |
| explicit skills produce durable abstraction | selective skill-benchmark gains | context-only matches on transfer/cost |
| responsibility decomposition improves safe evolution | SHE | composition effects defeat localization |
| harness evolution exposes latent capability | HSI / AHE family | no gain over simple search baseline |
| harness evolution has model ceilings | HSI negative NLE result | harness crosses repeated frozen-model ceiling |
| strategic populations help escape local optima | lock-in evidence + evolutionary logic | duplicated execution dominates |
| developmental genomes improve evolvability | developmental hypothesis | direct graph evolution dominates transfer/search |

---

# 35. What Should Not Be Hard-Coded

Current evidence argues against making these constitutional primitives:

```text
planner
critic
reflection loop
fixed agent boundary
fixed agent count
hierarchy
swarm
permanent skill injection
fixed memory topology
fixed communication protocol
fixed architecture
```

These should remain derived, learned, compiled, or evolved.

The substrate should hard-code only:

```text
execution semantics
authority
resources
identity
causal evidence
reproducibility
safe effects
scientific evaluation
```

---

# 36. Operational Definition of Intelligence

For the Meta-Framework, intelligence should be measured behaviorally.

A system becomes more intelligent when, under controlled resources, it improves its ability to:

```text
solve novel problems
learn from fewer experiences
transfer abstractions
select strategies
detect strategy failure
adapt architecture
recover from failure
allocate resources rationally
exploit new affordances
maintain calibration
```

while preserving:

```text
reliability
safety
reproducibility
```

This defines a measurable capability frontier.

---

# 37. Final Architectural Synthesis

```text
IMMUTABLE KERNEL
identity
authority
budgets
integrity
provenance
sandbox
rollback
evaluator separation
        ↓
PRIMITIVE RUNTIME
observe
represent
predict
select
act
store
retrieve
communicate
allocate
verify
schedule
        ↓
COMPOSITION / PHENOTYPE
dynamic graphs
agents
specialists
teams
        ↓
META-CONTROL
self-model
revision
consolidation
strategy management
capability-ceiling detection
        ↓
EVOLUTION
variation
populations
selection
architecture genomes
development programs
        ↓
LEARNING
policy/model adaptation
harness-native training
        ↓
INDEPENDENT SCIENTIFIC EVALUATION
benchmarks
hidden tests
statistics
replication
promotion
```

`COMPOSE`, `VARY`, `CONSOLIDATE`, `REVISE`, and `EVALUATE` remain typed interfaces across these conceptual layers.

---

# 38. Principal Scientific Conclusion

The critical question has changed from:

> How can the system improve its behavior?

to:

> **How can the system detect that the representation, strategy, architecture, or learning process generating its behavior is itself the object that must change?**

That distinction defines progressively deeper adaptation.

```text
changes actions
→ adaptive

changes procedures
→ learning

changes strategies
→ metacognitive adaptation

changes architectures
→ structural evolution

changes learning mechanisms
→ meta-learning

changes how hypotheses and experiments are generated
→ automated science
```

None of these count as real improvement unless independent evaluation demonstrates:

```text
causality
generalization
resource-normalized gain
reproducibility
safety
```

The target is therefore not an unconstrained self-modifying agent.

It is a **scientifically governed evolutionary computational substrate** capable of generating, testing, retaining, recombining, and discarding increasingly sophisticated organizations of computation.

---

# 39. Primary Sources — 25 August Delta

1. **What is Missing from AI Post-Training AI: An Empirical Analysis**  
   https://arxiv.org/abs/2608.19072

2. **Eureka: Task-Conditioned Meta-Agent Orchestration for Scientific Discovery**  
   https://arxiv.org/abs/2608.19047

3. **ContinualSkillBench: Can LLM Agents Truly Evolve Their Capabilities?**  
   https://arxiv.org/abs/2608.03874

4. **Hierarchical Self-Improvement: A Framework for Task-Specific Evolvable Agent Harnesses**  
   https://arxiv.org/abs/2608.08466

5. **SHE: Trajectory-driven Safety Harness Evolution for LLM Agents**  
   https://arxiv.org/abs/2608.09885

6. **Co-Evolution in Agentic Systems: Toward Self-Directed Evolution Beyond Human Design**  
   https://arxiv.org/abs/2608.10299

7. **Tree-of-Experience: Hierarchical Experience Management for Self-Evolving Agents**  
   https://arxiv.org/abs/2608.09044

8. **Metacognition in LLMs: Foundations, Progress, and Opportunities**  
   https://arxiv.org/abs/2607.11881

## Foundation carried forward from previous research

9. Agentic Harness Engineering  
   https://arxiv.org/abs/2604.25850

10. Evo-Harness  
    https://arxiv.org/abs/2608.15071

11. LEGO-RL  
    https://arxiv.org/abs/2608.17393

12. Agent Lightning v1.0  
    https://arxiv.org/abs/2608.17528

13. AI4AI-Bench  
    https://arxiv.org/abs/2608.20318

14. AEvo  
    https://arxiv.org/abs/2605.13821

15. MetaSkill-Evolve  
    https://arxiv.org/abs/2607.05297

16. Loreley  
    https://arxiv.org/abs/2608.19703

17. POET  
    https://arxiv.org/abs/1901.01753

18. MAP-Elites  
    https://arxiv.org/abs/1504.04909

---

# 40. Recommended Next Research Cycle

The next cycle should focus narrowly on unresolved mechanisms.

## Strategy revision

Study:

```text
Bayesian online change-point detection
non-stationary bandits
meta-level MCTS
value of computation
hypothesis portfolios
formal switching criteria
```

Central question:

> How can a system recognize that excellent local execution is occurring inside the wrong strategic frame?

## Developmental architecture

Study:

```text
graph grammars
HyperNEAT
indirect encodings
developmental programs
neural cellular automata
morphogenetic computation
program-generating programs
```

## Consolidation science

Determine when experience should become:

```text
nothing
episode
semantic memory
procedure
skill
policy
world-model update
```

## Capability ceiling detection

Develop statistical tests distinguishing:

```text
bad harness
from
insufficient underlying capability
```

## Strategic populations

Test populations of:

```text
hypotheses
world models
strategies
```

rather than duplicated worker agents.

## Scientific attribution

Develop efficient intervention methods for architecture-component causality without exhaustive combinatorial ablation.

---

# 41. Final Answer to the Research Question

The smallest currently defensible substrate is not a catalog of human-inspired cognitive faculties.

It is a set of typed computational operations:

```text
OBSERVE
REPRESENT
PREDICT
SELECT
ACT
STORE
RETRIEVE
COMMUNICATE
ALLOCATE
VERIFY
EVALUATE
COMPOSE
VARY
CONSOLIDATE
REVISE
SCHEDULE
```

executing under immutable laws:

```text
identity
authority
resource conservation
event/artifact integrity
provenance
sandbox isolation
rollback
evaluator independence
promotion independence
```

From these, agents, planners, memory structures, skills, organizations, and strategies should be instantiated as phenotypes.

The scientific proof process is:

```text
Observation
→ Hypothesis
→ Controlled Intervention
→ Candidate
→ Reproducible Execution
→ Independent Evaluation
→ Causal Comparison
→ Held-Out Replication
→ Promote / Reject / Inconclusive
```

Improvement is not established by:

```text
reflection
skill accumulation
more agents
more tokens
larger architecture
single-benchmark gain
```

It is established only when a versioned intervention produces a reproducible, resource-normalized, causally attributable improvement that transfers beyond the exact conditions that generated it while preserving immutable safety constraints.

The long-term objective is therefore **autonomous, evidence-governed scientific evolution of computational organization**.
