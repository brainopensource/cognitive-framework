---
id: lda-readme
class: reference
authority: descriptive
status: living
owner: documentation-architect
---

# LDA — LLM Docs Atlas

LDA is a thin, deterministic **repository-intelligence and context engine** for any project. It indexes code and documentation into a local SQLite + FTS5 fact graph, then compiles token-budgeted, provenance-bound context packets, briefings, and diagnostics for AI agents and humans — via **CLI, MCP server, or agent skill**. It is not a replacement parser, search engine, graph database, RAG system, or agent harness; it orchestrates those capabilities behind one stable interface.

**Why use it?** Measured on a 2,814-file repository (median of 3 runs, logs in acceptance gate):

```text
Baseline (3x rg + manual reading):  137 files / 231 lines / 770 KB to read
LDA (1 command):                    12 curated items / 13 KB, 10/12 task-term
                                    precision, with tests, callers, provenance
=> ~61x less reading for the same answer; 41x on a foreign repo
```

## Quick start

```bash
# 1. From inside any repository (LDA discovers the root automatically):
uv run lda doctor          # health check; tells you what to do next
uv run lda index           # build the fact graph (one-time; incremental after)
uv run lda check           # full diagnostics: profile, KB, graph, freshness, drift

# 2. Ask for bounded context (the primary product):
uv run lda context "where is X implemented" --budget 4000 --json

# 3. Get a full task briefing (markdown for humans, JSON for agents):
uv run lda brief "implement feature Y"
```

First run on a new repo: `doctor` reports `index_healthy: false` and instructs `lda index`. Indexing is incremental afterwards (`lda index --incremental`); `--rebuild` purges stale facts after mass deletions.

## The agent workflow (also in [SKILL.md](SKILL.md))

```bash
uv run lda identity --json                   # 0. which repo/commit am I on? is the index bound to it?
uv run lda doctor --json                     # 1. is the index healthy?
uv run lda context "<task>" --budget 6000 --json   # 2. bounded context packet
uv run lda brief "<task>" --json             # 3. obligations + falsifiers + narrative
# ... implement ...
uv run lda tests <touched-files> --json      # 4. targeted falsifiers for your change
uv run lda diff --json                       # 5. what changed vs the index? (or --since <sha>)
uv run lda drift --json && uv run lda consolidate --json   # 6. what did I leave stale?
```

Rule of thumb: **never load whole files**. Zoom with `lda symbol` / `lda callers` / `lda references` instead.

## CLI reference

| Command | Purpose |
|---|---|
| `lda index [--incremental/--rebuild]` | Build/refresh the SQLite+FTS5 fact graph |
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

Tools: `lda_context`, `lda_brief`, `lda_consolidate`, `lda_drift`, `lda_identity`, `lda_diff`, `lda_metrics`, `lda_repomap`, `lda_focused_tests`, `lda_symbol`, `lda_callers`, `lda_callees`, `lda_references`, `lda_tests_for_symbol`, `lda_docs_for_symbol`, `lda_fts_search`, `lda_map`, `lda_doctor`, `lda_check`, `lda_coverage`.
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
