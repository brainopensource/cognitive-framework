# 012 — Frontend decision register (Proposed)

Status: `Proposed`  
Date: 2026-08-16  
Product ADRs live in `docs/main_v4/09_vanguard_decision_register_v040.md`. This file only tracks FE-local choices.

## Citations, not duplicate ADRs

| Old FE id | Disposition |
|---|---|
| ADR-FE-002 (wire / daemon) | Cite **ADR-0062** |
| ADR-FE-004 (operator signatures) | Cite **ADR-0062** |
| ADR-FE-003 (fork the editor) | **Replaced by D3**: extension-first; fork is a documented reversal (009) |

Lane lock: D1–D6 in `frontend_senior_review_and_two_lanes.md`.

## Anti-patterns

- Casting daemon JSON to TypeScript types (`CT-03`).
- Silent mock fallback in live mode.
- Empty `argsDigest` / `descriptorDigest` presented as a successful signature (FE-A8).
- Reading `vanguard/packages/` from the client for “discovery”.
- Adding command names the daemon does not implement.
- Claiming JSON-RPC, `Ping`, or 4 MiB frames as current law.

## Checklist before merging FE work

- [ ] Path is `clients/cli` or `vanguard-ide` only
- [ ] Event kinds ⊆ VG-04 §12.2 or explicitly unknown-preserved
- [ ] DoD command from ROADMAP board ran
- [ ] No Joint-scope invention
- [ ] Mock/replay labelled `source: mock`
