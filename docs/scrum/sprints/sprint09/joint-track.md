# Sprint 9 · Joint Track

**Owners:** Tech Lead + Project Lead · **Refinement:** **REFINED AND OPEN (2026-08-16)**

> **`S9-J-03` is the gate on every number this programme publishes.** Until the Project Lead signs
> it: no cloud spend of any amount, and **nobody publishes a delta** — no lift, p-value, interval or
> comparative claim, from any lane. Lane C builds the instrument; it does not report through it.
>
> The three Q2 dogfood bugs for `S9-J-01` are **already pre-registered by name** in
> `docs/scrum/sprints/sprint08/joint-track.md §S8-J-03` (`DOGFOOD-01`, `-02`, `-03`), together with
> the substitution rule. Do not choose bugs in Sprint 9 — that is the whole point of naming them in
> Sprint 8.
>
> **`tools/002_LLM_API_MOCK/scenarios/t0-dogfood-bug-00{1,2,3}` are NOT Q2 evidence.** Despite the
> names they are LAM cassette replays; replay cannot answer *"would you reach for it again?"*
> because nobody reached for anything.

---

## S9-J-01 — Q2 dogfood ×3 · **the gate nobody can automate**

`GTS-13C` Ch. 10 Q2: three real bugs in a repository someone knows well, fixed interactively,
**without hand-patching mid-run**. Then, honestly: *next time, would you reach for it?*

- [ ] Preregister the three bugs **before** the runs (scheduled in Sprint 8 so tasks cannot be
      chosen after seeing the harness behave)
- [ ] Use only the installed CLI path. Prompt, approve and correct freely; **zero human source
      edits**
- [ ] Capture: model, turns, cost, elapsed, restart/approval/evaluator evidence, final verdict
- [ ] Capture corrections with reason codes — one keystroke, not a form (`T6.7`)
- [ ] Record the human answer per run

> **If Q2 is "no": stop.** That is the handbook. *"If no, the loop is not done, and no amount of
> later work fixes that."* A "no" recorded honestly is worth more than a "yes" manufactured by
> re-running until it works.

## S9-J-02 — Pre-registration sign-off

- [ ] Review and countersign every pre-registration hash before its arms run
- [ ] Confirm the family is declared **before** arms run; Holm–Bonferroni on the family
- [ ] **Optional stopping is forbidden.** The stopping rule is fixed in the artifact

## S9-J-03 — Spend authorisation

- [ ] Authorise cloud spend only after local calibration shows a model can `patch.apply`
- [ ] Confirm `models.json` `top` remains `[]` unless three ids are named in the Decision Register
- [ ] Every 10 live calls → a ledger line

## S9-J-04 — Q3 evidence review

- [ ] Does a per-class A/A floor exist, with N and MDE derived from it?
- [ ] Does one paired comparison report an effect with an interval, pre-registered?
- [ ] Is there a verifier–deployment gap number, **or** a written statement of why it is not yet
      computable, with a date?
- [ ] Update `ADR-0064`'s Q2 and Q3 rows **only** where evidence supports it

> **The failure mode to guard against this sprint** is not fraud; it is a true sentence read as a
> stronger one. "The floor exists" is not "the harness works". Say the narrower thing.
