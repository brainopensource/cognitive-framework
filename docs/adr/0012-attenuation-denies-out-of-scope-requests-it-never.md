---
adr: 0012
title: "Attenuation denies out-of-scope requests; it never silently intersects"
status: accepted
source_section: "3. Adjudications between the two lineages"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0012: Attenuation denies out-of-scope requests; it never silently intersects

**Reasoning.** Repeated over-broad requests are the strongest intrusion signal the system produces, and silent narrowing discards it by design

**Reversal condition.** Denial noise proves unmanageable, which would be a policy-authoring defect, not an argument for silence

**Owner · status.** Tech Lead · accepted
