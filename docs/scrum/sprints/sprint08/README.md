# Sprint 8 (Wave 7) — Recursion, Resume & Load-Bearing Manifests

**Phase:** 3 · **Wave:** W7 · **Timebox:** 2–3 weeks · 3 lanes + Joint
**Backlog:** `docs/reviews/doing/011_master_backlog_phase3_V043-REV.md §5`
**Target branch:** `sprints7-8/integration` — **the one integration branch.** `sprint07/integration`
is deleted (local and `origin`); it held zero unique commits. Do not recreate it.
**Refinement status:** **REFINED AND OPEN (2026-08-16).** Opened by TL + PL after Sprint 7
engineering closed at `248be91`. Sprint 7 evidence:
`docs/scrum/sprints/sprint07/evidence/s7-close-receipt.md`.

---

## 0. Start here — first task per lane

**Developers A, B and C may begin immediately.** These three tasks are disjoint in files and have no
dependency on each other. Take your lane's row, run its DoD command, commit with your lane prefix.

| Lane | First task | One-line scope | DoD command |
|---|---|---|---|
| **A** | **`S8-A-01`** — decompose `execute_harness` into `compose / HarnessSession / run`; one `Kernel` per run (three are built today); delete `_WitnessKernel` | `runtime/root.py`, `test/runtime/**` | `python3 -m unittest discover -s test/runtime -t .` → OK, and `HarnessSession` constructs with **fakes only, no live model** |
| **B** | **`S8-B-01a`** — finish `spawn`'s budget half: set `parent_lease` on child effect requests so the `Governor` lease tree is real; add the two missing property tests | `agency/episode/engine.py`, `test/agency/test_episode_spawn.py` | `python3 -m unittest test.agency.test_episode_spawn -v` → OK **including** `budget conserved two levels deep` and `child overrun debits the parent` |
| **C** | **`S8-C-02`** — cache-hit rate over a fixed replay (**`S8-C-01` is already done — see §0.1**) | `benchmarkings/**`, `tools/telemetry/**` | `python3 -m unittest discover -s test/lab -t .` → OK, and the metric emits from a cassette replay with **no network** |
| **Joint** | `S8-J-04` (node-present suite) | Leads only | — |

### 0.1 `S8-C-01` is already delivered — do not rebuild it

`EpisodeDepthProjection` (`runtime/ledger/projections.py:117`) already **is** the `S8-C-01` row.
Lane A landed it under `S7-A-05`. It derives depth from the `causationId` chain, stores nothing,
returns `None` rather than fabricating a root when the chain leaves the ledger, and applies the
`Atom/Molecule/Polymer/Cell/Body` labels **in the projection over an integer** — no class hierarchy,
exactly as `GTS-13C §4.3` requires. Tested in `test/runtime/test_episode_depth_projection.py`.

**`S8-C-01` = `[DONE]`. Lane C starts at `S8-C-02`.** The file sits in Lane A's Sprint 7 scope and
Lane C's Sprint 8 scope: Lane C owns it from now on; Lane A raises a PR comment rather than editing.

### 0.2 What runs in parallel, and what waits

```
FREE TO RUN NOW, IN PARALLEL — no cross-lane dependency
  A: S8-A-01 (root.py)            B: S8-B-01a (engine.py)      C: S8-C-02 (benchmarkings)
  A: S8-A-03 RandomPort/ClockPort  B: S8-B-04 approval_policy   C: S8-C-03 prefix-miss
  A: S8-A-04 RecordCorrection      (B-06..B-10 ACI: DONE)       C: S8-C-04 LAM regex
  A: S8-A-05 Claim  <-- do EARLY, it is the format lock

WAITS
  S8-A-02 resume-from-ledger   BLOCKED BY S8-A-01 (needs HarnessSession to re-enter)
  S8-J-01 VG-04 Claim wire     BLOCKED BY S8-A-05 (a note only until A-05 lands)
```

**The one hard cross-lane rule this sprint.** Lane A decomposes `root.py`; Lane B owns
`agency/episode/engine.py`. **Lane A must not delete, relocate or inline `EpisodeEngine.spawn`**
while decomposing. If `S8-A-01` appears to require touching `spawn`, that is a hand-off to Lane B,
not a quick edit. Conversely Lane B does not edit `root.py` — `S8-B-04` clears the
`TODO(S8-B-04)` at `root.py:740` **through a PR comment to Lane A**, not directly.

### 0.3 LLM rule — binding on all three lanes

1. **`tools/002_LLM_API_MOCK` first.** Every test and every DoD command in this sprint runs against
   the mock. No exceptions.
2. **Ollama if present** on the machine. Do not install it to satisfy a row.
3. **OpenRouter free tier only.** `band=free`.
4. **Never `band=top`.** `models.json` keeps `top: []` and `models_for_band("top")` **refuses**.
   That refusal is the spend control and is now asserted by
   `test/tools/test_lam_models.py::test_top_band_refuses_while_unnamed`. Do not name frontier ids.
   Do not "temporarily" populate the array.
5. **No lifts, no p-values, no deltas, no comparative claims in Sprint 8.** The instrument does not
   exist until Sprint 9 and the A/A floor is unknown. A number without a floor is not a result.
6. **No cloud spend** until the Project Lead signs `S9-J-03`.

### 0.4 Test commands — corrected

`python3 -m unittest test.tools` exits **5** (`NO TESTS RAN`): `test.tools` is a package, and
loading a package discovers nothing. The command was wrong, not the tests.

```bash
python3 -m unittest discover -s test/tools -t .      # 37 tests, exit 0   <-- use this
python3 -m unittest discover -s test -t .            # full suite
python3 -m unittest discover -s test/runtime -t .    # Lane A
python3 -m unittest discover -s test/agency -t .     # Lane B
python3 -m unittest discover -s test/lab -t .        # Lane C
```

Full suite is green at **539 tests, 0 failures**. The **14** remaining errors are all
`ReaderUnavailable: node is required` — install `node` and they disappear. **If you see a 15th
error or any failure, it is yours.** That is the baseline you are held to.

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
