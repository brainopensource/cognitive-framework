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
| Lane A | WP-A4 | `1.0.0` | `5f5f1c6` | **PACKAGE_READY** | `tests_pass AND m6_order9_evidence_verified AND rf95_order9_evidence_verified AND portable_artifacts AND clean_subject` | RF-95 live rerun with external provider reachability |
| Lane B | WP-B2 | `1.0.0` | `3e8b081` | **PACKAGE_READY** | `evidence_verifier_falsifiers_pass AND acceptance_authority_is_registered_outside_the_document AND producer_signatures_are_re_derivable AND m6_verified_green_from_a_clean_subject` | WP-B3 (blocked on M-4 re-execution and on Lane A registering a producer key) |

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

## Evidence signing and acceptance protocol

Every bundle is judged by `tools/linters/verify_evidence.py`, which re-derives
each judgement from bytes and answers `passed`, `failed` or `undeterminable`.
The three are not interchangeable, and `undeterminable` never satisfies a
predicate.

- **Keys live outside the repository.** `tools/runners/keygen_evidence_key.py`
  writes a 0600 Ed25519 key under `~/.aether/keys/` and prints its public half.
  A key readable from the tree is not an authority.
- **Authorities are registered, not self-declared.**
  `tools/linters/evidence_trust_root.json` names every accepted producer and
  reviewer key. A key that first appears inside the document it authenticates
  proves nothing, so an unregistered signer is `undeterminable` and a registered
  key id signed by a different key `failed`.
- **Signatures are `ed25519:<base64>`.** An unprefixed signature names no
  algorithm; the verifier refuses formats it cannot identify rather than
  guessing.
- **Materials declare their digest scheme.** Without `scheme`, a re-derived
  mismatch cannot be told from an unknown hashing convention, so it can only be
  `undeterminable`. With it, tampering is a decidable failure.
- **Evidence is additive.** Bundles are never overwritten; a re-execution is
  published under a new label. `check_evidence_acceptance.py` marks the earlier
  bundle *superseded* only when the successor verifies green and pins a
  descendant commit.
- **One command does all of it:** `tools/runners/publish_evidence.py` builds
  from a throwaway worktree at a pinned commit so the subject stays clean,
  signs, has a registered reviewer accept, and re-verifies before anything
  lands.

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

### Verified milestone evidence

| Milestone | Verifier verdict | Bundle |
|---|---|---|
| M-6 | `passed` | `M-6-canonical-recursion-order10` — 57 falsifiers in a fresh process, depth 3, kill-tree; clean subject `3e8b081`, signed `dev-b-evidence-1`, accepted `aether-evidence-reviewer-1`. Supersedes `M-6-canonical-recursion` and `-order9`, both of which stay on record as `undeterminable`. |
| M-4 | `failed` | `M-4-rf95-candidate-05` is substantively sound — clean subject, materials resolve, cold reconstruction present — and fails only on an unverifiable producer signature and an unregistered reviewer key. Rebuilding it through `publish_evidence.py` with a registered key verifies green. |
| M-5b, M-6.5 | `undeterminable` | Materials record no digest scheme, so their integrity cannot be re-derived. Re-emitting through the current builder closes this without re-running the studies. |

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
