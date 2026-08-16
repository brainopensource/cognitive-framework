# Sprint 8 · Lane A — Control Plane

**Owner:** Senior A · **Backlog:** `011 §5.1` · **Refinement:** PLANNED, NOT REFINED
**Write scope:** `vanguard/packages/runtime/**` · `vanguard/packages/ports/**` ·
`vanguard/packages/domain/evidence/**` (new) · `test/runtime/**`
**Do not touch:** `kernel/**` · `agency/**` (Lane B) · `benchmarkings/**`

---

## S8-A-01 — Decompose `execute_harness`

`root.py:634-809` is 175 lines performing eleven responsibilities. It builds **three `Kernel`
instances** with identical collaborators, because the segment loop is compensating for a missing
suspend/resume.

**Target shape:**

```
Runtime.compose(manifest) -> Harness          # exists and is good — keep unchanged
HarnessSession(harness, ports, task)          # NEW — owns wiring; ONE Kernel per run
HarnessSession.run() -> RunResult             # owns lifecycle, not wiring
```

- [ ] Failing test: `HarnessSession` constructs and runs one turn against injected fakes with **no
      live model, no bwrap, no network**
- [ ] Extract wiring into `HarnessSession`; construct exactly one `Kernel`
- [ ] Delete `_WitnessKernel` (`root.py:429-445`) — it exists only because `DispatchResult` does
      not carry the pending request through a suspension. Either add `request_digest` to
      `DispatchResult` or let the session hold the pending request
- [ ] Composition failures stay in `compose`; runtime failures stay in `run` (today a missing
      `bwrap` raises `CompositionError` *after* composition succeeded)
- [ ] Commit

**DoD:** one `Kernel` per run; `HarnessSession` unit-testable without I/O; `grep -c "Kernel(" root.py` → 1.

---

## S8-A-02 — Suspend / resume from the ledger

Today `root.py:738` loops `for _ in range(max_segments)` building a **fresh `Episode`** each time.
Consequences: the real turn bound is `max_turns × max_segments` (8×8=64); no-progress detection
resets every segment so `FT-02` livelock is undetectable across an approval; and resume depends on
live object identity (`_LayeredOperator._dialogue`) rather than the ledger.

- [ ] Failing test: suspend an episode for approval, **discard every in-memory object**, resume
      from the ledger, assert an identical `state_digest`
- [ ] Failing test: `max_turns` is a hard bound across an approval boundary
- [ ] Move suspension into the engine as terminal-with-continuation; re-entry reduces the ledger
      for that `episodeId`
- [ ] Delete the segment loop
- [ ] Commit

**Reuse:** `domain/ledger/reducer.py` (478 LOC) and `runtime/ledger/recovery.py` (221 LOC) already
reconstruct episode state for crash recovery. Approval suspension is the same mechanism with a
different trigger. **This is a reuse, not new code.**

---

## S8-A-03 — `RandomPort` + determinism-complete `ClockPort`

Without these, "replay" means state reconstruction only. Counterfactual re-execution — the thing
that makes the corpus *attributable* (`GTS-13C` Ch. 11 stage 2) — is unreachable, and the
progressive-vs-degenerating ratio cannot be computed at all.

- [ ] Failing test: two runs with the same `Recording` seed produce byte-identical trajectories
- [ ] `RandomPort` + fake/real pair; `ClockPort` completed for determinism
- [ ] Assert no module calls `random` or the system clock directly (architecture test)
- [ ] Commit

**~150 LOC total.** It unblocks Phase 4 `V5-A`.

---

## S8-A-04 — `RecordCorrection` calls `parse_wire`

`runtime/service/service.py:236` `_cmd_RecordCorrection` appends a loosely typed payload and never
calls `parse_wire("CorrectionRecord", ...)`. The wire contract already enforces the reason-code
enum and the rule that `style`/`architecture_preference` ⇒ `scope ∈ {user, team, repo}`.

- [ ] Failing test: a correction with `reasonCodes: ["style"]` and `scope: "general"` must be
      **rejected**
- [ ] Bind the parser; reject on failure
- [ ] Assert no promotion path exists from a correction (`MEM-1`, `D-07`)
- [ ] Commit

**1 day.** Open since the Beta audit.

---

## S8-A-05 — `Claim` as a `domain/` type · **DO THIS EARLY**

This is a **format lock** (`L-1`). Every run after it records evidence in the final shape; every
run before it needs migration.

- [ ] Failing test: a `Claim` with an empty `invalidationConditions` array **fails at parse**
- [ ] Failing test: a claim whose `substrate_profile` digest has changed evaluates as **stale
      without human review** (`C-12`, `INV-2`)
- [ ] Implement pure, no-I/O, in `domain/evidence/claim.py`: `subject`, `predicate` (scoped),
      `value`, `protocol`, `evaluator`, `environment_profile`, `substrate_profile`, `uncertainty`
      (interval, never a point estimate), `validity`, `invalidationConditions` (minItems 1, ≥1
      automatic)
- [ ] Add `support_count`, `last_corroborated_at`, `protection_class` — **recorded, not consumed**.
      Same argument `T4.11` already accepted for the competence prior: recording now costs nothing;
      retrofitting later costs a corpus migration. Hedges the library-drift failure mode
- [ ] Coordinate with Joint on the `VG-04` wire amendment
- [ ] Commit

---

## Stop conditions

| Signal | Action |
|---|---|
| Resume needs a live object carried across the boundary | **Stop.** That is restart, not resume |
| `Claim` needs a field that cannot state what would refute it | **Stop.** `ADR-0018` |
| Decomposition requires a `kernel/` change | **Stop.** ADR required |
