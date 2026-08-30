---
id: ref.events
canonical_id: ref.events
class: reference
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: domain-ledger
canonical_for:
  - event envelope contract
  - event-kind roster link/catalog
  - writer ownership
  - sequence/digest semantics
purpose: Own event versions, kinds, envelope fields, writer roles and ordering semantics.
audience:
  - operator
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-008
  - E-B-009
  - E-B-013
  - E-B-027
  - E-B-028
relationships:
  - arch.state.causal
  - arch.trust.kernel
  - ref.schemas
reviewer: documentation-specialist
confidence: high
---

# Event Substrate & Envelope Reference

## Purpose
This document is the canonical reference owner for the event envelope wire schema, event-kind classifications, privileged writer role authorizations, hash-chaining digest mechanics, and dual-version reader compatibility.

## Scope
- `EventEnvelope` data structures and schema fields (`mhf.event/1` and `mhf.event/2`).
- The canonical catalog of writable and deprecated event kinds.
- Privileged writer role mappings (`PRIVILEGED_KIND_OWNERS` and `ROLE_AUTHORITY_SOURCES`).
- Monotonic sequence numbers, causal timestamps, and SHA-256 hash-chaining.
- Reader compatibility for legacy VG-04 event streams.

## Non-responsibilities
- High-level event-sourcing lifecycle narrative (owned by [`arch.state.causal`](../architecture/causal-state.md)).
- State projection folding algorithms (owned by [`arch.state.causal`](../architecture/causal-state.md)).
- Kernel effect dispatch mechanics (owned by [`arch.trust.kernel`](../architecture/kernel.md)).

## AS_BUILT Status
- `IMPLEMENTED` — The `mhf.event/2` event envelope is the sole active production write version, supported by strict role-scoped emitters and deterministic canonicalization.

---

## 1. Schema Versions

| Version | Authority & Usage | Status |
|---|---|---|
| `mhf.event/2` | Active production write version (`EVENT_SCHEMA_VERSION`). Enforces role-scoped writer validation and full lineage binding. | `IMPLEMENTED` (Active) |
| `mhf.event/1` | Historical frozen envelope format. Supported indefinitely for reading past ledgers. | `IMPLEMENTED` (Dual-read only) |
| `VG-04` (Legacy) | Pre-MHF event wire formats. Handled via compatibility normalizers. | `OBSOLETE` (Historical) |

---

## 2. Event Envelope Wire Contract

An `EventEnvelope` (`vanguard/packages/domain/ledger/events.py`) contains the following canonical fields:

```json
{
  "api": "mhf.event/2",
  "event_id": "018f3a9a-7c20-7000-8000-000000000001",
  "sequence": 42,
  "kind": "EffectStarted",
  "timestamp": "2026-08-29T20:00:00.000000Z",
  "run_id": "018f3a9a-7c20-7000-8000-000000000000",
  "episode_id": "018f3a9a-7c20-7000-8000-000000000000",
  "scope": "episode",
  "principal_id": "principal:kernel:0",
  "principal_role": "kernel",
  "parent_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "digest": "d41d8cd98f00b204e9800998ecf8427e00000000000000000000000000000000",
  "payload": { ... },
  "metadata": {
    "confidentiality": "internal",
    "retention": "standard",
    "trainability": "prohibited",
    "redaction_status": "none"
  }
}
```

### Field Definitions

| Field | Type | Description |
|---|---|---|
| `api` | `string` | Envelope version identifier (`"mhf.event/2"`). |
| `event_id` | `string` (UUIDv7) | Universally unique, time-ordered identifier for this event. |
| `sequence` | `integer` ($\ge 0$) | Zero-indexed strictly monotonic event sequence within the run ledger. |
| `kind` | `string` | Past-tense verb phrase identifying the event kind. |
| `timestamp` | `string` (RFC 3339) | UTC timestamp of event emission. |
| `run_id` | `string` (UUIDv7) | Target run identifier. |
| `episode_id` | `string` (UUIDv7) | Scoped episode identifier (required for `scope="episode"`). |
| `scope` | `string` | Boundary domain: `"episode"`, `"governance"`, `"evolution"`, or `"recovery"`. |
| `principal_id` | `string` | Authenticated principal identifier emitting the event. |
| `principal_role` | `string` | Emitting role: `"kernel"`, `"session"`, `"evaluator"`, `"operator"`, `"process"`, `"user"`. |
| `parent_digest` | `string` (64-hex SHA-256) | Digest of the immediately preceding event envelope in the run. |
| `digest` | `string` (64-hex SHA-256) | Canonical JCS SHA-256 digest computed across this envelope (excluding `digest`). |
| `payload` | `object` | Event-specific data payload conforming to kind schema. |
| `metadata` | `object` | Governance classification (confidentiality, retention, trainability, redaction). |

---

## 3. Event Kinds and Privileged Writer Roles

Events must be emitted exclusively through `LedgerEmitter` via role-scoped facades. Direct unmediated writes are rejected (`INV-B-007`).

### Privileged Writer Role Mapping (`PRIVILEGED_KIND_OWNERS`)

