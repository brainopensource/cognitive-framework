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

The `knowledge` provider consumes `<generated_root>/knowledge/*.jsonl`; the `git` provider adds revision provenance. Context selection ranks keyword matches and authority via the active profile, prefers canonical/normative documents, and enforces the token budget. Research is opt-in. JSON is the stable agent-facing interface.

## Portability contract

`test/tools/test_lda_portability.py` is the executable definition of "LDA works in ANY project": generic-by-default profile selection (including repositories containing Aether-shaped artifacts), explicit profile resolution (config, env, repo-local override, fail-closed unknowns), single-emitter read-only behavior, HEAD-bound packet provenance, symbol ceilings, and a full index→packet pipeline on a non-Python (TypeScript/Markdown) repository. Any change to LDA core must keep this suite green.

Add a provider by implementing `available(ctx)` and `collect(ctx) -> ProviderResult`, then registering it in `atlas.default_registry()`. An analyzer should consume normalized results and return metrics/diagnostics. A future ranker can replace the transparent heuristic without changing the packet schema.

LDA deliberately delegates validation/build authority to existing `just docs-check`, `just docs-full`, and `just verify`; it adds no CI pipeline or parallel knowledge store. Heavy providers, embeddings, graph databases, servers, and autonomous inference are deferred. The `tools/lda` package is a stable import/entry-point facade over this physical project directory, which retains the requested numbered location.
