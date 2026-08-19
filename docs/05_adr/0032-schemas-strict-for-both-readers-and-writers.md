---
adr: 0032
title: "Schemas strict for both readers and writers"
status: accepted
source_section: "4. Corrections"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0032: Schemas strict for both readers and writers

**Reasoning.** `additionalProperties: false` on a reader rejects every future field, contradicting `04 [CT-44]`. Split into generated writer and reader profiles

**Evidence / bound test / links.** `SC-10`, `MF-27`

**Reversal condition.** 

**Owner · status.** Tech Lead · accepted
