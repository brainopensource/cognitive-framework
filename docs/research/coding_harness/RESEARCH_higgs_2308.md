# 2308 Research Harness --- Technical Implications for AETHER / Vanguard

**Date:** 2026-08-23\
**Purpose:** Convert the 23 August agentic-harness research into
concrete architectural decisions, implementation requirements,
experiments, and development sequencing for a reusable Harness Builder
and future Meta-Harness.

------------------------------------------------------------------------

## 1. Executive Thesis

The 23 August research materially sharpens the architecture around one
principle:

> **Execution, adaptation, and learning must be separable planes
> connected by causal evidence, not collapsed into one self-modifying
> agent loop.**

The most relevant research signals are:

1.  **Evo-Harness:** externally grounded feedback outperforms model
    self-judgment for evolving reusable harness knowledge.
    Self-generated feedback can degrade performance.
2.  **ClawGym II:** model optimization can occur through an existing
    harness by intercepting model calls and reconstructing trajectories,
    without moving the environment loop into the trainer.
3.  **AI4AI-Bench:** actual recursive algorithmic improvement is
    substantially harder than prompt, harness, data, or hyperparameter
    optimization; most current agents avoid changing the learning rule.
4.  **@skills:** procedural knowledge is becoming a context-allocation
    problem. Large skill libraries should be paged/retrieved rather than
    permanently injected.
5.  **DeepSeek Harness field failures:** provider serialization,
    reasoning channels, and tool-call ordering can corrupt semantics if
    the internal event representation is not canonical.
6.  **Terminal-Bench / long-horizon evaluation:** quality must be
    optimized jointly with cost, tokens, latency, verification
    expenditure, and resource consumption.

The practical consequence is that Vanguard should not implement
"self-improvement" as an introspective model that rewrites itself. It
should implement an **experimental control system**:

``` text
Execution
    ↓
Causal Trajectory
    ↓
External Evidence
    ↓
Candidate Adaptation
    ↓
Controlled Evaluation
    ↓
Promotion / Rejection / Inconclusive
```

This architecture creates a continuous path from the first Coding
Harness to procedural learning, automated harness engineering,
harness-native RL, and eventually algorithm-level experimentation
without requiring a rewrite of the substrate.

------------------------------------------------------------------------

# 2. The Three-Plane Architecture

The research supports an explicit separation into three planes.

``` text
┌──────────────────────────────────────────────┐
│ LEARNING PLANE                              │
│ model post-training, RL, algorithm research │
└───────────────────┬──────────────────────────┘
                    │ consumes trajectories
                    │ returns versioned models
┌───────────────────▼──────────────────────────┐
│ ADAPTATION PLANE                            │
│ skills, memory, retrieval, policy evolution │
│ candidate generation, experiment planning   │
└───────────────────┬──────────────────────────┘
                    │ proposes configuration
                    │ never grants authority
┌───────────────────▼──────────────────────────┐
│ EXECUTION PLANE                             │
│ kernel, runtime, tools, sandbox, budgets     │
│ canonical events, verification, effects     │
└──────────────────────────────────────────────┘
```

## 2.1 Execution Plane

This plane must remain deterministic enough to answer:

-   What happened?
-   Which component caused it?
-   Which authority permitted it?
-   What resources were consumed?
-   What evidence proves the outcome?

It owns mechanisms, not cognition.

Recommended trusted responsibilities:

``` text
Identity
Run lineage
Capability algebra
Budget accounting
Canonical event semantics
Artifact addressing
Effect mediation
Plugin lifecycle
Sandbox boundary
```

The execution plane should not decide whether a repository-search
strategy is intelligent, whether a skill is useful, or whether a model
should reflect. Those are policies.

## 2.2 Adaptation Plane

The adaptation plane changes *how* the substrate solves tasks without
changing the substrate's fundamental authority semantics.

Examples:

