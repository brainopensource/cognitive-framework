# LDA `repo_report` plugin

Small deterministic complement for `tools/007_LLM_DOCS_ATLAS`.

It does not replace LDA routing, `docs_rag_v0.py`, the canonical knowledge
generator, the existing AST provider, the SQLite fact graph, or the context
compiler. It consumes those surfaces and produces a compact rebuildable report.

## What it adds

- Git snapshot: branch, HEAD and dirty state.
- Freshness check against the current Atlas context.
- Incremental file delta using SHA-256 state.
- Inventory metrics: files, code, docs, bytes and lines.
- Contract inventory for schemas, manifests and protocol-like files.
- Existing LDA graph statistics: entities, symbols, documents and relations.
- `report.json` for machines.
- `report.md` for humans.
- Optional dependency-free Rust scanner for very large trees.

The generated report is a projection. It must never be treated as architectural
authority, and it never writes `.generated/knowledge/*`.

## Run directly

From the repository root:

```bash
python3 -m tools.007_LLM_DOCS_ATLAS.plugins.repo_report.report \
  --root . --output .lda/repo-report
```

Print machine metadata:

```bash
python3 -m tools.007_LLM_DOCS_ATLAS.plugins.repo_report.report \
  --root . --json
```

Ask the report to refresh the existing LDA SQLite index first:

```bash
python3 -m tools.007_LLM_DOCS_ATLAS.plugins.repo_report.report \
  --root . --refresh-index
```

The default output is:

```text
.lda/repo-report/report.json
.lda/repo-report/report.md
.lda/repo-report/state.json
```

## Register as an LDA plugin

Use the existing plugin manager; no core rewrite is needed:

```python
import importlib

registry = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.registry")
plugin_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.plugins.repo_report")

manager = registry.PluginManager.get_instance()
manager.register_plugin(plugin_mod.RepoReportPlugin())
```

Then collect it with the normal LDA provider flow. The plugin exposes one
provider named `repo_report` and no analyzer or custom skeletonizer.

For installed distributions, add an entry point to the package that owns LDA:

```toml
[project.entry-points."lda.plugins"]
repo_report = "tools.007_LLM_DOCS_ATLAS.plugins.repo_report.plugin:plugin"
```

The existing `PluginManager.discover_installed_plugins()` will discover it.

## Use from an agent

The recommended order is:

```bash
uv run lda doctor --json
uv run lda index --incremental --json
python3 -m tools.007_LLM_DOCS_ATLAS.plugins.repo_report.report --json
uv run lda context "<task>" --budget 6000 --json
```

The agent should read `report.json` first, then ask LDA for a bounded context
packet. It should not load the whole report or whole repository by default.

## Rust accelerator

The Rust component is optional and intentionally dependency-free. Build it only
when the repository is large enough for a faster filesystem walk:

```bash
cargo build --release --manifest-path \
  tools/007_LLM_DOCS_ATLAS/plugins/repo_report/rust/Cargo.toml
```

It emits tab-separated `relative_path`, `bytes`, and `lines`. Python remains the
authoritative orchestrator and computes hashes, contracts, freshness and report
schemas. The accelerator is therefore replaceable and cannot change authority.

## Integration boundary

Keep this plugin under `tools/007_LLM_DOCS_ATLAS/plugins/` while it is being
validated. Do not import it from `domain`, `kernel`, `agency`, or production
runtime code. If AETHER later needs the result, consume `report.json` through a
generic `IndexPort` adapter and retain the report's HEAD and generator version.

## Incremental behavior

`state.json` stores only repository-relative paths and content hashes. On the
next run the report emits changed, deleted and unchanged counts. The existing
LDA index remains responsible for incremental symbol and relation facts.

## Safety and limitations

- It reads the repository and writes only `.lda/repo-report` by default.
- It does not execute repository build commands.
- It does not call an LLM.
- It does not alter `.generated/knowledge`.
- It does not infer authority from a filename.
- JSON parsing failures are reported as inventory metadata.
- A missing or stale LDA index is visible in the graph section.
- Current HEAD mismatch is reported as `STALE`.
- Contract discovery is inventory, not full semantic validation.
- Tree-sitter and SCIP remain LDA providers, not reimplemented here.
