---
id: research.coding-harness-agentic-systems-engineering
kind: research
status: reference
authority: non-canonical
summary: "Comprehensive research on harness and agentic systems engineering for coding agents."
topic:
  - coding-harness
---
# Research: Harness & Agentic Systems Engineering

**Filename:** `research_harness_agentic_systems_engineering.md`  
**Document class:** consolidated research corpus / technical synthesis  
**Scope:** agentic harness engineering, general task-solving systems, multi-agent coordination, compositional runtimes, evidence, learning, context engineering, verification, provenance, and self-improving workflows  
**Posture:** **research, not development plan**  
**Source corpus:** `001_alfa_review_full_decision.md`, `002_beta_review_full_gem_proposal.md`, `004_delta_review_full_glm53_proposal.md`, `005_epsilon_review_full_dsv4-proposal.md`, `006_fi_review_full_gptsol_proposal.md`, `007_zeta_review_full_opus_proposal.md`, `008_alfa_review_full_grok_proposal.md`, `009_beta_review_higgs_gem.md`, `010_fi_review_higgs_gpt.md`

---

## Abstract

This report consolidates the research content distributed across the AETHER/Vanguard review corpus into a single non-normative body of knowledge. The original reports mix three different kinds of material: (1) forensic observations about particular repository snapshots, (2) architectural and execution proposals, and (3) reusable scientific and engineering ideas. This document intentionally extracts the third category.

The central research thesis is that **agent capability is not determined by the model alone**. It emerges from the interaction among model, context policy, tool surface, memory, orchestration, resource allocation, verification, state, provenance, and learning. The **harness** therefore becomes an independent experimental variable and, at a higher level, a search space over computational regimes.

Several complementary hypotheses recur throughout the source corpus:

1. **Harness-as-independent-variable:** the same model can exhibit materially different performance under different context, tool, loop, and verification regimes.
2. **Separability:** the system that produces an answer should be separable from the system that judges it; evaluation becomes more trustworthy when the evaluated process cannot author or influence the authoritative verdict.
3. **State-mediated coordination:** multi-agent systems can coordinate through durable environmental state rather than unconstrained pairwise natural-language messaging.
4. **Composition over specialization:** debate, critic/reviser loops, tree search, swarms, research agents, and coding agents can be represented as compositions over reusable primitives rather than separate monolithic runtimes.
5. **Evidence-complete trajectories:** trustworthy action/state/evidence traces are a strategic asset for debugging, scientific comparison, routing, skill synthesis, macro compilation, and preference optimization.
6. **Feasibility before optimization:** capability, security, evidence, and resource ceilings form hard constraints; cost, tokens, latency, and expected quality are optimized only inside that feasible region.
7. **Deterministic compounding before statistical compounding:** cache exact verified work first, then compile recurring successful procedures, then learn skills/routes, and only later optimize models or harnesses statistically.
8. **Measured generality:** a framework is general only if materially different task domains can use the same substrate semantics without adding domain-specific authority or execution logic.

The result is a research map rather than an implementation sequence. Competing ideas are retained as alternatives and explicit tensions, with equations, workflows, testable predictions, and references preserved for later evaluation.

---

# 1. Epistemic Posture

## 1.1 What this document is

This document is a **research notebook at architectural scale**. It is intended to support future decisions by organizing:

- hypotheses;
- conceptual primitives;
- mathematical formulations;
- alternative architectures;
- agent and swarm workflows;
- context and memory techniques;
- verification and provenance methods;
- learning and compounding mechanisms;
- benchmark and experimental methodology;
- external papers and systems worth studying;
- open research questions.

It is deliberately suitable for asking questions such as:

> Which coordination model should be tested?

> Should the loop be universal or replaceable?

> Is Active Inference actually useful for routing?

> When does multi-agent decomposition beat one stronger agent?

> What is the correct unit for reusable learned behavior: memory, skill, macro, workflow, or policy?

> Which information must be recorded to make harness experiments scientifically meaningful?

## 1.2 What this document is not

This document is **not**:

- a milestone roadmap;
- an ADR catalog;
- a sprint plan;
- a statement of current repository truth;
- an implementation authorization;
- a frozen architecture;
- a migration plan;
- a product release schedule.

Names such as `M-4`, `M-7`, `ADR-008x`, `NOVA-*`, or particular historical branch/commit states appear in the source corpus, but are not necessary to the research ideas and are therefore omitted except where useful for provenance.

## 1.3 Source-snapshot caution

The reports span different repository snapshots and dates. Some later reports explicitly correct factual or mathematical claims from earlier reports. Therefore:

- repository-state claims should be reverified against current code before use;
- benchmark percentages and product-behavior claims should be treated as reported observations unless independently reproduced;
- proposal convergence is evidence of recurring design intuition, not proof;
- the equations and methods below are research candidates, not automatic normative constraints.

---

# 2. Research Map

The consolidated research can be organized into eleven interacting domains:

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                     AGENTIC SYSTEMS ENGINEERING MAP                       │
├────────────────────────────────────────────────────────────────────────────┤
│  1. Harness Engineering        model ≠ agent ≠ harness                    │
│  2. Composition                components, bindings, topologies            │
│  3. Authority & Safety         capabilities, budgets, isolation            │
│  4. State & Coordination       events, artifacts, stigmergy, obligations  │
│  5. Context Engineering        retrieval, compression, cache alignment     │
│  6. Verification              exterior judges, witnesses, evidence         │
│  7. Provenance & Identity      digests, causal lineage, replay              │
│  8. Adaptive Control           Pareto routing, escalation, Active Inference │
│  9. Compounding                memo → macro → skill → policy/harness        │
│ 10. Multi-Agent Systems        delegation, branching, debate, swarms        │
│ 11. Scientific Method          paired trials, falsifiers, ablation, stats  │
└────────────────────────────────────────────────────────────────────────────┘
```

These areas should not be studied independently. For example, a powerful router without trustworthy telemetry learns from bad data; a reusable macro without least-privilege inference may silently widen authority; a multi-agent topology without attribution makes it impossible to know which component helped.

---

# 3. Core Research Hypotheses

## H1 — Harness Engineering Is a Primary Performance Variable

A useful decomposition is:

\[
\text{Observed Capability}
=
f(
\text{Model},
\text{Harness},
\text{Task},
\text{Environment},
\text{Evaluator}
).
\]

The harness includes:

- system/developer instructions;
- tool definitions;
- context selection;
- memory;
- retrieval;
- model routing;
- planning loop;
- delegation policy;
- stopping policy;
- budget;
- sandbox;
- verification;
- retry/escalation behavior.

The important implication is experimental: a model benchmark that does not freeze the harness is not purely a model benchmark.

### Research consequences

- Treat harness identity as an experimental variable.
- Compare models under identical harnesses and harnesses under identical models.
- Log enough configuration to reproduce the actual informational regime.
- Avoid attributing a benchmark gain to the model if the harness changed simultaneously.

---

## H2 — The Separability Thesis

A recurring principle across the reports is:

> What solved the problem should be separable from what judged the solution.

Let task domain \(d\), task instance \(x\), harness \(H_d\), universal execution mechanism \(U\), and domain verifier \(V_d\) be separated:

\[
\operatorname{Result}(d,x)
=
V_d\left(U(\operatorname{compile}(H_d),x)\right).
\]

The research claim is not that this decomposition is universally sufficient. The claim is that it produces unusually strong properties:

- cleaner evaluation;
- lower reward-channel manipulation;
- clearer provenance;
- reusable execution semantics;
- better training labels;
- better failure attribution.

### Stronger variant

The evaluator should be:

- independently addressed;
- subject-bound;
- unable to be modified by the worker;
- unable to expose private reference answers to the worker;
- cryptographically or structurally attributable where possible.

### Research question

How much robustness is gained by **structural evaluator separation** relative to prompt-level “self-critique” or agent-as-judge patterns?

---

## H3 — Composition Is a Better Generalization Axis Than New Engines

A general agentic system can be modeled as:

\[
H=(C,B,P,R,E),
\]

where:

- \(C\): named components;
- \(B\): bindings between components;
- \(P\): policy;
- \(R\): resources and capability ceilings;
- \(E\): evaluation/witness configuration.

The important distinction is:

> A **bag of components** is not a composition graph.

A useful graph needs both nodes and explicit relationships.

Examples of bindings:

- context → planner;
- planner → toolkit;
- planner → critic;
- candidate → evaluator;
- parent → child spawn grant;
- route → model provider;
- artifact → verifier.

### Hypothesis

Many agent architectures differ primarily in component topology and policy, not in fundamental execution semantics.

Potentially expressible as composition:

- ReAct;
- gather–act–verify;
- generator–critic;
- planner–executor–verifier;
- debate;
- tree search;
- best-of-N;
- reflection;
- research scout → synthesizer;
- hierarchical delegation;
- evolutionary candidate search.

This hypothesis is falsified if a useful class of algorithms repeatedly requires a different privileged execution kernel.

---

## H4 — State-Mediated Coordination Can Replace Much Peer Chatter

The source corpus uses **stigmergy** as the analogy: agents coordinate by changing a shared environment rather than continuously messaging each other.

Represent a shared workspace as:

\[
\mathcal W=
\langle
\mathcal A,
\mathcal H,
\mathcal E,
\mathcal T
\rangle
\]

where:

- \(\mathcal A\): artifacts;
- \(\mathcal H\): hypotheses / derived work state;
- \(\mathcal E\): evidence and event history;
- \(\mathcal T\): telemetry and cost.

A more conservative interpretation is preferable:

- authoritative facts are durable events and immutable artifacts;
- hypotheses are derived projections;
- large content lives in a blob/artifact store;
- semantic indexes are rebuildable projections;
- natural-language messages, if present, are observations rather than authority.

### Complexity claim — corrected

A full all-to-all round can produce:

\[
N(N-1)=O(N^2)
\]

directed messages.

State mediation does **not** magically prove \(O(N)\). A defensible bound is:

\[
O(cN)
\]

coordination operations per round if each of \(N\) agents performs at most \(c\) indexed state operations.

The real system must still measure:

- database contention;
- hot keys;
- bytes read/written;
- retries;
- queueing;
- model calls;
- critical path;
- synchronization overhead.

---

## H5 — Trustworthy Trajectories Are a Strategic Data Asset

A useful trajectory is not merely a transcript. It should bind:

- task identity;
- harness identity;
- run identity;
- component/model identities;
- observations;
- proposals;
- authorization decisions;
- effects;
- receipts;
- artifacts;
- evaluator evidence;
- token/cost/latency measurements;
- causal and derivation lineage;
- error taxonomy;
- terminal result.

This produces a corpus usable for:

- replay;
- failure localization;
- cost modeling;
- routing;
- skill discovery;
- macro mining;
- preference pair extraction;
- benchmark analysis;
- regression detection;
- scientific reproducibility.

### Key rule

Unknown cost is **unknown**, not zero.

Fabricated zeros destroy downstream economics because they make “not measured” indistinguishable from “free”.

---

## H6 — Feasibility Must Precede Optimization

Resource, authority, evidence, and safety constraints should be hard gates.

Only then should the system optimize:

- cost;
- tokens;
- latency;
- quality;
- information gain;
- reliability;
- throughput.

This naturally suggests a **partial-order / Pareto** formulation rather than one global scalar reward.

---

## H7 — Compounding Should Progress From Deterministic to Statistical

The source corpus converges on a four-tier compounding ladder:

```text
T0  exact verified reuse
 ↓
