# S19-A — Live Ollama smoke, four declared tasks

**Date:** 2026-08-17 · **Branch:** `feat_sprint_special` · `REQ-TRUST-001`
**Model port:** `ollama:deepseek-r1:14b` (local daemon) · **Nothing paid was contacted.**
**No lift is published. Q2 is not claimed.**

## Result

| Task | Outcome | Turns | Wall |
|---|---|---|---|
| DOGFOOD-01 | `attempts_exhausted` | 1 | 28.4s |
| DOGFOOD-02 | `attempts_exhausted` | 1 | 50.4s |
| DOGFOOD-03 | `attempts_exhausted` | 1 | 14.6s |
| GREENFIELD-API-HTML | `instrument_error` | 0 | 55.1s |

Denominator 4. Nothing resolved. **Failure is the data.**

## What the run actually shows

`deepseek-r1:14b` answers, but does not reliably emit a tool call against this
pack: on the three dogfood tasks it produced one turn of prose (`verb: None`,
no receipt) and finished. It told the operator to run `cat src/calculator.py`
rather than calling `fs.read`. On the greenfield task it produced nothing the
translator could use at all, which is reported as `model_not_invoked` — an
instrument error, not a failed repair.

That is a measurement of this model on this pack, at `max_turns=3`. It is not
a statement about the harness, and it is not a benchmark.

## Two instrument defects this smoke exposed, both mine

1. **The Ollama probe was fail-open.** `select_model` checked only that the
   daemon root answered, so it reported `ollama:deepseek-r1` available while
   that tag was not pulled. Every task then failed with `model_not_invoked` in
   0.0s — an instrument error dressed as four measurements. The probe now
   resolves the tag against `/api/tags` and refuses by name when absent,
   matching a family (`deepseek-r1` → `deepseek-r1:14b`) but never inventing
   one.

2. **The Ollama adapter sent the wrong tool shape.** It passed the manifest
   schema (`{name, verb, schema}`) straight through; the endpoint wants
   `{"type": "function", "function": {…, "parameters"}}`. Every request
   returned `HTTP 500`, surfacing as `model_not_invoked` — a live model that
   was never actually asked anything.

Both were only findable by running against a real daemon.

## Ledger export

`docs/scrum/sprints/sprint19/evidence/*.jsonl` are `vg.4` envelopes straight
from the store, projectable with
`python3 tools/export_coding_session.py --jsonl <file>`.
`GREENFIELD-API-HTML.jsonl` is empty because no turn occurred — an empty file
is the honest export of a run that produced nothing.

## Not run

OpenRouter free and DeepSeek flash: `OPENROUTER_API_KEY` is not set. Dated skip,
not a fake green.
