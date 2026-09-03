---
id: skill-lda-docs-atlas
class: how-to
authority: descriptive
canonical_for:
  - lda-operational-atlas
  - lda-technical-guide
status: living
owner: repository-governance
version: "1.1.0"
last_verified: 2026-09-03
---

# LDA Navigator — Complete Technical Atlas & Operational Guide

> **Canonical Skill Definition & Location**
>
> The sole, authoritative AI agent skill definition for repository intelligence is:
> 👉 [`.agents/skills/lda-navigator/SKILL.md`](../../.agents/skills/lda-navigator/SKILL.md)
>
> There are no duplicate skills, secondary shims, or legacy aliases. All agent invocations and human workflows bind exclusively to this single specification.

> **Executive Briefing & Core Protocol**
>
> LDA (Local Documentation Atlas / Universal Repository Intelligence Engine) is an offline, AST-aware, token-bounded fact graph engine built on SQLite + FTS5. It eliminates context-window exhaustion and signature hallucinations by compiling deterministic, submodular-optimized context packets under strict token budgets.
>
> **The 6-Step Golden Order (Strict Execution):**
> 1. **Identity & Freshness:** `uv run lda identity --json` (verify HEAD binding).
> 2. **Health Verification:** `uv run lda doctor --json` (fail-closed: confirm `index_healthy: true`).
> 3. **Context Compilation:** `uv run lda context "<task description>" --budget 4000 --json`
> 4. **Symbol Pinning:** `uv run lda symbol <SymbolName> --exact`
> 5. **Blast Radius Analysis:** `uv run lda callers <SymbolName>`
> 6. **Targeted Falsification:** `uv run lda tests <modified_file>`

---

## Navigation & Chapter Index

