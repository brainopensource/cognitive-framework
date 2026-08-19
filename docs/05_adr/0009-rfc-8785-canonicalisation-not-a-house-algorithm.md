---
adr: 0009
title: "RFC 8785 canonicalisation, not a house algorithm"
status: accepted
source_section: "3. Adjudications between the two lineages"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0009: RFC 8785 canonicalisation, not a house algorithm

**Reasoning.** A hand-rolled sort-and-number specification is a defect surface with no upside; a divergent digest breaks loop detection **silently**

**Reversal condition.** The standard proves inadequate for a required type, documented with the specific failing case

**Owner · status.** Tech Lead · accepted
