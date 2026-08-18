---
id: FE-02
file: 002_architecture.md
title: "Vanguard v4.0 — Frontend Architecture & Invariants"
version: 4.0.0
status: NORMATIVE
authority_scope: >
  The foundational architectural law and boundaries for all frontend skins,
  including Client Core, CLI TUI, and the Standalone GUI IDE.
supersedes: none
superseded_by: none
budget_words: 2500
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — Frontend Architecture & Invariants

> **Who this is for.** Anyone building or modifying client components interacting with the Vanguard runtime.

---

## 1. System Invariants (`INVAR-FE-01` … `04`)

| ID | Invariant |
|---|---|
| `INVAR-FE-01` | The client is strictly outside `vanguard/packages/`. It never imports kernel, agency, runtime internals, or backend adapters. |
| `INVAR-FE-02` | One event vocabulary: VG-04 §12.2. The UI reduces envelopes; it does not invent ledger kinds. |
| `INVAR-FE-03` | `RuntimeClient` is the only outbound port. Live, replay, and scenario adapters are interchangeable. Live never silently falls back to mock. |
| `INVAR-FE-04` | Operator authority (Ed25519) stays in the client process. The daemon verifies; it does not hold the operator private key (ADR-0062). |

---

## 2. Package Topology & Real Trees

1. **Client Core (`@vanguard/client-core` — Lane FE-1):**
   `vanguard/clients/client-core/src/{contract,adapters,application}`
   Pure TypeScript: contract types, `parseEventEnvelope`, `OperatorSigner` (RFC 8785 Ed25519), `RuntimeClient` port, and `reduceRunView`.

2. **CLI TUI (`vanguard/clients/cli/**` — Lane FE-2):**
   `vanguard/clients/cli/src/{headless,tui/{components,screens,hooks,theme},composition,main.tsx}`
   Ink presentation and binary entrypoint. Imports `@vanguard/client-core`.

3. **Standalone GUI IDE (`vanguard-gui/**` / `apps/desktop/` — Lane FE-3):**
   Standalone desktop application shell (Tauri 2 / React). Slot-based architecture (Monaco, xterm PTY, xyflow event viewer). Imports `@vanguard/client-core`.

---

## 3. Transports

- **Implemented:** Unix domain socket NDJSON (ADR-0062).
- **Future Joint Scope (J5):** Windows Named Pipe, TCP. Do not implement a second transport in the client until the daemon speaks it.
