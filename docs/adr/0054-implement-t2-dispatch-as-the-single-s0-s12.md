---
adr: 0054
title: "Implement T2 dispatch as the single S0–S12 path, with durable intent before execution, descriptor-bo"
status: accepted
source_section: "9. Kernel implementation decisions"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0054: Implement T2 dispatch as the single S0–S12 path, with durable intent before execution, descriptor-bound grants for privileged sinks, and recording for every sink class

**Context.** T2.1–T2.10 entered implementation scope and required a reconstructable choice at the TCB boundary

**Alternative considered (and rejected).** A second lightweight path for pure/observation effects was rejected because it would make complete attribution conditional and let classification bypass recording

**Evidence / bound test / links.** `vanguard/packages/kernel/`, `MF-KRN-008..011`, `TEST-KERNEL-001..003`; the initial measured kernel baseline is 1,307 logical source lines with a 131-line review alarm

**Reversal condition.** A mechanically verified design preserves identical durable attribution and mediation semantics with a smaller trusted path; growth beyond the alarm requires a superseding ADR or reviewed baseline

**Owner · status.** Tech Lead · accepted · 2026-08-15 · accepted
