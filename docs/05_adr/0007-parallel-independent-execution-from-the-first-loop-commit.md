---
adr: 0007
title: "Parallel independent execution from the first loop commit"
status: deferred (honoured, D-38)
source_section: "2. Foundational decisions"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0007: Parallel independent execution from the first loop commit

**Reversal condition.** Measured latency parity on real tasks, which falsifies `02 [C-04]`

**Owner · status.** Tech Lead · deferred (honoured, D-38)

**Note (Foundation Lock, ADR-M0-07):** independence-group parallelism stays deferred in v0.5.0; SPEC I-11 makes the scheduler sequential until a measured consumer exists (honours drift D-38).
