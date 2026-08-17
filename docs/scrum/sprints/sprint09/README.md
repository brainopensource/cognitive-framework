# Sprint 9 (Wave 8) — The Instrument (Q3)

**Phase:** 3 · **Wave:** W8 · **Timebox:** 2–3 weeks
**Refinement:** **REFINED AND OPEN (2026-08-16)** — opened alongside Sprint 8 so prep runs in
parallel. Read §0 before starting anything.
**Backlog:** `docs/reviews/doing/011_master_backlog_phase3_V043-REV.md §6`
**Target branch:** `sprints7-8/integration` until Sprint 8 closes, then `sprint9/integration`.

---

## 0. Start here — first task per lane, and what is blocked

Sprint 9 is **Lane C's sprint.** A and B support it. That asymmetry decides what can start early:
Lane C's first task has no Sprint 8 dependency and **starts now**; Lanes A and B are blocked on
Sprint 8 shapes and have prep work instead.

| Lane | S9 first task | Status | DoD command |
|---|---|---|---|
| **C** *(leads)* | **`S9-C-01`** — wire the `M-18` instrument tuple so a lift across differing `K_compat` **refuses**. Then `S9-C-02` (pre-registration) and `S9-C-03` (A/A runner) against `vg-shell-only` with `tools/002_LLM_API_MOCK` | **FREE — start now, parallel with Sprint 8** | `python3 -m unittest discover -s test/lab -t .` → OK, **and** a lift across differing `K_compat` refuses |
| **A** | **`S9-A-01`** — instrument fields on `RunResult` (`gene_digests`, composition digest, per-arm instrument-error reason, integer turn/token/cost) | **BLOCKED BY `S8-A-01`** | `python3 -m unittest discover -s test/runtime -t .` → OK with the new fields asserted |
| **B** | **`S9-B-01`** — three reconstructions differing on ≥3 dimensions | **BLOCKED BY `S8-B-01a` + `S8-B-04`** | `python3 -m unittest discover -s test/agency -t .` → OK, each pack composes with **zero** `agency/episode/` edits |
| **Joint** | `S9-J-03` spend authorisation | Leads only | — |

### 0.1 Blocked rows, stated plainly

| Row | Blocked by | Why it genuinely cannot start |
|---|---|---|
| `S9-A-01` | `S8-A-01` | `RunResult` is produced by `HarnessSession.run()`, which does not exist yet. Adding the fields to today's shape means adding them twice. |
| `S9-A-02` | `S9-A-01` | Integer-telemetry discipline applies to the fields `S9-A-01` adds. |
| `S9-B-01` | `S8-B-01a`, `S8-B-04` | Packs must differ on ≥3 dimensions. Compaction and routing are real; **approval policy is not real until `S8-B-04`**, so a pack cannot yet differ on it. |
| `S9-B-02` `bench` | `S9-C-02` | `bench` enforces a pre-registration hash, whose format is `S9-C-02`'s output. `build`/`run`/`diff` are **not** blocked — see §0.2. |
| `S9-J-01` Q2 dogfood | `S8-J-03` | Bugs are pre-registered in Sprint 8 (**already named** — `DOGFOOD-01..03`) so tasks cannot be chosen after seeing the harness behave. |
| **Every comparative claim** | `S9-J-03` | No cloud spend and no published delta until the Project Lead signs. |

### 0.2 What may start now, in parallel with Sprint 8

Blocked does not mean idle. Each lane has authorised prep:

- **C** — `S9-C-01`, `S9-C-02` and `S9-C-03` against MOCK: the `M-18` tuple, the pre-registration
  format (hypothesis, arms, N, MDE, oracle, hashed before the first arm runs), and the A/A runner
  with its refusal path. This is the bulk of the sprint and none of it needs Sprint 8.
- **A** — audit `Recording` against Phase 4 `V5-A`: which digests must a benchmarked run carry to
  replay (tool-schema, context-compiler, manifest, composition)? Prose, no code. A gap found here is
  an `L-1` envelope decision needing an ADR, and is far cheaper to find now.
- **B** — `REFERENCE.md` per pack: the public docs read and, explicitly, what was **not** copied.
  Prose against public sources, no code, and the part most likely to be rushed if left to Sprint 9.

### 0.3 The spend and claim rule — binding, no exceptions

