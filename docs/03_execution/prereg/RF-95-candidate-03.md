---
id: rf95-candidate-03-preregistration
class: execution
authority: execution
canonical_for:
  - rf95-candidate-03
status: frozen
owner: dev-a
version: "1.0.0"
last_verified: 2026-08-27
subordinate_to: ../../../VISION.md
supersedes: []
superseded_by: null
---

# RF-95 candidate 03 — preregistration (final authorized attempt)

## Why a third candidate exists

Both prior candidates returned **`UNDETERMINABLE`**, for two *different* and
separately diagnosed instrument defects. Neither evaluated the success
predicate, and neither is reused:

| Candidate | Terminal | Diagnosis |
|---|---|---|
| 01 (`5fee014`) | `instrument_error`, turn 0 | `provider returned HTTP 404` — route `anthropic/claude-3.5-sonnet` retired upstream |
| 02 (`9b0622c`) | `instrument_error` | `provider returned HTTP 402` — `anthropic/claude-sonnet-4.5` declares a 1,000,000-token context, and the provider reserves credit against that window, so the request is refused as unaffordable while $4.13 remains |

Candidate 02 did reach the agent, which produced a correct workspace diff
(`return a * b`) and a passing test suite. It nonetheless failed to reach a
terminal `completed` state and never emitted a mediated `proc.exec`
verification receipt, so its predicate is **not** satisfied and it is not
recorded as a pass.

## The honesty constraint on this document

Three preregistrations in one session is exactly the pattern that, left
unchecked, becomes drawing until a pass appears. Two things bound it:

1. **The predicate has never moved.** The fixture and verifier digests below
   are byte-identical across all three candidates. Every change has been to
   the instrument, and each was diagnosed from a durable ledger fact before
   being changed — not inferred from a disappointing result.
2. **This is the final authorized attempt.** If candidate 03 also returns
   `UNDETERMINABLE`, M-4 stays `OPEN`, the instrument is declared unfit in
   this environment, and the blocker is escalated to Leadership. No candidate
   04 is authorized by this document.

## Frozen subject

| Field | Value |
|---|---|
| Commit | `9b0622c` plus the WP-A1 working tree |
| Composition | `vanguard/packages/agency/manifests/vg-code-default/manifest.json` |
| Profile | `product` (`sqlite-wal` persistence) |
| Fixture digest | `sha256:21df5eaa24b9852fd6974f07d610e556121f4798edaab5830b4c43d698995294` |
| Verifier digest | `sha256:3c96abbc30d380d6ebc36bac82938b3790df8ddc7d1ef511c39d01326e80d1fb` |
| **Model route** | **`deepseek/deepseek-chat`** (the only changed field) |
| Provider | OpenRouter, live and attributable |

`deepseek/deepseek-chat` is selected on one criterion only: a 163,840-token
context, small enough that the provider's credit reservation cannot exceed
the remaining balance. It is a live, attributable, non-cassette provider, so
it satisfies RF-95's provider clause exactly as the previous pins did.

## Task, success predicate, invalidation conditions

Unchanged and unchangeable. The run passes only if **every** clause holds:

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

## Known defect this run does not repair

Candidate 02's ledger shows the agent re-proposing an already-applied
`patch.apply` roughly fifteen times, each reconciled as
`patch context not found in src/calc.py: no location match`. The workspace was
already correct; the agent could not tell "my patch failed" from "my patch
already succeeded", and burned its turn budget on the difference.

That is a real defect in the repair/feedback path, and it is recorded here
rather than fixed, because it lives in the agency loop and WP-A1's authorized
surface is delegation. It is reported to Leadership as a separate finding. It
is *not* a licence to loosen this predicate: if it prevents a terminal
`completed`, this candidate fails or is undeterminable on its own terms.

## Independence

Producer: Dev A. Acceptance requires a separate signed envelope from a
reviewer who is not Dev A.
