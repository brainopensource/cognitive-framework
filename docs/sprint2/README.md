# Sprint 2 closure

Status: `DONE — ENGINEERING CLOSED — APPROVAL-0003`  
Merged: PR #4 `sprint2/alpha-beta-gamma`  
Decision: `DECISION-0002`

## Done

| Item | Evidence |
|---|---|
| T2 kernel dispatch, attenuation, TCB alarm | `REQ-KRN-001..003` covered; ADR-0054 |
| T3 ledger, recovery, cassettes | `REQ-LEDGER-001..002` covered |
| T1.12–T1.15 dual readers / profiles | `REQ-SCHEMA-012`, `REQ-CONF-001` covered; schemas remain DRAFT |
| T7.1–T7.4 graph + `vg-shell-only` | `REQ-GRAPH-001`, `REQ-BASELINE-001` covered |
| T0b disposable slice (deterministic) | `@vanguard/disposable-slice` 5/5; `slice-findings.md` |
| Mock CLI | `REQ-CLI-001` covered; 3/3 |

## Residual (not a T2/T3 re-open)

- Live T0b (`REQ-SLICE-001`) — no disposable credential on 2026-08-15
- Schema `LOCKED` — withheld until T0 human gates (GAP-010..014 bundle, timing)
- Hosted branch protection on `main` — `gh` 404 unprotected

Sprint 3 does not re-implement T2 or T3 (`ADR-0055`).
