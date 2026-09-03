---
id: execution.milestones
canonical_id: execution.milestones
class: execution
authority: execution
truth_plane: TARGET
status: living
implementation_status: PARTIAL
owner: repository-governance
canonical_for:
  - milestone outcomes and gates
purpose: Present stable TARGET milestone outcomes, dependencies, and acceptance predicates without claiming current completion.
audience:
  - contributor
  - release-owner
version: 0.9.2a4
last_verified: 2026-09-03
normative_authority:
  - docs/SPEC.md#milestone-compatibility
  - docs/decisions.md
relationships:
  - execution.tasks
  - execution.backlog
  - execution.feature_spec
  - spec.core
reviewer: repository-governance
confidence: high
---

# TARGET Milestone Gates

## 1. Scope & Authority

This page defines stable release outcomes and gate predicates. It does not track day-to-day work packages (owned by [`backlog.md`](backlog.md)) or ephemeral session DAGs (owned by [`tasks.md`](tasks.md)). Mechanism presence does not infer milestone closure; closure requires producer-verifiable empirical receipts evaluated under the milestone acceptance boundary.

| Milestone | TARGET Outcome | Acceptance Boundary | Status |
|---|---|---|---|
| **M-0–M-3C** | Trust foundation & canonical composition | Historical completion anchors preserved; successor changes require explicit ADR and falsifier. | `DONE` (Verified & Frozen) |
| **M-4** | Real-model coding proof with durable causal evidence | Immutable RF-95 bundle plus valid acceptance; RF-85 remains optional assurance. | `DONE` (Base Tagged) |
| **M-5a** | Event-derived `AgentView` & accepted successor baseline | Replay evidence and verified `CONVERGENCE-BASE-v1` predicates. | `DONE` (Base Reconciled) |
| **M-5b** | Independent domain-generality witness | RF-86/RF-98 against uncontaminated successor baseline. | `MECHANISM AS_BUILT` (Awaiting Handoff) |
| **M-6** | Mediated recursive delegation | Depth-three cold reconstruction, attenuation, budget conservation, recovery, signed evidence. | `MECHANISM AS_BUILT` (59 tests green) |
| **M-6.5** | Measured adaptive strategy | Valid paired-study disposition; controller remains off unless profile-specific evidence authorizes it. | `MECHANISM AS_BUILT` (Controller Off) |
| **M-7** | Declarative multi-role topology through one runtime | Three real-effect topologies, persisted artifact flow, and explicit scheduler disposition. | `MECHANISM AS_BUILT` (40 tests, 6 skips) |
| **M-8** | Durable memory & governed learning MVP | Authorization, recovery, retention, held-out lift $\ge 0.05$, separated promotion authority, executed rollback receipts. | `BLOCKED` (Empirical runner repair & held-out lift remain open) |
| **M-9** | Installable operational beta `0.9.0b1` | Qualified M-1–M-8 evidence, unified product surfaces, health, two workflows, restart/resume, offline-after-install. | `UNAUTHORIZED` (Blocked on M-8) |
| **M-10** | Final `0.9.0` release | Migration, backup/restore, fault/security/performance qualification, reproducible artifacts, soak, exact-subject signed envelope. | `UNAUTHORIZED` (Blocked on M-9) |

---

## 2. Gate Semantics & Release Invariants

- **Invariant G-1 (Evidence Verifiability)**: Unknown, missing, failed, degraded, or `undeterminable` evidence never satisfies a predicate.
- **Invariant G-2 (Linear Authorization)**: M-9 cannot be authorized before M-8 has an exact producer-verifiable bundle and independent acceptance over its digest. M-10 closes only when `./ci/release_qualify.sh` exits `0` for the exact candidate.
- **Invariant G-3 (Non-Contamination)**: Local test suites, cassettes, and self-authored oracles never constitute an official SWE-bench result. Official claims require the SWE-P5 protocol.

---

## 3. Capability Wave Overlay: Backend Finish (W-092)

Vanguard v0.9.2 is an implementation and qualification overlay contributing evidence to existing M-4–M-10 gates. Active implementation details live in [`tasks.md`](tasks.md) and [`FEATURE_SPEC.md`](FEATURE_SPEC.md).

