# Full Plan (Archived): Backend/Frontend Integration, Test Buildout, and Build/Ship/Distribute for AETHER Clients

> Status: **Archived for future sprint authorization.** Drafted 2026-08-31 during a planning session. Only Phase 0 and Phase 1 (F0 wire contract freeze + F1 single causal event ledger) were authorized for immediate execution — see `.claude/plans/scalable-nibbling-graham.md` for that scoped slice. Everything else below (F2–F8, test buildout, build/ship/distribute) is deferred pending future authorization.

## Context

The studio client just got its Agent Studio manifest-compiler upgrade (agent-definition.ts, done). The user wants the full remaining arc:
1. more test coverage,
2. real backend integration (live agent runs, event streaming, approvals, manifest/workflow creation — a Claude-Code-CLI-like or Hermes-desktop-like experience),
3. backend improvements needed to support that,
4. a real build/ship/distribution pipeline for the CLI, TUI, and desktop app.

Investigation found this is **not greenfield**. The backend already has a working `RuntimeService` (`vanguard/packages/runtime/service/service.py`), a UDS NDJSON daemon (`service/server.py`), and an HTTP+SSE gateway (`runtime/service/studio_gateway.py`) built on a real event-sourced ledger (`domain/ledger/events.py`, hash-chained `EventEnvelope`s, `mhf.event/2`). There's a pre-existing 1108-line design dossier at `docs/research/frontend/integration_plan.md` (status: historical-reference, last verified 2026-08-27/29) that already specifies the target architecture, wire contracts, a 45-route API catalog, and an **8-phase roadmap F0–F8**. This plan adopts F0–F8 as the backbone, converges the frontend on the `@aether/*` stack (retiring `@vanguard/client-core`'s role over time), and adds a real Tauri shell for desktop plus the build/ship pipeline the dossier doesn't cover.

Key architectural rules to respect throughout (from the dossier, confirmed in code):
- **One write path, many read paths**: all commands go through `RuntimeService.execute_command`; HTTP and UDS are both thin transports over the same command vocabulary. Never let a client mutate state directly.
- **Compositions/manifests are immutable and digest-addressed** — no in-place YAML editing. Manifest "editing" UI must be validate → plan-activation → activate, matching `/api/v1/compositions:validate|:plan-activation|:activate` in the dossier's §9.2.
- **Event envelopes are hash-chained** (`parent_digest`/`digest`, RFC 8785 JCS) and role-scoped (`PRIVILEGED_KIND_OWNERS` in `domain/ledger/events.py`) — no unmediated writes.
- Backend stays stdlib-only (no FastAPI/Flask) — this is a deliberate TCB-minimization constraint per existing comments in `studio_gateway.py`; don't introduce a web framework dependency there.

---

## Phase 0 — Baseline verification (do first, cheap, unblocks everything)

Before trusting the dossier's Aug-27 "verified baseline," re-check against current code, since docs are already a few days stale relative to `last_verified: 2026-08-29`:

- Run existing test suites: `test/runtime/test_studio_gateway.py`, `test/contracts/test_runtime_service_*`, plus `npm run test` across `vanguard/clients/*` workspaces (`cli`, `client-core`, `client`, `contracts`, `studio`, `tui`, `desktop`, `lab`, `ui-web`, `projections`).
- Confirm whether `studio_gateway.py`'s `_pilot_run_simulation()` is still emitting synthetic events (dossier flags this as a correctness bug: it produces a second, non-canonical event history alongside `SqliteEventStore.events`).
- Confirm current route coverage of `studio_gateway.py` against the dossier's 45-route catalog (§9) to get an accurate "done vs. missing" delta — don't assume the dossier's numbers are current.
- Check `client-core/src/adapters/http/HttpRuntimeClient` (per dossier: "implements only a subset of `RuntimeClient`, returns placeholders for run snapshots") and Studio's `browser-entry.tsx` (per dossier: "bypasses `@vanguard/client-core` for health/SSE/approval calls with duplicated ad hoc fetch/EventSource code") — confirm both are still true.

Output of this phase: an updated gap list that supersedes the dossier's §1 "verified baseline" section, used to calibrate effort in Phases 1–4 below.

---

## Phase 1 — Backend integration hardening (maps to dossier F0–F3, F7)

