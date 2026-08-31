# AETHER CHIMERA — Full Code Manifest — Wave 3

## Delivery contract

- Branch: `feat/beta-release_electroweak-v091`
- Exact reconciled subject: `f242ced297216109736975376802f1e3dc4e29ce`
- Scope: backend only; frontend excluded.
- Focus: Search budgets, expected value of compute, capability boundaries, uncertainty, strategy genome, offline evolution, memory, skills, failures, scientific loop, and ToolScripts.
- Primary placement: `runtime/chimera`, `lab/chimera`, experience/artifact stores, and optional plugins.
- Status: implementation-ready manifest of complete changed classes, functions, schemas, policies, and tests.

## Code-first reconciliation

CHIMERA is lowered onto the existing Vanguard mechanisms rather than becoming a second framework. Existing authority remains in the kernel dispatch pipeline, capabilities, typed budgets, immutable events, artifact store, EpisodeEngine, guarded MetaController seam, context compiler, child runtime, model adapters, evaluator gateway, and SQLite-WAL store. Cognitive routing, blackboard projections, retrieval markets, symbolic solvers, search, local inference, learned ranking, and evolution are exterior ports/runtime/adapters or offline laboratory code. The kernel remains domain-blind and unchanged.

## Mandatory architectural interpretation

| PRD concept | Existing Vanguard owner | CHIMERA implementation boundary |
|---|---|---|
| Cognitive blackboard | ledger + artifacts + projections | derived projection; never mutable authority |
| Governor | `MetaController` + guarded consultation | deterministic exterior policy first |
| Mixture of Cognition | model/tool ports and routing | contextual router returning ordinary proposals |
| Local/graph/symbolic cortex | adapters | capability-declared optional plugins |
| Engineering search | child runtime + artifacts | bounded branches with attenuated budgets |
| Verification cortex | evaluator gateway + receipts | staged verification policy |
| Strategy genome | manifest/config artifacts | immutable, versioned, digest-bound values |
| Evolution lab | benchmark/evidence tooling | offline only; no task-time weight mutation |
| Learned skills | experience/artifact seams | evidence-gated admission and rollback |
| Atlas/LDA | `IndexPort` and optional adapters | optional provider; never authority |

## Non-negotiable implementation rules

1. No CHIMERA imports or domain vocabulary in `kernel/`.
2. No controller, model, bandit, GNN, solver, or capsule grants itself authority.
3. Every branch consumes a conserved child budget and returns artifacts/summaries.
4. Environment evidence outranks verbal confidence.
5. Learned routing begins in shadow mode and has a deterministic fallback.
6. Online adaptation changes routing/state only; weights and promoted skills change offline.
7. Heavy dependencies remain optional extras behind ports.
8. Every mechanism must beat a simpler baseline before promotion.

## Implementation specification and complete changed units

# 46. Critical-State Detector

A small local model or heuristic can mark checkpoints:

```text
first correct file localization
first reproduced failure
first useful test
first hypothesis with evidence
first patch changing failure mode
```

These become replay branch points.

---

# 47. Search Budget Controller

```python
@dataclass
class SearchBudget:
    max_nodes: int
    max_frontier_calls: int
    max_local_calls: int
    max_tool_calls: int
    max_wall_seconds: int
```

Search expands only while expected value remains positive.

---

# 48. Expected Value of Compute

Approximate:

```math
EVC(action) =
P(success_gain | action) * value_of_success
- compute_cost(action)
```

Use a heuristic/local predictor.

This is the basis for:

```text
Should we fork?
Should we use frontier?
Should we rerun?
Should we mutate?
```

---

# 49. Capability Boundary Model

For each model/worker maintain:

```python
CapabilityProfile(
    model_id,
    task_class_success,
    language_success,
    avg_cost,
    avg_latency,
    calibration,
    failure_modes,
)
```

Updated from verified trajectories.

---

# 50. Metacognitive Confidence

Do not use raw verbal confidence.

Calibrate confidence:

```text
model self-rating
+
historical accuracy for similar tasks
+
retrieval coverage
+
verification evidence
+
failure count
```

Example:

```math
C =
0.15 * self_report
+ 0.35 * historical_success
+ 0.20 * evidence_coverage
+ 0.30 * verification_signal
```

Weights initially heuristic.

Later learned.

---

# 51. Uncertainty Profile

```python
@dataclass(frozen=True)
class UncertaintyProfile:
    task_understanding: float
    localization: float
    implementation: float
    verification: float
    environment: float
```

This helps decide where to spend compute.

---

# 52. Meta-Cognitive Policy Example

```python
if uncertainty.localization > 0.7:
    route("retrieval_ensemble")

elif uncertainty.implementation > 0.8:
    route("frontier_hypothesis_search")

elif uncertainty.verification > 0.7:
    route("property_or_test_generation")

elif repeated_failure:
    route("trajectory_replay_or_branch")
```

