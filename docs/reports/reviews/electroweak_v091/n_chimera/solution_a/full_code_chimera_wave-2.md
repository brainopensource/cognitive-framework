# AETHER CHIMERA — Full Code Manifest — Wave 2

## Delivery contract

- Branch: `feat/beta-release_electroweak-v091`
- Exact reconciled subject: `f242ced297216109736975376802f1e3dc4e29ce`
- Scope: backend only; frontend excluded.
- Focus: Local cortex, retrieval market, value-of-information context, graph/symbolic/frontier cortices, verification plugins, and engineering search.
- Primary placement: `ports/`, optional `adapters/`, `agency/chimera/search`, and artifact-backed context.
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

# 16. Routing Must Be Safe

The router may choose **who computes**.

It may not choose:

```text
who has authority
who can bypass policy
who can exceed budget
```

AETHER authorization remains independent.

---

# 17. Local Cortex

The Local Cortex is a set of specialized inference services.

Initial recommended components:

```text
Code Embedding Retriever
Issue→File Reranker
Issue→Symbol Reranker
Failure Classifier
Test Prioritizer
Context Utility Scorer
Patch Risk Scorer
Trajectory Similarity Retriever
Cheap Summary Model
Router Model
```

These can run locally with:

```text
ONNX Runtime
llama.cpp
vLLM
Ollama
PyTorch
```

The adapter must abstract the backend.

---

# 18. Local Model Strategy

Do not initially train a giant "AETHER local intelligence model".

Start with specialized pretrained models.

Recommended progression:

```text
Phase 1
pretrained inference

Phase 2
lightweight calibration

Phase 3
LoRA / small finetuning

Phase 4
trajectory distillation

Phase 5
specialized local worker
```

---

# 19. Local Inference Port

```python
class LocalInferencePort(Protocol):
    def embed(
        self,
        texts: Sequence[str],
        model: str,
    ) -> Sequence[Sequence[float]]:
        ...

    def rank(
        self,
        query: str,
        candidates: Sequence[str],
        model: str,
    ) -> Sequence[float]:
        ...

    def classify(
        self,
        features: Mapping[str, object],
        model: str,
    ) -> Mapping[str, float]:
        ...

    def generate(
        self,
        request: "LocalGenerationRequest",
    ) -> "LocalGenerationResult":
        ...
```

This may justify a general Vanguard port because it is useful across agent domains.

---

# 20. Local Inference Adapter

Suggested implementations:

```text
LlamaCppAdapter
OllamaAdapter
OnnxAdapter
TorchAdapter
```

Do not couple runtime logic to one serving system.

---

# 21. Learned Bug Localization

Use retrieval ensemble:

```text
lexical
+
embedding
+
graph
+
git history
+
neural reranker
```

Candidate generation:

```python
candidates = union(
    bm25.search(issue),
    embedding.search(issue),
    lda.search(issue),
    graph_neighbors(seed_files),
)
```

Rerank:

```python
scores = issue_file_reranker.rank(
    issue,
    candidates,
)
```

---

# 22. Retrieval Market

Because no single retrieval family dominates, CHIMERA treats retrieval algorithms as competing bidders.

```python
@dataclass(frozen=True)
class RetrievalBid:
    provider: str
    candidate_id: str
    relevance: float
    confidence: float
    novelty: float
    token_cost: int
    provenance: str
```

Final utility:

```math
U(c) =
    α * relevance
  + β * structural_relevance
  + γ * novelty
  + δ * failure_relevance
  - λ * token_cost
```

---

# 23. Value-of-Information Context Selection

For each candidate context item:

```math
VOI(c) =
E[ΔP(success) | c]
/
(token_cost(c) + ε)
```

Exact probability does not need to be perfect.

Start with a learned or heuristic proxy:

```text
task relevance
graph proximity
test proximity
failure mention
novelty
token size
historical utility
```

---

# 24. Context Portfolio

Maintain several stores:

```text
Hot Context
    current model input

Warm Context
    compressed blackboard facts

Cold Context
    artifact store / repository index

Learned Context
    trajectory/skill memory
```

The context compiler pages items between levels.

---

# 25. Local Context Utility Model

A tiny model can predict:

```text
KEEP
DROP
COMPRESS
FETCH
PIN
```

Inputs:

```text
task embedding
context item embedding
current hypothesis embedding
source type
age
token size
historical use
```

This can be:

```text
small MLP
gradient boosted tree
small cross-encoder
```

Use whichever is empirically fastest.

Deep learning is not automatically superior.

---

# 26. Graph Cortex

Create or reuse a repository graph from LDA/Atlas.

Nodes:

```text
file
module
symbol
test
package
documentation
commit
```

Edges:

```text
imports
calls
references
contains
tests
changed_with
documents
depends_on
```

---

# 27. GNN Bug Locator

Optional learned graph model:

```python
class GraphBugLocator:
    def score_nodes(
        self,
        repo_graph,
        task_embedding,
        failure_features,
    ) -> Mapping[NodeId, float]:
        ...
```

Use it only when:

```text
repository graph exists
repo is large enough
model latency is low
```

Native search remains fallback.

---

# 28. GNN Test Prioritizer

Input graph:

```text
changed symbols
dependencies
test coverage/execution history
historical co-change
```

Output:

```text
ordered tests
predicted fault-detection value
estimated runtime
```

Utility:

```math
priority(test) =
P(detect regression)
/
runtime(test)
```

This can reduce full-suite waste.

---

# 29. Symbolic Cortex

CHIMERA adds first-class algorithmic tools.

Potential plugins:

