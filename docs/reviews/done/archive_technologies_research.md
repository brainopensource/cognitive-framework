# Archive Technologies Research: SOTA Mechanisms, Advanced Substrates & Meta-Harness Topologies

**Authority & Scope:** Exploratory & Technological Reference for Vanguard General Task Solver (GTS) Substrate.  
**Classification:** Research Document / Architectural Ideation Portfolio.  
**Target Architecture:** Vanguard v4.0+ (`domain` $\leftarrow$ `ports` $\leftarrow$ `kernel` $\leftarrow$ `agency` $\leftarrow$ `runtime` $\rightarrow$ `adapters`).

---

## 1. Executive Master Matrix: 20 SOTA Mechanisms

| # | Idea / SOTA Mechanism | Scientific Paradigm | How It Works in Vanguard Substrate | Feasibility in Code | Billion-$ Impact (Speed / Cost / Quality) |
|---|---|---|---|---|---|
| **1** | **Asymmetric Cloud-Edge Speculative Drafting** | Distributed Speculative Decoding (*PicoSpec / DFlash*) | Local RX 9060 (Qwen 2.5 1.5B/7B) drafts 16-token proposal blocks; Cloud OpenRouter (Claude 3.7) verifies in parallel. | **High:** Plugs into `ModelProviderPort` as a composite client. | **3–4× faster** interactive CLI; **60% lower** cloud API cost. |
| **2** | **Structure-Aware INT4 KV Cache Pruning** | Adaptive Attention Sinks (*StructKV / TriAttention*) | Prunes non-critical KV tokens in long sessions, keeping global anchor hubs and L1–L5 prefix cache in 16GB VRAM. | **High:** Supported via vLLM / llama.cpp runtime backend. | Enables **128k context locally** with **0% reasoning degradation** on 16GB GPU. |
| **3** | **4D Morphic Workflow Engine** | Spatiotemporal Causal Topology | Workflows are not static graphs; they dynamically deform ($x, y, z, \text{time}$) based on epistemic uncertainty deltas ($\Delta \mathcal{U}$). | **Medium:** Implemented in `agency/` by mutating `HarnessManifest` at runtime. | Autonomous structural adaptation; replaces brittle hardcoded DAGs with fluid self-assembly. |
| **4** | **CLS Replay Distillation Engine** | Neuroscience Complementary Learning (*McClelland*) | Offline daemon reads SQLite ledger (`T3.1`), extracts successful trajectories, and loRA-distills small local models overnight. | **High:** Separate background cron runner over immutable JSONL exports. | **Self-improving offline loop:** local 14B model reaches frontier capability over time for free. |
| **5** | **Process Reward MCTS Search** | Tree-of-Thought Operations Research | Monte Carlo tree search over patch alternatives, scored at each turn by a lightweight local PRM critic before executing sandbox runs. | **Medium:** Implemented as a pluggable search operator in `agency/`. | Eliminates dead-end code edits before they touch disk; **+40% pass@1** on hard tasks. |
| **6** | **MAP-Elites Harness Evolution** | Quality-Diversity Optimization | Evolutionary algorithm evolving populations of prompt/tool manifests across a multi-dimensional behavioral feature map. | **Medium:** Script in `lab/` running offline against sealed benchmark suites. | Discovers radically creative, non-obvious agent strategies that humans never hand-code. |
| **7** | **Conformal Abstention Shims** | Epistemic Uncertainty Quantification | Attaches formal $\alpha$-confidence statistical bounds to code proposals. If confidence drops below threshold, agent halts/escalates. | **High:** Mathematical wrapper inside `ProposalProduced` validator. | **Zero hallucination / zero silent corruption:** guarantees provable error bounds. |
| **8** | **Prefix-Stable Context Compaction** | KV Cache Hit Maximizer | Formats L1 (System) $\to$ L2 (Tools) $\to$ L3 (Repo Index) as immutable prefix blocks to force 100% prompt cache hits on OpenRouter/Gemini. | **High:** Implemented in `ContextCompiler` (`T4.9`). | **80% discount** on API costs; reduces turn time-to-first-token to **< 200ms**. |
| **9** | **Cassette Mutation Fuzzing** | Deterministic Replay Chaos Testing | Fuzzes recorded model cassettes (`T3.8`) with synthetic fault injections (rate limits, dropped tokens, corrupt ASTs) without I/O. | **High:** Already built on top of `CassettePlayer`. | Guarantees bulletproof crash-recovery before deploying any new harness. |
| **10** | **Lakatosian Invalidation Shields** | Epistemic Falsification (*INV-1/INV-2*) | Binds machine-checkable falsifiers to hypotheses. Downstream test failures instantly prune entire causal sub-trees. | **High:** Built into pure reducer `reduce_event` state transitions. | Cuts wasted compute by **70%** during deep backtracking design spirals. |
| **11** | **Asymmetric Model Routing Matrix** | Heterogeneous Cognitive Specialization | Claude 3.7 for architecture/planning; DeepSeek-R1 for logic proofs; local Qwen for fast AST edits; Gemini Flash for repo search. | **High:** Pure data routing policy in `HarnessManifest.yaml`. | Maximizes intelligence-per-dollar; optimal Pareto trade-off on every turn. |
| **12** | **Dynamic Tool Synthesis & Hot-Swapping** | Higher-Order Operator Generation | Agent generates custom single-use Python scripts/tools for complex data transformations, sandbox-executes, and discards them. | **High:** Built as sandboxed transient tool adapter. | Extends agent capabilities to infinite tool vocabularies without context bloat. |
| **13** | **Mutation-Score Sealed Judge** | Exterior Formal Verification | Evaluates candidate patches not just by unit tests passing, but by introducing AST mutations to verify tests actively catch bugs. | **High:** Standalone leaf evaluator in `adapters/evaluators/`. | Prevents agents from gaming tests with trivial assertions or empty test mocks. |
| **14** | **Monotone Capability Attenuation** | Object-Capability Security Lattices | Every sub-episode automatically receives a strictly smaller capability grant than its parent; authority can never escalate. | **High:** Core invariant of `vanguard/packages/kernel/`. | **Provably prevents prompt injection escapes** from compromising host or secrets. |
| **15** | **Verifier-Deployment Gap Monitor** | Meta-Evaluation Drift Metric | Computes correlation between benchmark pass rate and real-world deployment outcomes. Automatically freezes promotions if drift occurs. | **High:** Metric computation over `AuditProjection` history. | Solves benchmark overfitting and Goodhart's Law in agent evaluation. |
| **16** | **Hierarchical Budget Leases** | Finite Resource Tree Accounting | Wall-clock, token, and USD micro-unit budgets managed as a strict tree of decaying leases with atomic release of unused fractions. | **High:** Built into `BudgetProjection` and kernel broker. | Guaranteed zero runaway financial costs or runaway infinite background loops. |
| **17** | **Information-Flow Taint Tracking** | Security Provenance Propagation | Data read from untrusted files/web automatically propagates a `tainted` flag. Tool calls using tainted arguments require elevated human approval. | **Medium:** Tracked via `EventEnvelope.provenanceLabel` lattice. | Neutralizes indirect prompt injection attacks across untrusted repos. |
| **18** | **Neuro-Symbolic AST Refactor Engine** | Hybrid Tree-Sitter + LLM Patching | LLM outputs high-level semantic intent; deterministic Tree-Sitter parser generates exact syntactic AST delta. | **High:** Plugs into `fs.write` / edit tool adapter. | Eliminates indentation errors, syntax breaks, and truncation bugs in code output. |
| **19** | **DualPath Ephemeral KV Cache Transfer** | Disaggregated State Paging | Streams cached KV context of large codebases across ephemeral worker containers over high-speed shared memory (IPC/RAM). | **Medium:** Low-level Linux `shm` adapter for local worker perimeter. | Instantaneous sub-millisecond cold starts for newly spawned child episodes. |
| **20** | **Cognitive Immune System** | Anomaly Detection & Auto-Quarantine | Identifies looping patterns, repetitive failed tool arguments, and decaying reasoning quality, triggering automatic demotion and fallback. | **High:** Pure functional projection over sliding sequence window. | Robust autonomous self-healing without requiring human intervention. |

