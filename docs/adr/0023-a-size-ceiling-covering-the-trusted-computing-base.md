---
adr: 0023
title: "A size ceiling covering the trusted computing base"
status: accepted
source_section: "4. Corrections"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0023: A size ceiling covering the trusted computing base

**Reasoning.** The ceiling applies to the policy kernel; the TCB includes the operating system, runtimes, stores and build pipeline. Concealing a dependency does not remove it

**Evidence / bound test / links.** `05 [K-02]`, `AT-08`

**Reversal condition.** 

**Owner · status.** Tech Lead · accepted
