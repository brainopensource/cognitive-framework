---
id: research.coding-harness-meta-framework-2408
kind: research
status: reference
authority: non-canonical
summary: "Research report on evolvable agentic systems and meta-framework architecture."
topic:
  - coding-harness
---
# RESEARCH META FRAMEWORK 2408

## PhD-Level Research Report on Evolvable Agentic Systems

**Research date:** 2026-08-24

> **Central research question:** What minimal computational substrate
> can produce increasingly sophisticated intelligence as an emergent
> property of composition, learning, interaction, selection, and
> evolution---and how can we experimentally prove that improvements are
> causal, generalizable, and reproducible?

## 1. Executive Thesis

The strongest defensible architecture is not a universal agent, a
monolithic cognitive architecture, or an unconstrained self-modifying
program. It is a **scientific computational substrate** in which bounded
computational processes can observe, represent, select, act, store,
retrieve, communicate, allocate resources, compose, vary, learn, and be
independently evaluated.

The substrate should encode computational laws rather than intelligence
itself. Identity, authority, resource conservation, event integrity,
provenance, sandbox boundaries, evaluator independence, experiment
isolation, rollback, and causal traceability form an immutable kernel.
Above it, primitive operations compose into transient phenotypes:
agents, planners, critics, teams, memory systems, search procedures,
tool strategies, and organizations. These phenotypes may adapt and
evolve without redefining the laws under which they execute.

The minimal defensible primitive vocabulary is approximately:

``` text
OBSERVE
REPRESENT
SELECT
ACT
STORE
RETRIEVE
COMMUNICATE
ALLOCATE
EVALUATE
VARIATE
COMPOSE
SCHEDULE
```

Higher cognition should initially be derived rather than foundational:

``` text
attention = selection + resource allocation
memory = storage + retrieval + consolidation + forgetting
planning = predictive representation + search + selection
reflection = observation of internal trajectory + representation
metacognition = monitoring + self-model + control
skill = compressed reusable procedure + applicability + evidence
agent = bounded composition graph + state + capabilities + resources
evolution = variation + evaluation + selection + inheritance
```

This ontology minimizes foundational commitment and maximizes future
evolvability.

## 2. Evidence-Based Architectural Position

Recent harness research establishes that system architecture materially
affects capability independently of model weights. Agentic Harness
Engineering reports transferable gains primarily from tools, middleware,
and long-term memory rather than prompt editing. Evo-Harness reports
that externally grounded adaptation can improve future behavior while
self-generated feedback can make performance worse. Harness-native RL
systems such as LEGO-RL, Agent Lightning, and ClawGym II show that model
optimization can occur through the actual deployment harness while
preserving the harness as the environment-control system.

The next research frontier is therefore not simply stronger agents. It
is **controlled evolution of the structures that produce agents and
their behavior**.

AI4AI-Bench supplies an important boundary condition: changing a
learning algorithm itself remains much harder than improving prompts,
data, hyperparameters, tools, or surrounding engineering. This implies a
hierarchy of mutation power:

``` text
M0 runtime parameters
M1 runtime policies
M2 skills / procedural knowledge
M3 architecture and topology
M4 learning configuration
M5 model parameters
M6 learning algorithms
M7 evolutionary mechanisms
M8 experimental methodology
```

Each higher level should require stronger isolation, evidence, replay,
and independent authority.

## 3. Ontological Discipline

The principal conceptual risk is premature reification of current LLM
engineering concepts. `Agent`, `Planner`, `Critic`, `Reflection`,
`Debate`, `Supervisor`, and `Swarm` are useful abstractions, but none
has yet earned immutable primitive status.

A primitive should enter the foundational ontology only if it is
recurrent across qualitatively different architectures, cannot be
economically reconstructed from existing primitives, has stable typed
semantics, has measurable causal/resource behavior, remains meaningful
outside a particular model provider, and improves experimental
attribution.

This yields four conceptual levels:

``` text
Invariant mechanism
→ primitive operation
→ reusable derived structure
→ contingent phenotype
```

