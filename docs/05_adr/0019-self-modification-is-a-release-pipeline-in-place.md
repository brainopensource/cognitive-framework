---
adr: 0019
title: "Self-modification is a release pipeline; in-place modification is prohibited"
status: accepted
source_section: "3. Adjudications between the two lineages"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0019: Self-modification is a release pipeline; in-place modification is prohibited

**Reasoning.** A process that rewrites its running components cannot verify the result with the components it just rewrote, and the failure is undetectable from inside

**Reversal condition.** Never within this programme's assumptions

**Owner · status.** Tech Lead · accepted
