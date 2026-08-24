# AETHER / VANGUARD: EXECUTIVE & ARCHITECTURAL MASTER REPORT
**Substrate Status, Meta-Framework Generality, and Next-Generation Roadmap**

---

| Executive Dimension | Detail / Current Authority |
|---|---|
| **Author Perspective** | CEO, Principal Staff Engineer, AI PhD Specialist, Chief Architect, Senior Dev, Tech Lead |
| **Normative Authority** | `docs/SPEC.md` + `docs/01_law/` + ADR-0069 through ADR-0091 |
| **Execution State** | **M-3C Closed; W-3D Profile Wave Complete; M-4 Environment Qualification Open (RF-85)** |
| **Shipped Package** | `vanguard-runtime` `0.4.5b1` (Python `>=3.10`, tested on Python 3.12) |
| **Production Truth** | `vanguard/packages/` (`domain` → `ports` → `kernel` → `agency` → `runtime` → `adapters`) |

---

## 1. Executive Summary & Strategic Positioning (CEO Perspective)

Vanguard / AETHER is engineered around a singular core thesis: **Raw model capability changes every six months, but the verifiable trust, execution provenance, capability attenuation, and deterministic attribution spine is permanent enterprise value.**

### 1.1 The Market Trap vs. The Defensible Moat
In the current agent ecosystem (SWE-bench, Terminal Bench, WebArena):
- **Scaffolding is worth ~4 percentage points**; model generation is worth tens of points. Attempting to build an un-differentiated coding wrapper that relies on prompt magic is a commodity race to the bottom.
- **The Defensible Differentiator is Attributability:** No mainstream agent framework can produce:
  1. Cryptographically signed exterior verdicts (Ed25519) physically isolated from the agent worker (UID `10001` vs UID `10002`).
  2. Byte-exact replayable execution trajectories ($D_H, D_R, D_X$) with exact token/dollar accounting and zero fabricated zeros.
  3. Crash-resilient state continuation (SQLite WAL) where process death never duplicates already settled real-world effects.
  4. Typed four-state evidence algebra (`present_valid`, `unverifiable`, `invalid`, `absent`) instead of binary subjective self-reporting.

### 1.2 The Two Flagship Product Horizons
By establishing Vanguard as a **Domain-Agnostic Substrate (Meta-Framework)**, we unlock two high-value production products from a single immutable engine:
1. **Autonomous Coding Agent CLI (`vg-code`):** An industrial-grade CLI (competing directly with Claude Code and Codex CLI) with Tree-Sitter repo-mapping, AST diff patching, subagent delegation, and prompt-cache-aligned prefix management.
2. **Deep Intelligence & Scientific Research Agent (`vg-research`):** An epistemic search and discovery agent with source quote hash-chains, multi-query web crawling, PDF/table extraction, and cryptographic claim-to-evidence provenance graphs.

---

## 2. Comprehensive Inventory: What Has Been Built & Verified

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             HEXAGONAL PRODUCTION LATTICE                         │
│   domain  ←  ports  ←  kernel  ←  agency  ←  runtime  →  adapters  (apps/cli)    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Layer-by-Layer Architectural Audit

