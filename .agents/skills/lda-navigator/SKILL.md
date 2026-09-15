---
name: lda-navigator
description: >-
  Universal Repository Intelligence & Navigation Protocol (LDA).
  Use when exploring the codebase, finding symbols, routing tasks,
  compiling token-budgeted context, checking documentation debt, or locating test falsifiers.
version: "2.0.0"
authority: operational
---

# LDA 2.0 Repository Intelligence & Context Navigation Protocol

**LDA 2.0 (LLM Docs Atlas)** is a thin, deterministic, zero-daemon repository-intelligence and context engine. It transforms codebases into an in-process SQLite-WAL fact graph to compile token-budgeted, provenance-bound context packets, task plans, targeted test falsifiers, and a one-shot repository/task posture for AI agents and human developers.

---

## 1. What is LDA?

LDA provides **structured repository intelligence** across code and documentation without external services or heavy dependencies:
- **Zero Daemon Overhead:** Operates entirely in-process with SQLite-WAL. Consumes **0 MB idle RAM** and **0% background CPU** (zero watcher threads or background daemons).
- **Sub-50ms Delta Indexing:** Incremental AST & markdown re-indexing in **<25 ms** on dirty files (a different measurement from retrieval/`lda plan`). Full planning on this repository is seconds-scale, not sub-50ms.
- **One-Shot Task Bundling:** Compiles symbols, upstream caller graphs (blast radius), canonical doc obligations, and executable test commands in a single ~2-second call.
- **Offline Semantic Intent Resolution:** Pinpoints exact code symbols from natural language intent using BM25, graph in-degree, and architectural tier weighting without external embeddings or network calls.
- **Universal Brownfield Portability:** Zero-configuration discovery across arbitrary Python, TypeScript/JavaScript, Go, Rust, Java, and Kotlin repositories with dynamic doc mapping and relevance-ranked test falsifiers.

---

## 2. Why Use LDA?

| Problem in Standard Agent Workflows | LDA SOTA Solution | Measurable Impact |
|---|---|---|
| **Context Exhaustion:** Grepping and ingesting multi-thousand line files fills context windows quickly. | **Token-Bounded Slicing:** Extracts exact AST line slices and skeletons within strict token limits (e.g. 8000 tokens). | **~80% reduction** in context token consumption |
| **Stale Facts After Edits:** Modifying code makes AST line numbers and symbol references stale unless reindexed. | **Ephemeral Delta Indexing:** Auto-detects dirty git working tree files and syncs AST in milliseconds. | **592x faster** re-indexing (`21ms` vs `12.8s`) |
| **Multi-Roundtrip Discovery:** Agent runs 5+ exploratory commands to find code, callers, tests, and docs. | **One-Shot Task Bundle (`lda plan`):** Bundles target symbols, callers, doc obligations, and tests in 1 step. | **4x-5x fewer** exploratory tool calls |
| **Noisy Test Selection:** Distant benchmark tests crowding out direct unit falsifiers. | **Relevance-Ranked Falsification (`lda tests`):** Direct 1-hop test edges strictly prioritized over benchmark noise. | Exact falsifier ranked **#1** across languages |
| **Repomap Token Waste:** Alphabetical file sorting dumping benchmark fixtures before core modules. | **Centrality-Ranked Skeleton Map (`lda repomap`):** Core production architecture sorted by graph in-degree. | Core packages appear first in **< 1500 tokens** |
| **Brownfield Friction:** Rigid hardcoded docs failing on non-standard repos. | **Dynamic Doc Discovery:** Auto-detects `spec.md`, `README.md`, `ARCHITECTURE.md`, and module docs. | **Zero broken doc links** on any project |

---

## 3. Start with LDA 2.0 posture, then use the "Big 3"

At the start of an implementation, review, or bugfix task, establish the current
subject and select only work that is actually unblocked:

```bash
# Repository posture: HEAD/dirty state, targeted code health, and document health.
uv run lda sweep --json

# Do not ingest all of tasks.md merely to find runnable work.
uv run lda tasks --ready --json
```

