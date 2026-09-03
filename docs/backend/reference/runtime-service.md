---
id: ref.runtime-service
canonical_id: ref.runtime-service
class: reference
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: runtime-clients
canonical_for:
  - vg.4 frame contract
  - command payloads
  - error vocabulary
  - idempotency/CAS/stream semantics
  - known profile defect
purpose: Own exact vg.4 commands, frames, errors, sequencing and transport limits.
audience:
  - operator
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-005
  - E-B-044
  - E-B-045
  - E-B-046
  - E-B-048
  - E-B-049
  - E-B-052
relationships:
  - arch.interfaces.clients
  - ref.commands
  - ref.schemas
reviewer: documentation-specialist
confidence: high
---

# Runtime Service Protocol Reference (`vg.4`)

## Purpose
This document is the canonical reference owner for the `vg.4` JSON-RPC / IPC frame protocol, request/response payloads, error code definitions, concurrency guards, and stream semantics used by runtime daemons and client surfaces.

## Scope
- The four discriminated frame types: `CommandFrame`, `ReceiptFrame`, `EventFrame`, `ErrorFrame`.
- The 11 command payload specifications and argument schemas.
- Error codes, retry semantics, and error frame payloads.
- Sequence guards (`expectedSeq`), optimistic concurrency control (CAS), and stream subscriptions.
- Documented live `StartRun` profile default caveat (`UNR-B-001`).