``` text
retrieval policy
context packing
compaction
verification strategy
model routing
retry policy
procedural skills
memory consolidation
multi-agent composition
search strategy
```

This is the correct initial home of the Meta-Harness.

## 2.3 Learning Plane

The learning plane changes the model or eventually the learning
algorithm itself.

Examples:

``` text
SFT
DPO
PPO / GRPO
trajectory-based RL
curriculum generation
model distillation
loss-function changes
optimizer changes
training-algorithm experiments
```

It should consume evidence emitted by the runtime rather than own
runtime semantics.

------------------------------------------------------------------------

# 3. Finding: Grounded Feedback Must Govern Adaptation

## 3.1 Research result

Evo-Harness reports a critical negative result: self-generated feedback
can perform worse than no harness evolution.

For Claude Opus 4.6:

  Feedback regime               CL-Bench   SWE-bench Lite
  --------------------------- ---------- ----------------
  No evolution                     29.54            63.67
  Self-generated feedback          27.96            61.67
  Minimal external feedback        29.86            67.33
  Grounded diagnostics             34.02            67.00

The architectural importance is larger than the exact benchmark values.

A language model's interpretation of its own trajectory is **not an
authoritative observation of success**.

## 3.2 Consequence

Reflection must have epistemic status equivalent to a hypothesis.

``` text
Model:
"I should always run X before Y."

        ↓

CandidateLesson
confidence = model-estimated
evidence = none

        ↓

Evaluator:
held-out executions
tests
resource measurements
failure analysis

        ↓

PromotedSkill / RejectedCandidate
```

Therefore:

``` text
reflection != memory
reflection != truth
reflection != promotion
```

## 3.3 Required artifact types

``` python
CandidateInsight
EvidenceRecord
SkillCandidate
SkillVersion
EvaluationResult
PromotionDecision
```

A candidate insight should carry provenance:

``` yaml
candidate_id: ci_...
source_run: run_...
source_events:
  - evt_...
claim: "..."
scope: repository | domain | global
confidence: 0.71
evidence_state: unverified
```

Promotion should create a different immutable artifact rather than
mutate the candidate in place.

## 3.4 What Vanguard should do

Implement the memory pipeline as:

``` text
Trajectory
→ Evidence Extraction
→ Candidate Insight
→ Candidate Skill
→ Held-Out Evaluation
→ Promotion Controller
→ Skill Registry
```

Do **not** initially implement:

``` text
Trajectory
→ Reflection
→ append to MEMORY.md
```

That architecture creates an uncontrolled positive-feedback loop.

------------------------------------------------------------------------

# 4. Finding: Trajectories Are the Central Scientific Asset

ClawGym II, LEGO-RL, Agent Lightning, AHE, and Evo-Harness independently
increase the value of complete trajectories.

The trajectory is no longer merely debugging telemetry. It is
simultaneously:

``` text
debugging record
benchmark evidence
cost record
causal graph
training sample
skill-generation source
harness-evolution evidence
reproducibility artifact
```

## 4.1 Required event envelope

A useful minimum is:

``` rust
EventEnvelope {
    event_id,
    run_id,
    parent_event_id,
    logical_time,
    wall_time,
    event_type,
    actor_id,
    component_id,
    payload_ref,
    input_artifact_refs,
    output_artifact_refs,
    budget_delta,
    capability_context,
}
```

Large payloads should not be duplicated into the event stream. Store
them content-addressably and reference them.

## 4.2 Run identity

Every run should freeze:

``` text
HarnessDefinition ID
Model ID
Provider ID
Model capability profile
Prompt/system artifact IDs
Tool schema versions
Search policy version
Context policy version
Compaction policy version
Verification policy version
Sandbox profile
Evaluator version
Budget profile
```

Otherwise future experiments cannot distinguish a model improvement from
a harness/configuration change.

------------------------------------------------------------------------

# 5. Finding: Prefix-Addressed Trajectories Solve Two Problems at Once