| Event Kind | Authorized Writer Roles | Authority Source (`ROLE_AUTHORITY_SOURCES`) | Description |
|---|---|---|---|
| `CapabilityGranted` | `kernel` | `kernel-capability` | Capability lease created by kernel. |
| `CapabilityAttenuated` | `kernel` | `kernel-capability` | Child capability ceiling reduced. |
| `CapabilityRevoked` | `kernel` | `kernel-capability` | Capability lease terminated. |
| `BudgetReserved` | `kernel` | `kernel-capability` | Additive budget reserved for effect. |
| `BudgetCommitted` | `kernel` | `kernel-capability` | Budget debited after physical effect. |
| `BudgetReleased` | `kernel` | `kernel-capability` | Unused reserved budget refunded. |
| `BudgetExhausted` | `kernel` | `kernel-capability` | Run halted due to exhausted budget. |
| `EffectStarted` | `kernel` | `kernel-capability` | Intent recorded prior to physical I/O dispatch. |
| `EffectCompleted` | `kernel` | `kernel-capability` | Successful effect receipt and lease release. |
| `EffectFailed` | `kernel` | `kernel-capability` | Failed effect receipt recorded. |
| `EffectRejected` | `kernel` | `kernel-capability` | Effect denied by policy or classifier. |
| `EffectReconciled` | `kernel`, `recovery` | `recovery-policy` | Interrupted effect resolved during crash recovery. |
| `AuthorizationRequested`| `kernel` | `kernel-capability` | Effect paused pending human/operator approval. |
| `AuthorizationDenied` | `kernel` | `kernel-capability` | Operator rejected approval request. |
| `KernelAlarm` | `kernel` | `kernel-capability` | Trusted Computing Base security boundary alert. |
| `VerdictRecorded` | `evaluator_gateway` | `evaluator-signature` | Signed external evaluation verdict recorded. |
| `ChildSpawned` | `spawn_adapter` | `delegation-policy` | Mediated child episode instantiated. |
| `ChildReturned` | `spawn_adapter` | `delegation-policy` | Mediated child episode concluded. |
| `PluginDiscovered` | `registry` | `registry-policy` | Pack plugin candidate detected. |
| `PluginActivated` | `registry` | `registry-policy` | Pack plugin verified and loaded. |
| `PluginQuiesced` | `registry` | `registry-policy` | Pack plugin unloaded or deactivated. |
| `GoalDeclared` | `session` | `session-policy` | High-level execution goal established. |
| `PlanRevised` | `session` | `session-policy` | Plan steps updated. |
| `StrategyChanged` | `session` | `session-policy` | Agent strategy adjusted. |
| `ProgressAssessed` | `session` | `session-policy` | Goal progress evaluated. |
| `ContextCompacted` | `session` | `session-policy` | Context window compacted. |

### Deprecated Historical Kinds (`DEPRECATED_KINDS`)
The following kinds are frozen historical names from legacy specifications. They remain permanently readable by all readers to ensure past ledgers validate, but new writes are unconditionally rejected with `DeprecatedKindError`:
- `ObservationRequested`, `OperatorInvoked`, `OperatorSelected`, `CorrectionRecorded`, `CandidateBuilt`, `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered`.

---

## 4. Causal Ordering & Digest Chaining

Every event envelope establishes an immutable cryptographic chain:

1. **Monotonic Sequences**: `sequence` begins at `0` for the first event of a run and increments by `1` per event without gaps.
2. **Hash-Chain Preimage**: For event $N$, `parent_digest` must exactly equal the `digest` of event $N-1$. For event `0`, `parent_digest` is the genesis zero hash (`"0000000000000000000000000000000000000000000000000000000000000000"` or empty digest).
3. **Digest Canonicalization**: The `digest` is computed via RFC 8785 JSON Canonicalization Scheme (JCS) followed by SHA-256 hashing (`vanguard/packages/domain/canonicalisation/digest.py`).

---

## 5. Dual-Version Reader Compatibility

- `parse_event_envelope(data: Mapping[str, Any]) -> EventEnvelope`:
  - Automatically identifies whether payload is `mhf.event/1`, `mhf.event/2`, or legacy VG-04.
  - Normalizes legacy payloads into typed `EventEnvelope` instances in memory.
  - Preserves unknown extension payload fields under forward-compatibility rules without stripping unrecognized properties.

---

## Implementation Evidence

- **Domain Model**: `vanguard/packages/domain/ledger/events.py` (`EventEnvelope`, `parse_event_envelope`, `WRITABLE_KINDS`, `DEPRECATED_KINDS`).
- **Runtime Emitter**: `vanguard/packages/runtime/ledger_emitter.py` (`LedgerEmitter`, `RoleScopedEmitter`, `PRIVILEGED_KIND_OWNERS`, `ROLE_AUTHORITY_SOURCES`).
- **Canonical Digest**: `vanguard/packages/domain/canonicalisation/digest.py`, `vanguard/packages/domain/canonicalisation/jcs.py`.
- **Envelope Schemas**: `schemas/mhf/event_envelope.schema.json`, `schemas/v4/event-envelope.schema.json`.
- **Contract Tests**: `test/contracts/test_event_substrate_v2.py`, `test/contracts/test_event_store_port.py`, `test/test_ledger_properties.py`.
