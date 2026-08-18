# Sprint 10 · Joint Track — The MVP Gate Review

**Owners:** Tech Lead + Project Lead · **Refinement:** PLANNED, NOT REFINED

---

## S10-J-01 — The four-question gate review

Answer with **evidence paths, not slides**. `GTS-13C` Ch. 10 is explicit that merged tickets, green
CI and a demo that worked once do not close this.

- [ ] **Q1 — Is the boundary real?** Red team reaches neither control plane, evaluator, nor secrets ·
      every must-fail test fails against its broken counterpart · kill and restart preserve the
      distinction between known and uncertain · no second execution path exists, proven by
      architecture test
- [ ] **Q2 — Is it useful?** Three real bugs fixed interactively without hand-patching · the
      recorded answer to *"next time, would you reach for it?"*
- [ ] **Q3 — Is it measurable?** A/A floor per task class against `vg-shell-only` · a paired
      comparison · a verifier–deployment gap number, or a dated statement of why not
- [ ] **Q4 — Is it general?** TableWorld added · **the measured line count changed in `kernel/` +
      `agency/episode/` published**

## S10-J-02 — Reverse `ADR-0064` per gate, honestly

`ADR-0064` recorded all four gates as not met, each with its own reversal condition. Evaluate them
**one at a time**. A gate whose evidence does not support reversal **stays unreversed**, and that is
a normal outcome — it is the entire reason the ADR was written before the work.

## S10-J-03 — What may and may not be claimed at v0.4.3

**May say:** every privileged effect traverses one capability-mediated dispatch sequence with
fault-injection tests for every exit · the evaluator runs under a separate OS identity and image
digest, unreachable from every capability the episode holds · RFC 8785-canonical wire contracts with
golden triples and a decidable per-kind selector inclusion relation · here is a trajectory, here is
which component was active, here is what it cost.

**May not say:** AGI, or an AGI-like general solver · autonomous evolution · SOTA cognitive machine ·
that competence accumulates (`C-06` is not in Phase 3 scope) · that the harness improves outcomes,
unless a powered paired comparison against `vg-shell-only` says so.

> Market exactly what is proven: **a Linux framework for building governed agentic harnesses, plus
> one coding harness, with descriptor-bound human approval, isolated execution, durable traceability
> and exterior evaluation.** Generality and measurable competence accumulation become defensible
> only after Q3/Q4 evidence.

## S10-J-04 — Phase 4 authorisation

- [ ] Evaluate the `O-01` trigger: **has one distilled artifact cleared the A/A floor?** If not,
      the competence graph, operator registry and playbook engine stay unbuilt — `O-01` says derive
      the lifecycle from the survivor, not before it
- [ ] Evaluate the `O-03` trigger for general subagent composition
- [ ] Authorise Phase 4 / V5 scope from `010 §4`, ordered by dependency, starting with **V5-A exact
      corpus** — the one that cannot slip, because without tool-schema snapshots in `Recording`,
      the trajectory corpus is unusable for any later training
