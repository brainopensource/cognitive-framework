---
adr: 0029
title: "Read-only mounts protect the evaluator"
status: accepted
source_section: "4. Corrections"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0029: Read-only mounts protect the evaluator

**Reasoning.** Necessary, not sufficient: a candidate can add a **new** file that shadows the grader, invisible to a tracked-file diff

**Evidence / bound test / links.** `06 §4.3`, `MF-16`

**Reversal condition.** 

**Owner · status.** Tech Lead · accepted
