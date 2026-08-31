---
id: report.electroweak.solution-a.full-code-chimera-wave-6
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
---

# AETHER CHIMERA — Full Code Manifest — Wave 6

## Delivery contract

- Branch: `feat/beta-release_electroweak-v091`
- Exact reconciled subject: `f242ced297216109736975376802f1e3dc4e29ce`
- Scope: backend only; frontend excluded.
- Focus: Local supervisor, model residency, projections, algorithms, acceptance criteria, metrics, benchmark program, risk controls, PR plan, roadmaps, scientific standards, and final checklist.
- Primary placement: `runtime/chimera`, offline lab/benchmarks, registries, evidence, and operational configuration.
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

# 156. Local Runtime Supervisor

Manage local models:

```text
lazy startup
LRU unloading
memory budget
health checks
batching
```

Do not keep every model resident.

---

# 157. Model Residency Policy

Example:

```text
embedder resident
reranker resident
local LLM lazy
GNN lazy per repository
```

---

# 158. SQLite Projections

Suggested analytical projections:

```sql
chimera_task_features
chimera_route_decisions
chimera_retrieval_scores
chimera_search_nodes
chimera_skill_usage
chimera_model_outcomes
chimera_genome_results
```

Do not store duplicate authoritative payloads.

Use artifact/event IDs.

---

# 159. Example Route Table

| Operation | Default | Escalation |
|---|---|---|
| file candidate retrieval | embedding + lexical | LDA/GNN/frontier |
| file rerank | local cross-encoder | frontier |
| failure classification | heuristic/local | frontier |
| task architecture | frontier | alternate frontier |
| log compression | local SLM | cheap cloud |
| symbolic equation | SymPy/Z3 | frontier interpretation |
| patch design | frontier | search/multi-candidate |
| test ordering | heuristic/GNN | frontier |
| final verification | environment | rubric model |

---

# 160. Initial Algorithms to Implement

**P0**

```text
retrieval ensemble
local reranker
heuristic metacognitive governor
Thompson router
best-first patch/hypothesis search
trajectory distillation
```

**P1**

```text
PDR
trajectory replay
skill retrieval
SymPy/Z3
property testing
```

**P2**

```text
local SLM distillation
GNN bug localization
test prioritization
prompt optimization
genome evolution
```

---

# 161. Algorithms Not to Implement Initially

```text
full MCTS inside every coding task
online RL weight updates
giant multi-agent society
dozens of local models
unbounded evolutionary loops
end-to-end neural controller
automatic kernel rewriting
```

---

# 162. Acceptance Criteria — v0.1

1. `vg-code-chimera` runs through AETHER.
2. Blackboard state is reconstructable.
3. Retrieval ensemble works with local reranker.
4. Router chooses between at least local/cheap/frontier paths.
5. Real patch and verification execute.
6. Router decision/outcome is logged.
7. Existing harnesses remain unchanged.

---

# 163. Acceptance Criteria — v0.2

1. Best-first engineering search works.
2. At least two candidate hypotheses can be compared.
3. PDR or replay reuses trajectory summaries.
4. Symbolic plugin can produce environment-grounded evidence.
5. Skill retrieval is selective.
6. Adaptive verification changes depth by risk.

---

# 164. Acceptance Criteria — v0.3

1. Strategy Genome is immutable/versioned.
2. Offline evolution mutates genomes.
3. Validation/holdout gate blocks regressions.
4. Router learns from prior outcomes.
5. At least one local specialist is fine-tuned/distilled from trajectories.
6. Promotion is reversible.

---

# 165. Acceptance Criteria — Local Cortex

A local specialist is promoted only when:

```text
latency acceptable
calibration measured
baseline beaten
frontier cost reduced or success improved
fallback exists
```

---

# 166. Acceptance Criteria — Self Improvement

Self-improvement is real only when:

```text
new genome/model/skill
beats parent
on held-out tasks
with reproducible evidence
```

"Agent says it learned" is irrelevant.

---

# 167. Success Metrics

Primary:

```text
verified task success
```

Secondary:

```text
success/token
success/cost
success/time
retrieval recall
time to correct localization
repair recovery rate
branch utility
router regret
skill transfer
```

---

# 168. Router Regret

When multiple model outcomes are known experimentally:

```math
regret =
reward(best available route)
-
reward(chosen route)
```

Track cumulative regret.

This turns routing into a measurable problem.

---

# 169. Retrieval Metrics

```text
MRR
Recall@K
context precision
budgeted context yield
gold-file discovery latency
abstention calibration
```

Use retrieval benchmarks independently from patch benchmarks.

---

# 170. Search Metrics

