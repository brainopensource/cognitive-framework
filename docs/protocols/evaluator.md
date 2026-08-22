---
status: living
id: protocol-evaluator-port
class: protocol-reference
authority: descriptive
canonical_for:
  - evaluator-port-protocol
source_of_truth:
  - docs/SPEC.md#1-system-charter-and-boundaries
derived_from:
  - vanguard/packages/ports/evaluator.py
  - vanguard/packages/adapters/evaluators/daemon.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Evaluator Port Protocol (`EvaluatorPort`)

> **Source:** [`vanguard/packages/ports/evaluator.py`](../../vanguard/packages/ports/evaluator.py)  
> **Status:** `AS_BUILT` · Exterior Verifier Boundary (UID 10002).

---

## Interface Definition

```python
class EvaluatorPort(Protocol):
    def grade(
        self,
        request: EvaluationRequest,
    ) -> SignedVerdict:
        """Request signed evaluation verdict from exterior evaluator daemon."""
        ...
```

## Guarantees
- Evaluator runs in UID `10002` with independent memory and mounts.
- Produces Ed25519 cryptographic signatures over JCS canonical bytes.
