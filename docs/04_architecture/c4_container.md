---
status: living
id: architecture-c4-containers
class: architecture
authority: descriptive
canonical_for:
  - c4-containers-view
source_of_truth:
  - docs/SPEC.md
derived_from:
  - vanguard/packages/runtime/service/server.py
  - vanguard/packages/adapters/stores/event_store.py
  - containers/worker.Dockerfile
  - containers/evaluator.Dockerfile
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

# C4 Container View

> **Status:** `AS_BUILT` · Descriptive View.

```mermaid
flowchart LR
    subgraph Host["Host Operating System"]
        CLI["vg CLI (Node.js 20+ / Ink)"]
        Daemon["Runtime service (Python 3.10+)"]
        Store[("SQLite WAL Event Store")]
        
        subgraph WorkerNS["Worker Sandbox (UID 10001)"]
            WorkerProc["Tool / Process Execution (bwrap)"]
        end
        
        subgraph EvaluatorNS["Evaluator Isolation (UID 10002)"]
            EvalDaemon["Evaluator Daemon (Ed25519 Signer)"]
        end
    end

    CLI -->|Unix Domain Socket / JSON-RPC| Daemon
    Daemon -->|Single Writer LedgerEmitter| Store
    Daemon -->|Rootless Bwrap Jail| WorkerProc
    Daemon -->|UDS RPC Request| EvalDaemon
```

## Containers & Process Identities

| Container / Process | Runtime / Image | UID | Security Boundary & Isolation |
|---|---|---|---|
| **CLI Client (`vg`)** | Node.js 20+ / Ink | Current User | Presentation client only; no domain or kernel imports |
| **Control Plane Substrate** | Python 3.10+ | Current User | Hexagonal core, manages session lifecycle and ledger emissions |
| **Worker Sandbox** | `containers/worker.Dockerfile` / bwrap adapter | `10001` target identity | Rootless isolation whose actual containment is reported by probes; do not infer every mount/network property from this diagram |
| **Evaluator Daemon** | `containers/evaluator.Dockerfile` | `10002` | Independent process/mounts; possesses Ed25519 signing key |
| **Storage Engine** | SQLite WAL | Current User | Embedded transactional append-only log with WAL mode |
