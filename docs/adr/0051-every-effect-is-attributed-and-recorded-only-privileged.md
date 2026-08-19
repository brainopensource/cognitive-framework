---
adr: 0051
title: "Every effect is attributed and recorded; only `privileged` sinks require descriptor-bound capability"
status: accepted
source_section: "7. Sprint 0 adoption decisions"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0051: Every effect is attributed and recorded; only `privileged` sinks require descriptor-bound capability mediation

**Evidence / bound test / links.** Affects schema, kernel, ledger and adapters; verify descriptor-substitution, misclassification and receipt tests; `REQ-KRN-*`

**Reversal condition.** Evidence shows non-privileged recording costs exceed attribution value, or observation enables escalation

**Owner · status.** Tech Lead + Project Lead · `proposed` · 2026-08-14 · accepted