Persistent storage is a mechanism. Retrieval is a selection operation
over stored artifacts. Episodic memory is a derived system. A
memory-specialist agent is a phenotype. This distinction determines what
can safely evolve.

## 4. Intelligence as Adaptive Organization Under Constraints

Intelligence should be operationalized relationally:

``` text
Capability = f(system, environment, history, resources, objective)
```

Architectural complexity is not evidence of intelligence. A more
intelligent system should expand its attainable capability frontier over
task difficulty, novelty, compute, time, memory, uncertainty, and tool
availability.

Evaluation should therefore estimate **capability surfaces**, not merely
leaderboard scores. A system that gains two benchmark points by spending
ten times the compute may represent a regression for many operating
regimes.

Useful dimensions include:

``` text
correctness
generalization
robustness
learning efficiency
adaptability
autonomy
latency
tokens
money
memory
recovery
safety
reproducibility
```

Fitness is consequently vector-valued and should generally be handled
through Pareto analysis.

## 5. Immutable Kernel as Computational Physics

The protected kernel should behave less like a hard-coded cognitive
system and more like computational physics plus constitutional law.

It enforces:

``` text
identity
authority
capability attenuation
resource conservation
artifact identity
event integrity
provenance
sandbox isolation
rollback
evaluator independence
promotion authority
```

Examples of invariants:

``` text
Capabilities(child) ⊆ Capabilities(parent)
AllocatedCompute ≤ AvailableCompute
CommittedMoney ≤ Budget
HistoricalEventID is immutable
Artifact content identity is immutable
Candidate ≠ evaluator
Candidate ≠ promotion authority
```

Evolution may search freely inside these laws but cannot rewrite them.

## 6. Primitive Runtime

### Observation

Transforms external or internal state changes into typed observations.
Sources include tools, environments, models, evaluators, resource
monitors, messages, and internal execution state.

### Representation

Transforms information into artifacts suitable for future computation:
context projections, summaries, embeddings, symbolic structures, graphs,
hypotheses, plans, or compressed state.

### Selection

Chooses among alternatives under constraints. Attention, routing, action
selection, tool choice, task scheduling, retrieval, and delegation are
all selection problems.

### Action

An effect should be decomposed:

``` text
proposal → authorization → execution → observation
```

The model or adaptive process proposes. Deterministic authority decides.
The sandbox executes.

### Storage and Retrieval

Storage persists artifacts. Retrieval selects stored artifacts under
context, scope, policy, and budget. Memory is derived from these plus
lifecycle policies.

### Communication

Transfers typed information among bounded processes. Communication
channels must preserve sender, recipient, provenance, authority context,
cost, and causal position.

### Resource Allocation

Tokens, money, time, CPU/GPU, context, storage, network access, tool
calls, and parallel workers are explicit resources. Scarcity is
essential because rational metacognition requires trade-offs.

### Evaluation

Maps execution evidence into a multidimensional fitness vector.
Evaluation is a primitive mechanism, but evaluator authority remains
external to candidates.

### Variation

Produces descendants through parameter mutation, structural mutation,
replacement, synthesis, recombination, specialization, or program
transformation.

### Composition

Connects primitive instances through typed interfaces to produce
executable graphs.

### Scheduling

Controls activation, concurrency, dependency resolution, interruption,
and resource distribution. Scheduling mechanism belongs to runtime;
scheduling strategy can evolve.

## 7. Typed Composition and Causality

Ordinary workflow DAGs are insufficient for scientific evolution. Graph
edges should distinguish at least:

``` text
DATA
CONTROL
AUTHORITY
RESOURCE
```

The system should additionally distinguish observed causality from mere
dependency.

Architecture search over untyped graphs creates enormous, poorly
attributable search spaces. Typed graphs constrain invalid mutations and
make interventions interpretable.

A composition graph therefore represents not merely "what calls what,"
but how information, control, authority, and resources propagate through
the system.

## 8. Metacognition as Monitoring and Control

Metacognition should not be implemented as a prose instruction to
"reflect." Cognitive science distinguishes monitoring from control, and
confidence itself is an imperfect inference.

The computational system requires:

