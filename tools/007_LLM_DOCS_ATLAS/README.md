---
id: lda-readme
class: reference
authority: descriptive
status: living
owner: documentation-architect
---

# LDA — LLM Docs Atlas

LDA is a thin, deterministic Documentation-as-Code and machine-context control plane. It orchestrates existing repository indexes and checks; it is not a replacement parser, search engine, graph database, RAG system, or agent harness.

```mermaid
flowchart LR
  Tools[Existing tools and generated knowledge] --> Providers[LDA providers]
  Providers --> IR[Normalized facts]
  IR --> CLI[CLI: status/query/context/check]
  IR --> Dashboard[Static dashboard]
  CLI --> Agents[Humans and agents]
```

Run from the repository root:

```bash
python3 -m tools.007_LLM_DOCS_ATLAS.cli status --json
python3 -m tools.007_LLM_DOCS_ATLAS.cli context "modify delegation behavior" --budget 6000 --json
python3 -m tools.007_LLM_DOCS_ATLAS.cli inspect docs/SPEC.md
```

The `knowledge` provider consumes `.generated/knowledge/*.jsonl`; the `git` provider adds revision provenance. Context selection ranks keyword matches and authority, prefers canonical/normative documents, and enforces the token budget. Research is opt-in. JSON is the stable agent-facing interface.

Add a provider by implementing `available(ctx)` and `collect(ctx) -> ProviderResult`, then registering it in `atlas.default_registry()`. An analyzer should consume normalized results and return metrics/diagnostics. A future ranker can replace the transparent heuristic without changing the packet schema.

LDA deliberately delegates validation/build authority to existing `just docs-check`, `just docs-full`, and `just verify`; it adds no CI pipeline or parallel knowledge store. Heavy providers, embeddings, graph databases, servers, and autonomous inference are deferred.