---

# 53. Strategy Genome

CHIMERA represents its harness configuration as a versioned genome.

```python
@dataclass(frozen=True)
class StrategyGenome:
    genome_id: str

    prompt_refs: tuple[str, ...]
    skill_refs: tuple[str, ...]

    router_policy: str
    retrieval_policy: str
    search_policy: str
    verification_policy: str

    model_routes: Mapping[str, str]
    thresholds: Mapping[str, float]

    plugin_refs: tuple[str, ...]

    parent_genomes: tuple[str, ...]
    provenance: tuple[str, ...]
```

---

# 54. Why a Strategy Genome

It enables optimization over:

```text
prompts
skills
thresholds
routing
tool descriptions
search width
context ranking
verification depth
model allocation
```

without editing the kernel.

---

# 55. Genome Is Immutable

A production run uses a fixed genome ID.

```text
run
→ genome sha256:X
```

The run cannot silently rewrite it.

Mutations produce:

```text
sha256:Y
```

and require separate evaluation.

---

# 56. Online Adaptation vs Offline Evolution

## Online

Allowed during a task:

```text
bandit statistics
temporary hypotheses
temporary branch strategies
task-local scripts
task-local skills/capsules
```

## Offline

Required for permanent changes:

```text
prompt mutation
router weights
skill promotion
workflow topology
local model weights
threshold changes
```

This separation is mandatory.

---

# 57. Evolution Laboratory

Suggested package:

```text
vanguard/lab/chimera/
```

or equivalent existing `lab/` surface.

Components:

```text
dataset
experiment runner
genome registry
optimizer
evaluator
promotion gate
reports
```

This is not runtime kernel code.

---

# 58. Evolution Objective

Multi-objective score:

```math
J =
w_s * success
+ w_q * quality
- w_c * cost
- w_l * latency
- w_t * turns
- w_r * regression
- w_k * complexity
```

Include complexity penalty.

Otherwise evolution will produce bloated workflows.

---

# 59. Pareto Frontier

Do not collapse everything into one score.

Retain Pareto-optimal genomes across:

```text
success
cost
latency
complexity
```

Potential presets:

```text
chimera-fast
chimera-balanced
chimera-max
chimera-science
```

---

# 60. Prompt Optimization

Candidates:

```text
MIPRO-like Bayesian optimization
GEPA-like reflective prompt evolution
TextGrad-like textual gradient
simple evolutionary mutation
```

Prompt optimizer operates on:

```text
system instructions
tool descriptions
branch prompts
verifier rubrics
context compressor instructions
```

---

# 61. Prompt Optimization Dataset

Use:

```text
verified successful runs
verified failures
LAM scenarios
held-out internal tasks
```

Never optimize against only one benchmark split.

---

# 62. Textual Gradient Concept

```text
run fails
→ critique identifies prompt deficiency
→ optimizer assigns textual feedback to prompt component
→ mutated prompt generated
→ evaluate
```

Example:

```text
Failure:
agent repeatedly edits before reproducing bug.

Gradient:
system prompt should prioritize reproduction before modification
when a runnable failing test is available.
```

---

# 63. Bayesian Prompt Search

Parameters:

```text
instruction candidate
demo set
skill subset
thresholds
```

Surrogate predicts objective.

Next candidate chosen by acquisition function.

This is appropriate when evaluations are expensive.

---

# 64. Evolutionary Workflow Search

Genome mutation operations:

```text
add/remove skill
change model route
change retrieval provider weights
change search width
change stop threshold
change verifier depth
change prompt fragment
```

Crossover:

```text
parent A retrieval
+
parent B verification
```

Use only in offline lab.

---

# 65. Quality-Diversity Search

Do not only seek one best workflow.

Seek diverse strong strategies:

```text
strong Python repair
strong Rust repair
strong greenfield
strong math/code
strong large-repo retrieval
```

MAP-Elites-style quality-diversity could be explored later.

---

# 66. AFlow-Style Workflow Search

Represent operators as a graph:

```text
retrieve
generate
verify
branch
summarize
solver
```

Use MCTS offline to search graph topologies.

Do not run workflow MCTS inside every coding task.

---

# 67. Small Surrogate Models

The evolution lab can train a lightweight surrogate:

```text
genome features
task features
→ predicted success/cost
```

Model can be:

```text
XGBoost
small MLP
random forest
```

Choose by empirical calibration.

Do not force deep learning unnecessarily.

---

# 68. Self-Improvement Memory

Store three memory classes.

## Episodic

```text
what happened in a task
```

## Semantic

```text
repository/general facts
```

## Procedural

```text
what strategy worked
```

---

# 69. Procedural Skill Record

