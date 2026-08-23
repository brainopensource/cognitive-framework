---
status: living
id: theory-trajectory-credit
class: theory
authority: descriptive
canonical_for:
  - trajectory-credit-assignment
source_of_truth:
  - docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS.md
  - docs/05_adr/0078-trajectory-un-hollowing-cost-accounting.md
derived_from:
  - docs/06_references/
applies_to:
  - v0.6.1
implementation_status: RESEARCH
owner: cognitive-systems-researcher
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Trajectory Error Credit Assignment

> **Status:** `RESEARCH` · Target Milestone: **M-10**.

---

## Backward Fault Isolation Algorithm

Given an execution episode trajectory $\mathcal{T} = \{(s_0, a_0, r_0), (s_1, a_1, r_1), \dots, (s_T, a_T, r_T)\}$ and a terminal exterior signed verdict $V \in \{\text{pass}, \text{fail}\}$:

$$\mathcal{C}(a_t) = \nabla_{a_t} \mathcal{L}(V, \mathcal{T}) = \sum_{\tau=t}^T \gamma^{\tau - t} \cdot \delta_{\tau}$$

Where:
- $\delta_\tau = r_\tau + \gamma V(s_{\tau+1}) - V(s_\tau)$ is the temporal difference error.
- $\mathcal{C}(a_t)$ attributes blame or credit to individual turn actions without confounding upstream prompts.
