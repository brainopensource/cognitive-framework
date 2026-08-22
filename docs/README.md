---
id: docs-root-index
class: navigation
authority: descriptive
canonical_for:
  - documentation-precedence-map
  - role-based-reading-paths
status: living
owner: documentation-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Vanguard / AETHER Documentation Index

> **Status:** Living documentation precedence ladder, tier catalog, and progressive reading paths for Vanguard / AETHER v0.6.1 Foundation.

---

## 1. Documentation Precedence & Authority Tiers

All repository documentation follows a strict precedence hierarchy. Only Tiers 1, 2, and 3 authorize implementation work. Tiers 4 and 5 are descriptive and advisory.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                             1. THE LAW (WHAT)                            │
│  docs/SPEC.md (+ docs/04_annex/) — Pure RFC-2119 Normative Specification │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ governs
┌────────────────────────────────────▼─────────────────────────────────────┐
│                          2. THE DECISIONS (WHY)                          │
│  docs/05_adr/ — Immutable, append-only Architecture Decision Records     │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ directs
┌────────────────────────────────────▼─────────────────────────────────────┐
│                        3. THE EXECUTION (HOW & NOW)                      │
│  docs/03_sprints/sprint_active.md — Single living board & milestone ladder│
└──────────────────────────────────────────────────────────────────────────┘
```

| Tier | Directory / File | Authority | Role & Contents |
|---|---|---|---|
| **Tier 1 (Law)** | [`SPEC.md`](SPEC.md) · [`04_annex/`](04_annex/) | **Normative** | RFC-2119 normative law, invariants, formal contracts, and state machines. |
| **Tier 2 (Decisions)** | [`05_adr/`](05_adr/) | **Binding Decision** | Accepted ADRs (`0069`–`0086`), historical decisions summary, and the [Canonical RF Allocation Register](05_adr/INDEX.md#canonical-rf-falsifier-allocation-register). |
| **Tier 3 (Execution)** | [`03_sprints/sprint_active.md`](03_sprints/sprint_active.md) · [`02_roadmap/`](02_roadmap/) | **Execution** | Active sprint tasks, assigned files, exit gates, named falsifiers, and macro milestones (`milestones.md`). |
| **Tier 4 (Architecture)** | [`00_overview/SYSTEM_OVERVIEW.md`](00_overview/SYSTEM_OVERVIEW.md) | **Descriptive** | System topology, component flows, A-B-C-D operating foundation, and verified as-built facts. |
| **Tier 5 (Archive & Reference)** | [`06_references/`](06_references/) · [`07_reviews/`](07_reviews/) | **Advisory / Frozen** | Historical research, proposals (001–008), forensic reviews, and design provenance. Non-authoritative. |

---

## 2. Progressive Role-Based Reading Paths

### 👤 Newcomer / Contributor
1. [`README.md`](../README.md) — Mission, architecture summary, quick start commands.
2. [`00_overview/SYSTEM_OVERVIEW.md`](00_overview/SYSTEM_OVERVIEW.md) — System concepts, Three-Plane model, and component layout.
3. [`03_sprints/sprint_active.md`](03_sprints/sprint_active.md) — Current sprint focus and active gates.

### 💻 Feature Developer
1. [`README.md`](../README.md) — Overview and development setup.
2. [`03_sprints/sprint_active.md`](03_sprints/sprint_active.md) — Find your allocated task, file ownership boundary, and red falsifier test.
3. Governing [`SPEC.md`](SPEC.md) clause & [`05_adr/`](05_adr/) record — Review the normative requirements.
4. Named test file under `test/` — Confirm red-to-green proof obligation.

### 🛡️ Security & Trust Reviewer
1. [`04_annex/KERNEL.md`](04_annex/KERNEL.md) — Kernel invariants, S0–S12 dispatch pipeline, capability attenuation.
2. [`04_annex/MEASUREMENT.md`](04_annex/MEASUREMENT.md) — Measurement contracts, signed verdicts, and hash chains.
3. [`05_adr/INDEX.md`](05_adr/INDEX.md) — Review security ADRs (`0071`, `0072`, `0074`, `0076`, `0079`).
4. `test/kernel/` and `test/security/` — Security falsifier assertions.

### 📐 Architect
1. [`docs/README.md`](README.md) — This document.
2. [`00_overview/SYSTEM_OVERVIEW.md`](00_overview/SYSTEM_OVERVIEW.md) — Complete system topology and plane interactions.
3. [`SPEC.md`](SPEC.md) — Full normative specification.
4. [`05_adr/INDEX.md`](05_adr/INDEX.md) — Architecture decision catalog (`0069`–`0086`).
5. [`02_roadmap/milestones.md`](02_roadmap/milestones.md) — Macro gate ladder (M-0 through M-10).

### 🔍 Forensic / Incident Investigator
1. [`07_reviews/ARCHIVE.md`](07_reviews/ARCHIVE.md) — Archive index and frozen provenance notes.
2. [`07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/VANGUARD_V060_FORENSIC_DISCOVERY.md`](07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/VANGUARD_V060_FORENSIC_DISCOVERY.md) — Original forensic analysis and defect catalog.
3. [`05_adr/INDEX.md`](05_adr/INDEX.md) — History and resolution mapping (ADR-0086 recovery commit: `5b9966c`).

### 🤖 AI Coding Agent
1. [`AGENTS.md`](../AGENTS.md) — Single tool-neutral operating contract and anti-sprawl rules.
2. [`03_sprints/sprint_active.md`](03_sprints/sprint_active.md) — Active milestone, file ownership zones, merge order, and named falsifier.
3. Relevant [`SPEC.md`](SPEC.md) clause / [`05_adr/`](05_adr/) decision.
4. Verify using linters: `check_boundaries.py`, `check_tcb_budget.py`, `check_falsifier_ids.py`, `check_markdown_links.py`.
