---
status: living
id: theory-preference-promotion
class: theory
authority: descriptive
canonical_for:
  - preference-and-statistical-promotion
source_of_truth:
  - docs/04_annex/MEASUREMENT.md
  - docs/05_adr/0084-compounding-macro-tools-active-inference.md
derived_from:
  - docs/04_annex/MEASUREMENT.md
applies_to:
  - v0.6.1
implementation_status: RESEARCH
owner: cognitive-systems-researcher
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Pairwise Preference Harvesting & Statistical Promotion

> **Maturity:**
> - **DPO Preference Harvesting Pipeline**: `RESEARCH` · Target Milestone: **M-10** (Governed by ADR-0084).
> - **Statistical McNemar Doctrine**: `AS_BUILT` · Governed by Normative Annex [`docs/04_annex/MEASUREMENT.md`](../04_annex/MEASUREMENT.md).

---

## 1. Unforgeable DPO Preference Harvesting (`RESEARCH` - M-10)

Given paired execution runs $(y_w, y_l)$ where $y_w$ passed exterior signed evaluation and $y_l$ failed:

$$\mathcal{L}_{\text{DPO}}(\pi_\theta; \pi_{\text{ref}}) = -\mathbb{E}_{(x, y_w, y_l)} \left[ \ln \sigma \left( \beta \ln \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta \ln \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)} \right) \right]$$

---

## 2. McNemar's Exact Paired Promotion Test (`AS_BUILT`)

Governed by [`docs/04_annex/MEASUREMENT.md §2`](../04_annex/MEASUREMENT.md#2-statistical-doctrine):

| | Model B Pass | Model B Fail |
|---|---|---|
| **Model A Pass** | $a$ (Concordant) | $b$ (Discordant A wins) |
| **Model A Fail** | $c$ (Discordant B wins) | $d$ (Concordant) |

Exact Binomial p-value over discordant pairs $(b, c)$:

$$p = 2 \cdot \sum_{k=0}^{\min(b, c)} \binom{b+c}{k} \left(\frac{1}{2}\right)^{b+c}$$

- Promotion is licensed only when $p < \alpha / k$ (Holm-Bonferroni corrected) and the effect size exceeds the pre-registered A/A noise floor.
