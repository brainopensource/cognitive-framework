---
adr: 0049
title: "Shipped tools begin as typed `read/search/patch/test`; shell is selector-scoped and privileged, whil"
status: accepted
source_section: "7. Sprint 0 adoption decisions"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0049: Shipped tools begin as typed `read/search/patch/test`; shell is selector-scoped and privileged, while `vg-shell-only` remains the permanent experimental baseline

**Evidence / bound test / links.** Affects adapters, manifests and kernel policy; verify typed-schema, allowlist and undeletable-manifest tests; `REQ-HAR-*`

**Reversal condition.** Paired evidence shows typed tools cost more than they return; the control manifest remains for comparison

**Owner · status.** Tech Lead + Project Lead · `proposed` · 2026-08-14 · accepted