| Subsystem | Physical Path | As-Built Capabilities & Invariants |
|---|---|---|
| **Domain** | `vanguard/packages/domain/` | Pure Python stdlib. Wire contracts (`jsonrpc.py`, `wire/contracts.py`), RFC 8785 JSON Canonicalization Scheme (`jcs.py`), single canonical selector algebra (`resource_selector.py`), ledger state reducers, and evidence models. Zero internal repo imports. |
| **Ports** | `vanguard/packages/ports/` | Hexagonal port interfaces: `KernelPort`, `ModelPort`, `SandboxPort`, `EvaluatorPort`, `EventStorePort`, `BlobStorePort`, `EnvironmentPort`, `DeterminismPort`, `IndexPort`, and the 5 SPI protocols (`spi.py`). |
| **Kernel (TCB)** | `vanguard/packages/kernel/` | Pure security core ($1366 \le 1438$ LOC ceiling). **13-Stage effect dispatch pipeline (S0–S12)** (`dispatch.py`), monotonic capability attenuation (`attenuation.py`), 6D typed budget algebra (`budget.py`), descriptor-bound capability grants (`grants.py`), and fail-closed policy enforcement. Domain-blind (Invariant I-7). |
| **Agency** | `vanguard/packages/agency/` | Unary sequential episode machine (`EpisodeEngine`). Enforces budget ceilings, handles context compilation, and executes structured token compaction. |
| **Runtime** | `vanguard/packages/runtime/` | System composition and lifecycle. Canonical composition compiler (`compose.py`), single entrypoint `run_composed()` (`root.py`), session management (`session.py`), single-writer `LedgerEmitter`, evaluator gateway, and execution profiles (`profiles.py`). |
| **Adapters** | `vanguard/packages/adapters/` | Concrete implementations: Model adapters (OpenRouter, Ollama, Cassette, Fake), Exterior Evaluator RPC & Ed25519 signing daemon, Rootless Bubblewrap Sandbox (`sandbox/rootless.py`), and SQLite-WAL event store. Adapters never import `kernel` or `agency`. |
| **Domain Pack #1** | `packs/code-default/` | Modular Harness Framework pack for coding: `harness.yaml`, plugin manifests (`fs`, `ast-patch`, `repo-map`, `terminal`, `evaluation-gate`, `single-planner`), prompt templates. |
| **Interactive CLI** | `vanguard/clients/cli/` | TypeScript/React/Ink terminal UI (`vg`). Driven by Node stdlib and React/Ink without polluting the Python backend. |

### 2.2 Milestone Retrospective & Verification Matrix

```text
M-0 (Truth) ──> M-1 (Trust Spine) ──> M-2 (WAL & Recovery) ──> M-3C (Convergence) ──> W-3D (Profiles) ──> M-4 (Real Run)
```

- **M-0 (Engineering Truth - CLOSED):** All CI runs measure production packages under `vanguard/packages/`. Falsifier harness established (RF-01 through RF-21).
- **M-1 (Fail-Closed Trust Spine - CLOSED):** S0–S12 dispatch reference monitor verified; descriptor-bound grants prevent capability escalation; signed evaluator verdicts bound to worker output.
- **M-2 (Truthful Trajectories & Recovery - CLOSED):** Implemented `mhf.trajectory/1` with explicit token and latency accounting (no fabricated zeros); SQLite WAL crash recovery proved via `os._exit` fresh-process tests (RF-25).
- **M-3C (Canonical Composition Convergence - CLOSED):** Replaced legacy split parsers with single canonical `mhf.manifest/2` compiler; unified lifecycle state machine (`PluginDiscovered` $\to$ `PluginVerified` $\to$ `PluginActivated`); enabled namespaced binding providers.
- **W-3D (Product Runtime Profiles - CLOSED):** Added profile presets (`local`, `sandboxed`, `release`) under ADR-0089. Enabled local development on WSL2/macOS with host fallback while ensuring release builds fail-closed without Bubblewrap isolation.
- **Foundation Performance Wave (CLOSED):** Implemented layer interning and digest memoization in `runtime/context_store.py` plus PEP-562 lazy model imports:
  - **11.0× RAM reduction** (50-turn retention: 304 KB $\to$ 27 KB)
  - **11.9× CPU canonicalization speedup** (200-turn digest: 135 ms $\to$ 11.4 ms)
  - **10.9× cold start speedup** (lazy urllib/model loading: 140 ms $\to$ 12.9 ms)
  - Full suite unchanged: 1,294 passed / 8 environment skips.

---

## 3. Analysis of Reviews: Historical Proposals vs. Principal Audit

### 3.1 Historical Proposals (Alfa, Fi, Higgs) — Lessons Learned
- **Proposals 001–008 (Alfa, Beta, Delta, Epsilon, Fi/GPT-Sol, Zeta, Grok):** Contributed foundational ideas (Lexicographic Pareto controller, Active Inference belief updates, SQLite State Plane, A-B-C-D authority boundary). However, they also proposed speculative features that threatened to bloat the TCB (putting swarms, reinforcement learning, or graph neural networks into the kernel).
- **Higgs Architecture Review:** Correctly diagnosed the M-3 "dual authority" bug (where `mhf.manifest/2` existed on paper but the runtime still executed the legacy loader). This directly triggered the M-3C convergence wave.