```python
@dataclass(frozen=True)
class Skill:
    skill_id: str
    description: str
    applicability: tuple[str, ...]
    procedure: str
    tool_requirements: tuple[str, ...]
    evidence_runs: tuple[str, ...]
    success_rate: float
    version: str
```

---

# 70. Skill Retrieval

Use task features and embeddings:

```text
task
→ retrieve top candidate skills
→ local reranker
→ compile compact skill context
```

Do not inject entire skill library.

This follows Retrieval-Augmented Execution principles where skill context itself must be compiled effectively. [R25]

---

# 71. Skill Admission

A skill becomes active only if:

```text
applicability match
confidence above threshold
token/complexity budget acceptable
```

---

# 72. Skill Promotion

Task-local strategy:

```text
successful ephemeral procedure
→ candidate skill
→ evaluation
→ promotion
```

Failed procedures remain useful as negative evidence.

---

# 73. Failure Taxonomy

CHIMERA should maintain a structured taxonomy.

```text
F01 task misunderstanding
F02 wrong repository region
F03 wrong symbol
F04 missing dependency context
F05 excessive context
F06 wrong hypothesis
F07 invalid patch
F08 incomplete patch
F09 regression
F10 test misunderstanding
F11 insufficient verification
F12 tool misuse
F13 environment failure
F14 looping
F15 premature completion
F16 model mismatch
F17 skill mismatch
F18 solver misuse
F19 search-budget waste
F20 stale memory
F21 retrieval miss
F22 branch selection error
```

---

# 74. Failure Classifier

Start heuristic.

Later train a local classifier.

```python
class FailureClassifier:
    def classify(
        self,
        state,
        events,
        verification,
    ) -> Distribution[FailureClass]:
        ...
```

Use probabilistic distribution rather than one forced label.

---

# 75. Failure-to-Intervention Map

```text
retrieval miss
→ alternate retriever / GNN / LDA

wrong hypothesis
→ counterexample branch

invalid patch
→ compiler/test repair

repeated failure
→ trajectory replay / alternate model

model mismatch
→ router update / escalation

insufficient verification
→ test generation / property checking
```

---

# 76. Counterfactual Reasoning

When stuck, generate:

```text
"If my current hypothesis were false, what observation should I expect?"
```

Then run the cheapest discriminating test.

This turns reflection into experimental design.

---

# 77. Information-Gain Probe

Candidate probe:

```python
Probe(
    action,
    expected_outcomes,
    hypothesis_separation,
    cost,
)
```

Score:

```math
score =
expected_hypothesis_reduction
/
cost
```

Examples:

```text
read one file
run one targeted test
inspect one git commit
query one solver
```

---

# 78. Scientific Method Loop

```text
Hypothesis
→ Prediction
→ Experiment
→ Observation
→ Belief Update
```

This should be explicit in difficult debugging.

---

# 79. Engineering Loop

```text
UNDERSTAND
→ LOCALIZE
→ FORM HYPOTHESIS
→ PROBE
→ PATCH
→ VERIFY
→ UPDATE
```

Unlike the first design, these are **cognitive phases**, not mandatory workflow states.

The Governor may skip or revisit them.

---

# 80. Example Hybrid Task

```text
Issue:
cache expires entries early under concurrent refresh.

1. lexical + embedding retrieval finds 30 files
2. local reranker selects 8
3. graph model identifies expiry heap and concurrency lock
4. frontier model forms race-condition hypotheses
5. Z3/state-model plugin checks ordering invariant
6. cheap branch inspects tests
7. frontier worker patches locking logic
8. local test prioritizer selects 12 tests
9. tests expose secondary regression
10. trajectory search creates two repair candidates
11. verifier chooses candidate with passing tests
12. blackboard records successful strategy
```

No single model performed all cognition.

---

# 81. Tool Scripts

CHIMERA inherits the FORGE idea of programmatic tool calling.

But ToolScripts become one member of the portfolio.

Examples:

```text
batch repository analysis
test-log clustering
symbol graph traversal
patch statistics
AST queries
```

---

# 82. Local Script Registry

Develop coding-specific scripts:

```text
rank_failure_files.py
map_tests.py
diff_risk.py
trace_cluster.py
symbol_impact.py
api_surface.py
repo_bootstrap.py
dependency_slice.py
```

These should be deterministic and heavily reused.

---

# 83. Script Promotion

If a generated ToolScript repeatedly succeeds:

```text
task-local script
→ reviewed deterministic script
→ registered plugin tool
```

Prefer scripts over LLM calls for stable operations.

---


## Wave acceptance

Accept only after focused unit, contract, integration, and falsifier tests for this wave pass; boundary/domain-blindness/TCB linters remain green; optional dependencies fail closed; and no benchmark claim is made from unexecuted evaluation. Full-suite execution is deferred until final integration as requested.
