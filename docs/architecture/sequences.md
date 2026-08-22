---
status: living
id: architecture-sequences
class: architecture
authority: descriptive
canonical_for:
  - sequence-flows
source_of_truth:
  - docs/SPEC.md#4-execution-lifecycle
  - docs/04_annex/KERNEL.md#2-the-13-stage-dispatch-pipeline
derived_from:
  - vanguard/packages/kernel/dispatch.py
  - vanguard/packages/runtime/session.py
  - vanguard/packages/agency/episode/engine.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Subsystem Sequence Flows

> **Status:** `AS_BUILT` · Descriptive View.

---

## 1. 13-Stage Kernel Effect Dispatch Pipeline (S0–S12)

Governed by [`docs/04_annex/KERNEL.md`](../04_annex/KERNEL.md) and implemented in [`dispatch.py`](../../vanguard/packages/kernel/dispatch.py):

```mermaid
sequenceDiagram
    autonumber
    actor Engine as EpisodeEngine
    participant Kernel as Kernel Dispatch (TCB)
    participant Policy as Policy & Attenuation
    participant Sandbox as Sandbox / Adapter
    participant Ledger as LedgerEmitter / WAL

    Engine->>Kernel: dispatch(intent, justification)
    Note over Kernel: S0 Observe Intent & Justification
    Kernel->>Policy: S1 Parse & Validate Structure
    Kernel->>Policy: S2 Classify Action & Check Ceiling
    Kernel->>Policy: S3 Verify Principal Attenuation
    Kernel->>Policy: S4 Check & Debit 6D Budget
    Kernel->>Policy: S5 Request/Verify Approval (if privileged)
    Kernel->>Policy: S6 Issue Descriptor-Bound Grant
    Kernel->>Ledger: S7 Record Durable Intent in WAL
    Kernel->>Sandbox: S8 Execute Authorized Effect
    Sandbox-->>Kernel: S9 Capture Raw Execution Result
    Kernel->>Policy: S10 Evaluate Safety Invariants
    Kernel->>Ledger: S11 Issue Cryptographic Receipt & Event
    Kernel-->>Engine: S12 Return Receipt to Caller
```

---

## 2. Exterior Signed Evaluation Flow

```mermaid
sequenceDiagram
    autonumber
    participant Session as HarnessSession
    participant Gateway as EvaluatorGateway
    participant EvalDaemon as EvaluatorDaemon (UID 10002)
    participant Emitter as LedgerEmitter
    participant Store as SQLite WAL

    Session->>Gateway: evaluate_episode(episode_id, artifacts)
    Gateway->>EvalDaemon: JSON-RPC request over UDS
    Note over EvalDaemon: Independent grading & verification
    Note over EvalDaemon: Ed25519 signature over JCS canonical bytes
    EvalDaemon-->>Gateway: SignedVerdict(verdict, signature, nonce)
    Gateway->>Emitter: emit_verdict(SignedVerdict)
    Emitter->>Store: append(VerdictRecorded)
    Gateway-->>Session: Return validated verdict
```

---

## 3. Cold Replay & Continuation Flow (NOVA-2 / RF-25)

```mermaid
sequenceDiagram
    autonumber
    participant FreshProc as Fresh Python Process
    participant Recovery as LedgerRecovery
    participant Store as SQLite WAL File
    participant Reducer as LedgerState Reducer
    participant Session as Resumed HarnessSession

    FreshProc->>Recovery: recover_from_file(db_path)
    Recovery->>Store: Read durable event prefix
    Recovery->>Reducer: fold_events(events) -> EffectiveState
    Note over Recovery: Check open S8a intents (reconcile vs undeterminable)
    Recovery->>Session: construct_session(EffectiveState)
    Session->>Session: continue_turn_loop()
```
