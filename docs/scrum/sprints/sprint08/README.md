# Sprint 8 (Wave 7) — Recursion, Resume & Load-Bearing Manifests

**Phase:** 3 · **Wave:** W7 · **Timebox:** 2–3 weeks · 3 lanes + Joint
**Backlog:** `docs/reviews/doing/011_master_backlog_phase3_V043-REV.md §5`
**Refinement status:** **PLANNED, NOT REFINED.** Task shapes and DoDs are firm; step-level
breakdowns are written at sprint planning once Sprint 7's deletions have landed. Do not treat
estimates here as commitments.

---

## 1. The sentence this sprint makes true

> **A parent episode spawns a child under an attenuated grant and a child lease; the child's
> exploration never enters the parent's context; and the whole run reconstructs from the ledger
> alone.**

## 2. Why this is the centre of the programme

`GTS-13C §4.3` states the thesis: *"An agent is an Episode. A team is an Episode that spawns
Episodes. A department is an Episode that spawns Episodes that spawn Episodes. One type, one
budget algebra, one attenuation rule, one event stream — at every level of coordination."*

`agency/episode/engine.py:17-19` says the opposite: *"Depth-1… this engine never re-enters
itself."* Recursion is **not implemented**. `depth` is telemetry passed into `EffectRequest`.

**The good news, and why this is a two-week item rather than a quarter:** every hard part already
exists.

| Requirement | Already built |
|---|---|
| Child scope ⊆ parent | `kernel/attenuation.py` — property-tested monotone |
| Child lease on parent's remainder | `kernel/budget.py` `Governor` — conservation-tested |
| Depth as a budget dimension | `BudgetVector` already carries it |
| Child events nest under the parent | `EventEnvelope.causationId` |
| Suspend/resume from the ledger | `domain/ledger/reducer.py` + `runtime/ledger/recovery.py` already do this for crash recovery |

**Recursion is not new machinery. It is the call site that was never written.** Approval suspension
is the same mechanism as crash recovery with a different trigger.

## 3. What the field says this is worth

Context isolation via subagents is the mechanism `VG-03 §5.2` calls *"the one no static graph can
express"* and `VG-03 §10.3` calls *"the primary mechanism — the cheapest way to keep a context
window clean is never to put the exploration in it."*

**Cite carefully.** The published 90.2% figure is a multi-agent research system versus a
single-agent baseline on **one vendor's internal research eval** — not a public benchmark, and
unrelated to capability leases. The 84% token reduction is **context compaction** on a 100-turn
eval, not subagents. Both are real; neither says what a careless summary makes them say. See
`002 §2.1d`.

## 4. Lanes and write scopes

| Lane | Owner | Write scope |
|---|---|---|
| **A — Control Plane** | Senior A | `runtime/**` · `domain/evidence/**` (new) · `ports/**` · `test/runtime/**` |
| **B — Workload & Evidence** | Senior B | `agency/episode/**` · `agency/context/**` · `adapters/**` · `agency/manifests/**` |
| **C — Measurement & Lab** | Senior C | `runtime/ledger/projections.py` (read-only elsewhere) · `benchmarkings/**` · `tools/002_LLM_API_MOCK/**` |
| **Joint** | Leads | ADRs · `VG-04` wire amendments for `Claim` |

> **Note the exception.** Lane B edits `agency/episode/engine.py` this sprint — the only sprint in
> Phase 3 where that is permitted, and only for `spawn`. Every edit is priced against `ADR-0060`:
> it must add **no domain vocabulary**.

## 5. Dependency graph

```
S8-A-01 decompose execute_harness ─► S8-A-02 resume-from-ledger ─► S8-B-01 spawn
                                                                └─► S8-B-05 context isolation
S8-B-02 CompactionStrategy ─► turns S7-B-03 metamorphic test GREEN
S8-B-03 ModelRouter        ─┘
S8-A-03 RandomPort/ClockPort  (independent, unblocks Phase 4 V5-A)
S8-A-04 RecordCorrection parse_wire  (independent, 1 day)
S8-A-05 Claim domain type            (independent — but the FORMAT LOCK, do it early)
S8-B-06..10 ACI gifts                (independent, parallelisable, high ROI)
```

## 6. Exit gate

- [ ] Property: child grant strictly narrows verb, selector, constraints, expiry, uses, budget
- [ ] Property: budget conserved across a two-level spawn; child overrun debits the parent
- [ ] Test: a child's intermediate turns are **absent** from the parent's compiled context
- [ ] Test: suspend → resume reconstructs an identical `state_digest` **from the ledger alone**,
      with no live object carried across
- [ ] Test: `max_turns` is a hard bound **across** an approval boundary (today it is per-segment,
      so the real bound is 8×8=64)
- [ ] `S7-B-03` metamorphic test flips from expected-failure to **green**
- [ ] `Claim` with an empty invalidation array fails at parse; a substrate-digest change marks a
      claim stale **without human review** (`C-12`)
- [ ] Cache-hit rate recorded as a CI metric over a fixed replay
- [ ] `check_tcb_budget.py` PASS — **recursion must not grow the kernel**

## 7. Stop conditions

1. `spawn` requires a **new kernel primitive** → stop. Everything needed exists; if it does not,
   that is an architecture finding worth more than the feature.
2. Resume requires retaining a live object across the boundary → stop. That is restart, not
   resume, and it will break the moment the daemon serves it.
3. Any `agency/episode/` edit introduces a domain noun (`file`, `repo`, `patch`, `test`) →
   **`ADR-0060` violation**; stop.
4. `Claim` needs a field that cannot state what would refute it → stop. `ADR-0018`: *"a claim that
   cannot state its own refutation is not a claim."*
