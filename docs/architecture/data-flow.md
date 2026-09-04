---
id: arch.system.data-flow
canonical_id: arch.system.data-flow
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: system-architecture
canonical_for:
  - end-to-end execution lifecycle
  - causal state event flow
  - cross-tier streaming data flow
  - exterior evaluation data flow
purpose: Detail the system-wide end-to-end data flow, event-sourced lifecycle, causal ledger propagation, and assurance pipeline.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-002
  - E-B-011
  - E-B-013
  - E-B-017
  - E-B-022
  - E-B-023
  - E-B-044
normative_authority:
  - ../SPEC.md
relationships:
  - arch.system.overview
  - arch.system.boundaries
  - arch.runtime.execution
  - arch.agency.turns
  - arch.trust.kernel
  - arch.state.causal
  - ref.events
reviewer: documentation-specialist
confidence: high
---

# Vanguard End-to-End Data Flow & Causal State Propagation

## Purpose
This document is the canonical architecture owner for the system-wide execution lifecycle, end-to-end event propagation, causal state folding, client streaming protocols, and exterior assurance data flow across Vanguard.

## Scope
- Complete 8-stage end-to-end execution lifecycle from user invocation to signed verdict emission.
- Event-sourced ledger write pipeline (`mhf.event/2`) and content-addressed artifact store (SHA-256 CAS).
- Deterministic event folding into ephemeral state projections (`AgentView`, `RunSnapshot`).
- Client streaming data flow across UNIX domain sockets and WebSockets.
- Trajectory packaging and exterior evaluation RPC flow.

## Non-responsibilities
- 13-stage kernel dispatch algorithm internals (owned by [`arch.trust.kernel`](../backend/architecture/kernel.md)).
- Detailed turn cognition and prompt compilation (owned by [`arch.agency.turns`](../backend/architecture/agency.md)).
- Specific event envelope JSON schemas (owned by [`ref.events`](../backend/reference/events.md)).

## AS_BUILT Status
- `IMPLEMENTED` — End-to-end causal event flow is fully functional and verified through cold-replay and fresh-process lifecycle contract tests.

---

## 1. End-to-End Execution Lifecycle Flow

A complete task execution follows an 8-stage pipeline from client invocation to final verdict persistence:

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. INVOCATION│────>│2. COMPOSITION│────>│ 3. ACTIVATION│────>│ 4. COGNITION │
│ CLI / Studio │     │ Manifest + D_R│     │HarnessSession│     │ EpisodeEngine│
└──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                      │
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────▼───────┐
│  8. TEARDOWN │<────│ 7. ASSURANCE │<────│ 6. INGESTION │<────│  5. DISPATCH │
│ Stores Flush │     │Evaluator UID │     │ Context Feed │     │ Kernel S0-S12│
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

1. **Invocation**: Operator executes `vanguard run "<task>"` (Python) or `vg run "<task>"` (TypeScript).
2. **Composition & Identity**: `runtime.compose` loads manifests, binds configuration profiles, and seals the immutable `RunPlan` ($D_H, D_R$).
3. **Session Activation**: `HarnessSession` initializes, opens the SQLite WAL event ledger, binds `LedgerEmitter`, and writes `RunStarted`.
4. **Turn Cognition**: `agency.EpisodeEngine` compiles context layers (L1 System Prompt, L2 State Snapshot, L3 Trajectory History, L4 Dynamic Workspace) and prompts `ModelPort`.
5. **Kernel Effect Dispatch**: Proposed tool calls pass to `Kernel.dispatch()` through 13 discrete stages (S0 Observe $\to$ S1 Resolve $\to$ S2 Admissibility $\to$ S3 Reserve $\to$ S4 Persist Intent $\to$ S5–S9 Execute $\to$ S10 Commit Budget $\to$ S11 Release Leases $\to$ S12 Append Receipt).
6. **Receipt Ingestion**: Causal receipts and observations are fed back into context memory; the sequential turn loop repeats until completion.
7. **Exterior Assurance**: `EvidenceCaptureService` packages the final execution trajectory, calls `vanguard-evaluator` over RPC (UID 10002), and records signed `VerdictRecorded`.
8. **Teardown**: Leases close, SQLite WAL flushes, and the final `RunResult` returns to the invoking client.

---

## 2. Causal Ledger & Content-Addressed Storage Flow

State mutation flows through two distinct, immutable persistence layers:

```text
               Kernel Dispatch / Runtime Emitter
                               │
               ┌───────────────┴───────────────┐
               │                               │
        Structured Event                 Large Payload
        (Envelope Metadata)             (Blobs / Files)
               │                               │
               ▼                               ▼
       SQLite WAL Ledger             Content-Addressed CAS
        (events table)               (sha256-<digest>.bin)
```

- **Structured Events (`mhf.event/2`)**: Appended sequentially to the SQLite WAL database. Each event includes sequence number, millisecond timestamp, causal parent ID, run ID, and canonical JSON payload.
- **Content-Addressed Artifacts (CAS)**: Large outputs, tool artifacts, and workspace diffs are stored by SHA-256 digest in the blob store and referenced by digest in event payloads.

---

## 3. State Projection & Cold Replay Flow

Authoritative state is reconstructed on demand through pure deterministic folds:

$$\text{Event Stream } [E_0, E_1, \dots, E_n] \xrightarrow{\text{deterministic reducer}} \text{State Projection } (P_n)$$

- **`AgentView`**: Folds turn events to produce the agent's current perceptual context and memory bindings.
- **`RunSnapshot`**: Folds lifecycle events to provide live run status, spent budget counters, and active children.
- **Cold Replay**: Replaying the event stream in a fresh process reproduces exact causal state without relying on serialized in-memory objects.

---

## 4. Cross-Tier Client Streaming Flow

Live clients subscribe to execution updates over IPC transports:
1. Client submits command frame (`StartRun`, `SubmitInput`, `QuiesceRun`) over UNIX domain socket (`vg.4`) or WebSocket.
2. Runtime validates command schema, records idempotency key, and spawns background execution worker.
3. `LedgerEmitter` writes canonical events to SQLite WAL and simultaneously dispatches event frames to active subscriber queues.
4. Client receives NDJSON/WebSocket stream and folds events into UI state models in real time.

---

## 5. Exterior Trajectory Assurance Flow

Verification operates under strict identity and process separation (`DEC-07`):

```text
EpisodeEngine ──> EvidenceCaptureService ──> RPC Socket ──> vanguard-evaluator (UID 10002)
                                                                     │
Run Ledger <──────────── VerdictRecorded (Ed25519 Signed) <──────────┘
```

1. Upon run termination, `EvidenceCaptureService` serializes the verified trajectory events into standard format.
2. Trajectory payload is transmitted across the RPC boundary to the isolated `vanguard-evaluator` daemon (UID 10002).
3. Evaluator executes scoring criteria and signs the resulting verdict with its Ed25519 private key.
4. Runtime validates the signature against trusted roots and commits `VerdictRecorded` to the ledger.

---

## Implementation Evidence

- **Causal Persistence**: `vanguard/packages/runtime/ledger_emitter.py`, `vanguard/packages/adapters/stores/event_store.py` (`SqliteEventStore`)
- **Dispatch Pipeline**: `vanguard/packages/kernel/dispatch.py`
- **Replay Verification**: `test/contracts/test_rf25_fresh_process_wal_continuation.py`, `test/contracts/test_rf23_truthful_trajectories.py`