T1  verified macro/procedure compilation
 ↓
T2  skill retrieval + routing adaptation
 ↓
T3  model/harness learning and evolution
```

The rationale is epistemic.

If exact repetition can be removed deterministically, there is no reason to begin with stochastic learning. Statistical methods become valuable only after a trustworthy corpus and stable evaluation semantics exist.

---

# 4. Fundamental Primitives

## 4.1 Artifact

A content-addressed object produced, consumed, or transformed by execution.

Examples:

- source tree;
- patch;
- test report;
- paper snapshot;
- extracted table;
- proof script;
- research report;
- model output;
- compiled macro.

Desirable properties:

- immutable identity;
- provenance;
- content digest;
- policy/retention metadata;
- derivation refs.

---

## 4.2 Event

A small authoritative record of an observable occurrence.

Useful separation:

```text
event envelope      identity + ordering + causation
typed payload       operational fact
blob/artifact       large body
projection/index    rebuildable derived state
metrics warehouse   aggregate analysis
```

The event stream should not be treated as a place to dump unlimited raw content.

---

## 4.3 Effect

An externally meaningful action:

- file mutation;
- process execution;
- network request;
- tool invocation;
- child creation;
- database mutation;
- deployment action.

A robust system distinguishes:

```text
proposal → authorization → intent → execution → receipt → settlement
```

This distinction is particularly important for crash recovery and idempotency.

---

## 4.4 Capability

An explicit right to perform a class of effects against a bounded selector.

Research-relevant properties:

- fail closed;
- least privilege;
- descriptor-bound;
- attenuated during delegation;
- separable from natural-language instructions.

A child should generally satisfy:

\[
C_{child}\subseteq C_{parent}.
\]

---

## 4.5 Witness

A witness is the evidence contract used to evaluate an obligation or claim.

Examples:

- `tests_green`;
- `proof_checks`;
- `schema_conforms`;
- `replay_equivalent`;
- `citation_entails_claim`;
- `human_signed`;
- `panel_adjudicated`.

This is broader and more reusable than a binary “grader”.

---

## 4.6 Obligation

One alternative research abstraction treats the schedulable unit as a typed obligation:

\[
o=
\langle
g,w,\mathbf R_{max},d,\mathcal D,p,\kappa
\rangle
\]

with:

- goal \(g\);
- witness contract \(w\);
- resource ceiling \(\mathbf R_{max}\);
- deadline \(d\);
- dependencies \(\mathcal D\);
- parent \(p\);
- protection/capability class \(\kappa\).

Identity:

\[
D_O=
H(
\operatorname{JCS}
(g,w,\mathbf R_{max},d,\mathcal D,p,\kappa)
).
\]

A refinement operator may solve or decompose:

\[
\operatorname{Refine}_r(o)
\rightarrow
\begin{cases}
\widehat w(o), & \text{candidate discharge},\\
\{o_1,\ldots,o_m\},\Gamma, & \text{decomposition + composition rule}.
\end{cases}
\]

### Research tension

Should **obligation** replace the turn as the primary system primitive, or remain an exterior scheduling abstraction over a universal turn/effect mechanism?

The source corpus ultimately favors the latter, but the former remains useful as an experimental architecture.

---

# 5. Resource Algebra and Economics

## 5.1 Six-Dimensional Resource Tensor

The source corpus models resources as:

\[
\mathbf R=
(r_{\$},r_{tok},r_{byte},r_{ms};r_{turn},r_{depth})
\in
\mathbb N^4_{add}\times\mathbb N^2_{struct}.
\]

The first four are additive:

- money;
- tokens;
- bytes;
- charged time.

The last two are structural:

- turns;
- lineage depth.

Feasibility is component-wise:

\[
\mathbf R_a\preceq\mathbf R_b
\iff
\bigwedge_j R_{a,j}\le R_{b,j}.
\]

This is a **product partial order**. It intentionally prevents arbitrary statements such as “more dollars compensate for excessive depth”.

For child leases:

\[
\sum_i L_{i,j}+L_{remaining,j}=L_{parent,j}
\]

for additive dimensions \(j\), while structural constraints can be:

\[
turn_i\le turn_p,
\qquad
depth_i<depth_p.
\]

## 5.2 Why not one scalar?

A scalar objective such as:

\[
S = w_1Q-w_2C-w_3T-w_4L
\]

is convenient but dangerous if it allows a gain in one dimension to compensate for a violated invariant.

A better structure is:

1. authority feasible?
2. isolation feasible?
3. evidence feasible?
4. resource feasible?
5. quality/witness floor met?
6. Pareto comparison among feasible choices;
7. product-specific tie breaking.

---

# 6. Pareto Harness and Adaptive Routing

## 6.1 Quote Representation

For obligation \(o\), refinement \(r\), model \(m\), context policy \(b\), and parallel width \(k\):

\[
q=
(o,r,m,b,k,
\widehat{\mathbf c},
\widehat p_{pass},
\widehat I,
\widehat q_{evidence})
\]

where:

- \(\widehat{\mathbf c}\): predicted resource use;
- \(\widehat p_{pass}\): calibrated success probability;
- \(\widehat I\): expected information gain;
- \(\widehat q_{evidence}\): assurance/witness quality.

The quote is advisory. Measurement settles reality.

## 6.2 Multi-objective Allocation

A scheduling epoch can be viewed as:

\[
\max_x
\left(
\sum_q x_q\widehat p_{pass,q}V_q,
\sum_q x_q\widehat I_q,
-\sum_q x_q\widehat{\mathbf c}^{add}_q,
-\operatorname{critical\_path}(x)
\right)
\]

subject to:

\[
\sum_qx_q\widehat c_{q,j}\le R_{remaining,j},
\qquad
x_q\in\{0,1\}
\]

plus:

- capability;
- dependency;
- worker-count;
- exclusivity;
- protection;
- turn/depth;
- witness constraints.

## 6.3 Execution Profiles as Priors

Useful research profiles:

| Profile | Main objective | Typical topology |
|---|---|---|
| `flash` | low latency/cost | memo/macro, then one small worker |
| `balanced` | cost per verified success | scout/context projection → executor → verifier |
| `certain` | assurance | independent candidates + stronger verification |
| `frontier` | information gain | diverse controlled branches |
| `adaptive` | cheapest feasible policy first | escalate only after evidence |

Historical proposals contain specific latency/token bands. Those are best treated as **benchmark hypotheses**, not architecture.

## 6.4 Adaptive Escalation Workflow

```text
classify task
   ↓