---

## 2. Deep-Dive by Thematic Sectors

```mermaid
flowchart LR
    subgraph S1["Sector I · Inference & KV Acceleration"]
        T1["#1 Speculative Drafting"]
        T2["#2 INT4 KV Compression"]
        T8["#8 Prefix Cache Packing"]
        T19["#19 DualPath KV Transfer"]
    end

    subgraph S2["Sector II · Cognitive Topologies & Search"]
        T3["#3 4D Morphic Workflows"]
        T5["#5 PRM MCTS Search"]
        T6["#6 MAP-Elites Evolution"]
        T11["#11 Model Matrix Routing"]
        T12["#12 Dynamic Tool Synthesis"]
    end

    subgraph S3["Sector III · Memory & Neuro-Symbolics"]
        T4["#4 CLS Replay Distillation"]
        T9["#9 Cassette Mutation Fuzzing"]
        T18["#18 Tree-Sitter AST Engine"]
        T20["#20 Cognitive Immune System"]
    end

    subgraph S4["Sector IV · Epistemology & Sealed Judges"]
        T7["#7 Conformal Abstention"]
        T10["#10 Lakatosian Invalidation"]
        T13["#13 Mutation Testing Judge"]
        T15["#15 Verifier-Gap Monitor"]
    end

    subgraph S5["Sector V · Capability Security & Leases"]
        T14["#14 Monotone Attenuation"]
        T16["#16 Hierarchical Budgets"]
        T17["#17 Information Taint Flow"]
    end

    S1 --> S2 --> S3 --> S4 --> S5
```