**F0 — Contract and falsifier freeze**: lock the wire contract (`aether.contracts` schema, `CommandFrame`/`EventFrame`/`ReceiptFrame`, `CanonicalErrorCode`) so client and server can't drift. Concretely: promote/finish `@aether/contracts/src/types.ts` as the single source of truth for wire types (it's already the right home — confirmed low-level event/command types live there, not in `@vanguard/*`). Add contract-conformance tests that fail if `vanguard/packages/runtime/service/contract.py`'s `ERROR_CODES` and `@aether/contracts`'s `CanonicalErrorCode` diverge.

**F1 — RuntimeService over canonical ledger**: fix the dual-event-history bug — remove/replace `_pilot_run_simulation()` synthetic events in `studio_gateway.py`; make `SqliteEventStore.events` (via `EventStorePort`, `adapters/stores/event_store.py`) the single source SSE/UDS/HTTP all read from. This is the highest-priority backend fix — everything downstream (live event viewing, approvals-over-events) depends on one causal truth.

**F2 — UDS daemon and protocol parity**: verify `service/server.py` (UDS NDJSON) and `studio_gateway.py` (HTTP/SSE) expose the same command vocabulary and error codes (per "one write path, many read paths"). Add parity tests that run the same command matrix over both transports and assert identical results.

**F3 — HTTP gateway core**: finish out the remaining routes from the dossier's §9 catalog not yet implemented (confirm exact gaps from Phase 0). Priority order for a CLI/desktop-live experience: Runs (start/cancel/checkpoint/resume/stream — likely mostly done), Approvals (resolve — exists, verify crypto protocol per §7 is wired to real `OperatorSigner`/`WebCryptoSigner` rather than stubbed), Compositions (validate/plan-activation/activate — needed for "creating new agents/manifests" from a UI), Agents (6 routes, §9.3), Artifacts (7 routes, explain endpoint exists — verify rest).

Also close two smaller layering gaps found in exploration:
- No dedicated `ports/approval.py` — approval types live directly in `runtime/governance/approvals.py`. Add a port abstraction so approval flow is pluggable/testable like other ports (`ports/event_store.py` is the existing pattern to follow).
- Workspace file access is ad hoc in `studio_gateway.py` (`WORKSPACE_READ_SUFFIXES`/`DENYLIST` inline) — normalize into a port/adapter if a real file-browsing UI feature (desktop file tree, workspace diff view) is planned, matching the dossier's capability-discovery design in §10.

**F7 — Projection APIs**: build out `runtime/trajectory.py`/`trajectory_reader.py`-backed projection routes (e.g. `/api/v1/runs/{runId}/trajectory`) so clients don't have to re-derive run state from raw events client-side every time — `@aether/projections` (already has `run-snapshot`, `trace-graph`, `evidence-grid`, etc.) should consume these where it makes sense to move logic server-side, but keep pure derivations client-side per architecture (`@aether/projections` is described as "deterministic folds," which is correct to keep client-side for anything not needing server-only data).

---

## Phase 2 — Frontend convergence and live wiring (maps to dossier F4–F6)

**F4 — Client-core convergence**: converge on `@aether/client` + `@aether/contracts` as the canonical SDK.
- Fix Studio's `browser-entry.tsx` to go through `@aether/client`'s `HttpRuntimeClient`/`transports/http.ts` instead of ad hoc fetch/EventSource calls.
- Migrate `cli` off `@vanguard/client-core` onto `@aether/client` — `@aether/client` already has `SocketRuntimeClient` (UDS) and `ManagedRuntimeHost` (spawns/manages the Python daemon as a child process, with `OFFLINE/STARTING/RUNNING/.../CRASHED` states and auto-restart — this is exactly the piece needed for a Claude-Code-CLI-like "just run `aether` and it starts its own backend" UX). Reuse `ManagedRuntimeHost` for `cli`'s daemon lifecycle instead of `cli`'s current separate daemon-management code in `commands/daemon.ts`.
- `client-core`'s `application/coding-commands.ts` direct Python-subprocess-spawn path (`spawn(pythonBin, ["-m", module, "--stdin-json"])`) should be evaluated: either port the pattern into `@aether/client` if still needed, or replace with the UDS/HTTP RuntimeService path now that it's the canonical one-write-path.
- Once migration is stable, mark `@vanguard/client-core` deprecated (don't delete yet — `cli` and any remaining consumers need a clean cutover first); plan its removal as a follow-up once nothing imports it.

**Shared agent/manifest schema** (blocking for "creating new agents, workflows, manifests" across clients): promote `studio/src/agent-definition.ts`'s types (`AgentDefinition`, `AgentManifest`, `CompositionDelta`, `compileManifest`, `generateAaaCSource`, `compositionDigest`, `validateAgentDefinition` — all just built) out of studio-private code into `@aether/contracts` (or a new `@aether/agent-schema` package if contracts should stay purely wire-level — recommend keeping it in `contracts` since it's schema, not transport, and contracts already owns wire schema). Update `cli/src/commands/agent.ts` (which currently has its own implicit shape) and any future `tui`/`desktop` agent-creation UI to consume the shared types instead of re-deriving them.

