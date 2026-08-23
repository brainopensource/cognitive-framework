---
adr: 0086
title: "Historical ADR working-tree consolidation with permanent lineage"
status: accepted
accepted_date: 2026-08-21
source_section: "Director repository-noise reduction order"
implementation_milestone: "M-2 documentation hygiene"
---

# ADR-0086: Consolidate historical ADR bodies while preserving decision lineage

**Context.** Eighty-one pre-v0.6 and M0 ADR bodies repeat obsolete API, process, language, and
sprint-era context. Their surviving constraints are already governed by `docs/SPEC.md`, annexes,
ADRs 0069–0085, schemas, and executable falsifiers. Keeping every historical body in the default
working tree causes retrieval and contributor noise; Git already preserves the original bytes.

**Decision.**

1. Full ADR bodies 0000–0068 and ADR-M0-01–M0-13 leave the working tree. Their identifiers remain
   permanently reserved and their one-line subject/disposition remains in `INDEX.md`.
2. Recovery commit `5b9966c24c13d0ffc4315a39a97870fd756324a9` is the immutable source for
   those historical bodies. The consolidation commit records the removal set.
3. ADRs 0069–0085 remain full active bodies. This ADR becomes 0086 and remains with them.
4. A living requirement may not depend only on a removed body. Before removal, local links move to
   SPEC, an annex, ADR 0069–0086, or the consolidated lineage section. Plain historical citations
   remain legal provenance, never current implementation authority.
5. ADR-0000's logical protections survive: identifiers are never reused, history is never silently
   rewritten, newer decisions supersede explicitly, and every new ADR states a reversal condition.
   “Append-only” governs the decision stream and Git history; it no longer requires every
   superseded body to remain in the default working-tree projection forever.
6. Developers start with SPEC/annexes → ADR 0069–0086 → the active board. Historical bodies are
   consulted only for archaeology through the recovery commit.

**Bound falsifier.** The Markdown-link and stale-path checks find no live link to a removed body;
`INDEX.md` contains every removed identifier and the recovery commit; no file below 0069 or in the
ADR-M0 namespace remains under `docs/02_decisions/`; active ADRs 0069–0087 remain indexed.

**Alternatives rejected.** Keeping all bodies in the active directory; deleting history without a
recovery commit; renumbering active ADRs; copying historical prose into SPEC; or maintaining a
second archive directory that remains in normal retrieval scope.

**Reversal condition.** Git recovery becomes unavailable, an audit obligation requires selected
historical bodies in release artifacts, or a removed record is proven to contain unique current law
not represented by the Clean Triad. Restore only the proven records through a newer ADR.

**Owner · status.** Engineering Director / CIO · accepted · 2026-08-21
