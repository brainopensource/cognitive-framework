---
id: report.electroweak.solution-a.full-code-chimera-wave-4
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
---

# AETHER CHIMERA — Full Code Manifest — Wave 4

## Delivery contract

- Branch: `feat/beta-release_electroweak-v091`
- Exact reconciled subject: `f242ced297216109736975376802f1e3dc4e29ce`
- Scope: backend only; frontend excluded.
- Focus: Plugin families, layer placement, cognitive runtime, model portfolio, cognitive budget, verification cortex, learned routing, local inference lifecycle, Atlas/LDA/LAM, and phases 0–2.
- Primary placement: `runtime/chimera`, `ports/`, adapters, manifests, and benchmark evidence.
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

# 84. Plugin Families

Recommended CHIMERA plugin surface:

```text
chimera-retrieval
chimera-local-inference
chimera-graph
chimera-symbolic
chimera-search
chimera-verification
chimera-skills
chimera-meta
chimera-toolscript
chimera-memory
```

Avoid a monolithic plugin.

---

# 85. Proposed AETHER Architectural Changes

Unlike FORGE, CHIMERA is allowed to extend Vanguard.

Recommended general additions:

```text
LocalInferencePort
CognitiveRouter
StrategyGenome
typed CognitiveBlackboard projection
ExperimentOptimizer interface
ModelCapabilityProfile
```

Do not add them to the kernel unless authority semantics require it.

---

# 86. Suggested Layer Placement

```text
kernel/
    unchanged where possible

ports/
    local_inference.py
    cognitive_router.py

agency/
    cognitive/
        blackboard.py
        governor.py
        strategy.py
    manifests/
        vg-code-chimera/

runtime/
    cognitive_runtime.py
    search_runtime.py
    trajectory_replay.py
    skill_runtime.py

adapters/
    local_models/
    graph/
    symbolic/

lab/
    chimera/
        evolution/
        datasets/
        optimizers/
        reports/
```

Confirm actual repository structure before editing.

---

# 87. Cognitive Runtime

```python
class CognitiveRuntime:
    def __init__(
        self,
        governor,
        router,
        blackboard,
        episode_engine,
        search_runtime,
    ):
        ...

    def step(self):
        directive = self.governor.decide(
            self.blackboard.snapshot(),
            self.capabilities,
        )

        route = self.router.select(
            directive,
            self.blackboard,
        )

        result = self.execute_route(
            directive,
            route,
        )

        self.blackboard.apply(result)
```

The underlying effect execution still uses AETHER.

---

# 88. Separation from EpisodeEngine

Do not replace the ordinary agent loop if avoidable.

`CognitiveRuntime` should sit above or beside `EpisodeEngine` as an orchestration composition.

Possible model:

```text
CognitiveRuntime
    │
    ├── invokes EpisodeEngine for generative episodes
    ├── invokes local services
    ├── invokes deterministic tools
    └── coordinates search state
```

This is one of the few areas where a new runtime-level abstraction may be justified.

---

# 89. Cognitive Episode

```python
@dataclass(frozen=True)
class CognitiveEpisodeRequest:
    role: str
    objective: str
    context_refs: tuple[str, ...]
    model_route: str
    max_turns: int
```

A frontier or cheap LLM run can remain an ordinary AETHER child episode.

---

# 90. Model Portfolio

Manifest concept:

```yaml
models:
  frontier:
    primary: frontier-a
    fallback: frontier-b

  cheap:
    primary: fast-cloud

  local:
    coder: local-code-7b
    summarizer: local-code-3b

  learned:
    reranker: swe-reranker
    embedder: code-embed
    router: chimera-router-v1
    graph: chimera-grepognn-v1
```

Names are placeholders.

---

# 91. Cognitive Budget

```python
@dataclass
class CognitiveBudget:
    frontier_tokens: int
    cheap_tokens: int
    local_inferences: int
    search_nodes: int
    solver_seconds: int
    tool_calls: int
    wall_seconds: int
```

