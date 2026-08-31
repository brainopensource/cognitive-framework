---
id: lda-readme
class: reference
authority: descriptive
status: living
owner: documentation-architect
---

# LDA — LLM Docs Atlas

LDA is a thin, deterministic Documentation-as-Code and machine-context control plane. It orchestrates existing repository indexes and checks; it is not a replacement parser, search engine, graph database, RAG system, or agent harness.

## Project-agnostic by construction

LDA core contains **zero project-specific constants**. Everything repository-specific lives in a **profile** — pure data, never code:

- **Selection is explicit only** (no side-channel detection): `lda.yaml` / `lda.yml` / `lda.toml` `profile:` key → `$LDA_PROFILE` environment variable → built-in generic profile. A named-but-missing profile **fails closed** (ValueError), never silently degrades.
- **Profile lookup order**: `<repo>/profiles/lda/<name>.{toml,yaml,yml}` → `<repo>/.lda/profiles/<name>.{toml,yaml,yml}` → bundled `tools/007_LLM_DOCS_ATLAS/profiles/<name>.{toml,yaml,yml}`.
- Profiles carry: docs/source/test/schema roots, excluded dirs, authority vocabulary (`preferred`/`secondary`/`excluded`), non-canonical directory prefixes, low-signal locator patterns, `knowledge_adapter` name, `validation_commands`, and the invariants below.
- Bundled profiles: `generic.toml` (zero assumptions) and `aether.toml` (AETHER/Vanguard). This repository selects `profile: aether` via its root `lda.yaml`.

## Architectural invariants (enforced by contract tests)

1. **Single Emitter**: LDA never writes `<generated_root>/knowledge/*`. The canonical repository generator (in AETHER: `tools/generate_knowledge_base.py`, `just docs-knowledge`) is the sole emitter of record; LDA consumes it as a downstream, read-only projection. Rescans are in-memory only.
2. **Git-HEAD binding (fail-closed freshness)**: every context packet records `provenance.source_head_sha` (live workspace HEAD at compile time). Consumers MUST compare it against the current workspace HEAD and recompile or refuse to serve on mismatch — stale line numbers and symbols are worse than no facts.
3. **Bounded growth**: global symbol rankings are capped at Top-K (`profile.max_global_symbols`, default 500). Fine-grained symbol definitions remain available on demand via targeted zoom queries (`lda symbol` / `lda callers` / `lda references`).

Run from the repository root (the supported installable surface is the `lda` console script):

```bash
python3 -m tools.007_LLM_DOCS_ATLAS.cli status --json
python3 -m tools.007_LLM_DOCS_ATLAS.cli context "modify delegation behavior" --budget 6000 --json
python3 -m tools.007_LLM_DOCS_ATLAS.cli inspect docs/SPEC.md
uv run lda --help
uv run lda serve
```

The local dashboard binds only to `127.0.0.1:8765` by default. Its read-only API exposes `/api/status`, `/api/documents`, `/api/relations`, `/api/context`, and `/api/providers`. The Overview, Documents, Context, Graph, Quality, and Providers views all consume those same service results as the CLI.

## MCP server (upgraded)

`lda-mcp` (stdio JSON-RPC) exposes tools `lda_context`, `lda_brief`, `lda_consolidate`, `lda_drift`, `lda_repomap`, `lda_focused_tests`, `lda_symbol`, `lda_callers`, `lda_callees`, `lda_references`, `lda_tests_for_symbol`, `lda_docs_for_symbol`, `lda_fts_search`, `lda_map`, `lda_doctor`, `lda_check`, and `lda_coverage`; resources `lda://map` and `lda://docs/{id}`; prompts `lda_task_briefing` and `lda_repo_orientation`. On a cold index it degrades to authority-aware catalog routing (`degraded_mode: catalog_routing`) — LDA is standalone and imports no other repository tool. Agent-facing workflow recipes live in `SKILL.md`.