``` text
PerformanceMonitor
UncertaintyEstimator
SelfModel
StrategyStatistics
ResourceMonitor
ValueOfComputationPolicy
MetaControlPolicy
```

A SelfModel estimates contextual competence:

``` text
P(success | model, task_class)
P(tool_failure | operation)
P(skill_utility | environment)
P(memory_reliability | source)
ExpectedCost(strategy | task)
```

These predictions can be calibrated against external outcomes.

The core invariant remains:

``` text
internal belief ≠ evidence
reflection ≠ truth
self-evaluation ≠ external evaluation
memory ≠ validated knowledge
```

Reflection creates candidate hypotheses. External interaction and
evaluation determine persistence.

## 9. Value of Computation

Reasoning itself consumes resources and should be modeled as an action.

Before additional computation, the controller estimates approximately:

``` text
ExpectedUtility(next computation)
− ExpectedUtility(stop now)
− ComputationCost
```

Possible meta-actions include:

``` text
continue
stop
retrieve
simulate
verify
switch strategy
delegate
increase compute
reduce compute
ask for information
abandon hypothesis
```

This provides a principled path from "reflection" toward bounded
rational meta-reasoning.

## 10. Neuroscience: Computationally Useful Abstractions

Biology should provide candidate mechanisms, not architectural
templates.

### Replay and consolidation

Hippocampal replay motivates:

``` text
online experience
→ episodic trajectory
→ offline replay
→ pattern extraction
→ consolidation
→ modified future behavior
```

The engineering implication is asynchronous consolidation over completed
trajectories rather than permanent injection of history into context.

### Predictive processing

Prediction-error architectures motivate explicit:

``` text
prediction
observation
error
update
```

Prediction error can drive anomaly detection, curiosity, world-model
updates, calibration, and exploration. Strong universal claims about
predictive processing remain scientifically contested and should not be
encoded as foundational truth.

### Executive gating

Basal-ganglia analogies are useful only at the abstraction:

``` text
candidate processes → gating → scarce execution channels
```

This maps to selection and resource allocation.

### Homeostasis

Long-running systems need controlled internal variables:

``` text
memory growth
resource consumption
latency
failure rate
risk
population size
```

Homeostatic controllers keep these within viable ranges.

## 11. Genotype, Development, and Phenotype

A central long-range hypothesis is that evolving completed architectures
may be inferior to evolving compact developmental rules.

``` text
ArchitectureGenome
+ DevelopmentProgram
+ Environment
→ ExecutablePhenotype
```

Development can create repeated motifs, conditional specialists,
hierarchical structure, parameter sharing, graceful scaling, and
environment-dependent organization.

For example, a developmental rule may instantiate parallel specialists
only when the task dependency graph exposes sufficient parallelism, or
attach a verifier only when uncertainty and risk exceed thresholds.

This idea should be tested against direct graph mutation rather than
assumed.

## 12. Evolutionary Dynamics

Optimization and open-ended evolution are not equivalent. Strong
objective pressure may rapidly improve one metric while collapsing
diversity and eliminating future stepping stones.

The population model should therefore track:

``` text
genotypic diversity
phenotypic diversity
behavioral diversity
lineage depth
niche occupancy
resource distribution
mutation distribution
extinction rate
innovation rate
```

Quality-Diversity, MAP-Elites, novelty search, POET, evolutionary
strategies, genetic programming, population-based training, Bayesian
optimization, and MCTS should be treated as interchangeable search
policies over different representations and budgets.

Recent Quality-Diversity evidence is particularly instructive:
preserving stepping stones can work mechanistically without guaranteeing
better endpoint fitness at a fixed evaluation budget.

## 13. Neutral Evolution, Niches, and Exaptation

Neutral mutations can be strategically useful because they move
populations to new regions of architecture space. Selection should
optionally retain neutral descendants that introduce structural novelty,
behavioral novelty, compatibility, or new reachable mutation
neighborhoods.

Niches prevent one architecture from monopolizing the population.
Candidate niches may include low-cost, high-assurance, long-horizon,
local-only, coding, research, and high-parallelism solvers.

