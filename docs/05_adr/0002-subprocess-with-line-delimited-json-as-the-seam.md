---
adr: 0002
title: "Subprocess with line-delimited JSON as the seam to systems components"
status: accepted
source_section: "2. Foundational decisions"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0002: Subprocess with line-delimited JSON as the seam to systems components

**Reversal condition.** A measured hot path exceeds thousands of calls per second, justifying an in-process binding

**Owner · status.** Tech Lead · accepted