`sweep` reports current state; it is not an acceptance receipt and does not replace
the targeted falsifiers for the packet you select. If it is unavailable, use
`uv run lda doctor --json`, then fall back to the deterministic procedures in
section 8.

After posture is known, use the **Big 3** for 90% of development:

To prevent cognitive overload and tool paralysis across 20+ commands, agents should rely on the **Big 3** commands for 90% of development:

1. **`uv run lda plan "<task>"`** (or MCP `lda_plan`): The primary entry point. One-shot bundle providing target symbols, upstream caller blast radius, canonical docs, and relevance-ranked test falsifiers.
2. **`uv run lda resolve "<intent>"`** (or MCP `lda_resolve`): When the symbol name is unknown (e.g., *"how are capability tokens attenuated"*), pinpoints exact classes/functions in < 1.5s.
3. **`uv run lda repomap --budget 2000`** (or MCP `lda_repomap`): When orienting in a new or brownfield repo, renders a high-density, centrality-ranked architectural map of core production code without raw code bloat.

After edits, run **`uv run lda index --delta`** (< 25ms dirty-file AST sync; not a retrieval SLA) to refresh facts before running the falsifiers surfaced in Step 1.

---

## 4. Token-Efficient Golden Order (Mandatory Workflow)

For any task (implementation, review, bugfix), agents MUST follow this sequence:

```text
Step 0: lda sweep --json (New task: establish current repository posture)
    ↓
Step 0b: lda tasks --ready --json (Select a ready task without loading the whole runway)
    ↓
Step 1: lda plan "<task>" (One-shot bundle: symbols + blast radius + docs + test commands)
    ↓
Step 2: Read targeted line ranges only (Never ingest whole files!)
    ↓
Step 3: Implement surgical code changes
    ↓
Step 4: uv run lda index --delta (Instant AST sync for edited files)
    ↓
Step 5: Run targeted test falsifiers surfaced in Step 1, or use
        `lda code-status --task <id> --json` for the packet's changed files
    ↓
Step 6: uv run lda drift --json (Inspect documentation drift; do not mask global
        pre-existing findings as task success)
```

---

## 4.1 Developer Playbook: 4 Core Scenarios