This is distinct from authority but maps into existing conserved budgets.

---

# 92. Budget Allocation Policy

Example:

```text
20% exploration
50% implementation
20% verification
10% reserve
```

Dynamic reallocation:

```python
if localization_uncertainty_high:
    move_budget("implementation", "exploration", 0.10)

if candidate_patch_exists:
    move_budget("exploration", "verification", 0.10)
```

---

# 93. Frontier Escalation Reserve

Always preserve a small reserve for:

```text
final difficult diagnosis
cross-branch synthesis
architecture-level repair
```

Do not exhaust budget on early cheap loops.

---

# 94. Verification Cortex

Verification is a portfolio:

```text
compiler
typechecker
targeted tests
related tests
property tests
fuzzer
mutation test
static analyzer
LLM rubric verifier
```

Governor chooses depth.

---

# 95. Verification Scaling Levels

```text
V0 syntax
V1 targeted test
V2 related tests
V3 static/type checks
V4 generated properties
V5 fuzz/metamorphic
V6 mutation analysis
V7 independent model review
```

Most tasks should stop before V6/V7.

---

# 96. Rubric Verifier

For ambiguous tasks, build explicit rubric:

```python
VerificationRubric(
    requirements=[
        Requirement("behavior X"),
        Requirement("no regression Y"),
        Requirement("API compatibility"),
    ]
)
```

Verifier maps evidence to requirements.

---

# 97. Local Patch Risk Model

Features:

```text
files changed
LOC changed
API symbols changed
test files touched
dependency graph centrality
historical churn
typecheck failures
```

Output:

```text
low / medium / high risk
```

High risk increases verification depth.

---

# 98. Test-Time Search Policy

```python
if risk == "low" and tests_pass:
    stop

if risk == "medium" and uncertainty > threshold:
    refine_once()

if risk == "high":
    generate_alternate_candidate()
```

---

# 99. Dynamic Candidate Count

```math
K =
ceil(
    base_K
    * uncertainty
    * task_value
)
```

Bound tightly.

Example:

```text
simple task K=1
ambiguous task K=2
high-value difficult task K=3–4
```

---

# 100. Meta-Evolution Dataset

Projection table:

```text
chimera_runs
chimera_task_features
chimera_decisions
chimera_routes
chimera_retrievals
chimera_search_nodes
chimera_skills
chimera_outcomes
chimera_genomes
```

These are analytics projections.

Ledger remains authoritative.

---

# 101. Task Feature Vector

```python
TaskFeatures(
    language,
    repo_size,
    issue_length,
    stacktrace_present,
    tests_present,
    task_type,
    files_hint_count,
    dependency_complexity,
    historical_repo_familiarity,
)
```

Used by router and experiment analysis.

---

# 102. Decision Logging

Each adaptive decision records:

```text
state features
available routes
chosen route
reason
predicted value
actual outcome
cost
```

This is essential for learning.

---

# 103. Router Training

From verified trajectories:

```text
decision state
+
route
+
outcome
→ reward sample
```

Train:

```text
bandit posterior
or
small policy network
```

---

# 104. Router Reward

Example:

```math
R =
10 * task_progress
+ 50 * verified_success
- 0.002 * tokens
- 0.1 * seconds
- 5 * repeated_failure
```

Normalize in implementation.

Do not use a reward that can be trivially hacked by generating progress events.

---

# 105. Reward Hacking Defense

Reward must rely primarily on:

```text
environment-derived evidence
```

Never reward:

```text
self-reported confidence
number of TODOs completed
number of agent messages
length of explanation
```

---

# 106. Offline Holdout

Every meta-improvement uses:

```text
train/evolution tasks
validation tasks
held-out tasks
```

Prefer repository-separated or temporal splits.

Prevent leakage.

---

# 107. Temporal Evaluation

For repository learning:

```text
train on older issues
test on later issues
```

This approximates real continual learning and reduces contamination risk.

---

# 108. Continual Learning