- [Chapter 1: The Problem Space & Cost Models (Why LDA Exists)](#chapter-1-the-problem-space--cost-models-why-lda-exists)
- [Chapter 2: Theoretical Foundations & Mathematical Formulations](#chapter-2-theoretical-foundations--mathematical-formulations)
- [Chapter 3: System Architecture & The 6-Layer Pipeline](#chapter-3-system-architecture--the-6-layer-pipeline)
- [Chapter 4: The Fact Graph Relational Model & Storage Schema](#chapter-4-the-fact-graph-relational-model--storage-schema)
- [Chapter 5: Retrieval & Graph Diffusion Algorithms](#chapter-5-retrieval--graph-diffusion-algorithms)
- [Chapter 6: Token Economy, Representation Degradation & Budget Algebra](#chapter-6-token-economy-representation-degradation--budget-algebra)
- [Chapter 7: Comparative Analysis — Using vs. Not Using LDA](#chapter-7-comparative-analysis--using-vs-not-using-lda)
- [Chapter 8: Complete CLI & MCP Operational Manual](#chapter-8-complete-cli--mcp-operational-manual)
- [Chapter 9: Verified Autonomous Agent Workflows & Coding Recipes](#chapter-9-verified-autonomous-agent-workflows--coding-recipes)
- [Chapter 10: Empirical Benchmarks & Performance Metrics](#chapter-10-empirical-benchmarks--performance-metrics)
- [Chapter 11: Drift Detection, Consolidation & Knowledge Hygiene](#chapter-11-drift-detection-consolidation--knowledge-hygiene)
- [Chapter 12: Epistemic Confidence Tiers & Authority Vectors](#chapter-12-epistemic-confidence-tiers--authority-vectors)
- [Chapter 13: Architectural Roadmap & Engineering Extensibility for Senior/PhD Contributors](#chapter-13-architectural-roadmap--engineering-extensibility-for-seniorphd-contributors)

---

## Chapter 1: The Problem Space & Cost Models (Why LDA Exists)

### 1.1 The Context Window Tax in Autonomous Agentic Loops
When an LLM coding agent navigates a large software repository (>1,000 files) without indexing, it relies on primitive filesystem traversals (`find`, `rg`, `cat`). This introduces three catastrophic inefficiencies:

1. **Context Window Flooding (Noise Amplification):** A naive retrieval loading entire 1,500-line source files burns 20,000–50,000 tokens of the context window per turn. Attention degradation (the "needle-in-a-haystack" loss in deep transformer layers) leads to lost instructions and degraded reasoning.
2. **Signature & Path Hallucination:** Without an AST ground-truth index, agents reconstruct parameter names, types, and module imports from memory or vague fuzzy matches, generating syntactically valid but non-existent interfaces.
3. **Unseen Regression Blast Radius:** When modifying an internal function, an agent has no causal awareness of transitive callers across packages or test suites, causing downstream regressions.

### 1.2 Quantitative Cost Model: Naive vs. LDA Indexed
Let $C_{\text{turn}}$ be token cost per turn, $T_{\text{read}}$ be raw source token volume, and $B$ be declared budget.

$$\text{Efficiency} = \frac{\text{Tokens Used for High-Signal Reasoning}}{\text{Total Tokens Ingested}}$$

- **Naive Agent:** Ingests raw files (~40,000 tokens) to inspect a single 20-line method. Efficiency: < 10%.
- **LDA Agent:** Sets bounded budget $B \le 4000$ tokens via [`.agents/skills/lda-navigator/SKILL.md`](../../.agents/skills/lda-navigator/SKILL.md). LDA selects exact AST skeletons, authority docs, and test links. Efficiency: > 85%.
- **Result:** 7x to 10x reduction in token burn, with latency dropping from 15s filesystem regex scans to < 5ms indexed SQLite queries.

---

## Chapter 2: Theoretical Foundations & Mathematical Formulations

LDA merges information retrieval (IR), spectral graph theory, and combinatorial submodular optimization into a unified engine.

### 2.1 Lexical Baseline: BM25 (Robertson & Zaragoza, 2009)
Lexical search operates over an inverted index powered by SQLite FTS5. For query $q = (q_1, \dots, q_n)$ and document/entity $d$:

$$\text{BM25}(q, d) = \sum_{i=1}^n \text{IDF}(q_i) \cdot \frac{f(q_i, d) \cdot (k_1 + 1)}{f(q_i, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}$$

Where:
- $f(q_i, d)$ is the term frequency of token $q_i$ in entity record $d$.
- $|d|$ is entity length in tokens, and $\text{avgdl}$ is average entity token length across corpus.
- $k_1 = 1.2$ (term saturation ceiling), $b = 0.75$ (document length penalization).
- Inverse Document Frequency:
  $$\text{IDF}(q_i) = \ln \left( \frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1 \right)$$

### 2.2 Spectral Graph Diffusion: Personalized PageRank (PPR)
BM25 captures lexical overlap but fails on conceptual dependencies where terms differ (e.g. `attenuation` vs `StandardPolicy`). LDA constructs a directed multigraph $G = (V, E)$ where $V$ are code/doc entities and $E$ are typed relationships (`calls`, `imports`, `tests`, `documents`).

Let $A$ be the adjacency matrix, and $\hat{A} = D^{-1}A$ be the row-stochastic transition probability matrix (where $D_{ii} = \sum_j A_{ij}$).
Let $\mathbf{s} \in \mathbb{R}^{|V|}$ be the personalization seed vector defined by normalized top-k BM25 relevance scores.
The stationary Personalized PageRank vector $\mathbf{p}$ satisfies the diffusion recurrence:

$$\mathbf{p} = (1 - \alpha) \hat{A}^T \mathbf{p} + \alpha \mathbf{s}$$

Where:
- $\alpha \in (0, 1)$ is the teleportation/restart probability (default $\alpha = 0.15$).
- Iterative convergence is achieved via power iteration:
  $$\mathbf{p}^{(t+1)} = (1 - \alpha) \hat{A}^T \mathbf{p}^{(t)} + \alpha \mathbf{s}$$
  converging in 3 to 5 iterations over sparse matrices to $\| \mathbf{p}^{(t+1)} - \mathbf{p}^{(t)} \|_1 < \epsilon$.

### 2.3 Combinatorial Packing: Submodular Optimization
Given a candidate universe $\mathcal{U}$ of retrieved entities and documentation blocks, packing them into token budget $B$ is a Budgeted Maximum Coverage problem. Let $c(i)$ be the token cost of entity $i$. We define the set function $f: 2^{\mathcal{U}} \to \mathbb{R}_{\ge 0}$:

$$f(S) = \sum_{i \in S} \text{score}(i) - \lambda \sum_{i, j \in S, i \ne j} \text{Sim}(i, j)$$

$f(S)$ is **submodular**, satisfying diminishing marginal returns:

$$f(S \cup \{i\}) - f(S) \le f(T \cup \{i\}) - f(T) \quad \forall T \subseteq S \subseteq \mathcal{U}, \; i \notin S$$

LDA utilizes the Nemhauser-Wolsey greedy approximation algorithm with a guaranteed $(1 - 1/e) \approx 63.2\%$ approximation ratio:

$$i^* = \arg\max_{i \in \mathcal{U} \setminus S, \; c(S \cup \{i\}) \le B} \frac{f(S \cup \{i\}) - f(S)}{c(i)}$$

### 2.4 Hybrid Reciprocal Rank Fusion (RRF)
When both BM25 rank $R_{\text{lex}}(d)$ and PPR diffusion rank $R_{\text{graph}}(d)$ are computed, the alternative `--strategy hybrid_rrf` blends them without requiring score calibration:

$$\text{RRF}(d) = \sum_{m \in \{\text{lex}, \text{graph}\}} \frac{1}{k + R_m(d)}$$

Where $k = 60$ acts as a dampening factor against outlier rank positions.

### 2.5 Epistemic Authority Weighting
Every document entity possesses an authoritative class weight $\mathbf{W}_{\text{auth}}(d)$ reflecting its normative governance priority:

$$\text{FinalScore}(d) = \text{PPR}(d) \times \mathbf{W}_{\text{auth}}(d) \times \mathbf{C}_{\text{PageRank}}(d)$$

- **Normative Law** (`docs/SPEC.md`, `AGENTS.md`): $\mathbf{W} = 1.50$
- **System Architecture** (`docs/architecture/`, `docs/backend/`): $\mathbf{W} = 1.30$
- **Execution Runway** (`docs/execution/tasks.md`): $\mathbf{W} = 1.20$
- **Descriptive Documentation** (`docs/onboarding/`, guides): $\mathbf{W} = 1.00$
- **Non-Canonical Research / Scratchpads**: $\mathbf{W} = 0.50$

---

## Chapter 3: System Architecture & The 6-Layer Pipeline

```text
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ L5: Human Interface & CLI Surface (lda serve, lda map, lda brief, PR digests)        │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ L4: Agent Orchestration Layer (.agents/skills/lda-navigator/SKILL.md, Budgets, Debt)  │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ L3: Context Compilation Engine (Submodular Packing, Representation Degradation Ladder)│
├───────────────────────────────────────────────────────────────────────────────────────┤
│ L2: Multi-Modal Retrieval (SQLite FTS5 BM25, PPR Power Iteration, RRF Rank Fusion)   │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ L1: Relational Fact Graph (SQLite WAL, Incremental SHA-256 Hashes, Caller/Callee Joins│
├───────────────────────────────────────────────────────────────────────────────────────┤
│ L0: Extractor & Parser Tier (Tree-sitter AST, Python ast, DocSection Heading Splitter)│
└───────────────────────────────────────────────────────────────────────────────────────┘
```

1. **L0 Extractor Tier:** Uses Tree-sitter and Python standard library `ast` to parse grammar trees across 11+ languages into canonical Intermediate Representation (`IRSymbol`, `IRDocument`, `IRRelation`).
2. **L1 Relational Fact Graph:** Stores nodes and edges in SQLite (`.lda/index.db`) using WAL mode, enabling concurrent sub-millisecond lookups.
3. **L2 Retrieval Engine:** Executes BM25 lexical queries followed by graph walks across relation edges.
4. **L3 Compilation Engine:** Downscales AST bodies to skeleton/signature stubs to satisfy strict integer token budgets.
5. **L4 Agent Interface:** Emits structured JSON payloads defined by the single skill [`.agents/skills/lda-navigator/SKILL.md`](../../.agents/skills/lda-navigator/SKILL.md).
6. **L5 Surface:** Exposes human-readable summaries and visual topologies.

---

## Chapter 4: The Fact Graph Relational Model & Storage Schema

The property graph is backed by a normalized schema in `.lda/index.db`:

### 4.1 Schema DDL
```sql
CREATE TABLE entities (
    id TEXT PRIMARY KEY,             -- Stable content-addressed hash: sym:<sha256[:16]>
    kind TEXT NOT NULL,              -- class, method, function, interface, document, doc_section
    name TEXT NOT NULL,              -- Short identifier
    qualified_name TEXT NOT NULL,   -- Fully qualified symbol path
    file_path TEXT NOT NULL,         -- Relative repository path
    start_line INTEGER NOT NULL,     -- 1-indexed start line
    end_line INTEGER NOT NULL,       -- 1-indexed end line
    language TEXT NOT NULL,          -- python, typescript, markdown, etc.
    confidence_tier INTEGER NOT NULL,-- Epistemic tier (40..100)
    docstring TEXT,                  -- Extracted docstring
    signature TEXT,                  -- Reconstructed AST signature
    content_hash TEXT NOT NULL       -- SHA-256 hash of entity content for incremental freshness
);

CREATE TABLE relations (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES entities(id),
    target_id TEXT NOT NULL REFERENCES entities(id),
    kind TEXT NOT NULL,              -- calls, imports, tests, documents, inherits, defines
    location_json TEXT,              -- Call site file and line references
    confidence_tier INTEGER NOT NULL
);

CREATE VIRTUAL TABLE fts_entities USING fts5 (
    name, qualified_name, docstring, signature, content=entities
);
```

### 4.2 Measured Repository Scale (Live Graph Statistics)
- **Total Indexed Files:** 3,420
- **Total Indexed Symbols:** 10,611
- **Total Relational Edges:** 77,719
  - `calls`: 54,317
  - `tests`: 9,047
  - `imports`: 7,685
  - `inherits`: 1,125
  - `defines`: 5,545
- **Documents Indexed:** 286
- **Languages:** Python (9,306 symbols), TypeScript (1,235 symbols), Bash, Rust, JSON, YAML, TOML, Markdown.
- **Import Cycles:** 0 (clean topological hierarchy).

---

## Chapter 5: Retrieval & Graph Diffusion Algorithms

### 5.1 The Standard Query Algorithm (`ppr_submodular`)
When an agent invokes `lda context "<task>" --budget 4000`:
1. **Query Parse & Tokenization:** Task string is decomposed into lexical tokens; any regex matching file:line patterns (e.g. `vanguard/packages/kernel/policy.py:82`) is pinned as a high-priority root node.
2. **BM25 Seeding:** FTS5 generates top $K=50$ seed candidates.
3. **Graph Traversal:** 3-hop power iteration propagates relevance through `calls`, `tests`, and `documents` edges.
4. **Authority Modulation:** Scores are weighted by authority level.
5. **Greedy Submodular Packing:** Selects symbols, doc sections, and test falsifiers until the token budget is reached.

---

## Chapter 6: Token Economy, Representation Degradation & Budget Algebra

### 6.1 The Graceful Degradation Ladder
To maximize signal within a tight token budget, LDA degrades code representations through discrete AST tiers:

$$\text{FULL} \xrightarrow{\text{budget pressure}} \text{SKELETON} \xrightarrow{} \text{SIGNATURE} \xrightarrow{} \text{SUMMARY} \xrightarrow{} \text{REFERENCE}$$

- **FULL:** Complete source code (only for small, critical target functions).
- **SKELETON:** AST skeleton containing class header, docstring, and method stubs (`def method(self, x: int) -> bool: ...`).
- **SIGNATURE:** Single-line signature.
- **SUMMARY:** Name and docstring only.
- **REFERENCE:** File path and line range locator (`path/to/file.py#L40-L90`).

### 6.2 Hard Invariant Assertion
$$\sum_{i \in \text{Packet}} \text{TokenCost}(i) \le \text{Budget}_{\text{declared}}$$
LDA validates token consumption before serialization. If an item exceeds remaining budget, it is shifted down the degradation ladder or omitted, with `omitted_count` logged in telemetry.

---

## Chapter 7: Comparative Analysis — Using vs. Not Using LDA

| Capability / Metric | Without LDA (Manual / Grep / Cat) | With LDA Single Skill Protocol |
|---|---|---|
| **Context Window Overhead** | Dumps 10,000–50,000 raw lines; blows token limits | Guaranteed bounded token packet (e.g., 2,000–4,000 tokens) |
| **AST Signature Truth** | Hallucinated or guessed from memory | Ground-truth AST extract from SQLite (`kind`, `signature`, lines) |
| **Blast Radius Detection** | Blind trial and error; accidental test breakage | Immediate graph traversal: upstream `callers`, downstream `callees` |
| **Test Execution Loop** | Must run entire test suite (slow) or guess tests | Derives exact minimal test falsifiers for touched files in <50ms |
| **Speed & Cost** | Minutes of scraping, high LLM API cost | Sub-millisecond SQLite queries, zero LLM API cost |
| **Documentation Debt** | Docs drift and become stale silently | `lda drift` and `lda consolidate` catch orphaned/stale documents |

---

## Chapter 8: Complete CLI & MCP Operational Manual

The complete operational surface is defined in [`.agents/skills/lda-navigator/SKILL.md`](../../.agents/skills/lda-navigator/SKILL.md).

### 8.1 Diagnostic & Health Commands
- `uv run lda doctor --json`: Comprehensive index health check (SQLite integrity, HEAD freshness, orphan FTS rows).
- `uv run lda check --json`: Fast integrity check of active catalog, entity counts, and profiles.
- `uv run lda identity --json`: Repository snapshot: git commit SHA, dirty status, index freshness vs HEAD (`FRESH` vs `STALE`).

### 8.2 Retrieval & Context Commands
- `uv run lda context "<task>" --budget <N> [--strategy ppr_submodular|hybrid_rrf|fts5_bm25] [--json]`: Primary agent tool for token-bounded context packet compilation.
- `uv run lda brief "<task>" --budget <N>`: Formatted Markdown task briefing for humans and agents.
- `uv run lda query "<term>"`: Low-level lexical and entity lookup.

### 8.3 AST Symbol & Graph Navigation Commands
- `uv run lda symbol <Name> [--exact]`: AST symbol lookup with signature, docstring, line range, and confidence tier.
- `uv run lda callers <Symbol>`: Upstream callers graph traversal (evaluates blast radius).
- `uv run lda callees <Symbol>`: Downstream callees graph traversal.
- `uv run lda references <Symbol>`: All cross-repository usages, imports, and references.
- `uv run lda tests <file_path>`: Targeted test selection; outputs exact unittest commands for the specified file.

### 8.4 Structural Architecture Commands
- `uv run lda repomap --budget <N> [--focus <path>]`: PageRank-weighted structural repository overview.
- `uv run lda map --json`: Repository topology breakdown by language, entity kinds, and relation kinds.
- `uv run lda metrics --json`: Fan-in/fan-out hub analysis, import cycle detection, and hot file rankings.

### 8.5 Knowledge Hygiene & Index Maintenance Commands
- `uv run lda consolidate --json`: Detects duplicate documentation files and authority conflicts.
- `uv run lda drift --json`: Detects documentation drift: stale paths, undocumented symbols, and orphan docs.
- `uv run lda diff [--since <sha>] --json`: Fact-level diff between workspace and index.
- `uv run lda inspect <path> --json`: Metadata, authority class, and token estimates for a specific file.
- `uv run lda standardize <file>`: Inspects symbols extracted from a file by the standardizer.
- `uv run lda bench --budget <N> --k <K> --json`: Executes deterministic retrieval quality benchmarks (Recall@k, MRR, latency).
- `uv run lda index [--rebuild] [--json]`: Incremental or full index regeneration.

### 8.6 MCP Protocol Interface (JSON-RPC)
When interacting via Model Context Protocol:
- **Tools:** `lda_context`, `lda_brief`, `lda_symbol`, `lda_callers`, `lda_callees`, `lda_references`, `lda_focused_tests`, `lda_repomap`, `lda_map`, `lda_doctor`, `lda_check`, `lda_coverage`, `lda_drift`, `lda_consolidate`.
- **Resources:** `lda://map`, `lda://docs/{id}`.
- **Prompts:** `lda_task_briefing`, `lda_repo_orientation`.

---

## Chapter 9: Verified Autonomous Agent Workflows & Coding Recipes

### Recipe 1: Surgical Bug Fix (Blast-Radius Contained)
```bash
# Step 0: Confirm index integrity
uv run lda doctor --json

# Step 1: Acquire token-bounded context
uv run lda context "fix crash in kernel policy authorization" --budget 3000

# Step 2: Pin target symbol and verify exact parameters
uv run lda symbol StandardPolicy.authorize --exact

# Step 3: Check upstream callers to assess blast radius
uv run lda callers StandardPolicy.authorize

# Step 4: Apply code edit to vanguard/packages/kernel/policy.py

# Step 5: Execute targeted test falsifiers derived by LDA
uv run lda tests vanguard/packages/kernel/policy.py
python3 -m unittest test.kernel.test_attenuation -v
```

### Recipe 2: Feature Extension & Architecture Onboarding
```bash
# Step 1: Survey structural topology of target module
uv run lda repomap --budget 2500 --focus vanguard/packages/agency/episode/engine.py

# Step 2: Pin interface contract
uv run lda symbol EpisodeEngine --exact

# Step 3: Implement feature extension

# Step 4: Validate documentation debt obligations
uv run lda context "extend EpisodeEngine spawn lifecycle" --budget 2000
# Update canonical owner docs indicated in packet obligations
```

---

## Chapter 10: Empirical Benchmarks & Performance Metrics

From live executions on this repository (3,420 files, 10,611 symbols, 77,719 relations):

### 10.1 Latency & Retrieval Benchmarks
- **Mean Retrieval Latency (PPR Submodular):** $2.98\text{ ms}$
- **Mean Retrieval Latency (BM25):** $3.07\text{ ms}$
- **Recall@5:** $1.00$ (100% precision within top 5 candidates)
- **Mean Reciprocal Rank (MRR):** $0.67$ (target entity ranks on average at position 1.5)
- **Direct AST Symbol Lookup:** $< 5\text{ ms}$
- **Call-Graph Traversal (`lda callers` over 54k edges):** $< 5\text{ ms}$

---

## Chapter 11: Drift Detection, Consolidation & Knowledge Hygiene

LDA serves as a continuous linter for repository documentation:

1. **Stale Path Detection:** Identifies markdown files referencing code paths that no longer exist on disk.
2. **Undocumented Symbol Flagging:** Identifies public classes/functions that lack documentation edges in the graph.
3. **Duplicate Content Detection:** Uses n-gram Jaccard similarity to identify redundant documentation pairs, preventing documentation sprawl.

---

## Chapter 12: Epistemic Confidence Tiers & Authority Vectors

LDA tags every entity and relation with an epistemic confidence score:

| Confidence Tier | Level | Source Extractor | Epistemic Trust |
|---|---|---|---|
| `COMPILER` | 100 | Bytecode compiler / type-checker | Absolute ground-truth |
| `SCIP` | 90 | Semantic Code Intelligence Protocol | Full type-resolution |
| `TREE_SITTER` | 80 | Tree-sitter concrete syntax grammar | Syntactically verified AST |
| `AST_GREP` | 70 | Python stdlib `ast` parser | Language-specific syntax tree |
| `STRUCTURED_DOC` | 60 | Structured markdown heading parser | Formatted text representation |
| `HEURISTIC` | 40 | Regex / pattern matching / git history | Fallback approximation |

---

## Chapter 13: Architectural Roadmap & Engineering Extensibility for Senior/PhD Contributors

For senior engineers extending LDA:
1. **Decouple Repository Profiles:** Move repository-specific rules from Python modules to declarative `lda.profile.yaml` configurations.
2. **Dense Semantic Channel:** Integrate an optional local ONNX embedding model (e.g. `bge-small-en-v1.5`) to blend cosine semantic distance with lexical BM25.
3. **Incremental Graph Diffusion:** Rather than re-running PPR over the entire graph, maintain dynamic localized diffusion updates over changed subgraphs.
4. **SCIP Integration:** Upgrade TypeScript/Python extractors to SCIP to support precise cross-package jump-to-definition at confidence tier 90.