**F5 — CLI/TUI live vertical slice**: wire `cli` (already has the most complete command surface: `agent`, `approve`, `artifact`, `attach`, `composition`, `event`, `run`, `workflow`, etc., plus an Ink TUI subtree) and the standalone `tui` package (raw terminal renderer, no transport wired yet per exploration) onto the converged `@aether/client`. Decide whether the standalone `@aether/tui` package absorbs/replaces `cli`'s embedded Ink TUI, or whether they stay separate surfaces (`cli` for scripting/one-shot commands, `tui` for the full-screen cockpit) — recommend keeping both but sharing all business logic through `@aether/client` + `@aether/projections`, with `tui` becoming the primary "Claude-Code-CLI-like interactive" surface and `cli` staying the scriptable/composable command entry point.

**F6 — Studio live vertical slice**: with F1's single-event-history fix and F4's client convergence in place, verify Studio's Observatory (causal graph, event forensic inspector, timeline) and Agent Builder wizard work end-to-end against a real running backend, not just against fixtures. Given studio's test coverage is thin (1 test file for a huge UI surface — see Phase 3), this is also where most new integration tests should land.

---

## Phase 3 — Test buildout

Priorities, in order of leverage:
1. **Contract-conformance tests** (Phase 1/F0) — cheapest, highest-value, catches drift early.
2. **Transport parity tests** (Phase 1/F2) — one command matrix run over UDS and HTTP, asserting identical results.
3. **`studio_gateway.py` route tests** for every route in the dossier's §9 catalog, especially the ones newly implemented in Phase 1.
4. **Studio component/integration tests** — biggest gap (1 file for dozens of components). Target the Agent Builder wizard, Observatory event folding (`StudioFoldEngine`/`ColumnarEventStore` — already has some unit coverage, extend it), and Topology Studio's validate/plan-activation/activate flow.
5. **`@aether/contracts` tests** — currently only 1 file for a foundational package; add round-trip tests for every wire type and error code.
6. **`@aether/client`'s `ManagedRuntimeHost`** — test daemon spawn/crash/restart/reconnect state transitions (`OFFLINE→STARTING→RUNNING→CRASHED→...`) since this becomes the backbone of "just launch the app and it works."
7. **Mandatory falsifiers** — the dossier's §13.2 already names required falsifier tests; implement whichever are still missing (confirm in Phase 0).
8. Follow existing test layout conventions: Python tests under `test/runtime/`, `test/contracts/`, etc.; TS tests colocated per-package under `<package>/test/`, using `node --test` (existing pattern, confirmed working from the studio test run).

---

## Phase 4 — Build, ship, and distribute

Current state (confirmed via exploration): only dev-loop tooling exists. `justfile`/`Makefile` have no build/package/publish targets; CI (`ci.yml`, `clean-candidate.yml`) only runs verification gates, produces no artifacts; `install_vanguard.sh` installs only the Python backend into a venv; CLI/TUI are plain `tsc` builds with no bundling; desktop has no Tauri/Electron scaffold at all.

