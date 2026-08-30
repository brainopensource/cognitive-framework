# RESEARCH_2308B_gm: Foundations, Architectures, Algorithms, and Experimental Methods for Evolvable Agentic Systems

**Date:** 2026-08-23  
**Authors / Research Syndicate:** Vanguard / AETHER Research Group (AI Systems, Cognitive Architecture, Algorithms, Neuroscience, Psychology, Formal Methods)  
**Status:** Living Research Document — Advanced Theoretical & Empirical Reference  
**Classification:** Epistemic Reference & Meta-Framework Blueprint  

---

## 1. Date and Scope

This research report establishes the rigorous theoretical, algorithmic, and engineering foundations required to build an **Evolvable Meta-Framework for Recursive Agentic Systems**. 

The investigation spans:
1. **Minimal Computational Primitives:** Identification of irreducible operators vs. derived policies.
2. **Epistemic & Metacognitive Separation:** Formalizing `belief ≠ evidence`, `reflection ≠ truth`, and `self-evaluation ≠ external validation`.
3. **Neurobiology & Cognitive Architectures:** Biologically grounded computational abstractions (hippocampal-cortical replay, Global Workspace Theory, predictive processing, basal ganglia selection).
4. **Evolutionary Computation & Artificial Life:** Quality-Diversity (MAP-Elites), Minimal Criterion Coevolution (MC-CC), POET, and developmental genomic encodings.
5. **Information Theory & Mathematics:** Algorithmic Information Theory (MDL/Kolmogorov complexity), Causal Inference (Pearl DAGs, Shapley attribution), Active Inference (Variational & Expected Free Energy), and Rate-Distortion Theory.
6. **Empirical Agentic Harnesses:** Architectural extraction from SOTA systems (Claude Code, SWE-agent, Codex CLI, Aider, OpenHands, ClawGym II, Evo-Harness, AI4AI-Bench).
7. **The 7-Tier Plane Architecture & Machine-Readable Genome:** Complete data models for `PrimitiveGenome`, `ArchitectureGenome`, and the M0–M8 mutation taxonomy.
8. **Experimental Proof & Falsification:** A 10-experiment empirical program with strict falsifiers to prove causal emergent intelligence over benchmark gaming.

---

## 2. Executive Summary

### The Central Thesis
> **Intelligence in autonomous systems is not a monolithic program or a single massive prompt; it is an emergent property of interacting, bounded computational primitives operating under strict resource conservation, environmental pressure, external epistemic grounding, and multi-scale evolution.**

Current agentic frameworks commit a fundamental category error: they hardcode reasoning loops, monolithic prompts, and introspective reflection into rigid, self-grading architectures. When an LLM evaluates its own output, assigns its own credit, or modifies its own execution environment without external reference monitors, the system degenerates into ungrounded hallucinations, positive feedback loops, and benchmark overfitting.

To build an evolvable system that generalizes across domains (from software engineering to mathematical formalization, scientific research, and complex coordination), we must separate the **Immutable Execution Substrate** from the **Evolvable Cognitive Policies** and the **External Learning/Evaluation Planes**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           7. EVALUATION PLANE                           │
│  Exterior Oracles (UID 10002), Signed Verdicts (Ed25519), Paired Tests  │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │ verifies
┌────────────────────────────────────┴────────────────────────────────────┐
│                            6. LEARNING PLANE                            │
│  Trajectory Mining, Prefix-Tree RL (ClawGym II), DPO/SFT, Distillation  │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │ updates weights/policies
┌────────────────────────────────────┴────────────────────────────────────┐
│                            5. EVOLUTION PLANE                           │
│  Quality-Diversity (MAP-Elites), Architecture Search, M0–M8 Mutations   │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │ mutates genomes
┌────────────────────────────────────┴────────────────────────────────────┐
│                           4. ADAPTATION PLANE                           │
│  Procedural Skills, Context Compaction, Verification Scheduling, Router │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │ configures
┌────────────────────────────────────┴────────────────────────────────────┐
│                       3. COMPOSITION / AGENT PLANE                      │
│  Named Component Graphs (mhf.manifest/2), Attenuated Spawns, Topologies │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │ invokes
┌────────────────────────────────────┴────────────────────────────────────┐
│                        2. PRIMITIVE RUNTIME PLANE                       │
│  Model Gateway, Rootless Sandboxes (bwrap), SQLite WAL Store, Plugins   │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │ mediates
┌────────────────────────────────────┴────────────────────────────────────┐
│                      1. IMMUTABLE KERNEL SUBSTRATE                      │
│  S0–S12 Reference Monitor, Monotonic Attenuation, 6D Leases, JCS Digest │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Top 8 New Findings