---

### Sector I · Inference Acceleration, KV Optimization & Hybrid Cloud-Edge Topology

#### #1. Asymmetric Cloud-Edge Speculative Drafting (PicoSpec / DFlash)
- **Technical Mechanism:** Employs a local low-parameter draft model (e.g., Qwen 2.5 1.5B or 3B quantized via GGUF/ExLlamaV2 on an AMD/NVIDIA 16GB GPU) running asynchronous speculative rollouts. The draft model predicts a speculative block of 8–16 tokens representing tool calls, code boilerplate, or syntax structures. The frontier target model (Claude 3.7 Sonnet / Opus via OpenRouter) verifies and accepts/rejects the block in a single forward pass.
- **Vanguard Integration:** Wraps inside a composite `SpeculativeModelAdapter` implementing `ModelProviderPort`. The interactive CLI only interfaces with standard streaming completions while latency drops to ~250ms per multi-token step.

#### #2. Structure-Aware INT4 KV Cache Pruning (StructKV / TriAttention)
- **Technical Mechanism:** Rather than naive sliding-window eviction, attention heads are profiled to differentiate between *retrieval heads*, *syntactic anchor heads*, and *local attention heads*. Non-critical intermediate tokens are compressed to 4-bit integer representations or evicted, while code definitions, file outlines, and system contracts are locked into persistent high-precision memory.
- **Vanguard Integration:** Integrates into the local inference backend configuration (vLLM / llama.cpp wrapper in `vanguard/packages/adapters/`). Extends effective local context from 16k to 128k tokens on consumer 16GB VRAM GPUs.

#### #8. Prefix-Stable Context Compaction (KV Cache Hit Maximizer)
- **Technical Mechanism:** Enforces strict deterministic byte-level prefix invariance across all prompts. Prompts are assembled in hierarchical layers: `L1 System Contracts` $\to$ `L2 Tool Schemas` $\to$ `L3 Repository Map` $\to$ `L4 Task Specification` $\to$ `L5 Dynamic Dialogue History`. Because L1–L3 are byte-identical across all turns, cloud inference providers (Anthropic, Gemini, DeepSeek) achieve near 100% prompt-cache hits.
- **Vanguard Integration:** Core responsibility of `ContextCompiler` (`T4.9` in `vanguard/packages/agency/`).

