---
adr: 0044
title: "A single trailing emit point"
status: accepted
source_section: "4. Corrections"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0044: A single trailing emit point

**Reasoning.** A crash between dispatch and emit left no record the effect was attempted, making an executed effect invisible rather than undeterminable

**Evidence / bound test / links.** `05 [K-47]`, `MF-36`

**Reversal condition.** 

**Owner · status.** Tech Lead · accepted