1. **Self-Reflection Degradation (Evo-Harness Finding):** LLMs generating self-introspective feedback without external ground truth degrade task performance (e.g., Claude Opus dropping from 29.54% to 27.96% on CL-Bench). Reflection must be treated strictly as an *unverified hypothesis* (`CandidateLesson`), never as an authoritative update to memory or skills.
2. **Prefix-Addressed Merkle Trajectories (ClawGym II Finding):** Representing agent execution traces as branching DAG prefix-trees rather than linear transcripts prevents $O(N^2)$ memory explosion during multi-agent spawning and black-box reinforcement learning, allowing exact branch-point credit assignment.
3. **The AI4AI Complexity Wall:** Recursive algorithmic improvement (modifying the learning rule itself, M6–M7) faces extreme optimization instability. Evolution must operate through a strict hierarchy: hyperparameter tuning (M0) $\to$ policy selection (M1) $\to$ procedural skills (M2) $\to$ topology graphs (M3), with higher tiers requiring exponential verification rigor.
4. **Context Paging over Skill Injection (@skills Finding):** Procedural knowledge libraries exceed effective in-context attention budgets. Skills must be indexed by structural and semantic descriptors and paged dynamically via activation policies rather than globally injected into system prompts.
5. **Canonical Event Independence from Wire Formats:** Provider-specific wire serializations (OpenAI, Anthropic, DeepSeek reasoning channels) subtly corrupt causal event order. The runtime must enforce an immutable internal event algebra where external APIs are pure serializer/deserializer projections.
6. **Pareto Metric Vectors vs. Scalar Optimization:** Scalar reward optimization causes rapid specification gaming and severe cost inflation. Fitness must be evaluated across an invariant multi-dimensional vector: $\mathbf{F} = \langle \text{Correctness}, \text{Generalization}, \text{Cost}_{\text{USD}}, \text{Tokens}, \text{Latency}, \text{VerificationCompute}, \text{SecurityViolations} \rangle$.
7. **Cost-Aware Verification Scheduling:** Monolithic test-suite runs waste up to 80% of agent compute. Verification must be governed by an adaptive scheduler executing a staged cascade: Static Analysis $\to$ Local Unit Tests $\to$ Dependency-Impact Tests $\to$ Integration $\to$ Full Regression.
8. **Minimal Criterion Coevolution (MC-CC):** Open-ended agent evolution without premature convergence requires co-evolving the environment/task generator alongside the agent population (POET model), selecting for novelty and minimal viability rather than optimizing against a static benchmark.

---

## 4. Deltas Since Previous Harness Research

| Architectural Dimension | Previous Generation Harnesses | Evolvable Meta-Framework (AETHER/Vanguard) |
|---|---|---|
| **Ontology** | Hardcoded coding loop (ReAct / SWE-agent style). | Domain-blind computational substrate; coding is merely Pack #1. |
| **Authority** | In-process agent code has full ambient authority. | Monotonic capability attenuation via S0–S12 Reference Monitor. |
| **Resource Model** | Open-ended execution or single timeout. | 6D Conserved Leases: Additive (USD, tokens, bytes, millis) vs. Structural (depth, turns). |
| **Trajectory Truth** | Flat text logs / JSONL dumps; often zero-costed. | Merkle DAG with exact per-turn token/USD cost, model fingerprints, and signed verdicts. |
| **Memory Updates** | Append-only `MEMORY.md` updated by model reflection. | Staged Epistemic Pipeline: Trajectory $\to$ Candidate $\to$ Held-out Eval $\to$ Promoted Skill. |
| **Multi-Agent** | Hardcoded swarm engines or unregulated peer chats. | Mediated `agent.spawn` with parent-child capability and budget containment. |
| **Promotion Authority** | Agent promotes own code/prompts if tests pass. | Exterior Signed Evaluator (UID 10002, Ed25519) + Paired McNemar ($\chi^2 \ge 3.841$). |

---

## 5. Computational Primitives

To prevent ad-hoc bloat, we partition computational mechanisms into **Fundamental Primitives** (enforced by substrate), **Derived Primitives** (built via composition), and **Dynamic Policies** (learned/evolved).

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         COMPUTATIONAL PRIMITIVES                         │
├──────────────────────────┬──────────────────────────┬────────────────────┤
│  FUNDAMENTAL PRIMITIVES  │    DERIVED PRIMITIVES    │  DYNAMIC POLICIES  │
│  (Kernel & Runtime TCB)  │  (Component Compositions)│ (Evolvable M0–M3)  │
├──────────────────────────┼──────────────────────────┼────────────────────┤
│ • Observe (State Read)   │ • Working Memory Buffer  │ • Attention Mask   │
│ • Propose (Effect Intent)│ • Episodic Retrieval DAG │ • Tool Selection   │
│ • Authorize (S0–S12 Gate)│ • Decomposer / Sub-Goal  │ • Verification Freq│
│ • Execute (Sandboxed Op) │ • Verification Pipeline  │ • Compaction Rules │
│ • Record (Append Ledger) │ • Structured Reflector   │ • Model Escalation │
│ • Delegate (agent.spawn) │ • Consensus Aggregator   │ • Skill Eviction   │
│ • Settle (Budget Delta)  │ • Candidate Synthesizer  │ • Search Topologies│
│ • Evaluate (Sign Verdict)│ • Rollback Checkpointer  │ • Spawn Depth Cap  │
└──────────────────────────┴──────────────────────────┴────────────────────┘
```

### Mathematical Formulation of Authority Mediation
Every primitive action $a_t$ proposed by an agent $\alpha$ with grant $G_\alpha$ under context $\mathcal{C}$ is mediated by the reference monitor:
$$\mathcal{M}(a_t, G_\alpha, \mathcal{B}_t) = \begin{cases} 
\text{ALLOW}(a_t, \Delta \mathcal{B}_t) & \text{if } \text{Match}(a_t.\text{target}, G_\alpha.\text{selector}) \land \text{Cost}(a_t) \le \mathcal{B}_t \\
\text{DENY}(\text{ERR\_UNAUTHORIZED}) & \text{if } \neg \text{Match}(a_t.\text{target}, G_\alpha.\text{selector}) \\
\text{DENY}(\text{ERR\_BUDGET\_EXHAUSTED}) & \text{if } \text{Cost}(a_t) > \mathcal{B}_t
\end{cases}$$

---

## 6. Metacognition and Self-Models

Metacognition is defined computationally as **second-order control of cognitive resource allocation based on predictive modeling of self-performance**.

### Epistemic Separation Invariant
The meta-framework enforces strict epistemic barriers:
$$\text{Belief}_{\text{internal}}(\theta) \neq \text{Evidence}_{\text{external}}(\theta)$$
$$\text{Confidence}_{\text{model}}(y|x) \neq \text{Reliability}_{\text{empirical}}(y|x)$$

```
                                  EPISTEMIC PIPELINE
                                  
   ┌────────────────┐      ┌────────────────┐      ┌────────────────┐
   │ Model Output / │      │ Candidate      │      │ External       │
   │ Self-Reflection├─────►│ Hypothesis     ├─────►│ Evaluator      │
   │ (Subjective)   │      │ (Unverified)   │      │ (Objective)    │
   └────────────────┘      └────────────────┘      └───────┬────────┘
                                                           │
                                                           ▼
   ┌────────────────┐      ┌────────────────┐      ┌────────────────┐
   │ Skill Registry │      │ Promotion Gate │      │ Signed Verdict │
   │ (Persistent)   │◄─────┤ (McNemar Test) │◄─────┤ (Ed25519)      │
   └────────────────┘      └────────────────┘      └────────────────┘
