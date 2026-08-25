---
status: living
id: protocol-model-port
class: protocol-reference
authority: descriptive
canonical_for:
  - model-port-protocol
source_of_truth:
  - docs/SPEC.md
derived_from:
  - vanguard/packages/ports/model.py
  - vanguard/packages/adapters/models/openrouter.py
  - vanguard/packages/adapters/models/ollama.py
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

# Model Port Protocol (`ModelPort`)

> **Source:** [`vanguard/packages/ports/model.py`](../../vanguard/packages/ports/model.py)  
> **Status:** `AS_BUILT` · Owning contract: ICD §4 ModelProvider, REQ-PORT-002.

---

## Interface Definition

```python
class ModelPort(Protocol):
    """Inference seam for model proposal generation."""

    def propose(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        """Return a proposal, or a typed instrument error."""
        ...
```

## Supported Adapters
1. **OpenRouter (`adapters/models/openrouter.py`)**: Remote multi-provider router.
2. **Ollama (`adapters/models/ollama.py`)**: Local open-weights daemon.
3. **Cassette (`adapters/models/cassette.py`)**: Deterministic replay for hermetic CI.
4. **Fake (`adapters/models/fake.py`)**: In-memory test doubles.

## Authority and accounting boundary

`ModelPort.propose()` generates cognition; it is not an S0–S12 environment-effect verb. Every
concrete effect contained in the returned proposal still enters the canonical dispatcher. A remote
adapter MUST use only the route, egress policy, credential reference, and budget ceiling frozen at
composition. Credentials are adapter-private and MUST NOT appear in the context bundle, ledger, or
trajectory.

The runtime accounts each call attempt—including retries, fallback, and escalation—as one ordered
`invocations` entry. Provider/model route, fingerprint or typed absence, usage provenance, latency,
and `measured`/`estimated`/`unavailable` status follow
[`EVIDENCE.md`](../01_law/EVIDENCE.md#trajectory-accounting). Unknown cost is never zero. RF-23 is
the current conservation and attribution falsifier.
