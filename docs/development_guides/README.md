# Vanguard Development Governance & Leadership Prompts

**Active Integration Branch:** `sprints7-8/integration`  
**Current Milestone:** Phase 3 (Manifest Engine, Reconstruction Packs & Measurement Laboratory — Sprints 7 & 8)  
**Latest Merged Baseline:** Phase 2 closed at tag `v0.4.1-beta` (Sprint 6B)

---

## 1. Leadership Directives & Guidelines

| Directive | Target Audience | Scope & Purpose |
|---|---|---|
| [`sprints7_8_developer_onboarding_guide.md`](sprints7_8_developer_onboarding_guide.md) | All Engineers | **ACTIVE:** Phase 3 Architecture, emergent depth vs. class bloat, LAM/LAR testing workflows |
| [`../agile/sprint7_8/sprint7_8_directive_and_playbook.md`](../agile/sprint7_8/sprint7_8_directive_and_playbook.md) | Lead + Architect + Devs | **ACTIVE:** Executive Directive & Playbook for Sprints 7 & 8 |
| [`../agile/sprint7_8/lane-a-manifests-and-packs.md`](../agile/sprint7_8/lane-a-manifests-and-packs.md) | Dev A (Lane A) | **ACTIVE:** Manifest Engine & Pure-Data Reconstruction Packs specification |
| [`../agile/sprint7_8/lane-b-measurement-lab.md`](../agile/sprint7_8/lane-b-measurement-lab.md) | Dev B (Lane B) | **ACTIVE:** Measurement Laboratory CLI & Control Bench specification |
| [`guidelines_phase_2.md`](guidelines_phase_2.md) | Leadership Archive | Phase 2 (Sprints 5 & 6) structure — **EXECUTED & MERGED** |
| [`guidelines_phase_1_.md`](guidelines_phase_1_.md) | Leadership Archive | Phase 1 (Sprints 3 & 4) structure — **EXECUTED & MERGED** |
| [`guidelines_phase_0.md`](guidelines_phase_0.md) | Leadership Archive | Phase 0 (Sprint 0 & 1) baseline — **EXECUTED & MERGED** |

---

## 2. Developer Lanes & Packets

For Phase 3 (Sprints 7 & 8), developers work in two focused parallel lanes:
* **Lane A (Manifest Engine & Reconstruction Packs):**
  - Directive: `docs/agile/sprint7_8/lane-a-manifests-and-packs.md`
  - Targets: `vanguard/packages/agency/manifests/` (`loader.py`, `discovery.py`, `vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-code-swe-mini`)
* **Lane B (Measurement Laboratory & Control Bench):**
  - Directive: `docs/agile/sprint7_8/lane-b-measurement-lab.md`
  - Targets: `vanguard/packages/runtime/coordination.py`, `vanguard/packages/agency/manifests/vg-shell-only/`, `lab/` (`bench.py`, `diff.py`, `build.py`)

All PRs must maintain zero microkernel mutations in `vanguard/packages/kernel/` and pass all CI boundary checks.