```text
nodes expanded
successful candidate rank
reuse rate
trajectory replay savings
branch diversity
```

---

# 171. Self-Improvement Metrics

```text
parent vs child genome
holdout delta
cost delta
complexity delta
transfer across repositories
```

---

# 172. Benchmark Program

Do not chase one leaderboard.

Use:

```text
internal complex tasks
SWE-style fresh tasks
SWE-Bench Pro subsets where appropriate
repository retrieval benchmarks
scientific software tasks
greenfield tasks
algorithmic/equation tasks
```

---

# 173. First Experimental Matrix

```text
A baseline Vanguard
B + retrieval ensemble
C + local reranker
D + metacognitive routing
E + best-first search
F + PDR/replay
G + symbolic plugins
H + skills
I + local distilled worker
J + evolved genome
```

This establishes causal signal.

---

# 174. Why This Is Different from Coding Max

Coding Max:

```text
pre-designed strong workflow
```

CHIMERA:

```text
portfolio of heterogeneous cognitive algorithms
+
learned routing
+
search
+
offline evolution
```

---

# 175. Why This Is Different from FORGE

FORGE:

```text
minimal programmable agent runtime
```

CHIMERA:

```text
adaptive cognitive architecture
with specialized learned/non-LLM processors
and explicit self-optimization
```

---

# 176. When CHIMERA Should Win

Likely strong cases:

```text
large repository
complex context retrieval
multiple plausible failures
high-value difficult task
scientific/mathematical constraints
repeat work across similar repositories
```

---

# 177. When CHIMERA Should Lose

Likely weak cases:

```text
tiny obvious edit
single-file typo
very low latency requirement
no useful prior data
hardware-constrained environment
```

Use `forge-fast` or simple coding preset instead.

---

# 178. Architectural Risk: Overengineering

CHIMERA has permission to be ambitious.

It does not have permission to become undisciplined.

Every component must satisfy:

```text
clear role
measurable value
independent disable switch
fallback path
bounded complexity
```

---

# 179. Principal Engineering Rule

> **Build CHIMERA as an algorithm portfolio, not a cathedral.**

The architecture should allow deleting half its algorithms without breaking the runtime.

---

# 180. Recommended Initial Directory

```text
vanguard/packages/
├── agency/
│   ├── cognitive/
│   │   ├── blackboard.py
│   │   ├── governor.py
│   │   ├── confidence.py
│   │   └── strategy.py
│   └── manifests/
│       └── vg-code-chimera/
│
├── ports/
│   ├── local_inference.py
│   └── cognitive_router.py
│
├── runtime/
│   ├── cognitive_runtime.py
│   ├── engineering_search.py
│   ├── trajectory_replay.py
│   ├── retrieval_market.py
│   └── skill_runtime.py
│
├── adapters/
│   ├── local_models/
│   ├── graph/
│   └── symbolic/
│
└── lab/
    └── chimera/
        ├── evolution/
        ├── optimizers/
        ├── datasets/
        └── reports/
```

Adjust to current repository conventions after reconciliation.

---

# 181. PR Sequence

```text
CHM-PR-01 blackboard + manifest
CHM-PR-02 local inference port + embedding/reranker
CHM-PR-03 retrieval market
CHM-PR-04 governor + heuristic router
CHM-PR-05 Thompson bandit routing
CHM-PR-06 engineering search
CHM-PR-07 trajectory replay/PDR
CHM-PR-08 symbolic plugins
CHM-PR-09 skill retrieval
CHM-PR-10 Strategy Genome
CHM-PR-11 evolution lab
CHM-PR-12 local distillation
CHM-PR-13 graph cortex/GNN
```

---

# 182. First 30-Day Execution Priorities

The fastest path to useful capability is:

```text
1. retrieval ensemble
2. local reranker
3. blackboard
4. frontier/cheap routing
5. real verification
6. small hypothesis search
7. trajectory reuse
```

Do not spend the first month training GNNs.

---

# 183. First Local Models to Try

Prioritize mature, easy inference components:

```text
code embedding model
code reranker
small code summarizer
```

Then train:

```text
failure classifier
router
```

GNNs follow once graph pipeline/data exists.

---

# 184. What to Learn from Logs First

Ask:

```text
Where did correct files first appear?
Which tool/model found them?
How long until correct localization?
Which context was actually used?
What failure repeated?
Which model recovered?
Which tests predicted final success?
```

This determines the first learned specialists.

---

# 185. Self-Improvement Roadmap

```text
Stage 0
manual strategy variants

Stage 1
bandit routing

Stage 2
prompt optimization

Stage 3
skill evolution

Stage 4
genome evolution

Stage 5
local worker distillation

Stage 6
learned meta-controller
```