ClawGym II reconstructs model-call trajectories as prefix trees for RL.

This is also the correct storage primitive for multi-agent execution.

Consider:

``` text
Parent:
A → B → C

Child 1:
A → B → C → D → E

Child 2:
A → B → C → F → G
```

A naïve transcript architecture stores the shared prefix three times.

A persistent trajectory graph stores:

``` text
A
└── B
    └── C
        ├── D
        │   └── E
        └── F
            └── G
```

## 5.1 Why this matters

This reduces:

-   duplicated disk state;
-   duplicated serialization;
-   copied compacted contexts;
-   memory amplification;
-   ambiguity in parent/child lineage.

It also creates a natural RL representation because divergence points
become explicit.

## 5.2 Recommended structure

``` rust
TrajectoryNode {
    id,
    parent_id,
    event_segment_ref,
    state_digest,
}
```

A child run receives:

``` rust
SpawnLease {
    parent_node,
    context_projection,
    capability_set,
    token_budget,
    money_budget,
    time_budget,
    storage_budget,
}
```

It does **not** receive an independently copied parent transcript.

------------------------------------------------------------------------

# 6. Finding: The Model Gateway Should Become a First-Class Runtime Seam

Harness-native RL papers converge on interception at the model boundary.

Therefore all inference should flow through:

``` text
Runtime
  ↓
ModelGateway
  ↓
ProviderAdapter
  ↓
Provider
```

The gateway is not merely a convenience wrapper.

It should own cross-provider inference semantics:

``` text
request identity
provider capability negotiation
model identity
retry metadata
cache metadata
token accounting
cost accounting
latency
raw response
canonical response
trajectory linkage
```

## 6.1 Why this matters now

Even without RL, this gives:

-   deterministic mockability;
-   provider substitution;
-   benchmark replay;
-   cache experiments;
-   cost measurement;
-   failure injection;
-   trace correlation.

Later, an external trainer can intercept exactly this seam:

``` text
Harness → ModelGateway → Training Proxy → Policy
```

No kernel redesign is required.

------------------------------------------------------------------------

# 7. Finding: Provider Wire Formats Must Never Define Internal Semantics

DeepSeek Harness reports illustrate a class of adapter failure where
provider serialization changes causal ordering or event classification.

The internal model must therefore be canonical.

``` text
Canonical Event Graph
        │
        ├── OpenRouter serializer
        ├── OpenAI serializer
        ├── Anthropic serializer
        ├── local-model serializer
        └── UI renderer
```

Not:

``` text
Provider JSON
    ↓
becomes authoritative runtime state
```

## 7.1 Canonical message algebra

At minimum:

``` text
SystemInstruction
UserMessage
AssistantText
ReasoningSegment
ToolCall
ToolObservation
RuntimeEvent
EvaluatorObservation
```

A provider adapter should be approximately a pure function:

``` text
CanonicalConversation
        ↓
serialize(provider_capabilities)
        ↓
ProviderRequest
```

and:

``` text
ProviderResponse
        ↓
parse + validate
        ↓
CanonicalEvents
```

## 7.2 Important invariant

If:

``` text
AssistantToolCall → ToolObservation
```

is causal in the canonical graph, provider serialization cannot reorder
a user message between them unless that provider's semantics explicitly
require a transformation that preserves equivalence.

This should be contract-tested.

------------------------------------------------------------------------

# 8. Finding: Skills Need Paging, Versioning, and Compatibility Evidence

The skill ecosystem is scaling faster than context windows should be
expected to absorb.

The correct abstraction is:

``` text
SkillArtifact
≠
SkillActivationPolicy
```

A skill can exist without being active.

## 8.1 Proposed skill schema

