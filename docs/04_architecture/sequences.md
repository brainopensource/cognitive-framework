---
status: living
id: architecture-sequences
class: architecture
authority: descriptive
canonical_for:
  - sequence-flows
source_of_truth:
  - docs/SPEC.md
  - docs/01_law/DISPATCH.md#2-the-dispatch-sequence
derived_from:
  - vanguard/packages/kernel/dispatch.py
  - vanguard/packages/runtime/session.py
  - vanguard/packages/agency/episode/engine.py
applies_to:
  - v0.6.2
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Subsystem Sequence Flows

> **Status:** Mixed descriptive view. Sections 1–3 are `AS_BUILT`; section 3 records the
> fresh-process continuation behavior proven by RF-25.

---

## 1. 13-Stage Kernel Effect Dispatch Pipeline (S0–S12)

Governed by [`docs/01_law/DISPATCH.md`](../01_law/DISPATCH.md) and implemented in [`dispatch.py`](../../vanguard/packages/kernel/dispatch.py):

```mermaid
sequenceDiagram
    autonumber
    actor Engine as EpisodeEngine
    participant Kernel as Kernel Dispatch (TCB)
    participant Policy as Policy / Grant Issuer / Governor
    participant Sandbox as Sandbox / Adapter
    participant Ledger as LedgerEmitter / WAL

    Engine->>Kernel: S0 ENTER EffectRequest
    Note over Kernel: S1 PARSE schema
    Note over Kernel: S2 RESOLVE action in closed adapter table
    Note over Kernel: S3 DESCRIBE canonical descriptor digest
    Kernel->>Policy: S4 CLASSIFY capability widening
    Kernel->>Policy: S5 AUTHORIZE exact request
    Kernel->>Policy: S6 GRANT descriptor-bound authority
    Kernel->>Policy: S7 RESERVE parent-linked budget lease
    Note over Kernel: S8 VERIFY grant at point of effect
    Kernel->>Ledger: S8a INTENT append EffectStarted and fsync
    Kernel->>Sandbox: S9 DISPATCH adapter.execute()
    Sandbox-->>Kernel: AdapterOutcome and actual cost
    Kernel->>Policy: S10 COMMIT actual cost, including overrun
    Kernel->>Policy: S11 RELEASE lease on every path
    Kernel->>Ledger: S12 EMIT terminal outcome events
    Kernel-->>Engine: DispatchResult / receipt
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

## 3. Cold Replay & Continuation (NOVA-2 / RF-25 — `AS_BUILT`)

```mermaid
sequenceDiagram
    autonumber
    participant FreshProc as Fresh Python Process
    participant Recovery as LedgerRecovery
    participant Store as SQLite WAL File
    participant Reducer as LedgerState Reducer
    participant Governor as Reconstructed Governor
    participant Session as Resumed HarnessSession
    participant Trajectory as Trajectory Assembler

    FreshProc->>Recovery: open file-backed store in a fresh interpreter
    Recovery->>Store: Read durable event prefix
    Recovery->>Reducer: fold_events(events) -> EffectiveState
    Recovery->>Governor: restore and reconcile pending leases
    Note over Recovery: Open S8a intents remain undeterminable until reconciled
    Recovery->>Session: reconstruct legal continuation state
    Session->>Store: append RunRecovered through LedgerEmitter
    Session->>Session: continue without replaying settled or guessing uncertain effects
    Session->>Trajectory: join verified prefix plus current turns exactly once
```

RF-25 remains red. Current `runtime/ledger/recovery.py` can fold and scan durable events, but the
complete fresh-interpreter reconciliation and continuation contract above is the M-2 proof target.
