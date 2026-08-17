# Vanguard GUI — Slot-Based IDE (Phase 2)

Status: `PROPOSED ARCHITECTURE GUIDE`  
Authority: `frontend_senior_review_and_two_lanes.md` (D3, D4)  
Parent: `docs/front_v4/009_ide_extension.md`  
Related: `tui_product_surface.md` (same operator loop, different skin)

---

## 1. Strategy

Standalone desktop IDE. **Not** a VS Code extension. **Not** a Code-OSS fork.

**Build what is Vanguard** (run stream, approvals, pack path, budget, event view).  
**Bind what is already solved** (files, editor, git, terminal, menus, palette).

Frozen directory: **`vanguard-gui/`**. Frozen shell: **Tauri 2 + React + TypeScript** (`ADR-FE-GUI-001`). Rust side: fs walk, PTY, `git` spawn, window/menu — not a second runtime.

One core, two skins: `@vanguard/client-core` + Ink TUI; GUI slots bind the same reducers. Optional PTY running `vg` = TUI inside the IDE.

---

## 2. Slot registry (flexibility)

Every panel is a `SlotId` with a React component and a data adapter. Adding UX = new slot, not a layout rewrite.

```text
SlotId =
  | "editor" | "files" | "terminal" | "git"
  | "run" | "approve" | "trace-canvas" | "why" | "pack"
```

Host provides: dock (split panes), activity bar, command palette, theme tokens (same names as TUI: `accent`, `warning`, `danger`, `muted`). Slots must tolerate missing data (`not_available`).

**Performance:** virtualize file tree and run transcript; keep event history in the core ring buffer, not unbounded React lists; Monaco models disposed on tab close.

---

## 3. Slot → library (import, don’t vendor IDEs)

| Slot | Bind | Vanguard data | Do not |
|---|---|---|---|
| Editor | Monaco (or CodeMirror 6) | open files under `StartRun` repo | fork VS Code workbench |
| Files | `react-arborist` / virtual list + Tauri fs | repo path | walk `vanguard/packages` for “discovery” |
| Terminal | `@xterm/xterm` + PTY | optional `vg` | embed Ink in DOM |
| Git | `git` CLI via Tauri | display only | shadow-git as authority |
| Menus / palette | native menu + cmdk | actions → `RuntimeClient` / slot focus | new wire verbs |
| Diff / approve | Monaco diff + `OperatorSigner` | `ApprovalRequested` | empty digest success |
| Run / budget | `reduceRunView` | envelopes | second agent loop |
| Why | `explainArtifact` | `not_available` if empty | fabricated evidence |
| Pack inspector | read user-supplied manifest path | J3 until ListManifests | invent schema |
| Event canvas | `@xyflow/react` | VG-04 kinds as nodes | workflow engine / MCP |

**LSP:** Monaco built-in tokenization now. Language servers = Phase 4 (harvest P3).  
**Reference clones:** `../_refs/opencode` etc. for **UX copy**, not submodules (`features_to_add_v430.md` §6). Lapce = layout density reference only.

---

## 4. Forbidden

Second agent loop; second DAG engine; local RAG/vector DB; competitor IDE git submodules; Ink-in-DOM; client SIEM/DLP; Named Pipe until J5.

---

## 5. Replay & parallel

FE-3 develops against `ReplayRuntimeClient` + CLI fixtures with `source: mock`. No daemon required for FE-3-1…3-6 except live socket later (same path resolution as CLI).
