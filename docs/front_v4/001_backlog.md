# 001 — Frontend backlog (Proposed)

Status: `Proposed`  
Date: 2026-08-17  
Maps to: `docs/scrum/roadmap_frontend.md` and `docs/scrum/sprints_front/`

IDs are **FE-1\*** (Client Core), **FE-2\*** (Ink TUI CLI), and **FE-3\*** (Standalone GUI Start). VS Code extension (`FE-B*`) and Code-OSS fork are VOID.

## Lane FE-1 — `@vanguard/client-core`

| ID | Summary | Kit |
|---|---|---|
| FE-1-1 | Extract types, parse, and result helpers into client-core | lane_core_wave1 |
| FE-1-2 | Move `OperatorSigner` (RFC 8785 Ed25519) + `RuntimeClient` port | lane_core_wave1 |
| FE-1-3 | Move `run-view` reducer + approvals application logic | lane_core_wave1 |
| FE-1-4 | Move `LiveRuntimeClient`, `ReplayRuntimeClient`, `ScenarioRuntimeClient` | lane_core_wave1 |

## Lane FE-2 — `vanguard/clients/cli/**` (Ink TUI Product)

| ID | Summary | Kit |
|---|---|---|
| FE-2-1 | Wire CLI to import `@vanguard/client-core` | lane_a_wave1 |
| FE-2-2 | TUI screens (`tui/screens/`) with hexagonal layout | lane_a_wave1 |
| FE-2-3 | `vg --demo` replay + `source: mock` | lane_a_wave2 |
| FE-2-4 | Interactive approval prompt (`y`/`n`/`c`) | lane_a_wave2 |
| FE-2-5 | Honest daemon lifecycle (`not_available` until J1) | lane_a_wave2 |
| FE-2-6 | `vg --headless` script execution mode | lane_a_wave2 |
| FE-2-7 | `install.sh` + global bin packaging | lane_a_wave2 |
| FE-2-8 | Claude-class chrome: status bar, virtualized transcript, prompt bar, interrupt (`tui_product_surface.md`) | lane_a_wave2 |
| FE-2-9 | Resume chrome calling `requestResume` (no new wire) | lane_a_wave2 |

## Lane FE-3 — `vanguard-gui/**` (Standalone GUI IDE App — Phase 2)

| ID | Summary | Kit |
|---|---|---|
| FE-3-1 | App shell (**Tauri 2 + React**, `vanguard-gui/`) + ADR-FE-GUI-001 | lane_gui_wave1 |
| FE-3-2 | Import `@vanguard/client-core` + render replay run stream without daemon | lane_gui_wave1 |
| FE-3-3 | Slot placeholder: File tree & Monaco Editor tab | lane_gui_wave1 |
| FE-3-4 | Slot placeholder: `@xterm/xterm` PTY terminal pane (running `vg`) | lane_gui_wave1 |
| FE-3-5 | Slot placeholder: `@xyflow/react` VG-04 event visualizer tab | lane_gui_wave1 |
| FE-3-6 | Slot: Monaco diff + Ed25519 Approve/Reject | lane_gui_wave1 |
| FE-3-7 | Slot registry + command palette + git status chrome | lane_gui_wave1 |
