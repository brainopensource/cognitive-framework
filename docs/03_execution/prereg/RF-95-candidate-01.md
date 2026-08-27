---
id: rf95-candidate-01-preregistration
class: execution
authority: execution
canonical_for:
  - rf95-candidate-01
status: frozen
owner: dev-a
version: "1.0.0"
last_verified: 2026-08-27
subordinate_to: ../../../VISION.md
supersedes: []
superseded_by: null
---

# RF-95 candidate 01 — preregistration

This document is **frozen before execution**. It exists so the run that follows
can only confirm or refute a claim that was already written down, rather than
having its success criteria discovered afterwards from whatever happened.

`sprint_active.md` "Immediate execution order" item 3 authorizes exactly one new
RF-95 candidate when the original bundle cannot be recovered, and ADR-0102 §7
forbids reconstructing the historical claim. This is that one candidate.

## Recovery attempt (precondition)

Before preregistering, the repository was searched for the reported historical
RF-95 bundle. Result: **absent**. There is no `aether.evidence/1` envelope, no
foundation-evidence bundle, and no independent M-4 review receipt anywhere in
the tree or in git history. This matches the finding already recorded in
ADR-0102 and in `sprint_active.md` "Verified baseline". No historical claim is
reconstructed, and this candidate makes no assertion about the original run.

## Frozen subject

| Field | Value |
|---|---|
| Commit | `6a51c182779c86988d02faaabf2536d2a9e1c2d2` |
| Tree | `c6d9b69769880557c62eda10d83fff4715e5b30d` |
| Branch | `feat_higgs_M4_M8` |
| Composition | `vanguard/packages/agency/manifests/vg-code-default/manifest.json` |
| Profile | `product` (`sqlite-wal` persistence) |
| Runner | `tools/runners/run_rf95_product_proof.py` |
| Fixture digest | `sha256:21df5eaa24b9852fd6974f07d610e556121f4798edaab5830b4c43d698995294` |
| Verifier digest | `sha256:3c96abbc30d380d6ebc36bac82938b3790df8ddc7d1ef511c39d01326e80d1fb` |

The fixture and the verifier are digest-pinned above precisely so that neither
can be adjusted after seeing the outcome. A change to either invalidates this
preregistration and requires a new one.

## Task

A three-file git repository containing `src/calc.py` with a planted defect:
`multiply(a, b)` returns `0`. `tests/test_calc.py` asserts `multiply(3, 4) == 12`
and therefore fails at the frozen commit. `TASK.md` states the objective in
prose. The agent must repair the defect through ordinary mediated tools.

## Success predicate

Declared in full, in advance. The run passes only if **every** clause holds:

1. A live attributable provider is used, and its model route enters `D_R`.
2. The run goes through canonical composition and the product execution profile.
3. At least one repository observation, one authorized file mutation, and one
   process verification occur as mediated effects.
4. The workspace diff is non-empty and contains `return a * b`.
5. `python3 -m unittest discover -s tests` exits `0` in the workspace.
6. A file-backed SQLite-WAL ledger exists and holds a complete terminal
   `mhf.trajectory/2`.
7. A **fresh process** reopens that ledger and reconstructs the same terminal
   state digest.

## Invalidation conditions

Any one of these denies the candidate outright, and none may be waived:

- a fake, scripted, or cassette model provider;
- an alternate execution driver, or any path other than `Runtime.run_composed`;
- a hand-edited event, a stitched trace, or any manual repair of the ledger;
- an incomplete capture (`capture_incomplete` makes the run non-evidentiary);
- reconstruction performed in-process rather than by a fresh process;
- modification of the fixture or the verifier after this document is frozen.

## Declared outcome handling

A failing run is recorded as a failing run. `ADR-0101 §4` admits negative and
undeterminable outcomes as legitimate evidence; what is inadmissible is
retrying until the result is pleasant, or narrowing the predicate after the
fact. If this candidate fails, M-4 stays `OPEN` and a *new* preregistration is
required before any further attempt — this document is not reusable.

## Independence

The producer of the resulting envelope is Dev A. Acceptance requires a
**separate** signed envelope from a reviewer who is not Dev A. This
preregistration does not and cannot confer acceptance.