choose cheapest plausible profile
   ↓
execute under bounded lease
   ↓
external verification
   ├── pass → commit evidence
   └── fail → retain falsifier + workspace delta
                ↓
             escalate
                ↓
       stronger model/context/topology
```

Important idea:

> Carry forward the **falsifier and relevant state delta**, not necessarily the full transcript.

This attempts to reduce context growth while preserving the information that justifies escalation.

---

# 7. Active Inference — Correct Separation of VFE and EFE

Several early reports conflated Variational Free Energy and action selection. Later reports correct this.

## 7.1 Variational Free Energy — Belief Fitting

Let:

- \(s\): latent state;
- \(o\): observations/evidence;
- \(\tau=(o_{0:T},a_{0:T-1})\): trajectory;
- \(q_\phi(s|\tau)\): approximate posterior;
- \(p_\theta(\tau,s)\): generative model.

Then:

\[
\mathcal F(\phi,\theta;\tau)
=
\mathbb E_{q_\phi(s|\tau)}
[
\log q_\phi(s|\tau)
-
\log p_\theta(\tau,s)
]
\]

or:

\[
\mathcal F
=
D_{KL}
(
q_\phi(s|\tau)
\Vert
p_\theta(s|\tau)
)
-
\log p_\theta(\tau).
\]

Interpretation:

> VFE updates beliefs after observations.

## 7.2 Expected Free Energy — Policy Selection

For candidate policy \(\pi\):

\[
\mathcal G(\pi)
=
\mathbb E_{q(o,s|\pi)}
[
\log q(s|\pi)-\log p_C(o,s)
].
\]

Interpretation:

> EFE ranks candidate policies using pragmatic and epistemic value.

## 7.3 Resource-Constrained Form

\[
\theta^*=
\arg\min_{\theta\in\Theta}
\left(
\mathbb E[\mathcal G(\pi_\theta)]
+
\sum_j \lambda_j\mathbb E[c_j(\theta)]
\right)
\]

subject to resource and safety constraints.

### Practical mapping

| Active-Inference concept | Agentic-system interpretation |
|---|---|
| observation | ledger facts, receipts, artifacts, evaluator evidence |
| latent state | progress, failure class, dependency validity, uncertainty |
| policy | model route, context projection, topology, tool/macro choice |
| preferences | witness success + invariant preservation + budget |
| VFE | belief update |
| EFE | next-action policy ranking |

### Research question

Does EFE-based routing provide measurable advantage over:

- calibrated Bayesian expected utility;
- contextual bandits;
- Pareto heuristics;
- learned cost/pass regressors?

The answer should be empirical, not terminological.

---

# 8. Dynamic Informational Bottleneck

One proposal formalizes context compilation as:

\[
\mathcal B_\theta:
\mathcal W
\times
\text{TaskProfile}
\rightarrow
\text{ContextWindow}_{\le k}.
\]

This is one of the strongest general abstractions in the corpus.

The model should not consume the entire state. It should consume a **task-conditioned projection**.

Candidate input layers:

```text
L0  immutable system / safety / task identity
L1  tool or interface summaries
L2  structural map / repository or source map
L3  relevant artifacts and evidence
L4  recent trajectory and unresolved failures
L5  optional skills / examples / retrieved procedures
```

## 8.1 Context selection requirements

A robust compiler should retain:

- source identities;
- protection labels;
- omissions;
- compaction lineage;
- retrieval scores/rationales;
- token cost by layer.

## 8.2 Progressive disclosure

A recurring pattern:

1. always-on minimal law/task identity;
2. small descriptions of available skills/tools;
3. load full definitions only when needed;
4. retrieve ranked evidence/code excerpts;
5. retain bounded recent execution state;
6. compact old detail structurally;
7. rehydrate exact immutable artifacts when precision is required.

This aligns with later analysis of Claude Code and with the source corpus’s context-economy thesis.

---

# 9. Context Caching and Prefix Stability

A major practical research direction is **cache-aware prompt architecture**.

## 9.1 Prefix stability

Keep recurring content byte-stable and early:

```text
system policy
→ project instructions
→ stable tool definitions
→ stable repository/source map
→ mutable task history
```

Potential benefits:

- provider KV/prompt-cache reuse;
- reduced input cost;
- reduced latency;
- less repeated tokenization.

Historical source reports cite very large percentage improvements for specific systems. Those values should be independently benchmarked before being generalized.

## 9.2 Cache taxonomy

Useful caches include:

- provider prefix cache;
- tokenization cache;
- parsed document cache;
- AST cache;
- repository index shards;
- deterministic model call cache;
- pure observation/tool cache;
- exact witness/evaluator cache;
- context-compilation cache.

### Cache law

> A cache key must bind every behavior-affecting input.

A cache hit should produce observable evidence:

- cache key;
- source artifact;
- age;
- identity inputs;
- validation result;
- hit/miss;
- invalidation reason.

---

# 10. Repository and Knowledge Mapping

Coding agents need compressed structural awareness.

## 10.1 AST/Symbol Repo Map

Candidate pipeline:

```text
files
  ↓
Tree-Sitter / parser
  ↓
symbols + signatures + imports + references
  ↓
dependency graph
  ↓
ranking
  ↓
compact repo map
```

Possible ranking:

- PageRank;
- centrality;
- changed-file proximity;
- query-specific lexical score;
- symbol references;
- test ownership.

## 10.2 Incremental Indexing

Rather than rebuilding the full map:

```text
git diff / file hash change
      ↓
invalidate changed shards
      ↓
reparse affected files
      ↓
update graph/index
```

## 10.3 Generalization to research

The same idea extends beyond code:

- source catalog;
- citation graph;
- entity/time index;
- claim-to-source index;
- dataset schema graph;
- experiment lineage.

---

# 11. Hybrid Retrieval and Skill Memory

## 11.1 Dense + Lexical Retrieval

For query \(q\) and skill/item \(i\):

\[
s_d(i)=
\frac{e(q)^Te(i)}
{\|e(q)\|_2\|e(i)\|_2}
\]

\[
s_l(i)=
\operatorname{norm}_{[0,1]}
(
\operatorname{BM25}(q,i)
)
\]

combined as:

\[
s(i)=
\alpha s_d(i)
+
\beta s_l(i)
+
\eta L_i
+
\zeta C_i
-
\kappa A_i
\]

where:

- \(L_i\): evidence-backed lift;
- \(C_i\): reliability;
- \(A_i\): staleness/invalidation risk.

The 384-dimensional embedding used in some proposals should be understood as one implementation profile, not a universal requirement.

## 11.2 Hard filters before similarity

Before semantic scoring:

- tenant/project;
- protection class;
- invalidation state;
- required interface;
- schema version;
- capability compatibility.

Similarity should never override policy constraints.

---

# 12. Skill Dynamics and Evidence-Weighted Retention

One candidate model uses Elo-like updates.

For skill \(i\) vs baseline \(b\):

\[
p_i=
\frac{1}
{1+10^{(\mu_b-\mu_i)/400}}
\]

\[
\mu_i'
=
\mu_i+
K(n_i)w_i(y_i-p_i)
\]

where:

- \(y_i\in\{0,\frac12,1\}\);
- \(K(n_i)\) decreases with evidence;
- \(w_i\) is attributable contribution.

Unsigned/self-scored outcomes should have:

\[
w_i=0.
\]

Idle confidence can decay toward a prior:

\[
\mu_i(t)
=
\mu_0+
(\mu_i(t_0)-\mu_0)e^{-\lambda(t-t_0)}.
\]

A conservative utility:

\[
U_i
=
\operatorname{LCB}_{1-\alpha}(\Delta success_i)
-\lambda_c\Delta cost_i
-\lambda_t\Delta latency_i
-\lambda_r risk_i.
\]

### Research questions

- Elo vs Bayesian hierarchical models?
- Per-task-class vs global rating?
- How many paired trials are required before retrieval priority changes?
- How should correlated skills be credited?
- When should a skill become a deterministic macro?

---

# 13. Stigmergic Multi-Agent Coordination

## 13.1 Shared-State Work Protocol

A useful generic workflow:

```text
publish work item / obligation
        ↓
worker claims expected version + lease
        ↓
compare-and-swap / exclusive claim
        ↓
worker executes under attenuated authority
        ↓
publish immutable artifacts + witness refs
        ↓
