# Sprint 8 · Lane B — Workload & Evidence

**Owner:** Senior B · **Backlog:** `011 §5.2` · **Refinement:** PLANNED, NOT REFINED
**Write scope:** `agency/episode/**` · `agency/context/**` · `agency/manifests/**` · `adapters/**`
**Do not touch:** `kernel/**` · `runtime/**` (Lane A) · `benchmarkings/**`

> **This is the only sprint in Phase 3 where `agency/episode/` may be edited**, and only for
> `spawn`. Every edit is priced against `ADR-0060`: it must add **no domain vocabulary**. If you
> find yourself typing `file`, `repo`, `patch` or `test` in the engine, stop.

---

## S8-B-01 — `EpisodeEngine.spawn` · **the centre of the sprint**

Deliberately small. This is not a subagent framework; it is one method.

- [ ] Property test first: child grant strictly narrows verb, selector, constraints, expiry, uses,
      budget — **reuse `kernel/attenuation.py`, do not reimplement**
- [ ] Property test: budget conserved across two levels; child overrun debits the parent —
      **reuse the `Governor` lease tree**
- [ ] Test: `depth` denial at the limit returns a **typed result**, not an exception
- [ ] Test: child events carry `causationId` = parent episode and nest in projections
- [ ] Test: the return value is text or a structured payload — **never a handle, never shared
      mutable state**
- [ ] Test: a child failure is a typed result, not an exception propagated into the parent's loop
- [ ] Test: per-branch workspace destroyed in `finally`, **including on creation failure** (`N-16`)
- [ ] Implement `spawn`
- [ ] Commit

**Explicitly deferred:** parallel branch exploration, independence groups, rankers. Serial
recursion first — that is where the isolation benefit lives, and concurrency is unmeasurable
without a noise floor (`C-04` needs `T8.1`).

---

## S8-B-05 — Operator context isolation

- [ ] Failing test: a child's intermediate turns are **absent** from the parent's compiled context;
      only the child's return appears in the parent's L5
- [ ] Child gets a fresh `ContextCompiler` prefix
- [ ] Commit

> `VG-03 §10.3`: *"The cheapest way to keep a context window clean is never to put the exploration
> in it."* This is the payoff for `S8-B-01`.

---

## S8-B-02 — `CompactionStrategy` protocol + registry

Today the compiler implements `result_eviction` while every manifest declares
`{"kind":"recency-window","maxItems":64}`. **The manifest names one strategy and the code runs
another.**

- [ ] `CompactionStrategy` protocol in `ports/`
- [ ] Register `result_eviction` (existing behaviour) and `recency_window`
- [ ] Selected by `context_policy`, resolved and **frozen at composition** (`A-11`)
- [ ] **`S7-B-03`'s metamorphic test flips to green** — that is the DoD
- [ ] Commit

---

## S8-B-03 — `ModelRouter` protocol + registry

`adapters/models/routing.py` (107 LOC) **exists and is never instantiated.**

- [ ] `ModelRouter` protocol; wire the existing module
- [ ] Selected by `routing_policy`; frozen at composition
- [ ] Test: changing `routing_policy` changes the model selected
- [ ] Commit

> This is also where `meta_loop.py`'s tier-escalation idea lands — **as data**, not as a loop.

---

## S8-B-04 — `approval_policy` manifest component

- [ ] New component kind; replaces the hardcoded `approval_required_above="low"`
      (`root.py:693`, marked `TODO(S8-B-04)` in Sprint 7)
- [ ] Test: two packs with different approval policies behave differently
- [ ] Commit

---

## S8-B-06 … S8-B-10 — The ACI gifts (parallelisable, highest quality-per-line in the programme)

Each is an **adapter behaviour plus a tool-schema line**. None adds an atom (`VG-03 §7.4` freeze
holds). Source: SWE-agent ACI paper; see `010 §2`.

| ID | Gift | DoD |
|---|---|---|
| `S8-B-06` | **Paginated `fs.read`** — default 100 lines + offset; prompt states the convention | A 5,000-line file returns 100 lines + a continuation hint, not a dump |
| `S8-B-07` | **Succinct `fs.search`** — file hits first, capped snippets | Search returns a ranked file list, not concatenated bodies |
| `S8-B-08` | **Empty-output acknowledgement** on `proc.exec` | A silent command returns explicit text, not `""` — models loop on silence |
| `S8-B-09` | **Lint-on-patch as an observation receipt** | A syntax failure is a **receipt**, never a verdict. `A-05` preserved: this must not touch the evaluator |
| `S8-B-10` | **`maxTurns` from `budget_policy`** | A pack declaring 32 turns runs 32 turns; the engine reads the frozen policy (`D-12`) |

> `S8-B-09` is the one to get right. A lint result that becomes a pass/fail verdict is a second
> judge. It is an **observation**, recorded like any other receipt.

---

## Stop conditions

| Signal | Action |
|---|---|
| `spawn` requires a new kernel primitive | **Stop.** Everything needed exists; if not, that is an architecture finding |
| An `agency/episode/` edit introduces a domain noun | **Stop.** `ADR-0060` |
| A compaction strategy needs to rewrite L1–L3 | **Stop.** `VG-03 §10.2`; that is a cache-cost explosion (and SWE-agent's `LastNObservations` is the known example) |
| An ACI gift needs a new verb | **Stop.** `D-04`: registry rows, never engine branches |