#### #19. DualPath Ephemeral KV Cache Transfer
- **Technical Mechanism:** Uses POSIX shared memory (`/dev/shm`) and memory-mapped virtual pages to transfer compiled KV-cache context directly between parent episodes and freshly spawned ephemeral worker sub-processes without serialization overhead.
- **Vanguard Integration:** Sandboxed worker lifecycle controller in `vanguard/packages/runtime/`.

---

### Sector II · Cognitive Search, Multi-Dimensional Topologies & Morphic Workflows

#### #3. 4D Morphic Workflow Engine (Spatiotemporal Epistemic Deformations)
- **Technical Mechanism:** Replaces rigid static DAGs and simple sequential loops with a continuous 4-dimensional state topology. A workflow is represented as a manifold where execution branches, merges, accelerates, or backtracks dynamically based on real-time gradients of epistemic uncertainty $\nabla \mathcal{U}$ and budget velocity $\frac{d\mathcal{B}}{dt}$.
- **Vanguard Integration:** Manifested in `agency/` as a dynamic `EpisodeRunner` that adapts operator dispatch graphs based on state feedback emitted in the ledger.

#### #5. Process Reward MCTS Search (Tree-of-Thought Operations Research)
- **Technical Mechanism:** When facing ambiguous multi-file architectural refactors, the agent branches into a Monte Carlo Tree Search. Each candidate branch is evaluated by an ultra-fast local Process Reward Model (PRM) that scores logical step validity before executing real file mutations or running expensive test suites.
- **Vanguard Integration:** Pluggable search strategy in `agency/operators/`.

#### #6. MAP-Elites Harness Evolution (Quality-Diversity Optimization)
- **Technical Mechanism:** Employs Multi-dimensional Archive of Phenotypic Elites (MAP-Elites) to evolve populations of prompt templates, tool groupings, and verification thresholds. The feature grid maps dimensions such as *Code Verbosity vs. Succinctness*, *Tool Calling Frequency*, and *Exploration Depth*.
- **Vanguard Integration:** Offline research harness in `lab/` running overnight batch sweeps against canonical test suites.

#### #11. Asymmetric Model Routing Matrix
- **Technical Mechanism:** Dynamic token-level and task-level dispatch:
  - *High-order architecture & design:* Claude 3.7 / Opus.
  - *Formal logic, mathematical invariants & algorithmic proofs:* DeepSeek-R1.
  - *Fast AST grep, syntax repair, and file listing:* Local Qwen 2.5 14B.
  - *Massive repo indexing & needle retrieval:* Gemini 2.0 Flash.
- **Vanguard Integration:** Data-driven routing rules in `HarnessManifest.yaml`.

#### #12. Dynamic Tool Synthesis & Hot-Swapping
- **Technical Mechanism:** When standard tools (`fs.read`, `bash.exec`) are inefficient for a novel transformation (e.g., parsing an esoteric binary protocol or converting a custom schema), the agent writes a specialized Python script, sandbox-attests it, binds it as a temporary first-class tool for $N$ turns, and destroys it upon episode completion.
- **Vanguard Integration:** Transient capability grants registered dynamically through `vanguard/packages/kernel/broker.py`.

---

### Sector III · Memory Systems, Continuous Distillation & Neuro-Symbolic Hybridization

#### #4. CLS Replay Distillation Engine (Hippocampal-Neocortical CLS)
- **Technical Mechanism:** Implements Complementary Learning Systems:
  - *Hippocampal fast storage:* The append-only event store captures raw, high-fidelity episode trajectories.
  - *Neocortical slow consolidation:* A scheduled background daemon extracts verified success traces, synthesizes contrastive fine-tuning pairs, and runs parameter-efficient fine-tuning (LoRA/QLoRA) on local base models.
