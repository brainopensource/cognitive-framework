---
name: lda-repository-intelligence
description: >
  Use LDA (LLM Docs Atlas) to orient in any repository, compile token-budgeted
  task context, brief a task, and check knowledge health. Deterministic,
  fail-closed, HEAD-bound. Covers CLI, MCP tools, and the exact workflow order
  agents should follow plus fallbacks when the index is cold.
---

# LDA — Repository Intelligence Workflow

## When to use
- Starting any task in an unfamiliar repository (orientation).
- Before implementing: compile a bounded context packet or briefing instead of grepping the whole tree.
- After editing docs or code: check drift/consolidation and knowledge health.

## Golden order (token-efficient)
1. `lda doctor --json` — index health. If `index_healthy: false`: run `lda index` (or `lda index --rebuild` after mass deletions).
2. `lda context "<task>" --budget 6000 --json` — bounded packet: canonical docs, symbols, tests, provenance (HEAD-bound).
3. `lda brief "<task>" --json` — when you want obligations + falsifiers + markdown narrative.
4. Implement. Then `lda drift --json` and `lda consolidate --json` to see what your change left stale.
5. `lda tests <touched-files> --json` — targeted falsifiers for what you touched.

## Strategies
- `ppr_submodular` (default): graph diffusion — best for architectural/graph tasks.
- `hybrid_rrf`: dense+lexical fusion — best for paraphrased/semantic queries.
- `fts5_bm25`: pure lexical baseline.
- Stack traces in the task string route directly to file:line frames.

## Failure rules (fail-closed)
- Never trust a packet whose `provenance.source_head_sha` differs from current workspace HEAD — recompile.
- If the index is cold, `lda context` still routes via authority-aware catalog fallback (`degraded_mode: catalog_routing`).
- Prefer `lda symbol` / `lda callers` / `lda references` zoom queries over loading whole files.

## MCP surface
Tools: `lda_context`, `lda_brief`, `lda_consolidate`, `lda_drift`, `lda_repomap`,
`lda_focused_tests`, `lda_symbol`, `lda_callers`, `lda_callees`, `lda_references`,
`lda_tests_for_symbol`, `lda_docs_for_symbol`, `lda_fts_search`, `lda_map`,
`lda_doctor`, `lda_check`, `lda_coverage`.
Resources: `lda://map`, `lda://docs/{id}`. Prompts: `lda_task_briefing`, `lda_repo_orientation`.
