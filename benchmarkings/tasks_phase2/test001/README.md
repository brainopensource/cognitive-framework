# Phase 2 benchmark — test001

This is an append-only preregistered coding task for the Vanguard Beta path.
It is intentionally small: a one-file pure-function boundary defect with
deterministic public tests and evaluator-only oracle cases.

## Task contract

- **Initial repository:** `fixture/initial/`
- **Model-visible prompt:** “Fix `slugify.slugify` so that the returned slug
  never ends in a separator after its `max_length` boundary. Preserve the
  documented handling of ordinary punctuation, whitespace and empty input.”
- **Allowed model tools:** `fs.read`, `fs.search`, `patch.apply`, `proc.test`
- **Allowed source change:** `fixture/initial/slugify.py` only
- **Public command:** `python3 -m unittest discover -s tests`
- **Expected initial status:** failing
- **Final acceptance:** public tests and the evaluator-only oracle pass;
  the final patch changes only the permitted source file.

The model sees the task repository and public tests but never `oracle/`.
No fixed patch or answer is stored in the model-visible task. The oracle is
made available only to the exterior evaluator after terminal ledger evidence.

## Preregistered live-canary limits

| Field | Value |
|---|---:|
| Requested model | `openrouter/free` |
| Maximum model calls | 3 |
| Maximum prompt tokens | 4,000 |
| Maximum completion tokens | 1,000 |
| Maximum wall time | 120 seconds |
| Maximum model output bytes | 65,536 |
| Human source edits | 0 |

`openrouter/free` is a variable router. A provider-unavailable, missing-key or
rate-limit outcome is an instrument failure, never a pass and never a model
fallback. The provider-resolved identity, source label, limits, event hashes,
sanitized diff and evaluation result must be captured in a new `runs/<run-id>`
directory by the protected release runner.

## Immutability and future tasks

Do not edit `fixture/initial/` after a run is preregistered. Do not overwrite
an existing run directory. Every attempt receives a new sortable UUID or UTC
timestamp path below `runs/`; later tasks are siblings named `test002`,
`test003`, and so on. The empty `runs/` directory is retained with `.gitkeep`
until the first sealed run artifact exists.

## Current state

The fixture's public test is deliberately failing. It has **not** been run by
the installed Vanguard product path, so it is not dogfood evidence and cannot
close R7, R8 or R9.
