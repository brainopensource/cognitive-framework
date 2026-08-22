---
status: living
id: protocol-kernel-port
class: protocol-reference
authority: descriptive
canonical_for:
  - kernel-port-protocol
source_of_truth:
  - docs/04_annex/KERNEL.md
derived_from:
  - vanguard/packages/ports/kernel.py
  - vanguard/packages/kernel/dispatch.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
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

## 2. Kernel Dispatch Entrypoint (`kernel/dispatch.py`)

The kernel trusted computing base exports the 13-stage dispatch pipeline:

```python
def dispatch(
    intent: IntentRequest,
    justification: JustificationContext,
    *,
    clock: Clock,
    adapter: EffectAdapter,
    ledger: Ledger,
    sink: EventSink,
    policy: PolicyEngine,
    budget: BudgetEngine,
) -> DispatchReceipt:
    """Execute the 13-stage pipeline (S0–S12) fail-closed."""
    ...
```

## Security Guarantees
- **Domain-Blind (Invariant I-7)**: Kernel contains zero domain tokens (`coding`, `pytest`, `ast`).
- **Fail-Closed (K-01)**: Any unrecognized verb, out-of-bounds selector, or budget exhaustion raises an immediate rejection.
