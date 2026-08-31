# vg-code-max-v3 — root-cause findings from live qualification

All findings below were reproduced live against `deepseek/deepseek-v4-flash-0731`
through OpenRouter, with every model interaction recorded to a cassette under
`benchmarks/artifacts/ladder/`. Verdicts come from re-running each challenge's
own oracle in a subprocess after the agent finished.

## The prior conclusion was wrong

`.draft/CODING_MAX_BACKEND_HANDOFF_2026-08-31.md` concluded the blocker was a
model-capability ceiling — "a textbook greedy-decoding repetition trap … may be
a hard ceiling of these flash checkpoints" — and shipped sampling mitigations
that did not work.

That is falsified. Sending the **exact recorded prompt and tools** straight to
the OpenRouter endpoint returns the correct call every time:

```
read {"path": "lru/cache.py"}
read {"path": "lru/entry.py"}
```

9/9 raw probes correct, with and without tool descriptions, with and without
`reasoning_effort`. The model was never the problem. Six harness defects were.

## D1 — the prompt the model received was not the prompt that was assembled

`PromptAssembler` publishes `bundle["messages"]` as a **tuple**;
`openrouter._messages()` short-circuited on `isinstance(..., list)` only. A tuple
failed that check, so every live turn silently fell through to a lossy `blocks`
rendering — discarding the assembled conversation, the tool-call structure, and
the protocol-recovery feedback.

This is why replaying a recorded cassette "worked" while the live run failed:
JSON round-tripping turns the tuple into a list, so replay took the correct
branch that production never took.

**Fix:** accept any non-str sequence. `adapters/models/openrouter.py`.

## D2 — the run could not terminate successfully

A `finish` proposal is only produced when the model emits plain text with no
tool call (`invocation.py:81`). The phase ladder sets `tool_choice="required"`
on every turn, which obliges a tool call. Under the phase ladder a run was
therefore **structurally incapable of completing** — it could only end in
`abandoned` or an error. This alone explains the historical all-`abandoned`
results.

**Fix:** an explicit `finish` tool (`agency.finish`), declared in the manifest,
allowed in every phase, and mapped to a finish proposal by the translator.

## D3 — episode memory was destroyed on every approval round-trip

`session.py` rebuilds a fresh `EpisodeEngine` with an empty `Episode` after each
approval suspension. Since `patch.apply` and `proc.exec` are approval-gated,
this happened nearly every turn. Consequences: turn indices restarted at 0
(`tool result turn=0` forever), and no-progress detection could never accumulate
two consecutive turns.

**Fix:** `engine.run(prior_turns=...)`, threaded through the session re-entry
loop; `max_turns` re-based so the bound stays a bound on the episode.

## D4 — phase state was destroyed the same way

`seen_verbs` drives the phase ladder and was also engine-local. `_record()` calls
`calls.clear()`, so the re-entry seeding was empty too. The phase snapped back to
`inspect` mid-run and **un-offered the `patch` tool on the turn right after a
patch**, producing `tool is not declared by manifest: patch`.

**Fix:** `prior_seen_verbs`, accumulated in a session-level set that `_record`
does not clear.

## D5 — the completion gate never saw the patch it had just applied

After approval, the effect is re-dispatched directly (`K-14`) and bypasses the
engine's turn callback — the only path that fed `_observe_completion_dispatch`.
So `_completion_changed_files` stayed empty and the admission gate rejected
every `finish` with `MISSING_SOURCE_PATCH`, even with both files correctly
patched and the oracle green.

**Fix:** observe the approved dispatch explicitly in the re-entry path.

## D6 — tool descriptions were dropped on the wire

`_tools_payload` emitted only `name` and `parameters`. Every manifest tool
description was decorative in the native tool-calling payload. Not the cause of
the failure (probes were 6/6 correct either way) but a real defect.

**Fix:** send `description`.

## Secondary fixes

- **Livelock detector was dead.** `Turn.signature` included `state_digest`,
  which digests the *growing* turn history, so no two turns could ever match and
  `Episode.repeats()` was unsatisfiable. `state_digest` removed from the
  signature; the field is retained.
- **Repeat counting is signature-based over a window.** Livelock is "the outcome
  stopped changing", not "the outcome was ok" — real runs repeat with
  `approval_suspended`, not `ok`. A window rather than a strict consecutive run,
  because a nudged model varies for one turn and falls straight back.
- **Tool set is no longer filtered per phase.** The adapter resolves a tool name
  against the list it was offered, so filtering turned a recoverable phase
  violation into a fatal undeclared-tool error. The full set is offered and the
  existing bounded phase gate handles violations. Also keeps the cached prefix
  stable.
- **Admission gating is capability-derived**, not a hardcoded preset allowlist,
  so a new preset cannot silently ship ungated.
- **Broken `cryptography` install** (native module missing, stubs only) was
  masking 118 test errors; reinstalled 50.0.0 -> 50.0.1.

## Still open

- The model often re-runs a passing test instead of calling `finish`, so runs
  that pass the oracle can still end `abandoned`. The nudge now points at
  completion and the prompt is explicit; not fully resolved.
- Observation outcomes carry an all-zero `result_digest`, so `justifying_receipt`
  lines are noise and observation receipts cannot witness change.
- `_schemas_with_aliases` exposes each verb twice (`read` and `fs.read`),
  doubling the tool payload.
