# Sprint 8 · Joint Track

**Owners:** Tech Lead + Project Lead · **Backlog:** `011 §5` · **Refinement:** PLANNED, NOT REFINED

---

## S8-J-01 — `VG-04` wire amendment for `Claim`

Coordinates with `S8-A-05`. This is a **format lock** (`L-1`): *"changing it means re-running
everything ever recorded."*

- [ ] Review the `Claim` type against `VG-06`'s evidence claim; the schema already exists
      (`schemas/v4/evidence-claim.schema.json`) with `invalidationConditions` `minItems: 1`
- [ ] Add `support_count`, `last_corroborated_at`, `protection_class` as **optional reader-profile**
      fields (`T1.13` writer/reader split — a reader rejecting unknown fields breaks forward
      compatibility on its first bump)
- [ ] Golden vectors for the new fields
- [ ] Migration rehearsal (`T1.15`): add the field, bump minor, prove old readers survive
- [ ] Record as an ADR — it is irreversible

> **Why now, when nothing consumes it:** `T4.11` already accepted this argument for the competence
> prior. Recording costs nothing today; retrofitting costs a corpus migration. And the 2026
> library-drift literature says evidence-gated preservation is the structural mitigation — the
> fields are the cheapest possible hedge.

---

## S8-J-02 — Confirm `ADR-0060` held through recursion

Sprint 8 is the only sprint that edits `agency/episode/`. Verify the invariant survived.

- [ ] Diff `agency/episode/` and confirm **zero domain vocabulary** was introduced
- [ ] Confirm `check_tcb_budget.py` still passes — recursion must not grow the kernel
- [ ] If a domain noun did enter, that is a **finding**, and `ADR-0060`'s reversal condition should
      be evaluated honestly rather than the noun quietly renamed

---

## S8-J-03 — Q1/Q2 evidence review

- [ ] Q1: confirm Sprint 7's closure held through a sprint that added code
- [ ] Q2: schedule the three dogfood bugs for Sprint 9; preregister them now so the tasks cannot be
      chosen after seeing the harness behave
- [ ] Update `ADR-0064` gate rows **only** where evidence supports it

## Sign-off checklist

- [ ] All three lane DoDs green
- [ ] `S7-B-03` metamorphic test now green (manifests are load-bearing)
- [ ] TCB under budget; `ADR-0060` verified
- [ ] `Claim` format locked with golden vectors and a migration rehearsal
- [ ] Cache-hit rate is a live CI metric