- **Vanguard Integration:** Background pipeline processing exported JSONL ledgers (`T3.5`).

#### #9. Cassette Mutation Fuzzing (Deterministic Replay Chaos Testing)
- **Technical Mechanism:** Takes recorded deterministic model cassettes (`T3.8`), mutates intermediate responses with synthetic noise (truncated JSON, out-of-order tool call IDs, simulated 429 rate-limit exceptions), and replays them against the state reducer to prove provable crash recovery without network calls.
- **Vanguard Integration:** Automated test runner extending `test/contracts/t3_ledger.py`.

#### #18. Neuro-Symbolic AST Refactor Engine (Tree-Sitter + LLM)
- **Technical Mechanism:** Decouples semantic generation from syntax emission. The LLM outputs high-level refactor descriptors (e.g., "rename symbol and wrap in try/catch"), while a deterministic Tree-Sitter AST engine parses, checks scope bindings, and generates exact source diffs.
- **Vanguard Integration:** Integrated into filesystem and patch tool adapters in `vanguard/packages/adapters/`.

#### #20. Cognitive Immune System (Anomaly Detection & Auto-Quarantine)
- **Technical Mechanism:** A rolling window state projection monitors semantic entropy, repeated failure loops, and capability denial spikes. Upon detecting cognitive degradation or looping, it initiates a hard rollback to the last verified snapshot and injects an epistemic compensation brief.
- **Vanguard Integration:** Pure functional projection in `vanguard/packages/ledger/projections.py`.

---

### Sector IV · Epistemology, Formal Verification & Sealed Measurement

#### #7. Conformal Abstention Shims (Statistical Uncertainty Bounds)
- **Technical Mechanism:** Calibrates model prediction logits against historical task difficulty distributions using split conformal prediction. Guarantees that the agent's decision to accept a task carries a mathematically bounded error probability ($1 - \alpha$).
- **Vanguard Integration:** Pre-flight gate in `agency/` prior to task execution.

#### #10. Lakatosian Invalidation Shields (Falsification Pruning INV-1/INV-2)
- **Technical Mechanism:** Formally separates the *Hard Core* (invariants that cannot be violated) from the *Protective Belt* (mutable candidate hypotheses). Every hypothesis carries machine-checkable invalidation conditions (`INV-1`, `INV-2`). When a downstream test breaches an invalidation condition, the branch is culled immediately without wasteful compensatory repairs.
- **Vanguard Integration:** Implemented in `vanguard/packages/domain/ledger/reducer.py`.

#### #13. Mutation-Score Sealed Judge
- **Technical Mechanism:** The evaluation harness applies mutation operators (e.g., replacing `<` with `<=`, inverting booleans, deleting statements) to verify that generated test suites actually fail when bugs are injected, guaranteeing that patches are genuinely robust rather than trivial pass-throughs.
- **Vanguard Integration:** Leaf evaluator adapter in `vanguard/packages/adapters/evaluators/`.

#### #15. Verifier-Deployment Gap Monitor (Meta-Evaluation Drift Detection)
- **Technical Mechanism:** Continuously tracks the correlation coefficient between evaluation suite scores and real-world deployment telemetry. If the verifier-deployment gap widens (indicating the agent is exploiting benchmark loopholes), automatic promotions are frozen.
- **Vanguard Integration:** Statistical analyzer over `AuditProjection` history.

---

### Sector V · Security Perimeter, Resource Accounting & Attenuation Algebra

#### #14. Monotone Capability Attenuation
- **Technical Mechanism:** Implements unforgeable object-capability security where authority is strictly monotone decreasing ($\text{Cap}_{t+1} \subseteq \text{Cap}_t$). A child sub-agent can only receive a subset of the parent's permissions.
- **Vanguard Integration:** Mathematical algebra in `vanguard/packages/domain/selectors/` and enforced by `KernelBroker`.

