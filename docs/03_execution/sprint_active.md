---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: repository-governance
version: "1.1.0"
last_verified: 2026-08-27
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Active Delivery Board — AETHER v0.9

This is the sole current execution board. Stable task contracts are in
[`backlog.md`](backlog.md); later or dependency-qualified work is in
[`sprint_upcoming.md`](sprint_upcoming.md). Package and evidence states use ADR-0101.

## Verified baseline

- Branch: `feat_higgs_M4_M8`.
- Baseline commit: `43731e4`.
- Contract dataset: `aether.work-package/1`, backlog version `1.0.0`.

## Current Lane A and Lane B packages

Each lane has one current package. A package advances when its predicates are true;
no person, committee, or process approval is an entry dependency.

| Lane | Package | Contract | Baseline | State | Completion predicate | Next |
|---|---|---|---|---|---|---|
| Lane A | WP-C1 | `1.0.0` | `5142a3a` | **PACKAGE_READY** | `tests_pass AND trust_spine_preserved AND canonical_append_is_single_writer AND root_gated_clients_and_wheel_install_verified AND tree_clean` | WP-A2 |
| Lane B | WP-B2 | `1.0.0` | `b9fe664` | **PACKAGE_READY** | `evidence_verifier_falsifiers_pass AND acceptance_cannot_exceed_subject_outcome AND m65_disposition_preserved` | WP-B3 |

## Package state ledger

The ledger mirrors the stable backlog and makes state drift mechanically detectable.

| Package | Lane | State | Entry predicate | Completion predicate |
|---|---|---|---|---|
| WP-A1 | Lane A | **PACKAGE_READY** | `adr_0101 AND adr_0102` | `rf95_and_rf101_to_rf113_receipts_resolve` |
| WP-B1 | Lane B | **PACKAGE_READY** | `adr_0101 AND adr_0102` | `baseline_vectors_and_contract_receipts_resolve` |
| WP-A2 | Lane A | **BLOCKED** | `wp_a1_merged AND adr_0103_frozen AND wp_c1_predicate` | `runtime_seam_receipt_resolves` |
| WP-B2 | Lane B | **ACCEPTED** | `wp_a1 AND wp_a2 AND study_receipt` | `signed_study_disposition_resolves` |
| WP-A3 | Lane A | **NOT_STARTED** | `wp_a1_merged` | `three_topology_receipts_resolve` |
| WP-B3 | Lane B | **NOT_STARTED** | `wp_a3_receipt` | `m701_receipt_and_scheduler_decision_resolve` |
| WP-A4 | Lane A | **NOT_STARTED** | `adr_0099 AND adr_0100` | `durable_memory_receipts_resolve` |
| WP-B4 | Lane B | **NOT_STARTED** | `wp_a4 AND m65_disposition` | `held_out_and_rollback_receipts_resolve` |
| WP-C1 | Lane A | **PACKAGE_READY** | `adr_0062 AND adr_0089 AND adr_0101` | `trust_spine_and_single_writer_receipts_resolve` |

## Milestone predicates

Milestone acceptance is derived from digest-addressed evidence, not package presence or process status.

| Milestone | Required predicate |
|---|---|
| M-4 | `rf95_evidence_verified AND rf95_envelope_independently_verified` |
| M-5a | `agent_view_replay_verified AND convergence_base_v1_verified` |
| M-5b | `graph_coloring_rf86_rf98_verified_against_successor_base` |
| M-6 | `depth_3_recovery_and_budget_conservation_verified` |
| M-6.5 | `valid_paired_study_disposition_verified` |
| M-7 | `three_topologies_verified AND adr_0099_disposition_verified` |
| M-8 | `durable_memory_and_signed_rollback_verified` |

## Delivery rules

- Lane A owns runtime, execution, persistence, clients, packaging, deployment, and release surfaces;
  Lane B owns contracts, projections, evaluation, falsifiers, and promotion semantics.
- Each lane keeps WIP=1 and edits only its owned surfaces. Contract changes are consumed only after a
  frozen producer commit.
- Product-time operator approvals for privileged effects remain part of the security model. They are
  distinct from development workflow state and are checked by the runtime at use time.
- Unknown, absent, invalid, or undeterminable evidence never satisfies a predicate. A valid negative
  experiment selects its declared fallback.
- The release predicate is `./ci/release_qualify.sh == 0` with a signed envelope whose subject exactly
  matches the candidate; otherwise the first failing stage is repaired forward.

## Historical package context


The historical activation instructions are superseded by the current package
ledger above. Their stable contracts remain in [`backlog.md`](backlog.md).