```text
SymPy
Z3
SMT
constraint solver
SAT
numeric optimizer
linear algebra
property-based test generator
fuzzer
static analyzer
type checker
compiler
mutation tester
```

The goal is not "AI for everything".

The goal is to exploit exact computation when possible.

---

# 30. Equation & Scientific Problem Mode

For problems containing mathematical constraints:

```text
natural-language requirement
→ symbolic extraction
→ equations / invariants
→ solver
→ executable tests
→ implementation
```

Example:

```python
invariants = extract_invariants(task)

solution = sympy.solve(
    invariants.equations,
    invariants.variables,
)
```

Then use the result as **evidence**, not merely generated explanation.

---

# 31. SMT-Assisted Coding

Useful for:

```text
state machine correctness
boundary conditions
integer constraints
protocol invariants
resource conservation
```

Example workflow:

```text
LLM proposes invariant
→ Z3 checks satisfiability
→ counterexample returned
→ patch revised
```

---

# 32. Property-Based Testing Plugin

The harness should be able to generate candidate properties and use:

```text
Hypothesis
QuickCheck
proptest
fast-check
```

depending on language.

Flow:

```text
task requirements
→ derive property
→ run generator
→ discover counterexample
→ repair
```

This is especially useful when benchmark tests are sparse.

---

# 33. Metamorphic Testing

When exact expected output is hard to specify:

```text
define transformation
→ expected invariant relation
→ execute before/after
```

Examples:

```text
sorting idempotence
cache read-after-write
serialization round-trip
monotonicity
symmetry
scaling invariance
```

---

# 34. Mutation-Guided Verification

Mutation testing is expensive and therefore **not default**.

Use selectively:

```text
high-risk patch
critical logic
generated test confidence uncertain
```

Objective:

```text
Does the new test actually kill plausible incorrect variants?
```

This can become a strong verifier for difficult tasks.

---

# 35. Frontier Cortex

Frontier LLMs perform high-entropy tasks:

```text
task interpretation
architecture reasoning
hypothesis generation
novel patch design
multi-file integration
ambiguous requirement resolution
trajectory synthesis
```

They should not spend turns manually sorting 500 search results.

---

# 36. Cheap Cortex

Cheap hosted models perform:

```text
summarization
query expansion
branch investigation
simple patch candidates
documentation lookup
review of narrow diffs
```

The router chooses them when expected value is positive.

---

# 37. Local Small LLM Workers

Roles suitable for 0.5B–7B class models after distillation:

```text
failure classifier
tool-call planner
repo query generator
test log summarizer
context compressor
simple patch repair
skill selector
trajectory tagger
```

Do not use tiny models for unconstrained architectural reasoning.

---

# 38. Agent Distillation Flywheel

Training data:

```text
frontier run
→ tool trajectory
→ successful subtask
→ distillation sample
```

Example sample:

```json
{
  "state": "...",
  "objective": "rank likely files",
  "actions": ["search", "read", "rank"],
  "result": ["cache/store.py", "cache/expiry.py"],
  "outcome": "successful localization"
}
```

Train narrow local worker.

---

# 39. Distillation Safety

Never train on:

```text
failed trajectory labeled as success
benchmark hidden answers
contaminated future state
unverified model claims
```

Use only environment-grounded labels.

---

# 40. Engineering Search Space

Search nodes represent:

```python
@dataclass(frozen=True)
class EngineeringState:
    hypothesis: str
    context_refs: tuple[str, ...]
    workspace_digest: str
    patch_digest: str | None
    verification: str | None
    unresolved_failures: tuple[str, ...]
    cost: float
```

Edges:

```text
retrieve
edit
test
fork
replay
refine
change model
invoke solver
```

---

# 41. Best-First Engineering Search

Priority:

```math
priority(n) =
w_p * progress(n)
+ w_e * evidence(n)
+ w_v * verification(n)
+ w_i * information_gain(n)
- w_c * cost(n)
- w_r * risk(n)
```

Open queue:

```python
while frontier and budget.available():
    node = pop_best(frontier)

    children = expand(node)

    for child in children:
        evaluate(child)
        push(frontier, child)

    if verified_solution(child):
        return child
```

This is more general than a fixed repair loop.

---

# 42. Beam Search Mode

Maintain K promising states.

```text
beam width 2–4
```

Use when:

```text
multiple plausible patch designs
tests give delayed feedback
task is high-value
```

Avoid wide beams by default.

---

# 43. Parallel-Distill-Refine

CHIMERA should support PDR-like scaling:

```text
N initial attempts
→ compact trajectory summaries
→ synthesis of successes/failures
→ refined attempt conditioned on summaries
```

Key contract:

```python
TrajectorySummary(
    hypothesis,
    progress,
    files,
    patch,
    verification,
    failure_mode,
    useful_evidence,
    dead_ends,
)
```

---

# 44. Recursive Tournament Voting

When many candidates exist:

```text
group candidate summaries
→ compare small groups
→ retain winners
→ repeat
```

Use:

```text
environment evidence
+
local verifier
+
LLM judgment
```

not LLM judgment alone.

---

# 45. SWE-Replay-Style Trajectory Recycling

Instead of always starting over:

```text
archived trajectory
→ identify critical useful state
→ replay known prefix
→ branch from that state
```

Useful when:

```text
repository exploration was expensive
early localization was correct
later patch reasoning failed
```

---


## Wave acceptance

Accept only after focused unit, contract, integration, and falsifier tests for this wave pass; boundary/domain-blindness/TCB linters remain green; optional dependencies fail closed; and no benchmark claim is made from unexecuted evaluation. Full-suite execution is deferred until final integration as requested.