release claim
```

Crash handling should distinguish:

- safe retry;
- known completed effect;
- unknown external effect;
- expired claim;
- unresolved durable intent.

## 13.2 Why state mediation may help

Potential benefits:

- lower social coordination noise;
- better provenance;
- reduced context duplication;
- asynchronous workers;
- easier recovery;
- natural work queues;
- measurable contention.

Potential costs:

- stale reads;
- database contention;
- poor schema design;
- hidden coupling through shared mutable artifacts;
- loss of nuance compared with direct discussion.

## 13.3 Direct messaging is not forbidden research

A more nuanced position than “agents never communicate” is:

> Direct messages can exist as **attributed observations**, but should not become an alternate authority, verdict, claim, or promotion channel.

This allows research into hybrid designs.

---

# 14. Delegation and Subagents

## 14.1 Delegation as an Effect

A strong security interpretation is to model spawn/delegation as an ordinary mediated effect rather than an ambient runtime privilege.

Research invariants:

\[
C_{child}\subseteq C_{parent}
\]

\[
R_{child}\preceq R_{parent}
\]

and explicit parent-child provenance.

## 14.2 Context Isolation

Subagents are useful because they provide:

- independent context windows;
- specialization;
- parallel exploration;
- reduced contamination of the main context.

A compact return object might contain:

```text
status
artifact refs
evidence refs
summary
open uncertainty
cost
capability/lease lineage
```

rather than the entire transcript.

## 14.3 Research question

When is subagent isolation better than simply giving the primary model a larger context window?

Relevant variables:

- task decomposability;
- context overlap;
- model strength;
- tool latency;
- coordination overhead;
- verifier quality;
- branch independence.

---

# 15. Agent Topologies Worth Treating as Experimental Variables

## 15.1 Single-agent gather–act–verify

```text
GATHER
  repo/source exploration
  relevant context selection
      ↓
ACT
  minimal targeted operation
      ↓
VERIFY
  tests / proof / citation / schema / oracle
      ↓
repeat only on concrete failure
```

Advantages:

- low complexity;
- high attribution;
- good benchmark baseline.

---

## 15.2 Scout → Executor

```text
Scout
  ↓ structured findings
Executor
  ↓ candidate
Verifier
```

Good for tasks where discovery and mutation require different context.

---

## 15.3 Planner → Implementer → Verifier

Useful when planning and execution authority should differ.

Example:

- planner: broad read, no write;
- implementer: scoped write;
- verifier: independent execution/evaluation.

---

## 15.4 Generator → Critic → Reviser

```text
candidate_0
   ↓
critic evidence
   ↓
revision
   ↓
external verification
```

Important distinction:

> The critic may improve the candidate, but should not automatically be the authoritative evaluator.

---

## 15.5 Best-of-N / Speculative Branching

```text
               ┌→ branch A ─┐
task → branch ─┼→ branch B ─┼→ common evaluator → select
               └→ branch C ─┘
```

Research variables:

- N;
- branch diversity;
- model diversity;
- shared vs isolated context;
- evaluator cost;
- pruning policy;
- total cost per verified pass.

---

## 15.6 Debate

Debate can be modeled as cyclic component interaction.

This motivates an important correction in the source corpus:

> A composition graph need not be acyclic.

Termination can instead be bounded by:

- turns;
- depth;
- time;
- tokens;
- cost;
- explicit convergence rule.

A DAG is appropriate when topology *defines execution order*. It is less appropriate when topology merely defines allowed relationships and a separate turn mechanism controls execution.

---

## 15.7 Tree Search

Candidate dimensions:

- branching factor;
- heuristic;
- rollout depth;
- verifier frequency;
- branch-sharing policy;
- value estimate;
- pruning.

Research question:

Does explicit tree search beat adaptive sequential escalation once the verifier and tool environment are expensive?

---

## 15.8 Swarm / Blackboard

Roles can include:

- decomposer;
- scout;
- worker;
- critic;
- verifier;
- synthesizer.

The scientific question is not “does more agents help?” but:

\[
\Delta Q / \Delta Cost
\]

and the marginal contribution of each added role.

---

# 16. Failure Attribution and Backward Fault Isolation

Each run can form a provenance graph:

\[
G_\tau=
(V,E_c\cup E_d\cup E_a)
\]

where:

- \(E_c\): causation;
- \(E_d\): data/artifact derivation;
- \(E_a\): authority lineage.

For failed claim \(z\), reverse slice:

\[
B(z)
=
\{v\in V\mid v\leadsto z
\text{ through }E_c\cup E_d\}.
\]

Structural slicing is:

\[
O(|V|+|E_c|+|E_d|).
\]

A suspicion score:

\[
S(v)
=
\mathbf 1[v\in B(z)]
\gamma^{dist(v,z)}
(
\alpha q_v+\beta n_v+\chi u_v+\delta \rho_v
)
\]

can rank:

- severity;
- novelty;
- uncertainty;
- cost share.

### Critical epistemic distinction

A reverse slice identifies **possible causal ancestors**, not proof of causation.

Causal claims require:

- intervention;
- ablation;
- paired replay;
- factorial design;
- controlled replacement;
- possibly Shapley-style attribution for interacting components.

---

# 17. Exact Witness Memoization

The first compounding tier should be deterministic.

Memo key:

\[
K_{memo}
=
H(
D_O
\parallel D_{inputs}
\parallel D_{environment}
\parallel D_{checker}
\parallel D_{toolchain}
\parallel assurance
\parallel policy\_version
).
\]

A cache hit should return the original verified witness bundle by reference, not copy a verdict onto a new subject.

Invalidation conditions may include:

- changed input;
- environment drift;
- checker version;
- revocation epoch;
- TTL;
- changed protection class;
- changed policy;
- changed toolchain.

---

# 18. Macro-Tool Compilation

A macro is not simply a saved prompt.

It is a typed executable abstraction mined from recurring successful effect subgraphs.

## 18.1 Research pipeline

```text
verified trajectories
      ↓
find recurring causally connected effect subgraphs
      ↓
anti-unify constants into parameters
      ↓
infer interface + minimum capabilities
      ↓
synthesize workflow IR / implementation
      ↓
generate replay + adversarial/property tests
      ↓
run through ordinary authority/sandbox path
      ↓
evaluate with original witness checker
      ↓
paired comparison vs expanded baseline
```

## 18.2 Least-Privilege Inference

A conservative capability estimate:

\[
C_{macro}
=
\operatorname{hull}
\left(
\bigcup_{v\in subgraph}C_v
\right)
\cap C_{pack}
\cap C_{publisher}.
\]

The `hull` should be the smallest expressible selector set covering required effects.

Reject a macro if the permission model can only express an unacceptably broad grant.

## 18.3 Macro research questions

- How much task diversity is needed before anti-unification is safe?
- How can secrets, benchmark answers, tenant IDs, and incidental paths be prevented from becoming compiled constants?
- What IR best supports polyglot execution?
- When is a macro better than a skill description?
- How should fallback to the expanded procedure be priced?

---

# 19. Compounding Flywheel

The integrated flywheel:

```text
execution
  ↓
evidence-complete trajectory
  ↓
exact witness reuse
  ↓
macro mining
  ↓
skill retrieval
  ↓
routing adaptation
  ↓
preference pairs
  ↓
model / harness experiments
  ↓