## Non-responsibilities
- CLI command invocation and user experience (owned by [`ref.commands`](commands.md)).
- Core runtime execution and composition internals (owned by [`arch.runtime.execution`](../architecture/runtime-execution.md)).
- Governance and approval cryptographic design (owned by [`arch.trust.kernel`](../architecture/kernel.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Fully operational daemon and client protocol implemented in Python (`vanguard.packages.runtime.service`) and TypeScript (`@vanguard/client-core`).

---

## 1. Transport & Wire Framing

The `vg.4` protocol operates over local UNIX domain sockets, named pipes, standard I/O streams, or WebSocket bridges (`vanguard-studio`). Messages are newline-delimited JSON or structured WebSocket text frames conforming to `schemas/v4/runtime-service.schema.json`.

---

## 2. Discriminated Frames

All messages exchanged across the `vg.4` boundary belong to a single discriminated union identified by `frameType`:

```json
{
  "version": "vg.4",
  "frameType": "command | receipt | event | error",
  "frameId": "string (UUIDv7 or opaque identifier)"
}
```

### Frame Definitions

| Frame Type | Required Fields | Payload Structure | Description |
|---|---|---|---|
| `command` | `version`, `frameType`, `frameId`, `command` | `command: { name, commandId, idempotencyKey, actor?, runId?, payload }` | Inbound command issued by client to runtime. |
| `receipt` | `version`, `frameType`, `frameId`, `receipt` | `receipt: { commandId, status, runId?, result?, error?, detail? }`, `inReplyTo?` | Synchronous acknowledgment and command outcome (`completed` or `error`). |
| `event` | `version`, `frameType`, `frameId`, `event` | `event: EventEnvelope` (`schemas/v4/event-envelope.schema.json`) | Asynchronous event streamed from execution ledger. |
| `error` | `version`, `frameType`, `frameId`, `error` | `error: { code, message, retryable, correlationId?, detail? }`, `inReplyTo?` | Protocol-level or infrastructure error frame. |

---

## 3. Command Payload Specifications

The `vg.4` protocol defines 11 command types:

### 1. `StartRun`
Initiates a new agent run.
- **`runId`**: Target run identifier (UUIDv7 format).
- **`payload`**:
  - `manifestPath` (`string`, required): Path to pack or root manifest.
  - `repoPath` (`string`, required): Target repository root directory.
  - `brief` (`string`, required): Task prompt or instruction string.
  - `profileId` (`string`, optional): Execution profile (`product`, `local`, `hermetic`, `sandboxed`, `evaluation`).
  - `model` (`string`, optional): Target model route selector.
  - `episodeId` (`string`, optional): Caller-specified initial episode ID (auto-generated if omitted).
  - `expectedSeq` (`integer | string`, optional): Optimistic concurrency guard.

### 2. `GetRun`
Retrieves run metadata and state.
- **`runId`**: Target run identifier.
- **`payload`**: `{ expectedSeq? }`.

### 3. `ListRuns`
Queries recent runs.
- **`runId`**: Must be empty string `""`.
- **`payload`**:
  - `limit` (`integer`, optional, default 50, max 500): Number of runs to return.
  - `offset` (`integer`, optional, default 0): Paging offset.

### 4. `StreamEvents`
Subscribes to causally ordered ledger events for an active or completed run.
- **`runId`**: Target run identifier.
- **`payload`**:
  - `afterSeq` (`string`, optional): Integer string of sequence counter to resume streaming after.

### 5. `Cancel`
Requests clean interruption and cancellation of an active run.
- **`runId`**: Target run identifier.
- **`payload`**: `{ reason?: string, expectedSeq?: SeqGuard }`.

### 6. `Checkpoint`
Requests immediate state persistence and snapshot capture.
- **`runId`**: Target run identifier.
- **`payload`**: `{ label?: string, expectedSeq?: SeqGuard }`.

### 7. `Resume`
Resumes an interrupted, failed, or suspended run from durable storage.
- **`runId`**: Target run identifier.
- **`payload`**: `{ expectedSeq?: SeqGuard }`.

### 8. `ResolveApproval`
Submits an operator authorization decision for a pending capability or gate request.
- **`runId`**: Target run identifier.
- **`payload`**:
  - `decision`: Conforms to `schemas/v4/approval-decision.schema.json` (includes `decisionId`, `requestId`, `status: "approved" | "rejected"`, `actor`, `signature` [128-hex Ed25519]).

### 9. `RecordCorrection`
Attaches operator guidance or corrective feedback to an active episode.
- **`runId`**: Target run identifier.
- **`payload`**: `{ feedback: string, expectedSeq?: SeqGuard }`.

### 10. `ExplainArtifact`
Queries causal provenance DAG explaining how an artifact was produced.
- **`runId`**: Target run identifier.
- **`payload`**: `{ artifactDigest: string }`.

### 11. `GetCapabilities`
Queries available runtime tools, models, profiles, and backend qualifiers.
- **`runId`**: Empty string `""` or target run identifier.
- **`payload`**: `{}`.

---

## 4. Canonical Error Vocabulary

Error codes are synchronized byte-for-byte between Python `service/contract.py` (`ERROR_CODES`) and TypeScript `client-core` (`ClientFailure.code`):

| Error Code | Retryable | Semantic Meaning |
|---|---|---|
| `invalid_request` | `false` | Malformed JSON, missing required fields, or schema validation failure. |
| `unauthenticated` | `false` | Missing or invalid client/operator identity credentials. |
| `permission_denied`| `false` | Operation forbidden by profile policy or capability grant failure. |
| `not_found` | `false` | Requested `runId`, `frameId`, or artifact digest does not exist. |
| `conflict` | `true` | Optimistic concurrency violation (`expectedSeq` mismatch). |
| `incompatible_version` | `false` | Client requested protocol version other than `vg.4`. |
| `frame_too_large` | `false` | Payload exceeds max buffer limit (16MB). |
| `rate_limited` | `true` | Request throttled due to provider or queue saturation. |
| `not_available` | `true` | Required backend daemon (e.g. evaluator or sandbox) is offline. |
| `internal` | `false` | Unhandled server exception or invariant violation. |

---

## 5. Ordering, Concurrency & Idempotency

1. **Idempotency**: Every command contains an `idempotencyKey`. The runtime deduplicates repeated submissions within a run window, returning the cached `ReceiptFrame`.
2. **Optimistic Concurrency Control (CAS)**: Commands accepting `expectedSeq` assert that the run sequence has not advanced since the client read state. If sequence counters differ, the daemon rejects the command with `conflict` error code without mutating state.
3. **Event Stream Ordering**: Events emitted in `EventFrame` carry strictly monotonic `sequence` numbers and hash-chained digests (`digest` / `parent_digest`).

---

## 6. Known Failure Caveat (`UNR-B-001`)

- **Profile Default Defect**: The TypeScript live `StartRun` builder omits `profileId` by default. `RuntimeService` defaults unspecified profiles to `code-default` in legacy paths, which is unsupported under current profile presets. Callers should explicitly specify `profileId: "product"` or `profileId: "local"` in the `StartRun` payload.

---

## Implementation Evidence

- **JSON Schema**: `schemas/v4/runtime-service.schema.json`.
- **Python Server**: `vanguard/packages/runtime/service/server.py`, `vanguard/packages/runtime/service/contract.py`.
- **TypeScript Client Core**: `vanguard/clients/client-core/src/service/client.ts`, `vanguard/clients/client-core/src/contract/frames.ts`.
- **Parity Tests**: `test/contracts/test_runtime_service_contract_parity.py`, `test/contracts/test_runtime_service_vectors.py`, `test/runtime/test_runtime_service.py`.
