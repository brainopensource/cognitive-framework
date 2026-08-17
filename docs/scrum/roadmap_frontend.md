# Frontend roadmap (living board)

Status: `LIVING BOARD`  
Updated: 2026-08-17  
Law: `docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md`  
**Start here (implementers):** [`development_guides/frontend_implementer_playbook.md`](development_guides/frontend_implementer_playbook.md)

Statuses: `[DONE]` `[DOING]` `[TODO]` `[BLOCKED]` `[VOID]` `[DEFERRED]`

---

## 0. Keep or delete `docs/front_v4/`?

**Keep the folder. Do not delete it.**

| Keep (canonical, Proposed) | Ignore / VOID |
|---|---|
| Short files `001_backlog.md` … `012_decision_register.md`, `README.md`, `003_wire_consumer.md` | Long-named duplicates (`001_vanguard_frontend_*`, `003_vanguard_wire_protocols_rpc_and_mcp_spec.md`, …) |
| Wire consumer, tokens, manifest display, testing pyramid | `009_vanguard_lean_vscode_fork_engineering_spec.md` (**VOID**) |

`front_v4` is **not** VG-04. Normative wire = `docs/main_v4/04_…`. Active plan = this board + `docs/scrum/**`.

---

## 1. Doc map (what to open)

| Need | Open |
|---|---|
| D1–D6, J1–J5, lanes | `development_guides/frontend_senior_review_and_two_lanes.md` |
| Architecture, events, competitor atoms, **waves + subtasks** | `development_guides/frontend_implementer_playbook.md` |
| Hexagonal TUI + live frames appendix | `development_guides/cli_tui_architecture.md` |
| Claude-class Ink chrome | `development_guides/tui_product_surface.md` |
| Tauri slots, files/git/term | `development_guides/gui_ide_slots.md` |
| Harvest atoms vs loops | `features_to_add_v430.md` |
| Event names | VG-04 §12.2 (`docs/main_v4/04_…`) |
| Frames | `docs/front_v4/003_wire_consumer.md` + `server.py` |
| Kits | `sprints_front/lane_core_wave1.md`, `lane_a_wave1.md`, `lane_a_wave2.md`, `lane_gui_wave1.md` |
| Navigator | `docs/scrum/ROADMAP.MD` |

VOID: `sprints_front/sprint1`–`sprint4`, `lane_b_wave*.md`, VS Code extension / Code-OSS fork.

---

## 2. Rules

1. One client core, two skins (`@vanguard/client-core`). Never a third wire (vg.4 NDJSON UDS, 1 MiB, no new verbs).
2. Steal competitor **atoms**, not submodules.
3. Write scopes: FE-1 `vanguard/clients/client-core/**` · FE-2 `vanguard/clients/cli/**` · FE-3 `vanguard-gui/**` (Tauri 2 + React).
4. Backend frozen. Gaps = J1–J5.

---

## 3. Phases

| Phase | Focus | Status |
|---|---|---|
| **0 Docs** | Law, playbook, kits, void extension | `[DONE]` |
| **1 Wave 1–3** | Core extract + SOTA TUI + GUI slots | `[TODO]` implementers |
| **2 Live** | Both skins on real daemon | `[TODO]` / `[BLOCKED]` J1 runner |
| **4+** | LSP servers, J5 transports, RAG views | `[DEFERRED]` |

CLI hygiene FE-A1–A10 (dead code, transports, JCS, `--demo`, soak) already landed **inside** `vanguard/clients/cli` — still **extract** to client-core (FE-1).

---

## 4. Waves (parallel)

```text
Wave 0  [DONE]   docs
Wave 1  [TODO]   FE-1 extract ∥ FE-2 stay green ∥ FE-3 Tauri+replay
Wave 2  [TODO]   FE-2 Claude chrome ∥ FE-3 files/Monaco/PTY
Wave 3  [TODO]   FE-2 resume/why ∥ FE-3 approve/git/palette/canvas
Wave 4  [TODO]   live UDS both skins
```

---

## 5. Board

### 5.1 Docs / cleanup