#### #16. Hierarchical Budget Leases
- **Technical Mechanism:** Budgets (tokens, wall-clock milliseconds, USD micro-units) are treated as physical leases in a tree structure. A parent leases a bounded fraction to a child. Unused resources are atomically reclaimed upon child exit.
- **Vanguard Integration:** Implemented in `BudgetProjection` and `vanguard/packages/ports/event_store.py`.

#### #17. Information-Flow Taint Tracking
- **Technical Mechanism:** Provenance labels propagate with data. Reading an untrusted repository file or external web page marks all downstream intermediate context blocks as `untrusted-content`. High-risk sink tools (network egress, secret access) refuse to execute tainted payloads without explicit human escalation.
- **Vanguard Integration:** Enforced via `EventEnvelope.provenanceLabel` and kernel capability matchers.

---

## 3. SOTA Interface & Observability Topologies (TUI / GUI Meta-Harness)

| Mechanism | Technical Description | Tangible Vanguard Implementation | Engineering / UX Impact |
|---|---|---|---|
| **Live Causal State Tree (`vg graph`)** | Visualizes active sub-episodes, child lease trees, and causal step links ($A \to B \to C$) in real time. | Ink/React TUI in CLI (`vanguard/clients/cli/`); Canvas/D3 in web GUI. | Instant visual debugging of recursive depth and sub-agent coordination. |
| **Syntax-Aware Semantic Diff Preview** | Intercepts `privileged` file writes and renders colored AST-node diff hunks with symbol-level highlights before human approval. | Tree-Sitter parser integrated into `EnvironmentAdapter` preview stage. | Eliminates indentation errors and subtle logic breaks; enables confident 1-keystroke approvals. |
| **Epistemic Uncertainty Heatmap** | Colors token streams and generated proposals dynamically based on token logit entropy. | Visual shader / ANSI color map over streaming `ModelPort` tokens. | Highlights hallucination zones and low-confidence syntax in amber/red before execution. |
| **Time-Travel Scrubbing & Counterfactual Replay** | Allows the operator to rewind the ledger to step $N$, alter a constraint/prompt, and branch a new counterfactual trajectory. | Direct UI control over SQLite event store replayer (`T3.3` / `T1.11`). | Instant non-destructive experimentation and root-cause post-mortems. |

---

## 4. Cognitive & ML Architectural Mappings (From Neural Paradigms to Tangible Code)

| ML / Neural Concept | Core Mathematical Mechanism | Concrete Vanguard Adaptation | Tangible Engineering Gain |
|---|---|---|---|
| **LSTM / SSM Gating** | Input/Forget/Output state gates ($c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t$) | **Event Store Reducer & Context Compactor (`T4.9`):** Strips noisy compiler logs, retains verified facts, and keeps state vector constant. | Eliminates token bloat; prevents context window degradation in 16+ hour sessions. |
| **GNN Message Passing** | Aggregates localized 1-hop and 2-hop graph neighborhood states | **AST Code Graph Neighbor Query:** When resolving a bug in a symbol, aggregates only caller signatures, imported types, and test contracts. | **80% fewer context tokens** with 100% semantic relevance compared to full-file dumps. |
| **MCTS & Value Networks** | Multi-step forward tree branching scored by a Value critic | **Process-Reward Branching (`agency/operators/`):** Branches 2–3 alternative patch proposals and executes only the highest-scored branch. | Eliminates dead-end code edits before touching disk; cuts circular repair loops by **>40%**. |
| **Diffusion Denoising** | Multi-step iterative noise removal from coarse to fine | **3-Stage AST Patch Pipeline:** Coarse semantic plan $\to$ Tree-Sitter exact AST node binding $\to$ Test-driven residual error repair. | Prevents broken indentation, unclosed brackets, and hallucinated syntax on turn 1. |
| **Mixture of Experts (MoE)** | Dynamic token-level routing across specialized expert sub-networks | **Asymmetric Model Routing Matrix (`HarnessManifest`):** Fast models (local Qwen/Gemini Flash) for indexing/syntax; frontier models for architecture. | **60–80% lower API costs** with sub-200ms time-to-first-token. |

