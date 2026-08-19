---
adr: M0-06
title: "Plane-mapping archaeology"
status: accepted
---

# ADR-M0-06: Plane-mapping archaeology

**Decision.** The six-plane vocabulary (`docs/01_specs/backend/03_vanguard_architecture_planes_and_execution_model_v040.md`
§3: Interaction, Cognition, Control, Workload, Evidence, Evolution) is retired as living taxonomy —
SPEC speaks Layer-0 / SPI / plugin / pack instead — but the separations it encoded are preserved
once, here, for archaeology: Interaction → generated client contract; Cognition → `IPlanner` /
`IContextManager`; Control → kernel; Workload → `IToolkit` + sandbox; Evidence → evaluator daemon;
Evolution → Phase-2 plugins.

One line from the design-convergence evidence document survives as colour, not proof: "two
independent lineages converged on kernel-mediated effects and exterior evaluation."

**Context.** Matrix §1.6, §1.14.

**Reversal condition.** None — this is a historical mapping table, not a live claim.
