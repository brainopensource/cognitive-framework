# 002 — Frontend architecture (Proposed)

Status: `Proposed`  
Date: 2026-08-17  
Invariants below are the foundational law of all frontend skins.

## INVAR-FE-01 … 04

| ID | Invariant |
|---|---|
| INVAR-FE-01 | The client is outside `vanguard/packages/`. It never imports kernel, agency, runtime internals, or backend adapters. |
| INVAR-FE-02 | One event vocabulary: VG-04 §12.2. The UI reduces envelopes; it does not invent ledger kinds. |
| INVAR-FE-03 | `RuntimeClient` is the only outbound port. Live, replay, and scenario adapters are interchangeable. Live never silently falls back to mock. |
| INVAR-FE-04 | Operator authority (Ed25519) stays in the client process. The daemon verifies; it does not hold the operator private key (ADR-0062). |

## 3. Trees (reality)

1. **Client Core (`@vanguard/client-core` — Lane FE-1):**
   `vanguard/clients/client-core/src/{contract,adapters,application}`
   Pure TypeScript: contract types, `parseEventEnvelope`, `OperatorSigner` (RFC 8785 Ed25519), `RuntimeClient` port, and `reduceRunView`.

2. **CLI TUI (`vanguard/clients/cli/**` — Lane FE-2):**
   `vanguard/clients/cli/src/{headless,tui/{components,screens,hooks,theme},composition,main.tsx}`
   Ink presentation and binary entrypoint. Imports `@vanguard/client-core`.

3. **Standalone GUI IDE (`vanguard-gui/**` / `apps/desktop/` — Lane FE-3):**
   Standalone desktop application shell (Tauri 2 / React or Electron). Slot-based architecture (Monaco, xterm PTY, xyflow event viewer). Imports `@vanguard/client-core`.

## 4. Transports

**Implemented:** Unix domain socket NDJSON (ADR-0062). Path order in 003.

**Proposed, not FE work:** Windows Named Pipe, TCP. File as Joint note **J5**. Do not implement a second transport in the client until the daemon speaks it.
