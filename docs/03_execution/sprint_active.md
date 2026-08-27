---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: tech-lead
version: "1.0.0"
last_verified: 2026-08-26
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Active Sprint C1 — Truth Restoration and Recursive Runtime Repair

This is the sole current work authorization. Stable task contracts are in
[`backlog.md`](backlog.md); later or dependency-blocked work is in
[`sprint_upcoming.md`](sprint_upcoming.md). Status uses ADR-0101 only.

## Verified baseline

- Branch: `feat_higgs_M4_M8`.
- Verification subject before convergence edits:
  `15fbb7514ec3d8030da5259d2291acdf37c8686d`.
- `M-5A-BASE-v2`: local lightweight ref at `1b4ce1a...`; absent from the configured remote;
  contains successor treatment code; disposition `CONTAMINATED_UNPUBLISHED` (ADR-0102).
- RF-86: **fails** on 111 added protected-substrate lines at the verification subject.
- RF-98: structural Kernel neutrality and Kernel diff are green against the local tag, but this
  cannot validate the contaminated control.
- RF-95/M-6 release bundles and independent review receipts: absent from the repository.

## Active packages

| ID | Milestone | Owner | State | Dependencies | Acceptance evidence |
|---|---|---|---|---|---|
| WP-A1 | M-4/M-6 release path and canonical recursive child runtime | Dev A | **IN_PROGRESS** | accepted ADR-0101/0102 contracts | tests plus digest-addressed RF-95/M-6 bundles; independent receipts |
| WP-B1 | Baseline forensics, manifest verifier, and M-5b successor experiment preparation | Dev B | **IN_PROGRESS** | accepted ADR-0101/0102 contracts | forensic report; baseline verifier tests; preregistered graph-coloring protocol |
| C1-GATE | Convergence CI and independent package review | Leadership | **BLOCKED** | WP-A1 and WP-B1 `EVIDENCE_READY`; qualified Linux/TS gates | signed CI envelope and separate acceptance receipts |

Both developers work from the same reviewed commit and do not consume unfinished branches. Dev A
owns runtime/session/delegation integration. Dev B owns baseline/evidence tooling and the pack-local
fresh falsifier. Shared schema or runtime interfaces are frozen by ADR before use.

## Immediate execution order

1. Dev A removes the synthetic spawn result, introduces the required child-runtime interface,
   durable child identity, parent-bound componentwise budgets, and recovery/kill-tree tests.
2. Dev B records the contaminated-tag forensics in machine-verifiable test fixtures, implements the
   signed successor-baseline manifest verifier, and freezes the graph-coloring preregistration.
3. Leadership attempts recovery of original RF-95/M-6 artifacts by digest. If absent, it authorizes
   exactly one new RF-95 candidate after preregistration; no historical claim is reconstructed.
4. Run clean declared-dependency Python/TypeScript/static/UDS gates and obtain independent review.
5. Only then create and push annotated `CONVERGENCE-BASE-v1`; graph-coloring implementation starts
   after the tag and is therefore not active in this sprint.

## Explicit external evidence requests

- Original `M-5A-BASE-v2` tag object/annotation/target and review receipt, if any. Do not recreate it.
- Original RF-95 and M-6 evidence bundles, artifact digests, protocol/environment identities, and
  independent review receipts, if any.
- Qualified Linux AF_UNIX and clean TypeScript CI receipts for the convergence subject.

## Prohibited scope

- No movement, recreation, or validation-by-prose of `M-5A-BASE-v2`.
- No successor tag before clean gates and independent review.
- No broad M-6.5/M-7/M-8 feature implementation in C1.
- No M-9/M-10 feature or scaffold.
- No Kernel/domain semantics for spawn, topology, strategy, memory, or learning.
- No receiptless `ACCEPTED`, test weakening, manual evidence repair, or unknown-as-pass value.
