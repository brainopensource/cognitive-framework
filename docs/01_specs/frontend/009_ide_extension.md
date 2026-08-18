---
id: FE-09
file: 009_ide_extension.md
title: "Vanguard v4.0 — Standalone GUI IDE Architecture & Slot Model"
version: 4.0.0
status: PROPOSED
authority_scope: >
  Modular slot architecture, embedded component libraries, and desktop shell
  specifications for `vanguard-gui`.
supersedes: none
superseded_by: none
budget_words: 2500
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — Standalone GUI IDE Architecture & Slot Model

> **Who this is for.** Desktop application developers building the Phase 2 GUI.

---

## 1. Core Architecture & Stack Decision (D3)

Ship a **standalone GUI IDE** at **`vanguard-gui/`** (Phase 2).
- **Technology Stack**: Tauri 2 + React + TypeScript.
- **Consumption**: Consumes `@vanguard/client-core` over standard vg.4 frames.
- **Status**: VS Code extension (`FE-B*`) and Code-OSS fork are VOID.

---

## 2. Slot-Based Modular Architecture

| UI Slot | Technology / Library | Role |
|---|---|---|
| **Editor** | Monaco Editor / CodeMirror 6 | Code editing, syntax highlighting, keybindings. |
| **Diff** | Monaco Diff Editor | Patch review during `ApprovalRequested`. |
| **Terminal** | `@xterm/xterm` + native PTY | Interactive shell running `vg` CLI. |
| **File Tree** | Virtualized tree component | Workspace navigation. |
| **Git** | Native `git` CLI runner | Staging, uncommitted changes, branches. |
| **Run Stream** | `reduceRunView` | Real-time events, tool calls, and budget tracker. |
| **Workflow Canvas** | `@xyflow/react` | **Passive visualizer** of VG-04 event trajectories only. |
| **Signer** | `OperatorSigner` (RFC 8785 Ed25519) | Local cryptographic signing for approval decisions. |

---

## 3. Terminal Integration

The GUI embeds `@xterm/xterm` connected to a PTY process running the `vg` CLI or shell. Ink components are terminal-only and are not rendered into the browser DOM.
