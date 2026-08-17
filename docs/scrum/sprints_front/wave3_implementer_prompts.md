# Wave 3 — three parallel implementer prompts (SOTA TUI + IDE slots)

Status: `BINDING for Wave 3`  
Board: `docs/scrum/roadmap_frontend.md`  
Law: `docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md`

Wave 2 close (do not redo):
- FE-1-5…1-8 `[DONE]` (`selectStatusBar`, `windowTranscript`, `toTraceGraph`, `subscribeRun`; core 16/16; CLI 46/46)
- FE-2-8 chrome landed in `cli/src/tui/**` (consume core selectors this wave)
- FE-3 files/Monaco/PTY slots exist; **Vite still blocked** by host npm (`minizlib` / `Class extends value undefined`)

This is **not** a VS Code fork and **not** Cursor. Target: Claude-class TUI operator loop + a slot IDE (files, editor, term, git, palette, diff-approve, VG-04 canvas) on **one** `@vanguard/client-core` and **vg.4 only**. Live spawn remains Joint **J1**. LSP = Phase 4.

Paste **one** prompt per lane. Each prompt has **two sprint blocks**. Do not wait on sibling lanes except types already on the barrel.

---

## Prompt FE-1 — Core live/resume/why SDK

```text
│ Goal: Finish the headless SDK so both skins can resume durable runs, project Why,
│       and attach to a live UDS without inventing verbs. Wave 2 selectors/graph/subscribe
│       stay; this wave adds session/resume/why application helpers + live connect honesty.

    You are Developer FE-1 (Client Core). Implement Lane FE-1 Wave 3 only.

    LAW & SCOPE:
    - Binding Law: docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md (D1–D6, J1–J5)
    - Architecture: docs/scrum/development_guides/cli_tui_architecture.md
    - Playbook: docs/scrum/development_guides/frontend_implementer_playbook.md
    - Wire: docs/front_v4/003_wire_consumer.md + VG-04 §0, §12.2, §15; ADR-0062
    - Write Scope: vanguard/clients/client-core/**
    - CLI shims: import-path-only if a new export is required
    - MUST NOT EDIT: Ink/TUI, vanguard-gui/**, vanguard/packages/**, pack JSON
    - No React, Ink, Monaco, xyflow, Tauri in this package

    WAVE 2 GROUND TRUTH:
    - Barrel already exports selectStatusBar, windowTranscript, toTraceGraph, subscribeRun.
    - OperatorSigner RFC 8785; LiveRuntimeClient reconnect/afterSeq exists.
    - DoD last close: core 16/16; CLI 46/46 via file:../client-core. Do not regress.

    HONEST PRODUCT LIMIT:
    - You cannot spawn the daemon (J1). getDaemonStatus / manageDaemon remain connect-or-fail.
    - You cannot add Ping, ListManifests, Named Pipe (J2/J3/J5).
    - Empty approval digests remain fail-closed (J4).

    ═══════════════
    SPRINT BLOCK A — Resume + Why application (FE-1-9, FE-1-10)
    ═══════════════

    Task A1 — resumeRun contract (already in commands.ts) is the headless path.
    Subtasks:
      - Export a typed helper `buildResumeRequest(runId, checkpointId?: string): ResumeRunRequest`
        that refuses empty runId (`invalid_request`).
      - Add `describeResumeFailure(result: Result<RunRef>)` that maps `not_available` /
        `not_found` / `permission_denied` to stable messages skins can print verbatim.
        Do not invent “resumed locally”.
      - Tests: empty runId; passthrough of not_available; no thrown errors.

    Task A2 — Why / explainArtifact projection
    Subtasks:
      - Export `formatExplanation(explanation: ArtifactExplanation): { status; prediction; empty: boolean }`
        where empty === (status==="unknown" && activatedBy.length===0 && demotedBy.length===0).
      - Export `whyFromResult(result: Result<ArtifactExplanation>)`:
        if !ok, return { ok:false, code: result.error.code, message: result.error.message } — never
        synthesize ActivationChanged.
      - Golden: ReplayRuntimeClient.fromFile(cli fixtures/sessions/why-typed-tools.jsonl)
        yields status active with non-empty activatedBy; missing artifact → unknown, empty true.

    Task A3 — Session snapshot for skins (Cursor-like “current run” without a second store)
    Subtasks:
      - Export `selectSessionChrome({ view, source, lastSeq, runId, daemon? })` combining
        selectStatusBar + runId + daemon status code (`running` | `not_available` | `unknown`).
      - Daemon field is optional; default unknown. Never invent version strings (Wave 1 rule).

    DoD A: cd vanguard/clients/client-core && npm run typecheck && npm test
           CLI suite still green.

    ═══════════════
    SPRINT BLOCK B — Live attach helper (FE-1-11) + API docs in README
    ═══════════════

    Task B1 — `attachLive(options)` factory
    Subtasks:
      - Export `attachLive(opts: { socketPath?: string; signer?: OperatorSigner; manifest?: string; repo?: string }): RuntimeClient`
        that constructs LiveRuntimeClient (no stdin feed) with OperatorSigner.loadOrCreate() if signer omitted.
      - Socket resolution stays inside existing resolveSocketPath (--socket / env / /tmp/vanguard-runtime.sock).
      - `attachLive` must NOT start a child process. If connect fails, methods return not_available.

    Task B2 — AfterSeq resume of the *stream* (not episode resume)
    Subtasks:
      - Document in README: stream reconnect uses EventCursor.afterSeq (already in LiveRuntimeClient).
      - Test with a fake transport or existing transport.test patterns if they live in CLI — prefer a
        core unit test with a FeedTransport JSONL that drops mid-seq; do not require a real UDS.

    Task B3 — README SDK surface
    Subtasks:
      - vanguard/clients/client-core/README.md: table of barrel exports (RuntimeClient, reduceRunView,
        selectStatusBar, windowTranscript, toTraceGraph, subscribeRun, attachLive, whyFromResult,
        OperatorSigner). One paragraph: skins never import vanguard/packages.

    DoD B: core tests green; README lists attachLive; grep still shows no react/ink/xyflow/monaco in src/.
    Mark FE-1-9…1-11 [DONE] on the board only if green.
```

