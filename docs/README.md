# Vanguard GTS — Documentation Index & Governance Map

**Repository:** `Aether-D-System` (Vanguard General Task Solver)  
**Current Phase:** Phase 2 (Lightweight Beta MVP — Sprints 5 & 6)  
**Active Integration Branch:** `sprint5-6/integration`  
**Latest Release Tag:** `v0.4.0-sprint4`

---

## 1. Documentation Hierarchy & Authority Chain

To prevent architectural drift, conflicting specifications, and bloat, all project documentation follows an explicit hierarchy:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                               DOCUMENTATION AUTHORITY MODEL                              │
├───────┬───────────────────────────────┬──────────────────────────────────────────────────┤
│ Rank  │ Directory / Artifact          │ Authority & Purpose                              │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 1     │ docs/v4/09_vanguard_decision_ │ The Decision Register (Append-only ADRs).        │
│       │ register_v040.md              │ Absolute source of truth for architectural locks.│
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 2     │ docs/v4/ (v0.4.0 Corpus)      │ Normative System Specifications (Contracts,      │
│       │                               │ Kernel, Wire Schemas, Execution Planes, Security)│
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 3     │ docs/sprint0/active-mvp-      │ The Active MVP Contract. The ONLY merge gate     │
│       │ contract.json                 │ for PRs into main (100% test evidence required). │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 4     │ docs/sprint0/system-          │ Package boundaries, isolation topology, and      │
│       │ architecture-icd.md           │ activated port signatures.                       │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 5     │ docs/sprint0/verification-    │ Must-fail suite, adversarial tests, and A/A      │
│       │ threat-evaluation-plan.md     │ statistical measurement protocols.               │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 6     │ docs/v4/13_C_gts_mvp_program_ │ Living Program Document: milestone rationale,    │
│       │ and_engineering_plan.md       │ sequence map, and design motivations.            │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 7     │ docs/development/cli_tui_     │ Active specification for the hexagonal client,   │
│       │ architecture.md               │ RuntimeClient port, and Ink TUI screens.         │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 8     │ docs/review/todo/             │ Master Phase Review, audits, roadmap & tracking. │
│       │ phases_review.md              │                                                  │
└───────┴───────────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 2. Directory Map

### 📘 `docs/v4/` — Core Specifications (Normative)
The permanent, authoritative specification corpus:
- [`00_vanguard_registry_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/00_vanguard_registry_v040.md) — Document registry and namespace allocations.
- [`01_vanguard_engineering_handbook_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/01_vanguard_engineering_handbook_v040.md) — Coding standards, typing rules, invariant enforcement.
- [`02_vanguard_charter_claims_and_non_claims_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/02_vanguard_charter_claims_and_non_claims_v040.md) — System boundaries and non-claims.
- [`03_vanguard_architecture_planes_and_execution_model_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/03_vanguard_architecture_planes_and_execution_model_v040.md) — Execution planes and episode loop.
- [`04_vanguard_core_contracts_and_wire_schema_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/04_vanguard_core_contracts_and_wire_schema_v040.md) — Wire schemas, envelopes, and receipts.
- [`05_vanguard_kernel_capabilities_and_security_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/05_vanguard_kernel_capabilities_and_security_v040.md) — Capability mediation and attenuation.
- [`06_vanguard_competence_memory_and_evidence_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/06_vanguard_competence_memory_and_evidence_v040.md) — Claims and evaluator protocol.
- [`07_vanguard_loop_engineering_and_measurement_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/07_vanguard_loop_engineering_and_measurement_v040.md) — Measurement and A/A testing doctrine.
- [`09_vanguard_decision_register_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md) — **Authoritative ADRs (0001–0058)**.
- [`10_vanguard_deferred_and_rejected_register_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/10_vanguard_deferred_and_rejected_register_v040.md) — Deferred and rejected proposals.
- [`13_C_gts_mvp_program_and_engineering_plan.md`](file:///home/rocha/Coding/Aether-D-System/docs/v4/13_C_gts_mvp_program_and_engineering_plan.md) — Living program plan (GTS-13C).

### 🏛️ `docs/sprint0/` — Governance Baseline & Contracts
- [`active-mvp-contract.json`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json) — Gating contract (`requirement -> test_id -> status`).
- [`system-architecture-icd.md`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/system-architecture-icd.md) — Package dependency lattice and port interfaces.
- [`verification-threat-evaluation-plan.md`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/verification-threat-evaluation-plan.md) — Must-fail catalogue and threat models.
- [`baseline-manifest.json`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/baseline-manifest.json) — System baseline configuration.
- [`schema-archaeology/`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/schema-archaeology/) — Field inventory and manual bug traces from Sprint 0.

### 📦 `docs/sprint1/` through `docs/sprint4/` — Sprint Records (Historical)
- Preserved historical sprint backlogs, developer packets, and findings:
  - [`docs/sprint1/provider-notes.md`](file:///home/rocha/Coding/Aether-D-System/docs/sprint1/provider-notes.md) — Wire format quirks for LLM providers.
  - [`docs/sprint2/slice-findings.md`](file:///home/rocha/Coding/Aether-D-System/docs/sprint2/slice-findings.md) — Preserved findings from the disposable end-to-end slice.
  - [`docs/sprint2/kernel-tcb-budget.json`](file:///home/rocha/Coding/Aether-D-System/docs/sprint2/kernel-tcb-budget.json) — TCB line-count budget tracker.

### 🛠️ `docs/development/` — Development Architecture & Planning
- [`cli_tui_architecture.md`](file:///home/rocha/Coding/Aether-D-System/docs/development/cli_tui_architecture.md) — Hexagonal CLI architecture and `RuntimeClient` contract.
- [`dev_prompts/prompt_planning_sprint_5-6.md`](file:///home/rocha/Coding/Aether-D-System/docs/development/dev_prompts/prompt_planning_sprint_5-6.md) — Sprint 5–6 planning brief.

### 🔍 `docs/review/` — Architectural Reviews & Audits
- [`todo/phases_review.md`](file:///home/rocha/Coding/Aether-D-System/docs/review/todo/phases_review.md) — **Master Multi-Phase Technical Review & Gap Audit**.