Exaptation should be explicitly detected through lineage. A procedure
evolved for repository navigation that later improves literature search
represents a stronger form of generalization than direct benchmark
optimization.

## 14. Multi-Agent and Collective Intelligence

Current evidence rejects the assumption that adding agents monotonically
increases capability. Multi-agent architectures help when tasks expose
parallelizable independent work and coordination overhead is lower than
the gained parallelism. They can substantially hurt sequential
reasoning, amplify errors, and dilute expertise.

Therefore organizational topology should be an evolvable phenotype:

``` text
single process
→ planner/executor
→ hierarchy
→ expert panel
→ peer graph
→ market
→ swarm
→ dynamic topology
```

The routing system should condition topology on task dependencies,
expertise distribution, uncertainty, communication cost, and budget.

"Agent count" should never be treated as a capability metric.

## 15. Memory as an Evidence-Weighted Ecology

The difficult memory problem is not storage but selection:

``` text
what to encode
what to consolidate
what to retrieve
what to trust
what to forget
what to generalize
```

Memory should contain distinct classes:

``` text
TransientState
WorkingMemory
Episode
SemanticKnowledge
Procedure
Skill
WorldModel
SelfModel
ExperimentalMemory
```

Semantic claims preserve supporting and contradicting evidence rather
than overwriting each other.

A durable memory artifact should contain:

``` text
provenance
scope
confidence
support
contradictions
activation conditions
expiry/decay
security state
promotion state
```

Persistent memory is also a security surface. Memory poisoning research
shows that apparently benign stored content can alter future behavior,
including through contextual and compositional attacks. Durable state
therefore requires both write-time and retrieval-time defenses.

## 16. Consolidation, Compression, and Abstraction

Trajectory knowledge can be progressively compressed:

``` text
raw events
→ episode
→ recurring pattern
→ procedure
→ skill
→ schema
→ predictive model
```

Every abstraction should preserve links to supporting evidence.

Information-theoretic concepts provide useful engineering signals.
Predictive information asks how much stored past information predicts
future relevant outcomes. Minimum Description Length encourages compact
explanatory structures. Information bottleneck reasoning motivates
retaining task-relevant information while discarding irrelevant history.

These are optimization principles, not definitions of intelligence.

A useful operational criterion for an abstraction is:

> Does it compress many experiences while preserving or increasing
> predictive and decision utility on future environments?

## 17. Skill Evolution

Skills should be versioned procedural artifacts rather than permanent
prompt text.

``` text
Trajectory
→ Pattern Extraction
→ Candidate Procedure
→ Candidate Skill
→ External Validation
→ Held-Out Evaluation
→ Promotion / Quarantine / Rejection
```

Skill utility is conditional:

``` text
Utility(skill | model, architecture, environment, task distribution)
```

The Skill Registry therefore records compatibility and negative
evidence, not merely a global quality score.

Skill activation should be separate from skill existence. Large
libraries should be paged through lexical, structural, semantic, or
learned routing rather than permanently resident in context.

## 18. PrimitiveGenome

A primitive genome should encode:

``` text
type
implementation reference
parameters
interfaces
dependencies
capability requirements
resource model
compatibility
version
lineage
allowed mutation operators
```

Primitive definitions and primitive instances remain separate so one
definition can produce many parameterized runtime instances.

## 19. ArchitectureGenome

The architecture genome should encode:

``` text
STRUCTURE
nodes, edges, hierarchy, communication channels

POLICY
routing, scheduling, retrieval, verification

STATE
memory topology and persistent variables

RESOURCES
budgets, concurrency, quotas

AUTHORITY
capabilities and delegation

DEVELOPMENT
rules constructing runtime topology

ADAPTATION
online update mechanisms

LINEAGE
parents and mutation history
```

Evaluator references may be included for reproducibility, but candidate
genomes never control evaluator authority.

## 20. Causal Trajectories

Every execution must reconstruct:

``` text
Model
+ Architecture
+ PrimitiveGraph
+ Policies
+ Memory
+ Tools
+ Environment
+ Evaluators
+ Seeds
+ Budgets
→ EventGraph
→ Outcome
```

