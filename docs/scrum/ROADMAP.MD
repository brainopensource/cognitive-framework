# Vanguard roadmap (navigator)

Status: `NAVIGATOR`  
Last updated: 2026-08-16  
Authority: `docs/main_v4/` is normative for the product and wire. This file routes work; it does not restated contracts.

---

## 0. How to read this file

### 0.1 What lives where

| Tree | Role |
|---|---|
| `docs/main_v4/` | Normative product / wire / ADRs. **Frozen for frontend.** |
| `docs/scrum/sprints/sprint07` … `sprint10` | Backend lane kits (control plane, workload, measurement). |
| `docs/scrum/development_guides/` | Implementer projections, including the **ratified FE lock**. |
| `docs/front_v4/` | Frontend consumer notes. Status **Proposed** until ratified in the two-lanes doc. |
| `docs/scrum/sprints_front/` | Frontend delta kits (`FE-A-n` / `FE-B-n`). |

`docs/front_v4/` and `docs/scrum/sprints_front/` **exist**. Do not claim they are missing.

### 0.2 Rules for frontend

1. Consume the daemon as shipped. Do not silently fork the wire.
2. Backend gaps are Joint notes (`J1`–`J5` in the two-lanes doc), not client inventions.
3. Detail lives in sprint kits. This board is IDs, paths, depends, and acceptance commands only.

### 0.3 ID collision rule

Backend sprints keep `S7-…` / `sprint07` numbering. Frontend waves use **`FE-A*`** and **`FE-B*`** only. Do not name frontend kits “Sprint 1–4”.

---

## 1. Backend (frozen for FE)

Backend delivery continues under `docs/scrum/sprints/sprint07`–`sprint10` and `docs/reviews/doing/`. Frontend must not edit `vanguard/packages/**`, `benchmarkings/**`, backend tools/CI, or `docs/main_v4/**`.

Wire lock: **ADR-0062** + VG-04 §0 / §12 / §15. Implemented frames: `vanguard/packages/runtime/service/server.py`.

---

## 2. Frontend law

Binding: [`development_guides/frontend_senior_review_and_two_lanes.md`](development_guides/frontend_senior_review_and_two_lanes.md) (D1–D6).

CLI architecture (APPROVED): [`development_guides/cli_tui_architecture.md`](development_guides/cli_tui_architecture.md).

Two lanes from day one:

- **FE-A** — Ink TUI at `vanguard/clients/cli/**` (extend, do not rewrite).
- **FE-B** — VS Code extension at `vanguard-ide/**` (new; no Code-OSS fork now).

---

## 3. Frontend board (locked)

Each row: lane, scope path, depends, acceptance command. Task detail is in `sprints_front/`.

### 3.1 Lane FE-A — CLI TUI (`vanguard/clients/cli/**`)

| ID | Scope | Depends | Acceptance |
|---|---|---|---|
| FE-A1 | Delete dead scaffold; wire `adapters/signer.ts` | — | `cd vanguard/clients/cli && npm run typecheck && npm test`; grep shows no imports of deleted files | **DONE** |
| FE-A2 | Split live transports; type frames (CT-03) | FE-A1 | existing tests green without modification | **DONE** |
| FE-A3 | RFC-8785 JCS in signer + `~/.vanguard/keys` 0600 | FE-A1 | round-trip vs Python `OperatorSigner` golden vector | **DONE** |
| FE-A4 | TUI tree `src/tui/{components,screens,hooks,theme}/` + `useVanguardRun` | FE-A1 | boundary test extended; `ui.test.ts` passes | **DONE** |
| FE-A5 | Socket reconnect/backoff + timeouts | FE-A2 | new tests with fake socket | **DONE** |
| FE-A6 | `vg --demo` replay, `source: mock`, `fixtures/sessions/` | FE-A4 | typecheck + tests; demo UI labelled mock | **DONE** |
| FE-A7 | `manageDaemon` honest `not_available` until J1; fix hardcoded version | J1 for full lifecycle | typecheck + tests; no fake daemon status | **DONE** (spawn still J1) |
| FE-A8 | Approval digests from challenge; `explainArtifact` `not_available` when absent | FE-A3, J4 for E2E | typecheck + tests; no empty placeholder signatures as success | **DONE** |
| FE-A9 | `install.sh` + npm-global; usage documents flags | FE-A6 | install path documented; `vg --help` lists flags | **DONE** |
| FE-A10 | Fixture catalog + soak under `vanguard/clients/cli/test/` | FE-A6 | catalog matches architecture appendix; soak not in `tools/ci/` | **DONE** |

Wave kits: `sprints_front/lane_a_wave1.md` (A1–A5), `sprints_front/lane_a_wave2.md` (A6–A10).

**Lane FE-A: complete** (2026-08-16). Joint J1 still blocks real daemon spawn; A7 ships `not_available`.

### 3.2 Lane FE-B — IDE extension (`vanguard-ide/**`)

| ID | Scope | Depends | Acceptance | Status |
|---|---|---|---|---|
| FE-B1 | Extension scaffold (TS, `vscode` engine, esbuild): sidebar, commands, CodeLens stub | — | `cd vanguard-ide && npm run typecheck && npm run build` | Done |
| FE-B2 | Vendor `contract/` + `RuntimeClient` port + replay vs CLI fixtures | — (freeze at FE-A wave-1 start) | replay adapter reads `vanguard/clients/cli/fixtures/*.jsonl` | Done |
| FE-B3 | Webview run stream (thoughts/tools/budget); tokens from front_v4/004 | FE-B1, FE-B2 | webview renders from replay without a daemon | Done |
| FE-B4 | Approval UX: diff + CodeLens + Ed25519 (port of FE-A3) | FE-B3, FE-A3 for signer semantics | approve/reject path on replay challenge | Done |
| FE-B5 | Live socket bridge (same frames, same path resolution) | FE-B2 | live stream against real daemon | Done |
| FE-B6 | Editor context into `StartRun` brief only; new fields = Joint | FE-B5 | payload stays within existing `StartRun` shape | Done |
| FE-B7 | E2E matrix per front_v4/007 | FE-B5 | unit → VG-04 vectors → replay E2E → live E2E | Done |
| FE-B8 | `.vsix` + Open-VSX / private dist note | FE-B1 | `npm run build` produces `.vsix` | Done |

Wave kits: `sprints_front/lane_b_wave1.md` (B1–B4), `sprints_front/lane_b_wave2.md` (B5–B8).

**Lane FE-B: complete** (2026-08-16). All tasks B1–B8 delivered and verified under `vanguard-ide/**`.

**Parallel rule:** FE-B1–B4 need only frozen contract + fixtures. FE-A waves run concurrently.

---

## 4. Explicitly not on this board

- Tauri / AppImage-embedded-Python (Phase 4+).
- Code-OSS fork now (Phase 4+ reversal in front_v4/009).
- Client SIEM / DLP / SSO (DLP/egress is daemon-side → Joint).
- Invented verbs: `Ping`, `ListManifests` (J2, J3).
- FE edits under `vanguard/packages/**`.