Do not invert this order.

---

# 186. Meta-Cognitive Roadmap

```text
rules
→ calibrated confidence
→ historical competence profile
→ contextual bandit
→ learned policy
```

---

# 187. Research Program

Important research questions:

```text
RQ1 Which operations should never use frontier LLMs?
RQ2 Which local specialist gives the largest success/token gain?
RQ3 How much does retrieval quality predict repair success?
RQ4 When does search outperform single trajectory?
RQ5 How many prior trajectories are useful before returns diminish?
RQ6 Can skill retrieval outperform bigger prompts?
RQ7 Can a small local router reduce frontier spend without lowering success?
RQ8 Does GNN localization outperform retrieval ensemble enough to justify complexity?
RQ9 Which verification level predicts hidden-test success best?
RQ10 Can evolved genomes transfer across repositories?
```

---

# 188. Scientific Standards

For experiments:

```text
preregister hypothesis when practical
store exact genome/model versions
store task digest
store environment digest
store seed where relevant
do not mix dry-run and real results
do not call model self-report success
```

---

# 189. Benchmark Contamination

Use:

```text
fresh tasks
temporal splits
private internal tasks
held-out repositories
```

whenever possible.

Static benchmark score alone is insufficient.

---

# 190. Final Architecture Thesis

CHIMERA should become an **adaptive neuro-symbolic engineering system**:

```text
AETHER constitutional substrate
+
typed cognitive state
+
learned local specialists
+
frontier reasoning
+
symbolic computation
+
engineering search
+
trajectory reuse
+
skills
+
offline evolution
```

The architecture should make models progressively more interchangeable because the harness itself becomes better at:

```text
finding the right context
choosing the right computation
allocating the right model
verifying the right property
remembering what worked
improving itself safely
```

---

# 191. Final Development Directive

Implement CHIMERA incrementally.

The first milestone is **not** autonomous self-improvement.

It is:

> **Prove that heterogeneous computation beats “frontier LLM does everything.”**

Start with:

```text
retrieval ensemble
+
local reranker
+
metacognitive routing
+
frontier worker
+
real verification
```

Then add:

```text
search
trajectory reuse
solvers
skills
```

Only after these produce trustworthy data should the system begin:

```text
prompt evolution
workflow evolution
local model distillation
GNN training
```

The system may be ambitious at the research layer while keeping the execution core deterministic, inspectable, and reversible.

---

# 192. Final Principal Engineer Checklist

```text
[ ] Blackboard is projection, not authority
[ ] Local inference has explicit ports
[ ] Every local model has fallback
[ ] Retrieval algorithms are composable
[ ] Context selection is budget-aware
[ ] Frontier LLM reserved for high-value reasoning
[ ] Symbolic tools produce evidence
[ ] Search is bounded
[ ] Trajectories can be distilled/replayed
[ ] Router decisions are logged
[ ] Skills retain evidence/provenance
[ ] Strategy genomes are immutable
[ ] Live tasks cannot mutate permanent harness
[ ] Evolution uses validation + holdout
[ ] Reward relies on environment evidence
[ ] New algorithms beat simple baselines
[ ] Complexity is penalized
[ ] AETHER authority remains conserved
[ ] All self-improvement is reversible
```

---

# 193. Research References

**[R1]** Kim et al., *Scaling Test-Time Compute for Agentic Coding*, arXiv:2604.16529, 2026.  
https://arxiv.org/abs/2604.16529

**[R2]** Ding & Zhang, *SWE-Replay: Efficient Test-Time Scaling for Software Engineering Agents*, arXiv:2601.22129, 2026.  
https://arxiv.org/abs/2601.22129

**[R3]** Qin & Xie, *Agent Retrieval Bench: Evaluating Repository Context Retrieval for Coding Agents*, arXiv:2607.24882, 2026.  
https://arxiv.org/abs/2607.24882

**[R4]** Li et al., *ContextBench: A Benchmark for Context Retrieval in Coding Agents*, arXiv:2602.05892, 2026.  
https://arxiv.org/abs/2602.05892

**[R5]** Gandhi, Gao & Callan, *Repository-level Code Search with Neural Retrieval Methods*, arXiv:2502.07067, 2025.  
https://arxiv.org/abs/2502.07067

**[R6]** Reddy et al., *SweRank+: Multilingual, Multi-Turn Code Ranking for Software Issue Localization*, arXiv:2512.20482, 2025.  
https://arxiv.org/abs/2512.20482

**[R7]** Wang et al., *GREPO: A Benchmark for Graph Neural Networks on Repository-Level Bug Localization*, arXiv:2602.13921, 2026.  
https://arxiv.org/abs/2602.13921

