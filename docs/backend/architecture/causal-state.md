---
id: arch.state.causal
canonical_id: arch.state.causal
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: state-causal
canonical_for:
  - authoritative vs derived state
  - event lifecycle
  - artifact relationship
  - cold replay/checkpoint semantics
purpose: Explain the single authoritative truth model, projection folding, cold replay, and discardable checkpoints.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-008
  - E-B-009
  - E-B-010
  - E-B-026
  - E-B-027
  - E-B-028
  - E-B-029
  - E-B-030
  - E-B-031
  - E-B-051
relationships:
  - arch.system.overview
  - arch.trust.kernel
  - ref.events
  - ref.artifacts
reviewer: documentation-specialist
confidence: high
---

# Causal State & Persistence Architecture

## Purpose
This document is the canonical architecture owner for the event-sourced causal state model, authoritative versus derived state boundaries, deterministic projection reducers, crash recovery via cold replay, and discardable checkpoint proofs.

## Scope
- Authoritative event log truth model versus derived in-memory projections (`INV-B-006`).
- Event lifecycle from intent logging (`EffectStarted`) to durable append (`EffectCompleted`).
- Content-addressed artifact storage relationship to event payloads.
- Cold replay reconstruction and process restart recovery (`RF-25`).
- Discardable snapshot checkpoints and state integrity proofs (`RF-96`).

