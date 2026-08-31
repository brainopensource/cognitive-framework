---
id: report.electroweak.solution-a.full-code-chimera-wave-5
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
---

# AETHER CHIMERA — Full Code Manifest — Wave 5

## Delivery contract

- Branch: `feat/beta-release_electroweak-v091`
- Exact reconciled subject: `f242ced297216109736975376802f1e3dc4e29ce`
- Scope: backend only; frontend excluded.
- Focus: Phases 3–15, vg-code-chimera manifest and presets, complete orchestration pseudocode, experimental rules, tests, falsifiers, security, performance, and hardware profiles.
- Primary placement: `agency/manifests/vg-code-chimera`, `runtime/chimera`, adapters, and focused tests.
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

# 123. Phase 3 — Retrieval Ensemble

Implement:

```text
lexical
LDA
embedding
reranker
graph heuristic
```

Aggregate via Retrieval Market.

Acceptance:

```text
top-k candidate files visibly better than lexical baseline
on small localization set
```

---

# 124. Phase 4 — Meta-Cognitive Governor

Start deterministic.

Inputs:

```text
blackboard
uncertainty
budget
```

Outputs:

```text
route / retrieve / generate / verify / search
```

---

# 125. Phase 5 — Router

Version 0:

```text
rules
```

Version 1:

```text
Thompson sampling
```

Version 2:

```text
learned policy
```

Do not jump directly to neural routing.

---

# 126. Phase 6 — Symbolic Plugins

Add:

```text
sympy
z3
property testing
```

Only expose through AETHER tool capabilities.

---

# 127. Phase 7 — Search Runtime

Implement:

```text
EngineeringState
SearchNode
BestFirstSearch
beam mode
trajectory summaries
```

Do not implement generic MCTS first.

---

# 128. Phase 8 — Trajectory Replay / PDR

Add:

```text
critical-state checkpoints
trajectory distillation
replay branch
parallel-distill-refine
```

---

# 129. Phase 9 — Verification Cortex

Add adaptive verification planner.

Start with:

```text
targeted tests
related tests
property tests
```

Mutation testing later.

---

# 130. Phase 10 — Skill Runtime

Add:

```text
skill registry
skill retrieval
skill context compilation
task-local procedural candidate
```

---

# 131. Phase 11 — Strategy Genome

Make harness config immutable/versioned.

Every run records genome digest.

---

# 132. Phase 12 — Evolution Lab

Implement offline:

```text
genome mutation
experiment execution
metrics
Pareto selection
promotion
```

Start with simple evolutionary search.

---

# 133. Phase 13 — Prompt Optimizer

Integrate or reproduce minimal:

```text
MIPRO-like
or
GEPA/TextGrad-like
```

No need to import an entire external framework if a small adapter suffices.

---

# 134. Phase 14 — Local Model Distillation

Only when trajectory corpus is sufficient.

First targets:

```text
failure classifier
context compressor
repo query generator
```

---

# 135. Phase 15 — Graph Neural Models

Train or integrate:

```text
bug localization GNN
test prioritizer
```

Only after graph data is stable.

---

# 136. `vg-code-chimera` Manifest

Conceptual:

```yaml
agent: vg-code-chimera

strategy_genome: chimera-balanced-v1

cognitive:
  governor: adaptive
  blackboard: true

routing:
  policy: contextual-bandit

local_cortex:
  embeddings: true
  reranker: true
  classifier: true
  local_llm: optional
  graph_model: optional

frontier:
  enabled: true

search:
  mode: adaptive
  max_beam: 3

retrieval:
  ensemble: true
  lda: auto

symbolic:
  sympy: true
  z3: optional
  property_testing: auto

skills:
  retrieval: true

verification:
  adaptive: true

meta:
  evolution: offline_only
```

Translate to actual schema.

---

# 137. Presets

## `chimera-fast`

