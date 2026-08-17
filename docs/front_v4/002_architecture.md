# 002 — Frontend architecture (Proposed)

Status: `Proposed`  
Date: 2026-08-16  
Invariants below are the best content in this registry; keep them.

## INVAR-FE-01 … 04

| ID | Invariant |
|---|---|
| INVAR-FE-01 | The client is outside `vanguard/packages/`. It never imports kernel, agency, runtime internals, or adapters. |
| INVAR-FE-02 | One event vocabulary: VG-04 §12.2. The UI reduces envelopes; it does not invent ledger kinds. |
| INVAR-FE-03 | `RuntimeClient` is the only outbound port. Live, replay, and scenario adapters are interchangeable. Live never silently falls back to mock. |
| INVAR-FE-04 | Operator authority (Ed25519) stays in the client process. The daemon verifies; it does not hold the operator private key (ADR-0062). |

## 3. Trees (reality)

**CLI (binding after FE-A4)** — see `cli_tui_architecture.md` §5:

`vanguard/clients/cli/src/{contract,application,adapters,headless,tui/{components,screens,hooks,theme},composition}`

Today (pre-A4): `src/ui/`, `src/tui.tsx`, `src/main.tsx` still exist.

**IDE (FE-B):** `vanguard-ide/` VS Code extension. Webview + CodeLens + vendored contract. Not a Code-OSS tree.

## 4. Transports — proposed / backend-dependent

**Implemented:** Unix domain socket NDJSON (ADR-0062). Path order in 003.

**Proposed, not FE work:** Windows Named Pipe, TCP. File as Joint note **J5**. Do not implement a second transport in the client until the daemon speaks it.