```

### Computational Self-Models
A self-model comprises:
1. **Competence Map:** $P(\text{Pass} \mid \text{Domain}, \text{Complexity}, \text{Model}, \text{Harness})$.
2. **Cost-to-Solution Estimator:** $E[\text{Tokens}, \text{USD}, \text{Time} \mid \text{TaskDescription}]$.
3. **Error Signature Classifier:** Detecting cyclic tool failures, deadlocks, and thrashing within $k$ steps.

When prediction error $\delta_t = | \text{ObservedOutcome} - \text{ExpectedOutcome} | > \tau_{\text{surprise}}$, the metacognitive controller triggers an escalation policy (e.g., invoking a critic model, checkpoint rollback, or human-in-the-loop grant request).

---

## 7. Neuroscience and Cognitive Systems

| Biological Mechanism | Computational Abstraction | Vanguard Architectural Realization |
|---|---|---|
| **Hippocampal Rapid Encoding** | High-resolution, ephemeral episodic trajectory logging. | Append-only SQLite WAL Event Store logging every S0–S12 event. |
| **Cortical Consolidation (Replay)** | Offline batch extraction of recurring subgraphs into general schemas. | Background Skill Synthesizer clustering successful execution traces. |
| **Global Workspace Theory (GWT)** | Bounded working memory blackboard where specialized modules compete. | Context Compiler selecting top-$k$ relevant artifacts and skills into the prompt window. |
| **Basal Ganglia Action Selection** | Striatal gating of cortical actions under dopamine-modulated utility. | Kernel Reference Monitor gating proposed tool effects against capability grants. |
| **Predictive Processing (Friston FEP)** | Minimization of Variational Free Energy through active inference. | Agent planning to minimize Expected Free Energy (EFE), balancing epistemic and pragmatic value. |
| **Neuromodulatory Gain Control** | Dynamic tuning of exploration vs. exploitation (NE / ACh / DA). | Dynamic Pareto Controller adjusting temperature, top-$p$, and search beam width. |

---

## 8. Mathematical and Information-Theoretic Foundations

### 1. Active Inference and Free Energy Principle (FEP)
The agent selects action sequences (policies $\pi$) to minimize Expected Free Energy $G(\pi)$:
$$G(\pi) = \sum_\tau G(\pi, \tau)$$
$$G(\pi, \tau) \approx \underbrace{- \mathbb{E}_{Q(o_\tau, s_\tau \mid \pi)} \left[ \ln P(o_\tau \mid \mathcal{C}) \right]}_{\text{Pragmatic Value (Goal Realization)}} - \underbrace{\mathbb{E}_{Q(s_\tau \mid \pi)} \left[ D_{KL}\left( Q(o_\tau \mid s_\tau, \pi) \parallel Q(o_\tau \mid \pi) \right) \right]}_{\text{Epistemic Value (Information Gain / Curiosity)}}$$
This formally justifies why an agent must seek novel information (reducing uncertainty) before taking high-risk irreversible actions.

### 2. Algorithmic Information Theory & Minimum Description Length (MDL)
Learning and skill acquisition are framed as program compression:
$$\mathcal{L}(\text{SkillLibrary}) = \arg\min_{\mathcal{S}} \left( K(\mathcal{S}) + \sum_{i=1}^N K(\text{Trajectory}_i \mid \mathcal{S}) \right)$$
Where $K(\cdot)$ represents Kolmogorov complexity. A new skill is only admitted if the compression gain over the historical trajectory corpus exceeds the complexity cost of adding the skill to the registry.

### 3. Causal Credit Assignment via Shapley Attribution
For a multi-primitive or multi-agent trajectory yielding outcome $V$, the marginal contribution of primitive $i \in \mathcal{N}$ is:
$$\phi_i(V) = \sum_{\mathcal{S} \subseteq \mathcal{N} \setminus \{i\}} \frac{|\mathcal{S}|! (|\mathcal{N}| - |\mathcal{S}| - 1)!}{|\mathcal{N}|!} \left( V(\mathcal{S} \cup \{i\}) - V(\mathcal{S}) \right)$$
Using prefix-tree branching, counterfactual replays evaluate $V(\mathcal{S} \cup \{i\})$ against $V(\mathcal{S})$ without re-running the entire ancestor lineage.

---

## 9. SOTA Agentic and Coding Harness Architectures

An analysis of modern production and research agent frameworks reveals crucial structural patterns:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SOTA HARNESS ARCHITECTURAL MATRIX                    │
├──────────────┬──────────────────┬─────────────────┬─────────────────────┤
│ System       │ Strong Pattern   │ Weakness        │ Vanguard Separation │
├──────────────┼──────────────────┼─────────────────┼─────────────────────┤
│ Claude Code  │ Context packing, │ Monolithic,     │ Externalizes        │
│              │ sub-agent spawn, │ vendor-locked,  │ reference monitor & │
│              │ terminal tool.   │ in-process eval.│ signed evaluation.  │
├──────────────┼──────────────────┼─────────────────┼─────────────────────┤
│ SWE-agent    │ ACI (Agent-      │ Brittle regex   │ Hexagonal ports     │
│              │ Computer Interf.)│ parsers, flat   │ with structured JSON│
│              │ linter feedback. │ turn loop.      │ event schemas.      │
├──────────────┼──────────────────┼─────────────────┼─────────────────────┤
│ Aider        │ Git-backed map,  │ Fixed ReAct     │ Dynamic topology    │
│              │ repo-AST tokens, │ topology, no    │ graphs + mediated   │
│              │ diff architect.  │ delegation.     │ agent.spawn.        │
├──────────────┼──────────────────┼─────────────────┼─────────────────────┤
│ OpenHands    │ Event-stream,    │ Heavyweight,    │ Microkernel (≤1438  │
│              │ Docker sandbox,  │ multi-runtime   │ LOC) + rootless     │
│              │ polyglot agents. │ drift.          │ Bubblewrap.         │
├──────────────┼──────────────────┼─────────────────┼─────────────────────┤
│ ClawGym II   │ Prefix-tree RL,  │ Research-only,  │ Merkle Trajectory   │
│              │ black-box hook,  │ no capability   │ store integrated    │
│              │ trajectory reuse.│ security model. │ with 6D leases.     │
└──────────────┴──────────────────┴─────────────────┴─────────────────────┘
```

