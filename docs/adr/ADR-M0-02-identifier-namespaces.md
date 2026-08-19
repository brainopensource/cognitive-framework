---
adr: M0-02
title: "Identifier namespaces"
status: accepted
---

# ADR-M0-02: Identifier namespaces

**Decision.** MHF keeps exactly three identifier namespaces, each with a single owner:
`I-*` (invariants, owned by `docs/SPEC.md`), `ADR-*` (decisions, owned by `docs/adr/`), and
`S-M*-{A,B}-*` (sprint tasks, owned by `docs/03_sprints/`). No fourth namespace opens without an ADR.

**Context.** `docs/01_specs/backend/00_vanguard_registry_v040.md` §5 ran a document-precedence
machine (status lifecycle, word budgets, PR-* precedence rules, supersession maps) to adjudicate
between multiple normative documents. With one normative document (`docs/SPEC.md`), precedence is
the identity function — the machine dissolves by construction, but the namespace discipline it
enforced is worth keeping in miniature.

**Reversal condition.** A capability that genuinely needs a fourth namespace forces a design
review and an ADR naming it — never a silent PR.
