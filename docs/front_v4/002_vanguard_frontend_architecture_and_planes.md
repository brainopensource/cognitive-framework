# Vanguard Frontend Architecture & Plane Isolation Model

**Document ID:** `VG-FE-002`  
**Version:** `0.4.1-beta`  
**Status:** `Normative / Authoritative`  
**Owner:** `Tech Lead & Principal Architect`  
**Related Specs:** [`03_vanguard_architecture_planes_and_execution_model_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md), [`ADR-0062`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/09_vanguard_decision_register_v040.md#L181), [`ADR-0063`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/09_vanguard_decision_register_v040.md#L193)

---

## 1. Architectural Philosophy: Decoupled Interaction Plane

Vanguard strictly adheres to the principle: **"Daemon, not a CLI with a UI bolted on"** ([`VG-03 §12`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md#L547)).

The frontend (both Terminal UI and IDE surfaces) belongs exclusively to the **Interaction Plane**. It does **not** execute agent loops, it does **not** hold LLM provider keys, and it **never** directly imports Python kernel internals.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        INTERACTION PLANE (TypeScript)                  │
│                                                                        │
│   ┌───────────────────────────┐      ┌─────────────────────────────┐   │
│   │    CLI / TUI (React+Ink)  │      │  Code-OSS Secondary Panel   │   │
│   │   (@vanguard/cli / 'vg')  │      │     (Vanguard IDE Webview)  │   │
│   └─────────────┬─────────────┘      └──────────────┬──────────────┘   │
│                 │                                   │                  │
│                 └─────────────────┬─────────────────┘                  │
│                                   ▼                                    │
│                 ┌───────────────────────────────────┐                  │
│                 │    Client Application & State     │                  │
│                 │    (useVanguardRun, Store, Hooks) │                  │
│                 └─────────────────┬─────────────────┘                  │
│                                   │                                    │
│            ┌──────────────────────┴──────────────────────┐             │
│            ▼                                             ▼             │
│   ┌──────────────────┐                         ┌───────────────────┐   │
│   │ Live Daemon Port │                         │ Replay / Mock Port│   │
│   │  (UDS / Pipes)   │                         │  (JSONL Session)  │   │
│   └────────┬─────────┘                         └───────────────────┘   │
└────────────┼───────────────────────────────────────────────────────────┘
             │ 
             │ IPC BOUNDARY: Line-Delimited JSON (NDJSON Wire RPC)
             │ Transport: Unix Domain Socket / Windows Named Pipe
             │ 
┌────────────▼───────────────────────────────────────────────────────────┐
│                        CONTROL PLANE (Python Daemon)                   │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │   RuntimeService (UDS Server, Inbox/Outbox, Session Dispatch)  │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│   ┌───────────────────────────────▼────────────────────────────────┐   │
│   │   Microkernel, Capability Attenuation, Policy, SQLite Ledger   │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
└───────────────────────────────────┼────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        WORKLOAD & EVIDENCE PLANES                      │
│   Isolated Rootless Containers / Sandboxed Subprocesses (Worker/Eval)  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Core Invariants of the Interaction Plane

Developers implementing frontend modules must adhere strictly to these non-negotiable invariants:

* **INVAR-FE-01: Pure Consumer Isolation**  
  The UI is a view over data emitted by the ledger stream. It renders state transitions but never mutates the state ledger directly.
* **INVAR-FE-02: Asymmetric Approval Authority (`Principal::Operator`)**  
  The runtime daemon holds zero authority to approve high-risk capabilities on its own behalf. The frontend acts as the independent signing authority using an external Ed25519 private key ([`ADR-0062`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/09_vanguard_decision_register_v040.md#L181)).
* **INVAR-FE-03: Zero Shared Memory / No Subprocess Coupling**  
  The UI client communicates exclusively via structured NDJSON wire envelopes over standard OS IPC transports. No in-memory C-bindings or foreign function imports are permitted.
* **INVAR-FE-04: Bounded Buffer & Backpressure Protection**  
  The UI client must implement a sliding window for event logs (max 5,000 event frames in memory) to prevent runaway memory usage during high-throughput token streaming.

---

## 3. Hexagonal Package Structure for the Frontend

The TypeScript codebase under [`vanguard/clients/cli/`](file:///home/rocha/Coding/Aether-D-System/vanguard/clients/cli) is structured according to strict hexagonal dependency rules:

```
vanguard/clients/cli/
├── src/
│   ├── contract/          # [DOMAIN] Pure JSON Schemas, Wire Types & Conformance Readers
│   │   ├── wire.ts        # TypeScript types generated from normative JSON Schema
│   │   ├── validators.ts  # Validation routines ensuring vector conformance
│   │   └── index.ts
│   │
│   ├── application/       # [PORTS & USE CASES] Core client application logic
│   │   ├── ports.ts       # RuntimePort interface (StartRun, StreamEvents, ResolveApproval)
│   │   ├── session.ts     # Active session state machine
│   │   └── signer.ts      # Operator key management & RFC 8785 canonical bytes signer
│   │
│   ├── adapters/          # [ADAPTERS] Concrete transport implementations
│   │   ├── live.ts        # Live Unix Domain Socket / Named Pipe UDS client
│   │   ├── replay.ts      # Deterministic JSONL session file replayer
│   │   ├── mock.ts        # In-memory synthetic mock engine for fast unit testing
│   │   └── signer.ts      # Ed25519 cryptographic implementation
│   │
│   ├── runtime/           # [SUPERVISOR] Local daemon lifecycle supervisor
│   │   ├── supervisor.ts  # Spawns, checks health, and auto-starts Python backend
│   │   └── paths.ts       # Cross-platform socket and config path resolution
│   │
│   ├── ui/                # [PRESENTATION] React + Ink terminal visual components
│   │   ├── App.tsx        # Root terminal container and keyboard routing
│   │   ├── Header.tsx     # Manifest banner, token spend & status indicator
│   │   ├── StreamView.tsx # Token-by-token streaming response & thought renderer
│   │   ├── DiffView.tsx   # Git syntax-highlighted diff display
│   │   ├── ApprovalModal.tsx # Interactive Ed25519 capability approval prompt
│   │   ├── PromptBar.tsx  # Interactive multiline input with auto-complete
│   │   └── Inspector.tsx  # L1–L5 Prompt layer context inspection view
│   │
│   ├── main.tsx           # Entry point for the CLI binary ('vg')
│   └── tui.tsx            # Terminal UI bootstrap and fullscreen lifecycle
│
└── test/                  # Strict unit and integration test suite
```

---

## 4. Cross-Platform Transport Layer (IPC)

The frontend uses OS-optimized, zero-latency local transports:

| Platform | Transport Mechanism | Default Path / Identifier | Fallback |
| :--- | :--- | :--- | :--- |
| **Linux** | POSIX Unix Domain Socket | `/tmp/vanguard-$UID/runtime.sock` or `~/.vanguard/run/runtime.sock` | Localhost Loopback TCP (Authenticated) |
| **macOS** | POSIX Unix Domain Socket | `~/Library/Application Support/Vanguard/run/runtime.sock` | Localhost Loopback TCP (Authenticated) |
| **Windows** | Windows Named Pipe | `\\.\pipe\vanguard-runtime-%USERNAME%` | Localhost Loopback TCP (127.0.0.1:48199) |

---

## 5. Security & Threat Model of the Frontend

```
[ UNTRUSTED INTERNET / MODEL ]
              │
              ▼
    [ Vanguard Microkernel ] ──(Emits Capability Approval Request)──┐
                                                                     │ Wire RPC
                                                                     ▼
                                                      ┌─────────────────────────────┐
                                                      │  Vanguard Frontend (Client) │
                                                      │  1. Renders Request to User │
                                                      │  2. User Inspects Diff/Cmd  │
                                                      │  3. Ed25519 Signs Payload   │
                                                      └──────────────┬──────────────┘
                                                                     │ Signed Envelope
                                                                     ▼
    [ Vanguard Microkernel ] ◄──(Verifies Signature via PubKey)──────┘
              │
              ▼ (Executes Only if Valid)
    [ Sandboxed Sandbox Worker ]
```

1. **Private Key Storage:** The operator Ed25519 private key is held exclusively by the frontend in `~/.vanguard/keys/operator.key` (POSIX permissions `0600`). The Python daemon **never** receives or stores the private key; it only stores the public key.
2. **Deterministic Payload Signing:** Approvals sign the exact canonical SHA-256 digest of the RFC 8785 JSON bytes representing the requested action descriptor. This prevents man-in-the-middle forging or memory replay attacks.
