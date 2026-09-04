---
id: arch.system.boundaries
canonical_id: arch.system.boundaries
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: system-architecture
canonical_for:
  - system isolation boundaries
  - hexagonal dependency hierarchy
  - reference monitor containment
  - physical sandbox perimeters
purpose: Detail the system-wide architecture boundaries, hexagonal dependency constraints, TCB reference monitor isolation, and process sandboxing rules.
audience:
  - developer
  - architect
  - security-auditor
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-002
  - E-B-013
  - E-B-014
  - E-B-015
  - E-B-021
  - E-B-025
  - E-B-044
normative_authority:
  - ../execution/spec.md
relationships:
  - arch.system.overview
  - arch.system.data-flow
  - arch.trust.kernel
  - arch.interfaces.clients
  - ref.ports
reviewer: documentation-specialist
confidence: high
---

# Vanguard System Boundaries & Isolation Architecture

## Purpose
This document is the canonical architecture owner for the system-wide isolation boundaries, the hexagonal dependency hierarchy, the Trusted Computing Base (TCB) reference monitor perimeter, client transport boundaries, and physical process sandbox constraints across Vanguard.

## Scope
- Hexagonal boundary lattice and dependency direction enforcement (`INV-B-001`).
- Client-runtime transport perimeters (UNIX domain socket `0600`, WebSocket gateway, in-process bindings).
- Trusted Computing Base (TCB) reference monitor boundary and LOC budget constraints.
- Process sandboxing and physical privilege isolation (Bubblewrap UID 10001, Evaluator daemon UID 10002).
- Orthogonal separation of agent capability grants versus plugin process containment.

## Non-responsibilities
- Microkernel dispatch stage semantics (owned by [`arch.trust.kernel`](../backend/architecture/kernel.md)).
- Hexagonal port and SPI interface definitions (owned by [`ref.ports`](../backend/reference/ports.md)).
- Client wire message structures (owned by [`ref.runtime-service`](../backend/reference/runtime-service.md)).

## AS_BUILT Status
- `IMPLEMENTED` — All six boundary perimeters are active, enforced via automated linters (`check_boundaries.py`, `check_tcb_budget.py`, `check_isolation_policy.py`) and verified by security contract tests.

---

## 1. System Boundary Taxonomy

Vanguard enforces six distinct, non-overlapping boundary perimeters:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. HOST / USER BOUNDARY                                                │
│    CLI Invocation · Environment Variables · Local Filesystem Paths    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. CLIENT / RUNTIME TRANSPORT BOUNDARY                                │
│    UNIX Domain Socket (0600) · HTTP/WebSocket Studio Bridge · stdio   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 3. HEXAGONAL DEPENDENCY LATTICE                                       │
│    domain ← ports ← kernel ← agency ← runtime → adapters              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 4. TRUSTED COMPUTING BASE (TCB) REFERENCE MONITOR                      │
│    S0–S12 Monotonic Dispatch · Typed Budgets · Grants (<= 1438 LOC)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 5. PROCESS SANDBOX & PHYSICAL ISOLATION                                │
│    Bubblewrap Rootless Sandbox (UID 10001) · Evaluator Daemon (UID 10002)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ 6. AUTHORITATIVE CAUSAL STORAGE                                        │
│    Append-Only SQLite WAL Event Ledger · Content-Addressed Blobs (CAS)│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Hexagonal Dependency Lattice (`INV-B-001`)

The production codebase (`vanguard/packages/`) strictly enforces a unidirectional layer hierarchy:

$$\text{domain} \leftarrow \text{ports} \leftarrow \text{kernel} \leftarrow \text{agency} \leftarrow \text{runtime} \rightarrow \text{adapters}$$
$$(\text{apps/ is a client slot of runtime})$$

