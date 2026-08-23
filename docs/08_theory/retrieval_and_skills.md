---
status: living
id: theory-retrieval-skills
class: theory
authority: descriptive
canonical_for:
  - retrieval-and-skills-dynamics
source_of_truth:
  - docs/_archive/references/RESEARCH_deepseek-harness_algorithms-ideas.md
  - docs/02_decisions/0084-compounding-macro-tools-active-inference.md
derived_from:
  - docs/_archive/references/
applies_to:
  - v0.6.1
implementation_status: RESEARCH
owner: cognitive-systems-researcher
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# 384d Dense Hybrid Retrieval & Elo Skill Eviction

> **Status:** `RESEARCH` · Target Milestone: **M-9**.

---

## 1. Hybrid Semantic-Lexical Scoring

$$\text{Score}(q, d) = \alpha \cdot \frac{\vec{e}_q \cdot \vec{e}_d}{\|\vec{e}_q\| \|\vec{e}_d\|} + (1 - \alpha) \cdot \text{BM25}(q, d)$$

- Embeddings $\vec{e} \in \mathbb{R}^{384}$ capture semantic intent.
- BM25 captures exact code identifier and syntax matches.

---

## 2. Elo-Decayed Skill Card Eviction

Skill cards are ranked dynamically based on task pass/fail outcomes:

$$R_{\text{new}} = R_{\text{old}} + K \cdot (S - E)$$

Where:
- $S \in \{1, 0\}$ is the signed test verdict.
- $E = \frac{1}{1 + 10^{(R_{\text{task}} - R_{\text{skill}})/400}}$ is the expected success rate.
- Cards falling below the prune threshold $R_{\text{evict}}$ are evicted to prevent context pollution.
