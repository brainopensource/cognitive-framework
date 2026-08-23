---
status: living
id: contract-events
class: contract-reference
authority: descriptive
canonical_for:
  - event-envelope-contract
source_of_truth:
  - docs/SPEC.md
  - docs/05_adr/0071-authority-state-ledger-identity-trinity.md
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
supersedes: []
superseded_by: null
---

# Event Envelope Contract (`mhf.event/1`)

> **Schema:** [`schemas/mhf/event_envelope.schema.json`](../../schemas/mhf/event_envelope.schema.json)  
> **Status:** `AS_BUILT` · Governed by ADR-0071 / ADR-0076.

---

## Structure & fields

The wire schema requires `schema_version`, `event_id`, `kind`, `seq`, `occurred_at`, `run_id`,
`principal`, `payload`, and `digest`. Optional lineage includes episode/principal ancestry,
`project_id`, `harness_digest`, branch, previous digest, causation, correlation, and idempotency.
The richer domain envelope also carries scope, ownership, confidentiality, retention,
trainability, and redaction data. The schema and parser are the exact references; this page does
not duplicate a sample that could silently drift.

## Writer Authority Matrix

`runtime/ledger_emitter.py:PRIVILEGED_KIND_OWNERS` is the executable ownership table. It assigns
capability, budget, effect, authorization, and alarm events to `kernel`; `VerdictRecorded` to
`evaluator_gateway`; plugin lifecycle events to `registry`; `ApprovalResolved` to `approval`; and
`EffectReconciled` to `kernel` or `recovery`. Unlisted ordinary events still require a recognized
writer role and canonical emission path.