### Scenario 1: Explaining Code & Exploring Concepts (Anti-Blind Grepping)
- **Question:** *"Does Vanguard have an explanation agent or explanation mechanism?"*
- **Why Blind Grepping Fails:** Running `grep -rn "explanation"` returns hundreds of lines across research notes, tests, and documentation, filling your context window with noise.
- **The LDA Solution:**
  ```bash
  uv run lda resolve "explanation agent"
  ```
  In <1 second, LDA uses graph degree and architectural weighting to return the exact symbols:
  - [`vanguard/packages/runtime/explain.py::Explanation`](../../../vanguard/packages/runtime/explain.py#L31) and [`explain_artifact`](../../../vanguard/packages/runtime/explain.py#L54) (normative audit engine for `vg why <artifact>`).
  - [`vanguard/packages/domain/ledger/agent_view.py::AgentView`](../../../vanguard/packages/domain/ledger/agent_view.py#L31) (canonical ledger state projection).
  To inspect the implementation within a token budget:
  ```bash
  uv run lda context "explain artifact" --budget 2500
  ```

### Scenario 2: Finding Modules & Understanding Blast Radius
- **Question:** *"Where is a behavior implemented, and what will break if I change it?"*
- **The LDA Solution:**
  ```bash
  # 1. Structural skeleton of the subsystem
  uv run lda repomap --focus vanguard/packages/runtime/ --budget 2000
  # 2. Who calls this function? (Blast radius)
  uv run lda callers vanguard.packages.runtime.explain.explain_artifact
  # 3. What does this function call? (Dependencies)
  uv run lda callees vanguard.packages.runtime.explain.explain_artifact
  ```

### Scenario 3: Debugging Bugs & Instant Test Falsification
- **Question:** *"I need to fix a bug in admission gate verification. Which tests prove/falsify it?"*
- **The LDA Solution:**
  ```bash
  uv run lda plan "admission gate verification" --budget 4000
  ```
  LDA computes the graph intersection and outputs copy-paste test commands directly:
  ```bash
  python3 -m unittest test.packs.code_default.test_context_policy -v
  ```

### Scenario 4: Creating Features with Zero Documentation Drift
- **Question:** *"I added or modified a port/adapter. How do I guarantee zero stale paths or contracts?"*
- **The LDA Solution:**
  ```bash
  # 1. Plan feature dependencies
  uv run lda plan "sqlite event store adapter"
  # 2. After making surgical changes, sync AST in <30ms:
  uv run lda index --delta
  # 3. Check for documentation drift or broken link contracts:
  uv run lda drift --json
  ```

---

## 5. Retrieval Strategies

- `ppr_submodular` (default): Personalized PageRank graph diffusion + greedy submodular packing — optimal for architectural and graph-connected tasks.
- `hybrid_rrf`: Reciprocal Rank Fusion blending lexical BM25 with graph diffusion — optimal for semantic / paraphrased queries.
- `fts5_bm25`: Pure SQLite FTS5 BM25 lexical baseline — fast and deterministic.

---

## 6. Complete CLI Tool Surface

### 0. LDA 2.0 operational posture and task routing
```bash
uv run lda sweep --json                 # Repository, code, and documentation posture
uv run lda tasks --ready --json         # Unblocked runway tasks
uv run lda tasks --inspect T-141 --json # One task's parsed record
uv run lda code-status --task T-141 --json # Targeted falsifiers/linters for a packet
uv run lda doc-status --json            # Frontmatter, links, and documentation health
```

Use `code-status` only for the packet or files in scope; it is not permission to
run broad discovery or unrelated tests.

### 1. One-Shot Task Bundle (`lda plan`) [SOTA]
```bash
uv run lda plan "<task keywords or intent>" --budget 8000
uv run lda plan "monotonic capability attenuation" --json
```

### 2. Semantic Intent Symbol Resolution (`lda resolve`) [SOTA]
```bash
uv run lda resolve "bubblewrap execution runner"
uv run lda resolve "budget reservation commitment" --top-k 3 --json
```

### 3. Ephemeral Incremental Delta Indexing (`lda index --delta`) [SOTA]
```bash
uv run lda index --delta                  # Auto-detect dirty files (<50ms, 0 MB idle RAM)
uv run lda index --delta path/to/file.py  # Surgical single-file delta
```

### 4. Token-Bounded Task Context (`lda context`)
```bash
uv run lda context "<task keywords or error>" --budget 4000
uv run lda context "kernel capability attenuation" --budget 3000 --strategy ppr_submodular --json
```

### 5. Task Briefing (`lda brief`)
```bash
uv run lda brief "Fix admission gate verification" --budget 6000
```

### 6. Precise AST Symbol Lookup (`lda symbol`)
```bash
uv run lda symbol AdmissionGate
uv run lda symbol AdmissionGate --exact
```

### 7. Upstream Callers & Blast Radius (`lda callers`)
```bash
uv run lda callers AdmissionGate.evaluate
```

### 8. Downstream Callees (`lda callees`)
```bash
uv run lda callees AdmissionGate.evaluate
```

### 9. Symbol Usages & References (`lda references`)
```bash
uv run lda references AdmissionGate
```

### 10. Targeted Test Selection (`lda tests`)
```bash
uv run lda tests vanguard/packages/agency/episode/admission_gate.py
```

### 11. Structural Repository Map (`lda repomap`)
```bash
uv run lda repomap --budget 2000 --json
uv run lda repomap --budget 3000 --focus vanguard/packages/agency/episode/admission_gate.py
```

### 9. Subsystem Topology Map (`lda map`)
```bash
uv run lda map --json
```

### 10. Consolidation & Drift Diagnostics (`lda consolidate` / `lda drift`)
```bash
uv run lda consolidate --json
uv run lda drift --json
```

### 11. Repository Identity, Fact Diff, and Structural Metrics
```bash
uv run lda identity --json
uv run lda diff [--since <sha>] --json
uv run lda metrics --json
```

### 12. Retrieval Benchmark (`lda bench`)
```bash
uv run lda bench --budget 2000 --k 5 --json
```

### 13. Health & Index Diagnostics (`lda doctor` / `lda check`)
```bash
uv run lda doctor --json
uv run lda check --json
```

### 14. Document Inspection (`lda inspect`)
```bash
uv run lda inspect AGENTS.md --json
```

### 15. Standardizer (`lda standardize`)
```bash
uv run lda standardize vanguard/packages/agency/episode/admission_gate.py
```

### 16. Indexing & Rebuild (`lda index`)
```bash
uv run lda index --json           # Incremental update
uv run lda index --rebuild --json # Fresh rebuild
```

---

## 7. MCP Tool & Resource Surface

For agent environments connecting via Model Context Protocol (MCP JSON-RPC):

### MCP Tools
- `lda_sweep`: Master one-shot execution combining repo-status, code-status, and doc-status in <2.5s (`{"budget": 4000}`).
- `lda_repo_status`: Fast C-git status, HEAD SHA, branch, dirty diffstat (<25ms).
- `lda_code_status`: Auto-runs falsifiers for touched files via test-runner skill, plus linters (<2s) (`{"task_id": "...", "target_files": [...]}`).
- `lda_tasks`: AST/regex runway query over tasks.md by ID, owner, or unblocked status (`{"ready_only": true, "owner": "..."}`).
- `lda_plan`: Compile one-shot task bundle with symbols, callers, falsifiers, doc obligations, and context (`{"query": "...", "budget": 8000}`).
- `lda_resolve`: Semantic intent symbol resolution without exact names (`{"query": "...", "top_k": 5}`).
- `lda_delta`: Ephemeral incremental delta re-indexing (`{"files": ["..."]}`).
- `lda_context`: Compile token-bounded context packet (`{"query": "...", "budget": 4000}`).
- `lda_brief`: Structured Markdown task briefing (`{"task": "...", "budget": 6000}`).
- `lda_symbol`: Exact AST symbol lookup (`{"symbol_name": "..."}`).
- `lda_callers`: Upstream caller graph lookup (`{"symbol_id": "..."}`).
- `lda_callees`: Downstream callee graph lookup (`{"symbol_id": "..."}`).
- `lda_references`: Cross-references and imports (`{"symbol_id": "..."}`).
- `lda_focused_tests`: Test falsifiers for touched files (`{"touched_files": ["..."]}`).
- `lda_repomap`: Dense structural skeleton map (`{"budget": 2000}`).
- `lda_map`: Subsystem architecture summary.
- `lda_doctor`: Index health and database diagnostics.
- `lda_check`: Fast integrity check.
- `lda_coverage`: Language and relation coverage breakdown.
- `lda_fts_search`: Raw BM25 lexical query.
- `lda_drift`: Documentation drift report.
- `lda_consolidate`: Duplicate docs and authority conflict detector.

### MCP Resources & Prompts
- **Resources:** `lda://map` (topology summary), `lda://docs/{id}` (canonical document content).
- **Prompts:** `lda_task_briefing`, `lda_repo_orientation`.

---

## 8. Failure Rules & Operational Invariants

- **HEAD Integrity:** Never trust a context packet whose `provenance.source_head_sha` differs from the current workspace HEAD without recompiling or verifying freshness.
- **Cold Index Fallback:** If `.lda/index.db` is missing or corrupted, run `uv run lda index --json`. If unable to build, fall back immediately to `python3 tools/docs_rag_v0.py "<query>"` and `rg`.
- **Zoom Over Ingestion:** Never ingest whole multi-thousand line files into prompt context when `lda symbol`, `lda callers`, and `lda tests` provide exact AST line references.
- **Indexes Route, Documents Constrain, Tests Falsify:** Generated indexes are projections and never override normative specifications or code tests.