``` yaml
skill_id: skill_python_test_localization
version: 7

scope:
  domain: software_engineering
  languages: [python]

artifact:
  content_ref: sha256:...
  dependencies: [...]

activation:
  tags: [...]
  lexical_terms: [...]
  embedding_ref: ...
  auto_trigger_eligible: true

requirements:
  capabilities:
    - filesystem.read
    - shell.execute

evidence:
  evaluations: [...]
  compatible_models: [...]
  incompatible_models: [...]

state:
  candidate | promoted | quarantined | deprecated
```

## 8.2 Retrieval pipeline

``` text
Task
 ↓
cheap lexical / structural filter
 ↓
candidate skill IDs
 ↓
semantic reranking
 ↓
policy gate
 ↓
load selected skill bodies
 ↓
Context Compiler
```

Only selected skill content enters the model context.

## 8.3 Compatibility is contextual

Evo-Harness indicates that a skill useful with one solver/model can fail
to help another.

Therefore the score should approximate:

``` text
Utility(skill | model, harness, task_distribution)
```

rather than:

``` text
Utility(skill)
```

This means the Skill Registry needs compatibility evidence, not a single
global quality number.

------------------------------------------------------------------------

# 9. Finding: Self-Improvement Requires a Mutation Taxonomy

AI4AI-Bench demonstrates why "the system improved itself" is
scientifically insufficient.

We must identify **what changed**.

Recommended taxonomy:

  Class   Mutation surface           Example
  ------- -------------------------- ------------------------------
  M0      Runtime configuration      token budget
  M1      Runtime policy             retrieval top-k
  M2      Procedural knowledge       debugging skill
  M3      Harness composition        verification plugin
  M4      Training configuration     curriculum
  M5      Model parameters           RL/SFT
  M6      Learning algorithm         loss/update rule
  M7      Experimental methodology   experiment-generation policy

This makes improvement attribution explicit.

## 9.1 Promotion strength should increase with mutation power

``` text
M0/M1
→ cheap benchmark

M2/M3
→ held-out benchmark + compatibility tests

M4/M5
→ isolated training + benchmark suite

M6
→ hidden evaluator + clean replay from scratch

M7
→ independent evaluator and strict authority separation
```

The Meta-Harness should initially operate only on M1--M3.

------------------------------------------------------------------------

# 10. Meta-Harness as Experimental Control System

The Meta-Harness should not be a privileged super-agent.

It should be a composition of ordinary components operating under
stricter experimental rules.

``` text
Evidence Extractor
      ↓
Candidate Generator
      ↓
Experiment Planner
      ↓
Candidate HarnessDefinition
      ↓
Benchmark Runner
      ↓
External Evaluator
      ↓
Statistical Comparator
      ↓
Promotion Controller
```

## 10.1 Candidate contract

``` yaml
candidate_id: hc_0142
base_harness: H_0041

mutation_class: M1

changes:
  retrieval.top_k:
    from: 12
    to: 6

hypothesis:
  success_rate_delta: ">= 0"
  token_delta: "< -8%"
  latency_delta: "< -5%"

falsification:
  success_rate_delta: "< -1pp"

benchmark:
  suite: coding_core_v3
  seed_set: ...

rollback:
  harness: H_0041
```

The hypothesis exists **before execution**.

This creates decision observability and prevents post-hoc
rationalization.

------------------------------------------------------------------------

# 11. Evaluation Must Be External but Also Versioned

External evaluation prevents the candidate from declaring itself
successful.

However, benchmark evolution shows evaluators can also contain defects.

Therefore:

``` text
Evaluator != oracle
```

Every result must reference:

``` text
evaluator_id
evaluator_version
test_suite_hash
environment_hash
resource_profile
```

If evaluator v3 fixes a benchmark defect, historical results remain
interpretable.

## 11.1 Outcome algebra

Avoid Boolean-only results.

``` text
PASS
FAIL
PARTIAL
INCONCLUSIVE
INFRA_FAILURE
SECURITY_FAILURE
BUDGET_EXHAUSTED
```

This prevents infrastructure failures from contaminating capability
measurements.

------------------------------------------------------------------------

