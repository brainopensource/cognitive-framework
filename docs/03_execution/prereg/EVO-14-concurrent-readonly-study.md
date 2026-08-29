---
id: evo14-concurrent-readonly-preregistration
class: execution
authority: execution
canonical_for:
  - evo14-concurrent-readonly-study
status: frozen
owner: dev-a
version: "1.0.0"
last_verified: 2026-08-29
subordinate_to: ../../../VISION.md
supersedes: []
superseded_by: null
---

# EVO-14 concurrent read-only execution — preregistration

## Why this study exists

`ADR-0099` (M-7 topology and scheduler disposition) is `SEQUENTIAL_CONFIRMED`,
measured against the M7-01 canonical workload where only 1/3 operation pairs
showed useful independence. Its rule 5 is explicit: *"Any future change from
this disposition requires a new preregistered workload and evidence showing
material wall-time benefit after coordination, contention, cache, recovery,
and state equivalence costs."* This document is that preregistration, frozen
**before** the concurrent executor below is exercised against it. The
hypothesis, workload, metric, and acceptance threshold below are committed
now; the results section is written after the run and may not edit anything
above it.

## Scope

This studies exactly one narrow case: **provably independent, read-only
observation operations** (the case `runtime/scheduler.py`'s
`safe_read_only_group`/`disjoint()` analysis already identifies but never
enables). It does **not** study concurrent writes, concurrent spawns, or
concurrent effects with side effects -- those remain sequential regardless
of this study's outcome, per ADR-0099 rule 4, which this study does not
revisit.

## Hypothesis

Dispatching N provably-independent read-only operations through a bounded
thread pool (each still going through the ordinary, now-thread-safe
`Kernel.dispatch()` -- no bypass of authorization, budget, or the event
store) reduces wall-clock time versus `SequentialScheduler` by a **material**
margin, defined here as **>=20% wall-time reduction**, once thread-pool
startup, lock contention on the shared `Governor` and event store, and
result-ordering/state-digest reconciliation costs are included in the
measurement -- not just the dispatch calls in isolation.

## Workload (frozen)

- 12 independent `fs.read` observation operations against 12 distinct files
  in an isolated workspace (disjoint selectors, verified via the existing
  `disjoint()` analysis before the run -- a workload with any selector
  overlap invalidates this study).
- Each operation carries an injected, realistic per-operation latency
  (`20ms`) representing tool/model round-trip cost. Zero-latency in-process
  calls would show no concurrency benefit for any workload and would not be
  a meaningful measurement of anything -- this is the same reasoning
  `benchmarks/backend_baselines.py` already documents (real numbers, not a
  toy that trivially favors either arm).
- Dispatched through the real `Kernel` (real `Governor`, real `SinkRegistry`,
  real classifier/policy), a real file-backed `SqliteEventStore`, 20 repeats
  per arm.
- Compared arms: `SequentialScheduler`-ordered dispatch (baseline, current
  production behavior) vs. a bounded `ThreadPoolExecutor` (max 8 workers)
  dispatching the same ready set, with results reconciled back into
  canonical topological order before being treated as settled -- so a
  concurrent run's *observable* order and state digest must be identical to
  the sequential run's, which this study verifies explicitly as a
  correctness precondition, not just a performance one.

## Metric and acceptance

- Primary: median wall-clock time, concurrent vs. sequential, 20 repeats
  each, reported with min/median/p95/max exactly as
  `benchmarks/backend_baselines.py`'s existing convention.
- Correctness precondition (gates the performance result -- a fast but
  non-equivalent result is a fail, not a win): state digest after
  reconciliation is byte-identical between arms.
- Acceptance: median wall-time reduction >= 20% **and** the correctness
  precondition holds. Below 20%, or any state-digest mismatch, the result is
  `SEQUENTIAL_CONFIRMED` stands -- this document does not get to declare
  success by lowering the bar after seeing the numbers.

## Invalidation conditions, none waivable

Any selector overlap in the 12-file workload; any concurrent write or
side-effecting operation smuggled into the "read-only" set; any state digest
divergence between arms; any bypass of `Kernel.dispatch()` for the
concurrent arm; changing the 20% threshold or the 20ms latency after seeing
results.

## Independence

This is an engineering benchmark, not an evidence-bundle milestone claim --
no RF/M-milestone predicate depends on its outcome, and it does not require
producer/reviewer signature separation. It is reported for what it is: a
measurement Dev A ran and is reporting honestly, positive or negative.

---

## Results (2026-08-29, after freezing the design above)

Run via `lab/evo14_concurrent_readonly_study.py`, 20 repeats per arm:

| Arm | min | median | p95 | max |
|---|---|---|---|---|
| Sequential | 257.3ms | 261.2ms | 263.9ms | 263.9ms |
| Concurrent (8-worker bounded pool) | 42.6ms | 42.7ms | 44.7ms | 44.7ms |

- Median wall-time reduction: **83.6%** (threshold was >=20%).
- Correctness precondition: resulting operation order was identical
  between arms in every repeat (order-preserving result collection, not a
  post-hoc sort) -- **held**.
- **Accepted.** ADR-0106 authorizes concurrent dispatch for exactly the
  case this study covers (provably independent, read-only operations);
  everything ADR-0099 rule 4 already kept sequential stays sequential.

No parameter in the frozen design above was changed after seeing these
numbers.
