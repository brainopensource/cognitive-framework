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

# Kernel Port Protocol (`KernelPort`)

> **Source:** [`vanguard/packages/ports/kernel.py`](../../vanguard/packages/ports/kernel.py)  
> **Status:** `AS_BUILT` · TCB Boundary Interface.

---

## Interface Definition

```python
class KernelPort(Protocol):
    def dispatch(
        self,
        intent: IntentRequest,
        justification: JustificationContext,
    ) -> DispatchReceipt:
        """Execute the 13-stage dispatch pipeline (S0–S12) fail-closed."""
        ...
        
    def attenuate(
        self,
        parent_grant: CapabilityGrant,
        requested_subset: CapabilityDescriptor,
    ) -> CapabilityGrant:
        """Monotonically attenuate a capability grant."""
        ...
```

## Security Guarantees
- **Domain-Blind (Invariant I-7)**: Kernel contains zero domain tokens (`coding`, `pytest`, `ast`).
- **Fail-Closed (K-01)**: Any unrecognized verb, out-of-bounds selector, or budget exhaustion raises an immediate rejection.