- **`domain/`**: Pure value objects, wire contracts, RFC 8785 JCS canonicalization, deterministic event reducers, resource selectors, and task state models. Standard library Python only (zero I/O, zero network, zero dependencies).
- **`ports/`**: Hexagonal port protocols (`KernelPort`, `ModelPort`, `SandboxPort`, `EvaluatorPort`, `EventStorePort`, `BlobStorePort`, `IndexPort`) and 5 frozen SPI contracts (`spi.py`). Zero runtime dependencies.
- **`kernel/`**: Domain-blind reference monitor (TCB $\le 1438$ LOC; currently 1386 LOC). Mediates effects through 13-stage dispatch (S0–S12), monotonic attenuation, descriptor-bound capability grants, typed budget algebra, and execution provenance DAG.
- **`agency/`**: Sequential turn execution loop (`EpisodeEngine`), attenuated child agent `spawn()`, layered context compilation (L1–L4), admission gates, and protocol recovery.
- **`runtime/`**: Lifecycle orchestration (`compose.py`, `session.py`, `wiring.py`), single-writer `LedgerEmitter`, Ed25519 cryptographic governance (`governance/`), and SQLite WAL event storage.
- **`adapters/`**: Concrete implementations of port protocols (Model APIs, SQLite WAL, Bubblewrap `bwrap`, Evaluator RPC). **Must not** import `kernel` or `agency`.
- **`apps/`**: Thin application entrypoints (e.g., `vanguard/packages/apps/coding_max/facade.py` exposing `CodingMaxFacade` / `CodingMax`).
- **`clients/`**: Front-end workspaces under `vanguard/clients/`: TypeScript CLI (`vg`), Desktop UI, TUI, Lab, and Studio.

Enforced in CI by `tools/linters/check_boundaries.py` across all source packages.

---

## 3. Client Transport & Access Control Boundary

Clients access runtime services across strict transport barriers:
- **UNIX Domain Socket (`vg.4`)**: Bound with POSIX mode `0600`, restricting access exclusively to the owning user process. Rejects unauthorized concurrent connections.
- **Studio WebSocket Gateway**: Translates JSON-RPC frames over localhost-bound HTTP/WS bridges. Does not hold effect execution authority.
- **Direct In-Process Python**: Instantiates `ApplicationService` (`vanguard.packages.runtime.app_service.ApplicationService`) with in-memory message passing and zero privilege escalation.

---

## 4. Kernel TCB Reference Monitor Boundary

The Trusted Computing Base is bounded and domain-blind (`INV-B-002`):
- **Code Budget**: Strictly capped at $\le 1438$ logical lines of code (enforced by `check_tcb_budget.py`; currently 1386 logical LOC).
- **Domain Blindness**: Kernel structures operate solely on abstract effect descriptors, monotonic capability grants, and typed budgets (`usd_micros`, `millis`, `tokens`, `bytes`). Enforced by `check_domain_blindness.py`.
- **Fail-Closed Mediation**: Privileged operations cannot execute without verified capability grants and reserved budget slices.

---

## 5. Physical Sandboxing & Process Isolation (`INV-B-003`)

Untrusted tool execution and model evaluations run outside the primary application process:
- **Bubblewrap Rootless Sandbox**: Tool processes execute under dedicated UID `10001` with restricted Linux namespaces (PID, IPC, UTS, Mount), read-only root filesystems, and bounded tmpfs mounts.
- **Evaluator Daemon Isolation**: External scoring runs in an independent daemon process under UID `10002` communicating over mutual RPC, preventing model self-grading and evaluation tampering.

---

## 6. Orthogonal Security Separation (`DEC-09`)

Agent capability grants (attenuated model permissions) and plugin isolation policies (OS sandboxing/containerization) operate as strictly orthogonal security controls:
- Model capability attenuation restricts **what an agent is allowed to request**.
- Process containerization restricts **what executed binaries can access on the host**.
- Neither security mechanism may substitute for or bypass the other.

---

## Implementation Evidence

- **Hexagonal Boundary Enforcement**: `tools/linters/check_boundaries.py`
- **TCB Budget Linter**: `tools/linters/check_tcb_budget.py`
- **Isolation Policy Linter**: `tools/linters/check_isolation_policy.py`
- **Security Boundary Tests**: `test/contracts/test_b2_lifecycle_integration.py`, `test/falsifiers/test_rf94_single_runtime_authority.py`
