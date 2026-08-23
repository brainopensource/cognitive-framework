---
id: adr-0087-documentation-topology-context-budgets
class: decision
authority: binding-decision
canonical_for:
  - documentation-topology
  - context-bundle-budgets
status: append-only
owner: engineering-director
version: "0.6.1"
last_verified: 2026-08-23
read_when:
  - changing-documentation-structure
  - adding-context-bundles
do_not_read_when:
  - implementing-runtime-behavior
supersedes: []
superseded_by: null
---

# ADR-0087 — Documentation topology, context budgets, and archive boundary

**Status:** Accepted. **Date:** 2026-08-23. **Decision owner:** Engineering Director.

## Decision

1. `SPEC.md` is the compact normative index. Detailed RFC-2119 law is partitioned into the
   task-sized leaves under `docs/01_law/`; the former SPEC and kernel bodies are preserved there,
   without deleting or paraphrasing technical clauses.
2. Authority directories are ordered `01_law`, `02_decisions`, `03_execution`, `04_architecture`,
   `05_contracts`, `06_protocols`, `07_engineering`, `08_theory`, and `09_diagrams`. ADR, RF/F,
   schema, milestone, and invariant identifiers are never renumbered.
3. Historical references and reviews move atomically to `docs/_archive/references/` and
   `docs/_archive/reviews/`. They remain link- and secret-scanned, but normal developer/agent
   context bundles and searches exclude `_archive/`. No historical text is copied into living docs.
4. Living documents expose `read_when` and `do_not_read_when` guidance where they are entry points;
   indexes route an implementation bundle to at most the sprint task, law clause, decision, contract,
   and falsifier before code changes.
5. Initial document budgets are enforced by `tools/linters/check_doc_budgets.py`. Append-only ADRs
   and frozen archive material are exempt. The preserved compound law anchors (`01_law/RUNTIME.md`
   and `DISPATCH.md`) are explicit exemptions until a future section extraction; their content is
   still reached through the compact index and thematic leaves.

## Consequences

The top-level navigation is stable and authority-ordered. A developer can load a small task bundle
without reading every ADR or historical report, while reviewers retain the complete original law and
provenance. Relative links and governance linters are part of the migration gate; a stale old path is
an error, not a compatibility stub.
