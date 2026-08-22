---
id: normative-annex-measurement
class: law
authority: normative
canonical_for:
  - measurement-doctrine-annex
  - statistical-verification-contract
status: living
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
title: "Measurement"
source: 01_specs/backend/07_vanguard_loop_engineering_and_measurement_v040.md (VG-07) §5 (git history, 4f9f8b1)
supersedes: []
superseded_by: null
---

# Annex: Measurement

> The lab's constitution, kept nearly whole from VG-07 §5 per the archived
> `01_SPECS_MIGRATION_MATRIX.md` §1.10 (git history, `4f9f8b1`) — paired designs, McNemar's exact test,
> multiple-comparison policy, the A/A noise floor, arm design, the instrument tuple, splits and
> contamination discipline. This is what makes Phase-2 promotion (`docs/SPEC.md` §5.2, gate M5)
> statistically honest. RFC-2119 language is normative here, same as `docs/SPEC.md`.
>
> **v0.6 note (`ADR-0073`, `ADR-0074`).** This annex remains the measurement constitution.
> Phase-2 promotion is a **deferred blueprint**, not foundation scope. Foundation identity
> (`D_H`/`D_R`/`D_X`) MUST be complete before any promotion statistics are treated as attributable.
>
> **Status note.** §5.6's instrument tuple is still unwired in the shipped `tools/telemetry/` —
> wiring it is deferred with SPEC §7. The doctrine below is not retroactively true of the current
> code; it is the contract a later measurement wave wires against.

## 5. The measurement doctrine

### 5.1 Paired designs

Task difficulty variance dominates every other variance component in agent benchmarks: between-task variance in solvability exceeds between-configuration variance by a large margin. **An unpaired comparison of two configurations on two random task samples is measuring which sample was easier.**

> **`M-02`.** Every comparison is paired: both arms attempt the same instances, and the analysis is over discordant pairs only — the instances where the arms disagreed. Concordant pairs carry no information about the difference.

### 5.2 The test

> **`M-03`.** McNemar's **exact** test on the discordant counts. The exact binomial form, not the chi-squared approximation, which is unreliable at the discordant counts achievable at realistic sample sizes.

> **`M-04`.** Report all of: both discordant counts, their total, the exact p-value, the effect size, and a confidence interval on the paired difference. **A p-value without an effect size and an interval is not a result.** Significance answers *"is there a difference"*, which is rarely the question; the question is *"how large, and could it plausibly be zero."*

### 5.3 Multiple comparisons

> **`M-05`.** Any experiment testing more than one hypothesis controls family-wise error by Holm–Bonferroni. Holm rather than plain Bonferroni: uniformly more powerful, no additional assumptions.

> **`M-06`.** **The family is declared before any arm runs**, as a pre-registered artifact with a hash — hypotheses, primary metrics, alpha, correction, manifest hash, and a fixed stopping rule. Post-hoc family selection is the most common form of unintentional p-hacking and is **undetectable after the fact**, which is precisely why the declaration must be an artifact rather than an intention.

Optional stopping is not permitted. A stopping rule that reacts to the data is a different test than the one whose p-value is being reported.

### 5.4 The A/A noise floor

The floor is the same configuration against itself under pure stochasticity: how large a difference can appear when **nothing** differs.

| # | Rule | Rationale |
|---|---|---|
| `M-07` | **A floor whose arms sit at 0% or 100% is refused, not reported** | Zero discordance there is *unobserved*, not *low*, and every derived sample size inherits the degeneracy. The statistics module must refuse it — a gate that can actually fail |
| `M-08` | Floor sample size must be adequate | A floor at three instances characterises nothing |
| `M-09` | The floor is computed on the **same manifest** as the comparison it licenses | Noise is task-set dependent |
| `M-10` | A preliminary floor is marked as such and may not size an admission run | |
| `M-11` | A new floor is a **new artifact with a new hash**, never an in-place edit | Any published number citing the old hash must remain checkable |

**Sample size** is derived numerically from the floor's discordance rate, the minimum detectable effect, alpha and power, and is recorded in the family declaration. The practical consequence is sobering and should be internalised before anything is promised: **detecting a five-point effect against a realistic floor typically requires low hundreds of paired instances.** Most published agent comparisons are underpowered by an order of magnitude, which is a sufficient explanation for why the field's effect sizes fail to replicate.

### 5.5 Arm design

Each rule below corresponds to a defect that actually occurred, not a hypothetical.

