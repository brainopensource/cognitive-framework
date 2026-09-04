---
name: lda-navigator
description: >-
  Universal Repository Intelligence & Navigation Protocol (LDA).
  Use when exploring the codebase, finding symbols, routing tasks,
  compiling token-budgeted context, checking documentation debt, or locating test falsifiers.
---

# LDA Repository Intelligence & Context Navigation Protocol

**LDA (LLM Docs Atlas)** is a thin, deterministic, zero-daemon repository-intelligence and context engine. It transforms codebases into an in-process SQLite-WAL fact graph to compile token-budgeted, provenance-bound context packets, task plans, and targeted test falsifiers for AI agents and human developers.

---

## 1. What is LDA?

LDA provides **structured repository intelligence** across code and documentation without external services or heavy dependencies:
- **Zero Daemon Overhead:** Operates entirely in-process with SQLite-WAL. Consumes **0 MB idle RAM** and **0% background CPU** (zero watcher threads or background daemons).
- **Sub-50ms Delta Indexing:** Incremental AST & markdown re-indexing in **<25 ms**, replacing 12+ second full rebuilds.
- **One-Shot Task Bundling:** Compiles symbols, upstream caller graphs (blast radius), canonical doc obligations, and executable test commands in a single ~2-second call.
- **Offline Semantic Intent Resolution:** Pinpoints exact code symbols from natural language intent using BM25, graph in-degree, and architectural tier weighting without external embeddings or network calls.

---

## 2. Why Use LDA?

| Problem in Standard Agent Workflows | LDA SOTA Solution | Measurable Impact |
|---|---|---|
| **Context Exhaustion:** Grepping and ingesting multi-thousand line files fills context windows quickly. | **Token-Bounded Slicing:** Extracts exact AST line slices and skeletons within strict token limits (e.g. 8000 tokens). | **~80% reduction** in context token consumption |
| **Stale Facts After Edits:** Modifying code makes AST line numbers and symbol references stale unless reindexed. | **Ephemeral Delta Indexing:** Auto-detects dirty git working tree files and syncs AST in milliseconds. | **592x faster** re-indexing (`21ms` vs `12.8s`) |
| **Multi-Roundtrip Discovery:** Agent runs 5+ exploratory commands to find code, callers, tests, and docs. | **One-Shot Task Bundle (`lda plan`):** Bundles target symbols, callers, doc obligations, and tests in 1 step. | **4x-5x fewer** exploratory tool calls |
| **Unknown Symbol Names:** Agent doesn't know exact function name (e.g., "how capabilities are attenuated"). | **Intent Resolution (`lda resolve`):** Ranks symbols using multi-field tokens, in-degree, and authority tiers. | High precision without external API keys |
| **Missing Test Falsifiers:** Guessing which unit tests cover a specific function or file. | **Targeted Falsification (`lda tests`):** Direct indexed SQL join linking touched symbols to test suites. | Tests found in **<3ms** with copy-paste commands |

---

## 3. When to Use What

| Development Phase | Question / Need | Recommended Command / Tool |
|---|---|---|
| **Starting a Task** | "What files, symbols, docs, and tests are relevant to this task?" | `uv run lda plan "<task description>"` |
| **Concept Exploration** | "Where is this feature or behavior implemented if I don't know the symbol name?" | `uv run lda resolve "<natural language intent>"` |
| **After Modifying Code** | "How do I refresh the symbol graph for files I just modified?" | `uv run lda index --delta` |
| **Verifying Changes** | "Which exact tests falsify or verify my touched files?" | Output of `lda plan` or `uv run lda tests <files>` |
| **Checking Documentation Debt** | "Did my changes leave documentation, links, or contracts stale?" | `uv run lda drift --json` and `uv run lda diff --json` |
| **Diagnosing Index State** | "Is the SQLite fact graph healthy and bound to current git HEAD?" | `uv run lda doctor` and `uv run lda identity` |

---

## 4. Token-Efficient Golden Order (Mandatory Workflow)

For any task (implementation, review, bugfix), agents MUST follow this sequence:

```text
Step 1: lda plan "<task>" (One-shot bundle: symbols + blast radius + docs + test commands)
    ↓
Step 2: Read targeted line ranges only (Never ingest whole files!)
    ↓
Step 3: Implement surgical code changes
    ↓
Step 4: uv run lda index --delta (Instant AST sync for edited files)
    ↓
Step 5: Run targeted test falsifiers surfaced in Step 1
    ↓
Step 6: uv run lda drift --json (Verify zero doc drift or orphan contracts)
```

---

## 5. Retrieval Strategies

- `ppr_submodular` (default): Personalized PageRank graph diffusion + greedy submodular packing — optimal for architectural and graph-connected tasks.
- `hybrid_rrf`: Reciprocal Rank Fusion blending lexical BM25 with graph diffusion — optimal for semantic / paraphrased queries.
- `fts5_bm25`: Pure SQLite FTS5 BM25 lexical baseline — fast and deterministic.

---

## 6. Complete CLI Tool Surface

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
