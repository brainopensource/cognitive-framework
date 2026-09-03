---
name: lda-navigator
description: >-
  Universal Repository Intelligence & Navigation Protocol.
  Use when exploring the codebase, finding symbols, routing tasks,
  checking documentation debt obligations, or locating test falsifiers.
---

# LDA Repository Intelligence & Context Navigation Protocol

This skill equips AI agents with the complete suite of **Repository Intelligence Tools** over CLI (`uv run lda`) and MCP.

## Complete LDA Tool Surface

### 1. Token-Bounded Task Context (`lda context` / `lda_context`)
Compile high-signal context packets containing canonical docs, symbols, tests, and documentation debt obligations under a strict token budget:
```bash
# CLI execution
uv run lda context "<task keywords or error>" --budget 4000
```
```json
// MCP JSON-RPC execution
{"method": "tools/call", "params": {"name": "lda_context", "arguments": {"query": "kernel dispatch", "budget": 4000}}}
```

### 2. Task Briefing (`lda brief` / `lda_brief`)
Compile a structured task briefing formatted in Markdown for human + agent consumption:
```bash
uv run lda brief "Fix admission gate verification" --budget 8000
```

### 3. Precise AST Symbol Lookup (`lda symbol` / `lda_symbol`)
Lookup exact class/function signatures, docstrings, and line ranges with ranked ordering (production code > tools > tests > benchmarks) and exact match filtering:
```bash
uv run lda symbol AdmissionGate
uv run lda symbol AdmissionGate --exact
```
```json
{"method": "tools/call", "params": {"name": "lda_symbol", "arguments": {"symbol_name": "AdmissionGate"}}}
```

### 4. Upstream Callers & Impact Graph (`lda callers` / `lda_callers`)
Discover which functions and test methods call a specific symbol to assess blast radius and prevent regressions:
```bash
uv run lda callers AdmissionGate.evaluate
```
```json
{"method": "tools/call", "params": {"name": "lda_callers", "arguments": {"symbol_id": "AdmissionGate.evaluate"}}}
```

### 5. Downstream Callees (`lda callees` / `lda_callees`)
Discover what functions are called by a target method:
```bash
uv run lda callees AdmissionGate.evaluate
```
```json
{"method": "tools/call", "params": {"name": "lda_callees", "arguments": {"symbol_id": "AdmissionGate.evaluate"}}}
```

### 6. Symbol Usages & References (`lda references` / `lda_references`)
Find all occurrences, imports, and cross-references across the repository:
```bash
uv run lda references AdmissionGate
```
```json
{"method": "tools/call", "params": {"name": "lda_references", "arguments": {"symbol_id": "AdmissionGate"}}}
```

### 7. Targeted Test Selection (`lda tests` / `lda_focused_tests`)
Discover the exact unit tests, call-graph falsifiers, and runnable commands associated with touched or modified files (avoids full suite overhead):
```bash
uv run lda tests vanguard/packages/agency/episode/admission_gate.py
```
```json
{"method": "tools/call", "params": {"name": "lda_focused_tests", "arguments": {"touched_files": ["vanguard/packages/agency/episode/admission_gate.py"]}}}
```

### 8. Structural Repository Map (`lda repomap` / `lda_repomap`)
Generate a dense, graph-centrality (PageRank) ranked repository overview containing structural skeletons within a token budget:
```bash
uv run lda repomap --budget 2000 --json
uv run lda repomap --budget 3000 --focus vanguard/packages/agency/episode/admission_gate.py
```
```json
{"method": "tools/call", "params": {"name": "lda_repomap", "arguments": {"budget": 2000}}}
```

### 9. Subsystem Topology Map (`lda map` / `lda_map`)
View the high-level architecture boundaries, module paths, and logical LOC counts:
```bash
uv run lda map --json
```

### 10. Consolidation & Drift Diagnostics (`lda consolidate` / `lda drift`)
Detect duplicate documents, authority conflicts, stale documentation paths, undocumented symbols, and orphan docs:
```bash
uv run lda consolidate --json
uv run lda drift --json
```

### 11. Repository Identity, Fact Diff, and Structural Metrics
- **`lda identity`**: Branch, HEAD commit, dirty state, build systems, index-vs-HEAD freshness.
- **`lda diff [--since <sha>]`**: Fact-level workspace diff vs index or commit range.
- **`lda metrics`**: Fan-in/fan-out hubs, import cycles, and doc coverage.
```bash
uv run lda identity --json
uv run lda diff --json
uv run lda metrics --json
```

### 12. Retrieval Benchmark (`lda bench`)
Run deterministic retrieval-quality benchmarks (Recall@k, MRR, latency):
```bash
uv run lda bench --budget 2000 --k 5 --json
```

### 13. Health & Index Diagnostics (`lda doctor` / `lda check` / `lda scan`)
Assert SQLite database health, entity counts, per-language coverage, HEAD binding, and zero orphan FTS rows:
```bash
uv run lda doctor --json
uv run lda check --json
```

### 14. Document Inspection (`lda inspect`)
Inspect metadata, authority, and token estimates for a specific document path or canonical ID:
```bash
uv run lda inspect AGENTS.md --json
```

### 15. Standardizer / Ruler (`lda standardize`)
Inspect a single file — detected language, canonical symbol kinds, and import edges:
```bash
uv run lda standardize vanguard/packages/agency/episode/admission_gate.py
```

### 16. Indexing & Rebuild (`lda index`)
Incremental or full fresh rebuild of the SQLite fact graph (`.lda/index.db`):
```bash
uv run lda index --rebuild --json
```

---

## Autonomous Agent Coding Recipes

### Recipe 1: Fast Bug Fix & Surgical Test Validation
1. **Locate Context**: Run `lda context "<error trace>"` to retrieve relevant AST symbols and canonical docs.
2. **Inspect Skeletons**: Inspect type signatures and docstrings via `lda symbol <SymbolName> --exact` without reading entire multi-thousand line files.
3. **Trace Impact**: Run `lda callers <SymbolName>` to discover upstream callers and prevent unintended regressions.
4. **Edit Code**: Apply the targeted patch strictly to the offending module.
5. **Targeted Verification**: Run `uv run lda tests <modified_file>` to execute only the exact falsifiers covering your changes in <0.2s instead of the entire suite.

### Recipe 2: Feature Extension & Architecture Onboarding
1. **Global Orientation**: Run `lda repomap --budget 2000` to obtain a dense structural map of key interfaces and modules.
2. **Interface Pinning**: Use `lda symbol <InterfaceName>` to inspect exact protocol contracts.
3. **Trace Impact**: Run `lda callers <InterfaceName>` to check dependent call sites.
4. **Verify**: Run `lda tests <modified_file>` to execute targeted falsifiers.

---

## Mandatory Navigation Invariant

When assigned any coding, debugging, or refactoring task:

0. **Health Gate**: Run `uv run lda doctor --json` first. Confirm `"index_healthy": true` and `"status": "HEALTHY"`. If degraded, fall back to `python3 tools/docs_rag_v0.py "<query>"` and `rg`.
1. **Acquire Context**: Run `lda context "<task>"` to inspect high-signal context and documentation debt obligations.
2. **Verify Dependencies**: Pin symbols with `lda symbol` and trace callers with `lda callers`.
3. **Execute & Falsify**: Apply surgical diffs, run the tests identified in `lda tests`, and ensure all tests pass.