SWE-Bench-CL motivates evaluating whether coding agents transfer useful experience without catastrophic forgetting. [R26]

CHIMERA should track:

```text
forward transfer
backward transfer
forgetting
```

for skills/router/local models.

---

# 109. No Online Weight Mutation During Task

A live coding run may update:

```text
ephemeral bandit state
task memory
blackboard
```

But should not alter permanent model weights.

Weight updates happen in controlled lab runs.

---

# 110. Local Model Training Pipeline

```text
ledger/artifacts
→ trajectory extraction
→ verified label generation
→ dedup
→ leakage filtering
→ train/val split
→ fine-tune
→ calibration
→ benchmark
→ model registry
```

---

# 111. Candidate Local Models

Categories:

```text
embedding
cross-encoder reranker
small code LLM
graph neural network
MLP classifier
```

Use quantization for local inference where quality permits.

---

# 112. Quantization

Support:

```text
INT8
INT4
GGUF
```

depending on backend.

Record exact model digest and quantization in events.

---

# 113. Local Model Registry

```python
LocalModelSpec(
    id,
    task,
    architecture,
    artifact_digest,
    quantization,
    runtime,
    latency_profile,
    validation_metrics,
)
```

---

# 114. Capability Profiling

Run small calibration suites:

```text
retrieval
classification
summarization
patch repair
```

Record profile.

Router uses it.

---

# 115. Local Inference Caching

Cache deterministic model outputs by:

```text
model digest
input digest
config digest
```

Especially for:

```text
embeddings
reranking
graph inference
classification
```

---

# 116. LDA / Atlas Integration

LDA remains a repository intelligence provider.

CHIMERA can use it to build:

```text
repository graph
symbol metadata
doc-code links
test links
semantic index
```

Unlike FORGE, CHIMERA may integrate LDA more deeply because the Graph Cortex needs a normalized IR.

Still:

```text
LDA unavailable
→ native fallback
```

---

# 117. Atlas → Graph Cortex Pipeline

```text
repository
→ LDA providers
→ normalized IR
→ graph projection
→ embedding features
→ GNN / heuristics / graph queries
```

---

# 118. LAM Integration

LAM becomes the cheap experimental environment for L2 evolution.

Use it to:

```text
simulate model responses
inject tool failures
exercise router decisions
test stop gates
test search algorithms
generate trajectory fixtures
```

LAM does not prove real coding ability.

It validates harness mechanics cheaply.

---

# 119. Empirical Development Ladder

```text
Tier 0
unit / deterministic

Tier 1
LAM harness simulation

Tier 2
internal real coding tasks

Tier 3
small external benchmark sample

Tier 4
larger benchmark

Tier 5
held-out/private tasks
```

---

# 120. Implementation Phase 0 — Reconcile AETHER

Before coding:

```text
inspect current branch / HEAD
map EpisodeEngine
map HarnessSession
map MetaController
map AdmissionGate
map ContextCompiler
map SpawnAdapter
map TransformRuntime
map model routing
map skill lifecycle
map SQLite projections
map artifacts
map LDA/LAM integration points
```

Produce one compatibility map.

Do not repeatedly reopen the architecture afterward.

---

# 121. Phase 1 — Cognitive Blackboard

Implement typed blackboard projection.

Files conceptually:

```text
vanguard/packages/agency/cognitive/blackboard.py
vanguard/packages/runtime/cognitive_projection.py
```

Acceptance:

```text
task facts/hypotheses/evidence reconstruct from events
```

---

# 122. Phase 2 — Local Inference Port

Add:

```text
LocalInferencePort
LlamaCppAdapter
OnnxAdapter
```

Start with:

```text
embedding
reranking
classification
```

No local generative worker required yet.

---


## Wave acceptance

Accept only after focused unit, contract, integration, and falsifier tests for this wave pass; boundary/domain-blindness/TCB linters remain green; optional dependencies fail closed; and no benchmark claim is made from unexecuted evaluation. Full-suite execution is deferred until final integration as requested.
