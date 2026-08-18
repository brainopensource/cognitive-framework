# Sprint 10 · Lane C — Measurement & Lab

**Owner:** Senior C · **Backlog:** `011 §7` · **Refinement:** PLANNED, NOT REFINED

## S10-C-01 — Instrument support for a second domain

- [ ] Confirm the A/A runner, splits and statistics module work **unchanged** against TableWorld
- [ ] If the instrument needs a domain special case, that is a **finding** about the instrument,
      symmetric to `C-10` for the runtime — record it
- [ ] Per-domain noise floor: coding and TableWorld floors are separate numbers and must not be
      pooled

## S10-C-02 — Verifier–deployment gap dashboard

- [ ] Correlation between promotion score and accepted deployment outcome (`T8.7`)
- [ ] **Build the automatic freeze now, while there is nothing to freeze.** Retrofitting an
      automatic freeze onto a live promotion pipeline is how the freeze becomes advisory
- [ ] Widening past threshold freezes promotions automatically (even if the freeze only logs today,
      because autonomous promotion does not exist)

## S10-C-03 — Gate evidence pack

- [ ] Assemble the evidence paths for all four questions — commands and outputs, not prose
- [ ] Include the negative results: degenerate A/A if any, reconstructions that needed core
      changes, the TableWorld core-change count
- [ ] **Negative results are publishable** (`VG-02 §11.9`) and belong in the pack, not in a
      footnote