# 12. Verification Should Be Cost-Aware

Long-horizon benchmark observations indicate agents can waste
substantial compute repeatedly executing full test suites.

Verification should therefore be a scheduler.

``` text
Patch
 ↓
Static checks
 ↓
Targeted unit tests
 ↓
Changed-area tests
 ↓
Integration tests
 ↓
Full suite
```

Escalation depends on:

``` text
change scope
dependency graph
risk
previous failures
test cost
remaining budget
```

## 12.1 Verification policy interface

``` python
class VerificationPolicy:
    def next_checks(
        self,
        change_set,
        evidence,
        budget,
        dependency_graph,
    ) -> list[TestAction]:
        ...
```

This remains replaceable policy, not kernel logic.

------------------------------------------------------------------------

# 13. Metrics: Optimize a Vector, Not a Leaderboard Number

Terminal-Bench economics show large cost differences among
high-performing systems.

The substrate should preserve raw metrics:

``` text
task_success
partial_success
cost_usd
input_tokens
output_tokens
cached_tokens
wall_clock
model_latency
tool_latency
tool_calls
failed_tool_calls
retries
spawn_count
peak_context
compactions
artifact_bytes
peak_memory
sandbox_startup
tests_executed
verification_time
security_violations
```

Then compute profiles:

``` text
MaxQuality
Balanced
LowCost
LowLatency
LocalOnly
HighAssurance
```

A Meta-Harness should search Pareto fronts rather than hard-code one
universal weighted objective.

------------------------------------------------------------------------

# 14. Recommended Component Boundaries

## Kernel

Keep small:

``` text
identity
authority
budget conservation
canonical event semantics
effect mediation
artifact identity
plugin lifecycle
```

## Runtime

``` text
scheduler
model gateway
tool executor
sandbox
context compiler
trajectory recorder
verification engine
```

## Replaceable policy

``` text
planning
retrieval
search
AST strategy
compaction
memory
skills
retry
model routing
verification policy
multi-agent topology
```

## Meta-Harness

``` text
evidence extraction
candidate generation
skill compilation
experiment planning
harness mutation
comparison
promotion
rollback
```

## External learning

``` text
trajectory conversion
prefix-tree construction
reward mapping
SFT / DPO / RL
model registry
training-algorithm experiments
```

------------------------------------------------------------------------

# 15. Immediate Development Priorities

## P0 --- Measurement spine

Implement first:

``` text
HarnessDefinitionID
RunID
EventID
ArtifactID
ModelCall
ToolCall
BudgetDelta
SpawnLineage
EvaluationResult
```

**Acceptance criterion:** a completed run can be reconstructed
sufficiently to explain every external effect and final evaluation.

## P0 --- Canonical event algebra

Provider adapters must not own durable semantics.

Contract-test:

``` text
canonical → provider → canonical
```

for representative tool-call and reasoning cases.

## P0 --- Model Gateway

Centralize:

``` text
provider negotiation
request identity
cache metadata
cost
tokens
latency
retry
trajectory linkage
```

This also enables cheap mocked OpenRouter/provider replay during harness
optimization.

## P0 --- Prefix-addressed trajectories

Implement immutable branchable histories before multi-agent fan-out
becomes deeply embedded.

## P0 --- Grounded knowledge promotion

Implement candidate/quarantine/promoted states for memories and skills.

No model-generated lesson should become globally authoritative without
evaluation.

------------------------------------------------------------------------

# 16. Near-Term Experimental Program

## Experiment A --- Grounded adaptation

Compare:

``` text
A. no persistent adaptation
B. self-reflection persistence
C. externally grounded skill persistence
```

Use identical model, task distribution, and budgets.

Primary hypothesis:

``` text
Utility(C) > Utility(A) >= Utility(B)
```

This tests whether Evo-Harness's central result transfers to our
substrate.

## Experiment B --- Harness effect

Fixed model, fixed tasks:

