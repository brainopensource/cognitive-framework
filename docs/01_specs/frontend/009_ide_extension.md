# 009 — Vanguard GUI — Standalone IDE App (Proposed)

Status: `Proposed`  
Date: 2026-08-17  
Directory name: **`vanguard-gui/`** (or `apps/desktop/`).

## Decision (D3)

Ship a **standalone GUI IDE** at **`vanguard-gui/`** (Phase 2). Stack frozen: **Tauri 2 + React + TypeScript**. Consumes `@vanguard/client-core` over vg.4 frames.

- **VS Code Extension (`vanguard-ide/**`, FE-B*) is VOID.**
- **Code-OSS fork is out of scope.**

Bind OSS **libraries** (Monaco, xterm, arborist, xyflow-as-view). Do not vendor IDE repositories. See `gui_ide_slots.md`.

## Slot-Based Modular Architecture

The GUI binds lightweight open-source building blocks into dedicated UI slots:

| UI Slot | Technology / Library | Role |
|---|---|---|
| **Editor** | Monaco Editor or CodeMirror 6 | Code editing, syntax highlighting, keybindings. |
| **Diff** | Monaco Diff Editor | Patch review during `ApprovalRequested`. |
| **Terminal** | `@xterm/xterm` + native PTY | Interactive shell / terminal running `vg`. |
| **File Tree** | Virtualized tree (`react-arborist` or clean DOM tree) | Workspace files from active repo. |
| **Git** | Native `git` CLI runner | Staging, uncommitted changes, branches. |
| **Run Stream** | `reduceRunView` (from `@vanguard/client-core`) | Real-time thoughts, tool calls, and budget tracker. |
| **Workflow Canvas** | `@xyflow/react` | **Passive visualizer** of VG-04 event trajectories only. |
| **Signer** | `OperatorSigner` (RFC 8785 Ed25519) | Signs approval decisions locally. |

## Terminal Integration

The GUI does not embed Ink components directly into the DOM (Ink is terminal-only). Instead, the GUI embeds `@xterm/xterm` connected to a PTY process running the `vg` CLI or shell.
