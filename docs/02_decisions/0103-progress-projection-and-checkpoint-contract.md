---
id: adr-0103-progress-projection-and-checkpoint-contract
adr: 0103
class: decision
authority: binding-decision
canonical_for:
  - progress-projection-contract
  - semantic-checkpoint-reference
  - m65-observation-seam
status: accepted
owner: engineering-leadership
version: "1.0.0"
last_verified: 2026-08-27
accepted_date: 2026-08-27
extends:
  - ADR-0089
  - ADR-0096
  - ADR-0101
supersedes: []
superseded_by: null
---

# ADR-0103 — Progress projection and semantic checkpoint contract

## Status

Accepted 2026-08-27. This freezes the shared contract `WP-A2` needs before it
may be implemented. It authorizes no M-6.5 feature work by itself.

## Context

`sprint_upcoming.md` gates `WP-A2` on two conditions: **WP-A1 merged**, and the
**progress/checkpoint contract frozen**. The first is satisfied (`ca683fd`).
The second was not, and the gap was not cosmetic:

- `ProgressProjection/2` and `SemanticCheckpointRef` appear in the `WP-A2`
  backlog contract but exist in **no ADR and no source file**. A grep of
  `docs/02_decisions/` and of `vanguard/packages/domain/ledger/progress.py`
  finds neither name.
- `sprint_active.md` requires that "shared schema or runtime interfaces are
  frozen by ADR before use". Implementing against an unfrozen interface is
  precisely how two developers produce incompatible halves of one seam.

`WP-B2`'s paired study consumes whatever `WP-A2` emits. If the projection's
shape moves after the study begins, the study's comparability is destroyed
retroactively and its result becomes `UNDETERMINABLE` — the same failure that
already invalidated the historical M-6.5 instrument. Freezing first is cheaper
than discovering that later.

## Decision

**1. `ProgressProjection/2` is a derived projection, never a fact.** It is
folded from the ledger and is rebuildable; it is never appended, never
authoritative, and never an input to authorization. It exposes exactly:
verified delta, failed/unknown rate, repeat entropy, novelty, normalized burn,
revision effectiveness, and calibrated uncertainty. Adding a field is a new
schema version, not an edit.

**2. `SemanticCheckpointRef` binds `(run_id, episode_id, epoch, attempt)`.**
Common random numbers in any downstream study bind to *this* reference, not to
a raw turn index. A turn index is not stable across retries, escalations, or
approval re-entry, so keying perturbations on it silently pairs
non-comparable states.

**3. The controller carries no authority.** A directive binds
controller/policy/input/reason/confidence digests and **may not** carry a
grant, a verb, a sink, or a budget key. This is the ADR-0089 separation
restated at the M-6.5 seam: the controller observes and proposes; the runtime
retains every authority-bearing collaborator.

**4. Controller-off is the default and the baseline.** Telemetry loss, a stale
epoch, an unknown subject, a missing basis, an uncalibrated sole signal, or
nondeterminism must leave the projection and the verdict unchanged. A run with
the controller disabled must be byte-identical to one where it was never
composed — the disabled path is a parity claim, and it is falsifiable.

**5. The projection cannot close a gate.** It is a projection under ADR-0101's
class separation, so it is never a receipt. Only a signed `aether.evidence/1`
envelope, independently accepted, closes M-6.5.

## Consequences

- `WP-A2` may proceed once C1 closes: its interface is now frozen.
- `WP-B2` may build its instrument against this contract without waiting for
  `WP-A2`'s implementation, because the shape is fixed here rather than
  discovered from the code.
- A change to any of the five decisions above requires a successor ADR and a
  falsifier. Implementation inconvenience is not authority (`milestones.md`
  compatibility anchors).

## Falsifiers

Allocated from the register in `INDEX.md`:

| ID | Claim |
|---|---|
| `RF-114` | A directive carrying a grant, verb, sink, or budget key is refused |
| `RF-115` | Controller-off produces byte-identical events and state digest |
| `RF-116` | A stale epoch or unknown subject leaves the verdict unchanged |
| `RF-117` | `SemanticCheckpointRef` is stable across retry and approval re-entry |

## Notes

This ADR records a decision. It does not authorize M-6.5 feature
implementation, which remains prohibited while C1 is the active sprint
(`sprint_active.md` "Prohibited scope").
