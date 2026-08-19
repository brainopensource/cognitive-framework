---
adr: 0047
title: "`spike/` and `slice/` are disposable consumers only, may never be imported, and must be deleted at t"
status: accepted
source_section: "7. Sprint 0 adoption decisions"
migrated_from: docs/01_specs/backend/09_vanguard_decision_register_v040.md
---

# ADR-0047: `spike/` and `slice/` are disposable consumers only, may never be imported, and must be deleted at the S4 gate

**Evidence / bound test / links.** Affects dependency CI, `spike/`, `slice/`; verify `TEST-ARCH-002` and S4 absence check; `REQ-ARCH-002`

**Reversal condition.** Replace the experiment with a separately reviewed production adapter behind a port; disposable code is still deleted

**Owner · status.** Tech Lead + Project Lead · `proposed` · 2026-08-14 · accepted
