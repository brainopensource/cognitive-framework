---
id: adr-0106-evo14-readonly-concurrency-authorized-by-measurement
adr: 0106
class: decision
authority: binding-decision
canonical_for:
  - evo14-readonly-concurrency-authorization
status: accepted
owner: dev-a
version: "1.0.0"
last_verified: 2026-08-29
accepted_date: 2026-08-29
extends:
  - ADR-0099
supersedes: []
superseded_by: null
---

# ADR-0106 — EVO-14 read-only concurrency, authorized by measurement

## Status

Accepted 2026-08-29. Narrowly amends ADR-0099's `SEQUENTIAL_CONFIRMED`
disposition for exactly one case; does not touch anything else ADR-0099
decided.

## Context

ADR-0099 rule 5: *"Any future change from this disposition requires a new
preregistered workload and evidence showing material wall-time benefit
after coordination, contention, cache, recovery, and state equivalence
costs."* That study is now done. Preregistration:
`docs/03_execution/prereg/EVO-14-concurrent-readonly-study.md`, frozen
before the run. Runner: `lab/evo14_concurrent_readonly_study.py`.

**Result**: 12 provably-independent `fs.read` operations (disjoint
selectors, verified before the run), each with an injected 20ms round-trip
latency, dispatched through the real `Kernel` (real `Governor`, real
classifier/policy, real adapters), 20 repeats per arm:

| Arm | Median wall time |
|---|---|
| Sequential (`SequentialScheduler`, current production behavior) | 261.2ms |
| Concurrent (bounded thread pool, canonical-order result reconciliation) | 42.7ms |

**83.6% median wall-time reduction**, against a preregistered acceptance
threshold of >=20%. Correctness precondition held: the concurrent arm's
resulting operation order was byte-identical to the sequential arm's in
every repeat (deterministic join via order-preserving result collection,
not a post-hoc sort).

Separately, `vanguard/packages/runtime/scheduler.py` already contains
`AsyncGraphScheduler`/`execute_graph_async` (tagged EVO-14, added
concurrently with this study by the parallel implementation lane) -- a
real, generic, wave-based concurrent executor with causal-predecessor
ordering and selector-disjointness checking, currently unused by any
production path (`root.py` still constructs only `SequentialScheduler`).

## Decision

1. Concurrent dispatch of **provably independent, read-only** operations
   (disjoint selectors per `domain/selectors/independence.disjoint`,
   non-mutating sink class, no shared causal predecessors -- exactly
   `scheduler.safe_read_only_group`'s existing definition) is authorized.
   This is the only case this ADR authorizes.
2. **Everything ADR-0099 rule 4 already said stays sequential remains
   sequential**: writes, spawning, promotion, shared or unknown sinks,
   causal predecessors, overlapping selectors, incomplete timing, and
   unsettled effects. This ADR does not reopen that rule and does not
   authorize concurrent writes even when their selectors happen to be
   disjoint.
3. A caller implementing this must preserve every property this study's
   correctness precondition and ADR-0099 rule 2 require: results
   reconciled into canonical (not completion) order before being treated
   as settled; every dispatch still goes through the ordinary
   `Kernel.dispatch()` (no bypass of authorization, budget, or the event
   store); no second execution runtime.

## A finding this ADR does not resolve

`AsyncGraphScheduler.decide()` (`scheduler.py`) currently parallelizes
**any** pair of operations with disjoint selectors regardless of
`read_only`/sink class -- `test/contracts/test_evo14_async_scheduler.py::test_disjoint_resources_scheduled_in_parallel`
uses `sink="privileged"` (a write-class sink) and asserts `parallel=True`.
That is broader than both this ADR authorizes and what ADR-0099 rule 4
still requires (writes stay sequential regardless of selector
disjointness). It is currently inert -- unwired from every production
path -- so this is not a live violation, but wiring `AsyncGraphScheduler`
into `root.py` as-is would be one. Closing that gap requires either
narrowing `AsyncGraphScheduler.decide()` to the read-only case this ADR
actually authorizes, or a second preregistered study specifically for
disjoint-selector writes before that broader parallelization is wired
anywhere. Left as an open item for whichever lane wires this scheduler
into a real execution path.

## Consequences

- The read-only case now has both a decision procedure
  (`safe_read_only_group`) and measured evidence that acting on it is
  worthwhile, satisfying ADR-0099 rule 5 for this narrow slice.
- Wiring this into the M-7 topology execution path (`root.py`'s
  `SequentialScheduler` call site) is separate integration work, not done
  by this ADR -- this ADR authorizes the capability; it does not activate
  it.
- ADR-0099's disposition for every other case (writes, spawns, promotion,
  ambiguous sinks) is unchanged and still binding.

## Relevant code

- `docs/03_execution/prereg/EVO-14-concurrent-readonly-study.md` -- frozen
  preregistration.
- `lab/evo14_concurrent_readonly_study.py` -- the study runner.
- `vanguard/packages/runtime/scheduler.py` -- `safe_read_only_group`,
  `AsyncGraphScheduler`, `execute_graph_async`.
- `vanguard/packages/kernel/budget.py` -- the `Governor` thread-safety this
  and any future concurrent dispatch depends on (ADR-0105).
