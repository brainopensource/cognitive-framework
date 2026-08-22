---
status: living
id: protocol-sandbox-port
class: protocol-reference
authority: descriptive
canonical_for:
  - sandbox-port-protocol
source_of_truth:
  - docs/04_annex/KERNEL.md#1-the-trusted-computing-base
derived_from:
  - vanguard/packages/ports/sandbox.py
  - vanguard/packages/adapters/sandbox/rootless.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Sandbox Port Protocol (`SandboxRunner`)

> **Source:** [`vanguard/packages/ports/sandbox.py`](../../vanguard/packages/ports/sandbox.py)  
> **Status:** `AS_BUILT` · Owning contract: ICD §4 SandboxRunner, REQ-PORT-005.

---

## Interface Definition

```python
class SandboxRunner(Protocol):
    """Execute argv inside a perimeter and return receipt plus containment report."""

    def execute(self, argv: Sequence[str]) -> Result[SandboxResult]:
        ...
```

## Security Invariants & Probes
- **Containment Probes**: `ContainmentReport` requires verified startup probes (`mount`, `egress`, `syscall`).
- **Publication Gate**: `publication_decision(report)` refuses publication fail-closed if `report.verified` is false (K-44).
- **Isolation Policy (Invariant I-6)**: Untrusted execution runs in rootless Bubblewrap (UID `10001`) with read-only root and tmpfs workspaces.
