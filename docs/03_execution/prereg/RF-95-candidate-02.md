---
id: rf95-candidate-02-preregistration
class: execution
authority: execution
canonical_for:
  - rf95-candidate-02
status: frozen
owner: dev-a
version: "1.0.0"
last_verified: 2026-08-27
subordinate_to: ../../../VISION.md
supersedes: []
superseded_by: null
---

# RF-95 candidate 02 — preregistration

## Why a second candidate exists

Candidate 01 (`RF-95-candidate-01.md`, frozen at `5fee014`) executed and
returned **`UNDETERMINABLE`**, not a negative result. The ledger records
`EpisodeCompleted` with `outcome: instrument_error` and
`detail: "provider returned HTTP 404"` at **turn 0**: the pinned model route
`anthropic/claude-3.5-sonnet` had been retired upstream, so the provider was
never reached and the agent never acted.

That distinction is the whole reason this is a second preregistration rather
than a re-run of the first. `ADR-0101 §4` and `docs/01_law/EVIDENCE.md` are
explicit that a negative scientific result may close a preregistered
experiment, while **invalid instrumentation cannot**. Candidate 01's success
predicate was never evaluated, so it was neither passed nor failed. Candidate
01 is not reusable by its own terms, and it is not reused: it is recorded as
`UNDETERMINABLE` and retained as history.

This is *not* a retry until the answer is pleasant. Nothing about the task,
the fixture, the verifier, or the success predicate has changed — all four are
byte-identical to candidate 01, and their digests below are unchanged. The
single delta is the model route pin, which is the instrument that failed.

## Frozen subject

| Field | Value |
|---|---|
| Commit | `5fee014` plus the WP-A1 working tree |
| Branch | `feat_higgs_M4_M8` |
| Composition | `vanguard/packages/agency/manifests/vg-code-default/manifest.json` |
| Profile | `product` (`sqlite-wal` persistence) |
| Runner | `tools/runners/run_rf95_product_proof.py` |
| Fixture digest | `sha256:21df5eaa24b9852fd6974f07d610e556121f4798edaab5830b4c43d698995294` |
| Verifier digest | `sha256:3c96abbc30d380d6ebc36bac82938b3790df8ddc7d1ef511c39d01326e80d1fb` |
| **Model route** | **`anthropic/claude-sonnet-4.5`** (the only changed field) |
| Provider | OpenRouter, live and attributable |

The fixture and verifier digests are **identical to candidate 01**. That is
the check that matters here: it is what demonstrates the predicate was not
loosened between attempts.

## Task, success predicate, and invalidation conditions

Unchanged from candidate 01 in full. Reproduced so this document stands alone:

The fixture is a three-file git repository whose `src/calc.py` contains a
planted defect (`multiply` returns `0`). The run passes only if **every**
clause holds:

1. A live attributable provider is used, and its model route enters `D_R`.
2. The run goes through canonical composition and the product execution profile.
3. At least one repository observation, one authorized file mutation, and one
   process verification occur as mediated effects.
4. The workspace diff is non-empty and contains `return a * b`.
5. `python3 -m unittest discover -s tests` exits `0` in the workspace.
6. A file-backed SQLite-WAL ledger holds a complete terminal `mhf.trajectory/2`.
7. A **fresh process** reopens that ledger and reconstructs the same terminal
   state digest.

Invalidation conditions, none waivable: a fake/scripted/cassette provider; an
alternate execution driver; a hand-edited event, stitched trace, or manual
ledger repair; incomplete capture; in-process rather than fresh-process
reconstruction; or modification of the fixture or verifier after freezing.

## Declared outcome handling

A run that reaches the agent and fails the predicate is a **failure**, recorded
as one, and closes this candidate: M-4 stays `OPEN` and any further attempt
needs a third preregistration.

A run that dies before the agent acts is **`UNDETERMINABLE`**, as candidate 01
was. Repeated undeterminable outcomes are a signal that the instrument is
broken and must be repaired and re-preregistered — never a licence to keep
drawing until a pass appears.

## Independence

Producer: Dev A. Acceptance requires a separate signed envelope from a
reviewer who is not Dev A. This document confers no acceptance.