Canonical events include observations, state changes, selections, model
calls, effect proposals, authorizations, tool calls, memory
reads/writes, messages, mutations, evaluations, resource deltas, and
termination.

Shared histories should be prefix-addressed and immutable so branches
reference common ancestry rather than duplicate it.

The trajectory is simultaneously:

``` text
debug record
scientific evidence
training sample
cost record
skill source
evolution evidence
causal graph
replay object
```

## 21. Causal Credit Assignment

Overall improvement does not prove that any individual mutation was
beneficial.

The Meta-Harness should use interventions:

``` text
remove component
replace with incumbent version
freeze component
swap component across architectures
alter only component
```

For interacting components, evaluate pairwise effects or sampled
coalition contributions. Full Shapley attribution may be prohibitively
expensive, but approximate marginal contribution can reveal important
interactions.

Promotion confidence should increase through a replication hierarchy:

``` text
same-seed replay
→ different seeds
→ held-out tasks
→ different environments
→ different model families
→ temporal re-evaluation
```

## 22. Meta-Harness as Automated Science

The Meta-Harness should be primarily an experimental controller:

``` text
Evidence Collector
→ Failure/Opportunity Detector
→ Hypothesis Generator
→ Mutation Generator
→ Experiment Designer
→ Candidate Builder
→ Benchmark Runner
→ Independent Evaluator
→ Statistical Comparator
→ Promotion Controller
→ Registry
```

The governing invariant is:

``` text
system under evaluation
≠ evaluator
≠ promotion authority
```

A hypothesis is a first-class versioned object containing observations,
mechanism, intervention, predicted metric effects, and falsification
conditions.

The computational scientific method becomes:

``` text
Observe
→ Hypothesize
→ Intervene
→ Experiment
→ Measure
→ Compare
→ Accept / Reject / Inconclusive
→ Replicate
```

## 23. Mutation Privilege Lattice

Mutation power should determine required authority:

  -----------------------------------------------------------------------------
  Level             Surface                 Example           Control
  ----------------- ----------------------- ----------------- -----------------
  M0                runtime parameters      retrieval top-k   automatic

  M1                runtime policy          routing           benchmark gate

  M2                procedural knowledge    skill             evidence gate

  M3                architecture/topology   verifier branch   isolated
                                                              candidate

  M4                learning configuration  curriculum        training sandbox

  M5                model parameters        RL update         model registry

  M6                learning algorithm      new loss          hidden replay

  M7                evolutionary mechanism  mutation strategy independent
                                                              control

  M8                experimental            evaluator design  external
                    methodology                               governance
  -----------------------------------------------------------------------------

A system may propose higher-level mutations without possessing authority
to execute or promote them.

## 24. Open-Ended Evolution

Open-endedness cannot be equated with endless mutation. Artificial-life
research distinguishes change, novelty, complexity, and ecological
dynamics, and also demonstrates that systems can remain continuously
novel without producing meaningful functional innovation.

The framework should therefore track:

``` text
change potential
novelty potential
complexity potential
ecological potential
adaptive novelty
transfer
new niches
new affordance exploitation
exaptation
```

The strongest test of open-endedness is whether the system repeatedly
creates capabilities not directly specified in the original objective
and whether those capabilities remain useful across environments.

Agent/environment co-evolution is a promising mechanism because static
benchmarks impose a finite target. POET-like systems instead evolve
challenges and solvers together, preserving stepping stones that can
later unlock harder niches.

## 25. Emergence Requires Null Models

Emergence claims require explicit alternative explanations.

If two processes spontaneously specialize into search and verification,
possible causes include genuine adaptive specialization, role-label
bias, model differences, scheduler artifacts, or random early asymmetry.

Tests should include:

``` text
remove role labels
randomize identities
swap models
swap environments
replicate
ablate specialization
```

Only persistent, causally useful organization should be called emergent.

Likewise, an emergent communication protocol must demonstrably transmit
task-relevant information and improve outcomes relative to controlled
alternatives.

## 26. Evaluation and Fitness

Use a multidimensional `FitnessVector`:

``` text
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
novelty
```

