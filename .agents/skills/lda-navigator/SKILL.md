---
name: lda-navigator
description: >-
  Universal Repository Intelligence & Navigation Protocol.
  Use when exploring the codebase, finding symbols, routing tasks,
  checking documentation debt obligations, or locating test falsifiers.
---

# LDA Repository Intelligence & Context Navigation Protocol

This skill equips AI agents with the complete suite of **Repository Intelligence Tools** over CLI and MCP.

## Complete LDA Tool Surface

### 1. Token-Bounded Task Context (`lda_context`)
Compile high-signal context packets containing canonical docs, symbols, tests, and documentation debt obligations under a strict token budget:
```bash
# CLI execution
python3 tools/docs_rag_v0.py "<task keywords or error>" --budget 4000
```
```json
// MCP JSON-RPC execution
{"method": "tools/call", "params": {"name": "lda_context", "arguments": {"query": "kernel dispatch", "budget": 4000}}}
```

### 2. Precise AST Symbol Lookup (`lda_symbol`)
Lookup exact class/function signatures, docstrings, and line ranges:
```json
{"method": "tools/call", "params": {"name": "lda_symbol", "arguments": {"symbol_name": "Kernel"}}}
```

### 3. Upstream Callers & Impact Graph (`lda_callers`)
Discover which functions call a specific method to prevent regressions:
```json
{"method": "tools/call", "params": {"name": "lda_callers", "arguments": {"symbol_id": "Kernel.dispatch"}}}
```

### 4. Downstream Callees (`lda_callees`)
Discover what functions are called by a target method:
```json
{"method": "tools/call", "params": {"name": "lda_callees", "arguments": {"symbol_id": "EpisodeEngine.step"}}}
```

### 5. Symbol Usages & References (`lda_references`)
Find all occurrences and cross-references across the repository:
```json
{"method": "tools/call", "params": {"name": "lda_references", "arguments": {"symbol_id": "AdmissionGate"}}}
```

### 6. Executable Tests for Symbol (`lda_tests_for_symbol`)
Find all unit test cases that cover and verify a given symbol:
```json
{"method": "tools/call", "params": {"name": "lda_tests_for_symbol", "arguments": {"symbol_id": "BudgetGovernor"}}}
```

### 7. Documentation Sections for Symbol (`lda_docs_for_symbol`)
Retrieve exact canonical markdown sections specifying the behavior of a symbol:
```json
{"method": "tools/call", "params": {"name": "lda_docs_for_symbol", "arguments": {"symbol_id": "Attenuator"}}}
```

### 8. Full-Text BM25 Search (`lda_fts_search`)
Perform fast BM25 lexical search across all AST entities, doc sections, and symbols:
```json
{"method": "tools/call", "params": {"name": "lda_fts_search", "arguments": {"query": "admission gate verification", "limit": 10}}}
```

### 9. Subsystem Topology Map (`lda_map`)
View the high-level hexagonal architecture boundaries, module paths, and logical LOC counts:
```json
{"method": "tools/call", "params": {"name": "lda_map", "arguments": {}}}
```

### 10. Health & Index Stats (`lda_doctor` / `lda_check` / `lda_coverage`)
Assert SQLite database health, entity counts, per-language coverage, HEAD binding, and hygiene:
```json
{"method": "tools/call", "params": {"name": "lda_doctor", "arguments": {}}}
{"method": "tools/call", "params": {"name": "lda_check", "arguments": {}}}
{"method": "tools/call", "params": {"name": "lda_coverage", "arguments": {}}}
```
```bash
# CLI equivalents
uv run lda doctor --json      # health + coverage + HEAD + profile
uv run lda check --json       # full SOTA diagnostics (profile/KB/graph/hygiene/freshness)
```

### 11. Standardizer / Ruler (`lda standardize`)
Inspect a single file — detected language, canonical symbol kinds, and import edges — before editing code you must not guess at:
```bash
uv run lda standardize src/frontend/component.ts      # TS symbols/imports
uv run lda standardize vanguard/packages/kernel/budget.py
```

### 12. Rebuild vs. Incremental (`lda index`)
### 13. Structural Repository Map (`lda_repomap`)
Generate a dense, graph-centrality (PageRank) ranked repository overview containing structural skeletons within a token budget:
```bash
# CLI execution
uv run lda repomap --budget 2000 --json
```
```json
// MCP JSON-RPC execution
{"method": "tools/call", "params": {"name": "lda_repomap", "arguments": {"budget": 2000}}}
```

### 14. Targeted Test Selection (`lda_focused_tests` / `lda tests`)
Discover the exact unit tests and falsifiers associated with touched or modified files (avoids full suite overhead):
```bash
# CLI execution
uv run lda tests vanguard/packages/kernel/budget.py
```
```json
// MCP JSON-RPC execution
{"method": "tools/call", "params": {"name": "lda_focused_tests", "arguments": {"touched_files": ["vanguard/packages/kernel/budget.py"]}}}
```

### 15. SOTA Graph Diffusion & Submodular Strategy
`lda context` defaults to `ppr_submodular` (Markov spreading activation + Minoux submodular knapsack), but supports fallback to `fts5_bm25`:
```bash
uv run lda context "kernel budget" --strategy ppr_submodular --budget 4000
```

---

## Autonomous Agent Coding Recipes

### Recipe 1: Fast Bug Fix & Surgical Test Validation
1. **Locate Context**: Run `lda_context` with the error trace or bug description to retrieve relevant AST symbols and canonical docs.
2. **Inspect Skeletons**: Inspect the type signatures and docstrings returned in `symbols` to identify the bug root cause without reading entire multi-thousand line files.
3. **Edit Code**: Apply the targeted patch strictly to the offending module.
4. **Targeted Verification**: Run `lda_focused_tests` (or `uv run lda tests <modified_file>`) to run only the 1-3 falsifiers covering your changes in <0.2s instead of the entire 10s suite.

### Recipe 2: Feature Extension & Architecture Onboarding
1. **Global Orientation**: Run `lda_repomap --budget 2000` to obtain a dense structural map of all key interfaces, structs, and modules across the codebase.
2. **Interface Pinning**: Use `lda_symbol` on the target protocol/interface (e.g. `ModelPort`, `Governor`) to get exact contracts.
3. **Trace Impact**: Run `lda_callers` on affected methods to check which callers must be maintained.
4. **Verify**: Run `lda_focused_tests` to ensure no regressions were introduced.

---

## Mandatory 4-Step Navigation Invariant

When assigned any coding, debugging, or refactoring task:

0. **Health Gate**: Run `lda_doctor` / `lda_check` first. If `index_healthy` is `false`, fall back to `python3 tools/docs_rag_v0.py "<query>"` and `rg`.
1. **Acquire Context**: Run `lda_context` with your task prompt. Check `source_head_sha` against the workspace HEAD; on mismatch, recompile.
2. **Verify Dependencies**: Pin symbols with `lda_symbol` and trace callers with `lda_callers`.
3. **Execute & Falsify**: Apply surgical diffs, run the tests identified in `lda_focused_tests`, and update all documentation debt obligations returned by `lda_context`.

> Invariant: CLI and MCP serve the **same** fact graph and packet dialect — there is exactly one emitter and one freshness contract (`provenance.source_head_sha`).

