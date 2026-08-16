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

## Honest status of the product path

`Runtime.execute_harness` is the production loop (L1–L5, grants, Bubblewrap
worker, descriptor-bound patch approval). Dogfood in-tree still uses LAM.
`tasks_phase2_LAM/test001/run_*.py` calls the router **without tools**.

This runner uses the production loop with a live `OpenRouterModel`. Lab-only
departures, recorded in each `runs/<id>/result.json`:

1. Auto-approval of privileged diffs (no human in the loop).
2. Oracle evaluation after the episode, not IsolatedEvaluator UID 10002.
3. Tool JSON parameters injected at the provider wire (pack files still omit
   `schema`; without that, most models cannot form valid calls).
4. `maxTokens` raised from the adapter default of 256.

A pass here is **agentic coding evidence**. It is not a Beta sellable-path
claim and does not mark REQ-* covered.
