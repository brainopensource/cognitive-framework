# Sprint 9 (Wave 8) — The Instrument (Q3)

**Phase:** 3 · **Wave:** W8 · **Timebox:** 2–3 weeks · **Refinement:** PLANNED, NOT REFINED
**Backlog:** `docs/reviews/doing/011_master_backlog_phase3_V043-REV.md §6`

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