### 3.2 Principal Staff Engineer Audit (M-4 $\to$ M-8 Forensic Review)
The latest independent auditor review clarified three critical laws:
1. **The Invariant I-11 Concurrency Rule (M-7):** Concurrency must not be built based on theoretical manifests. Statically, two file operations on `/workspace` appear to conflict; dynamically, they touch disjoint files 80%+ of the time. We must capture runtime `EffectStarted` payloads over sequential runs before writing a leasing scheduler.
2. **Topologies as Declarative Manifests (M-8):** Multi-agent patterns (Planner-Coder-Critic, Debate, Tree Search) do not require a new workflow engine. They are expressed as declarative role sequences in `mhf.topology/1`, utilizing M-6 capability attenuation to enforce role boundaries (e.g. Critic is physically denied write permissions).
3. **Attributability is the True North:** Compete on *verifiable, immutable science*. A run must be pinned to $D_H$ (Harness), $D_R$ (Run Plan), and $D_X$ (Execution Hash Chain).

---

## 4. Master Roadmap: Immediate & Future Execution

```text
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│       STEP 1: M-4       │ ──> │       STEP 2: M-5       │ ──> │       STEP 3: M-6       │
│  RF-85 Qualification &  │     │   Generality Proof via  │     │ Capability-Mediated     │
│   Single Real Run       │     │   Formal Domain Pack #2 │     │ `agent.spawn`           │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
                                                                             │
                                                                             ▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│       STEP 6: M-9       │ ──> │       STEP 5: M-8       │ ──> │       STEP 4: M-7       │
│  Epistemic Compounding  │     │ Declarative Topologies  │     │ Sequential Effect Log & │
│  & Retrieval Labs       │     │ (Critic, Debate, Swarm) │     │ Measured Concurrency    │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

### Step 1: M-4 Single-Run Foundation Evidence (RF-85)
- **Environment:** Clean Linux host (non-root, non-WSL) with Bubblewrap UID `10001` and Evaluator UID `10002`.
- **Action:** Preregister coding task and oracle digest; execute one uninterrupted run via `Runtime.run_composed()`.
- **Target:** Populate all 9 rows of `mhf.foundation-evidence/1` with zero mocks, cassettes, or manual interventions.

### Step 2: M-5 Generality Proof (Formal Domain Pack #2)
- **Objective:** Prove Vanguard is a domain-agnostic meta-framework, not a dedicated coding harness.
- **Action:** Implement Domain Pack #2 (e.g. Formal Math / Table Reasoning / Epistemic Logic).
- **Enforcement:** **RF-86 Zero-Diff Gate** (`ci/rf86_gate.sh`): Pack #2 must execute with zero lines modified in `domain/`, `ports/`, `kernel/`, `agency/`, or `runtime/`.

### Step 3: M-6 Mediated Delegation (`agent.spawn`)
- **Authority:** ADR-0090 ratified event roster (`ChildSpawned`, `ChildReturned`).
- **Mechanics:** An agent requests `agent.spawn` through S0–S12. The runtime spawns an attenuated child context where capabilities, 6D budget, depth, and turn limits strictly decrease down the tree.
- **Recovery:** Cold recovery folds open child states and prevents duplicate execution upon parent crash.

### Step 4: M-7 Measured Scheduler & Concurrency
- **Prerequisite:** Capture real runtime effect instances (`EffectStarted` with concrete paths) during sequential baseline runs.
- **Gate:** Run the independence analyzer. If independent fraction $>30\%$, author an ADR to lift Invariant I-11 and introduce lease-based parallel dispatch; if $<30\%$, retain the robust sequential turn loop.

### Step 5: M-8 Explicit Topology Topologies
- Define `mhf.topology/1` schemas for Multi-Agent Architectures (Author-Critic, Planner-Executor-Verifier, Round-Robin Debate).
- Enforce role attenuation at runtime via M-6 grants without modifying the core episode engine.

---

## 5. Architectural Blueprint: Two Independent General Task Solvers

```text
                                  ┌────────────────────────┐
                                  │  Vanguard Meta-Kernel   │
                                  │  (S0-S12, WAL, Budget) │
                                  └───────────┬────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         ┌─────────────────────────┐                     ┌─────────────────────────┐
         │     CASE 1: CODING      │                     │    CASE 2: RESEARCH     │
         │ Autonomous Coding Agent │                     │  Deep Literature Agent  │
         ├─────────────────────────┤                     ├─────────────────────────┤
         │ • AST Tree-Sitter Patch │                     │ • Web Search & Scrape   │
         │ • Repo-Map Indexing     │                     │ • Markdown/PDF Parsers  │
         │ • Sandbox Proc Runner   │                     │ • Citation Graph Engine │
         │ • Test Suite Gate       │                     │ • Synthesis & Deduct    │
         └─────────────────────────┘                     └─────────────────────────┘
