# Zero-hint live coding tasks (v1)

Sibling of `tasks_phase2/` and `tasks_phase2_LAM/`. Those trees are **not**
modified. This suite is for proving whether `vg-code-default` can repair a
repository with a **live** LLM (OpenRouter or local OpenAI-compatible), not
LAM cassette replay and not single-shot `generate()`.

## What the model may see

Copied into the episode workspace:

- `fixture/initial/**` only (source + public tests)

Never copied into the workspace:

- `oracle/`
- `prompt.txt` is passed as the episode brief, not as a file
- this README, `preregistration.json`, and `runs/`

Public tests encode **required behaviour**. They do not name the algorithm,
the one-line patch, or a golden implementation. Source files contain no
FIXME/TODO pointing at the defect.

## Tasks

| Id | Shape | Public command |
|---|---|---|
| `test002_rate_window` | per-key request admission over a time window | `python3 -m unittest discover -s tests` |
| `test003_invoice_cents` | invoice totals in integer cents | `python3 -m unittest discover -s tests` |
| `test004_busy_merge` | merge closed busy intervals | `python3 -m unittest discover -s tests` |
| `test005_named_amounts` | two-module parse + aggregate (multi-file) | `python3 -m unittest discover -s tests` |

Paired DNA protocol: `PAIRING.md`. Packs: `--manifest vg-code-default` (default) or `vg-shell-only`.

## Honest status of the product path

`Runtime.execute_harness` is the production loop (L1–L5, grants, Bubblewrap
worker, descriptor-bound patch approval). Dogfood in-tree still uses LAM.
`tasks_phase2_LAM/test001/run_*.py` calls the router **without tools**.

This runner uses the production loop with a live provider model. Lab-only
departures, recorded in each `runs/<id>/result.json`:

1. Auto-approval of privileged diffs (no human in the loop).
2. Oracle evaluation after the episode, not IsolatedEvaluator UID 10002.
3. `maxTokens` raised from the adapter default of 256. Pack tool `schema` fields are data, not a runner inject.

## How to run a live episode

From the repo root (WSL). Oracle files are not copied into the workspace.

```bash
python3 benchmarkings/zero_hint_v1/run_live_agent.py --check-fixtures
python3 benchmarkings/zero_hint_v1/run_live_agent.py \
  --task test005_named_amounts \
  --manifest vg-code-default \
  --model ollama/llama3.2:3b \
  --max-turns 8
```

`--model` may be `ollama/<tag>` or an OpenRouter id. Artifacts land in
`tasks/<id>/runs/<utc>/` (`result.json`, `final.diff`, test tails).

## Live evidence already captured (2026-08-16)

These are **not** task passes. They are evidence that the production loop
called a real model and executed real tools inside Bubblewrap.

| Task | Model | Terminal | Tools that ran |
|---|---|---|---|
| `test004_busy_merge` | `llama3.2:3b` | `abandoned` (16-turn bound) | `fs.search`, then 13× `fs.read` of `busy.py` |
| `test003_invoice_cents` | `llama3.2:3b` | `abandoned` (10-turn bound) | `fs.search`, then 9× `fs.read` of `invoicing.py` |
| `test004_busy_merge` | `qwen3.6:27b` | `instrument_error` (provider timeout on turn 2) | `fs.search` |

No live run applied a `patch.apply` that made public tests green. Small local
models looped on read. 27B searched then exceeded HTTP time. OpenRouter
`google/gemini-2.0-flash-001` returned HTTP 404; `deepseek/deepseek-chat`
returned an empty completion.

`test002_rate_window` is preregistered and gold-checked; it has not had a live
episode yet.
