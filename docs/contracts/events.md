---
status: living
id: contract-events
class: contract-reference
authority: descriptive
canonical_for:
  - event-envelope-contract
source_of_truth:
  - docs/SPEC.md#2-ledger-as-truth
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

## Structure & Fields

Every causal event appended to the SQLite WAL ledger is wrapped in an immutable `EventEnvelope`:

```json
{
  "specversion": "mhf.event/1",
  "id": "018f23a4-8b1c-7f89-9a23-456789abcdef",
  "sequence": 42,
  "timestamp": "2026-08-21T21:00:00.000000Z",
  "kind": "EffectCompleted",
  "project_id": "proj-aether-core",
  "episode_id": "ep-001-turn-04",
  "causation_id": "018f23a4-8b1c-7f89-9a23-456789abcdee",
  "correlation_id": "018f23a4-8b1c-7f89-9a23-000000000001",
  "writer_role": "runtime",
  "payload": {
    "descriptor": "fs.write",
    "result_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "receipt_id": "rcpt-018f23a4"
  },
  "prev_digest": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
}
```

## Writer Authority Matrix

Privileged event kinds can only be emitted by authorized writer roles:
- **`kernel`**: `EffectAuthorized`, `CapabilityAttenuated`, `BudgetExhausted`
- **`evaluator_gateway`**: `VerdictRecorded` (requires valid Ed25519 signature)
- **`runtime`**: `RunStarted`, `RunRecovered`, `EpisodeCompleted`
