---
id: rf95-candidate-07-preregistration
class: execution
authority: execution
canonical_for:
  - rf95-candidate-07
status: frozen
owner: dev-a
version: "1.0.0"
last_verified: 2026-08-28
subordinate_to: ../../../VISION.md
supersedes: []
superseded_by: null
---

# RF-95 candidate 07 — preregistration

## Why a seventh candidate exists

`candidate-06` (`docs/03_execution/prereg/RF-95-candidate-06.md`) authorized
`z-ai/glm-5.2:free` and was attempted twice, both times terminating at turn 0 with
`EpisodeCompleted{outcome: instrument_error, detail: "provider returned HTTP 429 after 4 attempts"}`
— a durable, honestly-classified ledger fact, not a task failure. Free-tier OpenRouter routes are
rate-limited upstream in a way this environment does not control; neither attempt reached the
agent loop, so `candidate-06`'s predicate was never evaluated and stays `undeterminable`/not
reached. Its ledgers are preserved as run evidence of the instrument condition, not as RF-95
bundles (an `instrument_error` at turn 0 does not satisfy any RF-95 clause and is not published as
a milestone bundle).

This document changes exactly one field from `candidate-06`: the model route, from a free-tier
route to a paid, non-rate-limited route the operator has funded for this purpose. Fixture,
verifier, task, and success predicate are byte-identical to every prior candidate.

## Frozen subject

| Field | Value |
|---|---|
| Fixture | `tools/runners/run_rf95_product_proof.py::setup_rf95_fixture` (byte-identical calculator fixture used by every prior candidate) |
| Composition | `vanguard/packages/agency/manifests/vg-code-default/manifest.json` |
| Profile | `product` (`sqlite-wal` persistence) |
| Model route | `deepseek/deepseek-v4-flash-0731` (OpenRouter, live, attributable, paid, registry `default_paid_model`) |
| Provider | OpenRouter |

## Task, success predicate, invalidation conditions

Unchanged from every prior candidate:

1. A live attributable provider is used, and its model route enters `D_R`.
2. The run goes through canonical composition and the `product` execution profile.
3. At least one repository observation, one authorized file mutation, and one process
   verification occur as mediated effects.
4. The workspace diff is non-empty and contains `return a * b`.
5. `python3 -m unittest discover -s tests` exits `0` in the workspace.
6. A file-backed SQLite-WAL ledger holds a complete terminal `mhf.trajectory/2`.
7. A fresh process reopens that ledger and reconstructs the same terminal state digest.

Invalidation conditions, none waivable: a fake/scripted/cassette provider; an alternate execution
driver; a hand-edited event, stitched trace, or manual ledger repair; incomplete capture;
in-process rather than fresh-process reconstruction; or modification of the fixture or verifier
after freezing.

## Independence

Producer key: `dev-a-evidence-1`. Acceptance requires a separate signed envelope from
`aether-evidence-reviewer-1`, a registered reviewer identity distinct from the producer. See
`candidate-06`'s honesty note: both keys are, in this environment, held by the same operator who
requested this run, so acceptance is mechanically valid and operator-attested but not
organizationally independent until a genuinely separate party re-signs it.
