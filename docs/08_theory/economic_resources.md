---
status: living
id: theory-economic-resources
class: theory
authority: descriptive
canonical_for:
  - economic-resource-tensor
source_of_truth:
  - docs/01_law/DISPATCH.md#4-attenuation
  - docs/02_decisions/0074-gamma-lock-amendments-proof-budget-writer-identity.md
derived_from:
  - vanguard/packages/kernel/budget.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: cognitive-systems-researcher
version: "0.6.1"
last_verified: 2026-08-21
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# The 6D Economic Resource Tensor

> **Status:** `AS_BUILT` · Governed by ADR-0074.

---

## Tensor Structure

Resource allocation across recursive child agent trees is modeled as a 6-dimensional tensor:

$$\mathbf{R} = \begin{pmatrix} u \\ t \\ b \\ m \\ d \\ k \end{pmatrix} = \begin{pmatrix} \text{usd\_micros} \\ \text{tokens} \\ \text{bytes} \\ \text{charged\_millis} \\ \text{depth} \\ \text{turns} \end{pmatrix}$$

### Conservation Laws
For any root task $P$ spawning subagent tasks $\{C_1, C_2, \dots, C_n\}$:

1. **Additive Invariant**:
   $$\sum_{i=1}^n \mathbf{R}_{\text{consumed}}^{(C_i)} + \mathbf{R}_{\text{remaining}}^{(P)} = \mathbf{R}_{\text{allocated}}^{(P)} \quad \forall \text{ dimensions } \{u, t, b, m\}$$

2. **Structural Depth Bound**:
   $$d(C_i) = d(P) + 1 \le d_{\max}$$
