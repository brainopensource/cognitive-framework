---
adr: 0068
title: "**`EvidenceClaim` optional hedge fields `supportCount`, `lastCorroboratedAt`, `protectionClass`.** W"
status: accepted
source_section: "12. Phase 3 authorization, language ratification and gate status"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0068: **`EvidenceClaim` optional hedge fields `supportCount`, `lastCorroboratedAt`, `protectionClass`.** Writer schema names them; defaults omit them so historical canonical bytes hold. Readers already preserve unknown properties (`T1.13`). The fields are recorded, not consumed: they must not move staleness or validity (`T4.11`)

**Context.** `S8-A-05` carried the fields on the domain type and withheld them from `to_wire()` because `additionalProperties:false` would reject them. That withholding is now reversed

**Alternative considered (and rejected).** Keep withholding forever; or make the fields required (breaks the corpus)

**Evidence / bound test / links.** `schemas/v4/evidence-claim.schema.json`; `schemas/v4/vectors/evidence-claim/valid/hedge-fields.json`; `vanguard/packages/domain/evidence/claim.py`; `test/runtime/test_claim_domain_type.py`

**Reversal condition.** A later format lock that consumes the fields for promotion

**Owner · status.** Tech Lead + Project Lead · accepted · 2026-08-17 · accepted
