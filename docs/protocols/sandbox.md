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

# Sandbox Port Protocol (`SandboxPort`)

> **Source:** [`vanguard/packages/ports/sandbox.py`](../../vanguard/packages/ports/sandbox.py)  
> **Status:** `AS_BUILT` · Isolation Boundary (UID 10001).

---

## Interface Definition

```python
class SandboxPort(Protocol):
    def execute(
        self,
        command: Sequence[str],
        cwd: Path,
        grant: CapabilityGrant,
        timeout_seconds: float,
    ) -> SandboxExecutionResult:
        """Execute command inside rootless Bubblewrap container under capability constraints."""
        ...
```

## Security Constraints
- **Rootless bubblewrap**: Run as UID `10001` with unshared PID, network, and mount namespaces.
- **Read-only root**: Host system files mounted strictly read-only.
- **Ephemeral tmpfs**: Writes isolated to `/workspace` tmpfs mount.
