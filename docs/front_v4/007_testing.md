# 007 — Frontend testing (Proposed)

Status: `Proposed`  
Date: 2026-08-17

## Pyramid

1. **Unit** — reducers, parse, signer (`@vanguard/client-core` tests; TUI component tests in `vanguard/clients/cli/test/`).
2. **VG-04 golden vectors** — client parse agrees with schema vectors; do not edit vectors to pass.
3. **Wire contracts** — `test/contracts/t1_wire_contracts.py` (backend-owned; FE consumes, does not relocate).
4. **Replay E2E** — JSONL fixtures under `vanguard/clients/cli/fixtures/` run through both TUI (`vg --demo`) and GUI replay panel without daemon.
5. **Live E2E** — real daemon UDS; not substitutable by mock.

Soak harness lives in `vanguard/clients/cli/test/`, **not** `tools/ci/`.

## Phantom paths (do not use)

- `docs/development/cli_tui_architecture.md` — live path is `docs/scrum/development_guides/cli_tui_architecture.md`
- `tools/ci/` frontend soak
- `github.com/vanguard-ai/*` CI templates

## GUI Testing (FE-3)

Unit tests in `vanguard-gui` test panel renders against replay fixtures. No `.vsix` testing required (extension is VOID).
