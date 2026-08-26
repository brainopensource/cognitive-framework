---
id: adr-0098-event-substrate-v2-and-semantic-kind-roster
adr: 0098
class: decision
authority: binding-decision
canonical_for:
  - mhf-event-v2-envelope
  - m5a-semantic-kind-roster
  - deprecated-kind-register
  - m5a-baseline-identity
status: proposed
owner: engineering-leadership
version: "0.1.0"
last_verified: 2026-08-25
accepted_date: null
extends:
  - ADR-0096
  - ADR-0097
supersedes: []
superseded_by: null
---

# ADR-0098 — Event Substrate `/2` and the Semantic Kind Roster

## Status

**Proposed. Not accepted.**

ADR-0097 opens the ADR-0098 decision window only once M-4 is `CLOSED` on accepted RF-95 evidence.
At the time of drafting M-4 is **not** closed: RF-95 has not been executed, so the entry gate is
unmet and this ADR MUST NOT be treated as authorizing M-5a production implementation. It is drafted
now so the contract it freezes can be reviewed independently of the evidence that admits it.

Acceptance requires, in order: M-4 `CLOSED`; RF-95 accepted; a frozen M-4 append/fold benchmark;
and Leadership sign-off recorded on the active board.

## Context

M-4 proved the evidence path without touching the wire. Everything it could not say lives in the
gap this ADR closes.

`mhf.event/1` records *what happened* and never records *on whose authority*. A reader can see that
an effect completed; it cannot see whether the writer held capability authority, acted under a
policy version, or leaned on a human approval — so an orchestrator appending an event is
indistinguishable from a kernel appending the same event. That is the RF-99 gap.

Separately, `domain/ledger/events.py` carries `_V4_ONLY_KINDS`: sixteen kinds the generated wire
schema never knew about. Eight are live and reduced; eight are VG-04-normative and have never been
emitted by anything. The catalog is therefore two vocabularies that agree only by inspection, and
`LedgerEmitter` can write a kind the generated schema has no record of.

## Decision 1 — the `mhf.event/2` envelope

`/2` adds exactly four typed fields and changes nothing else:

| Field | Type | Nullable | Meaning |
|---|---|---|---|
| `authoritySource` | string | no | the writer role whose authority admitted this event |
| `policyVersion` | string | no | the policy version in force at append |
| `approvalReference` | string | yes | the human approval this event rests on |
| `capabilityGrant` | string | yes | the capability grant this event rests on |

`approvalReference` and `capabilityGrant` are null only when semantically inapplicable — never to
paper over an unknown. `/1` remains readable and unchanged; after cutover `/2` is the sole
production write version. Reader-side `/1` defaults are **projections only** and MUST NOT be
written back. `prev_digest` continuity is preserved across mixed `/1` and `/2` chains, and no
historical event or digest is ever rewritten.

## Decision 2 — role-consistent authority

Authority fields are populated from the actual writer role and the executed authority basis. A
forged or inconsistent value is rejected at append — specifically, an orchestrator claiming
capability authority it does not hold is refused, not recorded. This extends the existing
`PRIVILEGED_KIND_OWNERS` check from *which kinds a role may write* to *what a role may claim about
why*.

## Decision 3 — vocabulary convergence

The eight live legacy kinds fold into the generated schema:

`ActivationChanged`, `ArtifactCreated`, `CompetencePriorRecorded`, `ConflictDetected`,
`EffectPreviewed`, `EpisodeStateChanged`, `EvidenceClaimProduced`, `ObservationProduced`.

`_V4_ONLY_KINDS` is deleted. The generated schema becomes the sole live event-kind authority, which
removes the possibility of a second taxonomy drifting from the first.

## Decision 4 — deprecation, not deletion

These eight remain **readable** and reject all new writes:

`ObservationRequested`, `OperatorInvoked`, `OperatorSelected`, `CorrectionRecorded`,
`CandidateBuilt`, `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered`.

`DEPRECATED_KINDS` and `READABLE_KINDS` make the distinction explicit. Historical ledgers stay
readable forever; nothing new may claim these names. Reintroduction requires a full kind package —
ADR, allocation, writer, reducer, schema, golden vector, and coverage proof — never a one-line
addition to a set.

## Decision 5 — exactly five new semantic kinds

`GoalDeclared`, `PlanRevised`, `StrategyChanged`, `ProgressAssessed`, `ContextCompacted`.

Each arrives with an event allocation, payload schema, golden JCS vectors, writer ownership, a
generated type, reducer-coverage registration, and defined authority-field behaviour. No sixth kind
may enter without reopening this ADR **before** implementation.

`GoalDeclared` carries `goalDigest` and an optional digest-verified `goalArtifact`. Raw goal text
never enters the ledger: a goal may quote a secret, and an append-only store is the one place from
which nothing can be withdrawn.

## Decision 6 — resource semantics

Additive conserved resources are exactly `usd_micros`, `millis`, `tokens`, `bytes`. `depth` and
`turns` are independent structural ceilings and are never additive costs. `charged_millis` is not
introduced — a second time dimension whose relationship to `millis` is conventional rather than
conserved would make cost conservation unprovable.

## Decision 7 — compatibility, rollback, and the baseline

Mixed-version chains replay in a fresh process; old ledgers and deprecated events stay readable;
new writers emit only `/2`. Pre-baseline rollback uses an explicit writer-version switch;
post-baseline change requires a new ADR. The Kernel semantic diff MUST remain exactly zero.

On a green G-M5A gate, exactly one reviewed tag `M-5A-BASE-v2` is created. The historical
`M-5-BASE` tag is preserved at its existing commit and is never moved, replaced, or deleted.

## Falsifier obligations

`RF-96` fresh-process reconstruction including interrupted-mid-effect; `RF-97` transitive TCB
closure; `RF-99` authority provenance and mixed-chain replay; `RF-100` current-state reassessment
never overwriting run-close evidence.

## Consequences

Authority provenance expands every envelope by four fields, and the migration is the one authorized
substrate change in the ladder. Both costs are accepted because an event that cannot say on whose
authority it was written cannot support the delegation and recursion milestones that follow.

## Rejected alternatives

- **Adding authority as an untyped payload convention** — unenforceable, and invisible to schema.
- **Rewriting `/1` events in place** — destroys historical digests and the chain they anchor.
- **Keeping `_V4_ONLY_KINDS` alongside the generated schema** — preserves the two-vocabulary drift
  this ADR exists to end.
- **Deleting the eight unemitted historical kinds** — breaks readability of ledgers that legally
  contain them.
- **Admitting semantic kinds incrementally as needed** — makes the roster a moving target and
  defeats reducer-coverage proof.
- **Raw goal text in `GoalDeclared`** — unwithdrawable content in an append-only store.
