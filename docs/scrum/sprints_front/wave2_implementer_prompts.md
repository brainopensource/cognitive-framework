# Wave 2 — three parallel implementer prompts

Status: `BINDING for Wave 2`  
Board: `docs/scrum/roadmap_frontend.md`  
Law: `docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md`  
Playbook: `docs/scrum/development_guides/frontend_implementer_playbook.md`

Paste **one** prompt per lane. Lanes are disjoint. Do not wait on each other except where a type already exists on `@vanguard/client-core` (Wave 1). If a core helper (`windowTranscript`, `toTraceGraph`) is not exported yet, FE-2/FE-3 implement a **local** clamp and swap to the core symbol when FE-1-6/1-7 land — do not block.

Backend remains frozen. Gaps = Joint J1–J5, not new verbs.

---

## Prompt FE-1 — Core product API (Wave 2 sprint)

```text
│ Goal: Productize @vanguard/client-core as the headless SDK both skins consume:
│       public-API hygiene, status/transcript selectors, pure VG-04 trace graph,
│       and a single AbortController-owned stream subscriber.

    You are Developer FE-1 (Client Core). Implement Lane FE-1 Wave 2 only.

    LAW & SCOPE:
    - Binding Law: docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md (D1–D6, J1–J5)
    - Architecture: docs/scrum/development_guides/cli_tui_architecture.md §2–4
    - Playbook: docs/scrum/development_guides/frontend_implementer_playbook.md §0–3, §8 Wave 2 FE-1
    - Kit: docs/scrum/sprints_front/lane_core_wave2.md
    - Active Board: docs/scrum/roadmap_frontend.md §5.2 (FE-1-5 through FE-1-8)
    - Normative wire: docs/main_v4/04_… §0, §12.1–12.2, §15; ADR-0062
    - Consumer note: docs/front_v4/003_wire_consumer.md (vg.4 NDJSON, 1 MiB, no JSON-RPC)
    - Write Scope: vanguard/clients/client-core/**
    - Import-path-only edits allowed on vanguard/clients/cli/src/{contract,adapters,application}/*.ts shims
    - MUST NOT EDIT: Ink/TUI chrome, vanguard-gui/**, vanguard/packages/**, pack JSON, docs/main_v4/**

    WAVE 1 GROUND TRUTH (do not re-extract):
    - Package exists at vanguard/clients/client-core (10/10 tests).
    - Barrel: src/index.ts exports contract, parse, signer, transports, live/replay/scenario, run-view, approvals, commands, corrections.
    - CLI presentation already imports @vanguard/client-core (FE-2 Wave 1). Keep CLI `npm test` green (40 tests).
    - Known hygiene bug: src/application/commands.ts currently emits `jsonLine` *before* `import type` — illegal ESM style; hoist imports.
    - CliOptions lives in commands.ts and is consumed by FE-2 parse-cli / streamRun. You MAY add HeadlessRunOptions as an alias; you MUST NOT remove CliOptions this sprint.

    TASK INTENT (PhD / SOTA client SDK — not a UI rewrite):

    1. FE-1-5 Public API freeze
       - Treat `@vanguard/client-core` barrel as the supported import. Keep package.json `exports` subpaths
         (`./application/run-view.js`, `./adapters/live.js`, …) so existing CLI shims do not 404.
       - No React, Ink, DOM, Tauri, Monaco, xyflow, CSS, or process.stdout styling in this package.
       - CT-03: parsers remain the only place external JSON becomes EventEnvelope. Never `as EventEnvelope`.
       - `jsonLine` encodes JSON.stringify only — no pretty-print, no ANSI.
       - seq is IntString (decimal string). Do not coerce to number.

    2. FE-1-6 Selectors + windowed transcript (virtualization without a DOM)
       Ink has no windowing; React must not hold the full ledger. Export pure functions:

         export type StatusBarModel = {
           source: StreamSource | "unknown";
           seq: string;
           tokens: number;
           costMicros: string;
           kind: string;
         };
         export function selectStatusBar(input: {
           view: RunViewModel;
           source: StreamSource | "unknown";
           lastSeq?: string;
           lastKind?: string;
         }): StatusBarModel;

         export type TranscriptRow =
           | { kind: "thought"; text: string }
           | { kind: "tool"; name: string; status: string }
           | { kind: "opaque"; label: string };

         export function windowTranscript(
           view: RunViewModel,
           cursor: number,
           height: number
         ): { rows: TranscriptRow[]; cursor: number; total: number };

       Semantics: height default 16; cursor clamped to [0, max(0, total-height)]; thoughts then tools
       (stable order: thoughts in arrival order, then tools). Do not re-run reduceRunView inside selectors.
       Unknown future envelope kinds never crash; they simply do not appear unless lastKind is shown on the status bar.

    3. FE-1-7 toTraceGraph — passive event DAG for the GUI canvas
       Export a UI-library-agnostic projection:

         export type TraceNode = { id: string; kind: string; seq: string; runId?: string };
         export type TraceEdge = { id: string; source: string; target: string };
         export function toTraceGraph(envelopes: readonly EventEnvelope[]): { nodes: TraceNode[]; edges: TraceEdge[] };

       Rules:
       - node.id = eventId (UUID as on the envelope; do not mint IDs).
       - node.kind = payload.kind (VG-04 §12.2 vocabulary; unknown kinds still become opaque nodes).
       - If parentEventId is a string, emit an edge parent → child.
       - Else chain consecutive envelopes that share the same runId ordered by BigInt(seq) (seq is still stored/emitted as string).
       - Do not import @xyflow/react. FE-3 maps {nodes,edges} later.
       - Golden: read-only vanguard/clients/cli/fixtures/sessions/successful-episode.jsonl
         (parse via parseJsonlLine). Node count == parsed envelope count.

    4. FE-1-8 subscribeRun — one stream owner
       Presentation must not each invent a for-await. Export:

         export function subscribeRun(
           client: Pick<RuntimeClient, "streamEvents">,
           cursor: EventCursor,
           handlers: {
             onItem: (item: StreamItem) => void;
             onError?: (error: ClientFailure) => void;
             onDone?: () => void;
           },
           signal?: AbortSignal
         ): Promise<void>;

       Own a single `for await` of client.streamEvents. If signal aborts, break; do not throw domain errors
       (port contract is Result). Adapter-level reconnect/afterSeq stays in LiveRuntimeClient (already Wave 1).

    TDD:
    - Tests live in vanguard/clients/client-core/test/*.test.ts (node:test, matching Wave 1).
    - No timing sleeps. Fake async iterables + AbortController only.
    - Do not modify CLI tests except if a re-export type name changes (should not).

    DoD:
    - cd vanguard/clients/client-core && npm run typecheck && npm test
    - cd vanguard/clients/cli && npm run typecheck && npm test   # non-breaking
    - grep -R "from 'react'\\|from \"ink\"\\|xyflow\\|monaco" vanguard/clients/client-core/src  → empty
    - Mark FE-1-5…FE-1-8 [DONE] on docs/scrum/roadmap_frontend.md only if DoD is green.
```