| ID | Item | Status |
|---|---|---|
| DOC-1 | Two-lanes D3 GUI, three lanes | `[DONE]` |
| DOC-2 | Playbook (contracts, events, competitors, waves) | `[DONE]` |
| DOC-3 | `front_v4/` kept; fork spec VOID | `[DONE]` |
| DOC-4 | Kits `lane_core_wave1` + `lane_gui_wave1` | `[DONE]` |

### 5.2 Lane FE-1 — `@vanguard/client-core`

| ID | Scope | Depends | DoD | Status |
|---|---|---|---|---|
| FE-1-1 | types + parse package | — | core `typecheck && test` | `[TODO]` |
| FE-1-2 | signer + RuntimeClient | FE-1-1 | JCS golden | `[TODO]` |
| FE-1-3 | `reduceRunView` + approvals | FE-1-1 | reducer tests in core | `[TODO]` |
| FE-1-4 | live/replay/scenario adapters | FE-1-2 | CLI suite green via re-export | `[TODO]` |

Kit: `sprints_front/lane_core_wave1.md`

### 5.3 Lane FE-2 — Ink TUI

| ID | Scope | Depends | DoD | Status |
|---|---|---|---|---|
| FE-2-0 | Prior CLI deltas (delete dead, transports, demo, soak) | — | `cli` tests green | `[DONE]` in-tree |
| FE-2-1 | Import client-core | FE-1-4 | `cd vanguard/clients/cli && npm run typecheck && npm test` | `[TODO]` |
| FE-2-2 | `src/tui/**` hexagonal | FE-2-1 | `ui.test.ts` | `[DONE]` layout; re-wire after FE-1 |
| FE-2-3 | `--demo` `source: mock` | FE-2-1 | no daemon | `[DONE]`; keep after extract |
| FE-2-4 | y/n/c approve | FE-2-1 | no empty digests | `[DONE]` path; polish Wave 2 |
| FE-2-5 | daemon `not_available` J1 | — | no fake running | `[DONE]` |
| FE-2-6 | `--headless` JSONL | FE-2-1 | exit codes | `[DONE]` |
| FE-2-7 | `install.sh` + `--help` | FE-2-3 | flags listed | `[DONE]` |
| FE-2-8 | SOTA chrome (`tui_product_surface.md`) | FE-2-2 | virtualized transcript, prompt, ctrl+c | `[TODO]` |
| FE-2-9 | Resume UX → `requestResume` | FE-2-1 | honest `not_available` | `[TODO]` |

Kits: `lane_a_wave1.md`, `lane_a_wave2.md`

### 5.4 Lane FE-3 — `vanguard-gui/` (Tauri 2)

| ID | Scope | Depends | DoD | Status |
|---|---|---|---|---|
| FE-3-1 | Shell + slot registry + ADR-FE-GUI-001 | — | `npm run dev` | `[TODO]` |
| FE-3-2 | Replay run panel | FE-1-1, FE-1-3 | fixture, `source: mock` | `[TODO]` |
| FE-3-3 | File tree + Monaco | FE-3-1 | open file | `[TODO]` |
| FE-3-4 | xterm + PTY (`vg` optional) | FE-3-1 | interactive shell | `[TODO]` |
| FE-3-5 | xyflow event view | FE-3-2 | VG-04 kinds only | `[TODO]` |
| FE-3-6 | Monaco diff + signer | FE-3-2 | `resolveApproval` | `[TODO]` |
| FE-3-7 | Palette + git status display | FE-3-1 | ≥3 actions; branch label | `[TODO]` |

Kit: `sprints_front/lane_gui_wave1.md`

---

## 6. Joint (backend — not FE)

| ID | Need | Status |
|---|---|---|
| J1 | Daemon `__main__` / self-launch | `[BLOCKED]` |
| J2 | Ping/health verb | `[BLOCKED]` |
| J3 | ListManifests | `[BLOCKED]` |
| J4 | Populated approval digests | `[BLOCKED]` |
| J5 | Named Pipe / TCP | `[BLOCKED]` / `[DEFERRED]` |

---

## 7. DoD commands

```bash
cd vanguard/clients/client-core && npm run typecheck && npm test
cd vanguard/clients/cli && npm run typecheck && npm test
cd vanguard-gui && npm run typecheck && npm run dev
```