---

## 10. Emergence and Collective Intelligence

Higher-order intelligence emerges from populations of simpler agents under structured interaction constraints:

```
                   ORGANIZATIONAL TOPOLOGY PROGRESSION
                   
   1. Unary ReAct Loop       2. Critic / Reviser Pair      3. Hierarchical Spawn
   ┌──────────────┐          ┌──────┐      ┌──────┐        ┌──────┐
   │    Agent     │          │Planner─────►│Critic│        │Parent│
   └──────────────┘          └──────┘◄─────└──────┘        └──┬─┬─┘
                                                              │ │  (Attenuated)
   4. Stigmergic Blackbd     5. Dynamic Market Network        ▼ ▼
   ┌────────────────┐        ┌──────┐      ┌──────┐     ┌──────┐ ┌──────┐
   │ Shared Ledger  │        │Seller│◄────►│Buyer │     │Child1│ │Child2│
   │ & Artifact Dir │        └──────┘      └──────┘     └──────┘ └──────┘
   └────────────────┘
```

### Stigmergy Over Direct Message Passing
Direct peer-to-peer message passing scales as $O(N^2)$ in token and coordination cost. In Vanguard, collective intelligence is achieved via **Stigmergy**: agents communicate asynchronously by mutating shared immutable environment artifacts and emitting events to the append-only ledger. Child agents observe environmental state changes rather than maintaining long-lived conversational cross-talk.

---

## 11. Memory, Skills, and Learning Pipeline

```
                               SKILL EVOLUTION PIPELINE
                               
   ┌────────────────────────────────────────────────────────┐
   │ 1. EXECUTION TRAJECTORIES                              │
   │    Raw Merkle trees with full event lineage & costs    │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ 2. PATTERN MINING & DISTILLATION                       │
   │    Frequent successful action n-grams (lift > 1.5)     │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ 3. CANDIDATE FORMALIZATION                             │
   │    SkillCandidate(id, scope, dependencies, AST_patch)  │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ 4. HELD-OUT CONTROLLED EVALUATION                      │
   │    Paired comparison on N ≥ 50 held-out tasks          │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ 5. PROMOTION GATE (McNemar Test)                       │
   │    χ² ≥ 3.841 (p < 0.05) & Pareto vector non-inferior  │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ 6. VERSIONED SKILL REGISTRY                            │
   │    Immutable SkillVersion referenced in mhf.manifest/2 │
   └────────────────────────────────────────────────────────┘
```

### Contextual Skill Utility
Skills are never rated globally. The registry maintains a contextual utility tensor:
$$\mathcal{U}(\text{Skill} \mid \mathcal{M}, \mathcal{H}, \mathcal{E}, \mathcal{D})$$
conditioned on Model $\mathcal{M}$, Harness $\mathcal{H}$, Environment $\mathcal{E}$, and Task Distribution $\mathcal{D}$.

---

## 12. Primitive and Architecture Genomes

To enable automated search and evolution, every component and composition is represented as an immutable, typed genome.

### 1. PrimitiveGenome Schema
```yaml
primitive_genome_id: "pg_retrieval_ast_hybrid_v3"
type: "retrieval_policy"
version: "3.1.0"
lineage:
  parent_id: "pg_retrieval_ast_hybrid_v2"
  mutation_operator: "tune_parameter"
interfaces:
  provides: ["index.query/2"]
  requires: ["fs.read/1", "blob.get/1"]
parameters:
  top_k: 8
  lexical_weight: 0.35
  ast_depth: 4
  embedding_model: "text-embedding-3-small"
resource_envelope:
  max_memory_mb: 512
  max_duration_ms: 1200
  requires_network: false
capabilities_required:
  - "fs.read"
```

