---
adr: M0-10
title: "No metaphysical taxonomies"
status: accepted
---

# ADR-M0-10: No metaphysical taxonomies

**Decision.** No document under `docs/` may define a tier system, hierarchy-of-being, or
biological/cosmological mapping as specification content. Metaphors may appear in code comments and
talks; they may never appear as architecture. This is Invariant I-10 ("metaphors ship as comments,
not architecture") given ADR force.

**Context.** `docs/01_specs/backend/12_vanguard_vision_annex_v040.md` diagnosed the failure mode
correctly — "a metaphor in a specification is unfalsifiable" — and built a quarantine that
demonstrably failed: the cosmology escaped into `docs/00_executive/vision.md` v3.0.0 (a 14-tier
"String Theory → Solar Systems" continuum) and the README's 10-level biological dictionary
("Protons = Identity, Neutrons = Ledger, Electrons = Budget"). Both carried zero operational
semantics — no invariant, test, or schema referenced a tier — while imposing a vocabulary tax on
every contributor and creating false layering intuitions the actual import lattice contradicted
(audit AP-1). Quarantine is not a stable equilibrium for narrative; deletion is. README's taxonomy
is removed in this same wave (Step 8).

**Reversal condition.** None. The register entry (`REJ-10` in `docs/05_adr/DEFERRED_REJECTED.md`)
states plainly that nothing reopens it.
