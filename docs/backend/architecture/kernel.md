---
id: arch.trust.kernel
canonical_id: arch.trust.kernel
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: kernel-tcb
canonical_for:
  - kernel responsibility boundary
  - S1-S12 execution semantics
  - capability/budget ownership
  - failure semantics
purpose: Explain the Trusted Computing Base, dispatch pipeline, budget algebra, and fail-closed security invariants.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-013
  - E-B-014
  - E-B-015
  - E-B-016
  - E-B-018
  - E-B-027
  - E-B-056
relationships:
  - arch.system.overview
  - arch.agency.turns
  - ref.events
  - ref.ports
reviewer: documentation-specialist
confidence: high
---

# Kernel & Trusted Computing Base Architecture

## Purpose
This document is the canonical architecture owner for the Vanguard Trusted Computing Base (TCB), the deterministic 13-stage effect dispatch pipeline (S0–S12), monotonic capability attenuation, typed budget algebra, and fail-closed crash/undeterminacy recovery semantics.

## Scope
- The architectural responsibility boundary of `vanguard.packages.kernel`.
- The strict 13-stage dispatch sequence (S0 through S12).
- Capability grant issuance, cryptographic descriptor binding, and attenuation lattices.
- Typed additive budget reservations, overruns, and governor commits.
- Fail-closed error handling, lease safety, and intent logging (`EffectStarted` fsync).

## Non-responsibilities
- Exact wire event envelope schemas and catalogs (owned by [`ref.events`](../reference/events.md)).
- Specific model/tool adapter execution logic (owned by [`ref.ports`](../reference/ports.md) and [`guide.add-adapter-provider`](../guides/add-adapter-or-provider.md)).
- Agent prompt compilation and turn cognition (owned by [`arch.agency.turns`](agency.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Pure, domain-blind, dependency-free Trusted Computing Base ($1386$ logical LOC $\le 1438$ budget, verified by `check_tcb_budget.py` and `check_domain_blindness.py`).

---

## 1. Boundary & Trusted Computing Base (TCB)

The Kernel (`vanguard.packages.kernel`) is the sole trusted authority for mediating privileged side-effects and resource allocation.

### Core Architectural Invariants
- **Strict Domain Blindness (`INV-B-002`)**: The kernel imports zero task domain modules, zero agent logic, and zero concrete adapters. It operates strictly on generic descriptors, scopes, budgets, and capabilities.
- **TCB Budget Constraint (`INV-B-002`)**: The entire kernel package is strictly capped at $\le 1438$ logical lines of code (currently 1386 LOC across 9 single-responsibility modules) to ensure comprehensive formal and human auditability.
- **Single Dispatch Path**: There is no secondary, bypass, or administrative backdoor for physical effects; all execution flows through `Kernel.dispatch()`.

---

## 2. The 13-Stage Dispatch Sequence (S0–S12)

Every proposed effect request undergoes an immutable, sequentially ordered pipeline in `vanguard.packages.kernel.dispatch`:

```text
 S0  ENTER      EffectRequest arrives at Kernel boundary
 S1  PARSE      Validate syntax against contract schema
 S2  RESOLVE    Resolve action -> EffectAdapter (BEFORE any lease reservation)
 S3  DESCRIBE   descriptor = digest(JCS_canonical(action, normalisedArgs))
 S4  CLASSIFY   widensCapability := classifier(request) (per-request sink evaluation)
 S5  AUTHORIZE  decision := policy.authorize(scope, descriptor, principal)
 S6  GRANT      grant := issue(descriptor, principal, resources, ttl)
 S7  RESERVE    lease := governor.reserve(runId, resources, parentLease)
 +-- try (guarded execution block) ------------------------------------+
 | S8  VERIFY   Assert grant binds THIS exact descriptor and is unexpired
 | S8a INTENT   Durably append EffectStarted to ledger and FSYNC       |
 | S9  DISPATCH Execute physical adapter: adapter.execute(request, ctx)|
 | S10 COMMIT   governor.commit(lease, actual_consumed_resources)      |
 +-- finally ----------------------------------------------------------+
 S11 RELEASE    governor.release(lease) (ALWAYS executed on every path)|
 S12 EMIT       Emit terminal outcome events (AFTER lease release)     |
```

### Critical Dispatch Invariant Rules
- **`K-04` (S2 precedes S7)**: Adapter resolution precedes lease acquisition so an invalid tool name cannot strand a reserved lease.
- **`K-05` (S8 inside guard)**: Grant verification occurs immediately before physical execution, preventing replayed, expired, or swapped tokens.
- **`K-47` (S8a Intent Logging)**: `EffectStarted` is durably committed and synced to the ledger *before* calling `adapter.execute()`. If a crash occurs during physical execution, the effect is flagged as *undeterminable* upon recovery rather than disappearing silently (`INV-B-003`).
- **`K-06` (S11 precedes S12)**: Lease release occurs in `finally` before terminal event emission. A leaked lease is treated as more severe than an emission failure.
- **`K-07` (S10 Overrun Accounting)**: `commit` debits actual observed physical consumption even if it exceeded the original reservation.

---

## 3. Capability Monotonic Attenuation

The capability model enforces monotonic attenuation: child scopes can only maintain or reduce rights, never widen them (`INV-B-004`).

- **Lattice Scoping**: A `Scope` carries permitted action prefixes, resource ceilings, network permissions, and workspace constraints.
- **Descriptor Binding**: A `Grant` is cryptographically bound to `descriptor_digest = SHA256(JCS(action, args))`. A grant issued for file read cannot be used to execute a shell command or read a different path.

---

## 4. Typed Budget Algebra

Budgets in Vanguard are strictly partitioned into additive resources and structural limits (`INV-B-005`):

### Additive Resources (`Governor`)
- **`usd_micros`**: Financial cost (micro-USD).
- **`millis`**: Wall-clock execution time.
- **`tokens`**: Model prompt and completion tokens.
- **`bytes`**: Workspace and storage I/O volume.

These four quantities support additive debiting, reservations, commits, and refunds.

### Structural Ceilings
- **`turns`** and **`depth`** are structural limits enforced by the turn engine and recursion manager, not fungible debited currencies.

---

## 5. Failure Semantics & Undeterminacy

Kernel execution maps every exit to an explicit `FailurePath` entry (`05 §2.3`):

| Failure Category | Kernel Response | Ledger Consequence |
|---|---|---|
| Schema Mismatch (S1) | Reject immediately | `EffectRejected` emitted; zero leases allocated. |
| Policy Denied (S5) | Deny request | `EffectRejected` or `AuthorizationDenied`. |
| Budget Exhausted (S7) | Halt request | `BudgetExhausted` emitted; run enters suspension. |
| Approval Required | Suspend execution | `AuthorizationRequested` with `SuspensionToken`. |
| Adapter Crash (S9) | Catch exception | `EffectFailed` emitted; lease released at S11. |
| System Crash (S9 crash) | Crash recovery | `EffectStarted` without matching completed event lowers to `EffectReconciled` during recovery. |

---

## Implementation Evidence

- **Kernel Core**: `vanguard/packages/kernel/` (`dispatch.py`, `grants.py`, `budget.py`, `attenuation.py`, `policy.py`, `classifier.py`, `provenance.py`, `model.py`).
- **Budget Linter**: `tools/linters/check_tcb_budget.py` ($\le 1438$ LOC).
- **Domain Blindness Linter**: `tools/linters/check_domain_blindness.py`.
- **Falsification Tests**: `test/kernel/test_dispatch.py`, `test/kernel/test_attenuation.py`, `test/kernel/test_grant_budget_events.py`.