``` text
H0 minimal shell/editor
H1 Vanguard base
H2 + structured repository retrieval
H3 + verification scheduler
H4 + retrieval + verification
```

Measure the complete quality/cost vector.

## Experiment C --- Skill paging

Build 100--500 procedural skills and compare:

``` text
all resident
lexical retrieval
embedding retrieval
hybrid retrieval
explicit references
```

Measure activation precision, recall, tokens, latency, success, and
interference.

## Experiment D --- Spawn scaling

Run:

``` text
1 / 2 / 4 / 8 / 16 children
```

Measure physical storage and memory.

Desired property:

``` text
physical_growth ≈ unique_child_delta
```

not:

``` text
physical_growth ≈ children × parent_history
```

## Experiment E --- Verification economics

Compare:

``` text
full suite always
targeted-first escalation
model-selected tests
dependency-derived tests
```

Optimize success per verification second and success per dollar.

------------------------------------------------------------------------

# 17. What Not to Build Yet

The research argues against prematurely implementing several attractive
but weakly justified features.

Do not make these core primitives yet:

``` text
Swarm engine
Debate engine
Reflection engine
Global vector memory
Self-modifying kernel
Built-in RL trainer
Automatic unrestricted skill promotion
Evaluator plugins controlled by candidate agents
```

They can all be expressed later through ordinary policies, plugins,
artifacts, or external systems.

The substrate should first prove:

``` text
correct execution
causal observability
resource conservation
replaceability
evaluation integrity
```

------------------------------------------------------------------------

# 18. Development Sequence Toward Meta-Cognition

A credible progression is:

``` text
Stage 1
Reliable Coding Harness
        ↓
Stage 2
Typed causal trajectories
        ↓
Stage 3
Benchmark + external evaluation
        ↓
Stage 4
Grounded memory / skill compilation
        ↓
Stage 5
Automated harness experiments
        ↓
Stage 6
Meta-Harness candidate optimization
        ↓
Stage 7
Harness-native model post-training
        ↓
Stage 8
Cross-harness policy learning
        ↓
Stage 9
Training-algorithm experiments
        ↓
Stage 10
Recursive scientific experimentation
```

The key property is continuity: each stage consumes abstractions already
required by the previous stage.

Meta-Cognition therefore does not require a separate monolithic
"cognitive architecture." It can emerge as coordinated experimental
control over:

``` text
state
knowledge
policies
models
experiments
evaluations
```

------------------------------------------------------------------------

# 19. Definition of Self-Improvement for the Project

A useful formal definition is:

> A system self-improves when evidence generated by its executions
> causes a versioned change to a future decision-making component, and
> that change is independently demonstrated to improve an explicit
> objective under controlled evaluation.

This excludes:

``` text
longer prompts
unverified reflection
session-local adaptation
model claiming it learned
manual cherry-picking
benchmark leakage
```

It includes:

``` text
promoted skills
better retrieval policies
better verification policies
new harness compositions
post-trained models
improved training algorithms
```

provided the improvement is externally measured.

------------------------------------------------------------------------

# 20. Core Invariants

The following invariants should be treated as architecture-level
constraints.

### Invariant 1 --- Authority is deterministic

``` text
model proposal != permission
```

### Invariant 2 --- Evidence is external to reflection

``` text
model belief != evaluator evidence
```

### Invariant 3 --- Every adaptation is versioned

``` text
mutation → new artifact
```

Never silently overwrite the incumbent.

### Invariant 4 --- Every run is attributable

The system must reconstruct:

``` text
model + harness + policy + tools + environment + evaluator
```

### Invariant 5 --- Child authority is attenuated

``` text
Capabilities(child) ⊆ Capabilities(parent)
```

### Invariant 6 --- Resource budgets are conserved

A child cannot create budget unavailable to the parent.

### Invariant 7 --- Provider representation is not canonical state

Adapters serialize semantics; they do not define them.

