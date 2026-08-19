---
adr: M0-03
title: "Four pluggable things become five SPIs"
status: accepted
---

# ADR-M0-03: Four pluggable things become five SPIs

**Decision.** The engineering handbook's "exactly four pluggable things" (M2) is superseded:
MHF has exactly **five** frozen SPIs — `IPlanner`, `IMemoryEngine`, `IToolkit`, `IContextManager`,
`IEvaluationGate` — plus first-party `IModelProvider`/`ISandbox`/store ports that are not
user-pluggable extension points in the same sense. The taxonomy change is recorded, not silent.

**Context.** `docs/01_specs/backend/01_vanguard_engineering_handbook_v040.md` M2 named four
extension forms. `NEXT_GEN_META_HARNESS_SPECIFICATION.md` §2.2 needs a fifth to give evaluation
gating (`IEvaluationGate`) its own typed contract distinct from `IToolkit`, matching the audit's
S-3 finding that judge exteriority is architecturally load-bearing and deserves its own SPI rather
than being folded into tool execution.

**Reversal condition.** A capability that fits none of the five forces a design review, not a
sixth SPI merged by ordinary PR.
