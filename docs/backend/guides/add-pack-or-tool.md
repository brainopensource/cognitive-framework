---
id: guide.add-pack-tool
canonical_id: guide.add-pack-tool
class: how-to
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: guides-developer
canonical_for:
  - pack/tool addition procedure
  - binding/schema/test checklist
purpose: Step-by-step developer guide for adding a new tool to an existing pack or creating a new tool pack.
audience:
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-012
  - E-B-017
  - E-B-021
  - E-B-050
  - E-B-053
  - E-B-054
relationships:
  - arch.composition.extensibility
  - ref.manifests
  - ref.ports
  - guide.compose-agent
reviewer: documentation-specialist
confidence: high
---

# Add a Pack or Tool Guide

## Purpose
This guide is the canonical owner for operational developer procedures to declare, implement, register, and test a new tool within an agent pack.

## Scope
- Declaring tool JSON schemas in `manifest.json`.
- Implementing tool handlers in `IToolkit` (`tools.py`).
- Setting capability category and approval requirement flags.
- Writing hermetic unit tests with mock receipts.
- Boundary compliance checks.

## Non-responsibilities
- Kernel TCB S0–S12 effect dispatch pipeline internals (owned by [`arch.trust.kernel`](../architecture/kernel.md)).
- Port SPI interface specifications (owned by [`ref.ports`](../reference/ports.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Tool declaration via `mhf.manifest/2` and execution through `IToolkit` are fully operational across all packs.

---

## 1. Tool Declaration Checklist

To add a tool to an existing pack (e.g. `packs/code-default/`):

1. **Open `manifest.json`**: Add the tool definition to the `tools` array:

```json
{
  "name": "calculate_hash",
  "description": "Compute SHA-256 hash of a specified file",
  "category": "fs_read",
  "requires_approval": false,
  "schema": {
    "type": "object",
    "required": ["filepath"],
    "properties": {
      "filepath": {
        "type": "string",
        "description": "Path to target file within workspace"
      }
    },
    "additionalProperties": false
  }
}
```

---

## 2. Implement the Tool Handler (`tools.py`)

In `packs/<pack_name>/tools.py`, add the execution logic to the pack toolkit:

```python
import hashlib
from pathlib import Path
from vanguard.packages.domain.wire.result import Ok, Err, Result
from vanguard.packages.ports.spi import IToolkit
from vanguard.packages.domain.wire.types_gen import EffectRequest, EffectContext, Receipt

class CustomToolkit(IToolkit):
    def verbs(self):
        return {
            "calculate_hash": { ... }
        }

    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]:
        if request.action == "calculate_hash":
            filepath = request.args.get("filepath")
            target = Path(ctx.workspace_root) / filepath
            if not target.exists():
                return Err(f"File not found: {filepath}")
            
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            return Ok(Receipt(
                action=request.action,
                status="success",
                output={"sha256": digest}
            ))
        return Err(f"Unknown action: {request.action}")

    def compensate(self, receipt: Receipt) -> Result[Receipt]:
        # Read-only tools require no compensation
        return Ok(receipt)

    def health(self):
        return "healthy"
```

---

## 3. Testing the New Tool

Write a hermetic unit test in `test/packs/test_custom_tools.py`:

```python
import unittest
from vanguard.packages.domain.wire.types_gen import EffectRequest, EffectContext
from packs.code_default.tools import CodeToolkit

class TestCustomTool(unittest.TestCase):
    def test_calculate_hash(self):
        toolkit = CodeToolkit()
        ctx = EffectContext(workspace_root="/tmp", run_id="test")
        req = EffectRequest(action="calculate_hash", args={"filepath": "test.txt"})
        
        # Test tool response
        result = toolkit.execute(req, ctx)
        self.assertTrue(result.is_ok())
```

---

## 4. Boundary Compliance Check

Run repository linters to verify that the new tool does not violate architectural rules:

```bash
# Verify hexagonal boundaries
python3 tools/linters/check_boundaries.py

# Verify TCB budget is unaffected
python3 tools/linters/check_tcb_budget.py
```

---

## Related Documentation
- [Hexagonal Ports Reference](../reference/ports.md)
- [Manifests Reference](../reference/manifests.md)
- [Compose an Agent Guide](compose-an-agent.md)
