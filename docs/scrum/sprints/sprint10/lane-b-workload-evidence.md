# Sprint 10 · Lane B — Workload & Evidence

**Owner:** Senior B · **Backlog:** `011 §7` · **Refinement:** PLANNED, NOT REFINED

## S10-B-01 — TableWorld

**Requires:** `S10-A-01` domain de-capture.

Per `VG-03 §7.3` and `VG-08` Increment C:

- [ ] Versioned tables; `select` / `derive` / `update` / `validate`
- [ ] Constraints over sums, uniqueness, ranges and reconciliation
- [ ] **No version control, no shell, and no paths as a domain concept**
- [ ] Deterministic evaluator over invariants and expected relations — a **domain-native** evaluator
      under the same `EvaluatorPort`, not `coding-oracle@3`
- [ ] Inconsistency → **abstention**, which is a scored success (`T4.5`)
- [ ] New verbs (`table.read`, `table.diff`, `table.patch`) as **binding rows + adapter**, never
      engine branches (`D-04`)
- [ ] Commit

**Stop:** if you find yourself overloading `fs.read` on CSV files, you have **not** added a second
environment — you have added a coding task. That fails `C-10`'s spirit (`D-15`).

## S10-B-02 — Core-change detector

- [ ] CI counts lines changed in `kernel/**`, `agency/episode/**`, `domain/wire/**` on any
      domain-addition or reconstruction PR
- [ ] Such a PR touching those trees **fails** unless explicitly labelled `ADR-XXXX core change`
      with both leads on the review
- [ ] **The count is the `C-10` measurement and is published whatever it is**
- [ ] Commit

## S10-B-03 — `structured_consolidate`

- [ ] Emit `StructuredRecord`: `decisions`, `invariants`, `open`, `artifacts`, **`deadEnds`**
- [ ] `deadEnds` earns its place: *"an agent re-exploring an approach it already abandoned is among
      the most common and most expensive long-horizon failures"* (`VG-03 §10.4`)
- [ ] Measure consolidation quality: replace the full transcript with the record, re-run, compare
      outcomes. *"That is a number, not an opinion"*
- [ ] Register as a `CompactionStrategy` selectable by `context_policy`
- [ ] Commit

## S10-B-04 — Periodic re-grounding

- [ ] `regroundPolicy` in the loop, as an **authorised observation effect** — it goes through
      `broker.authorize` and `EnvironmentAdapter.observe` like any other effect. **Not a privileged
      side channel** (`VG-03 §6.1` reading note)
- [ ] Test: re-grounding produces a dispatch record in the ledger
- [ ] ~30 lines, and the cheapest defence against `FT-11` goal drift and silent error compounding
- [ ] Commit
