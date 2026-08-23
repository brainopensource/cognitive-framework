---
status: living
id: protocol-spi-protocols
class: protocol-reference
authority: descriptive
canonical_for:
  - spi-protocols-reference
source_of_truth:
  - docs/SPEC.md#2-plugin-architecture--spi-definitions
  - docs/02_decisions/0076-foundation-execution-decisions-canonical-artifacts.md
derived_from:
  - vanguard/packages/ports/spi.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Five Standard SPI Protocols (`ports/spi.py`)

> **Source:** [`vanguard/packages/ports/spi.py`](../../vanguard/packages/ports/spi.py)  
> **Status:** `AS_BUILT` · Governed by ADR-M0-03 / ADR-0076.

---

## Canonical interface roster

The normative five-SPI roster and method contracts live only in
[`RUNTIME.md` §2.2](../01_law/RUNTIME.md#22-spi-definitions-typed-frozen-versioned). The executable Python surface
is [`ports/spi.py`](../../vanguard/packages/ports/spi.py); this page intentionally does not maintain a
second interface list. Those protocols are client conveniences for the wire contract, not a second
authority surface. Transport behavior, including direct in-memory `in_process` dispatch, is governed
by [`RUNTIME.md` §2.1](../01_law/RUNTIME.md#21-plugin-model) and ADR-0072.