### Invariant 8 --- Promotion is independent from candidate generation

The component proposing an improvement cannot unilaterally certify it.

------------------------------------------------------------------------

# 21. Final Architecture

The 23 August research does not justify expanding the trusted kernel. It
justifies making the surrounding system more experimentally powerful.

The target structure is:

``` text
                    ┌──────────────────────┐
                    │ External Trainer     │
                    │ SFT / DPO / RL / RSI │
                    └──────────▲───────────┘
                               │
                       trajectory export
                               │
┌────────────────────────────────────────────────────┐
│ META-HARNESS                                       │
│                                                    │
│ Evidence → Candidate → Experiment → Compare        │
│                         ↓                          │
│                   Promote / Reject                 │
└───────────────────────┬────────────────────────────┘
                        │ versioned policies
┌───────────────────────▼────────────────────────────┐
│ HARNESS / POLICY LAYER                             │
│ retrieval · skills · memory · planning · verify    │
│ routing · compaction · orchestration               │
└───────────────────────┬────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────┐
│ RUNTIME                                            │
│ scheduler · gateway · tools · sandbox · context    │
│ trajectories · verification                        │
└───────────────────────┬────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────┐
│ KERNEL                                             │
│ identity · authority · budgets · events · effects  │
│ artifacts · lifecycle                              │
└────────────────────────────────────────────────────┘
```

The scientific loop becomes:

``` text
Build
→ Execute
→ Observe
→ Measure
→ Hypothesize
→ Mutate
→ Re-run
→ Falsify
→ Promote
→ Generalize
```

That loop is the most important capability to construct. Once it exists,
memory, skills, multi-agent policies, model training, and eventually
algorithmic self-improvement become different experimental surfaces over
the same substrate rather than independent architectures.

------------------------------------------------------------------------

# 22. Decision Summary

For the next implementation cycle:

1.  **Build causal measurement before sophisticated cognition.**
2.  **Make Model Gateway a stable first-class seam.**
3.  **Store histories as immutable branchable trajectory graphs.**
4.  **Separate canonical events from provider serialization.**
5.  **Treat reflection as hypothesis, never evidence.**
6.  **Require external grounding before promoting memory or skills.**
7.  **Separate SkillArtifact from SkillActivationPolicy.**
8.  **Introduce explicit mutation classes.**
9.  **Keep Meta-Harness outside the trusted kernel.**
10. **Keep model training external but make trajectories
    training-ready.**
11. **Version evaluators and benchmark environments.**
12. **Optimize quality, cost, latency, tokens, and verification
    jointly.**
13. **Delay unrestricted self-modification until controlled lower-level
    adaptation is empirically reliable.**

The near-term objective is therefore not "build Meta-Cognition." It is
to build the **causal, evidentiary and experimental substrate from which
Meta-Cognition can be developed without sacrificing reproducibility,
authority boundaries, or scientific validity.**

------------------------------------------------------------------------

## Research Basis

This technical interpretation is based primarily on the 23 August
research corpus covering:

-   **AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for
    Recursive Self-Improvement** --- 2026.
-   **ClawGym II: Exploring Black-Box RL on Agent Harness** --- 2026.
-   **Evo-Harness: Context-to-Harness Skill Compilation for
    Self-Evolving Agents** --- 2026.
-   **@skills: Attention Is All You Have** --- 2026.
-   **Demystifying Agent Skills: Why They Work---Until They Don't** ---
    2026.
-   **DeepSeek Harness** architecture and current adapter-level field
    reports.
-   **Terminal-Bench 2.1** and **Terminal-Bench Challenges**.
-   Supporting continuity from **Agentic Harness Engineering**,
    **LEGO-RL**, **Agent Lightning v1.0**, and **EvoHarness-RL**.

The quantitative values in this document are paper-author-reported
unless explicitly originating from an audited benchmark. They should be
treated as evidence for architectural hypotheses, not as universal
performance guarantees.
