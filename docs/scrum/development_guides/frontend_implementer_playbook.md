# Frontend implementer playbook — TUI + GUI (three lanes)

Status: `BINDING for FE-1 / FE-2 / FE-3 implementers`  
Updated: 2026-08-17  
Parent law: `frontend_senior_review_and_two_lanes.md`  
Board: `docs/scrum/roadmap_frontend.md`

This file is the **start-here** for the three frontend developers. Backend is **read-only**. Do not invent verbs, envelope fields, or manifest schemas.

---

## 0. Read order (do this before coding)

| Order | Document | Why |
|---|---|---|
| 1 | This playbook | Architecture, wire, events, competitor atoms, waves |
| 2 | `docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md` | D1–D6, J1–J5, write scopes |
| 3 | `docs/main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md` §0, §12.1–12.2, §15 | Normative JSON rules + event names |
| 4 | `docs/main_v4/09_vanguard_decision_register_v040.md` **ADR-0062** | UDS daemon + Ed25519 outside runtime |
| 5 | `docs/front_v4/003_wire_consumer.md` | Implemented frames (not JSON-RPC) |
| 6 | `vanguard/clients/cli/src/contract/types.ts` + `parse.ts` + `adapters/live.ts` | Live TypeScript contract |
| 7 | `vanguard/packages/runtime/service/server.py` + `service.py` | Verbs, 1 MiB, `receipt`/`error`/`event` |
| 8 | `docs/scrum/development_guides/cli_tui_architecture.md` | Hexagonal TUI tree + live appendix |
| 9 | `docs/scrum/development_guides/tui_product_surface.md` | Claude-class Ink chrome |
| 10 | `docs/scrum/development_guides/gui_ide_slots.md` | Tauri slots |
| 11 | `features_to_add_v430.md` §1–2, §5 P0 client rows | Harvest atoms vs loops |
| 12 | `docs/scrum/development_guides/02_manifest_and_pack_authoring.md` | Manifest shape (FE displays; BETA owns files) |
| 13 | Lane kits under `docs/scrum/sprints_front/` | Checkboxes + DoD |

**`docs/front_v4/`:** **keep the folder.** Canonical short files `001_backlog.md` … `012_decision_register.md` are Proposed consumer notes. **Ignore** long-named duplicates and anything marked VOID (`009_vanguard_lean_vscode_fork_engineering_spec.md`, `003_vanguard_wire_protocols_rpc_and_mcp_spec.md`). Do **not** treat `front_v4` as VG-04.

---

## 1. Architecture (one core, two skins, never a third wire)

```text
                    ┌──────────── vg --headless (JSONL stdout)
                    │
 Operator ──► Ink TUI (FE-2) ──┐
                    │          │
                    │     @vanguard/client-core (FE-1)
                    │          │  RuntimeClient
                    │          │  parse (CT-03) · reduceRunView · OperatorSigner
                    │          ▼
                    │     vg.4 NDJSON 1 MiB  UDS
                    │          │
                    │     RuntimeService (Python, frozen)
                    │
 GUI slots (FE-3) ──┘  same core
      Monaco / xterm / tree / git CLI are LOCAL IDE slots, not the agent loop
      PTY may run `vg` = TUI inside GUI
```

**Hexagonal rule:** presentation (Ink or React) → application reducers → `RuntimeClient` port → adapters. No `vanguard/packages` imports from FE.

**Identity:** `seq` is decimal **string** (IntString, CT large-int). Reconnect: `afterSeq`, dedupe by `eventId`. Optimistic UI: command `requested` until `ApprovalResolved` / `EpisodeCompleted` / `RunAborted`.

**CT rules FE must obey** (VG-04 §0): JSON only; no `undefined` on wire; RFC 3339 ms UTC; `sha256:` digests; enums as strings; **parse at process boundary (CT-03)** — `JSON.parse` then `parseEventEnvelope` / `parseDaemonFrame`, never `as EventEnvelope`; preserve unknown fields (CT-11, CT-44).

---

## 2. Wire contract (implemented — do not “improve”)

Source: `003_wire_consumer.md`, `server.py`.

