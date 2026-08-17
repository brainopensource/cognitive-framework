# Frontend Lock — CLI TUI now, IDE later, two parallel lanes

**Role:** Tech Lead, frontend. Backend (`vanguard/packages/**`, `benchmarkings/**`, backend tools/CI, `docs/main_v4/**`) is frozen. All FE work consumes the existing daemon over the shipped vg.4-frame protocol.

## 1. Locked decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | **Wire protocol = vg.4 frames as implemented** in `vanguard/packages/runtime/service/server.py` + `vanguard/clients/cli/src/adapters/live.ts`. | Backend frozen; `docs/front_v4/003` (JSON-RPC 2.0, `Ping`, `LedgerEvent`, 4 MB frames) describes a protocol that exists nowhere. Throw 003 away. |
| D2 | **TUI = keep the Ink stack and hexagonal layout** in `vanguard/clients/cli/`. Fix deltas; do not rewrite. | Layering is correct (verified: no vanguard-package imports, boundary test exists). Core is solid; problems are dead code and missing deltas, not architecture. |
| D3 | **IDE = standard VS Code extension** at `vanguard-ide/` (webview panel + CodeLens + daemon bridge over the same socket). **No Code-OSS fork now.** Standalone "Vanguard IDE" via VSCodium-style Code-OSS build is a Phase-4+ productization option, documented as a reversal path. | A fork is a multi-person maintenance program (upstream tracking, signing, per-OS CI) and sprint3's "~380 LOC fork" is fantasy. An extension delivers the same UX and keeps lane B unblocked. |
| D4 | **Two lanes, parallel from day one.** FE-A: `vanguard/clients/cli/**`. FE-B: `vanguard-ide/**`. | The real dependency is a frozen client-side wire contract + replay fixtures — both already exist (`src/contract/`, `fixtures/*.jsonl`, `adapters/replay.ts`). FE-B develops against replay/mock daemon; no wait on FE-A. |
| D5 | **`docs/front_v4/` demoted from self-declared "Normative" to "Proposed"** until TL ratification per file. 003/006/010 rewritten; 001/005/008/009/011/012 revised to reality; 002/004/007 kept with minor fixes. | The registry was never ratified (`frontend_senior_review_and_two_lanes.md` gate); 003 contradicts VG-04/ADR-0062 and the daemon. |
| D6 | **Backend gaps become Joint notes, not FE workarounds.** No client-side invention of RPCs, manifest schemas, or daemon entrypoints. | `frontend_senior_review_and_two_lanes.md`: "do not silently fork the wire"; ROADMAP §0.2 rule 2. |

## 2. Doc work (this plan's deliverables)

### 2a. Rewrite `docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md`
Convert the open review prompt into the **decision record**: verdicts extend/reshape/replace (extend CLI; replace front_v4/003 stack; extension-not-fork), the D1–D6 table, lane ownership, and the backend note list (§5). This is the top FE law below main_v4.

### 2b. Rewrite FRONTEND section of `docs/scrum/ROADMAP.MD`
- Fix staleness: `docs/front_v4/` and `docs/scrum/sprints_front/` exist; remove "missing" claims.
- Replace the staging board `FE-101…404` with the locked two-lane board (§4 below), IDs `FE-A1…`, `FE-B1…`, each row: lane, scope path, depends, acceptance command.
- Keep ROADMAP as navigator only — detail lives in sprint kits.

### 2c. Rewrite `docs/scrum/development_guides/cli_tui_architecture.md` (keep APPROVED status, bump revision)
- Update §5 target tree to the corrected structure: `src/tui/{components,screens,hooks,theme}/`, `src/composition/` — and make it binding.
- Add the live-socket frame protocol appendix (thin, cites VG-04 + `server.py` verbs; no restated contract).
- Document `--demo` mock-labelling rule (already in spirit; make explicit).
- Fixture catalog requirement: name the concrete fixture set.

