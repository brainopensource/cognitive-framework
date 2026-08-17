# Frontend roadmap

Status: living board  
Updated: 2026-08-16

**Spec:** `docs/main_v4/` (wire VG-04, daemon as shipped). Do not fork the wire in the client.  
**Notes:** `docs/front_v4/` · **How-to kits:** `docs/scrum/sprints_front/`  
**Backend board:** `docs/scrum/roadmap_backend.md`

This file is the only frontend backlog.

FE-A writes `vanguard/clients/cli/**`. FE-B writes `vanguard-ide/**`. Neither edits `vanguard/packages/**`.

---

## Roadmap (high level)

Operator surfaces for the same daemon: a TUI now, a VS Code extension now. Not a Code-OSS fork. Not Tauri.

| Wave | What | Status |
|---|---|---|
| FE-A wave 1 | Hygiene, transports, signer, TUI tree, reconnect | `[DONE]` |
| FE-A wave 2 | Demo replay, honest daemon status, approvals, install, soak | `[DONE]` |
| FE-B wave 1 | Extension scaffold, contract, replay webview, approval UX | `[DONE]` |
| FE-B wave 2 | Live socket, editor brief, E2E matrix, `.vsix` | `[DONE]` (live path still needs daemon J1) |
| Next | Real daemon E2E + dogfood on this repo | `[TODO]` — blocked on backend Joint J1 |
| Later | Named Pipe/TCP, extra installers, Code-OSS — `docs/front_v4/010_phase4_considerations.md` | not now |

DoD:

```bash
cd vanguard/clients/cli && npm run typecheck && npm test
cd vanguard-ide && npm run typecheck && npm run build
```

---

## Already done — Lane FE-A (CLI / TUI)

| ID | Status | Task |
|---|---|---|
| FE-A1 | `[DONE]` | Delete dead scaffold; wire `adapters/signer.ts` |
| FE-A2 | `[DONE]` | Split live transports; typed frames (CT-03) |
| FE-A3 | `[DONE]` | RFC-8785 JCS signer; keys `~/.vanguard/keys` 0600 |
| FE-A4 | `[DONE]` | TUI tree `src/tui/{components,screens,hooks,theme}/` + `useVanguardRun` |
| FE-A5 | `[DONE]` | Socket reconnect/backoff/timeouts |
| FE-A6 | `[DONE]` | `vg --demo` replay, labelled mock |
| FE-A7 | `[DONE]` | `manageDaemon` returns `not_available` until backend J1; no fake “running” |
| FE-A8 | `[DONE]` | Approval digests from challenge; no empty signature as success |
| FE-A9 | `[DONE]` | `install.sh` / npm-global; `vg --help` flags |
| FE-A10 | `[DONE]` | Fixture catalog + soak under `vanguard/clients/cli/test/` |

Kits: `sprints_front/lane_a_wave1.md`, `lane_a_wave2.md`.

---

## Already done — Lane FE-B (VS Code extension)

| ID | Status | Task |
|---|---|---|
| FE-B1 | `[DONE]` | Extension scaffold (TS, esbuild): sidebar, commands, CodeLens stub |
| FE-B2 | `[DONE]` | Vendor `contract/` + `RuntimeClient`; replay vs CLI fixtures |
| FE-B3 | `[DONE]` | Webview run stream from replay (no daemon) |
| FE-B4 | `[DONE]` | Approval UX: diff + CodeLens + Ed25519 (same semantics as A3) |
| FE-B5 | `[DONE]` | Live socket bridge (same frames as CLI) |
| FE-B6 | `[DONE]` | Editor context only in existing `StartRun` brief |
| FE-B7 | `[DONE]` | E2E matrix (unit → VG-04 vectors → replay; live waits J1) |
| FE-B8 | `[DONE]` | `.vsix` build |

Kits: `sprints_front/lane_b_wave1.md`, `lane_b_wave2.md`.

---

## Still to do (frontend)

Blocked items are backend Joint, not FE inventions.

| ID | Status | Task |
|---|---|---|
| FE-N1 | `[TODO]` | Live CLI: `vg` starts/uses real daemon once **J1** (spawn/supervisor) exists |
| FE-N2 | `[TODO]` | Live IDE: same daemon as CLI; one operator session |
| FE-N3 | `[TODO]` | Dogfood: one real coding task on this repo through `vg` (pairs backend S9-J-01) |
| FE-N4 | `[TODO]` | Manifest picker without inventing `ListManifests` until **J3** |
| FE-N5 | `[TODO]` | Connect/health without inventing `Ping` until **J2** |
| FE-N6 | `[TODO]` | Windows / extra transports only after daemon owns them (**J5**) |

**Not FE work:** SIEM, client DLP, SSO replacing Ed25519, Tauri, Code-OSS fork.

---

## Joint notes (backend must build; FE consumes)

| ID | Need |
|---|---|
| J1 | Daemon lifecycle so `manageDaemon` is real |
| J2 | Health/connect probe |
| J3 | List manifests (or documented substitute) |
| J4 | Artifact explain / E2E approval with real challenge |
| J5 | Extra transports if product requires them |
