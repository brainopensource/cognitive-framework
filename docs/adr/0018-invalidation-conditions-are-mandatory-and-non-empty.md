---
adr: 0018
title: "Invalidation conditions are mandatory and non-empty"
status: accepted
source_section: "3. Adjudications between the two lineages"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0018: Invalidation conditions are mandatory and non-empty

**Reasoning.** A claim that cannot state what would refute it is not knowledge. Empty arrays fail at parse (`04 [INV-1]`)

**Reversal condition.** Never — this is the operational form of falsifiability

**Owner · status.** Tech Lead · accepted
