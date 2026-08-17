# S27-A — Local live campaign, two Ollama arms

**Date:** 2026-08-17 · `REQ-TRUST-001` · **Local only. Nothing paid contacted.**
**Nothing resolved. No lift. No Q2. No leaderboard.**

## Results

Both arms: `vg-code-default`, pack prompt unmodified, BENCHMARK,
`max_turns=4`, `max_attempts=1`. Denominator 4 for each.

### `ollama:llama3.2:3b` — 0/4 resolved, 0 inconclusive

| Task | Outcome | Turns | Verbs |
|---|---|---|---|
| DOGFOOD-01 | `attempts_exhausted` | 1 | `fs.read` |
| DOGFOOD-02 | `attempts_exhausted` | 4 | `proc.exec` ×3, `fs.search` |
| DOGFOOD-03 | `attempts_exhausted` | 4 | `proc.exec` ×4 |
| GREENFIELD-API-HTML | `attempts_exhausted` | 1 | — |

### `ollama:deepseek-r1:14b` — 0/4 resolved, 1 inconclusive

| Task | Outcome | Turns | Verbs |
|---|---|---|---|
| DOGFOOD-01 | `instrument_error:provider_timeout` | 0 | — |
| DOGFOOD-02 | `attempts_exhausted` | 1 | — |
| DOGFOOD-03 | `attempts_exhausted` | 1 | — |
| GREENFIELD-API-HTML | `attempts_exhausted` | 1 | — |

**A-27-02: `deepseek-r1:14b` is a labelled skip, not a leaderboard row.** It
produced no tool call on any task — prose only — and timed out once at 300s.
Reporting it beside `llama3.2:3b` as though the two were comparable would be
comparing a model that tool-calls against one that does not.

The one timeout is `instrument_error:provider_timeout`, counted in the
denominator, and its `terminalRefusal` is on the ledger (`C-01`).

## Correction to the S22 note

S22 reported greenfield as **4/4 `multi_action_proposal`, deterministic**. That
was four consecutive runs in one session; it is not a stable property. In this
campaign greenfield produced a prose finish (`turns=1`, no verb, no refusal) on
both arms. The honest statement is: greenfield **sometimes** trips the
one-effect-per-turn rule and sometimes returns prose, and the earlier "4/4"
should be read as a sample, not a rate.

## A-27-03 — no paid call was made

The gate is a greenfield run producing at least one verb. Greenfield produced
**no** verb on either arm, so OpenRouter and DeepSeek were not called. Neither
key is set, and nothing was spent.

## Denominator

Every task is counted on both arms, including the timeout. Nothing was dropped.

Per-task `vg.4` ledgers in this directory; project with
`python3 tools/export_coding_session.py --jsonl <file>`.
