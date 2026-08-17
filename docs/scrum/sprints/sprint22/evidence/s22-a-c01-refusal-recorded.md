# S22-A / `C-01` — a refused proposal reaches the ledger

**Date:** 2026-08-17 · `REQ-TRUST-001` · **Local only. No spend. No lift. No Q2.**

## The defect

`agency/episode/engine.py` terminated on three paths *before* `_emit_proposal`:
the provider raised, the provider returned no proposal, or the translator
refused the proposal's shape. All three left **no event at all**. The ledger
showed an episode that never happened, and a model whose batch of tool calls
was refused was indistinguishable from a model that was never asked (`A-07`).

Measured before: a live greenfield run produced `events: []`.

## `C-01` — emit the refused terminal

**One function**, `EpisodeEngine._emit_terminal`, called on exactly those three
paths. It emits `EpisodeCompleted` — an existing kind the reducer already
understands — carrying `outcome` and the refusal `detail`. No new event kind,
no parallel store, no second loop.

It is deliberately **not** a `ProposalProduced`: no turn occurred, and
recording one would claim a turn the episode never took.

## After

Four consecutive live greenfield runs (`ollama:llama3.2:3b`), deterministic:

```
instrument_error:multi_action_proposal  turns=0
  terminalRefusal={'outcome': 'instrument_error',
                   'detail': 'multiple actions in one proposal are unsupported',
                   'afterTurn': 0}
```

The JSONL now contains the `EpisodeCompleted` envelope. Previously it was
empty.

## Both directions tested

- **Batch refused is recorded** — terminal event present, reason carried,
  `ProposalProduced` absent, session log surfaces `terminal_refusal`, and a
  provider *exception* is recorded too.
- **Single tool still dispatches** — `fs.read` still produces a turn, a normal
  run reports `terminal_refusal: None`, the MOCK driver run is unchanged
  (`attempts_exhausted`, 4 turns), and the ledger still reduces.

Engine regression suite (`test_episode`, `test_episode_spawn`, `test_spine`):
55 tests, unchanged.

## Scoring

`instrument_error:multi_action_proposal` is inconclusive, stays in the
denominator, and is never `oracle_green`.

## Not ours

The pack's one-tool-per-turn instruction is BETA (`S22-B`). Nothing here tunes
the model toward tool-calling, and the live rate is reported, not improved.
