---
status: living
id: theory-active-inference
class: theory
authority: descriptive
canonical_for:
  - active-inference-theory
source_of_truth:
  - docs/_archive/references/RESEARCH_THEORETICAL_SYNTHESIS.md
  - docs/02_decisions/0084-compounding-macro-tools-active-inference.md
derived_from:
  - docs/_archive/references/
applies_to:
  - v0.6.1
implementation_status: RESEARCH
owner: cognitive-systems-researcher
version: "0.6.1"
last_verified: 2026-08-21
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Active Inference & Free Energy Minimization

> **Status:** `RESEARCH` · Target Milestone: **M-10** (Governed by ADR-0084).

---

## Mathematical Formulation

In Vanguard / AETHER, the turn loop operates as an Active Inference engine minimizing Variational Free Energy $\mathcal{F}(\theta)$ during perception and Expected Free Energy $\mathcal{G}(\pi)$ during action selection.

### 1. Variational Free Energy (Perception & Belief Fitting)
$$\mathcal{F}(\theta) = \mathbb{E}_{q_\theta(s)} \left[ \ln q_\theta(s) - \ln p(o, s) \right] = D_{\mathrm{KL}}\Big(q_\theta(s) \parallel p(s \mid o)\Big) - \ln p(o)$$

- **$\ln p(o)$**: Log evidence of observed environment state.
- **$D_{\mathrm{KL}}$**: Divergence between internal belief $q_\theta(s)$ and posterior $p(s \mid o)$.

### 2. Expected Free Energy (Policy Selection)
$$\mathcal{G}(\pi) = \sum_\tau \mathcal{G}(\pi, \tau) = \underbrace{D_{\mathrm{KL}}\Big(q(o_\tau \mid \pi) \parallel p(o_\tau)\Big)}_{\text{Pragmatic Value (Goal Alignment)}} + \underbrace{\mathbb{E}_{q(s_\tau \mid \pi)}\left[\mathcal{H}\big(q(o_\tau \mid s_\tau)\big)\right]}_{\text{Epistemic Value (Information Gain)}}$$
