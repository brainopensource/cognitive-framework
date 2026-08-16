# Lane DD Developer Packet — React Ink TUI Screens & Single-Key Correction Capture

**Assignee:** Mid Developer D  
**Tickets:** `S6-DD-001`, `S6-DD-002`  
**Complexity:** Level 3 / 5 (Fast Lane)  
**Contract Row:** [`REQ-CLI-002`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json)  
**Owned Code:** `vanguard/clients/cli/src/ui/`  
**Target Test:** `npm --workspace @vanguard/cli test`

---

## 1. Scope & Objective
Implement the interactive **React Ink TUI Screens** in `@vanguard/cli`:
1. **Live Execution Screen:** Renders streaming thought chunks, active tool invocations, and live token/cost counters.
2. **Unified Diff Approval Modal:** Renders colorized unified diffs with line additions/deletions. Provides explicit `[y] Approve`, `[n] Reject`, and `[c] Correct` keybindings.
3. **Single-Keystroke Correction Capture (`S6-DD-002`):** When user presses `[c]`, prompt single-key taxonomy: `[d]efect`, `[s]tyle`, `[t]est`, `[s]ecurity`, `[a]rchitecture`, and persist `CorrectionRecord` to ledger.

---

## 2. Invariants & Rules
1. **Hexagonal Client Isolation:** Pure client living outside `vanguard/packages/`. Communicates strictly via `RuntimeClient` async event streams.
2. **No Terminal Escape Leaks:** Headless mode (`vg run --headless`) disables all Ink UI components and emits pure JSON lines.

---

## 3. Verification Gate
```bash
npm --workspace @vanguard/cli test
```
Must prove: Diff approval component handles approve/reject callbacks; correction capture persists typed taxonomy records.
