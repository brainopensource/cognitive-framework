---
adr: 0061
title: "Apply Specification v0.4.1 (v4B) patches before Sprint 5: partition M-18 instrument tuple into 4 exp"
status: accepted
source_section: "11. Sprint 3–4 closure and Phase 2 authorization"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0061: Apply Specification v0.4.1 (v4B) patches before Sprint 5: partition M-18 instrument tuple into 4 explicit algebraic subsets (excluding metadata timestamp from equality), formalize dual kernel ingress for `Principal::Episode` vs `Principal::EvidencePlane`, replace F-25 log-only fallback with transactional outbox + recovery reconciliation to `undeterminable`, correct DEF-02 test namespace, annotate DEF-12 supersession by ADR-0057, and qualify expressiveness and operator isolation loss profile claims

**Context.** Cross-examination of v0.4.0 corpus against senior architectural reviews revealed 3 mathematical/formal defects and 2 operational ambiguities that would cause execution friction and experimental invalidity in Phase 2

**Alternative considered (and rejected).** Proceed without patching and address issues ad-hoc during implementation

**Evidence / bound test / links.** `docs/v4/07` M-18, `docs/v4/05` §2.1/F-25, `docs/v4/10` DEF-02/DEF-12, `docs/v4/03` §2.2/§10.3

**Reversal condition.** A formal proof demonstrates original M-18 is physically satisfiable; or a concrete test demonstrates behavioral regression

**Owner · status.** Tech Lead + Project Lead · accepted · 2026-08-15 · accepted
