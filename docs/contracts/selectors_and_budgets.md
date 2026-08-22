---
status: living
id: contract-selectors-and-budgets
class: contract-reference
authority: descriptive
canonical_for:
  - selector-algebra-and-budgets
source_of_truth:
  - docs/04_annex/KERNEL.md
  - docs/05_adr/0074-gamma-lock-amendments-proof-budget-writer-identity.md
derived_from:
  - vanguard/packages/domain/selectors/resource_selector.py
  - vanguard/packages/kernel/budget.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Selector Algebra & 6D Budget Contract

> **Implementation:** [`resource_selector.py`](../../vanguard/packages/domain/selectors/resource_selector.py) and [`budget.py`](../../vanguard/packages/kernel/budget.py)  
> **Status:** `AS_BUILT` · Governed by ADR-0074 / ADR-0076.

---

## 1. Monotonic Selector Algebra

Selectors declare bounded permission scopes over resources:
- **`fs`**: Path globs under authorized root (e.g., `["/workspace/**"]`).
- **`generic`**: URI patterns (e.g., `["proc://exec/allow/git,pytest,ruff,python3"]`).

### Containment Rules
$$\text{ChildSelector} \subseteq \text{ParentSelector}$$
- Child grants must be an exact subset of the parent.
- An empty ceiling denies all requests (`empty_ceiling`).
- Unbounded child request under a bounded parent is denied fail-closed.

---

## 2. 6D Typed Budget Algebra

Budgets distinguish additive consumed resources from non-additive structural ceilings:

| Dimension | Type | Algebraic Rule |
|---|---|---|
| `usd_micros` | **Additive** | $\text{Child} + \text{Remaining} \le \text{Parent}$ |
| `tokens` | **Additive** | $\text{Child} + \text{Remaining} \le \text{Parent}$ |
| `bytes` | **Additive** | $\text{Child} + \text{Remaining} \le \text{Parent}$ |
| `millis` | **Additive** | Charged compute milliseconds; $\text{Child} + \text{Remaining} \le \text{Parent}$ |
| `depth` | **Structural** | $\text{ChildDepth} = \text{ParentDepth} + 1 \le \text{MaxDepth}$ (Siblings not summed) |
| `turns` | **Structural** | Max turns allowed for current subagent turn loop |
