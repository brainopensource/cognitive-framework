---
id: lda-readme
class: reference
authority: descriptive
status: living
owner: documentation-architect
---

# LDA — LLM Docs Atlas

LDA is a thin, deterministic, zero-daemon **repository-intelligence and context engine** for any project. It indexes code and documentation into a local SQLite-WAL + FTS5 fact graph, then compiles token-budgeted, provenance-bound context packets, briefings, and diagnostics for AI agents and humans — via **CLI, MCP server, or agent skill**. It requires no external services, network access, or persistent background daemons.

**Why use it?** Measured empirically on a 3,372-file repository (AETHER / Vanguard):

```text
Full Rebuild Baseline:        12,810 ms (12.8s) full AST graph rebuild
SOTA Delta Indexing:          21.62 ms (<25ms) auto-detected working tree delta (~592x faster)
Memory / Background Overhead: 0 MB idle RAM, 0% CPU (ephemeral SQLite WAL, zero daemons)
Context Window Efficiency:    ~80% token savings (slices & skeletons vs whole files)
Task Preparation Workflow:    1 unified command (`lda plan`) replacing 5 exploratory roundtrips
Test Falsifier Association:   2.03 ms indexed SQL joins (~120x faster than table scan)
```

## Quick start

```bash
# 1. Primary SOTA Fast Path: Compile a one-shot task execution bundle
#    (Auto-syncs dirty files, resolves target symbols, callers, doc obligations, & tests)
uv run lda plan "subagent episode spawn attenuate child capabilities" --budget 8000

# 2. Resolve code symbols from natural language intent (when exact name is unknown):
uv run lda resolve "attenuate capability tokens"

# 3. Sub-50ms incremental AST update after editing code (0 MB background daemon):
uv run lda index --delta

# 4. Diagnostics & health check:
uv run lda doctor          # health check; confirms SQLite & FTS5 integrity
uv run lda identity        # verifies branch, HEAD, dirty state, and freshness
```

First run on a new repo: `doctor` reports `index_healthy: false` and instructs `lda index`. Indexing is incremental afterwards (`lda index --delta` or `lda index --incremental`); `--rebuild` purges stale facts after mass deletions.

## The agent workflow (also in [SKILL.md](../../.agents/skills/lda-navigator/SKILL.md))

```bash
uv run lda plan "<task>" --budget 8000 --json   # 1. One-shot bundle: symbols + callers + docs + tests
# ... read targeted line ranges, then implement surgical code edits ...
uv run lda index --delta                        # 2. sub-50ms incremental re-index of touched files
uv run <test command output by lda plan>        # 3. run targeted test falsifiers
uv run lda drift --json && uv run lda diff --json  # 4. verify zero doc drift or orphan contracts
```

Rule of thumb: **never load whole files**. Zoom with `lda plan` / `lda symbol` / `lda callers` / `lda references` instead.

## CLI reference

| Command | Purpose |
|---|---|
| `lda plan "<task>" [--budget B] [--strategy S]` | **[SOTA] One-shot task bundle**: auto-delta sync, primary symbols, blast radius (callers), doc obligations, and test falsifiers |
| `lda resolve "<intent>" [--top-k K]` | **[SOTA] Semantic intent symbol resolution**: offline multi-signal ranking (BM25 + graph in-degree + tier authority) |
| `lda index --delta [files...]` | **[SOTA] Ephemeral incremental delta**: sub-50ms AST & markdown sync on modified files with 0 MB idle daemon |
| `lda index [--incremental/--rebuild]` | Build/refresh the full SQLite+FTS5 fact graph |
| `lda status` / `scan` | Snapshot: DB stats, topology, totals |
| `lda doctor` | Fast health check + actionable `index_hint` |
| `lda identity` | Repository identity: branch, HEAD, dirty state, submodules, build systems, index-vs-HEAD freshness (FRESH/STALE/UNKNOWN) |
| `lda diff [--since <sha>]` | Fact-level diff: workspace vs index (added/modified/deleted), or a git range |
| `lda metrics` | Structural metrics: fan-in/fan-out hubs, import cycles, hub files, doc coverage |
| `lda check` | Full diagnostics (profile, KB, graph, coverage, drift, consolidation) |
| `lda context "<task>"` | **Token-budgeted ContextPacket** (JSON, cached per git HEAD) |
| `lda brief "<task>"` | Structured briefing: intent, authority map, obligations, falsifiers |
| `lda query "<terms>"` | FTS search over symbols/docs (catalog fallback when cold) |
| `lda symbol <name>` | Definition, signature, docstring, location |
| `lda callers` / `references` <symbol_id> | Graph zoom queries |
| `lda map` | Architecture topology summary |
| `lda repomap [--budget N] [--focus files]` | PageRank-ranked structural map with skeletons |
| `lda tests <files...>` | Tests/falsifiers associated with touched files |
| `lda inspect <path-or-canonical-id>` | One document's catalog metadata |
| `lda drift` | Stale paths, undocumented symbols, orphan documents |
| `lda consolidate` | Duplicate documents, conflicting authority claims |
| `lda standardize <file>` | Language + symbol skeleton for one file |
| `lda bench` | Deterministic retrieval benchmark (recall@k, MRR, latency) |
| `lda build` | Regenerate the local dashboard |