### 2d. `docs/front_v4/` — file-by-file dispositions
- **003 wire spec → REWRITE** as thin consumer note: cite VG-04 §0/§12/§15, ADR-0062; document implemented frames (verbs, `receipt`/`error`, 1 MiB cap, UDS path resolution order `--socket-path` → `VANGUARD_RUNTIME_SOCKET` → `/tmp/vanguard-runtime.sock`). No new verbs. Keep only JCS-canonicalization guidance retargeted to the real `ApprovalChallenge`/`ApprovalDecision`.
- **006 dev guide/pseudocode → REWRITE** from the shipped `RuntimeClient` interface (AsyncIterable streaming, `Result<T>` failures), real frame shapes; keep ring-buffer cap + 0600 key handling.
- **010 enterprise → REWRITE** as a 1-page "Phase-4+ considerations" note; drop SIEM/DLP-in-client/SSO invention (DLP/egress is daemon-side → Joint note).
- **001 backlog → REVISE**: remap EPIC/US IDs to FE-A/FE-B rows; delete Tauri (ROADMAP rejects it), EPIC-09, M4 1000-run soak; fix hallucinated target files.
- **002 architecture → REVISE**: keep invariants INVAR-FE-01..04 (best content in registry); rewrite §3 tree to reality; mark §4 Named Pipe/TCP as proposed + backend-dependent.
- **004 UI/UX → REVISE (minor)**: re-key state machine to VG-04 event names (`ApprovalRequested`, `EpisodeCompleted`…); status → Proposed.
- **005 manifests → REVISE (heavy)**: real manifest schema (`{harness, components, capabilities[{verb,sink,selector,risk}], evaluators, budgetPolicy}`); discovery via proposed daemon verb, never direct `vanguard/packages/` reads; label subagents Phase-2-deferred (DEF-03).
- **007 testing → REVISE (minor)**: fix phantom paths; target VG-04 golden vectors + `test/contracts/t1_wire_contracts.py`.
- **008 packaging → REVISE**: channels 1–2 only (`curl|sh`, npm global); drop Tauri/AppImage-embedded-Python to Phase 4; fix dead links; remove invented `github.com/vanguard-ai/*` infra references.
- **009 fork spec → REVISE**: retitle "Vanguard IDE — extension-first, fork deferred"; keep debloat/product.json research as an appendix for the Phase-4+ option; fix `product.json` hallucinations; settle directory name `vanguard-ide/`.
- **011 demo spec → REVISE**: real fixture paths (`vanguard/clients/cli/fixtures/`); mandatory `source: mock` labelling; caveat the subagent scenario as deferred; `vg --demo` marked to-build.
- **012 decision register → REVISE**: ADR-FE-002/FE-004 become citations of ADR-0062; FE-003 replaced by D3 (extension-first with documented reversal); keep anti-patterns + checklist; strip meme language.
- **All files**: status header → `Proposed` until ratified; ratification recorded in the rewritten two-lanes doc (2a).

### 2e. `docs/scrum/sprints_front/` — replace kits 1–4 with lane-tagged delta kits
New structure: `sprints_front/README.md` (lane rules, DoD commands) + per-lane kits below (§4). Every task = delta against existing files, with acceptance criteria + DoD command (mirroring backend sprint kit format in `sprints/sprint07..10`). Sprint numbering: `FE-A-n` / `FE-B-n` waves, not "Sprint 1–4" (ROADMAP §0.3 collision rule).

## 3. Lane FE-A — CLI TUI workstream (`vanguard/clients/cli/**`)

Kit `sprints_front/lane_a_wave1.md` — hygiene & protocol truth:
- **FE-A1**: Delete dead scaffold: `src/commands.ts`, `src/runtime.ts`, `src/mock-runtime.ts`; wire `adapters/signer.ts` in or delete it (decision: wire it — needed for signed approvals). DoD: `npm run typecheck && npm test` green; grep shows no imports.
- **FE-A2**: Split `LiveRuntimeClient` into one transport per class (`FeedTransport` / `SocketTransport` behind a transport interface); remove `isFeedMode()` branches; type the `frame: any` paths (CT-03: parse, never cast). DoD: existing tests green without modification.
- **FE-A3**: Real RFC-8785 JCS canonicalization in `signer.ts` (add `canonicalize` dep) + key persistence at `~/.vanguard/keys` with 0600. DoD: round-trip test vs Python `OperatorSigner` golden vector (read-only use of backend test vectors).
- **FE-A4**: TUI restructure to `src/tui/{components,screens,hooks,theme}/`; extract stream-lifecycle hook (`useVanguardRun`) from `RunTui`; fix `ApprovalModal` misleading props. DoD: boundary test extended to new paths; `ui.test.ts` passes.
- **FE-A5**: Socket reconnect/backoff + configurable timeouts in live adapter. DoD: new tests with fake socket.

Kit `sprints_front/lane_a_wave2.md` — product surface:
- **FE-A6**: `vg --demo` replay mode (extends `adapters/replay.ts`), scenario flags, `source: mock` label, fixture catalog under `fixtures/sessions/`. Depends: FE-A4.
- **FE-A7**: `manageDaemon` real lifecycle against backend entrypoint — **blocked on Joint note J1**; until then, explicit `not_available` with actionable error text (no fake status). Also fix `getDaemonStatus` hardcoded version.
- **FE-A8**: Approval flow truth: populate `argsDigest`/`descriptorDigest`/`expiresAt` from the real challenge (no empty placeholders); stop fabricating `explainArtifact` evidence — surface `not_available`. 
- **FE-A9**: Distribution channels 1–2: `install.sh` + npm-global polish; usage text documents all flags. Depends: FE-A6.
- **FE-A10**: Fixture catalog completion per rewritten arch doc; soak harness inside `vanguard/clients/cli/test/` (not `tools/ci/`).

