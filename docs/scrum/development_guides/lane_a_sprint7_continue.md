# Copy-paste prompt — Senior Dev A (Lane A, Control Plane)

Finish remaining **Sprint 7 Lane A**, then **plan** Sprint 8 Lane A and **implement** it if your S7 exit for Lane A is met.

You are Senior Developer A. Authority: `docs/reviews/doing/011_master_backlog_phase3_V043-REV.md` **§4.1 then §5.1**. Lane kits are the source of steps and DoD (not this prompt):

- `docs/scrum/sprints/sprint07/lane-a-control-plane.md`
- `docs/scrum/sprints/sprint07/README.md` (Lane A items in the exit gate)
- `docs/scrum/sprints/sprint08/lane-a-control-plane.md` (DoDs firm; kit is **PLANNED NOT REFINED**)
- `docs/scrum/sprints/sprint08/README.md`
- `docs/scrum/development_guides/00_architecture_decisions_for_implementers.md`
- `docs/scrum/development_guides/01_layer_boundaries_and_ci_rules.md`
- `docs/scrum/development_guides/05_tdd_workflow_and_commit_conventions.md` (TDD loop; **ignore** that guide’s old per-task branch naming)

`ROADMAP` is a mirror. Flip **011** status when the DoD **command** for that row passes. Do not invent extra tasks.

---

## HARD RULE — git (not a suggestion)

- **Do not** use git worktrees, extra branches, or stash as isolation.
- **All work lands on the currently active branch: `sprint7-8/integration`.** Confirm with `git branch`. If you are already on it, **stay**. Do not create `sprint07/…` or `sprint08/…` feature branches.
- The Project Lead merges that branch to **main** only after **Sprints 7 AND 8**.
- Version control = **commits only**. Separate lanes by **COMMIT PREFIX**, never by branch.
- Commit format: `[lane-a] S7-A-xx: …` or `[lane-a] S8-A-xx: …`
- **Never `git stash -u`** on this shared tree (it previously swept other lanes’ uncommitted work).
- If another lane has uncommitted files in **your write scope**, do not overwrite: wait, or commit **your** files only (`git add` specific paths). **Never `git add -A`** if mixed dirty files exist.
- You **may** `git add` only your write-scope files and commit even if other lanes have dirty files elsewhere.
- Do not revert other lanes’ commits. If you need undo, revert **only** your own `[lane-a]` commits.

---

## Mission

1. Complete every remaining **Sprint 7** Lane A row (see below). **S7-A-07 is DONE — skip it.**
2. When **your** S7-A DoD commands pass, write a **short plan note** for Sprint 8 Lane A (order, risks, hand-offs), then implement S8-A-01…05.
3. You need **not** wait for Lane C to delete all runners or for Joint **SEC-01**.
4. Do **not** implement **spawn** (Lane B). If B already claimed S8-B spawn files, do not fight them unless those files are in **your** write scope.

---

## Sprint 7 remaining (A-07 skip)

Order: **A-01 → A-02 → A-03 → A-04 → A-05 → A-06**. TDD + `test/broken/` counterparts for **your** rules. Steps and stop conditions live in the S7 lane-a kit.

| ID | Intent |
|---|---|
| S7-A-01 | Lattice-completeness CI |
| S7-A-02 | No `subprocess` outside sandbox |
| S7-A-03 | No evaluator import (agency/runtime) |
| S7-A-04 | DELETE `runtime/loops/` |
| S7-A-05 | DELETE `runtime/coordination.py` |
| S7-A-06 | Remove hardcoded compose values |

**Write scope (S7):** `tools/check_boundaries.py`, `tools/repo_paths.py`, `vanguard/packages/runtime/**`, `test/runtime/**`, `test/broken/` counterparts for **your** rules.

**Do not touch:** `kernel/**`, `agency/episode/**`, `benchmarkings/**`, `docs/main_v4/**`.

`check_boundaries.py` is **shared with Lane C**. C owns the `benchmarkings/**` import rows. You **add** lattice / subprocess / evaluator rows. **Do not delete C’s S7-C-01 rule.** If you edit that file, **commit immediately** with `[lane-a]` so C can continue.

**S7 Lane A DoD:** run the commands in `sprint07/lane-a-control-plane.md` “Definition of done for the lane” and the README exit gate items that are Lane A’s (boundaries, broken counterparts, TCB, empty `runtime.loops` / `EpisodeCoordinator` grep). Do not own C’s planted-degenerate-benchmark or B’s alias/unread-component boxes.

If Active MVP Contract / dogfood receipts were purged: cite `req_id` from **GTS-13C / VG-03 / existing ADR** if the JSON is missing; **do not block the whole sprint** — note it in the PR body. **Do not restore** a 951-line contract unless Joint asks.

---

## Sprint 8 Lane A (after S7-A rows done)

Plan first (short note: order, risks), then implement. Kit DoDs are firm even though the kit is unrefined.

| ID | Intent |
|---|---|
| S8-A-01 | `HarnessSession` / one `Kernel` |
| S8-A-02 | Suspend/resume from ledger |
| S8-A-03 | `RandomPort` / `ClockPort` |
| S8-A-04 | `RecordCorrection` `parse_wire` |
| S8-A-05 | `Claim` domain type — coordinate with Joint **S8-J-01**; if wire is not ready, implement behind tests but **do not merge format lock** without TL |

**Write scope (S8):** `vanguard/packages/runtime/**`, `vanguard/packages/ports/**`, `vanguard/packages/domain/evidence/**` (new), `test/runtime/**`. Still no kernel; no `agency/**` (Lane B); no `benchmarkings/**`.

Suggested plan order (adjust in the note if evidence says otherwise): A-05 early (format lock, gated on Joint wire), A-01 → A-02 (B’s spawn depends on resume), A-03 and A-04 independent.

---

## Working style

- TDD: failing test (and broken counterpart for gates) before implementation.
- Deletions are deletions (no `_deprecated`). Git is the archive.
- Zero kernel mutation. If a task needs `kernel/`, stop and escalate (`ADR-0054`).
- Add **rows** to `check_boundaries.py`; do not rewrite the checker.
- Status in 011: only when the DoD command for that row actually passes.

When S7-A is done, leave the S8 plan note where the team will see it (PR body and/or a short comment on the lane kit — do not rewrite `docs/main_v4`).