| Item | Value |
|---|---|
| Transport | Unix domain socket, NDJSON lines, UTF-8 |
| Path | `--socket-path` → `VANGUARD_RUNTIME_SOCKET` → `/tmp/vanguard-runtime.sock` |
| Cap | `MAX_FRAME_BYTES = 1 MiB` |
| version | `"vg.4"` |
| Client frame | `frameType: "command"` + `command.{name,commandId,idempotencyKey,runId,actor,payload}` |
| Verbs | `StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `Cancel`, `Checkpoint`, `Resume`, `RecordCorrection`, `ExplainArtifact` |
| Replies | `receipt` (`status` completed/error) or `error` or stream `event` |
| `StartRun.payload` | `{ manifestPath, repoPath, brief }` **only** |
| Approvals | RFC 8785 JCS of decision payload; Ed25519; keys `~/.vanguard/keys` 0600 |

**Not on the wire:** JSON-RPC, `Ping`, `ListManifests`, MCP, Named Pipe, 4 MiB frames. Those are J2/J3/J5 or VOID.

**Client API** (`types.ts` `RuntimeClient`): `startRun`, `streamEvents` (`AsyncIterable<Result<StreamItem>>`), `getRun`, `requestCancel`, `requestCheckpoint`, `requestResume`, `explainArtifact`, `resolveApproval`, `recordCorrection`, `getDaemonStatus`. Failures are `Result` (`not_available`, `transport_interrupted`, …), not thrown domain errors.

---

## 3. Event envelope & UI mapping

Envelope: `schemaVersion: "vg.4"`, `eventId` UUID, `scope` ∈ episode\|governance\|evolution\|recovery, `seq` IntString, timestamps, tenancy fields, `payload.kind`.

**VG-04 §12.2 kinds** (only vocabulary). UI mapping:

| Kind | TUI | GUI slot |
|---|---|---|
| `ObservationProduced` | thought line (`payload.text`) | Run transcript |
| `OperatorInvoked` | tool card | Run + optional canvas node |
| `ProposalProduced` | compact card | Run |
| `BudgetCommitted` | status budget | Run header |
| `EffectPreviewed` / `EffectStarted` / `EffectCompleted` / `EffectReconciled` | tool/effect timeline | Run + diff if patch |
| `AuthorizationDenied` | hard fail | banner |
| `ApprovalRequested` | modal; wait for `ApprovalResolved` | Monaco diff + sign |
| `ApprovalResolved` | close modal | close approve slot |
| `EpisodeStarted` / `EpisodeStateChanged` / `EpisodeCompleted` | run lifecycle | Run |
| `Heartbeat` / `RunRecovered` / `RunAborted` | connection chrome | status |
| `ActivationChanged` | `vg why` | Why slot |
| unknown kind | opaque row | opaque node |

Do **not** emit `run.started`, `token`, `progress` as ledger kinds.

**Reducer law:** `EventEnvelope[] → reduceRunView → RunViewModel → selectors → props`. GUI uses the same function; do not reimplement in React.

---

## 4. Manifest (display only)

Shape (`005_manifests.md`, `domain/artifacts/manifest.py`):  
`{ harness, components, capabilities[{verb,sink,selector,risk}], evaluators, budgetPolicy }`.  
`sink` ∈ `pure|observation|privileged`.  
FE never walks `vanguard/packages/agency/manifests/`. Operator passes `--manifest` path (J3).

---

## 5. How competitor TUIs work — what we copy vs refuse

Read **public docs**, optional sibling clones `../_refs/` (`features_to_add_v430.md` §6). **Never submodule** their `src/` as a runtime.

| Product | Frontend atom to copy | Leave (their loop / skin) | Vanguard slot |
|---|---|---|---|
| **Claude Code** | Permission prompt with file/diff; `Esc` interrupt; streaming assistant+tool transcript; short status; resume session | Anthropic SDK loop, 28k cold start, their MCP UI | TUI layout + `requestCancel` + `ApprovalRequested` |
| **OpenCode** | TUI/server split; permission copy; `AGENTS.md` as *file the model reads* | Their agent while-loop, plugin host as authority | Pack genes (BETA); FE only shows path |
| **Codex CLI** | Sandbox knob ≠ approval knob (two lights in status) | Cloud handoff as required UX | Status bits; policy is daemon |
| **Pi** | Tiny chrome, four primitives, JSONL session *idea* | Importing their loop | Headless JSONL; ledger is session |
| **Aider** | “Read the map first” (repo map) | Aider as the product | `IndexPort` observation when ALFA lands; FE renders `ObservationProduced` |
| **mini-SWE-agent** | 100-line viewer, dense grep/lint receipts | Their scaffold | Adapter receipts (BETA); TUI shows `EffectCompleted` text |
| **Cline / Cursor** | Inline diff approve/reject | Shadow-git, YOLO, VS Code host | GUI approve slot + Monaco diff |

**TUI engineering (hard):** alternate screen, `NO_COLOR`, width reflow, Ink `useInput` vs prompt focus (don’t steal `y` while typing the brief), virtualize transcript (Ink has no DOM virt — window a slice of `RunViewModel` by cursor index), one `AbortController` per stream, 10k ring buffer already in live adapter.

---

## 6. How IDE GUIs work — bind, don’t rebuild

A coding IDE is a **workbench**: activity bar + editor groups + panel + status bar + command palette. VS Code/JetBrains/Zed/Lapce all do this. We **bind libraries into slots**, we do not fork workbench.git.

| Concern | How famous IDEs do it | Our bind (`gui_ide_slots.md`) |
|---|---|---|
| Files | Tree + watchers + ignore | Tauri `fs` + virtualized tree; ignore `.git`/`node_modules` |
| Editor | Buffer + LSP + dirty state | Monaco model per tab; **LSP servers = Phase 4** |
| Git | `git` porcelain / libgit2 | spawn `git status -sb`, `git branch --show-current` — **display**; ledger is truth |
| Terminal | PTY + xterm.js | `@xterm/xterm` + `portable-pty`; optional `vg` |
| Menus / palette | Command registry | cmdk → `RuntimeClient` methods + slot focus |
| Search | ripgrep | later slot; not a daemon verb |
| Agent | sidebar chat + apply patch | **Run + Approve slots** on vg.4 — not a second chat runtime |

**Hard GUI details:** Tauri 2 IPC for fs/pty (webview cannot raw POSIX pty); dispose Monaco models; do not put full ledger in React state (hold cursor + window on core buffer); `source: mock` badge on replay; Windows UDS = J5 (dev on Linux/WSL first).

---

## 7. Waves (groups → waves → lanes in parallel)

```text
Wave 0  docs frozen (this file + board)          [DONE]
Wave 1  FE-1 extract ∥ FE-2 core wire + demo/headless ∥ FE-3 shell+replay  [DONE]
Wave 2  FE-1 selectors/graph/subscribe ∥ FE-2 SOTA TUI ∥ FE-3 files/Monaco/PTY
Wave 3  FE-2 resume/why ∥ FE-3 approve/git/palette/canvas
Wave 4  live UDS both skins (needs daemon runner — J1 for spawn only)
Wave 5  installers, soak, dogfood → ship
```

Wave 2 copy-paste prompts: `docs/scrum/sprints_front/wave2_implementer_prompts.md`.

FE-2/FE-3 Wave 2 must **not** wait for FE-1-6/1-7: use local windowing until `windowTranscript` / `toTraceGraph` exist, then swap imports.

---

## 8. Task breakdown

### Wave 1

**FE-1 group “extract”** (`lane_core_wave1.md`)

| ID | Task | Subtasks |
|---|---|---|
| FE-1-1 | Package `@vanguard/client-core` | scaffold `package.json` Node≥20; move `types.ts` `parse.ts`; export map; no React |
| FE-1-2 | Signer | move `signer.ts`; `canonicalize`; 0600 keys; JCS golden |
| FE-1-3 | View-models | move `run-view.ts` approvals/corrections; tests; optional `toTraceGraph(envelopes)` pure |
| FE-1-4 | Adapters | move live/replay/scenario/transport; CLI re-export; `cli` tests unmodified semantically |

**FE-2 group “stay green”** (`lane_a_wave1.md`)

| ID | Task | Subtasks |
|---|---|---|
| FE-2-1 | Import core | change imports; keep `vg` bin |
| FE-2-2 | Tree already `src/tui/**` | boundary test no tui in application |

**FE-3 group “shell”** (`lane_gui_wave1.md`)

| ID | Task | Subtasks |
|---|---|---|
| FE-3-1 | Tauri 2 + React | `vanguard-gui/`; ADR-FE-GUI-001; dock; slot registry interface |
| FE-3-2 | Replay panel | `ReplayRuntimeClient` + `reduceRunView`; fixture jsonl; `source: mock`; virtualize list |

### Wave 2

**FE-1 group “SDK”** (`lane_core_wave2.md`) — `selectStatusBar`, `windowTranscript`, `toTraceGraph`, `subscribeRun`, commands.ts import hygiene.

**FE-2 group “Claude chrome”** (`tui_product_surface.md`, `lane_tui_wave2.md`)

| ID | Task | Subtasks |
|---|---|---|
| FE-2-3…2-7 | demo / approve / J1 / headless / help | `[DONE]` Wave 1 |
| FE-2-8 | SOTA chrome | status; windowed transcript; prompt vs approval focus; ctrl+c → `requestCancel` |

**FE-3 group “workbench slots”** (`lane_gui_wave2.md`)

| ID | Task | Subtasks |
|---|---|---|
| FE-3-0 | Toolchain | lockfile; Vite installs; `npm run dev` |
| FE-3-3 | Files + Monaco | tree virt; open file; encoding UTF-8; dispose models |
| FE-3-4 | xterm PTY | bash or honest `not_available`; optional `vg` |

### Wave 3

| ID | Task | Subtasks |
|---|---|---|
| FE-2-9 | Resume | `requestResume`; `not_available` honest |
| FE-2-why | `vg why` | `explainArtifact`; no fiction |
| FE-3-5 | xyflow | nodes from `payload.kind` only |
| FE-3-6 | Approve | Monaco diff + core signer |
| FE-3-7 | Palette + git | cmdk; `git status -sb` display |

### Wave 4 (live)

Same path resolution as CLI. Live never silent-fallback to mock. Blocked on real daemon **runner** (backend); socket client is FE-1-4.

---

## 9. DoD commands

```bash
cd vanguard/clients/client-core && npm run typecheck && npm test   # FE-1
cd vanguard/clients/cli && npm run typecheck && npm test           # FE-2
cd vanguard-gui && npm run typecheck && npm run dev                # FE-3
```

---

## 10. Stop conditions

New daemon verb, new `StartRun` field, reading core packs from FE, submodule of OpenCode/Cline/Void, Ink in DOM, JSON-RPC, `.vsix`, Code-OSS fork, RAG in the client.
