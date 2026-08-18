# S20-A — A live model completes tool-calling turns on `vg-code-default`

**Date:** 2026-08-17 · **Branch:** `feat_sprint_special` · `REQ-TRUST-001`
**No lift. No Q2. Nothing paid contacted.**

## S20-A-02 — the freeze target is met

`ollama:llama3.2:3b`, `vg-code-default`, **pack prompt unmodified**, BENCHMARK:

| Task | Outcome | Turns | Session |
|---|---|---|---|
| DOGFOOD-01 | `attempts_exhausted` | 4 | `fs.search`→completed · `patch.apply`→denied · `fs.search`→completed · finish |
| DOGFOOD-02 | `attempts_exhausted` | 1 | `fs.search`→completed |
| DOGFOOD-03 | `attempts_exhausted` | 3 | `proc.exec`→denied ×3 |
| GREENFIELD-API-HTML | `instrument_error` | 0 | — |

Live verbs observed: `fs.search`, `patch.apply`, `proc.exec`. The
`patch.apply` and `proc.exec` denials are `denied_ask_fail_closed` — BENCHMARK
mode refusing privileged verbs without a human, which is `K-17` working, not a
failure.

Nothing resolved. Denominator 4. **The runner is proven; the model is not
scored.**

## S20-A-01 — the two remaining causes, named

**`deepseek-r1:14b` does not tool-call.** With the pack prompt it returns
prose; with an explicit *"you MUST call exactly one tool"* system message it
still returns prose. `llama3.2:3b` and `qwen3.6:27b` both emit
`fs.read {path: src/calculator.py}` through the same adapter and the same
unmodified pack. So this is a property of that model in Ollama — **not** the
adapter and **not** the pack prompt. Earlier S19 rows labelled
`attempts_exhausted` for deepseek-r1 are that, and nothing more.

**Greenfield: `multiple actions in one proposal are unsupported`.** The model
batched several tool calls into one turn and the translator refused, because
one turn is one effect. That is a labelled design constraint of the harness,
not a model score, and it is now reported in those words instead of as
`model_not_invoked`.

## Instrument defects fixed this sprint

1. **Timeout read as a zero.** The 60s ceiling turned a reasoning model's think
   block into `instrument_error: timed out`, and the driver reported
   `model_not_invoked` — the *shape* of the failure, not its cause. Local
   timeout is now 300s and the driver surfaces the provider's own reason.
   Greenfield went 0 turns → 1 turn on that change alone.
2. **`model_not_invoked` was masking everything.** Any zero-turn run said the
   same thing whatever went wrong. The run's own `detail` now wins.

## Frozen entrypoints (v0.4.5)

```
python3 lab/run.py --pack P --task-dir D [flags]          # stdlib shim
python3 -m vanguard.packages.runtime.lab_driver …         # the driver
```
Flags: `--pack --task-dir --model mock|ollama|openrouter|deepseek --model-name
--interactive|--benchmark --max-turns --max-attempts --jsonl-out --json`.
Default `--model mock`. No daemon exists and none was invented.

JSONL is `vg.4` straight from the store; project with
`python3 tools/export_coding_session.py --jsonl <file>`. DOGFOOD-01 projects to
`denialCount: 1`.

## Not run

OpenRouter free / DeepSeek flash: `OPENROUTER_API_KEY` unset. Dated skip.