| Gate | Stable Outcome | Acceptance Predicate | Status |
|---|---|---|---|
| **W-092-F0** | Exact-subject navigation & benchmark truth | LDA/index health is HEAD-bound; runtime-to-patch-to-exterior-verdict evidence resolves; canary subjects content-addressed. | `DONE` (Consolidated & Validated) |
| **W-092-F1** | One canonical Coding Max product path | Fast/balanced/max invoke `ApplicationService -> Runtime -> HarnessSession -> EpisodeEngine`; no parallel production engine or bypass. | `IN_PROGRESS` (Active in `tasks.md`) |
| **W-092-F2** | Truthful task-aware completion | Observed test counts; zero-test/stale/partial evidence fails closed; bugfix/feature/migration/greenfield policies explicit. | `APPROVED` (Spec in `FEATURE_SPEC.md`) |
| **W-092-F3** | Durable long-session continuation | Fresh process restores task/composition/policy/budget identity; never duplicates settled effects across 40+ turns. | `APPROVED` (Spec in `FEATURE_SPEC.md`) |
| **W-092-F4** | Repository-scale progressive context | `ContextPacket` and `IndexPort` supply bounded, snapshot-bound, omission-bearing staged context with deterministic source fallback. | `APPROVED` (Spec in `FEATURE_SPEC.md`) |
| **W-092-F5** | Product qualification | Frozen multi-class tasks produce exact patches, fresh verification, exterior verdicts, event evidence, and resume parity. | `BLOCKED` (Requires F1–F4 completion) |
| **W-092-F6** | Specialist role disposition | Held-out ablations accept or reject reviewer/localizer/planner treatments without weakening verifier authority. | `DEFERRED` (Optional post-baseline) |

---

## 4. Post-M-10 Horizon: Octopus Outer-Loop Meta-Orchestration (`M-OCT`)

The following outcomes define the post-1.0 architectural horizon for multi-day, multi-agent campaign orchestration. They do not create active sprint milestones or authorize work that M-8/M-9 currently block.

| Wave | Horizon Outcome | Terminal Acceptance Boundary |
|---|---|---|
| **W-OCT-1** | **Content-Addressed Mailbox Protocol** | Roles communicate strictly by publishing and reading content-addressed immutable message digests (`digest_of(payload)`); zero shared memory between roles; replayable multi-agent determinism. |
| **W-OCT-2** | **Declarative CoordinationPlan DAG** | Topology declared as immutable data DAG with strict per-mille budget shares ($\sum \text{budget\_share} \le 1000$); formal merge policies implemented: `CONCAT`, `FIRST_COMPLETE`, `SYNTHESISE`, `UNANIMOUS`. |
| **W-OCT-3** | **Outer-Loop Multi-Day Roadmap Director** | Higher-order director layer executing above `EpisodeEngine`; decomposes complex roadmaps into independent task DAGs across process boundaries without violating kernel S0–S12 contracts. |
| **W-OCT-4** | **Meta-Conductor & Swarm Goal Algebra** | Formal algebraic separation and reconciliation of individual swarm agent objectives under a global parent mission; automated topology selection based on task classification. |

---

## 5. Parallel SWE Benchmark Program (SWE-P0–SWE-P5)

| Program | Outcome | Required Gate | Status |
|---|---|---|---|
| **SWE-P0** | Instrument-valid harness | Isolated materialization, trajectory linkage, evaluator validity, secret boundary. | `DONE` |
| **SWE-P1** | Honest baseline | Preregistered corpus/model/cost policy and explicit missingness reporting. | `APPROVED` |
| **SWE-P2** | Harness experiments | Controlled context/tool/recovery experiments with attributable receipts. | `APPROVED` |
| **SWE-P3** | Model/harness optimization | Predeclared optimization and held-out comparison without contamination. | `BLOCKED` (on P1) |
| **SWE-P4** | Controlled larger run | Budgeted larger sample, independent audit, reproducible subject identity. | `BLOCKED` (on P3) |
| **SWE-P5** | Official evaluation | Official benchmark procedure and receipt; local runs are never official. | `BLOCKED` (on P4) |