The `knowledge` provider consumes `<generated_root>/knowledge/*.jsonl`; the `git` provider adds revision provenance. Context selection ranks keyword matches and authority via the active profile, prefers canonical/normative documents, and enforces the token budget. Research is opt-in. JSON is the stable agent-facing interface.

## Retrieval strategies (Phase A)

`lda context --strategy {ppr_submodular,hybrid_rrf,fts5_bm25}`:

- **ppr_submodular** (default): BM25 seeds + Personalized-PageRank graph diffusion + submodular knapsack.
- **hybrid_rrf**: deterministic feature-hashed dense embeddings (md5-bucketed, stable across processes) fused with lexical BM25 via Reciprocal Rank Fusion (k=60). Dense-only semantic hits enter the candidate pool.
- **fts5_bm25**: lexical baseline.

Additional Phase A guarantees:

- **Section-level FTS**: document *sections* are indexed with full content; matching sections become zoomed `doc_section` candidates (`path#L1-L40`) and demote their whole-document parent, so packets carry the relevant passage.
- **Query conditioning** (`core/query.py`): intent classification (bugfix/feature/research/test/explain), symbol-token extraction, and stack-trace `file:line` frame routing (frames become top-scored code candidates).
- **Intent-conditioned budget mix**: docs/code/tests fractions follow the detected intent (e.g. bugfix → 20/55/25); override per intent via profile `budget_mix = { intent = [docs, code, tests] }`. Invalid overrides fail closed to the built-in mix.
- **Content dedup**: the knapsack allocator collapses near-identical content (shingle Jaccard ≥ 0.9) so duplicate documents cannot consume budget.

## Briefing, consolidation, drift (Phase B)

- `lda brief "<task>"` — structured briefing (markdown + JSON): task read-back, intent, authority map, key documents/code, documentation obligations, test falsifiers, HEAD-bound provenance.
- `lda consolidate` — duplicate/overlapping documents and conflicting authority claims (read-only diagnostics).
- `lda drift` — stale symbol paths, undocumented symbols, documents without code evidence.
- Both also run as warn-only checks inside `lda check` (`knowledge.consolidation`, `knowledge.drift`).

## Benchmark (Phase E)

`lda bench` runs the deterministic golden-query fixture (6-file repo, 4 queries) through every strategy and reports recall@5, MRR, and latency. Retrieval-quality regressions must keep `recall@5 >= 0.5` per strategy (`test/tools/test_lda_skill_bench.py`).

## Adopted plugin: `repo_report`

`plugins/repo_report/` (first adopted first-party plugin) provides deterministic repository snapshots — git state, freshness, incremental delta, inventory, contract inventory, graph stats — writing only `.lda/repo-report/`. Optional dependency-free Rust walk accelerator under `plugins/repo_report/rust/`. Registers through `PluginManager`; see its README.

## Portability contract

`test/tools/test_lda_portability.py` is the executable definition of "LDA works in ANY project": generic-by-default profile selection (including repositories containing Aether-shaped artifacts), explicit profile resolution (config, env, repo-local override, fail-closed unknowns), single-emitter read-only behavior, HEAD-bound packet provenance, symbol ceilings, and a full index→packet pipeline on a non-Python (TypeScript/Markdown) repository. Any change to LDA core must keep this suite green.

Add a provider by implementing `available(ctx)` and `collect(ctx) -> ProviderResult`, then registering it in `atlas.default_registry()`. An analyzer should consume normalized results and return metrics/diagnostics. A future ranker can replace the transparent heuristic without changing the packet schema.

LDA deliberately delegates validation/build authority to existing `just docs-check`, `just docs-full`, and `just verify`; it adds no CI pipeline or parallel knowledge store. Heavy providers, embeddings, graph databases, servers, and autonomous inference are deferred. The `tools/lda` package is a stable import/entry-point facade over this physical project directory, which retains the requested numbered location.
