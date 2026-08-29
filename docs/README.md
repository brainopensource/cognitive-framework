---
id: docs-root-index
class: navigation
authority: descriptive
canonical_for:
  - documentation-precedence-map
  - role-based-reading-paths
status: living
owner: documentation-architect
version: "0.9.0b1"
last_verified: 2026-08-26
read_when:
  - selecting-a-documentation-bundle
  - navigating-the-repository
do_not_read_when:
  - implementing-a-specific-module-after-bundle-selection
subordinate_to: ../VISION.md
supersedes: []
superseded_by: null
---

# Vanguard / AETHER Documentation Index

> **Status:** Living documentation precedence ladder and reading paths for AETHER v0.7+.

---

## 1. Documentation Precedence & Authority Tiers

Highest first. **In a conflict, the higher document wins.**

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                    0. THE VISION (WHAT AETHER IS)                        │
│  VISION.md — constitutional. Identity, ontology, direction. Law Zero.    │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ governs
┌────────────────────────────────────▼─────────────────────────────────────┐
│                             1. THE LAW (RULES)                           │
│  docs/SPEC.md (+ docs/01_law/) — RFC-2119 normative specification        │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ governs
┌────────────────────────────────────▼─────────────────────────────────────┐
│                          2. THE DECISIONS (WHY)                          │
│  docs/02_decisions/ — immutable, append-only ADRs                        │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ directs
┌────────────────────────────────────▼─────────────────────────────────────┐
│              3. CONTRACTS & PROTOCOLS (WIRE REALIZATION)                 │
│  docs/05_contracts/, docs/06_protocols/, schemas/                        │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ scheduled by
┌────────────────────────────────────▼─────────────────────────────────────┐
│                        4/5. THE EXECUTION (HOW & NOW)                    │
│  milestones/backlog sequence · sprint_active authorizes · upcoming stages │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ described by
┌────────────────────────────────────▼─────────────────────────────────────┐
│                         6. COMMUNICATION ONLY                            │
│  README · 04_architecture · 07_engineering · 08_theory — no architecture │
└──────────────────────────────────────────────────────────────────────────┘
```

Three binding rules (`ADR-0095`):

1. A lower document may **not** be used to reject a concept accepted in the locked
   [`VISION.md`](../VISION.md). Conflicting lower text is stale and must be reconciled.
2. The Vision changes only through an explicit Vision-superseding ADR.
3. Where implementation has not reached the Vision, that is documented as
   *current-state gap / planned migration* — never as a reason to weaken the Vision.


| Tier | Directory / File | Authority | Role & Contents |
|---|---|---|---|
| **Tier 1 (Law)** | [`SPEC.md`](SPEC.md) · [`01_law/`](01_law/) | **Normative** | Compact RFC-2119 index plus task-sized law leaves and preserved detailed clauses. |
| **Tier 2 (Decisions)** | [`02_decisions/`](02_decisions/) | **Binding Decision** | Accepted ADRs through `0102` and the [Canonical RF Allocation Register](02_decisions/INDEX.md#canonical-rf-falsifier-allocation-register). |
| **Tier 3 (Execution)** | [`03_execution/milestones.md`](03_execution/milestones.md) · [`03_execution/backlog.md`](03_execution/backlog.md) · [`03_execution/sprint_active.md`](03_execution/sprint_active.md) · [`03_execution/sprint_upcoming.md`](03_execution/sprint_upcoming.md) | **Execution** | Stable gates/packages, current authorization, and non-authorizing staging. |
| **Tier 4 (Architecture)** | [`04_architecture/`](04_architecture/) | **Descriptive** | System topology, C4 models, sequences, state machines, and traceability. |
| **Tier 5 (Modules)** | [`05_contracts/`](05_contracts/) · [`06_protocols/`](06_protocols/) · [`07_engineering/`](07_engineering/) · [`08_theory/`](08_theory/) | **Descriptive / How-To** | Wire contracts, ports, contributor procedures, and research theory. |
| **Tier 6 (Diagrams)** | [`09_diagrams/`](09_diagrams/) · [`09_tools/`](09_tools/) | **Frozen / Auxiliary** | Visual and tooling assets; `09_tools/` remains a separate archival decision. |
| **Archive** | [`_archive/`]( _archive/) | **Frozen / Non-authoritative** | Preserved references and reviews excluded from normal context bundles. |

---

## 2. Modular Subsystem Directory

| Subsystem Directory | Focus & Contents | Maturity |
|---|---|---|
| 📐 [`04_architecture/`](04_architecture/) | C4 Context, Containers, Components, Sequences, State Machines, and Traceability | Per-section maturity; future targets explicitly labelled |
| 📜 [`05_contracts/`](05_contracts/) | Wire schemas for events, trajectories, manifests, verdicts, and selectors | Mixed: current schemas plus RF-23/M-3 targets |
| 🔌 [`06_protocols/`](06_protocols/) | Port references for kernel dependencies, model, sandbox, evaluator, stores, and SPIs | `AS_BUILT` |
| 🧠 [`08_theory/`](08_theory/) | Active Inference, resource tensor, trajectory credit, harvesting, and promotion | `RESEARCH` / `AS_BUILT` |
| 🛠️ [`07_engineering/`](07_engineering/) | Contributor workflow, testing, security, adapters, packs, and context bundles | `AS_BUILT` |

---

## 3. Progressive Role-Based Reading Paths

### 👤 Newcomer / Contributor
1. [`README.md`](../README.md) — Mission, architecture summary, quick start commands.
2. [`04_architecture/c4_context.md`](04_architecture/c4_context.md) — System boundaries and actors.
3. [`07_engineering/development.md`](07_engineering/development.md) — Setup and daily test commands.

### 💻 Feature Developer
1. [`03_execution/sprint_active.md`](03_execution/sprint_active.md) — Find assigned task, file ownership boundary, and red falsifier test.
2. [`07_engineering/context_bundles.md`](07_engineering/context_bundles.md) — Select the minimum starting bundle, then follow its authoritative links.
3. Governing [`SPEC.md`](SPEC.md) clause & [`02_decisions/`](02_decisions/) decision.
4. Named test file under `test/` — Confirm red-to-green proof obligation.

### 🛡️ Security & Trust Reviewer
1. [`01_law/SECURITY.md`](01_law/SECURITY.md) — Kernel invariants, S0–S12 dispatch pipeline, capability attenuation.
2. [`04_architecture/sequences.md`](04_architecture/sequences.md) — S0–S12 execution timeline and signed verdict flow.
3. [`07_engineering/security_and_tcb.md`](07_engineering/security_and_tcb.md) — TCB budget ($\le 1438$ LOC) and domain blindness compliance.

### 📐 Architect
1. [`docs/README.md`](README.md) — This document.
2. [`04_architecture/c4_component.md`](04_architecture/c4_component.md) — Hexagonal production lattice.
3. [`04_architecture/traceability_matrix.md`](04_architecture/traceability_matrix.md) — Maturity-labelled concept-to-evidence map.
4. [`02_decisions/INDEX.md`](02_decisions/INDEX.md) — Architecture decision catalog through `0102`.
5. [`03_execution/milestones.md`](03_execution/milestones.md) and [`backlog.md`](03_execution/backlog.md) — M-4 through M-8 gates and packages.

### 🔬 Cognitive Systems Researcher
1. [`08_theory/README.md`](08_theory/README.md) — Theory index and maturity ratings.
2. [`08_theory/active_inference.md`](08_theory/active_inference.md) — Free energy minimization formulations.
3. [`08_theory/economic_resources.md`](08_theory/economic_resources.md) — four conserved costs and two structural ceilings.
4. [`08_theory/preference_and_promotion.md`](08_theory/preference_and_promotion.md) — DPO harvesting and McNemar promotion.

### 🤖 AI Coding Agent
1. [`AGENTS.md`](../AGENTS.md) — Operating contract and anti-sprawl rules.
2. [`03_execution/sprint_active.md`](03_execution/sprint_active.md) — Active wave tasks, assigned files, and falsifiers.
3. [`07_engineering/context_bundles.md`](07_engineering/context_bundles.md) — Ingest the task-specific starting bundle; do not assume an unmeasured token count.
4. Run verification linters: `check_boundaries.py`, `check_tcb_budget.py`, `check_doc_metadata.py`, `check_falsifier_ids.py`, `check_markdown_links.py`.

---

## 4. Find Information by Development Task

Start with the active board, then load only the row relevant to the change. A descriptive module
explains the current system but never overrides its governing SPEC clause or ADR.

| Development question | Start here | Then inspect | Proof of completion |
|---|---|---|---|
| What should be implemented now? | [`sprint_active.md`](03_execution/sprint_active.md) | Assigned ADR and files named by the task | Bound `RF-*` test and active-board gate |
| What ships in a later release? | [`milestones.md`](03_execution/milestones.md) | Relevant accepted ADR | Objective milestone exit gate; backlog is not authorization |
| How does the runtime fit together? | [`04_architecture/README.md`](04_architecture/README.md) | C4 view, sequence, or state machine for the affected boundary | [`traceability_matrix.md`](04_architecture/traceability_matrix.md) |
| What is the exact wire/data shape? | [`05_contracts/README.md`](05_contracts/README.md) | Generated schema and producer/reader named in that page | Contract test plus schema/code generation check |
| What can a boundary implementation call? | [`06_protocols/README.md`](06_protocols/README.md) | Exact port source and implementing adapter | Port/contract tests and boundary linter |
| How do I change kernel/security behavior? | [`01_law/SECURITY.md`](01_law/SECURITY.md) | Dispatch law, protocol, and security guide | Security test, boundary/domain-blindness checks, TCB budget |
| How do I add an adapter or pack? | [`07_engineering/README.md`](07_engineering/README.md) | Adapter/pack guide and minimum context bundle | Hermetic tests; a new pack requires zero domain/kernel diff |
| Is a cognitive or retrieval idea implemented? | [`08_theory/README.md`](08_theory/README.md) | Maturity label and governing roadmap/ADR | Only the named future milestone may promote it to active work |

## 5. Where Information Belongs

| Information type | Sole durable owner | Rule |
|---|---|---|
| Normative behavior or invariant | [`SPEC.md`](SPEC.md) or [`01_law/`](01_law/) | Use RFC-2119 language only here |
| Architectural decision and reversal condition | New append-only ADR under [`02_decisions/`](02_decisions/) | Never silently rewrite an accepted decision |
| Current work, ownership, and readiness | [`sprint_active.md`](03_execution/sprint_active.md) | Keep only the active wave |
| Stable sequencing and backlog | [`milestones.md`](03_execution/milestones.md) and [`backlog.md`](03_execution/backlog.md) | Does not authorize implementation before dependencies open |
| Next-window staging | [`sprint_upcoming.md`](03_execution/sprint_upcoming.md) | Preparation only; never current authorization |
| As-built explanation and navigation | Existing module under `04_architecture/`–`08_theory/` | Link to law/schema/code; do not duplicate canonical tables |
| Historical source or proposal | Frozen archive under [`_archive/`]( _archive/) | Preserve original language and content; never cite as execution authority |

Before adding a document, use [`07_engineering/documentation.md`](07_engineering/documentation.md). The
default is to update an existing owner rather than create another summary.

### Historical validation anchors

The final v0.6.1 architecture review used two frozen provenance anchors:

- [`001 — ALFA decision briefing`](_archive/reviews/backend/director_review_v0/proposals/001_alfa_review_full_decision.md)
  records the Director-facing synthesis and corrections applied to the proposal set.
- [`006 — Fi Tier S+ master proposal`](_archive/reviews/backend/director_review_v0/proposals/006_fi_review_full_gptsol_proposal.md)
  preserves the detailed source architecture, algorithms, risks, and proposed falsifiers.

They are useful for completeness audits only. The accepted ADR mapping in
[`02_decisions/INDEX.md`](02_decisions/INDEX.md), not the draft numbering inside either proposal, is controlling.
