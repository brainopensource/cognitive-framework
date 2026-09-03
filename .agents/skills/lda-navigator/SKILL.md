---
name: lda-navigator
description: >-
  Universal Repository Intelligence & Navigation Protocol (LDA).
  Use when exploring the codebase, finding symbols, routing tasks,
  compiling token-budgeted context, checking documentation debt, or locating test falsifiers.
---

# LDA Repository Intelligence & Context Navigation Protocol

This skill equips AI agents with the complete suite of **Repository Intelligence Tools** over CLI (`uv run lda`) and MCP.

---

## 1. When to Use
- **Orientation:** Starting any task in an unfamiliar part of the repository.
- **Pre-implementation:** Compile a bounded context packet or briefing instead of scanning/grepping entire directory trees.
- **Surgical Inspection:** Pin exact AST class/function signatures and inspect upstream callers before changing code.
- **Targeted Falsification:** Discover exact test falsifiers covering modified files.
- **Post-implementation Hygiene:** Detect documentation drift, orphaned docs, and authority conflicts.

---

## 2. Token-Efficient Golden Order (Mandatory Workflow)

1. **Identity & Freshness:** `uv run lda identity --json`
   - Confirms repository HEAD SHA and whether `.lda/index.db` is `FRESH` or `STALE`.
2. **Health Gate:** `uv run lda doctor --json`
   - Confirms `index_healthy: true` and `status: "HEALTHY"`. If unhealthy, run `uv run lda index --json` (or `uv run lda index --rebuild --json` after major branch changes). If degraded, fall back to `python3 tools/docs_rag_v0.py "<task>"` and `rg`.
3. **Compile Bounded Context:** `uv run lda context "<task description or error trace>" --budget 4000 --json`
   - Compiles AST skeletons, authority docs, and test links under a strict token ceiling. Check `token_accounting.omitted_count` to know if higher budget is needed.
   - Stack traces in the task string automatically route directly to specific `file:line` AST frames.
4. **Task Briefing (Optional / Human-Readable):** `uv run lda brief "<task>" --budget 6000`
   - Generates structured Markdown containing documentation obligations, code skeletons, and falsifiers.
5. **Exact Symbol Pinning & Blast Radius:**
   - `uv run lda symbol <SymbolName> --exact`
   - `uv run lda callers <SymbolName>` (upstream callers = blast radius).
6. **Implement & Target-Verify:**
   - Apply surgical patch.
   - `uv run lda tests <touched_files>` to execute only affected falsifiers.
   - `uv run lda drift --json` and `uv run lda consolidate --json` to ensure no documentation debt was left behind.

---

## 3. Retrieval Strategies

- `ppr_submodular` (default): Personalized PageRank graph diffusion + greedy submodular packing — optimal for architectural and graph-connected tasks.
- `hybrid_rrf`: Reciprocal Rank Fusion blending lexical BM25 with graph diffusion — optimal for semantic / paraphrased queries.
- `fts5_bm25`: Pure SQLite FTS5 BM25 lexical baseline — fast and deterministic.

---

## 4. Complete CLI Tool Surface

### 1. Token-Bounded Task Context (`lda context`)
```bash
uv run lda context "<task keywords or error>" --budget 4000
uv run lda context "kernel capability attenuation" --budget 3000 --strategy ppr_submodular --json
```

### 2. Task Briefing (`lda brief`)
```bash
uv run lda brief "Fix admission gate verification" --budget 6000
```

### 3. Precise AST Symbol Lookup (`lda symbol`)
```bash
uv run lda symbol AdmissionGate
uv run lda symbol AdmissionGate --exact
```

### 4. Upstream Callers & Blast Radius (`lda callers`)
```bash
uv run lda callers AdmissionGate.evaluate
```

### 5. Downstream Callees (`lda callees`)
```bash
uv run lda callees AdmissionGate.evaluate
```

### 6. Symbol Usages & References (`lda references`)
```bash
uv run lda references AdmissionGate
```

### 7. Targeted Test Selection (`lda tests`)
```bash
uv run lda tests vanguard/packages/agency/episode/admission_gate.py
```

### 8. Structural Repository Map (`lda repomap`)
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

## 5. MCP Tool & Resource Surface

For agent environments connecting via Model Context Protocol (MCP JSON-RPC):

### MCP Tools
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

## 6. Failure Rules & Fail-Closed Fallbacks

- **HEAD Integrity:** Never trust a context packet whose `provenance.source_head_sha` differs from the current workspace HEAD without recompiling or verifying freshness.
- **Cold Index Fallback:** If `.lda/index.db` is missing or corrupted, run `uv run lda index --json`. If unable to build, fall back immediately to `python3 tools/docs_rag_v0.py "<query>"` and `rg`.
- **Zoom Over Ingestion:** Never ingest whole multi-thousand line files into prompt context when `lda symbol`, `lda callers`, and `lda tests` provide exact AST line references.
