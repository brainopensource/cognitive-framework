# S21-A — The greenfield zero-turn, named

**Date:** 2026-08-17 · `REQ-TRUST-001` · **No lift. No Q2. Nothing paid.**

## S21-A-01 — hypotheses falsified, one cause found

Measured against `lab/tasks/greenfield-api-html`:

| Hypothesis | Result |
|---|---|
| compose refuses an empty tree | **false** — composes, 11 tools, 4 verbs |
| IndexPort/map on empty tree | **false** — `index_component` is `None`; no index is bound |
| `TASK.md` not bound | **false** — bound, 248 chars |
| brief needs an `AGENTS.md` that 404s | **false** — `AGENTS.md` present |
| model called with zero tools | **false** — 11 tool schemas sent |
| `max_turns` 0 | **false** — run with `max_turns=4` |

**Cause: `instrument_error:multi_action_proposal`.** The model emits several
tool calls in one turn; the translator refuses because one turn is one effect.
The refusal is correct. What was wrong was calling it `instrument_error` — the
same word used when a provider never answers, when a daemon times out, and when
a workspace is missing. Each read like the model scoring zero.

Outcomes are now `instrument_error:<cause>`:
`multi_action_proposal`, `provider_timeout`, `model_tag_absent`,
`provider_unreachable`, `provider_key_missing`, `paid_model_refused`,
`provider_server_error`, `malformed_proposal`, `undeclared_tool`,
`tape_exhausted`, `model_not_invoked`, and `unclassified` for anything unseen —
inventing a category for a message nobody has seen is how a taxonomy starts
lying. Every one stays in the denominator.

## S21-A-02 — the loop does run on an empty workspace

MOCK on greenfield: **4 turns**, `attempts_exhausted`. The empty tree is not
skipped and greenfield is a valid workspace.

`turns=0` on the live run is **not a driver bug**, and it points at a named
line: `agency/episode/engine.py:235-245` terminates on a failed or malformed
proposal **before** `_emit_proposal`, so a refused proposal reaches no ledger
event. The model answered, the harness refused, and the refusal left no trace.

**This is a ledger-completeness gap for whoever owns `engine.py`** (`A-07`:
everything is an event). A refused proposal should be a recorded turn with a
receipt. I did not edit it — `engine.py` is out of my write scope.

## S21-A-03 — live tool-calling turns

`ollama:llama3.2:3b`, pack prompt unmodified. **Measured tool-call rate: 4/6**
single-shot runs on DOGFOOD-01. Verbs observed live: `fs.search`,
`patch.apply`, `proc.exec`.

The test gives the model 3 independent runs and fails if none tool-calls.
Retrying until green would be padding; a single shot would assert determinism
this model does not have. When the daemon is down it skips closed.

## Two more instrument defects fixed

1. **Duplicate ledger sequences across attempts.** Every attempt built a new
   session over the same `episode_id`, restarting the sequence counter, and
   `reduce_event` correctly refused with `Non-monotonic sequence`. An attempt
   starts from the workspace as it stands, so it is now its own episode; the
   run id groups them and the JSONL exports by run.
2. **A completed run reported `model_not_invoked`.** `HarnessSession` derives
   that from "this episode recorded no turn" — a fair proxy for a run that
   never started, a false positive for one that completed. The terminal now
   wins over the proxy.

Evidence JSONL in this directory; project with
`python3 tools/export_coding_session.py --jsonl <file>`.
