---
adr: 0021
title: "'Every effect passes a mediating layer'"
status: corrected
source_section: "4. Corrections"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0021: "Every effect passes a mediating layer"

**Reasoning.** A logical mediator in the host language is not a containment boundary. Subprocess execution grants execution *inside an already-limited environment*; nothing intercepts syscalls

**Evidence / bound test / links.** `05 [K-01]`, `05 [K-22]`, `MF-11`

**Reversal condition.** 

**Owner · status.** Tech Lead · corrected
