# harness_lab

Compile a harness from a manifest, run it against N model routes on one
zero-hint challenge, and print what the harness *did to* each turn.

Not a new engine. It calls `Runtime.compose` / `Runtime.execute_harness` — the
same composition root, kernel, approval flow and sandbox as every other suite
here. What it adds is a tracer at two seams a reader normally cannot see.

```
observe ──▶ propose ──▶ [translate] ──▶ authorize ──▶ effect ──▶ receipt
   │            │            │                                      │
 context     raw model    alias → canonical verb              outcome + stderr
 summary     tool call    args  → bound resource
```

## Layout

| Path | What it is |
|---|---|
| `harness/vg-mini-coder/` | A harness **built with the framework**: manifest + 3 tools + prompt + policies. Compiles to its own content-addressed digest. |
| `challenge/zero_hint_stats/` | One zero-hint task: fixture, public tests, held-out oracle, preregistration. |
| `profiles/` | Model routes. `_UNSUPPORTED.json` records probed models that cannot run this harness, so the negative result is not re-discovered. |
| `run_ab.py` | The runner + workflow tracer. |
| `runs/` | Append-only results. Each run writes `result.json` (with the full `workflow` array), `final.diff`, and any changed workspace files. |

## Run

```bash
OLLAMA_HOST=127.0.0.1:11434 python3 benchmarkings/harness_lab/run_ab.py \
  --task zero_hint_stats \
  --profile profiles/qwen25-coder-14b.json \
  --profile profiles/llama32-3b.json
```

`--harness NAME` overrides the harness the task names, which is how you A/B two
harnesses against one model instead of two models against one harness.

## Adding a harness

Copy `harness/vg-mini-coder/`, edit `manifest.json`. Component paths resolve
against the *parent* of the manifest directory, so they are prefixed with the
harness directory name. Capabilities are the grant ceiling: held authority is
their union, and a verb the manifest does not declare is denied, not inferred.

## Lab departures

Recorded in every `result.json`. Privileged effects are auto-approved by a lab
signer, the in-episode verifier is `SkipEvaluator`, and the oracle runs after
the episode in a copied tree rather than in the isolated evaluator daemon.
These are lab conditions, not the production evidence path — a run from here is
`lab-execute-harness` evidence and is not publishable as a signed verdict.
