# Vanguard GTS — Documentation Index & Governance Map

**Repository:** `Aether-D-System` (Vanguard General Task Solver)  
**Current Phase:** Phase 2 closure-in-progress (Sprint 6B)  
**Active Integration Branch:** `sprint5-6/integration`  
**Latest Release Tag:** `v0.4.0-sprint4`  
**Release status:** `NO-GO` — gates R0–R10 are open until independently signed receipts exist.

---

## 1. Documentation Hierarchy & Authority Chain

Canonical live layout (S6B-GOV-001). Pre-move documentation directories are absent; tools resolve the live map through `tools/repo_paths.py`.

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                               DOCUMENTATION AUTHORITY MODEL                              │
├───────┬───────────────────────────────┬──────────────────────────────────────────────────┤
│ Rank  │ Directory / Artifact          │ Authority & Purpose                              │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 1     │ docs/main_v4/09_vanguard_     │ The Decision Register (Append-only ADRs).        │
│       │ decision_register_v040.md     │ Absolute source of truth for architectural locks.│
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 2     │ docs/main_v4/                 │ Normative System Specifications (Contracts,      │
│       │                               │ Kernel, Wire Schemas, Execution Planes, Security)│
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 3     │ docs/agile/sprint0/active-    │ The Active MVP Contract. The ONLY merge gate     │
│       │ mvp-contract.json             │ for PRs into main (100% test evidence required). │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 4     │ docs/agile/sprint0/system-    │ Package boundaries, isolation topology, and      │
│       │ architecture-icd.md           │ activated port signatures.                       │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 5     │ docs/agile/sprint0/           │ Must-fail suite, adversarial tests, and A/A      │
│       │ verification-threat-          │ statistical measurement protocols.               │
│       │ evaluation-plan.md            │                                                  │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 6     │ docs/main_v4/13_C_gts_mvp_    │ Living Program Document: milestone rationale,    │
│       │ program_and_engineering_plan  │ sequence map, and design motivations.            │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 7     │ docs/development_guides/      │ Active specification for the hexagonal client,   │
│       │ cli_tui_architecture.md       │ RuntimeClient port, and Ink TUI screens.         │
├───────┼───────────────────────────────┼──────────────────────────────────────────────────┤
│ 8     │ docs/reviews/todo/            │ Master Phase Review, audits, roadmap & tracking. │
│       │ phases_review.md              │                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

Path resolution for tools and CI is `tools/repo_paths.py`. Commands must be run from any working directory; they resolve the repository root themselves.

---

## 2. Directory Map

### `docs/main_v4/` — Core Specifications (Normative)

- [00_vanguard_registry_v040.md](main_v4/00_vanguard_registry_v040.md) — Document registry and namespace allocations.
- [01_vanguard_engineering_handbook_v040.md](main_v4/01_vanguard_engineering_handbook_v040.md) — Coding standards, typing rules, invariant enforcement.
- [02_vanguard_charter_claims_and_non_claims_v040.md](main_v4/02_vanguard_charter_claims_and_non_claims_v040.md) — System boundaries and non-claims.
- [03_vanguard_architecture_planes_and_execution_model_v040.md](main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md) — Execution planes and episode loop.
- [04_vanguard_core_contracts_and_wire_schema_v040.md](main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md) — Wire schemas, envelopes, and receipts.
- [05_vanguard_kernel_capabilities_and_security_v040.md](main_v4/05_vanguard_kernel_capabilities_and_security_v040.md) — Capability mediation and attenuation.
- [06_vanguard_competence_memory_and_evidence_v040.md](main_v4/06_vanguard_competence_memory_and_evidence_v040.md) — Claims and evaluator protocol.
- [07_vanguard_loop_engineering_and_measurement_v040.md](main_v4/07_vanguard_loop_engineering_and_measurement_v040.md) — Measurement and A/A testing doctrine.
- [09_vanguard_decision_register_v040.md](main_v4/09_vanguard_decision_register_v040.md) — **Authoritative ADRs**.
- [10_vanguard_deferred_and_rejected_register_v040.md](main_v4/10_vanguard_deferred_and_rejected_register_v040.md) — Deferred and rejected proposals.
- [13_C_gts_mvp_program_and_engineering_plan.md](main_v4/13_C_gts_mvp_program_and_engineering_plan.md) — Living program plan (GTS-13C).

### `docs/agile/` — Sprint records and contracts

- [sprint0/active-mvp-contract.json](agile/sprint0/active-mvp-contract.json) — Gating contract (`requirement -> test_id -> status`).
- [sprint0/system-architecture-icd.md](agile/sprint0/system-architecture-icd.md) — Package dependency lattice and port interfaces.
- [sprint0/verification-threat-evaluation-plan.md](agile/sprint0/verification-threat-evaluation-plan.md) — Must-fail catalogue and threat models.
- [sprint0/baseline-manifest.json](agile/sprint0/baseline-manifest.json) — Local integrity manifest.
- [sprint0/schema-archaeology/](agile/sprint0/schema-archaeology/) — Field inventory and manual bug traces from Sprint 0.
- [sprint1/](agile/sprint1/) through [sprint6/](agile/sprint6/) — Historical sprint records.
- [sprint6B/backlog.md](agile/sprint6B/backlog.md) — Current Sprint 6B backlog (`PROPOSED / RELEASE NO-GO`).

### `docs/development_guides/` — Development architecture and planning

- [cli_tui_architecture.md](development_guides/cli_tui_architecture.md) — Hexagonal CLI architecture and `RuntimeClient` contract.
- [dev_prompts/](development_guides/dev_prompts/) — Lane developer prompts.

### `docs/reviews/` — Architectural reviews and audits

- [todo/phases_review.md](reviews/todo/phases_review.md) — Master multi-phase technical review and gap audit.
- [todo/phases_0-2_review_full_rev2.md](reviews/todo/phases_0-2_review_full_rev2.md) — Rev2 gate meanings.
- [todo/phases_0-2_review_full_rev3.md](reviews/todo/phases_0-2_review_full_rev3.md) — Rev3 implementation findings.
