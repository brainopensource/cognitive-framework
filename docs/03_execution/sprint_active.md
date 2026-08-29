---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: repository-governance
version: "1.2.1"
last_verified: 2026-08-29
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
| Lane A | WP-A3 | `1.0.0` | `3e8b081` | **IN_PROGRESS** | `three_topology_receipts_resolve AND role_operations_execute_real_effects AND artifact_flows_resolve_from_persisted_receipts` | Repair abandoned multi-role lineages; publish M-7 evidence only after real artifact flow |
| Lane B | WP-B4 | `1.0.0` | exact bundle subjects | **PACKAGE_READY** | `m4_verified` (**done**, `candidate-07`, operator-attested not org-independent) `AND convergence_base_v1_verified AND m5b_successor_verified AND m65_successor_disposition_verified AND m8_independently_accepted` | Close remaining evidence dependencies in order; never reinterpret failed/undeterminable bundles |

## Package state ledger

The ledger mirrors the stable backlog and makes state drift mechanically detectable.

| Package | Lane | State | Entry predicate | Completion predicate |
|---|---|---|---|---|
| WP-A1 | Lane A | **PACKAGE_READY** | `adr_0101 AND adr_0102` | `rf95_and_rf101_to_rf113_receipts_resolve` |
| WP-B1 | Lane B | **PACKAGE_READY** | `adr_0101 AND adr_0102` | `baseline_vectors_and_contract_receipts_resolve` |
| WP-A2 | Lane A | **PACKAGE_READY** | `wp_a1_merged AND adr_0103_frozen AND wp_c1_predicate` | `runtime_seam_receipt_resolves` |
| WP-B2 | Lane B | **BLOCKED** | `wp_a1 AND wp_a2 AND study_receipt` | `signed_study_disposition_resolves` |
| WP-A3 | Lane A | **IN_PROGRESS** | `wp_a1_merged` | `three_topology_receipts_resolve` |
| WP-B3 | Lane B | **EVIDENCE_READY** | `wp_a3_receipt` | `m701_receipt_and_scheduler_decision_resolve` |
| WP-A4 | Lane A | **PACKAGE_READY** | `adr_0099 AND adr_0100` | `durable_memory_receipts_resolve` |
| WP-B4 | Lane B | **PACKAGE_READY** | `wp_a4 AND m65_disposition` | `held_out_and_rollback_receipts_resolve` |
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

## Active critical path

Mechanism work and evidence close-out proceed in parallel, but the following gates remain ordered:

1. ~~Re-emit M-4 `candidate-06`~~ **done as `candidate-07`** — `candidate-06` (`z-ai/glm-5.2:free`)
   hit two consecutive `instrument_error` (HTTP 429) turn-0 aborts and never reached the agent
   loop; `candidate-07` reran the identical fixture/task/verifier over the paid
   `deepseek/deepseek-v4-flash-0731` route, produced the required diff, passed tests, and
   `tools/linters/verify_evidence.py` returns `passed` for the signed-and-accepted bundle. See the
   independence caveat below the verdict table: producer (`dev-a-evidence-1`) and reviewer
   (`aether-evidence-reviewer-1`) keys were both held by the same operator for this run, so
   acceptance is mechanically valid but not yet organizationally independent.
2. ~~Externally create and publish the annotated, remotely resolvable `CONVERGENCE-BASE-v1`~~ **done**
   — the annotated tag (`ee80748872104f06c927e098fd5392b139ea7251`, dereferencing to commit
   `532abf16defb23a0d91259f45aa7042c9b2bae6d`) resolves on the configured remote, and
   `evidence/baselines/CONVERGENCE-BASE-v1.json` carries a signed `aether.baseline/1` manifest with
   both creator and reviewer signatures present (55 schema pins, 4 reducer pins, 3 protected
   subtrees). As with every other bundle in this repository, mechanical signature validity does not
   by itself establish organizational reviewer independence. `tools/linters/check_baseline_manifest.py`
   run at current HEAD reports reducer-pin drift against files changed by ordinary development since
   the tag was cut (e.g. `vanguard/packages/domain/ledger/events.py`) — this is the drift-detection
   mechanism working as designed (RF-86/RF-98 compare *new* treatment to this frozen baseline going
   forward), not a defect in the baseline itself.
