---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: tech-lead
version: "0.7.2"
last_verified: 2026-08-25
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Active Sprint — S-P2-01 M-4 Package Delivery

Authority: [`VISION.md`](../../VISION.md) -> [`SPEC.md`](../SPEC.md) +
[`01_law/`](../01_law/) -> accepted ADRs through
[`ADR-0097`](../02_decisions/0097-phase0-ratification-and-two-lane-activation.md) ->
[`milestones.md`](milestones.md) -> this board. This is the sole current implementation
authorization. The Director handoff and reviews under `docs/00_leadership_supersede_all/` informed
this board but do not form a second execution authority.

## 1. Current phase and activation receipts

**Phase 0 complete. S-P2-01 is in M-4 package delivery from activated baseline
`f9d7ceb257e8e2c7d6014bd0a29604ffcd89ee0e`. Dev A and Dev B are both `PACKAGE_READY`; the G-M4
review is open and unfinished (§5b).**

Activation receipts: ADR-0096 v0.4.0 and ADR-0097 v0.2.0 accepted; law, milestones and execution
authorization reconciled; Contract Kit, ownership and merge order frozen; Linux RF-38…RF-45 13/13
on 2026-08-25.

`PACKAGE_READY` is isolated readiness only — neither `MERGED` nor `GATE_ACCEPTED`. RF-95 remains
**NO-GO** until §6 passes; M-5a remains blocked on M-4 closure and accepted ADR-0098.

## 2. Frozen delivery decisions

These are ratified in [`ADR-0096 §14`](../02_decisions/0096-constitutional-correction-evidence-causal-invariants-and-falsifiers.md)
and [`ADR-0097`](../02_decisions/0097-phase0-ratification-and-two-lane-activation.md) and are not
restated here; the board records status, the ADRs hold the decisions. In force for M-4: `/1`
byte-frozen with dual-read `/1|/2` and single-write `/2`; historical bytes, digests and identities
never rewritten; exact provider I/O captured at `runtime/session.py::_LayeredOperator.propose`;
blob before ledger fact with the store computing the digest; evidence-append and required-capture
failure fatal; optional degradation only after a durable `capture_incomplete`, making the run
non-evidentiary; retention (`digests_only|standard|full`) never authorizing capture; WAL and pins
as prerequisites only, `verified` needing a run-bound executed receipt; run-close assessment
immutable.

Ownership seam: Dev B owns profile/trajectory schemas, writer, reader, reproducibility and contract
falsifiers, and published the frozen fixtures first. Dev A owns Runtime capture/wiring and the
generic Agency provenance integration, edits no Dev B-owned surface, and escalates rather than
works around a missing field. M-4 authorizes no event-kind, envelope, Kernel, or import change.

## 3. Simple active backlog

Acceptance rules are in §§4–6 and the accepted law/ADR stack.

### Done

PH0-00…PH0-05 and A-M4-00/B-M4-00 are complete; see git history.

### In progress — M-4 packages

A-M4-01…05 and B-M4-01…06 are complete; both lanes are `PACKAGE_READY`.

### Next — integration and gate

G-M4-01/02 done (review + reconstructed merge order). G-M4-03 gates green except the TypeScript
suite. G-M4-04 (RF-95), G-M4-05 (independent review) and G-M4-06 (closure) remain open.

### Blocked future backlog

M-5a (G-M4 + ADR-0098), M-5b and M-6 (`M-5A-BASE-v2`; plus the oracle decision and the production
SpawnAdapter contract respectively), M-6.5 (M-4 telemetry, and M-6 for delegation), M-7 (M-6.5 and
the M7-01 decision), M-8 (M-7). Ladder detail lives in [`milestones.md`](milestones.md).

## 4. Dev A — Evidence Runtime and Causal Capture

State: **PACKAGE_READY**. WIP limit: one package.

Surfaces: new `runtime/{artifacts,provenance}.py`, `agency/provenance.py`; edits to
`runtime/{session,root}.py` and `agency/context/{compiler,layers}.py`; 76 focused tests.

Obligations map to named test classes in `test/runtime/test_evidence_capture.py`, one class per
rule: durable ordering, store-owned digest, no inline content, retention-is-not-authorization,
redaction before persistence, fatal required-capture failure, durable degradation, fatal
evidence append, exact I/O at the provider seam, cache-only-when-reported, legacy `blobs=None`,
boundary, roster stability, the frozen B-M4-01 seam, and the integrated `/2` bundle.

The published B-M4-01 fixture was consumed as frozen; no Dev B-owned file was edited. Dev A adopted
the fixture's `checkpoint_state` role name. No fixture field was materially missing, so no
escalation is open against B-M4-01.

## 5. Dev B — Scientific Contracts and Verification

State: **PACKAGE_READY**. WIP limit: one package.

Objective: implement versioned scientific contracts and falsifiers that prevent evidence claims from
exceeding executed proof.

Exclusive surfaces: `runtime/{profiles,reproducibility,trajectory,trajectory_reader}.py`, profile and
trajectory schemas/vectors/readers/fixtures, Dev B-focused tests, and the append/fold benchmark.

Package contract: publish B-M4-01 first, then complete B-M4-02…06 in §3. `/1` stays frozen;
`/2` is the sole new write contract; absent historical evidence remains absent; RF-100 cannot
overclaim; and the benchmark is frozen. Use supported `python3`; the broken `.venv` is out of scope
without separate authorization. `PACKAGE_READY` requires all focused contract tests green.

