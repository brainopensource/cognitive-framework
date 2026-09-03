---
id: guide.add-adapter-provider
canonical_id: guide.add-adapter-provider
class: how-to
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: guides-developer
canonical_for:
  - adapter/provider procedure
  - factory/bootstrap integration
  - hermetic tests
purpose: Step-by-step developer guide for implementing a new hexagonal adapter or model provider.
audience:
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-017
  - E-B-024
  - E-B-025
  - E-B-052
relationships:
  - arch.composition.extensibility
  - ref.ports
  - ref.configuration
reviewer: documentation-specialist
confidence: high
---

# Add an Adapter or Provider Guide

## Purpose
This guide is the canonical owner for developer procedures to implement a new infrastructure adapter (e.g. model provider, sandbox isolation backend, store engine) satisfying hexagonal port protocols.

## Scope
- Selecting a target port in `vanguard.packages.ports`.
- Implementing the adapter in `vanguard.packages.adapters`.
- Registering adapter factories in `bootstrap.py`.
- Authoring hermetic unit tests with recorded cassettes or fakes.
- Security and credential isolation checks.

## Non-responsibilities
- Complete port protocol method signatures (owned by [`ref.ports`](../reference/ports.md)).
- Configuration and environment variable tables (owned by [`ref.configuration`](../reference/configuration.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Pluggable adapter architecture operating behind hexagonal ports.

---

## 1. Select the Target Port Protocol

Identify the port in `vanguard/packages/ports/`:
- `ModelPort` (`ports/model.py`): For LLM inference providers.
- `SandboxPort` (`ports/sandbox.py`): For process isolation environments.
- `EventStorePort` (`ports/event_store.py`): For event storage engines.
- `BlobStorePort` (`ports/blob_store.py`): For artifact storage.

---

## 2. Implement the Adapter (`vanguard/packages/adapters/`)

Create your adapter file in `vanguard/packages/adapters/<subsystem>/<name>.py`:

```python
from typing import Iterator
from vanguard.packages.ports.model import ModelPort, ModelRequest, ModelResponse, ModelStreamChunk

class CustomModelAdapter(ModelPort):
    def __init__(self, endpoint: str, api_key: str | None = None):
        self.endpoint = endpoint
        self.api_key = api_key

    def generate(self, request: ModelRequest) -> ModelResponse:
        # Call provider API
        ...
        return ModelResponse(
            content="...",
            usage={"prompt_tokens": 10, "completion_tokens": 20},
            model_id=request.model_id
        )

    def stream(self, request: ModelRequest) -> Iterator[ModelStreamChunk]:
        ...
```

### Critical Boundary Invariant
Adapters **must never import `kernel` or `agency`** (`INV-B-001`). Adapters import only `domain` and `ports`.

---

## 3. Register in Bootstrap Factory (`runtime/bootstrap.py`)

Wire the adapter into the runtime model resolver:

```python
# vanguard/packages/runtime/bootstrap.py
def resolve_model_adapter(model_spec: str) -> ModelPort:
    if model_spec.startswith("custom:"):
        return CustomModelAdapter(endpoint="...")
    ...
```

---

## 4. Author Hermetic Tests

Never commit live API keys or write tests that make live network calls during automated test runs (`scan_secrets.py`):

```python
import unittest
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.ports.model import ModelRequest

class TestCustomModel(unittest.TestCase):
    def test_fake_inference(self):
        adapter = FakeModel(responses=["Hello world"])
        resp = adapter.generate(ModelRequest(prompt="Test"))
        self.assertEqual(resp.content, "Hello world")
```

---

## 5. Security & Boundary Checklist

Before submitting changes:

```bash
# 1. Boundary check (ensures no kernel/agency imports in adapters)
python3 tools/linters/check_boundaries.py

# 2. Secret scan (ensures no committed API keys)
python3 tools/linters/scan_secrets.py

# 3. Full test discovery
python3 -m unittest discover -s test/contracts -t .
```

---

## Related Documentation
- [Hexagonal Ports Reference](../reference/ports.md)
- [Configuration Reference](../reference/configuration.md)
- [Composition Architecture](../architecture/composition-extensibility.md)