---

## Prompt FE-2 — SOTA TUI operator loop (Claude-class)

```text
│ Goal: Make `vg` feel like Claude Code / Codex CLI for the Vanguard loop:
│       consume Wave 2 core selectors + subscribeRun; finish resume + why chrome;
│       live attach is honest (source: live vs source: mock). FE-2-9 is this wave.

    You are Developer FE-2 (TUI Product Lead). Implement Lane FE-2 Wave 3 only.

    LAW & SCOPE:
    - Binding Law: docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md
    - Surface: docs/scrum/development_guides/tui_product_surface.md
    - Harvest atoms: features_to_add_v430.md §1–2 (permission copy, Esc interrupt, short status,
      resume session *idea* — ledger is session, not Pi JSONL)
    - Kit leftover: docs/scrum/sprints_front/lane_tui_wave2.md (chrome exists; this wave consumes core)
    - Board: docs/scrum/roadmap_frontend.md §5.3 FE-2-8 polish + FE-2-9
    - Write Scope: vanguard/clients/cli/** (tui, composition, headless, test, install.sh)
    - MUST NOT EDIT: client-core internals (import paths OK), vanguard-gui/**, vanguard/packages/**

    WAVE 2 GROUND TRUTH:
    - Hexagonal Ink layout, focus machine (prompt|approval|correct|help|run), y/n/c + OperatorSigner,
      demo/headless/J1 honesty, local windowTranscript in src/tui/transcript-window.ts.
    - Core now has selectStatusBar, windowTranscript, subscribeRun — DELETE local duplicates if
      signatures match; wrap if height/cursor semantics differ (prefer core).
    - Last reported CLI tests: 46/46. Do not regress --help, --demo source:mock, headless JSONL.

    ═══════════════
    SPRINT BLOCK A — Bind core SDK into chrome (FE-2-8 close)
    ═══════════════

    Task A1 — Status + transcript from core
    Subtasks:
      - StatusBar uses selectStatusBar({ view, source, lastSeq, lastKind }) then formatStatusBar
        (keep `source: mock` mapping in sourceLabel for replay).
      - Transcript pane uses core windowTranscript; delete or re-export cli/src/tui/transcript-window.ts
        as a thin wrapper so ui.test.ts clamp tests still pass (same 16-row default, cursor clamp).
      - useVanguardRun: one stream owner via subscribeRun(client, cursor, handlers, signal) instead of
        a raw for-await. Abort on unmount.

    Task A2 — Cursor-like density (still Pi-length chrome)
    Subtasks:
      - Status bits as two lights in copy only: `policy: daemon` and `sandbox: daemon` (display strings;
        do not invent health RPCs). Never green “live” when source is mock/replay.
      - Help `?` lists resume: `vg run --resume <run-id>` and in-TUI key `r` (Block B).
      - Width < 80 still stacks transcript above detail.

    Task A3 — Tests
    Subtasks:
      - ui.test.ts: windowTranscript import still clamps 100→16; prompt-mode y does not approve;
        subscribe abort does not throw (fake client).
    DoD A: npm run typecheck && npm test; vg --help flags unchanged.

    ═══════════════
    SPRINT BLOCK B — Resume + Why (FE-2-9, FE-2-why)
    ═══════════════

    Task B1 — Resume UX
    Subtasks:
      - Headless already has resumeRun in core commands. Wire `vg resume <run-id>` (exists) and TUI:
        key `r` in mode===run opens a resume buffer (run id) or uses --resume / parsed.resumeFrom.
      - On Result.ok===false, render error.code + error.message verbatim (not_available is success
        of honesty). Do not replay a fixture and call it resume.
      - After requestResume ok, streamEvents on the returned runId (subscribeRun). Optimistic UI:
        status `requested` until EpisodeStarted / RunRecovered / error.

    Task B2 — Why
    Subtasks:
      - Key `w` already calls explainArtifact. Pipe through whyFromResult if FE-1-10 exported;
        else keep Result.ok===false → print code only.
      - Headless `vg why <artifact>` already exists; keep JSONL; no CSI.
      - Fixture: --demo why-typed-tools still works.

    Task B3 — Live vs mock composition
    Subtasks:
      - If --demo/--replay/--scenario: never call attachLive.
      - Else TUI may use LiveRuntimeClient as today OR attachLive from core if exported.
      - Connection badge / status: source from StreamItem.source only.

    DoD B:
      - cd vanguard/clients/cli && npm run typecheck && npm test
      - ui.test.ts: resume with fake client returning not_available does not start a mock stream
      - vg run --demo --headless still source:mock
      - vg resume without daemon: exit 2, JSON has not_available
```