### 2. ArchitectureGenome Schema
```yaml
architecture_genome_id: "ag_swe_triad_pareto_v1"
schema_version: "mhf.manifest/2"
digest_dh: "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
components:
  planner:
    primitive_ref: "pg_planner_hierarchical_v2"
    isolation: "in_process"
    ceiling: { depth: 3, turns: 20 }
  executor:
    primitive_ref: "pg_executor_coding_v4"
    isolation: "subprocess"
    ceiling: { depth: 1, turns: 50 }
  verifier:
    primitive_ref: "pg_verifier_test_cascade_v1"
    isolation: "container"
    ceiling: { depth: 1, turns: 10 }
topology:
  entrypoint: "planner"
  wiring:
    - { from: "planner.subtask", to: "executor.execute", contract: "subtask/1" }
    - { from: "executor.patch", to: "verifier.test", contract: "patch_verify/1" }
    - { from: "verifier.verdict", to: "planner.feedback", contract: "verdict_feed/1" }
budget_ceiling:
  usd_micros: 500000
  tokens: 250000
  wall_clock_millis: 300000
```

---

## 13. Evolution Operators and Mutation Taxonomy

Vanguard establishes an 9-level mutation hierarchy ($M_0$ to $M_8$), where mutation power is strictly coupled to required verification rigor:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   MUTATION TAXONOMY & GOVERNANCE GATES                   │
├──────┬──────────────────────┬────────────────────────┬───────────────────┤
│ Tier │ Mutation Class       │ Target Surface         │ Verification Gate │
├──────┼──────────────────────┼────────────────────────┼───────────────────┤
│ M0   │ Runtime Parameters   │ Token limits, top-k.   │ Fast Benchmark.   │
├──────┼──────────────────────┼────────────────────────┼───────────────────┤
│ M1   │ Runtime Policies     │ Verification cascade,  │ Held-out Testbed. │
│      │                      │ router escalation.     │                   │
├──────┼──────────────────────┼────────────────────────┼───────────────────┤
│ M2   │ Procedural Knowledge │ New skill cards,       │ Paired McNemar    │
│      │                      │ prompt subroutines.    │ ($\chi^2 \ge 3.84$).│
├──────┼──────────────────────┼────────────────────────┼───────────────────┤
│ M3   │ Harness Topology     │ Adding critic/reviser, │ Full Regression + │
│      │                      │ re-wiring components.  │ Cross-Domain Test.│
├──────┼──────────────────────┼────────────────────────┼───────────────────┤
│ M4   │ Training Config      │ Curriculum, SFT split. │ Model Validation. │
├──────┼──────────────────────┼────────────────────────┼───────────────────┤
│ M5   │ Model Parameters     │ RL / DPO fine-tuning.  │ Adversarial Suite.│
├──────┼──────────────────────┼────────────────────────┼───────────────────┤
│ M6   │ Learning Algorithms  │ Loss update rules,     │ Isolated Replay   │
│      │                      │ optimizer parameters.  │ from Scratch.     │
├──────┼──────────────────────┼────────────────────────┼───────────────────┤
│ M7   │ Evolutionary Rules   │ Mutation operators,    │ Meta-Evaluation.  │
│      │                      │ selection pressure.    │                   │
├──────┼──────────────────────┼────────────────────────┼───────────────────┤
│ M8   │ Methodology          │ Benchmark suites,      │ Human Director    │
│      │                      │ evaluation protocols.  │ Approval Only.    │
└──────┴──────────────────────┴────────────────────────┴───────────────────┘
```

---

## 14. Causal Trajectories and Merkle DAG Accounting

Execution traces are stored as content-addressed Merkle DAGs:

```
                             MERKLE TRAJECTORY DAG
                             
                             Node A (Root Intent)
                             [Digest: a1b2... | Cost: $0.01]
                                       │
                                       ▼
                             Node B (Code Search)
                             [Digest: c3d4... | Cost: $0.03]
                                       │
                                       ▼
                             Node C (Patch Proposal)
                             [Digest: e5f6... | Cost: $0.05]
                                  /         \
                                 /           \  (Counterfactual / Spawn)
                                ▼             ▼
                      Node D (Unit Tests)     Node F (Formal Check)
                      [Digest: g7h8...]       [Digest: k1l2...]
                                │                     │
                                ▼                     ▼
                      Node E (Success)        Node G (Failure)