Do not permanently scalarize this vector. Different deployment profiles
should select different points on a Pareto frontier.

Emergence signals include previously unsolved task classes, spontaneous
specialization, transferable abstractions, novel strategies, adaptive
topology, emergent communication, zero-shot transfer, and improved
learning efficiency.

Ordinary score optimization is not emergence.

## 27. Safety and Evolutionary Containment

Evolution creates failure modes absent from static systems:

``` text
reward hacking
evaluator gaming
privilege escalation
resource acquisition
uncontrolled replication
memory poisoning
catastrophic forgetting
monoculture
evolutionary instability
benchmark overfitting
```

Immutable boundaries include authority, sandbox enforcement, evaluator
separation, provenance, experiment isolation, resource ceilings,
promotion authority, audit logs, and rollback.

Population creation is budgeted through explicit leases. Environmental
errors never grant additional authority. Persistent memory receives
code-like security treatment.

## 28. Candidate Meta-Framework Architecture

``` text
┌───────────────────────────────────────────┐
│ Independent Evaluation Plane             │
│ benchmarks · statistics · hidden tests   │
│ replication · promotion authority        │
└──────────────────▲────────────────────────┘
                   │ evidence
┌──────────────────┴────────────────────────┐
│ Evolution / Learning Plane               │
│ populations · mutation · QD · RL         │
│ coevolution · meta-learning              │
└──────────────────▲────────────────────────┘
                   │ candidate genomes
┌──────────────────┴────────────────────────┐
│ Adaptation Plane                         │
│ skills · memory · routing · verification │
│ context · retrieval · policies           │
└──────────────────▲────────────────────────┘
                   │ compositions
┌──────────────────┴────────────────────────┐
│ Composition / Agent Plane                │
│ graphs · agents · teams · organizations  │
└──────────────────▲────────────────────────┘
                   │ primitive operations
┌──────────────────┴────────────────────────┐
│ Primitive Runtime                        │
│ events · scheduler · gateway · sandbox   │
│ tools · artifacts · trajectories         │
└──────────────────▲────────────────────────┘
                   │ invariants
┌──────────────────┴────────────────────────┐
│ Immutable Kernel                         │
│ identity · authority · budgets ·         │
│ integrity · provenance · isolation       │
└───────────────────────────────────────────┘
```

## 29. Formal Data Model

The foundational data model should include:

``` text
PrimitiveDefinition
PrimitiveInstance
PrimitiveGenome
ArchitectureGenome
AgentDefinition
HarnessDefinition
EnvironmentDefinition
Hypothesis
Experiment
Trajectory
Event
Artifact
Skill
Memory
Evaluator
Mutation
Population
Generation
FitnessVector
Lineage
PromotionDecision
```

Every evolved artifact preserves:

``` text
parentage
mutation
environment
benchmark delta
resource delta
supporting evidence
negative evidence
promotion state
descendants
```

The Lineage Graph should support mutation, recombination, derivation,
and inspiration edges.

## 30. Minimum Viable Meta-Framework

The MVP should implement laboratory infrastructure before ambitious
cognition.

Required components:

``` text
Primitive Registry
Composition Graph
Canonical Event System
Trajectory Store
Model Gateway
Experiment Registry
Hypothesis Registry
Benchmark Runner
Evaluator Registry
Mutation Engine
Population Registry
Selection Engine
Skill Registry
Artifact Registry
Lineage Graph
Sandbox
Observability
```

Initially permit M0--M3 evolution only.

Protect:

``` text
kernel
security policy
evaluator authority
model weights
learning algorithms
evolutionary algorithm
experimental methodology
```

## 31. Top 10 Experiments

1.  **Primitive sufficiency:** build coding, research, and tool-use
    solvers from the minimal primitive vocabulary; promote a new
    primitive only if repeated architectures require the same
    irreducible mechanism.

2.  **Agent-boundary ablation:** compare explicit Agent objects with
    generic bounded composition graphs under equal compute.

3.  **Grounded metacognition:** compare no self-model, verbal
    reflection, and calibrated externally grounded self-models.