```text
heuristics
retrieval ensemble
local reranker
one cheap/frontier worker
targeted verification
```

## `chimera-balanced`

```text
router
local cortex
frontier escalation
best-first search up to small width
skills
adaptive verification
```

## `chimera-max`

```text
full portfolio
PDR/replay
multiple frontier candidates
symbolic verification
graph cortex
strong verification
```

## `chimera-science`

Adds:

```text
SymPy
Z3
numeric tools
scientific domain retrieval
metamorphic tests
```

---

# 138. Pseudocode — Top-Level

```python
def run_chimera(task, runtime, genome):
    board = CognitiveBlackboard.from_task(task, genome)

    while board.budget.available():
        board.refresh_from_ledger()

        directive = governor.decide(
            state=board,
            capabilities=runtime.capabilities,
        )

        route = router.select(
            decision=directive,
            state=board,
            portfolio=portfolio,
        )

        result = execute_cognitive_route(
            directive=directive,
            route=route,
            runtime=runtime,
            board=board,
        )

        runtime.record(result)
        board = board.apply(result)

        if should_search(board):
            board = engineering_search(board, runtime)

        if completion_gate.accepts(board):
            return complete(board)

    return fail(board)
```

---

# 139. Pseudocode — Router

```python
def select_route(request, features, profiles):
    eligible = [
        route
        for route in profiles
        if route.supports(request)
    ]

    if deterministic_solver_available(request):
        return "symbolic"

    if simple_local_task(request):
        return bandit.select(
            context=features,
            arms=eligible_local_routes,
        )

    if high_entropy(request):
        return "frontier"

    return "cheap"
```

---

# 140. Pseudocode — Retrieval Market

```python
def retrieve(task, board):
    bids = []

    for provider in retrieval_providers:
        results = provider.retrieve(task)

        for result in results:
            bids.append(
                RetrievalBid(
                    provider=provider.id,
                    candidate_id=result.id,
                    relevance=result.score,
                    confidence=result.confidence,
                    novelty=novelty(result, board),
                    token_cost=result.token_cost,
                    provenance=result.provenance,
                )
            )

    merged = deduplicate(bids)

    reranked = local_reranker.rank(
        task.text,
        merged,
    )

    return select_by_value_of_information(
        reranked,
        board.context_budget,
    )
```

---

# 141. Pseudocode — Engineering Search

```python
def engineering_search(root, runtime):
    frontier = PriorityQueue()
    frontier.push(root)

    while frontier and search_budget.available():
        state = frontier.pop()

        if verified(state):
            return state

        actions = propose_expansions(state)

        for action in actions:
            route = router.select(action, state, portfolio)
            child = execute(action, route, runtime)

            child.score = search_value(child)

            if not dominated(child):
                frontier.push(child)

    return best_observed(frontier)
```

---

# 142. Pseudocode — PDR

```python
def parallel_distill_refine(state, n=3):
    attempts = parallel_rollouts(
        state,
        count=n,
    )

    summaries = [
        trajectory_distiller(a)
        for a in attempts
    ]

    synthesis = synthesize(
        successes=summaries,
        failures=summaries,
        dead_ends=summaries,
    )

    return frontier_worker.run(
        state=state,
        additional_context=synthesis,
    )
```

---

# 143. Pseudocode — Meta-Evolution

```python
def evolve(population, tasks):
    evaluated = evaluate_population(
        population,
        tasks,
    )

    pareto = pareto_front(evaluated)

    parents = select_diverse(pareto)

    candidates = []

    for parent in parents:
        candidates.extend(
            mutate_genome(parent)
        )

    for a, b in pairwise(parents):
        candidates.append(
            crossover(a, b)
        )

    validated = evaluate(
        candidates,
        validation_tasks,
    )

    return promote_if_holdout_improves(validated)
```

---

# 144. Pseudocode — Prompt Textual Gradient

