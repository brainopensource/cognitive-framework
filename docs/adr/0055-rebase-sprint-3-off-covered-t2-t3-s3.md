---
adr: 0055
title: "Rebase Sprint 3 off covered T2/T3. S3 = port bundles + first cassette episode slice + process engine"
status: accepted
source_section: "10. Sprint 0–2 closure and Sprint 3–4 structure"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0055: Rebase Sprint 3 off covered T2/T3. S3 = port bundles + first cassette episode slice + process engine. S4a = finish episode + no-model trajectory. S4b = perimeter + S4 exit delete of `spike/`/`slice/`. Process engine is S3 not S4b so S4b is not XL

**Context.** GTS-13C Part II still listed T2.6–T3.8 as S3 after `REQ-KRN-002` and `REQ-LEDGER-002` were covered

**Alternative considered (and rejected).** Keep Part II literally, or pack process+perimeter+trajectory into S4

**Evidence / bound test / links.** This register; `docs/sprint3/`; `docs/sprint4/`

**Reversal condition.** New evidence that process resume cannot be tested without the full trust-spine

**Owner · status.** Tech Lead + Project Lead · accepted · 2026-08-15 · accepted
