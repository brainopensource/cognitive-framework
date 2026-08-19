---
adr: M0-12
title: "A tool is not an Episode"
status: accepted
---

# ADR-M0-12: A tool is not an Episode

**Decision.** Tools execute typed effects; Episodes coordinate open-ended work. The
`IToolkit`/`IPlanner` boundary is protected: a toolkit never runs its own multi-turn loop, and a
planner never directly executes an effect outside a proposal.

**Context.** Correction 3 in `docs/01_specs/backend/13_C_gts_mvp_program_and_engineering_plan.md`'s
`corrections_from_13B`, restated as `ADR-0050`'s distinction between Effects (execution primitives),
Episodes (recursive coordination), and declared durable state machines (governance). This boundary
is what keeps `mhf.planner.meta-reflector` (SPEC §5.1) from becoming a second engine, and what keeps
a toolkit like `mhf.toolkit.terminal`'s PTY loop from becoming a second planner.

**Reversal condition.** None within this programme's assumptions — collapsing the boundary
reintroduces the `MetaLoopEngine` anti-pattern (`ADR-0041`/D-41: kept deleted; the outer loop is a
plugin at a scheduler slot, never an engine).
