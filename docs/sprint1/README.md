# Sprint 1 developer packet index

Project decision: `CONDITIONAL GO — preparation and local schema work only`  
Superseded for engineering close by `DECISION-0002` / `APPROVAL-0003` (2026-08-15). Historical merge condition below is retained as the schema-lock gate.  
Decision: `DECISION-0001`, 2026-08-15  
Merge condition: independent T0 reconstruction, prospective human timing sample, protected-branch evidence and baseline tag

## Dispatch record — 2026-08-15

| Developer | Local branch | Packet | Dispatch state |
|---|---|---|---|
| Dev 1 | `sprint1/dev-1-canonicalization` | `dev-1-packet.md` | merged via sprint1/integration |
| Dev 2 | `sprint1/dev-2-effect-contracts` | `dev-2-packet.md` | merged via sprint1/integration |
| Dev 3 | `sprint1/dev-3-evidence-contracts` | `dev-3-packet.md` | merged via sprint1/integration |
| Dev 4 | `sprint1/dev-4-provider-process` | `dev-4-packet.md` | merged via sprint1/dev4-tui and integration |

`REQ-SCHEMA-001..012` are covered as DRAFT. No schema may be marked locked until the T0 human gates in `DECISION-0002` close. T0a remains disposable in `spike/` and cannot be imported.

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

T1 rows `REQ-SCHEMA-001..012` are assigned and covered. Work completed on short-lived branches. No schema may be marked locked, no durable production trajectory may be recorded against LOCKED status, and Sprint 3 merges follow `DECISION-0003`. T0a remains disposable in `spike/` and cannot be imported.