4.  **Replay/consolidation:** compare raw episodic retrieval, summaries,
    and offline trajectory-to-skill consolidation.

5.  **Topology evolution:** evolve single, planner/executor, hierarchy,
    peer, and specialist structures across tasks with different
    dependency graphs.

6.  **QD versus champion search:** compare sequential incumbent search,
    independent-root search, and MAP-Elites while measuring both
    endpoint fitness and stepping-stone use.

7.  **Skill ecology:** allow skill promotion, competition, decay,
    retirement, recombination, and contextual activation.

8.  **Agent/environment co-evolution:** implement a bounded POET-like
    task generator and measure adaptive novelty beyond a static
    curriculum.

9.  **Causal component attribution:** compare naïve architecture deltas
    against intervention-based attribution.

10. **Meta-evolution:** after M0--M3 stabilize, compare fixed mutation
    operators against adaptive and meta-agent-modified mutation
    procedures while keeping evaluation immutable.

## 32. Staged Evolution Roadmap

### Stage 1 --- Deterministic Harness

Establish canonical events, sandboxing, artifacts, model gateway,
trajectories, and reproducible execution.

**Falsification:** inability to reconstruct external effects.

### Stage 2 --- Adaptive Harness

Allow retrieval, memory, verification, context, routing, and skills to
adapt.

**Metric:** held-out transfer.

### Stage 3 --- Evolutionary Harness

Add populations, mutations, lineage, selection, and optional QD
archives.

**Falsification:** failure to beat strong search/random baselines under
equal budgets.

### Stage 4 --- Meta-Harness

Automate hypothesis generation, experiment design, comparison,
promotion, and rollback.

**Metric:** validated improvement per experiment budget.

### Stage 5 --- Population Intelligence

Evolve specialization, topology, heterogeneous models, and
communication.

**Falsification:** no advantage over the best single architecture after
compute matching.

### Stage 6 --- Harness-Native Learning

Export prefix-addressed trajectories to external SFT/DPO/RL systems
while preserving deployment semantics.

### Stage 7 --- Open-Ended Evolution

Add environment populations, niches, novelty, coevolution, and adaptive
curricula.

**Falsification:** diversity increases while functional capability
remains flat.

### Stage 8 --- Meta-Learning Evolution

Permit controlled mutation of learning strategies and eventually
learning algorithms.

**Falsification:** apparent gains reduce to data, compute, or
hyperparameter tuning.

## 33. Scientific Infrastructure

Every experiment should generate a reproducibility manifest containing
code revision, architecture genome, model versions, environment hash,
evaluator hash, seeds, budgets, and artifact manifest.

Maintain an immutable experiment ledger:

``` text
hypothesis
candidate
control
results
statistics
promotion decision
later reversals
```

Failed experiments should remain available. Negative evidence prevents
repeated dead ends and becomes training data for future experiment
planners.

Registries should remain semantically distinct:

``` text
PrimitiveRegistry
ArtifactRegistry
SkillRegistry
ArchitectureRegistry
ModelRegistry
EnvironmentRegistry
EvaluatorRegistry
ExperimentRegistry
PopulationRegistry
```

while sharing common identity, provenance, and artifact infrastructure.

## 34. Falsification Program for the Central Hypothesis

The project should actively attempt to disprove its own thesis.

**Primitive ceiling:** if sophisticated systems repeatedly require
irreducible hard-coded cognitive modules, the primitive vocabulary is
incomplete.

**Evolution adds no value:** if automated architecture evolution fails
to outperform strong manual/search baselines under equal budgets,
evolutionary complexity is unjustified.

**No transfer:** if evolved improvements remain benchmark-local, the
process demonstrates optimization rather than generalized intelligence
improvement.

**Complexity regression:** if increasingly complex architectures lose to
minimal loops after controlling model and compute, selection should
favor simplification.

**Nonfunctional novelty:** if novelty and diversity rise while adaptive
capability does not, open-ended evolution is producing decorative
complexity.

**Meta-evolution instability:** if evolving mutation procedures causes
collapse, evaluator exploitation, or irreproducibility, meta-evolution
must remain constrained.

