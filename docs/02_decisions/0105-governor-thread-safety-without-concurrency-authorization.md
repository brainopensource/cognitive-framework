---
id: adr-0105-governor-thread-safety-without-concurrency-authorization
adr: 0105
class: decision
authority: binding-decision
canonical_for:
  - kernel-budget-thread-safety
status: accepted
owner: repository-governance
version: "1.0.0"
last_verified: 2026-08-29
accepted_date: 2026-08-29
extends:
  - ADR-0099
supersedes: []
superseded_by: null
---

# ADR-0105 — `Governor` thread safety without concurrency authorization

## Status

Accepted 2026-08-29.

## Context

Auditing `vanguard/packages/kernel/budget.py` for EVO-07/EVO-14 (backend
evolution plan: async scheduling, concurrent lineage execution) found that
`Governor.reserve()` is check-then-act on `self._held` with no
synchronization: it reads `remaining(dimension)` to decide whether to grant
a reservation, then mutates `_held` afterward. Two threads calling
`reserve()` concurrently can both pass the ceiling check against the same
stale read and both commit, oversubscribing the ceiling — a real
budget-conservation violation (`K-07`), reproduced deterministically in
`test/kernel/test_governor_concurrency.py` by widening the race window.

Separately: ADR-0099 records M-7's disposition as `SEQUENTIAL_CONFIRMED`
with **no active concurrency authorization**. `runtime/scheduler.py`'s
`SequentialScheduler` is the only scheduler wired into any execution path;
`ready_operations`/`safe_read_only_group` are dependency-readiness analysis
only, explicitly documented as "not a concurrent executor."

## Decision

1. `Governor.reserve`, `.commit`, and `.release` now hold an internal
   `threading.Lock` for their full body, not just the mutating tail — a
   caller that dispatches from multiple threads gets the same conservation
   guarantee a single-threaded caller already had.
2. This is a **defensive property**, not a scheduling change. No caller in
   this tree currently invokes `Governor` from more than one thread at a
   time; `SequentialScheduler` remains the only wired scheduler. This ADR
   does **not** authorize, enable, or wire concurrent effect dispatch, and
   does not amend ADR-0099's `SEQUENTIAL_CONFIRMED` disposition.
3. Building and enabling an actual concurrent scheduler/executor (parallel
   dispatch of independent ready operations) requires its own successor
   ADR that explicitly amends ADR-0099 — that ADR must additionally address
   idempotency, cancellation, child-failure handling, and shared-store
   correctness under real concurrency, none of which this change touches.

## Why

The kernel neutrality gate (`RF-98`) treats any diff to
`vanguard/packages/kernel/` against its baseline as a change requiring
either a revert or an ADR classifying it — by design, kernel changes are
rare and deliberate. This change is generic thread-safety with no new
domain knowledge (`check_kernel_neutrality.py`'s structural half, which
scans for pack/domain verb leakage, remains `neutral`); it earns the ADR
because the gate requires one for *any* kernel diff, not because it
introduces a domain concept.

## Consequences

- `test/kernel/test_governor_concurrency.py` proves the fix: an unlocked
  variant of `Governor` lets two threads both win a reservation that only
  one ceiling's worth of budget could satisfy; the locked version correctly
  denies the second.
- `RF-98`'s historical-diff check will report `budget.py` as changed
  against its configured baseline (`M-5A-BASE-v2` — itself already recorded
  as contaminated/unpublished by ADR-0102) until a release owner moves the
  baseline forward as part of their own process; that is an external,
  release-owner action this ADR does not perform (moving or tagging a
  baseline is explicitly reserved, per the active execution board).
- A future concurrent-scheduler ADR can now build on a `Governor` that is
  already safe to call from multiple threads, without needing to
  re-litigate budget-conservation correctness at the same time it
  litigates scheduling.

## Relevant code

- `vanguard/packages/kernel/budget.py` — `Governor.reserve`/`.commit`/`.release`.
- `test/kernel/test_governor_concurrency.py` — the falsifying/verifying tests.
- `vanguard/packages/runtime/scheduler.py` — `SequentialScheduler`, the only
  wired scheduler; unaffected by this change.
