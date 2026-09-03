---
id: guide.compose-agent
canonical_id: guide.compose-agent
class: how-to
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: guides-developer
canonical_for:
  - composition procedure
  - identity/validation checks
  - test procedure
purpose: Step-by-step developer guide for creating, configuring, validating, and executing custom agent pack compositions.
audience:
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-012
  - E-B-019
  - E-B-020
  - E-B-021
  - E-B-022
  - E-B-023
  - E-B-024
  - E-B-026
  - E-B-050
  - E-B-053
  - E-B-054
relationships:
  - arch.composition.extensibility
  - arch.agency.turns
  - ref.manifests
reviewer: documentation-specialist
confidence: high
---

# Compose an Agent Pack Guide

## Purpose
This guide is the canonical owner for the end-to-end procedure of authoring, configuring, compiling, validating, and testing a custom domain agent pack.

## Scope
- Choosing a base pack template (`packs/code-default/`).
- Authoring `manifest.json` conforming to `mhf.manifest/2`.
- Binding custom SPI component classes (`IPlanner`, `IContextManager`, `IToolkit`, `IMemoryEngine`).
- Validating immutable composition digests ($D_H$).
- Executing hermetic tests against custom agent compositions.

## Non-responsibilities
- Detailed manifest schema field reference (owned by [`ref.manifests`](../reference/manifests.md)).
- Hexagonal boundary theoretical constraints (owned by [`arch.composition.extensibility`](../architecture/composition-extensibility.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Declarative composition compiler and pack loader are fully operational in `vanguard.packages.runtime.compose`.

---

## 1. Choose a Base Pack

Create a new directory under `packs/` or clone an existing pack:

```bash
cp -r packs/code-default packs/my-agent
```

Pack structure:
```text
packs/my-agent/
├── manifest.json
├── __init__.py
├── planner.py
├── context.py
├── tools.py
└── test/
```

---

## 2. Configure `manifest.json`

Define the agent pack properties in `packs/my-agent/manifest.json`:

```json
{
  "api": "mhf.manifest/2",
  "id": "my-custom-agent",
  "name": "Custom Domain Agent",
  "version": "0.1.0",
  "description": "Specialized agent pack with domain tools",
  "entrypoint": "agent",
  "components": {
    "planner": "packs.my_agent.planner:CustomPlanner",
    "context_manager": "packs.my_agent.context:CustomContextManager",
    "toolkit": "packs.my_agent.tools:CustomToolkit",
    "memory": "vanguard.packages.adapters.stores.memory_engine:SqliteMemoryEngine"
  },
  "tools": [
    {
      "name": "custom_search",
      "description": "Execute specialized domain search",
      "schema": {
        "type": "object",
        "required": ["query"],
        "properties": {
          "query": { "type": "string" }
        }
      },
      "category": "domain_search"
    }
  ]
}
```

---

## 3. Implement SPI Components

Ensure all declared components implement the corresponding SPI protocols (`vanguard.packages.ports.spi`):
- `planner.py`: Subclass `IPlanner` (implement `plan`, `observe`, `reflect`).
- `context.py`: Subclass `IContextManager` (implement `compile`, `ingest`, `compact`).
- `tools.py`: Subclass `IToolkit` (implement `verbs`, `execute`, `health`).

---

## 4. Validate and Compile Composition

Verify the manifest syntax and compile the immutable composition:

```bash
# Validate using TypeScript CLI
vg composition --path packs/my-agent/manifest.json

# Or test composition via Python runtime
python3 -c "
from vanguard.packages.runtime.compose import compose_harness
composition = compose_harness("packs/my-agent/manifest.json")
print("Composition Digest (D_H):", composition.digest)
"
```

---

## 5. Execute Hermetic Tests

Write a test under `packs/my-agent/test/` to verify deterministic execution with fakes:

```python
import unittest
from vanguard.packages.runtime.compose import compose_harness
from vanguard.packages.runtime.session import HarnessSession
from vanguard.packages.runtime.profiles import PRESETS

class TestCustomAgent(unittest.TestCase):
    def test_agent_run(self):
        comp = compose_harness("packs/my-agent/manifest.json")
        session = HarnessSession.create(
            composition=comp,
            profile=PRESETS["local"],
            task_brief="Test run",
        )
        result = session.run()
        self.assertEqual(result.termination, "COMPLETED")
```

Run test:
```bash
python3 -m unittest discover -s packs/my-agent/test
```

---

## 6. Common Failure Cases

| Failure | Root Cause | Solution |
|---|---|---|
| `ManifestValidationError` | Missing required fields in `manifest.json`. | Ensure `api: "mhf.manifest/2"` and all required keys exist (`ref.manifests`). |
| `SPISignatureMismatch` | Component class does not implement all required SPI methods. | Check method signatures against `ports/spi.py` (`ref.ports`). |
| `BoundaryViolationError` | Pack imports forbidden internal kernel modules. | Ensure pack imports only `domain`, `ports`, and standard library. |

---

## Related Documentation
- [Composition & Extensibility Architecture](../architecture/composition-extensibility.md)
- [Manifests Reference](../reference/manifests.md)
- [Add a Pack or Tool Guide](add-pack-or-tool.md)