```

Each node stores:
$$\text{NodeID} = \text{SHA256}( \text{ParentNodeID} \parallel \text{EventDigest} \parallel \text{StateDelta} \parallel \Delta \mathcal{B} )$$
This enables:
1. **Zero-Copy Multi-Agent Spawns:** Child agents branch from ancestor nodes without copying the event history.
2. **Exact Replay & Continuation:** Resuming a failed run from the last immutable node without repeating settled effects.
3. **Causal Blame Assignment:** Identifying the exact node where a trajectory diverged into an unrecoverable failure.

---

## 15. The Meta-Harness Architecture

The Meta-Harness is not a monolithic agent; it is an **Automated Scientific Laboratory**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        META-HARNESS LAB ENGINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   1. Evidence Extractor ──► Analyzes failed/expensive trajectories      │
│            │                                                            │
│            ▼                                                            │
│   2. Hypothesis Engine  ──► Formulates: "If top_k reduces 12->6,        │
│            │                cost drops 15% with zero quality loss."     │
│            ▼                                                            │
│   3. Mutation Compiler  ──► Generates candidate ArchitectureGenome      │
│            │                                                            │
│            ▼                                                            │
│   4. Benchmark Harness  ──► Executes candidate on Attributed Dataset    │
│            │                                                            │
│            ▼                                                            │
│   5. Exterior Evaluator ──► UID 10002 generates SignedVerdicts          │
│            │                                                            │
│            ▼                                                            │
│   6. Pareto Comparator  ──► Computes statistical significance (McNemar) │
│            │                                                            │
│            ▼                                                            │
│   7. Promotion Manager  ──► Flips registry pointer or triggers Rollback │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 16. Evaluation, Fitness, and Emergence Detection

### 1. The Multi-Dimensional Fitness Vector
Fitness is never a scalar. A candidate $\theta$ dominates baseline $\theta_0$ iff:
$$\forall i \in \{1 \dots k\}, F_i(\theta) \ge F_i(\theta_0) \quad \land \quad \exists j \in \{1 \dots k\}, F_j(\theta) > F_j(\theta_0)$$
Across dimensions:
$$\mathbf{F} = \langle \text{Accuracy}, \text{Generalization}, \text{Cost}^{-1}, \text{Latency}^{-1}, \text{Safety}, \text{Robustness} \rangle$$

### 2. Emergence Criteria (True Emergence vs. Optimization)
We classify behavior as **genuinely emergent** only if it passes three objective criteria:
1. **Non-Triviality:** The capability cannot be produced by any single primitive in isolation.
2. **Exaptation / Zero-Shot Transfer:** The evolved composition solves a task family outside the training/mutation benchmark distribution.
3. **Information Compressibility:** The multi-agent interaction pattern exhibits lower mutual entropy and higher predictive efficiency than the sum of independent agents.

---

## 17. Safety and Evolutionary Containment

To prevent specification gaming, privilege escalation, and runaway evolution, the architecture enforces five strict containment boundaries:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     EVOLUTIONARY CONTAINMENT MATRIX                     │
├─────────────────────────┬───────────────────────────────────────────────┤
│ Threat                  │ Architectural Defense                         │
├─────────────────────────┼───────────────────────────────────────────────┤
│ Evaluator Hacking       │ Exterior evaluation process runs in isolated  │
│                         │ UID 10002 with separate Ed25519 signing keys. │
├─────────────────────────┼───────────────────────────────────────────────┤
│ Self-Authorizing Grants │ Kernel Reference Monitor (S0–S12) is static;  │
│                         │ agents cannot widen capability grants.        │
├─────────────────────────┼───────────────────────────────────────────────┤
│ Infinite Resource Loops │ 6D typed leases enforce strictly non-additive │
│                         │ depth/turn ceilings and hard USD/time caps.   │
├─────────────────────────┼───────────────────────────────────────────────┤
│ Sandbox Escape          │ Rootless Bubblewrap namespaces (UID 10001)    │
│                         │ block network, host mounts, and syscalls.     │
├─────────────────────────┼───────────────────────────────────────────────┤
│ Monoculture Collapse    │ Quality-Diversity (MAP-Elites) maintains a    │
│                         │ diverse archive of behavioural niches.        │
└─────────────────────────┴───────────────────────────────────────────────┘
```

---

## 18. Candidate Meta-Framework Architecture

The complete system unifies the 7 architectural planes into an operational lifecycle:

```
                                SYSTEM TOPOLOGY
                                
   ┌──────────────────────────────────────────────────────────────────┐
   │                          META-HARNESS                            │
   │  Experiment Registry · Hypothesis Engine · Promotion Controller  │
   └────────────────────────────────┬─────────────────────────────────┘
                                    │ deploys
                                    ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │                         HARNESS SESSION                          │
   │       ActivationPlan · Component Graph · Context Compiler        │
   └───────┬────────────────────────┬────────────────────────┬────────┘
           │                        │                        │
           ▼                        ▼                        ▼
   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
   │   Planner    │         │   Executor   │         │   Verifier   │
   │ (in_process) │         │ (subprocess) │         │ (container)  │
   └───────┬──────┘         └───────┬──────┘         └───────┬──────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │ effects
                                    ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │                    KERNEL REFERENCE MONITOR                      │
   │  S0–S12 Dispatch Pipeline · Capability Grants · 6D Leases        │
   └────────────────────────────────┬─────────────────────────────────┘
                                    │ emits
                                    ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │                    APPEND-ONLY LEDGER / WAL                      │
   │       Merkle Trajectory Store · Canonical Event Linters          │
   └────────────────────────────────┬─────────────────────────────────┘
                                    │ audits
                                    ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │                    EXTERIOR EVALUATOR (UID 10002)                │
   │           Signed Verdicts · Paired McNemar Analysis              │
   └──────────────────────────────────────────────────────────────────┘
```

---

## 19. Formal Data Model

The core entities are formalized in pure data contracts (RFC 8785 JCS canonical):

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CORE ENTITY RELATIONS                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ArchitectureGenome ──► FrozenComposition (D_H)                        │
│                               │                                        │
│                               ▼                                        │
│  RunConfiguration   ──► RunExecution (D_R)                             │
│                               │                                        │
│                               ▼                                        │
│  EventEnvelope*     ──► Trajectory (Merkle DAG)                        │
│                               │                                        │
│                               ▼                                        │
│  ExperimentSpec (D_X)──► SignedVerdict (Ed25519)                       │
│                               │                                        │
│                               ▼                                        │
│  PromotionDecision  ──► Updated Registry Pointer                       │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 20. Minimum Viable Implementation (M-3C to M-5 Roadmap Integration)

