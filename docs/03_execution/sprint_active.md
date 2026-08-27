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
last_verified: 2026-08-27
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
- RF-95/M-6 release bundles: **produced** by WP-A1 in `docs/03_execution/evidence/`, and now
  **producer-signed** (`dev-a-operator`). Both record `undeterminable`, not `passed`:
  - `M-4-rf95-candidate-03.json` — the run did not bind its preregistration (empty
    `preregistration_digest`), and its ledger artifact lived in a volatile temporary
    directory whose bytes no longer match the recorded digest, so the material is
    unresolvable. The runner now threads preregistration and can export portable artifacts.
  - `M-6-canonical-recursion.json` — `pins.dirty` is true, so the pinned commit does not
    name the bytes that produced the result and a reviewer cannot recompute it.

  Independent reviewer envelopes were generated for all four bundles and pass cryptographic,
  digest-binding, and producer-separation checks. The M-4 and M-6 envelopes do not close their
  milestones because their producer outcomes remain `undeterminable`; M-5b remains blocked on the
  successor baseline.
- WP-B1 evidence bundle is present as `M-5b-graph-coloring.json`, with an independent reviewer
  envelope, but its outcome remains `undeterminable` pending the successor baseline and remote
  resolution. WP-B1 therefore remains `PACKAGE_READY` pending baseline qualification.
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
| M-4 | `/2`, RF-100 and product runner present; RF-95 candidate 03 executed and passed its five conditions | **PACKAGE_READY** | `MERGED` | `OPEN` | `M-4-rf95-candidate-03.json` (`sha256:5a98afee…`, signed, outcome `undeterminable`) | re-executed candidate under the preregistration-binding runner, then independent acceptance |
| M-5a | AgentView/checkpoints integrated; historical control invalid | **PACKAGE_READY** | `MERGED` | `OPEN` | `[]` | accepted successor baseline |
| M-5b | Graph coloring material run, exterior oracle, and daemon signatures verified; undeterminable without remote control | **PACKAGE_READY** | `MERGED` | `OPEN` | `M-5b-graph-coloring.json` (`sha256:cb0a3956…`) | successor baseline, remote tag, review |
| M-6 | Synthetic success removed; real `ChildRuntimePort` re-enters `run_composed`; durable derived identity; componentwise reservation; open-subtree reconciliation | **PACKAGE_READY** | `MERGED` | `OPEN` | `M-6-canonical-recursion.json` (`sha256:33316512…`, signed, outcome `undeterminable`) | re-production against a clean subject with depth>=3 and kill-tree artifacts, then independent acceptance |
| M-6.5 | Stochastic attributable paired study and signed evidence envelope produced | **ACCEPTED** | `MERGED` | `ACCEPTED` | `M-6.5-attributable-paired-study.json` (`sha256:293e738c…`) + independent acceptance envelope | — |
| M-7 | Topology lowering is wired through `Runtime.run_composed`; the shipped default composition has no `agent.spawn`, so multi-role live execution remains fail-closed | **PACKAGE_READY** | `PARTIAL` | `OPEN` | `[]` | live three-topology execution, signed M7-01 envelope, and acceptance |
| M-8 | Capability-mediated memory contracts, turn-loop retrieval, causal experience emission, and durable governed-learning restore are present; acceptance evidence remains open | **PACKAGE_READY** | `PARTIAL` | `OPEN` | `[]` | authorized memory evidence and held-out lift acceptance |
| M-9/M-10 | Compatibility horizon only | **NOT_STARTED** | `NONE` | `NOT_AUTHORIZED` | `[]` | M-8 acceptance and new authority |

## Active packages

| ID | Milestone | Owner | State | Dependencies | Acceptance evidence |
|---|---|---|---|---|---|
| WP-A1 | M-4/M-6 release path and canonical recursive child runtime | Dev A | **PACKAGE_READY** | accepted ADR-0101/0102 contracts | RF-101…RF-113 green; M-4/M-6 bundles producer-signed but `undeterminable` (unbound preregistration; unresolvable artifact; dirty subject). Re-execution against a clean subject required before independent review |
| WP-B1 | Baseline forensics, successor control, and fresh M-5b generality package | Dev B | **PACKAGE_READY** | accepted ADR-0101/0102 contracts; treatment starts only after successor tag | verified baseline verifier, graph-coloring vectors; signed material run; M-5b-graph-coloring.json produced; blocked on remote successor tag |
| WP-B2 | M-6.5 attributable stochastic study and evidence bundle | Dev B | **ACCEPTED** | accepted ADR-0103/backlog contracts | RF-114…RF-117 green; stochastic ModelPort adapter; >=60 pairs; valid A/A floor; signed M-6.5 evidence bundle and independent acceptance envelope verified |
| WP-C1 | Backend service trust spine and canonical event truth | Dev A | **PACKAGE_READY** | accepted ADR-0062/0089/0101; no Kernel or schema change | falsifiers for key material, non-TTY approval denial, approval verification, gateway auth/origin/size, `StreamEvents` validation, canonical single-writer append, envelope round-trip fidelity, checkpoint reconstruction, resume restart, worker-observed cancellation |
| C1-GATE | Convergence CI and independent package review | Leadership | **BLOCKED** | WP-A1 `PACKAGE_READY`; WP-B1 `PACKAGE_READY`; WP-B2 `ACCEPTED`; WP-C1 `PACKAGE_READY`; complete acceptance is not established | **independent adjudication:** baseline manifest/tag absent; M-4/M-6 evidence remains `undeterminable`; qualified Linux AF_UNIX and remote tag verification outstanding |


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

## C1 exit state (2026-08-27)

Developer-side work is complete **on the WP-A1 and WP-B1/WP-B2 surfaces**. It is not complete on the
backend service and distribution surface: `runtime/service/` and the standalone CLI entered the tree
outside the M-4–M-8 packages and regress already-accepted invariants (`I-5` approval verification,
the M-2 one-writer anchor, and `I-4`/`I-9` recovery truth). That repair is authorized above as
`WP-C1` and is in progress; it closes no gate of its own.

Three further items remain outside implementation:

1. **Qualifying M-4 and M-6 closure remains outstanding.** Independent reviewer envelopes now
   exist, but ADR-0101 does not allow a reviewer receipt to turn an `undeterminable` producer
   outcome into a pass. M-4 requires a fresh preregistration-bound run with portable artifacts;
   M-6 requires a clean-subject re-production with the promised depth/kill-tree artifacts.
2. **Qualified Linux AF_UNIX CI receipt** for the convergence subject, still
   requested externally.
3. `CONVERGENCE-BASE-v1` remains uncreated, correctly: it is gated on clean
   gates *and* the independent review above.

Two findings are handed to Leadership rather than fixed in C1, because both
sit outside WP-A1's authorized surface:

- **The runner does not bind its preregistration.** `preregistration_digest`
  is empty in the RF-95 trajectory, so the candidate is tied to its frozen
  document by commit ordering rather than by an in-run digest. Recorded in the
  M-4 envelope's `detail` rather than hidden. Fixing it means threading
  `TaskContext.preregistration` in `tools/runners/run_rf95_product_proof.py`.
- **The agency loop cannot tell "my patch failed" from "my patch already
  applied".** Candidate 02's ledger shows ~15 re-proposals of an
  already-applied `patch.apply`, each reconciled `patch context not found`,
  burning the turn budget on a workspace that was already correct. This lives
  in the repair/feedback path, not in delegation.

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
