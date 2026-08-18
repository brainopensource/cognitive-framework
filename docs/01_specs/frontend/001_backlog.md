# 001 — Frontend Backlog (Pending Work)

> **Status**: Living Frontend Backlog (Pending Tasks Only)
> **Date**: 2026-08-17
> **Scope**: CLI TUI Enhancements (`FE-2`) and Standalone GUI App (`FE-3`).
> **Note**: Lane `FE-1` (`@vanguard/client-core`) and base TUI commands (`FE-2-1`..`FE-2-7`) are **100% IMPLEMENTED**.

---

## 1. Lane FE-2 — Pending TUI Product Surfaces (`vanguard/clients/cli/**`)

| ID | Summary | Target Subsystem / Location | Status |
|---|---|---|---|
| **FE-2-8** | Claude-class Chrome: virtualized transcript scrolling, prompt bar, interrupt signal | `vanguard/clients/cli/src/tui/` | `[TODO]` |
| **FE-2-9** | Live session resume chrome calling `requestResume` | `vanguard/clients/cli/src/application/` | `[TODO]` |

---

## 2. Lane FE-3 — `vanguard-gui/**` (Standalone GUI IDE App — Phase 2)

| ID | Summary | Target Subsystem / Architecture | Status |
|---|---|---|---|
| **FE-3-1** | App Shell (**Tauri 2 + React**, `vanguard-gui/`) | `vanguard-gui/` | `[PLANNED]` |
| **FE-3-2** | Import `@vanguard/client-core` & render replay run stream without daemon | `vanguard-gui/src/` | `[PLANNED]` |
| **FE-3-3** | File tree pane & Monaco Editor tab | `vanguard-gui/src/components/editor/` | `[PLANNED]` |
| **FE-3-4** | `@xterm/xterm` PTY terminal pane (running local `vg`) | `vanguard-gui/src/components/terminal/` | `[PLANNED]` |
| **FE-3-5** | `@xyflow/react` VG-04 event graph visualizer tab | `vanguard-gui/src/components/graph/` | `[PLANNED]` |
| **FE-3-6** | Monaco Diff viewer + Ed25519 Approve/Reject modal | `vanguard-gui/src/components/approval/` | `[PLANNED]` |
| **FE-3-7** | Command palette, slot registry & git status chrome | `vanguard-gui/src/components/chrome/` | `[PLANNED]` |