A scientific Meta-Framework is meaningful only if observations can force
substantial revision or rejection of its hypotheses.

## 35. Core Architectural Invariants

``` text
model proposal ≠ authority
reflection ≠ evidence
memory ≠ validated knowledge
candidate ≠ evaluator
candidate ≠ promotion authority
provider serialization ≠ canonical state
mutation → new versioned artifact
child capability ⊆ parent capability
resource allocation ≤ available budget
every external effect is causally attributable
every promoted adaptation has evidence
```

## 36. Final Technical Position

The target is not maximum architectural complexity. It is **maximum
evolvability per unit of foundational commitment**.

The kernel supplies computational laws. The runtime supplies mechanisms.
Composition produces cognitive organizations. Adaptation modifies their
behavior. Evolution modifies their structure. Learning modifies
predictive and action policies. Meta-evolution modifies the procedures
generating future adaptations. Independent evaluation determines whether
any of these changes actually improve capability.

A successful substrate must allow future systems to discover that
concepts currently considered fundamental---agent boundaries, planners,
critics, fixed memory classes, hierarchical teams, explicit reasoning
phases---are unnecessary, replaceable, or should be reorganized in ways
not anticipated by the framework designers.

The strongest operational principle is therefore:

> **Provide computational laws, resources, memory, interaction,
> variation, environmental pressure, and scientific feedback; allow
> useful intelligence to occupy and progressively reorganize the
> resulting design space.**

The long-term objective is not a system that merely raises its benchmark
score. It is a system that becomes progressively better at **discovering
reusable ways to become better**, while retaining causal evidence
explaining why those changes worked, demonstrating transfer beyond the
optimization distribution, and remaining bounded by invariants it cannot
rewrite.

------------------------------------------------------------------------

# Bibliography and Primary Research Basis

The report is grounded in the preceding 24 August research corpus and
its primary-source bibliography, including work on Agentic Harness
Engineering, AEvo, MetaSkill-Evolve, Evo-Harness, AI4AI-Bench, Loreley,
POET, MAP-Elites, MODES, open-ended artificial life, metacognition and
confidence, hippocampal replay and systems consolidation, predictive
information, MDL, information bottleneck, MAML, learned optimizers,
Shapley-style credit assignment, multi-agent scaling, memory poisoning,
SWE-agent, OpenHands, Codex safety architecture, and Aider.

Key direct references:

-   Agentic Harness Engineering --- https://arxiv.org/abs/2604.25850
-   Harnessing Agentic Evolution / AEvo ---
    https://arxiv.org/abs/2605.13821
-   MetaSkill-Evolve --- https://arxiv.org/abs/2607.05297
-   Evo-Harness --- https://arxiv.org/abs/2608.15071
-   AI4AI-Bench --- https://arxiv.org/abs/2608.20318
-   Loreley --- https://arxiv.org/abs/2608.19703
-   POET --- https://arxiv.org/abs/1901.01753
-   MAP-Elites --- https://arxiv.org/abs/1504.04909
-   MODES --- https://doi.org/10.1162/artl_a_00280
-   Metacognition and Confidence ---
    https://doi.org/10.1146/annurev-psych-022423-032425
-   Predictive Information --- https://arxiv.org/abs/cond-mat/9902341
-   MAML --- https://proceedings.mlr.press/v70/finn17a.html
-   SWE-agent --- https://arxiv.org/abs/2405.15793
-   OpenHands Software Agent SDK ---
    https://github.com/OpenHands/software-agent-sdk

## Research Priority for the Next Cycle

The highest-value unresolved question is **developmental architecture
evolution**: whether indirect encodings, graph grammars, morphogenetic
rules, HyperNEAT-like representations, neural cellular automata, and
program-generating programs can produce substantially more evolvable
computational organizations than direct architecture-graph mutation.

Closely behind it are value-of-computation metareasoning, formal
open-endedness metrics for software-agent populations, evolutionary
major transitions, causal architecture attribution, learned routing,
computational ecologies, and internal AI4AI-style benchmarks capable of
separating improvements in execution, data, learning configuration,
model parameters, and learning algorithms.