future execution
```

Important safety principle:

> Learned state may influence selection, but should not automatically widen authority or declare truth.

---

# 20. Preference Optimization

## 20.1 DPO Objective

For prompt \(x\), preferred completion \(y^+\), rejected completion \(y^-\), policy \(\pi_\theta\), reference \(\pi_{ref}\), and temperature \(\beta\):

\[
\mathcal L_{DPO}(\theta)
=
-\mathbb E
\log
\sigma
\left(
\beta
\left[
\log\frac{\pi_\theta(y^+|x)}{\pi_{ref}(y^+|x)}
-
\log\frac{\pi_\theta(y^-|x)}{\pi_{ref}(y^-|x)}
\right]
\right).
\]

## 20.2 Preference Pair Quality

A useful pair should bind:

- identical or comparable task;
- common prefix until divergence;
- environment;
- oracle;
- seed policy;
- evidence-complete runs;
- independently verified outcomes;
- execution digests;
- explicit pair label rule.

DPO trains against the supplied pair.

It does **not** prove that the pair label is correct.

---

# 21. Statistical Promotion and Harness Experiments

## 21.1 Exact Paired McNemar

For paired binary trials:

- \(b\): candidate passes, baseline fails;
- \(c\): baseline passes, candidate fails;
- \(n_d=b+c\).

Under equal marginal success:

\[
B\sim \operatorname{Binomial}(n_d,\frac12).
\]

Exact two-sided p-value:

\[
p_{exact}
=
\min
\left(
1,
2
\sum_{k=0}^{\min(b,c)}
{n_d\choose k}2^{-n_d}
\right).
\]

## 21.2 Better experimental discipline

A candidate comparison should preregister:

- task set;
- endpoint;
- alpha;
- minimum detectable effect;
- stopping rule;
- multiplicity correction;
- handling of inconclusive/instrument-error runs;
- resource metrics;
- security invariants.

Do not report only p-values.

Also report:

- effect size;
- confidence interval;
- cost;
- tokens;
- latency;
- reliability;
- failure taxonomy.

## 21.3 A/A floor

Before trusting an A/B pipeline, run A/A.

If identical treatments produce unstable differences, the experiment infrastructure itself is noisy.

---

# 22. Harness Genome and Evolution

A harness can be viewed as a genome:

\[
\theta=
(
\text{components},
\text{bindings},
\text{prompts},
\text{model routes},
\text{context policy},
\text{tools},
\text{memory},
\text{topology},
\text{budget},
\text{evaluation}
).
\]

Mutation operators might include:

- replace component implementation;
- change prompt layer;
- alter context budget;
- alter retrieval weights;
- change model route;
- add/remove critic;
- vary branch count;
- change escalation threshold;
- replace tool;
- modify stopping policy.

### Research requirement

Do not mutate several dimensions simultaneously if the goal is causal attribution, unless using a factorial or population-search protocol designed for interactions.

---

# 23. Identity and Provenance

A useful identity trinity appears throughout the corpus:

\[
D_H = \text{harness/composition identity}
\]

\[
D_R = \text{run-plan identity}
\]

\[
D_X = \text{execution/event-chain identity}.
\]

One possible harness identity:

\[
D_H
=
H(
\operatorname{JCS}
(\text{resolved composition graph})
).
\]

A run identity can bind:

- task;
- workspace/source state;
- model route;
- budget;
- environment;
- evaluator.

Execution identity can bind the event sequence or hash chain.

### Why separate them?

Because these answer different questions:

- “What behavior configuration was intended?”
- “What exact experiment/run cell was requested?”
- “What actually happened?”

Collapsing them destroys useful denominators.

---

# 24. Event-Sourced Scientific Observability

Scientific logging should capture observable transformations, not hidden chain-of-thought.

Recommended event families:

- model request prepared;
- model invocation started/completed/failed;
- context layer selected;
- context transformed/compacted/rehydrated;
- tool request proposed/authorized/started/settled/denied;
- source acquired/normalized/extracted/cited;
- artifact created/transformed/evaluated;
- cache lookup/hit/miss/write/eviction;
- evaluator request/verdict/verification;
- child lifecycle and budget transfer;
- recovery/reconciliation.

Useful common fields:

- project/run/episode/branch/principal;
- sequence;
- schema version;
- producer;
- causation/correlation;
- input/output refs;
- model/environment digests;
- capability/grant;
- budget reservation/settlement;
- timing;
- token/cost;
- error taxonomy;
- idempotency;
- terminal state.

---

# 25. Replay, Fork, Resume, and Cold Recovery

Append-only history enables four different operations:

## Replay

Recompute derived state from recorded events.

## Resume

Continue an interrupted run after reconstructing state.

## Fork

Create a new branch from a prior state while preserving lineage.

## Counterfactual Replay

Re-run from a point with one controlled change.

These capabilities are particularly powerful for agent research because they make:

- ablation cheaper;
- bugs reproducible;
- alternative policies comparable;
- state corruption easier to detect.

### Important distinction

Event replay does not automatically make external side effects exactly-once.

Durable intent + idempotency + effect reconciliation are still required.

---

# 26. External Tool Protocols and MCP

MCP-like protocols are useful as **interoperability layers**, not authority boundaries.

A safe abstraction:

```text
external tool discovery
      ↓
normalize schema
      ↓
bind selector/capability policy
      ↓
ordinary authorization
      ↓
invoke
      ↓
receipt + provenance
```

Research questions:

- How much tool-schema context should be loaded eagerly?
- Can tool discovery itself be retrieved on demand?
- How should remote tool identity/version be hashed?
- What permissions should be inferred vs explicitly configured?
- How should MCP server changes invalidate cached behavior?

---

# 27. Plugins: “Everything Is a Plugin” vs Small Trusted Core

This is one of the major architectural tensions.

## Extreme A — Everything Is a Plugin

Potentially replaceable:

- model;
- loop;
- scheduler;
- memory;
- sandbox;
- tools;
- storage;
- UI;
- sessions.

Advantages:

- maximal experimentation;
- low central coupling;
- broad ecosystem.

Risks:

- inconsistent authority;
- multiple sources of truth;
- plugin-owned privileged history;
- unbounded trust surface.

## Extreme B — Small Rigid Mechanism + Replaceable Exterior

Keep only trust semantics non-replaceable:

- canonicalization;
- authorization;
- capability attenuation;
- budget algebra;
- durable intent;
- privileged event ownership;
- evidence verification.

Everything else can vary.

### Research synthesis

The reports consistently prefer:

> **flat, highly composable surface; rigid, minimal trust core.**

But the “everything is a plugin” extreme remains valuable as a comparative research architecture.

---

# 28. Universal Turn Loop vs Pluggable Loops

A candidate universal loop:

```text
observe
  ↓
propose
  ↓
authorize
  ↓
effect
  ↓
receipt
  ↓
evaluate
  ↓
reflect / continue
```

Hypothesis:

> A large family of agent algorithms can be represented as topology + policy over this mechanism.

Competing hypothesis:

> The loop itself should be a plugin because different domains require fundamentally different execution semantics.

### Test

Collect algorithms that resist representation through the universal mechanism.

Potential counterexamples to investigate:

- continuous control;
- real-time streaming systems;
- asynchronous market/event systems;
- differentiable planning;
- large distributed consensus;
- simulation-heavy scientific workflows;
- agents with persistent background processes.

The universal-loop thesis should survive counterexamples, not slogans.

---

# 29. Turn-Centric vs Obligation-Centric Systems

## Turn-centric

Primary unit:

- observation;
- proposal;
- effect;
- receipt.

Strengths:

- simple;
- matches interactive agents;
- natural security mediation.

## Obligation-centric

Primary unit:

- goal;
- witness;
- dependencies;
- resource price;
- claim/lease;
- refinement.

Strengths:

- scheduler-friendly;
- naturally supports decomposition;
- explicit completion semantics;
- work stealing;
- memoization.

### Hybrid hypothesis

Use:

- obligations for work planning/scheduling;
- turns/effects for execution and authority.

This retains a single effect mechanism while allowing richer work semantics.

---

# 30. Outcome/Data-First vs Substrate-First

The source corpus contains a genuine higher-level alternative.

## Substrate-first

Question:

> What minimal trusted mechanism makes arbitrary agentic behavior safe, attributable, and reproducible?

Strength:

- rigorous invariants;
- stable trust semantics;
- high-quality data.

Risk:

- architecture may advance faster than user-visible capability.

## Outcome/data-first

Question:

> Which informational configuration produces the best verified result per cost/token/time?

Strength:

- naturally optimization-oriented;
- product feedback arrives early;
- harness search is central.

Risk:

- evaluation and provenance may be bolted on too late;
- a weak corpus can make optimization self-deceptive.

## Convergence

Both approaches eventually require:

- separability;
- component composition;
- state;
- identity;
- evidence;
- bounded resources;
- trustworthy trajectories.

This makes the difference one of **center of gravity**, not necessarily final principles.

---

# 31. Coding-Agent Research Patterns

The reports identify several techniques that deserve isolated evaluation.

## 31.1 Gather–Act–Verify

Already covered as a topology, but particularly strong for coding.

## 31.2 Repo Map

- Tree-Sitter;
- symbol extraction;
- imports/references;
- PageRank/centrality;
- changed-file bias;
- compact structural prompt.

## 31.3 AST-Aware Patching

Compare:

- line replacement;
- unified diff;
- fuzzy patch;
- AST transformation;
- syntax-tree constrained edit.

Metrics:

- patch validity;
- minimality;
- retry rate;
- token cost;
- semantic regression.

## 31.4 Test-Driven Feedback

Tool outputs should be compressed into:

- failing test names;
- stack traces;
- assertion diffs;
- exit codes;
- changed files.

Avoid repeatedly injecting huge raw logs.

## 31.5 Benchmark-Minimal Mode

DeepSeek-inspired concept:

> remove optional harness assistance to measure the model/tool loop cleanly.

This is useful for decomposing benchmark gains.

---

# 32. Research-Agent Patterns

A domain-independent researcher can be decomposed as:

```text
question
   ↓
query planner
   ↓
parallel source scouts
   ↓
acquisition + normalization
   ↓
atomic fact / claim extraction
   ↓
citation binding
   ↓
contradiction / uncertainty analysis
   ↓
synthesis
   ↓
