# Sprint 0 governance baseline

Status: `ENGINEERING CLOSED — APPROVAL-0003; residuals listed in DECISION-0002`  
Time box: 2026-08-14 through 2026-08-27 (10 working days, America/Sao_Paulo)  
Approval required: Tech Lead + Project Lead

## Authority order

1. approved Decision Record: `docs/v4/09_vanguard_decision_register_v040.md`;
2. Vanguard v4 contracts;
3. `system-architecture-icd.md`;
4. `verification-threat-evaluation-plan.md`;
5. `active-mvp-contract.json` — the only merge-gating requirement map;
6. GTS-13C — programme sequencing and rationale only;
7. issue tracker;
8. lead-only historical inputs.

Conflicts are recorded and resolved by the owning authority; implementation must not silently choose. This baseline does not delete or rewrite historical material.

## Executable artifacts

| Artifact | State | Gate |
|---|---|---|
| Decision Record | ADR-0045..0057; APPROVAL-0001..0003 | append-only approval event |
| System Architecture & ICD | approved | boundary checker and architecture review |
| Active MVP Contract | S0–S2 covered rows; S3–S4 assigned/open | contract validator at 100%/100% merged scope |
| Verification, Threat & Evaluation Plan | S0–S2 executable; S4 trust-spine planned | test-owner mapping and executable registry |

Tag `v0.0.0-sprint0` exists. Hosted branch protection on `main` was unverified (HTTP 404) on 2026-08-15. T1 schemas are DRAFT/covered, not LOCKED. Live T0b remains open.

## Bootstrap rule

Until a baseline tag and protected-branch evidence exist, a merge may contain only documentation, governance, contract, CI or repository scaffolding. It must cite `REQ-GOV-005`, attach the manual evidence the future gate requires and contain no product behaviour. Branch protection is an external repository setting; this repository can require checks but cannot prove that the hosting setting is enabled.

Product merges for S1/S2 already landed under later approvals; new S3 product merges follow `DECISION-0003`.

## Approval record

| Role | Identity | Decision | Date |
|---|---|---|---|
| Tech Lead | repository principal `rocha` (`acting-tech-lead`) | approved | 2026-08-15 |
| Project Lead | repository principal `rocha`, acting under explicit user authority | S0–S2 engineering closed; S3 conditional go | 2026-08-15 |

`DECISION-0001` permitted Sprint 1 preparation. `DECISION-0002` closes Sprint 0–2 engineering with named residuals. Schema lock remains closed until the two human T0 gates and hosted branch protection are evidenced.