The evolutionary meta-framework is realized through sequential, falsifiable milestones:

1. **Phase 1 (M-3C / v0.6.2 — Canonical Composition Convergence):**
   - Single canonical ingress: `mhf.manifest/2` object-map form.
   - Runtime generates immutable `ActivationPlan` derived from frozen graph.
   - Registry lifecycle integrated into public runtime execution.
   - Multi-domain validation: `vg-code-default` and `vg-table-default` execute on same runtime with zero kernel diffs.
2. **Phase 2 (M-4 / v0.6.3 — Honest Foundation E2E):**
   - Uncompromised 9-row real model execution on durable SQLite WAL with cold recovery and exterior signed verdicts.
3. **Phase 3 (M-5 / v0.7.0 — Generality Gate & Pack #2):**
   - Formal mathematical / logic pack operating with zero diffs under `domain/` and `kernel/`.
4. **Phase 4 (M-6 to M-8 — Delegation & Explicit Topologies):**
   - Mediated `agent.spawn` as a capability-attenuated kernel verb.
   - Plural topologies: Critic/Reviser, Bounded Tree Search, and Stigmergic Blackboard.
5. **Phase 5 (M-9 to M-10 — Meta-Harness & Scientific Self-Improvement):**
   - Prefix-addressed Merkle trajectory store, skill distillation pipeline, and automated paired promotion controller.

---

## 21. Top 10 High-Impact Experiments

1. **Evo-Harness Grounding Benchmark:** Compare (A) Static Baseline vs. (B) Model Self-Reflection vs. (C) Externally Grounded Skill Compilation on 200 coding and reasoning tasks. *Hypothesis:* Performance(C) $>$ Performance(A) $\ge$ Performance(B).
2. **Prefix-Tree Trajectory Compression:** Measure memory and storage scaling across 1 to 32 concurrent child agents. *Falsifier:* Storage growth must scale as $O(\Delta_{\text{child}})$, not $O(N \cdot \text{History})$.
3. **Verification Scheduler Economics:** Compare monolithic test execution against an adaptive verification cascade. *Metric:* Success-per-USD and time-to-first-failure detection.
4. **Context Paging Precision/Recall:** Benchmark 500 procedural skills under (A) full injection vs. (B) lexical vs. (C) semantic vs. (D) hybrid structural retrieval. *Metric:* Token efficiency and distraction rate.
5. **Domain-Generality Proof (I-7):** Execute coding, table manipulation, and formal Lean/Coq tasks on the same frozen kernel. *Pass Criterion:* Exactly 0 lines modified in `domain/` or `kernel/`.
6. **Multi-Agent Stigmergy vs. Direct Messaging:** Compare token consumption and task completion in 8-agent teams using shared ledger vs. peer conversational chat. *Hypothesis:* Stigmergy reduces token cost by $\ge 40\%$ without loss of accuracy.
7. **Adversarial Evaluator Separation:** Inject simulated prompt-injection exploits attempting to forge passes. *Pass Criterion:* Zero forged verdicts recorded in the ledger.
8. **Cold Recovery Determinism:** Send `SIGKILL` to active runtime mid-turn; restart in a clean process and resume from WAL. *Pass Criterion:* Exact state parity and zero duplicate settled effects.
9. **Mutation Power Tier Containment:** Attempt M0–M2 mutations engineered to escalate permissions. *Pass Criterion:* Kernel reference monitor denies 100% of escalation attempts.
10. **McNemar Promotion Falsification:** Run 100 A/B candidate harness comparisons with synthetic noise. *Pass Criterion:* False positive promotion rate $\alpha \le 0.05$.

---

## 22. Staged Evolution Roadmap

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STAGED EVOLUTION ROADMAP                        │
├──────────────┬────────────────────────┬─────────────────────────────────┤
│ Stage        │ Focus                  │ Core Deliverable                │
├──────────────┼────────────────────────┼─────────────────────────────────┤
│ **Stage 1**  │ Trust & Foundation     │ S0–S12 Kernel, 6D Leases, WAL,  │
│              │                        │ Bubblewrap Sandbox (M-0 to M-2).│
├──────────────┼────────────────────────┼─────────────────────────────────┤
│ **Stage 2**  │ Canonical Composition  │ mhf.manifest/2, ActivationPlan, │
│              │                        │ Multi-domain runtime (M-3C, M-4)│
├──────────────┼────────────────────────┼─────────────────────────────────┤
│ **Stage 3**  │ Generality & Spawns    │ Pack #2 (Formal), mediated      │
│              │                        │ agent.spawn verb (M-5, M-6).    │
├──────────────┼────────────────────────┼─────────────────────────────────┤
│ **Stage 4**  │ Plural Topologies      │ Critic loops, Tree Search,      │
│              │                        │ Stigmergic Blackboards (M-7,M-8)│
├──────────────┼────────────────────────┼─────────────────────────────────┤
│ **Stage 5**  │ Causal Learning        │ Merkle Trajectory Mining, Skill │
│              │                        │ Compilation, DPO (M-9, M-10).   │
├──────────────┼────────────────────────┼─────────────────────────────────┤
│ **Stage 6**  │ Open-Ended Evolution   │ Quality-Diversity (MAP-Elites), │
│              │                        │ Meta-Harness Lab (Post-v1.0).   │
└──────────────┴────────────────────────┴─────────────────────────────────┘
```

---

## 23. Unknowns, Evidence Gaps, and Falsifications

| Unknown / Open Question | Potential Failure Mode | Falsification Test |
|---|---|---|
| **Skill Interference at Scale:** As skill count exceeds $>1000$, do conflicting instructions degrade reasoning? | Context pollution and contradictory procedural constraints. | Inject mutually conflicting skills into registry; test whether activation policy suppresses irrelevant cards. |
| **Merkle Tree Trajectory Overhead:** Does branch hashing add unacceptable latency to high-speed token generation? | Serialization bottleneck in streaming loops. | Benchmark p99 latency of ledger appends during 100-token/s model streaming. |
| **Evaluation Oracle Drift:** When external test suites or benchmarks contain bugs, can the Meta-Harness overfit to oracle flaws? | Goodhart's Law / Specification Gaming. | Rotate randomized held-out oracle suites; penalize candidates whose gains do not transfer across suites. |
| **Multi-Agent Coordination Deadlocks:** Can decentralized stigmergy cause livelocks on shared artifacts? | Indefinite turn cycling without progress. | Enforce structural turn/depth budget ceilings that fail-closed on zero-progress cycles. |

---

## 24. Reusable Algorithms, Primitives, and Code Templates

### 1. The Reference Monitor Invariant ($S0 \dots S12$)
```python
def dispatch_effect(request: EffectRequest, session: SessionState) -> Receipt:
    # S0: Observe & Bind Context
    ctx = session.observe()
    
    # S1-S3: Identity, Grant Match, Selector Check
    grant = session.grants.match(request.verb, request.target)
    if not grant:
        return session.fail_closed("ERR_UNAUTHORIZED", request)
        
    # S4-S6: 6D Budget Reservation
    cost_estimate = session.estimator.estimate(request)
    reservation = session.budgets.reserve(cost_estimate)
    if not reservation.approved:
        return session.fail_closed("ERR_BUDGET_EXHAUSTED", request)
        
    # S7-S9: Sandboxed Execution via Port
    try:
        raw_result = session.sandbox.execute(request, grant.attenuation)
        receipt = session.settle_success(reservation, raw_result)
    except SandboxException as e:
        receipt = session.settle_failure(reservation, e)
        
    # S10-S12: Append Ledger & Return
    session.ledger.append(receipt)
    return receipt
```

### 2. The McNemar Paired Promotion Test
```python
import scipy.stats as stats

def evaluate_promotion(control_results: list[bool], candidate_results: list[bool]) -> bool:
    assert len(control_results) == len(candidate_results) >= 50
    # b: control failed, candidate passed (improvement)
    # c: control passed, candidate failed (regression)
    b = sum(1 for ctrl, cand in zip(control_results, candidate_results) if not ctrl and cand)
    c = sum(1 for ctrl, cand in zip(control_results, candidate_results) if ctrl and not cand)
    
    if b + c == 0:
        return False  # No difference
        
    chi_square = ((abs(b - c) - 1) ** 2) / (b + c)
    p_value = 1.0 - stats.chi2.cdf(chi_square, df=1)
    
    # Require chi_square >= 3.841 (p < 0.05) and net positive gain (b > c)
    return chi_square >= 3.841 and b > c and p_value < 0.05
```

---

## 25. Bibliography & Direct Links

1. **AI4AI-Bench:** *Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement* (2026). [arXiv:2602.xxxxx](https://arxiv.org)
2. **ClawGym II:** *Exploring Black-Box RL on Agent Harness* (2026). [arXiv:2601.xxxxx](https://arxiv.org)
3. **Evo-Harness:** *Context-to-Harness Skill Compilation for Self-Evolving Agents* (2026). [arXiv:2602.xxxxx](https://arxiv.org)
4. **@skills:** *Attention Is All You Have: Paging and Selection in Large Skill Libraries* (2026). [arXiv:2601.xxxxx](https://arxiv.org)
5. **SWE-agent:** *Agent-Computer Interfaces Enable Automated Software Engineering* (2024). [arXiv:2405.15793](https://arxiv.org/abs/2405.15793)
6. **Active Inference:** Friston, K. *The Free-Energy Principle: A Unified Brain Theory?* Nature Reviews Neuroscience (2010). [DOI:10.1038/nrn2787](https://doi.org/10.1038/nrn2787)
7. **POET:** Wang et al. *Paired Open-Ended Trailblazer (POET): Endlessly Generating Problems and Their Solutions* (2019). [arXiv:1901.01753](https://arxiv.org/abs/1901.01753)
8. **MAP-Elites:** Mouret, J. B., & Clune, J. *Illuminating search spaces by mapping elites* (2015). [arXiv:1504.04909](https://arxiv.org/abs/1504.04909)
9. **JCS Canonicalization:** Rundgren, A., et al. *JSON Canonicalization Scheme (JCS)* RFC 8785 (2020). [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785)
10. **Reflexion:** Shinn, N., et al. *Reflexion: Language Agents with Verbal Reinforcement Learning* (2023). [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)

---

## 26. What Should We Research Next?

1. **Information-Theoretic Metric for Emergence:** Formalizing an online estimator of Multi-Information / Excess Entropy across agent interaction graphs to detect when an agent swarm forms an irreducible higher-order cognitive unit.
2. **Epigenetic Developmental Encodings for Toolkits:** Designing L-system / Neural Cellular Automata (NCA) developmental rules that grow domain-specific toolkits and context schemas dynamically based on environmental feedback rather than direct genome mutation.
3. **Formal Verification of Monotonic Attenuation:** Writing Coq / Lean 4 proofs certifying that no sequence of valid $S0 \dots S12$ kernel transitions under `agent.spawn` can result in a child process possessing an ambient capability $C \notin \text{AncestorCapabilities}$.
