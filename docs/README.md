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
last_verified: 2026-08-23
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
| **Tier 6 (Archive)** | [`06_references/`](06_references/) · [`07_reviews/`](07_reviews/) · [`08_diagrams/`](08_diagrams/) · [`09_tools/`](09_tools/) | **Advisory / Frozen** | Historical research, proposals (001–008), visual models, tooling notes, forensic reviews, and design provenance. Non-authoritative. |

---

## 2. Modular Subsystem Directory

| Subsystem Directory | Focus & Contents | Maturity |
|---|---|---|
| 📐 [`architecture/`](architecture/) | C4 Context, Containers, Components, Sequences, State Machines, Glossary, and Traceability Matrix | Per-section maturity; future targets explicitly labelled |
| 📜 [`contracts/`](contracts/) | Wire schemas for Envelopes (`mhf.event/1`), Trajectories (`mhf.trajectory/1`), Manifests, Verdicts, Selectors | Mixed: current schemas plus RF-23/M-3 targets |
| 🔌 [`protocols/`](protocols/) | Verified references for kernel dependencies, model, sandbox, evaluator, stores, and five SPIs | `AS_BUILT` |
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
2. [`engineering/context_bundles.md`](engineering/context_bundles.md) — Select the minimum starting bundle, then follow its authoritative links.
3. Governing [`SPEC.md`](SPEC.md) clause & [`05_adr/`](05_adr/) decision.
4. Named test file under `test/` — Confirm red-to-green proof obligation.

### 🛡️ Security & Trust Reviewer
1. [`04_annex/KERNEL.md`](04_annex/KERNEL.md) — Kernel invariants, S0–S12 dispatch pipeline, capability attenuation.
2. [`architecture/sequences.md`](architecture/sequences.md) — S0–S12 execution timeline and signed verdict flow.
3. [`engineering/security_and_tcb.md`](engineering/security_and_tcb.md) — TCB budget ($\le 1438$ LOC) and domain blindness compliance.

### 📐 Architect
1. [`docs/README.md`](README.md) — This document.
2. [`architecture/c4_component.md`](architecture/c4_component.md) — Hexagonal production lattice.
3. [`architecture/traceability_matrix.md`](architecture/traceability_matrix.md) — Maturity-labelled concept-to-evidence map.
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
3. [`engineering/context_bundles.md`](engineering/context_bundles.md) — Ingest the task-specific starting bundle; do not assume an unmeasured token count.
4. Run verification linters: `check_boundaries.py`, `check_tcb_budget.py`, `check_doc_metadata.py`, `check_falsifier_ids.py`, `check_markdown_links.py`.

---

## 4. Find Information by Development Task

Start with the active board, then load only the row relevant to the change. A descriptive module
explains the current system but never overrides its governing SPEC clause or ADR.

| Development question | Start here | Then inspect | Proof of completion |
|---|---|---|---|
| What should be implemented now? | [`sprint_active.md`](03_sprints/sprint_active.md) | Assigned ADR and files named by the task | Bound `RF-*` test and active-board gate |
| What ships in a later release? | [`milestones.md`](02_roadmap/milestones.md) | Relevant accepted ADR | Objective milestone exit gate; backlog is not authorization |
| How does the runtime fit together? | [`architecture/README.md`](architecture/README.md) | C4 view, sequence, or state machine for the affected boundary | [`traceability_matrix.md`](architecture/traceability_matrix.md) |
| What is the exact wire/data shape? | [`contracts/README.md`](contracts/README.md) | Generated schema and producer/reader named in that page | Contract test plus schema/code generation check |
| What can a boundary implementation call? | [`protocols/README.md`](protocols/README.md) | Exact port source and implementing adapter | Port/contract tests and boundary linter |
| How do I change kernel/security behavior? | [`KERNEL.md`](04_annex/KERNEL.md) | Kernel protocol, dispatch sequence, security guide | Security test, boundary/domain-blindness checks, TCB budget |
| How do I add an adapter or pack? | [`engineering/README.md`](engineering/README.md) | Adapter/pack guide and minimum context bundle | Hermetic tests; a new pack requires zero domain/kernel diff |
| Is a cognitive or retrieval idea implemented? | [`theory/README.md`](theory/README.md) | Maturity label and governing roadmap/ADR | Only the named future milestone may promote it to active work |

## 5. Where Information Belongs

| Information type | Sole durable owner | Rule |
|---|---|---|
| Normative behavior or invariant | [`SPEC.md`](SPEC.md) or [`04_annex/`](04_annex/) | Use RFC-2119 language only here |
| Architectural decision and reversal condition | New append-only ADR under [`05_adr/`](05_adr/) | Never silently rewrite an accepted decision |
| Current work, ownership, and readiness | [`sprint_active.md`](03_sprints/sprint_active.md) | Keep only the active wave |
| Future sequencing and backlog | [`milestones.md`](02_roadmap/milestones.md) | Does not authorize implementation before dependencies open |
| As-built explanation and navigation | Existing module under `architecture/`, `contracts/`, `protocols/`, or `engineering/` | Link to law/schema/code; do not duplicate canonical tables |
| Historical source or proposal | Frozen archive under `06_references/`–`09_tools/` | Preserve original language and content; never cite as execution authority |

Before adding a document, use [`engineering/documentation.md`](engineering/documentation.md). The
default is to update an existing owner rather than create another summary.
