---
adr: 0025
title: "A dying process emits a terminal event"
status: accepted
source_section: "4. Corrections"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0025: A dying process emits a terminal event

**Reasoning.** A killed process emits nothing. Satisfiable only against a graceful-shutdown mock, and untestable against the real failure

**Evidence / bound test / links.** `03 §9`, `MF-21`

**Reversal condition.** 

**Owner · status.** Tech Lead · accepted