exterior citation/factuality verification
```

Important properties:

- immutable source refs or snapshots;
- source-span citations;
- distinction between source statement and inference;
- temporal metadata;
- contradictory evidence retained;
- reproducible export.

### Research metrics

- citation precision;
- claim entailment;
- source diversity;
- contradiction recall;
- time freshness;
- retrieval cost;
- synthesis token cost;
- verifier agreement.

---

# 33. Structured Compaction

Compaction should preserve state, not merely summarize prose.

A compacted state may explicitly retain:

- task objective;
- accepted decisions;
- rejected hypotheses;
- open questions;
- modified artifacts;
- failing invariants;
- pending intents;
- evidence refs;
- source digests.

Compression itself should have provenance:

```text
source range
compactor identity
instructions
output digest
token counts
rehydration link
```

### Research question

Which compaction representation preserves downstream performance best?

Candidates:

- prose summary;
- structured JSON state;
- key-value decision ledger;
- graph summary;
- vector retrieval + short state;
- hybrid.

---

# 34. Hooks, Skills, Tools, Instructions, and Agents Should Remain Distinct

Later source analysis of Claude Code argues for a useful taxonomy.

| Mechanism | Meaning |
|---|---|
| Instructions | persistent behavioral context |
| Skill | model-interpreted reusable knowledge/procedure |
| Tool | externally executed capability |
| Hook | deterministic lifecycle-triggered automation |
| MCP integration | external tool/service protocol |
| Subagent | isolated reasoning/execution context |
| Plugin | packaging/distribution unit |

Collapsing all of these into “plugins” can hide important semantic differences.

Example:

> A skill says *how* the model might do something. A capability decides whether it *may* do it. A hook deterministically triggers something. A tool performs an external operation.

---

# 35. Security and Isolation Research

Relevant mechanisms in the corpus include:

- capability-based authorization;
- rootless sandboxing;
- Linux Landlock;
- namespaces;
- `no_new_privs`;
- seccomp/LSM;
- network denial;
- explicit filesystem selectors;
- separate evaluator boundary;
- typed budgets.

Research principle:

> “Uses a sandbox” is not a security claim. The policy and configured arguments determine the protection.

Research comparisons should test:

- host process;
- namespace sandbox;
- container;
- microVM;
- WASM;
- remote isolated worker.

Metrics:

- escape surface;
- startup latency;
- memory;
- filesystem fidelity;
- network policy;
- portability;
- debugging cost.

---

# 36. Provenance Standards and Canonicalization

The reports reference:

- RFC 8785 JSON Canonicalization Scheme;
- W3C PROV;
- SLSA provenance;
- in-toto attestation.

Useful research question:

> How much of agent execution provenance should reuse existing supply-chain provenance standards versus an agent-specific event vocabulary?

Potential mapping:

- entity → artifact;
- activity → tool/model/effect execution;
- agent → principal/component;
- derivation → artifact edge;
- builder → runtime/harness identity;
- subject → evaluated artifact/run.

---

# 37. Research Methodology

## 37.1 Evidence Hierarchy

A good general hierarchy:

1. directly measured execution;
2. source code / machine-verifiable artifact;
3. first-party technical documentation;
4. peer-reviewed paper;
5. preprint with released artifacts;
6. independent reproduction;
7. engineering report;
8. proposal/hypothesis;
9. anecdote.

The order may vary by question, but the principle is:

> architecture should not silently promote a hypothesis into a fact.

## 37.2 Falsifier-First Design

For every strong claim, write the test that could refute it.

Examples:

| Claim | Falsifier |
|---|---|
| composition graph is general | topology requires engine/domain-specific branch |
| state-mediated coordination scales | coordination cost becomes dominant |
| cold recovery is sufficient | fresh process cannot reconstruct continuation |
| macro preserves semantics | replay differs under held-out inputs |
| skill improves outcomes | paired trials show no lift |
| routing saves cost | cost/pass exceeds fixed baseline |
| second domain proves generality | requires core semantic changes |

## 37.3 Intervention Before Causation

Chronology does not imply causation.

Use:

- paired replay;
- one-factor replacement;
- ablation;
- factorial experiments;
- randomized task ordering;
- matched seeds;
- counterfactual forks.

## 37.4 Benchmark Contamination

Protect:

- hidden evaluators;
- test answers;
- benchmark fixtures;
- private reference outputs;
- training/evaluation split.

A strong evaluation design makes contamination structurally difficult, not merely forbidden in instructions.

---

# 38. Measurement Framework

A complete agentic-system evaluation should record multiple fronts.

## Capability

- pass rate;
- task completion;
- exactness;
- robustness.

## Economics

- USD;
- tokens;
- tool calls;
- model calls;
- CPU;
- wall time;
- critical path.

## Context

- prompt tokens by layer;
- cache-hit fraction;
- compression ratio;
- rehydration frequency;
- retrieved evidence utilization.

## Coordination

- workers;
- branches;
- messages/events;
- bytes;
- contention;
- retries.

## Reliability

- recovery success;
- duplicate-effect rate;
- idempotency failures;
- evaluator disagreement;
- malformed output rate.

## Security

- denied unauthorized effects;
- selector escape attempts;
- sandbox violations;
- evaluator reachability;
- authority widening attempts.

---

# 39. Cost per Verified Pass

A strong operational metric from the source corpus:

\[
CPP(s,k)
=
\frac{
\sum_{\text{runs of strategy }s\text{ on class }k}
cost_{add}(run)
}{
|\{\text{verified passing runs}\}|
}.
\]

This makes the optimization target more useful than raw success rate.

A 2% quality gain at 10× cost may be undesirable for one profile and ideal for another.

---

# 40. Research Tensions Matrix

| Question | Alternative A | Alternative B | What to measure |
|---|---|---|---|
| Core architecture | universal trusted mechanism | everything pluggable | flexibility vs trust-surface complexity |
| Loop | universal turn loop | pluggable loops | counterexamples, domain coverage |
| Work unit | turn/effect | typed obligation | decomposition, recovery, scheduler clarity |
| Coordination | peer messages | shared state/stigmergy | token/latency/bytes/contention |
| Composition | fixed roles/slots | named graph + bindings | expressiveness, complexity |
| Evaluation | self-critique | exterior witness | calibration, manipulation resistance |
| Guardrails | mandatory | declared-absent vs forged | generality vs evidence quality |
| Routing | static profile | adaptive Pareto | cost/pass, regret, calibration |
| Planning | one agent | branching/subagents | marginal quality per cost |
| Learning | skills | macros | transfer vs determinism |
| Optimization | weighted scalar | partial-order Pareto | invariant preservation |
| Memory | transcript | structured state + retrieval | long-horizon accuracy |
| Context | full history | progressive disclosure | quality/token efficiency |
| Concurrency | eager parallelism | measured selective concurrency | speedup vs contention |
| Product strategy | substrate-first | result/data-first | time-to-capability vs scientific integrity |

---

# 41. Research Questions Worth Answering

## Harness

1. How much variance in benchmark performance is attributable to harness vs model?
2. Which harness dimensions have the highest marginal effect?
3. Are interactions between context, tools, and model tier super-additive?
4. How portable is a good harness across model families?

## Context

5. What is the optimal stable-prefix vs dynamic-context ratio?
6. What information should survive compaction?
7. Does graph-structured context outperform ranked text chunks?
8. When does retrieval noise outweigh missing context?

## Multi-agent

9. At what task complexity does multi-agent decomposition become economical?
10. What branch diversity metric predicts best-of-N gain?
11. Does stigmergic shared state outperform sparse direct messaging?
12. How does evaluator cost change the optimal number of branches?

## Verification

13. Which witness classes correlate with true downstream success?
14. When is an LLM critic useful as a non-authoritative signal?
15. How much robustness is gained by physically separated evaluation?
16. How should inconclusive evidence affect routing?

## Compounding

17. What fraction of recurring trajectories can be safely compiled into macros?
18. How many distinct examples are required before anti-unification?
19. When should a skill become a macro?
20. Which router-learning method gives the lowest regret under changing models?

## Scientific methodology

21. What is the minimum telemetry needed to reproduce an agent run?
22. Which event fields provide actual causal value vs logging noise?
23. How stable are paired benchmark results across provider/model drift?
24. How should long-horizon agent experiments handle non-stationarity?

---

# 42. Suggested Experiment Families

These are **research experiment families**, not a development schedule.

## E1 — Harness Factorial Experiment

Freeze:

- task set;
- model;
- evaluator.

Vary:

- context compiler;
- tool set;
- verification frequency;
- planning topology.

Measure interaction effects.

---

## E2 — Context Projection Experiment

Compare:

- full recent history;
- structured compacted state;
- lexical retrieval;
- hybrid retrieval;
- graph projection.

Measure:

- pass rate;
- tokens;
- cache hit;
- missing-evidence errors.

---

## E3 — Single vs Multi-Agent

Same task/model budget.

Arms:

- one strong agent;
- scout + executor;
- generator + critic;
- best-of-3;
- state-mediated swarm.

Measure CPP and critical path.

---

## E4 — State vs Messaging

Equivalent multi-agent problem.

Arm A:

- sparse direct messages.

Arm B:

- shared durable state.

Arm C:

- hybrid.

Measure:

- coordination tokens;
- events;
- latency;
- attribution;
- contention;
- errors.

---

## E5 — Macro Compiler

Mine recurring procedures.

Compare:

- original multi-turn agent execution;
- compiled macro;
- skill prompt;
- deterministic script.

Use held-out instances and adversarial parameter changes.

---

## E6 — Router Comparison

Compare:

- fixed profile;
- heuristic escalation;
- contextual bandit;
- Bayesian expected utility;
- EFE-inspired router;
- Pareto frontier + lexicographic selection.

Measure regret and CPP.

---

## E7 — Recovery

Inject crashes:

- before external effect;
- after durable intent;
- after effect before receipt;
- after receipt before state reduction.

Measure duplicate/omitted effects.

---

## E8 — Evaluation Separation

Compare:

- self-score;
- peer LLM judge;
- isolated LLM judge;
- deterministic checker;
- formal verifier;
- human panel.

Measure calibration and exploitability.

---

# 43. External Systems and Architectural Lessons

## 43.1 DeepSeek Harness / Cordis

Source-corpus interpretation:

- broad configuration-driven composition;
- pluginized models/tools/skills/sessions/sandboxes/storage/loops/UI;
- append-only session history;
- standard/code/minimal/creator modes.

Research lessons:

- composition is valuable;
- minimal benchmark mode is valuable;
- creator/inspection mode is valuable;
- unified event history is valuable.

Research caution:

- broad pluginization should be compared with a bounded trust core;
- preview APIs may change;
- plugin extensibility is not equivalent to authority safety.

---

## 43.2 Claude Code / Agent SDK

Source-corpus interpretation:

- project instructions;
- skills;
- MCP;
- subagents;
- hooks;
- code intelligence;
- context compaction;
- session resume/fork.

Research lessons:

- distinguish extension mechanisms;
- progressive context loading;
- isolate subtask contexts;
- stable prompt prefix;
- explicit compaction boundaries;
- deterministic hooks for automation.

---

## 43.3 Codex / Aider / OpenCode Family

Research themes highlighted in the corpus:

- repository mapping;
- AST/symbol extraction;
- incremental indexing;
- compact structural context;
- diff-oriented editing;
- terminal-native workflows.

These should be studied as patterns rather than assumed exact implementations.

---

# 44. Literature and Primary-Source Map

The following references are reproduced from the source corpus as a research index. Inclusion means “worth investigating,” not “validated here.”

## Harness Engineering and Agent Systems

- **Agentic Harness Engineering** — https://arxiv.org/abs/2604.25850
- **Agent Harness Engineering: A Survey** — https://picrew.github.io/LLM-Harness/main.pdf
- **Harness-Bench** — https://arxiv.org/html/2605.27922v1
- **From Question Answering to Task Completion: A Survey on Agent System and Harness Design** — https://arxiv.org/pdf/2606.20683
- **Harness as an Asset (CAAF)** — https://arxiv.org/pdf/2604.17025
- **Anthropic multi-agent research system** — https://www.anthropic.com/engineering/multi-agent-research-system
- **Asymptotic analysis with LLM primitives** — https://proceedings.mlr.press/v267/meyerson25a.html

## Multi-Agent Coordination and Shared State

- **LLM multi-agent blackboard** — https://arxiv.org/abs/2510.01285
- **CodeCRDT** — https://arxiv.org/pdf/2510.18893
- **Beyond Text-Passing: Shared Cognitive Substrates** — https://openreview.net/forum?id=RRIw2L4Z1g
- **PatchBoard** — https://arxiv.org/pdf/2605.29313
- **Token Coherence / MESI for MAS** — https://arxiv.org/pdf/2603.15183
- **AgentFlow: Agent Dependency Graphs** — https://arxiv.org/html/2607.01640
- **Declarative Data Services** — https://arxiv.org/abs/2605.20690

## Trajectory Learning and Credit Assignment

- **ASTRA** — https://arxiv.org/abs/2601.21558
- **GraphGPO** — https://arxiv.org/abs/2605.26684
- **Agent Lightning** — https://arxiv.org/abs/2508.03680
- **TRACE** — https://arxiv.org/abs/2607.13988
- **DMPO** — https://arxiv.org/abs/2406.14868

## Active Inference

- **Expected Free Energy-based Planning as Variational Inference** — https://arxiv.org/abs/2504.14898
- Alternate source referenced in the corpus — https://arxiv.org/html/2606.20658
- **Active Inference as a Convex MDP** — https://arxiv.org/pdf/2607.20152

## Skill and Macro Evolution

- **SkillTTA** — https://arxiv.org/abs/2605.16986
- **Globalized Skill Evolution** — https://arxiv.org/abs/2608.06153
- **MACRO** — https://arxiv.org/abs/2603.05860
- **AlphaEvolve** — https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- **Darwin Gödel Machine** — https://openreview.net/pdf?id=pUpzQZTvGY

## Preference Optimization

- **DPO** — https://arxiv.org/abs/2305.18290
- **DMPO** — https://arxiv.org/abs/2406.14868

## Capability Security / Provenance

- **Progent** — https://arxiv.org/abs/2504.11703
- **MiniScope** — https://arxiv.org/abs/2512.11147
- **From Agent Traces to Trust** — https://arxiv.org/pdf/2606.04990
- **Lingering Authority: Revocable Resource-and-Effect Capabilities** — https://arxiv.org/pdf/2606.22504
- **Execution-security / TOCTOU survey referenced by source** — https://arxiv.org/pdf/2607.05743
- **W3C PROV** — https://www.w3.org/groups/wg/prov/publications/
- **SLSA v1.2 provenance** — https://slsa.dev/spec/v1.2/provenance
- **in-toto provenance predicate** — https://github.com/in-toto/attestation/blob/main/spec/predicates/provenance.md

## Sandbox / Platform

- **Linux Landlock** — https://www.kernel.org/doc/html/latest/userspace-api/landlock.html
- **Bubblewrap** — https://github.com/containers/bubblewrap
- **Bubblewrap setuid advisory referenced by source** — https://github.com/containers/bubblewrap/security/advisories/GHSA-xq78-7hw4-5jvp

## Data and Identity Standards

- **JSON Schema Draft 2020-12** — https://json-schema.org/draft/2020-12
- **RFC 8785 JCS** — https://www.ietf.org/rfc/rfc8785.html
- **SQLite WAL** — https://www.sqlite.org/wal.html

## Contemporary Agent Products / First-Party Material

- **DeepSeek Harness developer preview** — https://deepseek.com/harness/en/
- **DeepSeek Harness repository** — https://github.com/deepseek-ai/deepseek-harness
- **Claude Code extension architecture** — https://code.claude.com/docs/en/features-overview
- **Claude Agent SDK loop/context management** — https://code.claude.com/docs/en/agent-sdk/agent-loop

---

# 45. Source-Provenance Map

| Research theme | Main source documents |
|---|---|
| harness as independent variable | `002`, `004`, `005`, `006`, `007`, `008` |
| A-B-C-D abstraction | `002`, `004`, `005`, `006`, `007`, `008` |
| separability / exterior evaluator | `002`, `004`, `005`, `006`, `007`, `008`, `009`, `010` |
| dynamic informational bottleneck | `002`, `008` |
| Pareto profiles | `002`, `006`, `007`, `008` |
| six-dimensional resources | `006`, `007`, `008` |
| VFE / EFE correction | `006`, `007`, `008` |
| stigmergic state coordination | `002`, `004`, `005`, `006`, `007`, `008` |
| typed obligation abstraction | `006`, `007`, `008` |
| macro-tool compilation | `002`, `006`, `007`, `008` |
| skill retrieval / Elo | `004`, `005`, `006`, `007` |
| DPO / paired evidence | `004`, `005`, `006`, `007`, `008` |
| exact McNemar | `006`, `007`, `008` |
| fault attribution | `004`, `005`, `006`, `008` |
| named component graph | `001`–`008` |
| path-bag ≠ graph correction | `007`, `008` |
| universal loop tension | `004`, `005`, `006`, `007`, `008` |
| outcome/data-first alternative | `005` |
| DeepSeek / Claude / Codex analysis | `009`, `010` |
| indexing/caching/context | `009`, `010` |
| coding vs research agents | `009`, `010` |
| scientific event telemetry | `009`, `010` |
| decision synthesis / advisory-vs-law separation | `001` |

---

# 46. Corrections and Caveats Preserved From Cross-Review

The consolidated corpus should retain the corrections discovered across independent reviews.

## 46.1 VFE is not EFE

- VFE: posterior/belief fitting.
- EFE: candidate policy evaluation.

Do not call an arbitrary weighted reward “free energy”.

## 46.2 Shared state does not prove linear scaling

State-mediated coordination can avoid the protocol of all-to-all chat, but database and synchronization costs still require measurement.

## 46.3 A named component bag is not a graph

Graph claims require explicit bindings/edges.

## 46.4 Cycles can be legitimate

Critic/reviser and debate systems can be cyclic. Termination can be enforced by resource bounds rather than graph acyclicity.

## 46.5 Unknown economics are not zero

Missing cost must carry explicit missingness.

## 46.6 A hash chain proves integrity/order, not semantic truth

External verification remains necessary.

## 46.7 DPO does not validate preference labels

The preference-generation process must itself be trustworthy.

## 46.8 Approximate chi-square is not “exact McNemar”

Use the exact paired binomial form when sample sizes/discordant counts justify it.

## 46.9 Token-collapse and latency percentages are hypotheses

Historical reports include aggressive efficiency claims. Treat them as targets to reproduce, not general truths.

## 46.10 Multi-agent is not automatically better

The correct objective is marginal verified value per marginal cost.

---

# 47. Integrated Conceptual Architecture — Research View

The ideas can be assembled into one research architecture without implying that this is the final production design:

```text
                        TASK / OBLIGATION
                              │
                              ▼
                  ┌─────────────────────┐
                  │  HARNESS CONTROLLER │
                  │ profile / router    │
                  │ Pareto / EFE / bandit
                  └─────────┬───────────┘
                            │
                 context projection Bθ
                            │
                            ▼
            ┌──────────────────────────────┐
            │  COMPOSITION / TOPOLOGY      │
            │ nodes + bindings + policies  │
            └──────────────┬───────────────┘
                           │
                           ▼
             observe → propose → authorize
                           │
                           ▼
                       EFFECT
                           │
                           ▼
                       RECEIPT
                           │
              ┌────────────┴─────────────┐
              ▼                          ▼
       DURABLE STATE                 EXTERIOR WITNESS
     events + artifacts                / evaluator
              │                          │
              └────────────┬─────────────┘
                           ▼
                  EVIDENCE TRAJECTORY
                           │
        ┌──────────────────┼────────────────────┐
        ▼                  ▼                    ▼
      MEMO               MACRO                SKILL
        │                  │                    │
        └──────────────────┼────────────────────┘
                           ▼
                  ROUTING / LEARNING
                           │
                           ▼
                    NEXT EXPERIMENT
