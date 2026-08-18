# Sprint 10 (Wave 9) — Generality & The MVP Gate (Q4)

**Phase:** 3 · **Wave:** W9 · **Timebox:** 2 weeks · **Refinement:** PLANNED, NOT REFINED
**Backlog:** `docs/reviews/doing/011_master_backlog_phase3_V043-REV.md §7`

---

## 1. The sentence this sprint makes true

> **A non-coding environment runs, and the number of lines changed in `kernel/` and
> `agency/episode/` to add it is measured and published — whatever it is.**

## 2. Why TableWorld was supposed to be first

`VG-03 §7.3` makes TableWorld **mandatory in Phase 0** and states the reason plainly:

> *"If adding TableWorld requires changing the episode engine, the capability algebra or the event
> envelope, generality has been falsified early — cheaply, and therefore usefully. That is the
> point of building it first rather than last."*

It has been deferred four phases. Meanwhile the capture it was designed to detect **has already
begun**: `adapters/models/invocation.py` hardcodes coding verbs, per-verb argument validation and
filesystem selector construction. `ADR-0060`'s letter is honoured (`kernel/` and `agency/episode/`
are clean) and its purpose is defeated — adding a domain today means editing a model adapter.

So Sprint 10 does de-capture **first**, then TableWorld.

## 3. A non-zero core-change count is a finding, not a failure

`C-10` is falsifiable on purpose. A zero count is a strong claim; a small non-zero count with a
published diff is an honest one. **Only a hidden non-zero count is a failure.**

If the count is non-zero: record it, write the ADR, adjust the claim. `VG-02 §11.9` commits the
programme to publishing negative results, and this is the cheapest one available.

## 4. Lanes

| Lane | Focus |
|---|---|
| **A** | Domain de-capture; `BlobStorePort`/`IndexPort`; `vg why` |
| **B** | TableWorld adapter + domain evaluator; core-change detector; structured consolidation; re-grounding |
| **C** | Instrument support for a second domain; per-domain floors |
| **Joint** | The four-question gate review |

## 5. Exit gate — the actual MVP gate (`GTS-13C` Ch. 10)

| # | Question | Required evidence |
|---|---|---|
| **Q1** | Boundary real? | Red team reaches neither control plane, evaluator, nor secrets. Every must-fail test fails against its counterpart. Kill/restart preserves known vs uncertain. **No second execution path exists, proven by architecture test** |
| **Q2** | Useful? | Three real bugs fixed interactively without hand-patching; the recorded reach-for-it-again answer |
| **Q3** | Measurable? | A/A floor per task class vs `vg-shell-only`; one paired comparison; a verifier–deployment gap number **or** a dated statement of why not |
| **Q4** | General? | TableWorld added, **and the measured line count changed in `kernel/` + `agency/episode/` published** |

> `GTS-13C` Ch. 10: *"Tickets merged, CI green, and a demo that worked once do not close it."*
> Each question needs an evidence path, not a slide.

## 6. Stop conditions

1. TableWorld needs an `EpisodeEngine`, capability-algebra or event-envelope change → **stop.**
   File the finding; do **not** "make the engine more general" in the same PR as the adapter
   (`D-15`).
2. TableWorld is implemented as "CSV files in git" → **stop.** That is a coding task wearing a
   different name and it fails `C-10`'s spirit. No version control, no shell, no paths as a domain
   concept.
3. The gate review cannot answer a question with evidence → record it as **not met**. `ADR-0064`
   exists precisely so this is a normal outcome rather than an embarrassment.
