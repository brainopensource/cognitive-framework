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
| **Tier 4 (Architecture)** | [`00_overview/SYSTEM_OVERVIEW.md`](00_overview/SYSTEM_OVERVIEW.md) · [`architecture/`](architecture/) | **Descriptive** | System topology, C4 models, sequences, state machines, and verified as-built facts. |
| **Tier 5 (Reference & Theory)** | [`contracts/`](contracts/) · [`protocols/`](protocols/) · [`theory/`](theory/) · [`engineering/`](engineering/) | **Descriptive / How-To** | Wire contracts, port protocols, cognitive equations, and contributor how-to guides. |
| **Tier 6 (Archive)** | [`06_references/`](06_references/) · [`07_reviews/`](07_reviews/) | **Advisory / Frozen** | Historical research, proposals (001–008), forensic reviews, and design provenance. Non-authoritative. |

---

## 2. Modular Subsystem Directory

| Subsystem Directory | Focus & Contents | Maturity |
|---|---|---|
| 📐 [`architecture/`](architecture/) | C4 Context, Containers, Components, Sequences, State Machines, Glossary, and Traceability Matrix | `AS_BUILT` |
| 📜 [`contracts/`](contracts/) | Wire schemas for Envelopes (`mhf.event/1`), Trajectories (`mhf.trajectory/1`), Manifests, Verdicts, Selectors | `AS_BUILT` |
| 🔌 [`protocols/`](protocols/) | Hexagonal Port Protocols (`KernelPort`, `ModelPort`, `SandboxPort`, `EvaluatorPort`, `EventStorePort`, `SPI`) | `AS_BUILT` |
| 🧠 [`theory/`](theory/) | Active Inference ($\mathcal{F}/\mathcal{G}$), 6D Resource Tensor $\mathbf{R}$, Trajectory Credit Assignment, DPO Harvesting, McNemar Promotion | `RESEARCH` / `AS_BUILT` |
| 🛠️ [`engineering/`](engineering/) | Contributor Workflow, Testing & Red Falsifiers, TCB Security, Adding Adapters, Adding Packs, Context Bundles | `AS_BUILT` |

---

## 3. Progressive Role-Based Reading Paths

### 👤 Newcomer / Contributor
1. [`README.md`](../README.md) — Mission, architecture summary, quick start commands.
2. [`architecture/c4_context.md`](architecture/c4_context.md) — System boundaries and actors.
3. [`engineering/development.md`](engineering/development.md) — Setup and daily test commands.

### 💻 Feature Developer
1. [`03_sprints/sprint_active.md`](03_sprints/sprint_active.md) — Find assigned task, file ownership boundary, and red falsifier test.
2. [`engineering/context_bundles.md`](engineering/context_bundles.md) — Load the exact sub-1k token context bundle for your subsystem.
3. Governing [`SPEC.md`](SPEC.md) clause & [`05_adr/`](05_adr/) decision.
4. Named test file under `test/` — Confirm red-to-green proof obligation.

### 🛡️ Security & Trust Reviewer
1. [`04_annex/KERNEL.md`](04_annex/KERNEL.md) — Kernel invariants, S0–S12 dispatch pipeline, capability attenuation.
2. [`architecture/sequences.md`](architecture/sequences.md) — S0–S12 execution timeline and signed verdict flow.
3. [`engineering/security_and_tcb.md`](engineering/security_and_tcb.md) — TCB budget ($\le 1438$ LOC) and domain blindness compliance.

### 📐 Architect
1. [`docs/README.md`](README.md) — This document.
2. [`architecture/c4_component.md`](architecture/c4_component.md) — Hexagonal production lattice.
3. [`architecture/traceability_matrix.md`](architecture/traceability_matrix.md) — Complete concept-to-test mapping.
4. [`05_adr/INDEX.md`](05_adr/INDEX.md) — Architecture decision catalog (`0069`–`0086`).
5. [`02_roadmap/milestones.md`](02_roadmap/milestones.md) — Macro gate ladder (M-0 through M-10).

### 🔬 Cognitive Systems Researcher
1. [`theory/README.md`](theory/README.md) — Theory index and maturity ratings.
2. [`theory/active_inference.md`](theory/active_inference.md) — Free energy minimization formulations.
3. [`theory/economic_resources.md`](theory/economic_resources.md) — 6D resource tensor algebra.
4. [`theory/preference_and_promotion.md`](theory/preference_and_promotion.md) — DPO harvesting and McNemar promotion.

### 🤖 AI Coding Agent
1. [`AGENTS.md`](../AGENTS.md) — Operating contract and anti-sprawl rules.
2. [`03_sprints/sprint_active.md`](03_sprints/sprint_active.md) — Active wave tasks, assigned files, and falsifiers.
3. [`engineering/context_bundles.md`](engineering/context_bundles.md) — Ingest the specific ~500-token context bundle.
4. Run verification linters: `check_boundaries.py`, `check_tcb_budget.py`, `check_doc_metadata.py`, `check_falsifier_ids.py`, `check_markdown_links.py`.