```

This integrated picture makes one research priority explicit:

> **The learning loop is only as good as the observability, attribution, and evaluation underneath it.**

---

# 48. Final Research Synthesis

The consolidated corpus suggests that the most promising direction in agentic systems engineering is not a single “super-agent” architecture. It is a **scientific substrate for exploring many agentic regimes while preserving comparable evidence**.

The durable ideas are:

1. model capability and harness capability must be separated experimentally;
2. composition should be declarative enough to express multiple topologies;
3. authority should remain explicit, bounded, and independent from model reasoning;
4. evaluation should be separated from generation whenever strong claims depend on it;
5. state and artifacts should carry coordination and provenance, not only transcripts;
6. context should be compiled dynamically rather than accumulated blindly;
7. resource economics should remain multidimensional;
8. routing should operate inside hard feasibility constraints;
9. multi-agent structures should justify their coordination cost empirically;
10. exact verified reuse should precede learned reuse;
11. macros, skills, routers, and model training are different compounding mechanisms and should be evaluated separately;
12. causal claims require intervention, not narrative explanation;
13. replay, fork, cold recovery, and counterfactual execution are foundational research instruments;
14. benchmarks should treat harness configuration as part of the experimental identity;
15. the strongest meta-framework is likely one that can change almost everything about behavior while changing almost nothing about the semantics of trust, evidence, and measurement.

The most valuable conceptual shift across the reports is therefore:

> **Do not design one agent. Design a measurable space of agentic systems.**

In that space, coding agents, research agents, formal solvers, critics, swarms, tree searches, and future architectures become experimental points generated by different compositions, context regimes, policies, budgets, and verification structures.

The scientific objective is not to declare one architecture universally superior. It is to make the system capable of answering, with attributable evidence:

\[
\boxed{
\text{Which agentic configuration solves this task class
with the best admissible trade-off of
quality, cost, tokens, latency, safety, and evidence?}
}
\]

That is the unifying research question behind the source corpus.

---

# Appendix A — Compact Equation Index

### Resource tensor

\[
\mathbf R=
(r_{\$},r_{tok},r_{byte},r_{ms};r_{turn},r_{depth})
\]

### Feasibility

\[
\mathbf R_a\preceq\mathbf R_b
\iff
\forall j,\ R_{a,j}\le R_{b,j}
\]

### VFE

\[
\mathcal F=
\mathbb E_q[\log q-\log p]
\]

### EFE

\[
\mathcal G(\pi)=
\mathbb E_{q(o,s|\pi)}
[
\log q(s|\pi)-\log p_C(o,s)
]
\]

### Pareto/EFE constrained policy

\[
\theta^*=
\arg\min_\theta
\left(
\mathbb E[\mathcal G(\pi_\theta)]
+
\sum_j\lambda_j\mathbb E[c_j]
\right)
\]

subject to hard feasibility.

### Informational bottleneck

\[
\mathcal B_\theta:
\mathcal W\times TaskProfile
\to Context_{\le k}
\]

### Obligation

\[
o=
\langle
g,w,\mathbf R_{max},d,\mathcal D,p,\kappa
\rangle
\]

### Backward slice

\[
B(z)=
\{v:v\leadsto z\}
\]

### Hybrid retrieval

\[
s(i)=
\alpha s_d+\beta s_l+\eta L_i+\zeta C_i-\kappa A_i
\]

### Elo update

\[
\mu_i'=
\mu_i+K(n_i)w_i(y_i-p_i)
\]

### DPO

\[
\mathcal L_{DPO}
=
-\mathbb E\log\sigma
\left(
\beta[
\log\frac{\pi_\theta(y^+|x)}{\pi_{ref}(y^+|x)}
-
\log\frac{\pi_\theta(y^-|x)}{\pi_{ref}(y^-|x)}
]
\right)
\]

### Exact McNemar

\[
p_{exact}
=
\min
\left(
1,
2\sum_{k=0}^{\min(b,c)}
{b+c\choose k}2^{-(b+c)}
\right)
\]

### Macro capability hull

\[
C_{macro}
=
\operatorname{hull}
\left(
\bigcup C_v
\right)
\cap C_{pack}\cap C_{publisher}
\]

### Memo key

\[
K_{memo}
=
H(
D_O\parallel
D_{inputs}\parallel
D_{environment}\parallel
D_{checker}\parallel
D_{toolchain}\parallel
assurance\parallel
policy
)
\]

### Cost per verified pass

\[
CPP=
\frac{\text{total additive cost}}
{\text{verified passes}}
\]

---

# Appendix B — Practical Research Checklist

Before treating any new idea as better:

- [ ] Freeze task set.
- [ ] Freeze or explicitly vary model.
- [ ] Record harness identity.
- [ ] Record environment.
- [ ] Record context policy.
- [ ] Record tool versions.
- [ ] Record exact resource usage.
- [ ] Use an independent or clearly typed witness.
- [ ] Preserve baseline.
- [ ] Run A/A where measurement noise matters.
- [ ] Use paired trials when possible.
- [ ] Report effect size and uncertainty.
- [ ] Test security/trust regressions separately.
- [ ] Preserve failed experiments.
- [ ] Avoid simultaneous uncontrolled changes.
- [ ] Mark unknown measurements as unknown.
- [ ] Distinguish correlation from intervention-backed causation.
- [ ] Treat large efficiency claims as reproducibility targets.
- [ ] Keep learned policy separate from authoritative truth.

---

# Appendix C — Source Corpus

1. `001_alfa_review_full_decision.md` — decision synthesis and proposal disposition.
2. `002_beta_review_full_gem_proposal.md` — informational-flow primitives, Pareto profiles, stigmergic blackboard, compounding flywheel.
3. `004_delta_review_full_glm53_proposal.md` — theory, credit assignment, retrieval, DPO, statistical methodology.
4. `005_epsilon_review_full_dsv4-proposal.md` — alternative outcome/data-first framing and generality arguments.
5. `006_fi_review_full_gptsol_proposal.md` — most complete mathematical and research synthesis; obligation harness, corrected VFE/EFE, macro compilation, evidence methodology.
6. `007_zeta_review_full_opus_proposal.md` — Pareto/stigmergy/Active-Inference/macros synthesis and cross-proposal corrections.
7. `008_alfa_review_full_grok_proposal.md` — compact reconciled synthesis and obligation-market alternative.
8. `009_beta_review_higgs_gem.md` — coding/research product research; DeepSeek, Claude Code, Codex, repo mapping, prompt caching.
9. `010_fi_review_higgs_gpt.md` — later research complement on DeepSeek/Claude extension architecture, indexing, caching, context, event telemetry, and two-domain generality.

---

**End of consolidated research report.**
