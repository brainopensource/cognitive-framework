---
status: living
id: theory-index
class: theory
authority: descriptive
canonical_for:
  - cognitive-and-mathematical-theory-index
source_of_truth:
  - docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS.md
  - docs/05_adr/0084-compounding-macro-tools-active-inference.md
derived_from:
  - docs/06_references/
applies_to:
  - v0.6.1
implementation_status: RESEARCH
owner: cognitive-systems-researcher
version: "0.6.1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Cognitive Systems & Mathematical Foundations Index

> **Classification:** Theoretical Foundation & Cognitive Research.  
> **Authority:** Non-normative. Research literature retained in [`docs/06_references/`](../06_references/).

---

## Theory Modules

Every row carries a maturity label. `RESEARCH` explains a future mechanism but is not an
implementation requirement; only an opened milestone and active-board task may authorize that work.

| Module | Mathematical Formulation & Focus | Maturity |
|---|---|---|
| [`active_inference.md`](active_inference.md) | Variational Free Energy ($\mathcal{F}$) & Expected Free Energy ($\mathcal{G}$) in turn loops | `RESEARCH` (Target: M-10) |
| [`economic_resources.md`](economic_resources.md) | Four additive resources plus depth/turn structural ceilings | `AS_BUILT` algebra; RF-23 telemetry population remains active |
| [`trajectory_credit.md`](trajectory_credit.md) | Backward Fault Isolation & Attributable Credit Assignment over Trajectory Graphs | `RESEARCH` (Target: M-10) |
| [`retrieval_and_skills.md`](retrieval_and_skills.md) | 384d Dense Hybrid Retrieval, Elo-Decayed Skill Cards & Eviction Dynamics | `RESEARCH` (Target: M-9) |
| [`preference_and_promotion.md`](preference_and_promotion.md) | Pairwise DPO harvesting plus the existing exact-paired measurement doctrine | `MIXED`: DPO `RESEARCH`; measurement doctrine `AS_BUILT` |
