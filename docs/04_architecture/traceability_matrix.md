---
status: living
id: architecture-traceability-matrix
class: architecture
authority: descriptive
canonical_for:
  - bidirectional-traceability-matrix
source_of_truth:
  - docs/SPEC.md
  - docs/02_decisions/INDEX.md
derived_from:
  - vanguard/packages/
  - test/
applies_to:
  - v0.7.x
implementation_status: MIXED_VERIFIED_PER_ROW
owner: principal-systems-architect
version: "0.9.0b1"
last_verified: 2026-08-26
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Bidirectional Traceability Matrix

This is navigation, not proof. Current milestone state lives only in
[`sprint_active.md`](../03_execution/sprint_active.md).

| Concept | Law / decision | Production symbol | Executable check | Verified maturity |
|---|---|---|---|---|
| S0–S12 dispatch | SPEC A-1; DISPATCH; ADR-0069/0074 | `kernel/dispatch.py:Kernel.dispatch` | `test/kernel/test_dispatch.py` | `AS_BUILT`, M-1 accepted |
| Capability attenuation | DISPATCH §4; ADR-0070/0074 | `kernel/attenuation.py:attenuate` | `test/kernel/test_attenuation.py` | `AS_BUILT`, M-1 accepted |
| Budget algebra | ADR-0074/0098 | `kernel/budget.py:Governor` | grant/budget and delegation falsifiers | four additive costs + structural ceilings built |
| Ledger writer/replay | RUNTIME; ADR-0071/0076 | `runtime/ledger_emitter.py` | ledger truth, RF-25 | `AS_BUILT`, M-2 accepted |
| Exterior signed judge | EVIDENCE; ADR-0072 | evaluator daemon/signing | evaluator signing tests | `AS_BUILT`, M-1 accepted |
| Canonical composition | EXTENSIBILITY; ADR-0077/0081 | `runtime/compose.py`, registry compiler | RF-78–RF-84 | `AS_BUILT`, M-3C accepted |
| Trajectory `/2` | EVIDENCE; ADR-0096 | `runtime/trajectory.py` | trajectory/RF-100 tests | mechanism built; M-4 evidence open |
| AgentView/checkpoints | RUNTIME §1.5; ADR-0098 | domain AgentView, runtime checkpoints | RF-96/97/99 | mechanism built; successor baseline open |
| Formal domain | EXTENSIBILITY; ADR-0102 | `packs/formal-sat`, formal evidence | RF-52/53, material-run tests | SAT demo built; clean M-5b proof open |
| Mediated spawn | ADR-0080/0090 | `runtime/delegation.py`, wiring | RF-55–RF-59 | partial; synthetic/canonical recursion gaps |
| Meta-control | ADR-0096 | progress/controller/study modules | M-6.5 falsifiers | package ready; valid study blocked |
| Topology/scheduler | ADR-0096; pending ADR-0099 | topology, scheduler, M7 analyzer | topology/M701 tests | library mechanisms; runtime integration open |
| Memory/promotion | ADR-0100 | memory and skill-evaluation modules | M-8 lifecycle tests | in-memory prototypes; product not started |
| Evidence acceptance | ADR-0101 | evidence/baseline tooling (planned) | execution-truth and future envelope gates | governance contract accepted; bundles open |
