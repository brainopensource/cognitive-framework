SOTA Coding-Agent TUI for AETHER

Context

AETHER already has a working agent substrate and a working terminal client — they are just barely connected to each other.

The backend is real: 32 agent manifests in vanguard/packages/agency/manifests/registry.json (including vg-code-max, vg-code-chimera, vg-1-forge-v2 — the agents you named all exist), a 13-stage kernel dispatch with cryptographic Ed25519 approvals, an event-sourced SQLite-WAL ledger with cold replay and resume, tier-escalating model routing, and a UDS daemon (vanguard-daemon) speaking NDJSON command frames with live event streaming.

The frontend does not reach any of it. There are two competing TUI codebases — vanguard/clients/tui (hand-rolled cell renderer, ~2.2k LOC) and vanguard/clients/cli/src/tui (Ink + React, 17 components) — with duplicated palettes, themes, and stores. Neither exposes the agent registry, neither reads the model registry, neither has plan mode, and the one slash-command implementation that exists (tui/src/store.ts:301-383) is half-wired: the palette entries in app.ts:123-127 have empty action: () => {} closures and their indices disagree with keyboard.ts:352-359, so picking "cancel" from the palette actually fires "history".

Meanwhile FrontendAppController (vanguard/clients/client/src/application/app-controller.ts, ~1150 lines) is already a complete headless application layer — conversations, providers, credentials, approvals, resume, attach, grouped history — and the TUI uses maybe a fifth of it.

The outcome: one terminal client, aether, that you can drop into any repo and drive a real coding challenge through vg-code-max / chimera / forge, with the interaction grammar of opencode and Hermes and a governance model neither of them has.

Sources studied

- opencode TUI, agents, keybinds — ctrl+x leader grammar, Tab-to-cycle primarmission distinction (allow/ask/deny per tool), @file fuzzy refs, !shell,git-backed /undo.
- Hermes Agent CLI — /context glyph-grid usage breakdown, /status, /usage, br / interrupt), Ctrl+G open composer in $EDITOR, Ctrl+S stash draft, zero-cost ! shell mode, SQLite session resume by id/title/latest.

We take both and add what neither has: capability-enforced plan mode and signed approvals, because AETHER's kernel already enforces them.

---

Decisions taken

┌────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│    Question    │                                                   Decisio                        │
├────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Render stack   │ OpenTUI + SolidJS, per PRD_AETHER_TUI.md §2. Gated on the qualification spike the PRD itself requires (§8.1). │
├────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ Agent catalog  │ Discovered from manifests — registry.json + each manifest                        │
├────────────────┼──────────────────────────────────────────────────────────────────────────────────┤
│ /login /logout │ Print browser URL + persist real session state via the exetwork.                 │
├────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Plan mode      │ Enforced at the harness via a read-only execution profile                        │
└────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

Two constraints you should know before we start

1. OpenTUI needs Bun. @opentui/core requires Bun ≥1.3 or Node ≥26.4 with --ehrough a native Zig core over FFI. This machine has Bun 1.4.0 but Node 24.20, so
   Node cannot run it — the TUI becomes a Bun program. The end-user story st-compile produces a standalone binary with the runtime embedded, which is what
   PRD_AETHER_CLI.md §2 already targets. But it does mean OpenTUI is a nativTS convention is "zero runtime deps outside Node stdlib". W0 exists to prove it
   holds up before we commit.
2. This work is not currently authorized. docs/SPEC.md TC-E-047 puts packaged CLI/TUI in M-9, which is UNAUTHORIZED (blocked on M-8), and both WIP=1 lanes in docs/execution/active.md
   are backend (CMX-09, REL-01R). Per docs/execution/backlog.md §2.9 this nefinition-of-Ready fields and lane authorization. W6 does that paperwork; youneed to authorize the lane before W1 lands.

---

Architecture: split the core from the renderer

The single most important structural move. Everything that is not drawing goes into a new headless package:

