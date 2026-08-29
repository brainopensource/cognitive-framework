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
version: "0.9.0b1"
last_verified: 2026-08-26
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Conserved Resource Vector and Structural Ceilings

> **Status:** `AS_BUILT` · Governed by ADR-0074.

---

## Tensor Structure

Resource allocation across recursive child lineages is modeled as a four-dimensional additive vector
plus two independent structural ceilings:

$$\mathbf{C} = \begin{pmatrix} \text{usd\_micros} \\ \text{millis} \\ \text{tokens} \\ \text{bytes} \end{pmatrix},\qquad depth,turns\in\mathbb{N}_0$$

### Conservation Laws
For any root task $P$ spawning subagent tasks $\{C_1, C_2, \dots, C_n\}$:

1. **Additive Invariant**:
   $$\sum_{i=1}^n \mathbf{C}_{\text{consumed}}^{(C_i)} + \mathbf{C}_{\text{remaining}}^{(P)} = \mathbf{C}_{\text{allocated}}^{(P)}$$

2. **Structural Depth Bound**:
   $$d(C_i) = d(P) + 1 \le d_{\max}$$
