---
status: living
id: contract-selectors-and-budgets
class: contract-reference
authority: descriptive
canonical_for:
  - selector-algebra-and-budgets
source_of_truth:
  - docs/01_law/DISPATCH.md
  - docs/02_decisions/0074-gamma-lock-amendments-proof-budget-writer-identity.md
derived_from:
  - vanguard/packages/domain/selectors/resource_selector.py
  - vanguard/packages/kernel/budget.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-23
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Selector Algebra & 6D Budget Contract

> **Implementation:** [`resource_selector.py`](../../vanguard/packages/domain/selectors/resource_selector.py) and [`budget.py`](../../vanguard/packages/kernel/budget.py)  
> **Status:** `AS_BUILT` · Governed by ADR-0074 / ADR-0076.

---

## Canonical algebra

The selector partial order and six budget dimensions are defined normatively only in
[`RUNTIME.md` §1.0](../01_law/RUNTIME.md#10-recursive-machine-authority-and-identity-adr-0070-adr-0071-adr-0074) and
[`DISPATCH.md` §4](../01_law/DISPATCH.md#4-attenuation). ADR-0074 records why additive
resources and structural ceilings are distinct. This page intentionally does not repeat their matrix.

Executable behavior lives in
[`resource_selector.py`](../../vanguard/packages/domain/selectors/resource_selector.py) and
[`budget.py`](../../vanguard/packages/kernel/budget.py). Implementations must preserve fail-closed
comparison, empty-ceiling denial, component-wise conservation for additive resources, and the
non-additive semantics of depth and turn ceilings.