---

## Prompt FE-3 — Slot IDE (VS Code/Cursor atoms, not a fork)

```text
│ Goal: Make vanguard-gui a basic coding workbench: activity-bar + editor group + panel,
│       real xyflow from toTraceGraph, Monaco diff + OperatorSigner, command palette + git
│       display. Unblock npm/Vite. Still not LSP, not a VS Code extension, not Cursor cloud.

    You are Developer FE-3 (GUI Shell). Implement Lane FE-3 Wave 3 only.

    LAW & SCOPE:
    - Binding Law: D3 standalone GUI; extension VOID; Code-OSS fork out of scope
    - Slots: docs/scrum/development_guides/gui_ide_slots.md
    - ADR: vanguard-gui/docs/ADR-FE-GUI-001.md (Tauri 2 + React + TS)
    - Playbook §6: bind libraries (Monaco, xterm, cmdk, xyflow, git CLI) — do not vendor workbench.git
    - Board: FE-3-0, FE-3-5, FE-3-6, FE-3-7 (files/Monaco/PTY claimed in Wave 2; keep them)
    - Write Scope: vanguard-gui/**
    - MUST NOT EDIT: cli internals, client-core internals (import paths OK), vanguard/packages/**
    - Forbidden: Ink-in-DOM, second agent loop, xyflow-as-workflow-engine, competitor submodules,
      walking vanguard/packages for manifests (J3)

    WAVE 2 GROUND TRUTH:
    - Slots: src/slots/files.tsx, editor.tsx, terminal.tsx; replay via ReplayRuntimeClient + reduceRunView;
      Monaco dispose; terminal not_available in browser Vite; approve switch-case fixed.
    - npm install failed on this host: `Class extends value undefined is not a constructor or null`
      inside npm’s minizlib. You MUST leave a reproducible install path (lockfile + engines + README)
      even if CI/host npm is broken: document Node 20+, `npm install --workspaces=false`, and a
      fallback (`corepack pnpm` or `npx --yes pnpm@9`) that actually installs vite.
    - toTraceGraph and OperatorSigner now exist on @vanguard/client-core.

    ═══════════════
    SPRINT BLOCK A — Toolchain + VS Code-shaped shell (FE-3-0, workbench)
    ═══════════════

    Task A1 — Install that works
    Subtasks:
      - package.json engines.node >= 20. Pin vite, @vitejs/plugin-react, typescript in lockfile.
      - README: exact commands; note parent npm workspaces; --workspaces=false.
      - If npm is corrupt: add packageManager field (corepack) OR pnpm-lock.yaml *in addition to*
        documenting npm — do not leave “cannot npm install” as the only story.
      - DoD: on a clean Node 20: install + `npm run typecheck`. `npm run dev` starts Vite OR
        the README states the single remaining host bug with a workaround that you verified.

    Task A2 — Workbench chrome (Cursor/VS Code atoms)
    Subtasks:
      - Layout: activity bar (slot icons) | primary (files + editor tabs) | side (run/approve/why) |
        bottom panel (terminal + git). CSS grid/flex; no seven empty dashboards.
      - Theme tokens: accent, warning, danger, muted (match TUI names). source: mock badge on replay.
      - Do not put unbounded EventEnvelope[] in React state; keep a window (Wave 2 100-cap) or
        windowTranscript from core for the run slot.

    Task A3 — Files/editor/term regression
    Subtasks:
      - Opening a mock-labelled file still fills Monaco; models disposed on tab close.
      - Terminal: PTY when Tauri; else not_available text (no fake `$ _`).

    DoD A: typecheck green; README install; workbench layout in src/shell/.

    ═══════════════
    SPRINT BLOCK B — Canvas, Approve, Palette, Git (FE-3-5…3-7)
    ═══════════════

    Task B1 — FE-3-5 xyflow event view
    Subtasks:
      - Slot trace-canvas: @xyflow/react nodes/edges = toTraceGraph(envelopes) mapped to xyflow types.
      - Nodes are VG-04 payload.kind only. Click → payload JSON in a detail drawer. No dispatch,
        no DAG execution, no MCP.
      - Same replay stream as the run slot. Fixture: successful-episode.jsonl and
        approval-pending-resolved.jsonl if present under cli/fixtures/sessions/.

    Task B2 — FE-3-6 Monaco Diff + signer
    Subtasks:
      - On ApprovalRequested (from reduceRunView.pendingApproval): Monaco DiffEditor original vs
        modified from unifiedDiff (parse +/- hunks conservatively; if unparseable, show unified
        text, still require explicit Approve/Reject).
      - Approve/Reject call RuntimeClient.resolveApproval. Use OperatorSigner only when
        argsDigest, descriptorDigest, expiresAt are non-empty; otherwise disable buttons and show
        Joint J4 / not_available — never ok:true with empty signatures.
      - Optimistic: button state `requested` until ApprovalResolved.

    Task B3 — FE-3-7 Palette + git display
    Subtasks:
      - cmdk (or equivalent) palette: ≥3 actions — Focus Files, Focus Terminal, Start replay run,
        Cancel run (requestCancel), Focus Approve. Actions call RuntimeClient or slot focus only.
      - Git: spawn `git status -sb` and `git branch --show-current` via Tauri command when native;
        in Vite-browser show not_available. Display branch in the status bar. Ledger remains authority
        (no shadow-git).

    Task B4 — Why slot (thin)
    Subtasks:
      - why slot calls explainArtifact; render Result error.code if !ok. No fiction.

    DoD B:
      - cd vanguard-gui && npm run typecheck
      - npm run dev if install works
      - Replay: source: mock visible; canvas nodes === envelope count for successful-episode
      - Approve slot: empty digest cannot succeed
      - Palette opens with ≥3 actions; git branch or honest not_available
```