```

### Case 1: Industrial Autonomous Coding Agent CLI (`packs/coding-pro/`)
- **Core Domain Primitives:**
  - `fs.read`, `fs.write`, `fs.glob`, `fs.grep` (bounded by workspace directory selectors).
  - `patch.apply` (Tree-Sitter AST-aware fuzzy matching unified diff patcher).
  - `proc.exec` (isolated in rootless Bubblewrap with CPU/RAM/wall-clock constraints).
  - `git.checkout`, `git.diff`, `git.commit` (version control tracking).
  - `test.runner` (isolated test execution producing structured failure receipts).
- **Topology Configuration (M-8 Manifest):**
  - *Lead Architect:* Read-only capability, analyzes problem, generates execution plan.
  - *Implementer:* Read-write capability, applies patches, edits files.
  - *Verifier / Evaluator:* Executes test suites, verifies assertions, generates feedback loop.

### Case 2: Deep Scientific & Intelligence Research Agent (`packs/researcher/`)
- **Core Domain Primitives:**
  - `web.search` (multi-engine aggregator: Google, Tavily, SearXNG, Semantic Scholar).
  - `web.fetch` (headless HTTP fetching with automated Readability markdown conversion).
  - `doc.parse` (PDF, arXiv, LaTeX, and table parsing into structured token chunks).
  - `citation.bind` (immutable provenance tracking: records URL, SHA-256 content hash, and timestamped verbatim excerpt).
  - `graph.synthesize` (connects claims, supporting evidence, and contradictory evidence into an epistemic belief network).
- **Topology Configuration (M-8 Manifest):**
  - *Query Planner:* Decomposes high-level research questions into sub-queries.
  - *Crawler / Scout:* Traverses web pages and fetches academic literature in parallel.
  - *Fact Extractor:* Extracts atomic facts and data tables with strict attribution links.
  - *Chief Synthesizer:* Drafts literature review, checks citation integrity, and audits contradictory evidence.

---

## 6. Scientific Event-Sourced Methodology & Observability

To meet the highest standards of scientific reproducibility, every event inside Vanguard is recorded in the append-only SQLite WAL:

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      EVENT-SOURCED SCIENTIFIC LOGGING                           │
│                                                                                 │
│   Input       Transform       Authorize        Effect        Receipt     Verdict│
│  ───────> ─────────────────> ───────────> ─────────────────> ───────> ────────── │
│  Prompt    Token / AST / Ref   S0-S12 TCB   Sandbox UID10001   WAL     UID10002 │
│                                                                                 │
│      Replayable Trajectory (D_R) + Hash-Chained SQLite WAL + Signed Evidence    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.1 The Cryptographic Identity Triad
1. **$D_H$ (Harness Digest):** SHA-256 JCS hash of all plugin manifests, tool schemas, system instructions, and sandbox configurations.
2. **$D_R$ (Run Digest):** SHA-256 JCS hash of task description, initial workspace tree hash, model route, and allocated budget.
3. **$D_X$ (Execution Digest):** Incremental cryptographic hash chain over all ledger events from $E_0$ to $E_N$.

### 6.2 Granular Scientific Telemetry
Every turn captures exact empirical observations:
- **LLM Invocations:** Input prompt tokens, cached prompt tokens, completion tokens, TTFT (time-to-first-token), total latency (ms), exact USD cost, provider fingerprint.
- **Kernel Dispatch:** Capability descriptor evaluation, 6D budget reservation, pre-effect durable intent ($S8a$), sandbox exit codes, post-effect settlement ($S12$).
- **Context Dynamics:** Active token count, compaction compression ratio, context layer interning hit rate.
- **Statistical A/B Benchmarking:** Prompts, models, and topologies are compared using **paired McNemar tests** and Fisher exact tests over fixed-seed benchmark suites to prove statistically significant improvements.

---

# 7. RESEARCH COMPLEMENT: DeepSeek Harness, Claude Code CLI & Codex Architecture

This chapter synthesizes cutting-edge architectural patterns from the latest open-source and proprietary agent harnesses to guide the implementation of Vanguard's domain packs and CLI.

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SOTA EXTENSIBILITY LAYER                              │
│                                                                                 │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────────┐  │
│  │   Plugin SPI & MCP    │  │    Repo & Retrieval   │  │ Context Management  │  │
│  │ Model Context Protocol│  │  Tree-Sitter + BM25   │  │ Layer Interning &   │  │
│  │ Dynamic Tool Registry │  │  Multi-Tier Indexing  │  │ Prompt Cache Optim  │  │
│  └───────────────────────┘  └───────────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 7.1 DeepSeek Harness (`dsh`) Research & Deconstruction

Released by DeepSeek AI (mid-August 2026), **DeepSeek Harness (`dsh`)** is built on the **Cordis** meta-framework and introduces several breakthrough architectural concepts.

#### 1. The "Everything is a Plugin" Architecture
- **Separation of Mind and Hands:** The core runtime is completely agnostic to what the agent does. The LLM is treated as a swappable "mind," while tools, environments, UI, and session stores are modular plugins.
- **Plugin Composable Ecosystem:** In `dsh`, even the agent loop itself is a plugin. A single configuration file determines whether the runtime executes a simple linear chain, an interactive web REPL, or a multi-turn SWE-bench evaluation runner.
- **Direct Alignment with Vanguard:** Vanguard's Modular Harness Framework (`mhf.manifest/2`) and the 5 Port SPIs (`ToolProvider`, `ContextProvider`, `PromptProvider`, `PolicyHook`, `StorageProvider`) match this philosophy directly, with the added advantage of Vanguard's kernel-enforced capability security and sandboxing.

#### 2. Lessons from DeepSeek-V4 Benchmarks & Evaluation
- DeepSeek achieved top SWE-bench and Terminal Bench results by running in a "minimal mode" harness, proving that **clean, low-overhead harnesses with concise tool feedback outperform complex, noisy multi-agent frameworks**.
- **Contamination Resistance:** Evaluating models requires strict isolation of benchmark tasks from the model's training memory. Vanguard's preregistered task/oracle model ensures tamper-proof scientific attribution.

---

### 7.2 Claude Code CLI Research & Deconstruction

Anthropic's **Claude Code CLI** is currently the state-of-the-art terminal-native autonomous coding assistant. Its architecture is refined for extreme token efficiency, speed, and long-horizon reliability.

#### 1. The "Gather, Act, Verify" Loop
Unlike naive ReAct loops that jump straight into writing code, Claude Code strictly enforces a three-phase cognitive loop:
1. **Gather:** Scout the repository using fast, low-cost search tools (`grep`, `glob`, symbol queries). Read file outlines before reading raw lines.
2. **Act:** Formulate a targeted patch using an AST-aware or line-oriented diff tool. Modify only the necessary lines.
3. **Verify:** Immediately run lint checks, typecheckers, or unit tests to confirm the fix before reporting completion.

#### 2. Prompt Caching & Prefix Optimization (The 90% Cost Reduction Moat)
- Claude Code is designed specifically to maximize Anthropic's **Prompt Caching** (and DeepSeek's KV Cache):
  - **Static Prompt Ordering:** System instructions, developer guidelines (`CLAUDE.md` / `AGENTS.md`), tool definitions, and baseline environment specifications are placed at the **exact prefix** of the prompt array.
  - **Append-Only History:** New turns and tool receipts are strictly appended to the tail. The static prefix never shifts by even a single byte.
  - **Result:** **~90% reduction in input token costs** and up to **85% reduction in latency**, because the model provider reuses the KV cache across dozens of consecutive turns.

#### 3. Subagents & Focused Context Isolation
- Claude Code dynamically spawns lightweight subagents for isolated research tasks (e.g. searching 50 files for a symbol definition).
- The subagent executes in its own ephemeral context window and returns only a concise 2-sentence summary back to the main agent.
- This prevents the primary session from suffering from **Context Collapse** or catastrophic attention degradation.

#### 4. Auto-Compaction Pipeline
- When the active conversation reaches $\sim 70\%$ of the context limit, Claude Code executes an automatic background compaction:
  - Prunes verbose tool outputs (e.g., massive 500-line test outputs are collapsed into exit codes and failing stack traces).
  - Summarizes resolved intermediate steps while preserving the active task goal, open questions, and modified file list.

#### 5. Model Context Protocol (MCP) Integration
- Supports local and remote MCP servers via JSON-RPC, enabling instant integration with databases, GitHub PRs, Slack, and custom enterprise tools without writing custom agent code.

---

### 7.3 Codex CLI & Modern Repo-Mapping Architecture

Techniques pioneered by Codex CLI, Aider, and OpenCode provide the blueprint for repository-level intelligence.

#### 1. AST-Based Repository Mapping ("Repo Map")
- **The Problem:** Passing an entire 100,000-line codebase to an LLM is impossible or prohibitively expensive.
- **The Solution:** Use **Tree-Sitter** to parse the entire codebase into an Abstract Syntax Tree (AST), extracting only:
  - File paths and directory hierarchy.
  - Class definitions, method signatures, and exported function interfaces.
  - Import dependency graphs (e.g., `Module A` imports `Class B` from `Module C`).
- **PageRank Symbol Ranking:** Use a graph ranking algorithm (similar to Google PageRank) over the import graph to identify the most central "hub" classes in the project.
- **Result:** A 1,000-token structural skeleton that gives the LLM complete architectural awareness of a massive repository.

#### 2. Incremental Git-Aware Indexing
- The repo map is cached locally as a structured JSON graph.
- On each command, the agent inspects `git status` / `git diff HEAD` to identify only modified files, updating the AST index incrementally in $<20\text{ ms}$.

---

## 8. SOTA Design Patterns for Vanguard's Next Phase

Integrating these insights into Vanguard yields the following concrete architectural implementations:

| SOTA Feature | Vanguard Implementation Design | Architectural Layer |
|---|---|---|
| **MCP Tool Bridge** | `vanguard/packages/adapters/tools/mcp.py`: An adapter implementing `ToolProvider` that connects to any MCP server over stdio/SSE and translates MCP tools into Vanguard S0–S12 capability grants. | `adapters/` |
| **Prefix-Cache Alignment** | `vanguard/packages/agency/context/compiler.py`: Re-order context layers into static immutable blocks ($L_0$ System Law, $L_1$ Tool Schemas, $L_2$ Repo Map) followed by mutable $L_3$ history, ensuring $90\%+$ provider KV cache hits. | `agency/context/` |
| **Tree-Sitter Repo-Map** | `packs/code-default/plugins/repo_map.py`: Standalone plugin using Tree-Sitter to extract symbols and dependency graphs, cached by file SHA-256. | `packs/code-default/` |
| **Structured Compactor** | `vanguard/packages/agency/context/compactor.py`: Multi-stage compactor that truncates verbose tool receipts ($>50$ lines) and summarizes past turns when context exceeds 75% capacity. | `agency/context/` |
| **Subagent Spawning** | `vanguard/packages/runtime/delegation.py` (M-6): Attenuated `agent.spawn` capability with separate context stores, reporting summaries back to the parent. | `runtime/` & `kernel/` |
| **Scientific Trajectory Logger** | `vanguard/packages/adapters/stores/event_store.py`: Append-only SQLite WAL recording $D_H, D_R, D_X$, exact prompt/cached/completion tokens, latency ms, and dollar costs per turn. | `adapters/` & `domain/` |

---

## 9. Conclusion & Immediate Execution Directive

Vanguard / AETHER has achieved foundational integrity. The Trust Spine (M-1), Crash Recovery (M-2), Canonical Composition (M-3C), and Runtime Profiles (W-3D) are closed and green.

**The Immediate Directive for the Team:**
1. **Execute M-4 (RF-85):** Run the single preregistered coding run on a clean Linux host with Bubblewrap UID `10001` and Evaluator UID `10002`.
2. **Execute M-5 (RF-86):** Validate the Meta-Framework generality by shipping Domain Pack #2 with zero diffs to the core substrate.
3. **Build the Flagship Packs:** Equip `packs/code-default/` and `packs/researcher/` with MCP tool bridges, Tree-Sitter repo-mapping, prefix cache alignment, and structured context compaction.