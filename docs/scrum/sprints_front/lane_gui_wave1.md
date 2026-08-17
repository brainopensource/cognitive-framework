# Lane FE-3 · Wave 1 — standalone GUI scaffold (not VS Code)

**Write scope:** `vanguard-gui/**` only  
**Depends:** FE-1-1 + FE-1-3 types/reducers (replay panel). PTY/Monaco stubs may start on FE-3-1 alone.  
**Do not touch:** `vanguard/clients/cli/**` internals · `vanguard/packages/**`  
**DoD default:** `cd vanguard-gui && npm run typecheck && npm run dev`

**Frozen stack (ADR-FE-GUI-001, write in `vanguard-gui/docs/ADR-FE-GUI-001.md`):** Tauri 2 + React + TypeScript. Not Electron unless ADR records a reversal. Not a Code-OSS fork. Not a VS Code extension.

**OSS bind (import libraries; do not vendor IDE trees):** Monaco, `@xterm/xterm`, `react-arborist` (or equivalent virtual list), `@xyflow/react` (event view only), `portable-pty` / Tauri shell sidecar for PTY. Reference clones live in sibling `../_refs/` per `features_to_add_v430.md` §6 — never `git submodule` OpenCode/Cline/Void.

---

## FE-3-1 — Shell + slot registry

App window, dock layout (editor | side | bottom), **slot registry** (`SlotId → React component`). Empty slots render a labelled placeholder. Command palette stub (cmdk/kbar) listing slot focus + `StartRun`/`requestCancel` when core is linked.

**DoD:** `npm run dev` opens the shell.

---

## FE-3-2 — Replay run panel (no daemon)

Import `@vanguard/client-core` `ReplayRuntimeClient` + `reduceRunView`. Load `vanguard/clients/cli/fixtures/sessions/successful-episode.jsonl` (or `fixtures/*.jsonl`). Visible `source: mock`. Virtualized transcript (do not mount one DOM node per historical event).

**DoD:** thoughts/tools/budget from fixture without a daemon.

---

## FE-3-3 — Files + editor slot

Virtualized file tree from a workspace path; Monaco tab for open file. Syntax highlighting via Monaco languages. **Full LSP servers = Phase 4** (harvest P3). No second file watcher protocol on the daemon.

**DoD:** open a file from the tree into Monaco.

---

## FE-3-4 — Terminal slot

xterm + PTY. Default shell; optional spawn `vg`. This **is** TUI-in-GUI. Do not render Ink in the DOM.

**DoD:** interactive shell in the dock.

---

## FE-3-5 — Event canvas slot

xyflow nodes/edges derived from VG-04 envelope kinds only. Passive. Clicking a node shows payload; it must not dispatch tools.

**DoD:** graph updates from the same replay stream as FE-3-2.

---

## FE-3-6 — Diff + approve slot

Monaco diff on `ApprovalRequested`. Approve/Reject calls core signer. No empty digest success (J4).

**DoD:** replay fixture with `ApprovalRequested` shows diff; reject/approve hits `RuntimeClient.resolveApproval`.

---

## FE-3-7 — Git + command palette (thin)

Git: `git status`/`branch` via process spawn (Tauri command), display only. Ledger remains authority. Palette: focus slot, run replay, cancel run — all mapped to existing `RuntimeClient` methods or local UI.

**DoD:** branch name visible; palette opens with ≥3 actions.