**4a. Python backend (`vanguard-runtime`)**
- Add a `just build-backend` / CI job: `uv build` → produce sdist + wheel from the existing `pyproject.toml` (entry points already correct: `vanguard`, `vanguard-evaluator`, `vanguard-daemon`, `vanguard-studio`, `lda`, `lda-mcp`).
- Add a release workflow (new `.github/workflows/release.yml`) triggered on tag push: build wheel/sdist, run `tools/release_qualification.py` (already exists per justfile's `release-verify`), upload as GitHub Release assets. PyPI publish is optional/deferred — ask before wiring real publish credentials.
- Consider whether `containers/worker.Dockerfile`/`evaluator.Dockerfile` need a corresponding CI build/push job (currently manually-maintained digests in `containers/manifest.json`) — these are internal sandboxes, not release artifacts, so lower priority than a general-purpose "backend server" image if one is wanted for hosted/team deployments later.

**4b. CLI and TUI (`@aether/cli`-or-current-`@vanguard/cli`, `@aether/tui`)**
- Add bundling: use `esbuild` (already a devDependency pattern in `studio/scripts/build-browser.mjs` — reuse that approach) to produce a single-file Node bundle per package, eliminating the `node_modules` runtime dependency that currently blocks standalone distribution.
- Evaluate `bun compile` or Node's built-in single-executable-application (SEA) support for true standalone binaries (no Node runtime required on target machine) — flag as a decision point, don't just pick one without checking current Node/bun version constraints in the repo.
- Update `bin/aether`/`bin/aether-tui` shims (currently assume in-place repo/dist layout) once bundling exists — they should point at the bundled artifact.
- Add `npm publish`-readiness: version bump strategy, `publishConfig`, `prepublishOnly` build step, `files` array audit (currently declared but untested).

**4c. Desktop app**
- Scaffold a real Tauri app: `src-tauri/` with `Cargo.toml` and `tauri.conf.json`, wire the existing `TauriNativeBridge` (`desktop/src/bridge/tauri-bridge.ts`) to real Tauri commands instead of its current browser-fallback stubs.
- Use Tauri's sidecar mechanism to bundle/launch the Python backend (leverages the same daemon-lifecycle logic already built in `@aether/client`'s `ManagedRuntimeHost` — the Rust shell can shell out to it, or `ManagedRuntimeHost` can run inside the Tauri webview's Node-free JS context if Tauri's IPC is used instead — this needs a concrete decision during implementation, not resolved here).
- Add `desktop`'s missing browser-bundling step first (it currently only has `tsc`, unlike `studio`'s `esbuild`-based `build-browser.mjs`) — needed regardless of Tauri, since the Tauri webview needs a bundled JS asset.
- Add `tauri build` to CI for at least one platform (start with Linux, since dev environment is WSL2/Linux) producing an AppImage or `.deb`; expand to macOS/Windows cross-compilation once the pipeline works.

**4d. CI/release orchestration**
- New `.github/workflows/release.yml`: on version tag, build all four artifacts (backend wheel, CLI bundle, TUI bundle, desktop Tauri app) in a matrix, upload to a GitHub Release. Keep existing `ci.yml` verification gates as a required check before any release job runs.
- Add a version-bump/changelog step (decide: manual, `changesets`, or simple script) — not currently specified anywhere in the repo.

---

## Suggested execution order

1. Phase 0 (baseline verification) — half a day, informs everything else.
2. Phase 1/F1 (fix dual event history) — unblocks all live-UI work, do this before anything else backend-side.
3. Phase 1/F0, F2, F3 in parallel with Phase 2/F4 (contract freeze + client convergence can proceed once F1 lands).
4. Phase 2/F5, F6 — wire CLI/TUI/Studio to the now-consistent backend.
5. Phase 3 (tests) — interleave with Phases 1–2 rather than batching at the end; add tests as each route/component is fixed, per existing repo convention (`just verify` gate implies tests are expected alongside code).
6. Phase 4 (build/ship) — start 4a/4b (backend + CLI/TUI bundling) once Phase 2/F5 is stable; start 4c (Tauri) once Phase 2/F6 (studio/desktop UI) is stable enough to be worth packaging.

## Verification

