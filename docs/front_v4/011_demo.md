# 011 — Demo spec (Proposed)

Status: `Proposed`  
Date: 2026-08-16

## Fixtures

Real paths: `vanguard/clients/cli/fixtures/*.jsonl` today; `vanguard/clients/cli/fixtures/sessions/` for `--demo` catalog (FE-A6 / architecture §4.2).

Do not invent fixtures under `docs/` or `tools/ci/`.

## Labelling

Mandatory: `source: mock` on every demo/replay surface (CLI header, JSONL `StreamItem.source`, IDE webview badge). Replay of a recorded live ledger still must not claim `live` unless the socket is connected.

## `vg --demo`

**To-build** (FE-A6). Extends `adapters/replay.ts`. Scenario flags select catalog ids. Default: no daemon socket.

## Subagents

Subagent / swarm demo scenario is **deferred (DEF-03)**. A fixture may exist later; it is not a current acceptance criterion.

## IDE

FE-B3/B7: webview must render `successful-episode.jsonl` (and peers) **without** a running daemon.
