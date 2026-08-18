# 011 — Demo spec (Proposed)

Status: `Proposed`  
Date: 2026-08-17

## Fixtures

Real paths: `vanguard/clients/cli/fixtures/*.jsonl` today; `vanguard/clients/cli/fixtures/sessions/` for `--demo` catalog.

Do not invent fixtures under `docs/` or `tools/ci/`.

## Labelling

Mandatory: `source: mock` on every demo/replay surface (CLI header, JSONL `StreamItem.source`, GUI badge). Replay of a recorded live ledger still must not claim `live` unless the socket is connected.

## `vg --demo`

Extends `adapters/replay.ts` in `@vanguard/client-core`. Default: no daemon socket required.

## Standalone GUI Replay

FE-3: The standalone GUI shell must render `successful-episode.jsonl` (and peers) **without** a running daemon via `ReplayRuntimeClient`.
