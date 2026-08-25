---
status: living
id: protocol-kernel-port
class: protocol-reference
authority: descriptive
canonical_for:
  - kernel-port-protocol
source_of_truth:
  - docs/01_law/DISPATCH.md
derived_from:
  - vanguard/packages/ports/kernel.py
  - vanguard/packages/kernel/dispatch.py
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

# Kernel Port Interfaces (`ports/kernel.py`) & Dispatch Entrypoint

> **Source:** [`vanguard/packages/ports/kernel.py`](../../vanguard/packages/ports/kernel.py) & [`vanguard/packages/kernel/dispatch.py`](../../vanguard/packages/kernel/dispatch.py)
> **Status:** `AS_BUILT` · TCB Boundary Interfaces.

---

## 1. Ports the Kernel Depends On (`ports/kernel.py`)

Per hexagonal dependency inversion, the kernel core depends on four narrow ports and implements none of them:

```python
@runtime_checkable
class Clock(Protocol):
    """Injected monotone time (domain forbids system clocks)."""
    def now(self) -> str: ...

@runtime_checkable
class EffectAdapter(Protocol):
    """One typed effect adapter."""
    name: str
    def healthy(self) -> bool: ...
    def execute(self, request: Any) -> Any: ...

@runtime_checkable
class EventSink(Protocol):
    """Kernel event emission sink (F-25: failure never fails an effect)."""
    def emit(self, event: Any) -> None: ...

@runtime_checkable
class Ledger(Protocol):
    """Durable intent persistence (K-47), written before effect execution."""
    def append_intent(self, event: Any) -> None: ...
```

---

## 2. Kernel dispatch entrypoint (`kernel/dispatch.py`)

`Kernel` receives adapters, policy, classifier, `Governor`, grant issuer, clock, ledger, event sink,
and optional sink registry at construction. `Kernel.dispatch(request, *, requested_scope,
reservation, spans=None, cross_process=False, purpose_digest=...)` executes the S1–S12 reference
monitor sequence and returns `DispatchResult`. Refer to the source for the exact signature rather
than copying it into a second API definition.

## Security Guarantees
- **Domain-Blind (Invariant I-7)**: Kernel contains zero domain tokens (`coding`, `pytest`, `ast`).
- **Fail-Closed (K-01)**: Any unrecognized verb, out-of-bounds selector, or budget exhaustion raises an immediate rejection.
