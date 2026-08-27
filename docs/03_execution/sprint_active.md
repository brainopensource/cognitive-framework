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
- RF-95/M-6 release bundles: **produced** by WP-A1 in `docs/03_execution/evidence/`.
  Independent review receipts: still absent — the producer cannot accept its own work.
- Original RF-95 bundle: searched for and **not recoverable** (git history at `349c7d1`
  carries only the test and runner). Three preregistered candidates were executed;
  01 and 02 were `UNDETERMINABLE` on diagnosed instrument defects, 03 passed.

## Canonical milestone status

This is the sole current milestone-status table. `Merge` records mechanism presence only; `Gate`
records acceptance independently. Empty `Evidence` means no qualifying repository receipt. All rows
were verified against `15fbb7514ec3d8030da5259d2291acdf37c8686d` plus the uncommitted convergence diff.

| Milestone | Mechanism / integration truth | Package state | Merge | Gate | Evidence | Blocked on |
|---|---|---|---|---|---|---|
| M-0–M-3C/W-3D | Historical mechanisms integrated | **ACCEPTED** | `MERGED` | `ACCEPTED` | accepted ADR/gate lineage | — |
| M-4 | `/2`, RF-100 and product runner present; RF-95 candidate 03 executed and passed | **EVIDENCE_READY** | `MERGED` | `OPEN` | `M-4-rf95-candidate-03.json` (`sha256:aec94c0f…`) | independent acceptance receipt |
| M-5a | AgentView/checkpoints integrated; historical control invalid | **PACKAGE_READY** | `MERGED` | `OPEN` | `[]` | accepted successor baseline |
| M-5b | SAT regression path present; clean witness absent | **PACKAGE_READY** | `MERGED` | `OPEN` | `[]` | successor baseline, fresh graph coloring, RF-86/RF-98, review |
| M-6 | Synthetic success removed; real `ChildRuntimePort` re-enters `run_composed`; durable derived identity; componentwise reservation; open-subtree reconciliation | **EVIDENCE_READY** | `MERGED` | `OPEN` | `M-6-canonical-recursion.json` (`sha256:041c4d62…`) | independent acceptance receipt |
| M-6.5 | Controller/statistics present; study instrument invalid | **PACKAGE_READY** | `MERGED` | `OPEN` | `[]` | valid attributable paired study |
| M-7 | Topology library present; public runtime integration absent | **IN_PROGRESS** | `PARTIAL` | `OPEN` | `[]` | three topologies, monotonic telemetry, M7-01, ADR-0099 |
| M-8 | In-memory prototypes only | **NOT_STARTED** | `PREPARATION_ONLY` | `OPEN` | `[]` | M-7 disposition, durable authorized memory, lift and rollback |
| M-9/M-10 | Compatibility horizon only | **NOT_STARTED** | `NONE` | `NOT_AUTHORIZED` | `[]` | M-8 acceptance and new authority |

## Active packages

| ID | Milestone | Owner | State | Dependencies | Acceptance evidence |
|---|---|---|---|---|---|
| WP-A1 | M-4/M-6 release path and canonical recursive child runtime | Dev A | **EVIDENCE_READY** | accepted ADR-0101/0102 contracts | RF-101…RF-113 green; digest-addressed M-4/M-6 bundles produced; independent receipts outstanding |
| WP-B1 | Baseline forensics, successor control, and fresh M-5b generality package | Dev B | **EVIDENCE_READY** | accepted ADR-0101/0102 contracts; treatment starts only after successor tag | verified baseline verifier, graph-coloring vectors; signed material run; RF-86/RF-98 bundle |
| C1-GATE | Convergence CI and independent package review | Leadership | **BLOCKED** | WP-A1 and WP-B1 `EVIDENCE_READY`; qualified Linux/TS gates | signed CI envelope and separate acceptance receipts |

Both developers work from the same reviewed commit and do not consume unfinished branches. Dev A
owns runtime/session/delegation integration. Dev B owns baseline/evidence tooling and the pack-local
fresh falsifier. Shared schema or runtime interfaces are frozen by ADR before use.

## Director developer control

| Sprint | Milestone | Task ID | Owner | Task name | One-phrase assignment |
|:--|:--|:--|:--|:--|:--|
| C1 | M-4/M-6 | WP-A1 | Dev A · Main Senior | Canonical recursion | Fully deliver RF-95 and canonical fail-closed child execution with durable identity, attenuated conserved budgets, recovery, tests, and evidence. |
| C1 | M-5a/M-5b | WP-B1 | Dev B · Senior | Clean generality proof | Fully deliver the baseline verifier and accepted `CONVERGENCE-BASE-v1`, then implement and prove the fresh pack-local graph-coloring falsifier without touching Dev A runtime code. |

### Leadership helper

- Start: “Dev A, execute C1 WP-A1 for M-4/M-6”; “Dev B, execute C1 WP-B1 for M-5a/M-5b.”
- Checkpoint: ask each developer for `task -> code -> test -> evidence -> blocker`, then update only this board.
- Merge: review Dev A's runtime package and Dev B's baseline tooling independently; open `C1-GATE` only when both are `EVIDENCE_READY`.
- Next: after C1 acceptance, assign A2/B2 for M-6.5, then A3/B3 for M-7, then A4/B4 for M-8.

## Immediate execution order

1. Dev A removes the synthetic spawn result, introduces the required child-runtime interface,
   durable child identity, parent-bound componentwise budgets, and recovery/kill-tree tests.
2. Dev B records the contaminated-tag forensics in machine-verifiable test fixtures, implements the
   signed successor-baseline manifest verifier, and freezes the graph-coloring preregistration.
3. Leadership attempts recovery of original RF-95/M-6 artifacts by digest. If absent, it authorizes
   exactly one new RF-95 candidate after preregistration; no historical claim is reconstructed.
4. Run clean declared-dependency Python/TypeScript/static/UDS gates and obtain independent review.
5. Only after shared generic repairs and clean review, create and push annotated
   `CONVERGENCE-BASE-v1`; Dev B then completes graph coloring, RF-86/RF-98, signed vectors, and
   independent review inside WP-B1 before C1 closes.

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
