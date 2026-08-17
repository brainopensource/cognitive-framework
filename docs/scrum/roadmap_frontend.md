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
| Kits | `sprints_front/lane_core_wave1.md`, `lane_core_wave2.md`, `lane_tui_wave2.md`, `lane_gui_wave2.md`, `wave2_implementer_prompts.md` |
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
| **1 Wave 1** | Core extract + CLI wire + GUI scaffold/replay | `[DONE]` 2026-08-17 |
| **1 Wave 2–3** | SOTA TUI chrome + GUI files/Monaco/PTY + core selectors | `[DOING]` Wave 2 prompts |
| **2 Live** | Both skins on real daemon | `[TODO]` / `[BLOCKED]` J1 runner |
| **4+** | LSP servers, J5 transports, RAG views | `[DEFERRED]` |

---

## 4. Waves (parallel)

```text
Wave 0  [DONE]   docs
Wave 1  [DONE]   FE-1 extract ∥ FE-2 core wire + demo/headless ∥ FE-3 shell+replay
Wave 2  [DOING]  FE-1 selectors/graph/subscribe ∥ FE-2 Claude chrome ∥ FE-3 files/Monaco/PTY
Wave 3  [TODO]   FE-2 resume/why ∥ FE-3 approve/git/palette/canvas
Wave 4  [TODO]   live UDS both skins
Wave 5  [TODO]   installers, soak, dogfood → ship
```

Wave 2 copy-paste prompts: [`sprints_front/wave2_implementer_prompts.md`](sprints_front/wave2_implementer_prompts.md)

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
| FE-1-1 | types + parse package | — | core `typecheck && test` | `[DONE]` |
| FE-1-2 | signer + RuntimeClient | FE-1-1 | JCS golden | `[DONE]` |
| FE-1-3 | `reduceRunView` + approvals | FE-1-1 | reducer tests in core | `[DONE]` |
| FE-1-4 | live/replay/scenario adapters | FE-1-2 | CLI suite green via re-export | `[DONE]` |
| FE-1-5 | Public API freeze + commands.ts import hygiene | FE-1-4 | barrel + CLI still green | `[TODO]` Wave 2 |
| FE-1-6 | `selectStatusBar` + `windowTranscript` | FE-1-3 | selector unit tests | `[TODO]` Wave 2 |
| FE-1-7 | `toTraceGraph(envelopes)` | FE-1-1 | golden vs successful-episode.jsonl | `[TODO]` Wave 2 |
| FE-1-8 | `subscribeRun` + AbortSignal | FE-1-4 | fake-iterable abort test | `[TODO]` Wave 2 |

Kits: `sprints_front/lane_core_wave1.md`, `lane_core_wave2.md`

### 5.3 Lane FE-2 — Ink TUI

| ID | Scope | Depends | DoD | Status |
|---|---|---|---|---|
| FE-2-0 | Prior CLI deltas (delete dead, transports, demo, soak) | — | `cli` tests green | `[DONE]` in-tree |
| FE-2-1 | Import client-core | FE-1-4 | `cd vanguard/clients/cli && npm run typecheck && npm test` | `[DONE]` 40/40 |
| FE-2-2 | `src/tui/**` hexagonal | FE-2-1 | `ui.test.ts` | `[DONE]` |
| FE-2-3 | `--demo` `source: mock` | FE-2-1 | no daemon | `[DONE]` |
| FE-2-4 | y/n/c approve | FE-2-1 | no empty digests | `[DONE]` |
| FE-2-5 | daemon `not_available` J1 | — | no fake running | `[DONE]` |
| FE-2-6 | `--headless` JSONL | FE-2-1 | exit codes | `[DONE]` |
| FE-2-7 | `install.sh` + `--help` | FE-2-3 | flags listed | `[DONE]` |
| FE-2-8 | SOTA chrome (`tui_product_surface.md`) | FE-2-2 | virtualized transcript, prompt, ctrl+c | `[TODO]` Wave 2 |
| FE-2-9 | Resume UX → `requestResume` | FE-2-1 | honest `not_available` | `[TODO]` Wave 3 |

Kits: `lane_a_wave1.md`, `lane_tui_wave2.md` (Wave 2 sprint), `lane_a_wave2.md` (historical FE-A6–A10)

### 5.4 Lane FE-3 — `vanguard-gui/` (Tauri 2)

| ID | Scope | Depends | DoD | Status |
|---|---|---|---|---|
| FE-3-0 | Toolchain: lockfile + Vite install | — | `npm install && npm run dev` | `[TODO]` Wave 2 (Wave 1 blocker) |
| FE-3-1 | Shell + slot registry + ADR-FE-GUI-001 | — | `npm run typecheck` | `[DONE]` scaffold; dev blocked until FE-3-0 |
| FE-3-2 | Replay run panel | FE-1-1, FE-1-3 | fixture, `source: mock` | `[DONE]` in-browser; not virtualized |
| FE-3-3 | File tree + Monaco | FE-3-1 | open file | `[TODO]` Wave 2 (stubs today) |
| FE-3-4 | xterm + PTY (`vg` optional) | FE-3-1 | interactive shell or honest `not_available` | `[TODO]` Wave 2 |
| FE-3-5 | xyflow event view | FE-3-2, FE-1-7 | VG-04 kinds only | `[TODO]` Wave 3 |
| FE-3-6 | Monaco diff + signer | FE-3-2 | `resolveApproval` | `[TODO]` Wave 3 |
| FE-3-7 | Palette + git status display | FE-3-1 | ≥3 actions; branch label | `[TODO]` Wave 3 |

Kits: `sprints_front/lane_gui_wave1.md`, `lane_gui_wave2.md`

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
