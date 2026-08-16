# Developer Prompt — Lane DD: Mid Developer D (Sprint 6)

**Role:** Mid Developer D (Client & Interactive Ink TUI)  
**Branch:** `sprint5-6/integration`  
**Base:** Sprint 5 merged cleanly on `sprint5-6/integration`  
**Assigned Packet:** [`docs/sprint6/dd-packet.md`](../../sprint6/dd-packet.md)  
**Contract Row:** [`REQ-CLI-002`](../../sprint0/active-mvp-contract.json)  
**Your Target Code:** `vanguard/clients/cli/src/ui/`

---

## 1. Goal
Implement the **React Ink TUI Screens** in `@vanguard/cli`: Live execution screen, unified diff approval modal, and single-keystroke human correction capture (`[d]efect`, `[s]tyle`, `[t]est`, `[s]ecurity`, `[a]rchitecture`).

---

## 2. Mandatory Reading Before Writing Code
Read these exact files in order:
1. [`docs/development/cli_tui_architecture.md`](../cli_tui_architecture.md) — §3 TUI Screen Specifications.
2. [`docs/sprint6/dd-packet.md`](../../sprint6/dd-packet.md) — Ink TUI screen components and keybinding taxonomy.
3. [`docs/sprint0/active-mvp-contract.json`](../../sprint0/active-mvp-contract.json) — `REQ-CLI-002`.
4. [`vanguard/clients/cli/src/`](../../../vanguard/clients/cli/src/) — Client codebase.

---

## 3. Strict Invariants (DO NOT DRIFT)
* **Hexagonal Isolation:** Client package lives outside `vanguard/packages/`. It consumes `RuntimeClient` events only.
* **No Terminal Escape Leaks:** Headless mode (`vg run --headless`) disables all Ink UI components and emits pure JSON lines.
* **Correction Persistence:** Pressing `[c]` during diff review logs a structured `CorrectionRecord` directly to the ledger.

---

## 4. Verification Gate
```bash
npm --workspace @vanguard/cli test
```
Push with commit message format: `[dev-dd] S6-DD-001: <reason naming REQ-CLI-002>`.