| # | Rule | Defect prevented |
|---|---|---|
| `M-12` | **Both arms' change mechanisms must have equal expressive power** | One arm's mechanism silently dropped newly created files while the other's could express them. Lift would be biased against the harness on every file-creating task. *A comparison whose mechanisms differ measures the mechanism* |
| `M-13` | Identical model fingerprint and sampling parameters | Otherwise you measured the model |
| `M-14` | The baseline is specified exactly and its template hashed | "We used the standard prompt" must be checkable |
| `M-15` | **Both arms must be posed the actual problem** | A task type carried no field for the problem statement, so the baseline received an identifier as its brief. Both arms equally uninformed; the lift would have characterised a harness that was never told what to do |
| `M-16` | Instrument errors excluded, and the **per-arm error rate reported** | An asymmetric error rate is a confound masquerading as a result |
| `M-17` | Cost non-inferiority must be non-vacuous | If every row reports zero cost, the cost condition passes vacuously. Priced accounting precedes any cost claim |

`M-15` deserves the emphasis: the failure was invisible because both arms ran, both produced reports, and the comparison was arithmetically valid. Nothing about the output indicated that the experiment had no content.

### 5.6 The instrument tuple

Every result carries an instrument tuple partitioned into four explicit algebraic subsets:

$$\text{Tuple} = \langle \mathcal{K}_{\text{compat}}, \mathcal{D}_{\text{treatment}}, \mathcal{S}_{\text{strat}}, \mathcal{M}_{\text{meta}} \rangle$$

- $\mathcal{K}_{\text{compat}}$ (**Compatibility Key**): benchmark ID, split hash, model fingerprint and sampling parameters, harness commit, agent definition hash, evaluator image digest, containment report digest (`05 §6.2`), substrate profile (`06 §7`), runner version, and schema version. Must be strictly equal ($\mathcal{K}_A = \mathcal{K}_B$) across compared arms.
- $\mathcal{D}_{\text{treatment}}$ (**Treatment Dimensions**): the declared experimental axis under test (e.g. `vg-code-default` vs `vg-shell-only`, or L1–L5 prefix-cache enabled vs disabled).
- $\mathcal{S}_{\text{strat}}$ (**Stratification Fields**): controlled categorical dimensions (e.g. task difficulty tier, repository programming language).
- $\mathcal{M}_{\text{meta}}$ (**Observation Metadata**): physical timestamp, run ID, node ID, operator identity. **Explicitly excluded from the strict equality comparison operator.**

> **`M-18` — the comparability rule.** Two results are comparable **if and only if** their compatibility keys match ($\mathcal{K}_A = \mathcal{K}_B$) and their tuples differ in exactly the declared treatment dimensions ($\mathcal{D}_{\text{treatment}}$). The comparison harness **refuses** to compute a lift between runs differing in an undeclared dimension. Observation metadata ($\mathcal{M}_{\text{meta}}$) is excluded from the equality check.

This is the single highest-leverage piece of the apparatus, because it converts the most common analytical error in the field from a discipline problem into a runtime failure. A cross-schema-version comparison is a tuple delta and is refused unless declared.

### 5.7 Splits and contamination

| Split | Purpose | Access |
|---|---|---|
| DEV | Iteration, debugging, optimisation | Unrestricted |
| HOLDOUT | Promotion decisions (`CL-2`) | Read at promotion time only; never optimised against |
| SEALED | Publication | Touched only under the full publication protocol; every touch logged; a fixed number of touches per period |

> **`M-19`.** Contamination is one-directional and irreversible. A sealed set used for iteration is a development set **forever**, and no amount of care restores it. Touches are a depleting budget and are recorded in a ledger.

> **`M-20`.** Any instance whose trajectory entered the training corpus is contaminated for evaluation permanently. **Corpus membership must be checkable per instance**, or the entire evaluation becomes unfalsifiable the moment training begins.

### 5.8 What becomes measurable

Because the harness is composable and the tuple is complete, each of these is a clean one-variable experiment, and none is currently available to anyone: caching on or off against cost per resolved task; single-turn against tool-loop at the same model; a faster index against resolve rate — *does faster search change outcomes, or only latency?*, which determines whether a systems-language investment is justified at all; playbook rigidity across its three settings; a flat agent against composition **at equal total budget**, which asks whether composition pays or is merely more spend; operator isolation against horizon length; consolidated record against full transcript; recall on or off; and model-tier routing across the cost-quality frontier.

> **Restated because it is the rule most often broken:** a change showing a six-point improvement has measured nothing until the A/A floor on that task set is known.

---
