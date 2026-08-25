---
status: living
id: protocol-evaluator-port
class: protocol-reference
authority: descriptive
canonical_for:
  - evaluator-port-protocol
source_of_truth:
  - docs/SPEC.md
  - docs/02_decisions/0072-plugin-boundary-wire-first-evaluator-exterior.md
derived_from:
  - vanguard/packages/ports/evaluator.py
  - vanguard/packages/adapters/evaluators/daemon.py
applies_to:
  - v0.6.2
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.2"
last_verified: 2026-08-23
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Evaluator Port Protocol (`EvaluatorPort`)

> **Source:** [`vanguard/packages/ports/evaluator.py`](../../vanguard/packages/ports/evaluator.py)  
> **Status:** `AS_BUILT` · Owning contract: ICD §4 EvaluatorPort, REQ-PORT-004, ADR-0048.

---

## Interface Definition

```python
class EvaluatorPort(Protocol):
    """Exterior evaluation seam. Agency has no import path here."""

    def evaluate(
        self,
        run_ref: RunRef,
        protocol: EvaluationProtocol,
    ) -> Result[Verdict]:
        """Return fixed claims, or an inconclusive verdict on instrument error."""
        ...
```

## Verdict Contract & Cryptographic Binding
```python
@dataclass(frozen=True, slots=True)
class Verdict:
    outcome: str  # "claims" | "inconclusive"
    claims: tuple[Mapping[str, Any], ...] = ()
    reason: str = ""
    signature: str | None = None
    signer_key_id: str | None = None
    binding: Mapping[str, Any] | None = None
```
- **Binding Rule**: `runtime/evaluator_gateway.py` refuses to ledger a `VerdictRecorded` without an Ed25519 cryptographic signature over canonical JCS bytes.
- **Foundation Rule**: the M-4 auditor verifies the exterior signature and its canonical lineage
  bindings itself; it never promotes a caller-supplied boolean to evidence.