**[R8]** Sowmyadevi & Alphy, *Graph neural network-based mutation-aware regression test ordering using code dependency graphs and execution traces*, MethodsX, 2025/2026.  
https://pmc.ncbi.nlm.nih.gov/articles/PMC12808596/

**[R9]** Kang et al., *Distilling LLM Agent into Small Models with Retrieval and Code Tools*, arXiv:2505.17612, 2025.  
https://arxiv.org/abs/2505.17612

**[R10]** OpenHands/Mistral, *Devstral: A new state-of-the-art open model for coding agents*, 2025.  
https://www.openhands.dev/blog/devstral-a-new-state-of-the-art-open-model-for-coding-agents

**[R11]** Zhou et al., *Agent-as-a-Router: Agentic Model Routing for Coding Tasks*, arXiv:2606.22902, 2026.  
https://arxiv.org/abs/2606.22902

**[R12]** Liu et al., *Metacognition in LLMs: Foundations, Progress, and Opportunities*, arXiv:2607.11881, 2026.  
https://arxiv.org/abs/2607.11881

**[R13]** Wang & Shu, *MetaCogAgent: A Metacognitive Multi-Agent LLM Framework with Self-Aware Task Delegation*, arXiv:2605.17292, 2026.  
https://arxiv.org/abs/2605.17292

**[R14]** Hou et al., *Learn Like Humans: Use Meta-cognitive Reflection for Efficient Self-Improvement*, arXiv:2601.11974, 2026.  
https://arxiv.org/abs/2601.11974

**[R15]** Wan et al., *Inference-Time Scaling of Verification: Self-Evolving Deep Research Agents via Test-Time Rubric-Guided Verification*, arXiv:2601.15808, 2026.  
https://arxiv.org/abs/2601.15808

**[R16]** Kulsum et al., *A Case Study of LLM for Automated Vulnerability Repair: Assessing Impact of Reasoning and Patch Validation Feedback*, 2024.  
https://arxiv.org/abs/2405.15690

**[R17]** Zhang et al., *AFlow: Automating Agentic Workflow Generation*, ICLR 2025.  
https://proceedings.iclr.cc/paper_files/paper/2025/hash/5492ecbce4439401798dcd2c90be94cd-Abstract-Conference.html

**[R18]** Opsahl-Ong et al., *Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs*, EMNLP 2024.  
https://aclanthology.org/2024.emnlp-main.525/

**[R19]** Yuksekgonul et al., *TextGrad: Automatic "Differentiation" via Text*, arXiv:2406.07496, 2024.  
https://arxiv.org/abs/2406.07496

**[R20]** Wang et al., *EvoAgentX: An Automated Framework for Evolving Agentic Workflows*, arXiv:2507.03616, 2025.  
https://arxiv.org/abs/2507.03616

**[R21]** Brookes et al., *Evolving Excellence: Automated Optimization of LLM-based Agents*, arXiv:2512.09108, 2025.  
https://arxiv.org/abs/2512.09108

**[R22]** Novikov et al., *AlphaEvolve: A coding agent for scientific and algorithmic discovery*, arXiv:2506.13131, 2025.  
https://arxiv.org/abs/2506.13131

**[R23]** Deng et al., *SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?*, arXiv:2509.16941, 2025.  
https://arxiv.org/abs/2509.16941

**[R24]** Xu et al., *SWE-bench Science: Can Coding Agents Resolve Engineering Tasks in Science?*, arXiv:2608.19799, 2026.  
https://arxiv.org/abs/2608.19799

**[R25]** Meng, Wang & Fang, *SkillRAE: Agent Skill-Based Context Compilation for Retrieval-Augmented Execution*, arXiv:2605.10114, 2026.  
https://arxiv.org/abs/2605.10114

**[R26]** Joshi, Chowdhury & Uysal, *SWE-Bench-CL: Continual Learning for Coding Agents*, arXiv:2507.00014, 2025.  
https://arxiv.org/abs/2507.00014

---

# 194. Closing Statement

Coding Max asks:

> What is the strongest workflow we can engineer?

FORGE asks:

> What is the smallest programmable harness that lets a strong model engineer its own strategy?

CHIMERA asks:

> **What if software engineering capability emerges from coordinating the best algorithm, model, solver, memory, search strategy, and learned skill for each decision — and the system gets measurably better at making those choices over time?**

That is the third architectural bet.

## Wave acceptance

Accept only after focused unit, contract, integration, and falsifier tests for this wave pass; boundary/domain-blindness/TCB linters remain green; optional dependencies fail closed; and no benchmark claim is made from unexecuted evaluation. Full-suite execution is deferred until final integration as requested.