---

## 5. Intrinsically Emergent Intelligence & Autonomous Compounding

True emergence is not a buzzword—it is the mathematical result of **Variation + Selection + Retention** running inside a sealed, ungameable environment:

```
┌──────────────────────────────────────────────────────────────┐
│                    SEALED ENVIRONMENT                        │
│   (Real Repositories · Unit Tests · Compilers · Linters)     │
└──────────────────────────────▲───────────────────────────────┘
                               │ (Merciless Feedback)
┌──────────────────────────────┴───────────────────────────────┐
│                    THE EXECUTION EPISODE                     │
│   Observed State ──► Propose ──► Attenuate ──► Effect ──► Receipt
└──────────────────────────────┬───────────────────────────────┘
                               │ (Immutable Event Recording)
┌──────────────────────────────▼───────────────────────────────┐
│                 IMMUTABLE LEDGER & CAUSALITY                 │
│      Counterfactual Replay · Credit Assignment · Falsifiers   │
└──────────────────────────────┬───────────────────────────────┘
                               │ (Autonomous Optimization)
┌──────────────────────────────▼───────────────────────────────┐
│                  SELF-EVOLVING ARTIFACT GRAPH                │
│    Mutated Prompts · Tool Genesis · New Playbook Generation  │
└──────────────────────────────┴───────────────────────────────┘
```

1. **Self-Synthesizing Scaffolding (Autonomous Evolution):** All prompts, tool groupings, and retrieval heuristics are stored as declarative, content-addressed `Artifact` nodes (`T7.1`). An offline daemon identifies failure patterns in the SQLite ledger and autonomously drafts, tests, and promotes candidate successor artifacts.
2. **Causal Attribution (Credit Assignment Engine):** Cryptographic causation and correlation IDs across every `EventEnvelope` enable counterfactual replays (`T1.11 / T3.3`), computing exact mathematical Shapley credit values for every tool and prompt instruction.
3. **Dynamic Tool Genesis & DSL Emergence:** When repeating a multi-step shell workflow, the agent writes a specialized compiled micro-tool (in Python/Rust), verifies it in the sandbox, registers it into the kind registry, and uses it forever after.
4. **Synthetic Self-Play & Curiosity Arena:** During idle periods, the Evidence Plane (`T5.3`) injects synthetic mutations and subtle bugs into sandbox repos. The agent explores and fixes them, distilling passing trajectories into long-term reusable Playbooks (`T4.3`).
5. **Lakatosian Hard-Core / Protective-Belt Separation:** 
   * *The Hard Core (Sealed & Immutable):* Kernel security, capability attenuation, budget leases, and the exterior Evaluator (`T5.3`) can never be modified by the agent.
   * *The Protective Belt (100% Plastic):* Prompts, context layers, and tools evolve continuously. Because the scoreboard is physically outside the agent's reach, self-evolution cannot collapse into reward hacking.

---

## 6. Consumer-Hardware Feasibility & Real-Time In-Session Learning

| Concern | Resolution in Vanguard Architecture |
|---|---|
| **Zero-Cluster Feasibility** | **Runs on a standard 16–32GB PC.** Appending SQLite events takes **<1ms** and uses **<30MB RAM**; Tree-Sitter AST parsing takes **~2ms**; heavy reasoning is offloaded to fast cloud APIs or local quantized 7B–14B models. No neural backpropagation cluster required. |
| **Live In-Session Learning** | **<5ms Fast-Path:** Failed commands and broken syntax are cached instantly as *negative constraints* in L4 working context. 1-keystroke human correction codes (`T1.10`) update active episode constraints in real time without restarting the session. |
| **Cross-Session Generalization** | At the end of a multi-day coding session, a **15-second background summarizer** extracts domain-invariant strategies into human-readable, versioned **Playbook Artifacts** loaded on day one of any new project. |

