# Sprint 8 · Lane C — Measurement & Lab

**Owner:** Senior C · **Backlog:** `011 §5.3` · **Refinement:** PLANNED, NOT REFINED
**Write scope:** `runtime/ledger/projections.py` (coordinate with Lane A) · `benchmarkings/**` ·
`tools/002_LLM_API_MOCK/**` · `tools/telemetry/**`

---

## S8-C-01 — Depth as a ledger projection

Replaces the SQLite table deleted in Sprint 7.

- [ ] Failing test: episode depth and parent/child structure derive from ledger events alone
- [ ] Implement over `causationId` in `runtime/ledger/projections.py`
- [ ] Depth **labels** (`Atom`/`Molecule`/`Polymer`/`Cell`/`Body`) are applied **by the
      projection** — never a class hierarchy
- [ ] Commit

> `GTS-13C §4.3`: *"Build the classes and you have hand-authored the hierarchy you claimed would
> emerge… Nature did not implement `class Cell`; it implemented a replicator under selection and
> let scale happen."*

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