vanguard/clients/tui-core/     NEW — @aether/tui-core, zero deps, pure TS
  src/commands/                slash command registry + handlers
  src/catalog/agents.ts        manifest registry discovery
  src/catalog/models.ts        models_registry.json reader
  src/session/                 session model, resume, transcript folding
  src/auth/                    mocked login/logout over the persistence port
  src/keymap/                  leader-key grammar, mode machine
  src/plan-mode.ts             read-only profile selection

vanguard/clients/tui/          REWRITTEN — @aether/tui, OpenTUI + Solid view

Why: the OpenTUI bet is real but contained. Every behaviour worth testing — command parsing, catalog discovery, plan-mode profile selection, resume, key grammar — lives in tui-core and
is unit-testable with node --test and no terminal, per the repo's hermetic-tification, we swap the view layer back to the existing cell renderer and lose
nothing above the driver line.

tui-core consumes FrontendAppController from @aether/client rather than reimport kernel, agency, ports, or adapters (vanguard/clients/README.md).

---

W0 — OpenTUI qualification spike

The gate PRD_AETHER_TUI.md §8.1 requires before Ink deletion. Build a throwa streams 10k synthetic tokens into a scrolling transcript with a live status
footer, and measure it against the PRD §9 budgets.

- Terminals: the local emulator, tmux, and an SSH session. macOS/Windows Terminal are out of scope here — record them as unqualified rather than claiming them.
- Color: 24-bit, 256-color, and 16-color ANSI fallback.
- Resilience: SIGWINCH resize storms, wide CJK glyphs, combining characters, multi-line paste.
- Budgets: first frame <40 ms, keystroke→cell <12 ms P95, event→cell <50 ms P95, resize reflow <16 ms, RSS <45 MB.

Exit criterion: all three terminals green on all three color modes, or we faerminal/screen.ts driver and record the failure. Do not skip this — it is the
one step that makes the stack choice reversible.

Deliverable: a receipt with real measured numbers. No claim of PASS for an uest status reporting).

---

W1 — @aether/tui-core

Command registry

One typed registry replacing the switch in store.ts:306 and the two disagreeand declares name, aliases, description, argHint, mode (available in plan
mode?), and run(ctx, args). The palette, /help, and tab-completion all rendetructurally kills the index-mismatch bug.

The seven you asked for:

┌─────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Command │
│
├─────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
┤
│         │ Picker over vanguard/packages/adapters/models/models_registry.js of truth; hardcoding model names fails closed with ModelPolicyError. Groups by│
│ /model  │  tier, marks free vs paid, warns when VANGUARD_ALLOW_PAID is unsker; /model <id> sets directly and validates against the registry (today it│
│         │ accepts any string).
│
├─────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
┤
│ /plan   │ Toggles plan mode. See W3.│
├─────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
┤
│ /exit   │ Cancels any live run, flushes conversation state through NodeFsPhe terminal, exits 0. Aliases /quit, /q.
│
├─────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ /resume │ Picker merging client.listRuns() (daemon-side runs) with persistay / Yesterday / Last 7 Days via the existing groupSessionsByDate(). Selecting│
│         │ one calls controller.attachRun(runId), replays the ledger from st, and continues in place. /resume latest skips the picker.
│
├─────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
┤
│ /agents │ Picker over the manifest registry (below). Selection sets manifeAlias /agent.│
├─────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
┤
│ /login  │ Prints Open https://auth.aether.dev/device?code=XXXX-XXXX in yous session.json (account, expiry, fake token) through the persistence port.
│
│         │ Header then shows the account.│
├─────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
┤
│ /logout │ Clears session.json, header reverts to anonymous.
│
└─────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

The rest of the SOTA set, because "the usual way of using it" is most of the