## Non-responsibilities
- Exact event envelope schemas and field catalogs (owned by [`ref.events`](../reference/events.md)).
- Low-level blob store APIs and filesystem layout (owned by [`ref.artifacts`](../reference/artifacts-memory.md)).
- SQLite WAL transaction mechanics (owned by [`ref.configuration`](../reference/configuration.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Pure event sourcing with deterministic state folding and verified checkpoint caches is implemented in `vanguard.packages.domain.ledger` and `vanguard.packages.runtime.checkpoints`.
- `PARTIAL` — Coding task, verification freshness, and classified-recovery projections are **v0.9.2 targets**. Until their event payloads and reducers exist, they must not be represented as durable current behavior.

---

## 1. The Authoritative Truth Model (`INV-B-006`)

Vanguard enforces a strict separation between authoritative durable facts and derived projections:

```text
┌─────────────────────────────────────────────────────────────┐
│                 AUTHORITATIVE STATE OF RECORD               │
│   Append-Only SQLite WAL Event Store (mhf.event/2 Envelopes)│
│   + Content-Addressed Blob Storage (CAS Blobs)              │
└──────────────────────────────┬──────────────────────────────┘
                               │
               Deterministic Event Folding (Pure Reducers)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    DERIVED IN-MEMORY VIEWS                  │
│   LedgerState · AgentView · ProgressView · WorkflowState   │
│   (Discardable Caches / Reconstructible from Event Stream)  │
└─────────────────────────────────────────────────────────────┘
```

### Invariant Rules
1. **Single Source of Truth**: The append-only event store is the sole authoritative record of execution.
2. **Deterministic Derivability**: All runtime views (`LedgerState`, `AgentView`, `WorkflowState`) are pure functions of the ordered event sequence:
   $$	ext{State}_N = 	ext{fold}(	ext{InitialState}, [e_0, e_1, \dots, e_N])$$
3. **No Direct State Mutation**: In-memory views cannot be mutated directly by API calls; state changes must occur via appended events.

---

## 2. Event Lifecycle & Intent Logging

Every state transition progresses through a durable lifecycle:

1. **Intent Registration**: Before any physical I/O or model call occurs, the kernel appends an `EffectStarted` event and commits it to disk (`fsync`).
2. **Physical Execution**: The adapter performs the leased work.
3. **Receipt Emission**: Upon return, the kernel appends an `EffectCompleted` or `EffectFailed` event with the resulting receipt digest and consumed budget.
4. **Projection Folding**: Active domain projections ingest the new event, updating in-memory status.

---

## 3. Projection Ownership & Reducers

Projections in `vanguard.packages.domain.ledger` are pure, zero-I/O reducers:

| Projection Class | Module | State Tracked |
|---|---|---|
| `LedgerState` | `domain.ledger.state` | Active run status, sequence counter, cumulative budgets, active leases, last digest. |
| `AgentView` | `domain.ledger.agent_view` | Turn count, recent message history, pending approval requests, tool receipts. |
| `ProgressView` | `domain.ledger.progress` | Milestone completion percentages, sub-goal progress, blocker tracking. |
| `WorkflowState` | `domain.ledger.workflow` | Step graph execution statuses, dependency DAG transitions. |

---

## 4. Artifact Relationship (Content-Addressed Blobs)

To keep the event store lean and bounded:
- Large payloads (source code files, diffs, images, multi-megabyte tool outputs) are written to the **Content-Addressed Blob Store** (`ref.artifacts`).
- The event envelope carries only the immutable `ArtifactRef` containing the SHA-256 digest, byte size, and MIME type.
- An event log can be replayed safely even if large blob bodies are offloaded or archived.

---

## 5. Cold Replay & Crash Recovery (`RF-25`)

If a process terminates unexpectedly (SIGKILL, power loss, container eviction):
1. A fresh Vanguard process starts with `vanguard resume --run-id <ID>`.
2. The runtime opens the SQLite WAL event store and reads events sequentially from sequence `0` to $N$.
3. The reducers fold the entire history, perfectly reconstructing the in-memory `LedgerState` and `AgentView` to the exact microsecond before the crash.
4. If an `EffectStarted` event has no matching `EffectCompleted` or `EffectFailed`, the recovery manager marks the effect as *undeterminable* and appends `EffectReconciled` before resuming the turn loop.

---

## 6. Discardable Checkpoint Proofs (`RF-96`)

To accelerate cold start times on runs with thousands of events:
- The runtime periodically computes a snapshot of `LedgerState` and writes a checkpoint.
- **Verification Rule**: A checkpoint is never trusted blindly. It contains the sequence number and `state_digest`. The runtime verifies that the checkpoint digest matches the fold of events up to sequence $K$.
- If a checkpoint is corrupted or deleted, the runtime seamlessly falls back to replaying from genesis event `0` without data loss.

---

## 7. v0.9.2 Target: Coding-State and Evidence Projections

> **TARGET / PLANNED — not AS_BUILT.** Exact event kinds and payload schemas require implementation and registration in [`ref.events`](../reference/events.md); this section defines only causal-state properties.

Coding plans, repository-context selections, patch postimages, verification receipts, failure classifications, recovery decisions, and completion-admission decisions must follow the same authority split as every other runtime view:

```text
ledger facts + content-addressed artifacts
                 -> pure reducers
                 -> CodingTaskState / verification / recovery views
```

No generated repository index, LDA database, context packet, checkpoint, or benchmark summary becomes operational truth. These are reconstructible projections or evidence artifacts. Their provenance must bind the source repository snapshot and generator/provider identity.

Projection compatibility is part of the event contract. Reducers must consume the fields actually emitted by the active writer, preserve dual-read behavior when a field is renamed, and have contract vectors that fold representative current envelopes. Unknown or incompatible fields must not silently become generic actions when that would change planning, budget, verification, or recovery semantics.

Verification freshness is derived from causal order and identity: a verification receipt is applicable only to the workspace/postimage it evaluated, and any later accepted edit invalidates it for completion admission. A compact expression is:

$$
\operatorname{fresh}(v, s) =
(v.\operatorname{postimage\_digest} = s.\operatorname{postimage\_digest})
\land (v.\operatorname{sequence} > s.\operatorname{last\_edit\_sequence})
$$

Benchmark evidence should bind `run_id`, task and repository digests, harness/manifest identity, model/provider identity, trajectory digest, terminal reason, patch digest, verification and evaluator receipts, and measured tokens/cost/latency/turns/tool calls/retries. A report row without a trajectory link may be retained diagnostically but is not qualifying evidence.

---

## Implementation Evidence

- **Ledger State & Reducers**: `vanguard/packages/domain/ledger/` (`state.py`, `agent_view.py`, `progress.py`, `events.py`).
- **Checkpoints**: `vanguard/packages/runtime/checkpoints.py`.
- **Event Store Adapter**: `vanguard/packages/adapters/stores/event_store.py` (`SqliteEventStore`).
- **Recovery Tests**: `test/falsifiers/test_rf25_cold_continuation.py`, `test/falsifiers/test_rf96_checkpoint_reconstruction.py`, `test/contracts/test_b3_wal_recovery.py`.

---

## Architectural Decisions & Philosophical Rationale

### DEC-03 — Authoritative Causal History over Mutable In-Memory State

- **Decision:** Authoritative state is defined strictly by the append-only causal event stream; all in-memory objects, projection graphs, and caches are disposable views.
- **Rationale:** Mutable in-memory state creates competing truths across crashes, restarts, and distributed processes. Deterministic event folding over an append-only log guarantees crash consistency, provenance auditability, and cold replayability.
- **Rejected alternative:** Object-oriented persistence where state machines mutate in-place and serialize periodic snapshots.
- **Reversal condition:** Workload evidence demonstrating that deterministic event folding cannot meet latency budgets even when assisted by discardable checkpoint caches.

### DEC-05 — Static Composition Distinct from Observed Trajectory

- **Decision:** Declarative composition (`mhf.manifest/2`) declares available capabilities; the durable event trajectory records what actually occurred. Neither may impersonate the other.
- **Rationale:** Conflating declared intent with observed execution prevents truthful post-mortem auditing, hides runtime attenuation, and allows unverified declarations to pass as evidence.
- **Rejected alternative:** Dynamic manifest mutation during execution to reflect intermediate turn outcomes.
- **Reversal condition:** None; maintaining declared versus observed separation is an inviolable architectural auditability invariant.