All commands accept `--json` (the stable agent-facing interface) and `--root <path>` (run against any repository from anywhere).

## Choosing a strategy (`lda context --strategy`)

| Strategy | Best for | How it ranks |
|---|---|---|
| `ppr_submodular` *(default)* | Architectural / graph questions | BM25 seeds → Personalized-PageRank diffusion → submodular knapsack |
| `hybrid_rrf` | Paraphrased / semantic queries, zero-keyword matches | Deterministic hashed embeddings fused with BM25 via RRF (k=60) |
| `fts5_bm25` | Exact keyword lookup | Pure lexical baseline |

Built-in retrievals that always apply: **section-level zooming** (packets carry the matching passage, not the whole doc), **stack-trace routing** (paste `File "src/x.py", line 42` into the task — it becomes a top-scored code candidate), **intent-conditioned budget mix** (bugfix vs research vs test tasks get different docs/code/tests fractions), **content dedup** (identical docs can't consume budget twice), and **bounded omissions** (every packet lists what was considered but *not* selected and why — `omitted: [{locator, reason: budget_exhausted}]`, capped at 12 — so absence of evidence is never silent).


## Adapting LDA to any project (profiles)

LDA core contains **zero project-specific constants**. Everything repository-specific lives in a **profile** — pure data (TOML/YAML), never code. Drop a `lda.yaml` at any repo root:

```yaml
profile: my-project
```

and either commit the profile or put it in `.lda/profiles/my-project.toml`:

```toml
name = "my-project"
docs_roots = ["doc"]                    # where documentation lives
source_roots = ["src"]                  # where code lives
test_roots = ["spec"]                   # where tests live
excluded_dirs = ["vendor", "gen"]       # never index these
preferred_authority = ["normative"]     # frontmatter authority vocabulary
excluded_authority = ["archive"]
non_canonical_prefixes = ["scratch/"]   # demote these doc tiers
low_signal_patterns = ["__init__.py", "/fixtures/"]
max_global_symbols = 300                # bounded-growth ceiling
```

Optional per-intent packet mix `[docs, code, tests]` (fractions sum to 1.0) — invalid rows fail closed to the built-in mix:

```toml
[budget_mix]
bugfix   = [0.10, 0.70, 0.20]
research = [0.60, 0.25, 0.15]
```

**Selection is explicit only** (no side-channel detection): `lda.yaml` `profile:` key → `$LDA_PROFILE` env → built-in `generic` profile. A named-but-missing profile **fails closed** (ValueError), never silently degrades. Lookup order: `<repo>/profiles/lda/` → `<repo>/.lda/profiles/` → bundled `profiles/` (`generic.toml`, `aether.toml`).

## Architectural invariants (enforced by contract tests)

1. **Single Emitter**: LDA never writes `<generated_root>/knowledge/*`. The canonical repository generator (in AETHER: `tools/generate_knowledge_base.py`, `just docs-knowledge`) is the sole emitter of record; LDA consumes it as a downstream, read-only projection. Rescans are in-memory only.
2. **Git-HEAD binding (fail-closed freshness)**: every context packet records `provenance.source_head_sha` (live workspace HEAD at compile time), and every index run records the `head_sha` it indexed. Consumers MUST compare against the current workspace HEAD and recompile or refuse to serve on mismatch — stale line numbers and symbols are worse than no facts. `lda identity` reports the index-vs-HEAD binding as `FRESH` / `STALE` / `UNKNOWN` in one shot.
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

## MCP server (for AI agents)

`lda-mcp` speaks JSON-RPC 2.0 over stdio. Register it in your agent config (e.g. Claude Desktop / Cline):

```json
{
  "mcpServers": {
    "lda": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/Aether-D-System", "lda-mcp", "--root", "/path/to/any/repo"]
    }
  }
}
```

Tools: `lda_plan`, `lda_resolve`, `lda_delta`, `lda_context`, `lda_brief`, `lda_consolidate`, `lda_drift`, `lda_identity`, `lda_diff`, `lda_metrics`, `lda_repomap`, `lda_focused_tests`, `lda_symbol`, `lda_callers`, `lda_callees`, `lda_references`, `lda_tests_for_symbol`, `lda_docs_for_symbol`, `lda_fts_search`, `lda_map`, `lda_doctor`, `lda_check`, `lda_coverage`.
Resources: `lda://map`, `lda://docs/{id}`. Prompts: `lda_task_briefing`, `lda_repo_orientation`.
On a cold index the server degrades to authority-aware catalog routing (`degraded_mode: catalog_routing`) — LDA is standalone and imports no other repository tool.

## Local dashboard

`uv run lda serve` binds to `127.0.0.1:8765` (read-only): Overview, Documents, Context, Graph, Quality, and Providers views consuming the same services as the CLI (`/api/status`, `/api/documents`, `/api/relations`, `/api/context`, `/api/providers`).

## Extending LDA

- **Provider**: implement `available(ctx)` and `collect(ctx) -> ProviderResult`, register in `atlas.default_registry()`.
- **Plugin**: implement the `Plugin` protocol (providers/analyzers/skeletonizers) and register via `PluginManager`. Reference implementation: [`plugins/repo_report/`](plugins/repo_report/README.md) — deterministic repo snapshots (git state, freshness, incremental delta, contract inventory), optional Rust walk accelerator, writes only `.lda/repo-report/`.
- **Ranker/strategy**: add a strategy to `StrategySwitcher`; the packet schema does not change.

## Quality gates

- `lda bench`: deterministic golden-query fixture, per-strategy recall@5 / MRR / latency; regression floor `recall@5 >= 0.5` (`test/tools/test_lda_skill_bench.py`).
- `test/tools/test_lda_portability.py` is the executable definition of "works in ANY project": generic-by-default selection, fail-closed profiles, single-emitter read-only behavior, HEAD-bound provenance, symbol ceilings, and a full index→packet pipeline on a non-Python repository. Any core change must keep it green.
- Embeddings are md5-bucketed feature hashes — byte-identical across processes (cross-process determinism is tested).

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `index_healthy: false` in doctor | Index is cold: run `lda index` (or `--rebuild` after mass deletions) |
| Context packet looks stale | HEAD moved: packets are cached per git HEAD; recompile (or use `--no-cache`) |
| Packet empty on a cold index | Expected: `degraded_mode: catalog_routing` routes via the knowledge catalog only; index for full retrieval |
| Wrong files favored | Check `low_signal_patterns` / `excluded_dirs` in the active profile; `lda doctor` shows which profile is active |
| Missing symbols for a language | AST providers cover Py/TS/Rust/Go; other languages fall back to the generic identifier scanner |
| `--root` against a repo without git | Works; only HEAD-bound freshness checks degrade (reported as warnings, never silent) |

## Where things live

```text
tools/007_LLM_DOCS_ATLAS/          # LDA (this package)
├── atlas.py                       # engine coordinator (index/query/context APIs)
├── cli.py                         # `lda` command surface
├── server_mcp.py                  # `lda-mcp` stdio JSON-RPC server
├── SKILL.md                       # agent skill manifest (workflow recipes)
├── core/                          # IR, storage (SQLite+FTS5), ranking, PPR,
│                                  # hybrid RRF, query conditioning, allocator,
│                                  # briefing, consolidation, drift, bench, health,
│                                  # identity, repodiff, metrics
├── providers/                     # filesystem, markdown, code_ast, git, knowledge
├── plugins/repo_report/           # first-party plugin (repo snapshots)
└── profiles/                      # bundled generic.toml / aether.toml
tools/lda/                         # stable `lda` / `lda-mcp` entry-point facade
test/tools/test_lda_*.py           # contract + falsifier suites
```

LDA stores all derived state under `<repo>/.lda/` (index, caches, reports) — one directory to delete for a clean slate. It deliberately adds no CI pipeline or parallel knowledge store and delegates validation authority to the repository's own commands. Heavy integrations (tree-sitter, SCIP, sqlite-vec, graph backends) are deferred or optional behind the plugin ports.