## 5b. G-M4 review findings (Tech Lead)

Review **partially complete**. Gate **NOT** accepted; RF-95 remains **NO-GO**.

Verified: full suite 1446 passed / 8 skipped / 0 failed; codegen `--check`; eleven linters;
RF-38…RF-45 13/13. Confirmed frozen: `/1` schema files byte-unmodified; `domain/ledger/events.py`
and `_V4_ONLY_KINDS` zero-line diff; RF-100 `verified` requires a run-bound executed receipt. Dev
B's F-12 and `audit.py` edits extend coverage and dual-read; they do not weaken falsifiers.

Defects found and fixed (D1–D3 in the B-M4 commit, D4 in A-M4):

- **D1** codegen resolved `"$ref": "#"` against one global root title, so adding a schema file
  silently retyped `Proposal.requests` to `ArtifactCreatedPayload`; `--check` passed because the
  generator agreed with itself. Now per-document; `TestF13RefsResolvePerDocument` fails unfixed.
- **D2** the `/1` profile preimage was pinned by nothing, so shape-only tests would stay green
  while every historical `profile_digest` (which enters `D_R`) moved. Four digests now pinned.
- **D3** `/2` defaulted an absent capture status to `complete`; now null, keeping "captured
  nothing" distinct from "captured all that was asked".
- **D4** `assemble_trajectory` accepted the artifact index, provenance and capture status;
  `session.py` passed none, so each lane proved only its own half. Wired and asserted end-to-end.

Blocking, gate cannot close:

1. Merge order was **reconstructed**: both packages were built in one working tree, so no
   B-M4/A-M4 branches existed. Commits land B-then-A with correct attribution, but Leadership must
   accept the reconstruction or require a redo.
2. RF-95 not executed and not authorized here (needs an attributable live provider, forbids
   fake/cassette, single preregistered irreversible run).
3. TypeScript suite unmet in this environment (`tsc: not found`); no TS surface changed.
4. No independent review receipt exists; none is self-assertable.

Pre-existing doc-budget overruns: `milestones.md` (269), `SPEC.md` (253).


## 5c. M-5a status (drafted ahead of its entry gate)

ADR-0098 is **drafted and `proposed`, not accepted**: its entry gate (M-4 `CLOSED` on accepted
RF-95) is unmet, so it authorizes nothing. The A-M5A substrate work is implemented against it so
the contract can be reviewed against real code rather than prose, and is **not** `PACKAGE_READY`.

Implemented: `mhf.event/2` with the four typed authority fields, `/1` preimage byte-identical and
digest-pinned; role-derived authority with orchestrator forgery of capability/approval refused;
the eight live legacy kinds folded into the generated schema and `_V4_ONLY_KINDS` deleted, making
that schema the sole live vocabulary; `DEPRECATED_KINDS`/`READABLE_KINDS` with the eight historical
kinds readable and unwritable; the five semantic kinds allocated, reduced, and entering the state
digest, with `GoalDeclared` carrying digests only; `prev_digest` continuity across mixed chains;
explicit `writer_version` rollback. Kernel semantic diff is exactly zero.

Verified: 1481 passed / 8 skipped / 0 failed, including 35 A-M5A falsifiers and fresh-process
mixed-chain replay parity over a file-backed WAL. Eleven linters, codegen `--check`, and the
zero-Kernel-diff check pass.

A further generator defect surfaced while folding the vocabulary: duplicate `$defs` across schema
documents were resolved last-writer-wins, so a stale copy silently replaced the live definition
(`CostVector` diverged between `/1` and `/2`). The generator now refuses conflicting duplicates and
the shared definitions are `$ref`d from their owning document.

**`M-5A-BASE-v2` is NOT created.** Tag creation requires every G-M5A gate green, and RF-95, the
TypeScript suite, and independent review remain unmet.

## 6. Integration and RF-95

```text
READY -> IN_PROGRESS -> PR_OPEN -> REVIEW -> PACKAGE_READY -> MERGED -> GATE_ACCEPTED
```

Merge order is Dev B, then Dev A rebased on main, then the integrated gate; both packages become
`GATE_ACCEPTED` together or neither does. RF-95 may run only once both are `GATE_ACCEPTED`, every
gate in §7 is green, RF-38…RF-45 is green in CI, a non-trivial live task and its verifier are frozen
before execution, profile `/2` resolves `retention=standard` and `capture.required=true`, and the
provider is attributable rather than fake/cassette.

The single candidate must produce a terminal `mhf.trajectory/2`, exact model-I/O artifacts,
context/compaction/cache provenance as applicable, proof-honest reproducibility, a real workspace
diff, passing verifier receipt, durable WAL, and fresh-process reconstruction receipt. Failure is
preserved without manual repair and keeps M-4 open. Independent review plus Leadership acceptance
closes M-4.

## 7. Required verification

Every gate listed in [`AGENTS.md §2`](../../AGENTS.md), plus the full Python and TypeScript suites.
## 8. Explicit non-scope

- No event-envelope or event-kind change before accepted ADR-0098 and M-5a.
- No `agent.spawn`, topology, scheduler, memory, skills, or meta-control implementation in M-4.
- No Kernel semantic change, second runtime, upward dependency, or weakened falsifier.
- No historical ADR rewrite or movement/deletion of the historical `M-5-BASE` tag.
- No M-5a implementation before M-4 closure and ADR-0098 acceptance; no separate backlog or scratch
  Markdown outside the Clean Triad.
