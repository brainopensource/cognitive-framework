# Sprint 0 governance baseline

Status: `APPROVED GOVERNANCE BASELINE — product merges remain conditionally closed`  
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
| Decision Record | ADR-0045..0053 accepted by `APPROVAL-0001` | append-only approval event |
| System Architecture & ICD | approved | boundary checker and architecture review |
| Active MVP Contract | approved S0 scope; T1 rows assigned/open | contract validator at 100%/100% |
| Verification, Threat & Evaluation Plan | approved S0 scope | test-owner mapping and executable registry |

The current contract covers ten Sprint 0 controls and assigns twelve open T1 schema rows. T0 archaeology deliberately precedes locking those schemas. Later T1–T10 product/assurance rows activate only when their dependencies enter scope. This is a blocking obligation, not a waiver.

## Bootstrap rule

Until a baseline tag and protected-branch evidence exist, a merge may contain only documentation, governance, contract, CI or repository scaffolding. It must cite `REQ-GOV-005`, attach the manual evidence the future gate requires and contain no product behaviour. Branch protection is an external repository setting; this repository can require checks but cannot prove that the hosting setting is enabled.

## Approval record

| Role | Identity | Decision | Date |
|---|---|---|---|
| Tech Lead | repository principal `rocha` (`acting-tech-lead`) | approved | 2026-08-15 |
| Project Lead | repository principal `rocha`, acting under explicit user authority | conditional go | 2026-08-15 |

`DECISION-0001` permits Sprint 1 preparation and local schema work. Schema lock and product merges remain closed until the two human T0 gates, hosted branch protection and baseline tagging are evidenced.