---

## Prompt FE-2 — Claude-class Ink TUI (Wave 2 sprint)

```text
│ Goal: Finish SOTA Ink chrome (FE-2-8): status bar, windowed transcript, detail/approval/why
│       column, prompt bar with a real focus state machine, ctrl+c → requestCancel, `?` help.
│       Keep demo/headless/signer/J1 honesty from Wave 1.

    You are Developer FE-2 (TUI Product Lead). Implement Lane FE-2 Wave 2 only (FE-2-8).

    LAW & SCOPE:
    - Binding Law: docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md
    - Surface: docs/scrum/development_guides/tui_product_surface.md  ← BINDING LAYOUT
    - Architecture: docs/scrum/development_guides/cli_tui_architecture.md
    - Harvest atoms (copy UX, not loops): features_to_add_v430.md §1–2
      Claude Code: permission+diff, Esc interrupt, streaming transcript, short status
      OpenCode: TUI/server split, permission copy
      Codex CLI: sandbox knob ≠ approval knob as two status bits (display only; policy is daemon)
      Pi: tiny chrome, JSONL is not the ledger — our ledger is
    - Kit: docs/scrum/sprints_front/lane_tui_wave2.md
    - Active Board: docs/scrum/roadmap_frontend.md §5.3 FE-2-8
    - Write Scope: vanguard/clients/cli/**  (src/tui/**, src/composition/**, src/headless/**, test/**, install.sh)
    - MUST NOT EDIT: client-core internals (except import paths), vanguard-gui/**, vanguard/packages/**

    WAVE 1 GROUND TRUTH (do not regress):
    - Presentation already imports @vanguard/client-core.
    - Hexagonal tree: src/tui/{components,screens,hooks,theme}/
    - P0-4 y/n/c via composition/operator-approval.ts → OperatorSigner when digests exist; empty digests are not fabricated (J4).
    - vg --demo labels source: mock; --headless NDJSON; manageDaemon start/stop = not_available (J1).
    - DoD last close: cd vanguard/clients/cli && npm run typecheck && npm test  → 40/40
    - Current chrome is a stacked column (VG / RUN, badge, LiveScreen, modal). That is NOT the binding layout yet.

    BINDING LAYOUT (implement this, not a dashboard):

      ┌─ vg · source · seq · budget ─────────────────────────┐
      │ transcript (windowed)      │ detail / approval / why │
      ├────────────────────────────┴─────────────────────────┤
      │ prompt bar  (brief)     hints: ctrl+c cancel · ?     │
      └──────────────────────────────────────────────────────┘

    TASK INTENT (terminal-systems / SOTA TUI):

    1. Focus state machine (hardest product bug in Ink TUIs)
       Modes: prompt | approval | correct | help | run.
       - While mode===prompt, alphanumeric keys including y/n/c go to the brief buffer. Enter submits.
       - Empty Enter does NOT call startRun; set a local status string invalid_request (Result-shaped, no throw).
       - While pendingApproval && mode!==prompt, y/n/c keep existing submitInteractiveApproval / correct taxonomy.
       - Ink useInput vs TextInput: do not register global y/n while the prompt is focused.
       - ctrl+c (and Esc when mode!==prompt): runtime.requestCancel(activeRunId) if a run id exists; do not process.exit.
       - `?` toggles help (plain text; must be readable under NO_COLOR=1). `q` still quits.

    2. Status bar
       One line: `vg · ${sourceLabel(source)} · seq ${seq} · tok ${tokens} · ${costMicros}µ · ${kind}`
       Prefer selectStatusBar from @vanguard/client-core if FE-1-6 has landed; otherwise derive from RunViewModel + hook state.
       Demo/replay: sourceLabel already maps replay→ `source: mock`. Never paint green “live” for mock.

    3. Windowed transcript
       Prefer windowTranscript(view, cursor, height) from core. Else local clamp of thoughts+tools to ~16 rows.
       PgUp/PgDn or j/k (only in mode===run) move cursor. Do not re-reduce envelopes on keystroke.
       Keep useVanguardRun as the single stream owner (or switch to subscribeRun if FE-1-8 exported).

    4. Detail column
       - Default: selected tool/thought text.
       - If pendingApproval: existing ApprovalModal (diff + y/n/c copy).
       - Why: a key `w` may call runtime.explainArtifact on a stub artifact id from the selected tool name;
         if Result.ok===false, render error.code (not_available) verbatim. Never invent ActivationChanged evidence.

    5. Prompt bar
       Feeds StartRun.brief. Wave 1 startRun already runs on mount. Change: do not auto-start with the default
       brief when stdin is a TTY and --prompt was not passed — wait for Enter on the prompt bar.
       Headless path MUST remain auto-start (do not break streamRun / --headless tests).
       Composition: TUI-only gate in RunTui / main.tsx; do not change client-core streamRun semantics.

    6. Layout engineering
       Ink Box flexDirection row for the two columns; column for chrome. Respect process.stdout.columns;
       if width < 80, stack (transcript above detail) — still two regions, not seven panels.
       Semantic theme tokens already in src/tui/theme/tokens.ts. No color-only meaning.

    TDD (extend test/ui.test.ts; node:test):
    - Focus: in prompt mode, key "y" does not call resolveApproval.
    - Empty Enter does not call startRun (fake client).
    - approvalActionForKey still y/n/c in approval mode.
    - window clamp: 100 thoughts → rendered slice length <= height.
    - NO_COLOR path: sourceLabel("mock") === "source: mock" (already exists; keep).
    - Do not use real sleeps; fake RuntimeClient.

    OUT OF SCOPE THIS SPRINT:
    - FE-2-9 requestResume chrome (Wave 3)
    - New daemon verbs, /mcp, parallel sessions, JSON-RPC

    DoD:
    - cd vanguard/clients/cli && npm run typecheck && npm test
    - ui.test.ts covers the new focus + window behaviors
    - vg --help unchanged completeness (wave2.test.ts)
    - vg run --demo --headless still emits source: mock JSONL
```

