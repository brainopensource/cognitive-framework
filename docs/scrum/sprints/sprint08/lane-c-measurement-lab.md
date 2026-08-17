# Sprint 8 · Lane C — Measurement & Lab

**Owner:** Senior C · **Backlog:** `011 §5.3` · **Refinement:** **REFINED AND OPEN (2026-08-16)**
**Branch:** `sprints7-8/integration` · **Commit prefix:** `[lane-c]`
**Write scope:** `runtime/ledger/projections.py` (**yours from Sprint 8**; Lane A raises PR comments)
· `benchmarkings/**` · `tools/002_LLM_API_MOCK/**` · `tools/telemetry/**` · `lab/**` · `test/broken/**`

---

## S8-C-01 — Depth as a ledger projection — **`[DONE]`, DO NOT REBUILD**

**TL verification (2026-08-16):** this row is already delivered. Lane A landed it under `S7-A-05`.

`EpisodeDepthProjection` (`runtime/ledger/projections.py:117`) satisfies every bullet this row asked
for, and one it did not:

- Depth is the length of the `causationId` chain, **recomputed on read and stored nowhere**
- Labels `Atom/Molecule/Polymer/Cell/Body` are applied **in the projection, over an integer** — no
  class hierarchy, exactly as `GTS-13C §4.3` demands
- An episode whose parent was never observed returns `None`, **not** depth 0 — it refuses to
  fabricate a root the ledger does not carry. A causation cycle also returns `None`.
- Tested: `test/runtime/test_episode_depth_projection.py`, including incremental-vs-rebuilt equality

**Verify it yourself once, then move on:**
```bash
python3 -m unittest test.runtime.test_episode_depth_projection -v
```

The file is now in **your** write scope. Own it; Lane A raises PR comments rather than editing.

> `GTS-13C §4.3`: *"Build the classes and you have hand-authored the hierarchy you claimed would
> emerge… Nature did not implement `class Cell`; it implemented a replicator under selection and
> let scale happen."* The delivered projection honours this — keep it that way.

---

## ▶ YOUR FIRST TASK: `S8-C-02` — cache-hit rate over a fixed replay

Because `S8-C-01` is done, you start here. It is also, per the note below, the highest-value single
day in the programme.

**DoD command:**
```bash
python3 -m unittest discover -s test/lab -t .
```
Green, and the metric emits from a **cassette replay with no network**. If the provider does not
report cache hits, record prefix-digest stability and **label the limitation** — that is explicitly
not a stop (stop condition 1).

**Then, in any order — both independent:** `S8-C-03` (prefix-miss attribution), `S8-C-04` (LAM
schema regex). All three of your rows are free to run in parallel with Lanes A and B; you have no
inbound dependency this sprint.

## ▶ YOUR SPRINT 9 FIRST TASK: `S9-C-01` — the `M-18` tuple · **you lead Sprint 9**

**NOT BLOCKED. You may start Sprint 9 prep in parallel with Sprint 8, under one restriction.**

Sprint 9 is your sprint — Lanes A and B support it. The A/A floor is the number every comparative
claim in the programme is downstream of, and it does not exist.

**Authorised to start now:**
- [ ] `S9-C-01` — wire `tools/telemetry/tuple.py` (`M-18`, implemented and wired into nothing) so a
      lift across differing `K_compat` **refuses**
- [ ] `S9-C-03` — the A/A harness and its refusal path against **`vg-shell-only`** with
      **`tools/002_LLM_API_MOCK`**
- [ ] Plant a degenerate configuration (all-pass and all-fail) and prove the runner **refuses to
      report** and emits `inconclusive`
- [ ] `S9-C-02` — the pre-registration file format: hypothesis, arms, N, MDE, oracle, hashed
      **before** the first arm runs

**Explicitly forbidden until the Project Lead signs `S9-J-03`:**
- No cloud spend, of any amount, on any provider
- No lift, delta, p-value, interval or comparative claim — **nobody publishes a delta**
- No A/A run on LAM replay used as a floor: replay is deterministic, so variance ≈ 0 and the run
  invents significance (`D-06`, `CL-3`). Build the harness against replay; do not report a floor
  from it.

> A degenerate floor is a **valid outcome** and the runner must refuse rather than print zero
> variance. If the floor swallows the deltas we intended to claim, `RSK-06` requires reducing claim
> ambition — **not** raising N until something is significant.

---

## S8-C-02 — Cache-hit-rate metric over a fixed replay · **highest-value single day in the programme**

`VG-03 §12` calls prompt caching *"the largest single cost lever"* and marks the vendor-reported
50–90% figure **"unverified here."** It is still unverified. Our prefix is architecturally correct
and its hit rate has **never been observed**.

- [ ] Fixed replay corpus (cassette-backed, no network)
- [ ] Record prefix digest stability across turns
- [ ] Record provider-reported cache hits where available
- [ ] Emit as a **monitored CI metric** (`VG-03 §10.2`: *"a metric without a replay to run over is
      an intention"*)
- [ ] Commit

---

## S8-C-03 — V5-L prefix-miss attribution

- [ ] Every model call records **why** the prefix broke: `system` / `tools` / `compact` / `snip` —
      or records a hit
- [ ] Test: mutating L1 attributes the miss to `system`
- [ ] Commit

> Reasonix's `CompareShape` is the reference mechanism. Do not assume any provider's automatic
> cache behaviour; measure it.

---

## S8-C-04 — LAM schema regex reconciliation

`schema.py` requires `^t[1-5]-` while the corpus contains `t0-*` and `t6-*`. Corpus and validator
disagree.

- [ ] Failing test: every scenario in `scenarios/` validates
- [ ] Freeze one regex; generate the other family under a second schema, or extend with an explicit
      documented waiver artifact — **not a silent loosening**
- [ ] Commit

---

## What this lane may **not** do this sprint

| Forbidden | Why |
|---|---|
| Compute or publish any lift | No A/A floor yet — that is Sprint 9 |
| Spend the live budget | Calibration-first; pre-registration lands in Sprint 9 |
| Run an A/A on LAM replay | Deterministic → variance ≈ 0 → invents significance (`D-06`, `CL-3`) |

## Stop conditions

1. Cache-hit rate cannot be measured because the provider does not report it → **not a stop**;
   record prefix-digest stability instead and label the limitation.
2. Depth projection needs a field the envelope does not carry → **stop**; an envelope change is a
   `L-1` corpus-format decision requiring an ADR.