1. **`tools/002_LLM_API_MOCK` first**, always. Ollama if already present. OpenRouter **free tier
   only**. **Never `band=top`** — `models.json` keeps `top: []` and `models_for_band("top")`
   refuses; that refusal is the spend control, asserted by `test/tools/test_lam_models.py`.
2. **Nobody publishes a delta.** No lift, p-value, interval or comparative claim until the A/A floor
   exists **and** the Project Lead has signed `S9-J-03`.
3. **No cloud spend of any amount** before `S9-J-03`. Local calibration must first show a model can
   `patch.apply` — if none can, that is a harness/tool-schema defect and **cloud will not fix a
   dialect bug** (stop condition 4).
4. **An A/A floor from LAM replay is not a floor.** Replay is deterministic, variance ≈ 0, and the
   run invents significance (`D-06`, `CL-3`). Build the harness against replay; never report a floor
   from it.
5. **A degenerate floor is a valid outcome.** The runner refuses and emits `inconclusive` rather
   than printing zero variance. If the floor swallows the deltas we meant to claim, `RSK-06`
   requires **reducing claim ambition** — not raising N until something is significant.

---

## 1. The sentence this sprint makes true

> **An A/A noise floor exists per task class against `vg-shell-only`, and the runner refuses to
> report when the design is degenerate.**

## 2. Reassignment — read this first

The previous Sprint 9 was *"Meta-Harness Loop Engineering & Self-Correction"*. That work is
**`[REJECTED]`**, not deferred (`011 §8`): it executed effects outside the kernel and graded its own
output, inverting `A-05`. Its three useful ideas re-landed as data in Sprint 8.

Sprint 9 becomes what `ADR-0057` always said S7–S9 were for: **Q3, measurability.**

## 3. Why nothing else can come first

`T8.1`: *"No delta is interpretable until this number exists."* Every comparative claim, every
harness experiment, every promotion decision, and the `O-01` trigger that would license building
the competence graph — all of them are downstream of one number that does not exist.

The field measures **9.5–20 points** of harness-only variance on a fixed model. Our deltas must
clear our own floor, and we do not know what it is.

## 4. Expect an uncomfortable result

If the floor swallows the deltas we intended to claim, **that is the finding.** `RSK-06` requires
acting on it — reducing claim ambition — rather than raising N until something is significant.
`VG-02 §11.5`: *"the temptation to believe a favourable result is strongest precisely when you
designed the change."*

A degenerate floor (all-pass or all-fail) is also a valid outcome, and the runner must **refuse to
report** it rather than printing zero variance.

## 5. Lanes

| Lane | Focus |
|---|---|
| **C — Measurement** (primary) | A/A floor, pre-registration, statistics, splits, oracle hardening, sabotage |
| **B — Workload** | Real reconstructions that differ on ≥3 dimensions; `vg harness build\|run\|diff\|bench` |
| **A — Control Plane** | Support only: telemetry surfaces, `RunResult` fields the instrument needs |
| **Joint** | Q2 dogfood ×3; pre-registration sign-off; spend authorisation |

## 6. Exit gate

- [ ] A per-task-class A/A floor number exists, with N and MDE **derived from it** and recorded
- [ ] The runner **refuses** on a planted degenerate configuration
- [ ] One paired comparison runs end to end and reports an effect **with an interval**,
      pre-registered and hashed **before the first arm ran**
- [ ] Per-arm instrument-error rate reported; asymmetry flagged as a confound
- [ ] A seeded proxy-exploiting candidate is **rejected** by the pipeline
- [ ] A comment-only patch **fails** the hardened `bug-001` oracle
- [ ] Three real bugs fixed interactively; the honest *"would you reach for it again?"* recorded —
      **including if it is no**
- [ ] The three reconstructions produce **different behaviour**, demonstrated, not asserted

## 7. Stop conditions

1. The A/A floor is zero → **the instrument is not exercising anything.** Refuse to report; this is
   a finding about the task set, not a green light.
2. Every arm fails identically → ranking two packs that both fail is `CL-3` degeneracy. Stop and
   fix calibration (Plane C) before any DNA comparison.
3. A reconstruction requires a core change → **stop**, write the finding. `T7.6` is falsified, and
   that is a cheap and valuable result.
4. No live model can `patch.apply` → **do not buy cloud tokens.** That is a harness/tool-schema
   defect, and cloud will not fix a dialect bug.
