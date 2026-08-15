# Vanguard Development Governance & Leadership Prompts

**Active Integration Branch:** `sprint5-6/integration`  
**Current Milestone:** Phase 2 (Lightweight Beta MVP — Sprints 5 & 6)  
**Latest Merged Baseline:** Phase 1 closed at tag `v0.4.0-sprint4`

---

## 1. Leadership Directives & Guidelines

| Directive | Target Audience | Scope & Purpose |
|---|---|---|
| [`guidelines_phase_2.md`](guidelines_phase_2.md) | Project Lead + Tech Lead | **ACTIVE:** Phase 2 Architecture, 4-lane developer allocation, polyglot boundaries, anti-drift doctrine |
| [`dev_prompts/prompt_planning_pre_phase_2.md`](dev_prompts/prompt_planning_pre_phase_2.md) | Project Lead + Architect | **ACTIVE:** Master evaluation directive for pre-Phase 2 readiness & SOTA cross-examination |
| [`cli_tui_architecture.md`](cli_tui_architecture.md) | CLI & Client Engineers | **ACTIVE:** Hexagonal CLI architecture and `RuntimeClient` streaming specification |
| `guidelines_phase_1_.md` | Leadership Archive | Phase 1 (Sprints 3 & 4) structure — **EXECUTED & MERGED** |
| `guidelines_phase_0.md` | Leadership Archive | Phase 0 (Sprint 0 & 1) baseline — **EXECUTED & MERGED** |

---

## 2. Developer Lanes & Packets

Developers do not receive leadership governance prompts. For Phase 2 they receive their specific lane packets:
* **Sprint 5 Packets:** `docs/sprint5/sa-packet.md` (Context Compiler), `sb-packet.md` (Judge Isolation), `dc-packet.md` (OpenRouter enhancements), `dd-packet.md` (CLI client alignment).
* **Sprint 6 Packets:** `docs/sprint6/sa-packet.md` (Composition Root & Dogfood), `sb-packet.md` (Approvals), `dc-packet.md` (Telemetry), `dd-packet.md` (Ink TUI Screens).

All PRs must cite an active requirement ID (`REQ-*`) from [`docs/sprint0/active-mvp-contract.json`](../sprint0/active-mvp-contract.json) and maintain 100% test coverage.

