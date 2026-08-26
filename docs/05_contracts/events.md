---
status: living
id: contract-events
class: contract-reference
authority: descriptive
canonical_for:
  - event-envelope-contract
source_of_truth:
  - docs/SPEC.md
  - docs/02_decisions/0071-authority-state-ledger-identity-trinity.md
derived_from:
  - schemas/mhf/event_envelope.schema.json
  - vanguard/packages/domain/ledger/events.py
  - vanguard/packages/runtime/ledger_emitter.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Event Envelope Contract (`mhf.event/1` and `/2`)

> **Schemas:** [`event_envelope.schema.json`](../../schemas/mhf/event_envelope.schema.json) and
> [`event_envelope_v2.schema.json`](../../schemas/mhf/event_envelope_v2.schema.json)
> **Status:** `/1` readable and byte-frozen; `/2` single-write migration under ADR-0098.

---

## Structure & fields

The wire schema requires `schema_version`, `event_id`, `kind`, `seq`, `occurred_at`, `run_id`,
`principal`, `payload`, and `digest`. Optional lineage includes episode/principal ancestry,
`project_id`, `harness_digest`, branch, previous digest, causation, correlation, and idempotency.
The richer domain envelope also carries scope, ownership, confidentiality, retention,
trainability, and redaction data. The schema and parser are the exact references; this page does
not duplicate a sample that could silently drift.

`mhf.event/2` adds exactly four typed authority fields: `authority_source` and `policy_version`
are required strings; `approval_reference` and `capability_grant` are nullable references. The
reader keeps `/1` authority absent rather than inventing defaults, and mixed `/1` → `/2` chains
preserve `prev_digest` continuity.

## Semantic projection kinds

The M-5a semantic roster is fixed by ADR-0098. Payload schemas and generated types are the source
for field shape; `AgentView` is a projection over the canonical ledger reducer, never a second
source of truth.

| Kind | Required payload identity | Projection effect |
|---|---|---|
| `GoalDeclared` | `goalDigest` | latest goal identity |
| `PlanRevised` | `revision`, `planDigest` | append ordered plan revision |
| `StrategyChanged` | `from`, `to`, `trigger` | update strategy history |
| `ProgressAssessed` | `assessment`, `signals`, `basis` | append progress assessment |
| `ContextCompacted` | `inputDigest`, `outputDigest` | advance context epoch |

The following historical kinds remain readable but are unwritable: `ObservationRequested`,
`OperatorInvoked`, `OperatorSelected`, `CorrectionRecorded`, `CandidateBuilt`,
`CandidateAttested`, `CanaryPromoted`, and `RollbackTriggered`.

## Writer Authority Matrix

`runtime/ledger_emitter.py:PRIVILEGED_KIND_OWNERS` is the executable ownership table. It assigns
capability, budget, effect, authorization, and alarm events to `kernel`; `VerdictRecorded` to
`evaluator_gateway`; plugin lifecycle events to `registry`; `ApprovalResolved` to `approval`; and
`EffectReconciled` to `kernel` or `recovery`. Unlisted ordinary events still require a recognized
writer role and canonical emission path.