3. Re-emit M-5b against that successor baseline. Preserve every historical failed bundle.
4. Re-emit the stored M-6.5 study with portable references and an explicit digest scheme now that
   M-4 verifies. A valid positive or negative result closes the study; the current undeterminable
   bundle does not.
5. Complete M-7 by making planner/executor/reviewer and fork/read/merge children perform real effects
   and exchange authorized artifacts by digest through ordinary M-6 spawn. Lowered declarations or
   empty abandoned lineages do not satisfy the predicate.
6. Publish M-8 from a clean immutable subject, sign it, independently accept the exact bundle digest,
   and verify it again in a fresh process. Green tests or a locally built bundle are not acceptance.
7. Only after M-8 is independently accepted may M-9 move from staging to this board. M-10 follows a
   qualified M-9 beta and closes only on exact-subject release proof.

The external Git operations in steps 2 and 6 are release-owner actions. Coding lanes prepare and
verify their inputs but never simulate commits, tags, remote resolution, or clean-subject identity.
Step 1's commit/signing was performed by the requesting operator directly, not simulated; the open
item it leaves is a genuinely separate reviewer identity, not a mechanical gap.

### Verified milestone evidence

Verdicts below are `tools/linters/verify_evidence.py --json` output over
`docs/03_execution/evidence/`, not summaries of test runs. A milestone with no
published bundle has no verdict, however green its suites are.

| Milestone | Verifier verdict | Bundle |
|---|---|---|
| M-6 | `passed` | `M-6-canonical-recursion-order10` — 57 falsifiers in a fresh process, depth 3, kill-tree; clean subject `3e8b081`, signed `dev-b-evidence-1`, accepted `aether-evidence-reviewer-1`. Supersedes `M-6-canonical-recursion` and `-order9`, which stay on record. |
| M-4 | `passed` | `M-4-rf95-candidate-07` — clean subject `7a3adb1`, live run over `deepseek/deepseek-v4-flash-0731`, real diff (`return a * b`), passing tests, file-backed WAL, complete `mhf.trajectory/2`, matching cold reconstruction; signed `dev-a-evidence-1`, accepted `aether-evidence-reviewer-1`; `verify_evidence.py` returns `passed`. **Caveat**: the producer and reviewer keys were controlled by the same operator for this run (see `RF-95-candidate-06.md`/`-07.md` honesty notes) — mechanically independent, not yet organizationally independent; a distinct reviewer identity re-signing the same digest would close that gap without rerunning anything. `candidate-05` (`failed`: raw-hex signature, mismatched reviewer key) and `candidate-06` (two `instrument_error` HTTP 429 aborts on `z-ai/glm-5.2:free`, never reached the agent loop) are preserved unmodified. |
| M-5b | `failed` | `M-5b-graph-coloring` records an acceptance claiming `passed` over an `undeterminable` subject. Its materials also record no digest scheme. The builder now emits `raw-sha256`; a labelled successor is gated on `CONVERGENCE-BASE-v1`. |
| M-6.5 | `passed` | `M-6.5-attributable-paired-study-order13` — 32 paired trials with portable report references and `raw-sha256` digests; signed `dev-b-evidence-1`, accepted `aether-evidence-reviewer-1`; `verify_evidence.py` returns `passed`. |
| M-5a | published | `CONVERGENCE-BASE-v1` is published: annotated tag `ee80748` on commit `532abf16`, resolves on the configured remote. `evidence/baselines/CONVERGENCE-BASE-v1.json` is a signed `aether.baseline/1` manifest (creator + reviewer signatures present). `check_baseline_manifest.py` at current HEAD reports expected reducer-pin drift from development since the tag (not a bundle defect). M-5a's own completion predicate (`agent_view_replay_verified AND convergence_base_v1_verified`) still requires the replay half separately. |
| M-7 | `passed` | `M-7-topology-order12` — 40 tests, all 25 markers true; direct, planner/executor/reviewer, and fork/read/merge run as real M-6 children with CAS artifact flow; signed `dev-a-evidence-1`, accepted `aether-evidence-reviewer-1`; `verify_evidence.py` returns `passed`. |
| M-8 | `passed` | `M-8-durable-memory-order12` — 59 tests, all 34 markers true; authorization-before-ranking, CAS composition registry, verified rollback in fresh process; signed `dev-b-evidence-1`, accepted `aether-evidence-reviewer-1`; `verify_evidence.py` returns `passed`. |

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
