---
adr: M0-13
title: "End-to-end disposable slice before deep contracts"
status: accepted
---

# ADR-M0-13: End-to-end disposable slice before deep contracts

**Decision.** A trivial echo-plugin traverses the full plugin lifecycle
(`DISCOVERED → RESOLVED → VERIFIED → ACTIVATED → QUIESCING → RETIRED`) and one complete episode
through the scheduler + kernel + ledger before any real plugin (planner, toolkit, memory engine) is
written. This is the M2 "walking skeleton" rule.

**Context.** Correction 1 in `docs/01_specs/backend/13_C_gts_mvp_program_and_engineering_plan.md`'s
`corrections_from_13B`. `docs/TECH_LEAD_REVIEW/03_SPRINTS_PARALLEL_EXECUTION_PLAN.md` schedules this
as S-M1-B-07 ("walking skeleton α," scripted-planner + echo-toolkit + cassette-model) and
S-M2-B-03 ("walking skeleton β," the same run driven through the registry from `plugins/` with zero
hardcoded imports). T6's "coding harness is the first, **disposable**, point design" from GTS-13C is
vindicated by M3 (Domain Pack #1 extraction) and cited here as its origin.

**Reversal condition.** None — this is a sequencing discipline, not a claim about the system.