## 4. Lane FE-B — IDE extension workstream (`vanguard-ide/**`, new)

Kit `sprints_front/lane_b_wave1.md` — scaffold against replay (no FE-A dependency):
- **FE-B1**: `vanguard-ide/` extension scaffold (TypeScript, `vscode` engine, esbuild), CI-free local build. Contributes: sidebar webview view, commands, CodeLens provider stub.
- **FE-B2**: **Vendor the client contract**: copy `contract/types.ts` + `contract/parse.ts` + a `RuntimeClient`-shaped port into `vanguard-ide/src/contract/` (single-source-of-truth = FE-A repo path; vendoring is a build step so the extension has no monorepo dependency). Replay adapter port for development against `vanguard/clients/cli/fixtures/*.jsonl`.
- **FE-B3**: Webview panel: run stream view (thoughts/tools/budget) consuming the reducer pattern from FE-A (`run-view.ts` ported or shared via vendored package `@vanguard/client-contract`). Design tokens from revised front_v4/004.
- **FE-B4**: Approval UX: diff view + `[Approve & Sign]/[Reject]` CodeLens + Ed25519 signing (port of FE-A3 signer).

Kit `sprints_front/lane_b_wave2.md` — live + editor integration:
- **FE-B5**: Live socket bridge (same frame protocol, same path resolution) — shared vendored transport. Depends: FE-B2; integrates against the real daemon.
- **FE-B6**: Editor context sync (active editor, selection, git state) into run brief payload — within existing `StartRun` payload shape; any new field is a Joint note.
- **FE-B7**: E2E matrix per revised front_v4/007: unit → VG-04 golden vectors → replay E2E → live E2E.
- **FE-B8**: `.vsix` packaging + Open-VSX/private distribution note. (No MSI/notarization program — deferred.)

**Parallel rule:** FE-B1–B4 need only the frozen contract + fixtures; FE-A waves run concurrently. Shared code (contract, parse, signer) is owned by FE-A, consumed by FE-B via vendoring; FE-B never edits `vanguard/clients/cli/**` and vice versa.

## 5. Joint notes (backend requests — NOT edited by FE)

- **J1**: Daemon self-launch entrypoint (`python3 -m vanguard.packages.runtime.service.server` currently has no `__main__`). Blocks FE-A7 full lifecycle; workaround shipped in FE-A7.
- **J2**: `Ping`/health verb (supervisor probe currently connect-only).
- **J3**: `ListManifests` verb (manifest selector; interim: FE reads nothing backend-side — selector ships with user-provided manifest path only).
- **J4**: Populated approval challenge digests so FE-A8 signs real content end-to-end.
- **J5**: Wire-change wishes (e.g., Windows Named Pipe transport) filed as notes for Joint per the brief; no FE-side transport invention.

## 6. What is thrown away (explicit)

- `front_v4/003`, `006`, `010` — full rewrites as scoped above.
- `sprints_front/sprint1–4` kits — replaced by lane kits (old content mined for: reconnect/JCS/key-persistence deltas, `--demo` concept, webview/CodeLens ideas, E2E pyramid).
- `vanguard/clients/cli/src/{commands,runtime,mock-runtime}.ts` — dead code deleted (FE-A1).
- Tauri channel, Code-OSS-fork-now, EPIC-09, M4 soak fantasy — deleted from all docs.

## 7. Verification

1. Docs: every FE doc status header updated; `grep -r "jsonrpc" docs/front_v4 docs/scrum/sprints_front` returns nothing; every event name in FE docs matches VG-04 §12.2 vocabulary; ROADMAP FE board rows all carry lane + acceptance command.
2. CLI: `cd vanguard/clients/cli && npm run typecheck && npm test` green; new tests for transport split, JCS vectors, reconnect; boundary test still enforces no-UI-imports-in-application.
3. IDE: `cd vanguard-ide && npm run typecheck && npm run build` produces `.vsix`; webview renders from replay fixture without a daemon.
4. Parallel-lane proof: FE-B1–B4 completable with `vanguard/clients/cli/` checked out at the FE-A-wave-1-start commit (fixture+contract freeze point).
5. Boundary audit: `grep -r "vanguard/packages" vanguard/clients/cli/src vanguard-ide/src` returns nothing; no edits under `vanguard/packages/**`, `benchmarkings/**`, `docs/main_v4/**`.
