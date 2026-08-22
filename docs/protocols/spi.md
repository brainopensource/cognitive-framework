---
status: living
id: protocol-spi-protocols
class: protocol-reference
authority: descriptive
canonical_for:
  - spi-protocols-reference
source_of_truth:
  - docs/SPEC.md#3-hexagonal-production-lattice
  - docs/05_adr/0076-foundation-execution-decisions-canonical-artifacts.md
derived_from:
  - vanguard/packages/ports/spi.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Five Standard SPI Protocols (`ports/spi.py`)

> **Source:** [`vanguard/packages/ports/spi.py`](../../vanguard/packages/ports/spi.py)  
> **Status:** `AS_BUILT` · Governed by ADR-M0-03 / ADR-0076.

---

## 1. The Five Standard SPI Interfaces

The substrate standardizes 5 Service Provider Interfaces:
1. **`ToolSPI`**: Plug-in tool execution.
2. **`ModelSPI`**: Model inference adapter.
3. **`MemorySPI`**: Long-term state & vector storage.
4. **`SandboxSPI`**: Process & container isolation.
5. **`EvaluatorSPI`**: Independent grading & signed verification.
