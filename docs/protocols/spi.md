---
status: living
id: protocol-spi-protocols
class: protocol-reference
authority: descriptive
canonical_for:
  - spi-protocols-reference
source_of_truth:
  - docs/SPEC.md#2-plugin-architecture--spi-definitions
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

## 1. The five standard SPI interfaces

The exact protocols exported by `ports/spi.py` are:

1. **`IPlanner`** — turn-level proposal planning, observation, and reflection.
2. **`IContextManager`** — context compilation, receipt ingestion, compaction, and regrounding.
3. **`IToolkit`** — verb schemas, effect execution, compensation, and health.
4. **`IMemoryEngine`** — write, recall, consolidation, invalidation, and declared capabilities.
5. **`IEvaluationGate`** — requests exterior judgment and returns gate decisions; it does not mint verdict authority.

These Python protocols are client conveniences for the wire contract, not a second authority surface.
