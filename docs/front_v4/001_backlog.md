# 001 — Frontend backlog (Proposed)

Status: `Proposed`  
Date: 2026-08-16  
Maps to: `docs/scrum/ROADMAP.MD` §3 and `docs/scrum/sprints_front/`

IDs are **FE-A\*** / **FE-B\*** only. There is no Tauri epic, no EPIC-09, no M4 1000-run soak, and no invented target files under `vanguard/packages/`.

## Lane FE-A — `vanguard/clients/cli/**`

| ID | Summary | Kit |
|---|---|---|
| FE-A1 | Delete `src/commands.ts`, `src/runtime.ts`, `src/mock-runtime.ts`; wire `adapters/signer.ts` | wave1 |
| FE-A2 | Split `LiveRuntimeClient` transports; parse frames | wave1 |
| FE-A3 | RFC-8785 JCS + `~/.vanguard/keys` 0600 | wave1 |
| FE-A4 | Move UI to `src/tui/{components,screens,hooks,theme}/`; `useVanguardRun` | wave1 |
| FE-A5 | Reconnect / backoff / timeouts | wave1 |
| FE-A6 | `vg --demo` replay + `source: mock` + `fixtures/sessions/` | wave2 |
| FE-A7 | Honest daemon lifecycle (`not_available` until J1) | wave2 |
| FE-A8 | Approval challenge fields; no fabricated why evidence | wave2 |
| FE-A9 | `install.sh` + npm global; flag docs | wave2 |
| FE-A10 | Fixture catalog + soak in `vanguard/clients/cli/test/` | wave2 |

## Lane FE-B — `vanguard-ide/**`

| ID | Summary | Kit |
|---|---|---|
| FE-B1 | Extension scaffold | wave1 |
| FE-B2 | Vendor contract + replay | wave1 |
| FE-B3 | Webview run stream | wave1 |
| FE-B4 | Approval CodeLens + signer port | wave1 |
| FE-B5 | Live UDS bridge | wave2 |
| FE-B6 | Editor context in existing `StartRun` brief | wave2 |
| FE-B7 | E2E pyramid | wave2 |
| FE-B8 | `.vsix` packaging | wave2 |

## Removed from earlier drafts

- Tauri desktop (ROADMAP rejects it for this phase).
- EPIC-09 / standalone Code-OSS fork-now (see 009).
- M4 soak of 1000 live daemon runs as a frontend gate.
- Target paths that never existed (`src/commands.ts` as the *product* surface after A1 is deleted, not expanded).
