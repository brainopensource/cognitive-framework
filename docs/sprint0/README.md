# Sprint 0 governance baseline

Status: `DRAFT — controlled bootstrap only`  
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
| Decision Record | proposed Sprint 0 additions, append-only | joint Tech Lead + Project Lead approval |
| System Architecture & ICD | draft | boundary checker and architecture review |
| Active MVP Contract | draft, active S0 assurance scope | contract validator at 100%/100% |
| Verification, Threat & Evaluation Plan | draft | Tech Lead approval and test-owner mapping |

The current contract activates only Sprint 0 governance and repository assurance controls. T0 archaeology deliberately precedes locking product schema rows. Before any product implementation merges, the Tech Lead must activate the applicable T1–T10 product/assurance rows with stable IDs, owners, tests and evidence. This is a blocking obligation, not a waiver.

## Bootstrap rule

Until joint approval and a baseline tag exist, a merge may contain only documentation, governance, contract, CI or repository scaffolding. It must cite `REQ-GOV-005`, attach the manual evidence the future gate requires and contain no product behaviour. Branch protection is an external repository setting and must be confirmed by the Project Lead; this repository can require checks but cannot prove that the hosting setting is enabled.

## Approval record

| Role | Identity | Decision | Date |
|---|---|---|---|
| Tech Lead | repository principal `rocha` (`acting-tech-lead`) | pending | — |
| Project Lead | unassigned | pending | — |

No go/conditional-go decision is implied by these drafts.