```python
def optimize_prompt(component, failed_runs):
    critiques = [
        analyze_failure(run, component)
        for run in failed_runs
    ]

    gradient = aggregate_textual_feedback(critiques)

    candidates = prompt_mutator.generate(
        component.prompt,
        gradient,
    )

    return evaluate_prompt_candidates(
        candidates,
        validation_tasks,
    )
```

---

# 145. Pseudocode — Local Distillation

```python
def build_distillation_dataset(runs):
    samples = []

    for run in runs:
        if not run.environment_verified:
            continue

        for decision in run.decisions:
            if decision.is_good_training_example():
                samples.append(
                    distill(decision)
                )

    return leakage_filter(
        deduplicate(samples)
    )
```

---

# 146. Development Rule — Prefer Small Experiments

For every new cognitive mechanism:

```text
Problem
Hypothesis
Small implementation
3–10 representative tasks
Compare
Keep/Revert
```

Do not implement the entire architecture before observing the first gain.

---

# 147. Development Rule — Algorithms Need Baselines

Every learned component must compare against:

```text
simple heuristic
```

Examples:

```text
GNN bug locator vs ripgrep/BM25
neural router vs static rule
test prioritizer vs changed-file heuristic
```

If the advanced model does not win enough to justify complexity, remove it.

---

# 148. Development Rule — Local Model Must Earn Its Runtime

Require:

```math
utility_gain > inference_overhead
```

A local model is useful when:

```text
called frequently
low latency
reliable enough
saves frontier tokens
```

---

# 149. Development Rule — Frontier Calls Must Be Accountable

Log:

```text
why frontier was selected
alternative route
cost
outcome
```

This produces training data for future routing.

---

# 150. Development Rule — Self-Improvement Must Be Reversible

Every promotion:

```text
old genome retained
new genome versioned
rollback one command/config change
```

---

# 151. Testing

## Unit

```text
blackboard reducers
routing rules
bandit updates
retrieval fusion
search ordering
genome serialization
skill selection
```

## Integration

```text
retrieval → frontier → patch → verify
local route → escalation
symbolic counterexample → repair
search candidate → selection
trajectory replay → refinement
```

## Learning

```text
router offline replay
prompt optimizer holdout
local model calibration
```

---

# 152. Falsifiers

```text
local router sends impossible task to weak model forever
→ escalation required

retrieval ensemble misses hinted file
→ diagnose provider coverage

GNN returns stale graph node
→ repo digest mismatch rejected

strategy optimizer improves training but hurts holdout
→ promotion rejected

reward optimizer produces more "progress" but no passing tasks
→ objective rejected

skill library injects irrelevant procedure
→ retrieval calibration failure

model changes genome during live run
→ forbidden
```

---

# 153. Security

CHIMERA expands computational surface.

Therefore:

```text
local models cannot grant capabilities
solvers cannot bypass tool policy
generated scripts remain sandboxed
optimization lab cannot mutate production registry without promotion
model artifacts are content-addressed
training datasets preserve provenance
```

---

# 154. Performance

Fast path target:

```text
task
→ local retrieval/rerank
→ one frontier episode
→ test
```

Heavy path activates only when required.

Do not initialize:

```text
GNN
all local LLMs
mutation engine
search population
```

for a trivial bug.

Use lazy loading.

---

# 155. Hardware Profile

CHIMERA should degrade gracefully.

## CPU-only

```text
lexical retrieval
small ONNX models
heuristics
frontier cloud
```

## Consumer GPU

```text
embeddings
rerankers
3B–7B local model
GNN
```

## Larger GPU

```text
larger local coder
parallel local branches
```

Cloud frontier remains optional/configurable.

---


## Wave acceptance

Accept only after focused unit, contract, integration, and falsifier tests for this wave pass; boundary/domain-blindness/TCB linters remain green; optional dependencies fail closed; and no benchmark claim is made from unexecuted evaluation. Full-suite execution is deferred until final integration as requested.