---

## Prompt FE-3 — Standalone GUI workbench (Wave 2 sprint)

```text
│ Goal: Unblock Vite, then replace CSS stubs with a real files slot + Monaco editor
│       and an honest xterm/PTY slot. Keep Wave 1 replay run panel (source: mock).

    You are Developer FE-3 (GUI Shell). Implement Lane FE-3 Wave 2 only (FE-3-0, FE-3-3, FE-3-4).

    LAW & SCOPE:
    - Binding Law: docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md (D3 standalone GUI; extension VOID)
    - Slots: docs/scrum/development_guides/gui_ide_slots.md
    - ADR: vanguard-gui/docs/ADR-FE-GUI-001.md (Tauri 2 + React + TypeScript — do not reverse without a new ADR)
    - Kit: docs/scrum/sprints_front/lane_gui_wave2.md
    - Playbook: docs/scrum/development_guides/frontend_implementer_playbook.md §6 (bind libraries, do not fork workbench.git)
    - Active Board: docs/scrum/roadmap_frontend.md §5.4 FE-3-0/3-3/3-4
    - Write Scope: vanguard-gui/**
    - MUST NOT EDIT: vanguard/clients/cli/** internals, client-core internals (import paths OK), vanguard/packages/**
    - MUST NOT: VS Code extension, Code-OSS fork, Ink-in-DOM, competitor git submodules, second agent loop, xyflow-as-engine

    WAVE 1 GROUND TRUTH:
    - Scaffold: vanguard-gui/src/main.tsx slot host (files|editor|terminal|run|trace-canvas|approve).
    - Replay: ReplayRuntimeClient.fromJsonl(..., "mock") + reduceRunView. Badge `source: mock`.
    - Monaco / xterm / xyflow are package.json deps but UI is mostly CSS stubs (fake tree, <pre> editor, fake `$ _` prompt).
    - typecheck was reported green; `npm run dev` was BLOCKED: vite not installed; npm install failed
      (`Class extends value undefined is not a constructor or null`). Fix the toolchain first.
    - Switch in main.tsx is missing a `case "approve"` (falls through incorrectly). Fix as a drive-by if you touch that file.
    - Do not put the full EventEnvelope[] into React state long-term. Wave 1 collected `events` for the stub canvas;
      Wave 2 run transcript should window. Full canvas bind is Wave 3 (toTraceGraph).

    TASK INTENT (IDE-systems / SOTA workbench — bind, don’t rebuild):

    0. FE-3-0 Toolchain (first hour, non-negotiable)
       - engines.node >= 20 in package.json. Commit package-lock.json (or npm-shrinkwrap) that actually installs vite.
       - Install with `npm install --workspaces=false` from vanguard-gui (parent repo is an npm workspace and
         previously threw EUNSUPPORTEDPROTOCOL on workspace:*). Document this in vanguard-gui/README.md.
       - Do not “fix” the Class-extends-undefined error by deleting node_modules without a lockfile.
       - npm run typecheck && npm run dev must start Vite. If Tauri CLI is not installed, Vite-only is acceptable
         for this sprint *provided* native slots degrade to not_available (see PTY).

    1. Slot architecture (keep registry)
       SlotId remains a discriminated union. Each slot is a module under vanguard-gui/src/slots/{files,editor,terminal,run}/.
       Host (dock + activity bar) stays in src/shell/. Theme tokens: accent, warning, danger, muted (names shared with TUI).
       Replay run slot stays wired to @vanguard/client-core. Never reimplement reduceRunView in React.

    2. FE-3-3 Files + Monaco
       Bind, don’t vendor:
       - Tree: virtualized list (react-arborist or a windowed <ul>). Ignore .git and node_modules.
       - Workspace root: user-picked directory. In Tauri: fs walk via a Rust command. In Vite-dev without Tauri:
         a clearly labelled browser stub (source: mock) using a tiny fixture tree — not a fake “live workspace”.
       - Open file → @monaco-editor/react model, UTF-8. On tab close, dispose the Monaco model (leak = fail).
       - Do not walk vanguard/packages/ for “manifest discovery” (J3).
       - LSP language servers = Phase 4. Use Monaco TextMate/Monarch tokenization only.
       DoD: click a file, see its bytes in Monaco.

    3. FE-3-4 xterm + PTY
       - Render @xterm/xterm in the terminal slot. Fit addon on container resize. Dispose on unmount.
       - Native PTY: Tauri 2 sidecar or portable-pty behind invoke("pty_write"|"pty_resize"). Linux/WSL first (J5 = no Named Pipe).
       - Optional: spawn `vg` inside the PTY (this IS TUI-in-GUI). Never import Ink into the React bundle.
       - If the environment cannot open a PTY (plain Vite in CI): slot shows not_available and the reason string.
         A CSS fake `$ _` that looks like a live shell is a spec violation.

    4. Performance / CT
       - Virtualize the file tree and the run transcript. Core live adapter already rings 10k events; UI windows.
       - Parse at the client-core boundary only. GUI does not JSON.parse envelopes by hand.
       - Optimistic UI: command receipts are requested until ApprovalResolved / EpisodeCompleted (Wave 3 approve slot).

    OUT OF SCOPE THIS SPRINT (Wave 3):
    - Real @xyflow/react bind (FE-3-5) — keep placeholder unless toTraceGraph is already exported and time remains
    - Monaco diff + OperatorSigner (FE-3-6)
    - cmdk palette + git status -sb (FE-3-7)
    - Live UDS (Wave 4). Replay remains the default data plane.

    DoD:
    - cd vanguard-gui && npm install --workspaces=false && npm run typecheck && npm run dev
    - Files: open at least one real or mock-labelled file into Monaco
    - Terminal: interactive PTY OR honest not_available
    - Run slot still shows source: mock on the Wave 1 fixture
    - No imports of vanguard/packages, no Ink, no .vsix
```
