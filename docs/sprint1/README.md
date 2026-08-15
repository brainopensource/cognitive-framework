# Sprint 1 developer packet index

Project decision: `CONDITIONAL GO — preparation and local schema work only`  
Decision: `DECISION-0001`, 2026-08-15  
Merge condition: independent T0 reconstruction, prospective human timing sample, protected-branch evidence and baseline tag

## Required reading order

1. `docs/v4/09_vanguard_decision_register_v040.md`
2. `docs/v4/13_C_gts_mvp_program_and_engineering_plan.md`
3. `docs/sprint0/system-architecture-icd.md`
4. `docs/sprint0/active-mvp-contract.json`
5. `docs/sprint0/verification-threat-evaluation-plan.md`
6. `docs/sprint0/schema-archaeology/field-inventory.md`
7. `docs/sprint1/backlog.md` and the assigned developer packet
8. VG-01, VG-03, VG-04 and VG-05
9. `.github/pull_request_template.md` and `vanguard/packages/README.md`

Do not use Rev A/B, GTS-13, GTS-13B, obsolete reader packets or the Sprint 0 leadership mandate as implementation authority. Report contradictions to the Tech Lead; do not choose silently.

## Current gate

T1 rows `REQ-SCHEMA-001..012` are assigned and `open`. Work may begin on short-lived local branches, starting with tests and vectors. No schema may be marked locked, no durable event may be recorded against it and no product implementation may merge until the blockers above close. T0a remains disposable in `spike/` and cannot be imported.