- Core — /help (?), /new, /clear, /init
- Session — /sessions, /title <name>, /status, /context, /cost, /compact, /e
- Repo — @path fuzzy file reference inlined into the prompt; !cmd shell mode that runs locally and adds output as context without invoking the model (Hermes's zero-cost trick)
- Runtime — /doctor, /runtime, /workspace, /provider, /approve, /diff, /undose

Agent catalog — src/catalog/agents.ts

Read registry.json, then each <name>/manifest.json for its components, capabsolve the manifests dir from VANGUARD_ROOT / AETHER_REPO_ROOT, falling back towalking up for .vanguard/workspace.toml.

The picker shows name, role from the registry, the capability verbs (fs.read, patch.apply, proc.exec, agent.spawn), and the budget ceiling — so it is visible at a glance that
vg-code-explain cannot write and vg-code-max can. vg-code-max, vg-code-chimefor free, no new manifests needed.

This replaces the fictional DEFAULT_AGENTS in app-controller.ts:131 (keep thwhen no repo root resolves).

Auth — src/auth/

Extend FrontendPersistencePort (client/src/persistence/persistence-port.ts) ts own rather than inventing storage — the port already owns settings.json,providers.json, conversations.json, credentials.json under XDG_CONFIG_HOME.

Keep it out of credentials.json. That file is the real-secret store, written at mode 0o600 behind a dedicated setCredential/getCredential/deleteCredential API (persistence-port.ts:317-336) and holding live provider keys. A mocked login token has no business in it — mixing a fake credential into the real credential store is how a fake later
gets treated as real. session.json holds only {account, displayName, issuedAritten at 0o600 for consistency.

Make the mock token unmistakably fake. tools/linters/scan_secrets.py matchesKIA[0-9A-Z]{16}, PEM private-key blocks, and OPENROUTER_API_KEY=sk-…/or-…
assignments. Runtime state lands in XDG_CONFIG_HOME, outside the scanned treests, and docs examples live in the repo and are scanned. So the mock token is a fixed, obviously-synthetic literal such as aether-mock-session-000000000000 — no sk-/or-/AKIA prefix, no base64-looking entropy, no PEM framing. Assert this in a tui-core unit test so
a future edit cannot quietly make the fixture look like a real key.

/logout deletes session.json outright rather than blanking fields, so there is no stale token at rest.

---

W2 — OpenTUI + Solid render layer

Rewrite vanguard/clients/tui/src/ as Solid components over @opentui/solid, fd §4 layout: header bar, virtualized transcript, conditional governance deck,composer, status footer.

Port rather than rewrite where the existing code is already good: theme.ts (semantic tokens + color-mode detection), terminal/cell.ts (grapheme width handling), and the pure
text-formatting halves of components/cards/*. The parts that go away are terinput.ts — OpenTUI's Zig core owns the cell buffer and key events now.

Key grammar — opencode's leader convention, so muscle memory transfers:

┌────────────────────────────────┬──────────────────────────────────────────
│            Binding             │                           Action                            │
├────────────────────────────────┼──────────────────────────────────────────
│ ctrl+x                         │ Leader (2s timeout)                                         │
├────────────────────────────────┼──────────────────────────────────────────
│ <leader> n / l / m / a / e / t │ new session / sessions / models / agents / $EDITOR / themes │
├────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ ctrl+p                         │ Command palette
├────────────────────────────────┼──────────────────────────────────────────
│ Tab                            │ Cycle primary agent
├────────────────────────────────┼──────────────────────────────────────────
│ Shift+Tab                      │ Cycle focus region                                          │
├────────────────────────────────┼──────────────────────────────────────────
│ Enter / Shift+Enter            │ Submit / newline                                            │
├────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ ctrl+c                         │ Interrupt run; double-press exits
├────────────────────────────────┼──────────────────────────────────────────
│ ctrl+d                         │ Exit
├────────────────────────────────┼──────────────────────────────────────────
│ ctrl+g                         │ Open composer buffer in $EDITOR                             │
├────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ ctrl+s                         │ Stash draft, press again to restore                         │
├────────────────────────────────┼──────────────────────────────────────────
│ y / n / d                      │ Approval deck: sign / reject / view diff                    │
├────────────────────────────────┼──────────────────────────────────────────
│ Esc                            │ Close modal                                                 │
└────────────────────────────────┴──────────────────────────────────────────

Status footer, merging the PRD's metrics with Hermes's context bar: model · text-usage bar colored green <50% / yellow <80% / orange <95% / red ≥95% · cost· seq · latency · PLAN badge when active.

Accessibility (PRD_AETHER_TUI.md §8.2, non-negotiable): every state carries a textual cue ([OK], [FAIL], [HOLD]) alongside color; focus regions use inverse-video borders; --no-animation
replaces spinners with static progress.

---

W3 — Plan mode, enforced by grant attenuation

Client-side politeness is not enforcement. Plan mode withholds the write vernt is never issued the authority in the first place.

The kernel is not touched. vanguard/packages/kernel/ is domain-blind (I-7) and under a hard TCB budget (currently 1386/1438 logical lines, enforced by tools/linters/check_tcb_budget.py,
which measures vanguard/packages/kernel only). Encoding a "plan mode" notionend TCB budget on a product concern and teach the kernel about a domain.Enforcement belongs in the runtime composition layer, which is outside the budget and already owns this decision.

The exact seam is _scope_for(harness) at vanguard/packages/runtime/wiring.pyroot authority as actions=frozenset(harness.verbs) straight from the manifest
ceiling. It is called from exactly one place — session.py:509, self.scope = _for(harness).

1. Add a plan preset to PRESETS in runtime/profiles.py:189 — workspace_acceslt="deny", otherwise mirroring local. ExecutionProfile already carries bothfields; the four existing presets are all workspace-write.
2. Make _scope_for profile-aware — _scope_for(harness, *, workspace_access="-only, subtract the mutating verbs from actions and drop their entries from_ceiling_resources, so the declared ceiling and the granted scope stay consistent. Retained: fs.read, fs.search, fs.list, agent.spawn. Withheld: patch.apply, proc.exec (a shell is a
   write path). Keeping agent.spawn is safe because attenuation is monotonicold authority the parent lacks, so spawned agents inherit the read-only surface.
3. Carry workspace_access on SessionPorts, set from the resolved profile at composition. There is direct precedent one screen away: session.py:667 resolves capture_policy from the profile the same way. Do not thread a new argument through plan_run — RunPlan is a digest/identity record and holds no grant.
4. The TUI sends profileId: "plan" on StartRun. No new wire command needed —ady accepts profileId and contracts/src/types.ts:138 already carries it.
5. Falsifier (the Definition-of-Ready requirement): a test asserting that paan" is denied at S5 with a grant-scope cause, that the denial is recorded in the
   ledger, and that the workspace is byte-identical afterward. A second testds under the same profile — otherwise "read-only" is indistinguishable from
   "broken".

Do not use interactive=False for this. That maps to kernel BENCHMARK mode (Kval closed — it kills reads too, and means something different.

/plan toggles for the next turn and shows a PLAN badge in the header. Compleplain, whose manifest declares no write verbs at all, is plan mode byconstruction.

---

W4 — The coding loop

What makes it usable on a real challenge in a real repo:

- Streaming. Consume RuntimeService.stream_events(run_id) over UDS. Keystrokes preempt stream rendering (PRD §6.1 zero-input-starvation); tokens append to the live turn without
  reflowing history.
- Progressive disclosure. Fold high-volume tool events into one line — ▸ Read 8 files [0.14s] — expandable to paths, sizes, latencies. The card components already exist and just need the OpenTUI view.
- Diffs. 24-bit syntax-highlighted unified diffs; d from the approval deck o
- Approvals. y invokes OperatorSigner, signs the canonical RFC-8785 bytes, dscriptorBoundApprovalPolicy means an approval is bound to the exact descriptor
  digest and cannot be transplanted (K-15).
- Busy-input modes (Hermes) — /busy queue|steer|interrupt controls what a me
- Daemon lifecycle. Use the existing ManagedRuntimeHost in @aether/client so typing aether in a cold repo spawns and supervises vanguard-daemon itself. This is the "just works" piece
  and it is already written.

---

W5 — Packaging and consolidation

- bun build --compile → a standalone aether binary, embedding the Bun runtimor Node (PRD_AETHER_CLI.md §2).
- Delete vanguard/clients/cli/src/tui/ and drop ink + react from @vanguard/cli, leaving the CLI purely headless per its PRD. Remove ink from the root package.json. Also removes
  src/commands/legacy.tsx.
- bin/aether-tui and bin/aether exec the compiled binary; bin/aether with no args on a TTY offers to launch the TUI.

---

W6 — Verification and paperwork

Automated:

npm --workspace @aether/tui-core test     # node --test, hermetic, no terminal
npm run typecheck
just check                                 # boundaries, TCB, domain-blindness, path hygiene, docs
python3 tools/linters/scan_secrets.py      # mock session token must not rea
python3 -m unittest discover -s test/runtime -t .   # the plan-scope falsifi

just check must stay green on check_tcb_budget.py (kernel untouched → the 13e at all) and on check_domain_blindness.py.

Manual end-to-end — the actual acceptance test:

1. cd into a scratch repo that is not this one.
2. aether — daemon auto-spawns, TUI paints.
3. /login → account in header. /agents → pick vg-code-max. /model → pick a tier-1 free model.
4. /plan, then ask for a refactor. Confirm it produces a plan and that git status is clean — this is the falsifier, run it and report the real output.
5. /plan off, same request. Approve the patch with y. Confirm the file chang in the ledger.
6. /exit, relaunch, /resume latest — transcript restored, conversation conti
7. /logout.

Docs. AGENTS.md §7 forbids creating new markdown anywhere under docs/. So: no new files. Edit docs/execution/backlog.md to add the package with Definition-of-Ready fields,
docs/execution/active.md to authorize the lane, and PRD_AETHER_TUI.md §2's Asays React+Ink, which is stale for @aether/tui). Then just docs-knowledge.

---

Critical files

┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    Path                                   ange                         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ vanguard/clients/tui-core/**                                                │ New headless package                                  │
├─────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ vanguard/clients/tui/src/**                                                 │ Rewritten on OpenTUI + Solid                          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ vanguard/clients/cli/src/tui/**                                           d                            │
├─────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ vanguard/clients/client/src/application/app-controller.ts:131             y fallback                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ vanguard/clients/client/src/persistence/persistence-port.ts                 │ Add session.json slot, separate from credentials.json │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ vanguard/packages/runtime/profiles.py:189                                   │ Add plan preset                                       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ vanguard/packages/runtime/wiring.py:455                                   ions under read-only         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ vanguard/packages/runtime/session.py:509                                  m the resolved profile       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ vanguard/packages/kernel/**                                                 │ Untouched — I-7 domain-blindness, TCB budget          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ bin/aether, bin/aether-tui, package.json                                    │ Compiled-binary launch                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ docs/execution/{active,backlog}.md, docs/product/frontend/PRD_AETHER_TUI.md │ Edit in place, no new files                           │
└─────────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────┘

Reused, not rebuilt

- FrontendAppController — conversations, approvals, resume, attach, provider
- ManagedRuntimeHost — daemon supervision
- NodeFsPersistenceAdapter — all local state
- @aether/projections — pure event folds (run-snapshot, conversation, approval-state, trace-graph)
- groupSessionsByDate() in desktop/src/state/session-history.ts — session gr
- theme.ts, terminal/cell.ts, components/cards/* from the current TUI

Sequencing

W0 gates W2. W1 is independent and can start immediately. W3's backend half  is independent of the whole frontend and is the highest-value single change inthe plan./