---
adr: M0-01
title: "Control coverage discipline"
status: accepted
---

# ADR-M0-01: Control coverage discipline

**Decision.** Every SPEC invariant (I-1…I-11) maps to exactly one of {CI job, contract test,
static-analysis proof}, enumerated in CI config, with the mapping itself CI-checked. The bijection
discipline from the old `rule_test_map.py` generator is kept — including its legitimate
**justified UNTESTABLE** entry class (e.g. lattice rules proven by static analysis rather than
runtime test) — but retargeted at the eleven SPEC invariants instead of the retired VG rule corpus
(`N-*`, `CC-*`, `CT-*`, `K-*`, `MF-*`).

**Context.** `docs/01_specs/backend/00_phase0-rule-backlog.md` and `00_rule-test-map.md` tracked 203
rules against documents this wave archives; 133 gaps against a dead corpus is not information. The
one durable idea — a machine-checked bijection with justified-untestable exceptions — survives; the
corpus it tracked does not.

**Reversal condition.** None; this is process, not a claim about the system. It is superseded only
by a stronger coverage discipline, never silently dropped.

**Task.** `tools/rule_test_map.py` is retargeted in M1 (task S-M1-A-08 in
`docs/03_sprints/plans/m1-m2-lanes.md`) to enumerate I-1…I-11 instead of the VG rule corpus.