- Each phase should end green against: `just verify` (existing full CI gate wrapper), `npm run typecheck` and `npm test` across all touched workspaces, and Python `uv sync --frozen && python -m unittest` (or whatever `ci.yml`'s `vanguard-living-gates` job runs) for backend changes.
- For live-integration work specifically: the dossier's §14 "Commands and smoke-test runbook" gives concrete manual smoke-test steps — use these to confirm real end-to-end behavior (start daemon, start run, stream events, resolve approval) beyond what unit tests cover.
- For build/ship work: a successful `tauri build` producing an installable artifact, and a CLI/TUI bundle that runs on a machine without the repo's `node_modules` present, are the concrete "done" signals.

## Investigation source material (from the planning session)

Key facts gathered during exploration, retained here for whoever resumes this plan:

- **Backend**: Already has `RuntimeService` (`vanguard/packages/runtime/service/service.py`), UDS daemon (`service/server.py`), HTTP+SSE gateway (`studio_gateway.py`, 721 lines, stdlib-only `http.server`, no FastAPI/Flask by design). Event model: `EventEnvelope` (`mhf.event/2`) in `vanguard/packages/domain/ledger/events.py`, hash-chained via RFC 8785 JCS (`domain/canonicalisation/digest.py`), role-scoped writers (`PRIVILEGED_KIND_OWNERS`, enforced by `runtime/ledger_emitter.py`). Episode engine in `vanguard/packages/agency/episode/engine.py` (observe→propose→authorise→effect→receipt; never self-evaluates or emits kernel-owned events — only `Kernel.dispatch` in `packages/kernel/dispatch.py` does). Manifests: `mhf.manifest/2`, `vanguard/packages/agency/manifests/{loader,validator,discovery}.py`, ~25 existing manifest packs (`vg-code-default`, `vg-code-max-v3`, `vg-chimera-v1`, etc.). Known bug: `studio_gateway.py`'s `_pilot_run_simulation()` emits synthetic events separate from `SqliteEventStore.events` — two event histories, needs unification (this is what Phase 1/F1 of the authorized slice fixes). Legacy/unrelated: `vanguard/packages/runtime/studio/server.py` is an older, simpler static-file server prototype — distinct from and less capable than `studio_gateway.py`, don't confuse the two.
- **Frontend**: Two parallel stacks — `@vanguard/*` (`cli`, `client-core`, mature, UDS-only, v0.4.1-beta) and `@aether/*` (`tui`, `desktop`, `studio`, `lab`, `client`, `contracts`, `projections`, `ui-web`, newer, HTTP/SSE+UDS, all v0.1.0). `studio` straddles both today. `@aether/contracts` only has wire-level types (`EventEnvelope`, `EventCursor`, `CommandFrame`/`ReceiptFrame`/`EventFrame`, `CanonicalErrorCode`) — no agent/manifest types, those live studio-private in `studio/src/agent-definition.ts`. `@aether/client` has `ManagedRuntimeHost` (spawns/manages the Python daemon, state machine `OFFLINE→STARTING→RUNNING→...→CRASHED`, auto-restart) — the key piece for a "just launch and it works" experience. `studio` has the only real browser-bundling pipeline (`scripts/build-browser.mjs`, esbuild) and the richest UI surface (Agent Builder wizard, Observatory, Topology Studio) but thinnest tests (1 file). `lab` has the best test ratio among AETHER apps (11 files) and a solid workbench UI but no browser-bundling step. `desktop` is a plain DOM app with a Tauri-shaped bridge stub (`TauriNativeBridge`) but zero actual Tauri scaffolding (no `src-tauri/`, `Cargo.toml`, `tauri.conf.json`).
- **Build/ship**: `justfile`/`Makefile` have no build/package/publish targets, only dev-loop and cleanup. CI (`ci.yml`, `clean-candidate.yml`) runs verification gates only, produces no artifacts, no Docker build/push, no PyPI/npm publish, no GitHub Release creation. `install_vanguard.sh` builds a Python wheel and installs into a venv with symlinked entry points (`vanguard`, `vanguard-evaluator`, `vanguard-daemon`, `vanguard-studio`) — Python-only, no equivalent for JS clients. `bin/aether`/`bin/aether-tui` are thin Node ESM shims assuming an in-place repo/dist layout. CLI/TUI packages are plain `tsc` builds with no bundler (`pkg`/`nexe`/`bun compile`/`esbuild`) — still depend on `node_modules` at runtime, not portable. `containers/worker.Dockerfile`/`evaluator.Dockerfile` are internal sandboxed-execution images (rootless, UID 10001/10002), not distribution artifacts.
- **Reference docs**: `docs/research/frontend/integration_plan.md` (primary dossier, 1108 lines, historical-reference status), `docs/backend/reference/{events,manifests,ports,api-ports,commands,schemas}.md`, `docs/backend/guides/operate-runtime-service.md`, `docs/backend/architecture/workflows/{event-lifecycle,request-execution,recovery-resume}.md`, `docs/product/frontend/PRD_{FRONTEND_PLATFORM,AETHER_CLI,AETHER_DESKTOP,AETHER_LAB,AETHER_TUI}.md`.
