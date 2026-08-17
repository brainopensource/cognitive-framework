# Sprint 1: Core Wire IPC, Live Daemon Client & React+Ink Terminal TUI (`vg`)

**Sprint ID:** `SPRINT-FE-01`  
**Phase / Wave:** `Wave 1 — Terminal Interaction Surface`  
**Foundation Docs:** [`docs/front_v4/002_vanguard_frontend_architecture_and_planes.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/002_vanguard_frontend_architecture_and_planes.md), [`docs/front_v4/003_vanguard_wire_protocols_rpc_and_mcp_spec.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/003_vanguard_wire_protocols_rpc_and_mcp_spec.md), [`docs/front_v4/004_vanguard_uiux_views_and_interaction_workflows.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/004_vanguard_uiux_views_and_interaction_workflows.md), [`docs/front_v4/006_vanguard_frontend_dev_guide_and_pseudocode.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/006_vanguard_frontend_dev_guide_and_pseudocode.md)  
**Primary Goal:** Build the resilient TypeScript UDS/NDJSON client, wire schema validators, Ed25519 signer, and the interactive React+Ink terminal UI.

---

## Sprint Goals & Deliverables

1. **Robust Socket Transport:** Implement `LiveDaemonClient` over Unix Domain Sockets and Windows Named Pipes with exponential backoff auto-reconnect and framed line parsing.
2. **Asymmetric Operator Signer:** Implement `OperatorSigner` with Ed25519 keypair generation, RFC 8785 canonical bytes hashing, and signature generation.
3. **Interactive TUI Core:** Implement React + Ink terminal interface (`StreamRenderer`, `DiffViewer`, `ApprovalModal`, `PromptBar`, `BudgetMeter`).
4. **End-to-End Terminal Session:** Connect `vg` to the Python runtime daemon, execute live runs, and resolve interactive capability approvals.

---

## Detailed Task Breakdown

### TASK-FE-101: Live Daemon Client & Stream Parser
* **Subtasks:**
  * Implement `LiveDaemonClient` in [`vanguard/clients/cli/src/adapters/live.ts`](file:///home/rocha/Coding/Aether-D-System/vanguard/clients/cli/src/adapters/live.ts).
  * Implement NDJSON frame buffer with split-line handling and $4\text{ MB}$ payload safeguard.
  * Implement JSON-RPC 2.0 request/response matching with timeout rejection.
  * Implement `StreamEvents` event emitter with typed `LedgerEvent` models.
* **Target Files:** `vanguard/clients/cli/src/adapters/live.ts`, `vanguard/clients/cli/src/contract/wire.ts`
* **Est. LOC:** ~320 LOC | **Complexity:** 65/100 | **Seniority:** Senior Dev (4★)

### TASK-FE-102: Cryptographic Operator Approval Signer
* **Subtasks:**
  * Implement `OperatorSigner` in [`vanguard/clients/cli/src/adapters/signer.ts`](file:///home/rocha/Coding/Aether-D-System/vanguard/clients/cli/src/adapters/signer.ts).
  * Auto-generate `~/.vanguard/keys/operator.key` with `0600` filesystem permissions.
  * Integrate `canonicalize` package for RFC 8785 JSON Canonicalization Scheme (JCS).
  * Implement Ed25519 signing and verification helper routines.
* **Target Files:** `vanguard/clients/cli/src/adapters/signer.ts`, `vanguard/clients/cli/src/application/signer.ts`
* **Est. LOC:** ~180 LOC | **Complexity:** 75/100 | **Seniority:** Tech Lead / Senior Dev (4★)

### TASK-FE-103: React Custom Hooks & Session State Machine
* **Subtasks:**
  * Implement `useVanguardRun` hook managing session lifecycle (`idle` $\to$ `running` $\to$ `waiting_approval` $\to$ `completed`).
  * Implement bounded ring buffer for ledger events (max 5,000 items) to avoid memory leaks.
  * Implement `useEventStream` token chunk accumulator for smooth streaming text.
* **Target Files:** `vanguard/clients/cli/src/ui/hooks/useVanguardRun.ts`, `vanguard/clients/cli/src/application/session.ts`
* **Est. LOC:** ~260 LOC | **Complexity:** 50/100 | **Seniority:** Normal Dev (3★)

### TASK-FE-104: React + Ink Visual Components
* **Subtasks:**
  * Implement `StreamRenderer.tsx`: Token streaming, `<Thinking>` collapsible block, markdown code highlighter.
  * Implement `DiffViewer.tsx`: Unified green/red diff display with syntax highlighting.
  * Implement `ApprovalModal.tsx`: High-risk action prompt, `[A] Accept & Sign / [D] Deny` keybindings.
  * Implement `BudgetMeter.tsx`: Token spent, remaining budget, L1–L4 prompt cache hit rate indicator.
  * Implement `PromptBar.tsx`: Multiline text input with history buffer and `/` command autocomplete.
* **Target Files:** `vanguard/clients/cli/src/ui/*.tsx`
* **Est. LOC:** ~580 LOC | **Complexity:** 55/100 | **Seniority:** Normal Dev (3★)

### TASK-FE-105: CLI Bootstrap & Live Integration Test
* **Subtasks:**
  * Implement `main.tsx` and `tui.tsx` bootstrap routines.
  * Add unit tests with `ink-testing-library` and `node:test`.
  * Verify live end-to-end run against running Python `RuntimeService` daemon.
* **Target Files:** `vanguard/clients/cli/src/main.tsx`, `vanguard/clients/cli/test/tui.test.ts`
* **Est. LOC:** ~220 LOC | **Complexity:** 45/100 | **Seniority:** Normal Dev (3★)
