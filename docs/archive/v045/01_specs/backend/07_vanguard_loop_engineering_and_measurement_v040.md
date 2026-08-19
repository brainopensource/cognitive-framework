---
id: VG-07
file: 07_vanguard_loop_engineering_and_measurement_v040.md
title: "Vanguard v4.0 — Loop Engineering, Measurement & Self-Improvement"
version: 4.0.0
status: NORMATIVE
authority_scope: >
  The improvement partition and the three closure conditions; levels of loop
  engineering as vocabulary; the measurement doctrine; the instrument tuple;
  splits and contamination; the experiment registry; the release pipeline;
  the transfer experiment; preparation for search and process rewards.
supersedes: none (v4 is the first version of this document)
superseded_by: none
budget_words: 5000
owners: [Research Lead, Tech Lead]
last_reviewed: 2026-08-14
---

# Vanguard v4.0 — Loop Engineering, Measurement & Self-Improvement

> **One sentence.** Under a partition where the judge is unreachable from everything it judges, *"the harness builds a better harness"* is not exotic — it is a coding task with an unusually good test suite.

---

## 0. What this document owns

The conditions under which an improvement claim is trustworthy, the apparatus that produces such claims, and the pipeline that turns one into a running change. Competence lifecycle belongs to `06`; the kernel boundary that makes closure enforceable to `05`.

**A number produced outside the rules in §5 is not a number.** That sentence is the entire normative content of this document, and the rest is how to comply with it.

**Implementation binding (`S8-J-07`, 2026-08-17).** The in-tree apparatus that must obey §5 is `tools/telemetry/` (`tuple.py` M-18, `preregistration.py`, `aa_runner.py`, `statistics.py`, `splits.py`, `gap_freeze.py`) and `lab/{build,run,diff,bench}.py`. A lift across differing `K_compat` is refused. Degenerate A/A designs are refused. p-values at n<20 are refused. This does not publish a floor number; spend (`S9-J-03`) still gates live arms.

---

## 1. The three closure conditions

An improvement loop is trustworthy if and only if all three hold. Each has failed in published work.

| # | Condition | Failure mode when violated |
|---|---|---|
| `CL-1` | **Judge exteriority** — the verifier is not reachable by anything it judges | Reward hacking; the system optimises the measurement |
| `CL-2` | **Evaluation exteriority** — the task set used to *promote* is disjoint from the set used to *optimise* | Training-set scoring; improvements that do not replicate |
| `CL-3` | **Noise exteriority** — the observed delta exceeds the variance of the identical configuration against itself | Publishing noise; a random seed presented as a design insight |

`CL-1` is architectural and is enforced by `05 §7` and `06 §4.2`. `CL-2` and `CL-3` are protocol and are enforced here.

> All three are cheap to state and expensive to maintain, and **every one of them will be inconvenient exactly when a result you like depends on ignoring it.** That is the condition they are designed for; a rule that only binds when convenient is decoration.

The improvement partition itself — what is human-changed and what is machine-improvable — is owned by `05 §1.2` as mutability classes. It is not restated here.

---

## 2. Levels of loop engineering

A **vocabulary for locating work**, and explicitly not a roadmap.

| Level | Work |
|---|---|
| L0 | Single completion; no loop |
| L1 | Tool loop; retry on failure |
| L2 | Context engineering, compaction, re-grounding |
| L3 | Composition: operators, isolation, playbooks |
| L4 | Outer loop: distillation, promotion, demotion |
| L5 | Corpus and training feedback |

Conflating these is the primary reason agent projects plateau: work at L1 is mistaken for work at L4, and the absence of instruments is mistaken for the absence of headroom.

> **`M-01`.** The levels are vocabulary, never a backlog. **No ticket may ever read "implement L6."** A level taxonomy invites treating movement up the ladder as progress; movement is only progress when an instrument says so.

---

## 3. Long-horizon instrumentation

Three failure modes of long runs, each with a measurable signal. The mechanisms are owned by `03 §10`; what belongs here is that each is an experiment rather than a craft judgement.

| Signal | Measurement |
|---|---|
| Consolidation loss | Replace the transcript with the structured record, re-run, compare outcomes. A materially positive delta means consolidation is dropping something that matters |
| Re-grounding divergence | How often re-grounding finds a divergence, and whether a rising rate predicts eventual failure. Available **during** the run, which makes it actionable rather than diagnostic |
| Retrieval value | Arm A with recall, arm B without; per-record counterfactual attribution against a matched base rate |

The retrieval question is not *"did we retrieve something relevant"* — unfalsifiable and self-assessed — but **"did retrieval change the outcome, and in which direction."** A record whose recall correlates with worse outcomes is a poisoned record and is demoted automatically (`06 [V-11]`).

This is what turns context engineering from craft into engineering, and it is not currently performed by anyone.

---

## 4. Distillation and promotion

```
run tasks
  → the verifier admits successes                          (CL-1)
    → distil recurring patterns (offline operator)
      → candidate artifact + pre-registered hypothesis
        → paired comparison on HOLDOUT, against unguided
          AND against the incumbent                        (CL-2)
          → effect must exceed the A/A floor               (CL-3)
            → promotion under the three-stage relation     (06 §5)
              → continuous attribution → demotion
```

Two comparisons, not one. Against unguided establishes that the artifact does anything; against the incumbent establishes that it does more than what is already active. A library that only ever beats *nothing* accumulates redundancy and calls it growth.

---

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

## 6. Optimisation, and what it cannot do

Hill-climbing under a fixed evaluator improves the configuration you have. It does not discover the configuration you did not think of.

The exploitation trap is structural: the corpus records what the current system does, promotion favours what the corpus supports, and the next generation optimises harder within the same basin. The mitigation is not clever search but an **explicit variance budget** — a fixed fraction of experimental capacity reserved for changes that are not incremental, evaluated against a held-out *different* set rather than against the incumbent's strengths.

**Paradigm shifts come from humans reading trajectories.** The system's contribution is making anomalies visible: a rising re-grounding divergence rate, a task class where every arm fails identically, a competence artifact that transfers where nothing else does. Those are the observations a human turns into a new approach, and the apparatus exists to surface them, not to have the idea.

---

## 7. The release pipeline

Self-improvement is a **build-and-promote pipeline**, never an in-place edit. The prohibition and its boundary are owned by `05 §7`; the mechanism is here.

```
candidate artifact (ephemeral workspace, no writable mount shared with the evaluator)
  → hermetic build          reproducible, inputs pinned
    → attestation           over inputs, toolchain and outputs, by digest
      → evaluation          hard constraints, then frontier (06 §5)
        → signed canary     bounded traffic, bounded blast radius
          → promotion       activation pointer moved, never file contents
            → rollback      predecessor bootable, rollback tested before promotion
```

| # | Rule |
|---|---|
| `M-21` | Promotion moves an **activation pointer**. It never writes over a running component |
| `M-22` | A rollback that has not been executed successfully is not a rollback. It is tested before the promotion it protects, never after |
| `M-23` | Canary telemetry is compared against the incumbent under the tuple rule (`M-18`), not against expectations |
| `M-24` | Root and TCB classes have **no autonomous promotion path** (`05 [SA-5]`) |

**Why an external pipeline rather than a self-modification mechanism.** A process that rewrites its own running components cannot verify the result using the components it just rewrote. The failure is undetectable from inside, which is the specific property that makes it unacceptable regardless of how good the tests are.

---

## 8. The transfer experiment

The sharpest form of the question this programme exists to answer:

> **What is the smallest system in which a structure the designers did not author, and could not have anticipated, measurably improves performance on tasks it was not derived from, survives replacement of the model that produced it, and can be shown not to be memorisation, retrieval, or proxy optimisation?**

**The impoverished-ontology transfer experiment**, runnable in Phase 2:

1. An environment with hidden structure expressible only through a representation absent from the initial artifact set.
2. An agent with minimal representations, a bare operator set, and the competence machinery of `06`.
3. Run until performance plateaus. **Plateau is the trigger** — it is the observable form of *"my representation is inadequate."*
4. Invoke representation invention. The candidate enters as a candidate, never as active.
5. **Control A** — an agent given the candidate must outperform one given an equal-length random or shuffled structure. *Guards against novelty theatre.*
6. **Control B** — evaluate on a structurally related environment never seen and not used in distillation. *Guards against memorisation.*
7. **Control C** — rehydrate under a different model family and re-run control B. *Guards against substrate dependence.*
8. **Control D** — an agent with the full trajectory history but **without** the candidate entry must underperform. This distinguishes *the representation* from *the experience of having encountered the data*, and it is **the control most likely to fail, which is why it is the one that matters.**
9. Report against the A/A floor on the transfer environment, with the family declared in advance.

**This falsifies the programme** if no candidate ever clears controls A through D. That is the point of running it.

---

## 9. The experiment registry

Experimental capacity is the scarcest resource in the programme, and it is finite in a way that intuition understates. The registry makes that scarcity visible.

| # | Rule |
|---|---|
| `M-25` | Every experiment is registered before it runs: family declaration, manifest, hypotheses, derived sample size, and the split it will consume |
| `M-26` | The registry tracks **committed capacity** — compute, wall-clock and human adjudication time — against available capacity per period |
| `M-27` | Human adjudication time is a budgeted, scheduled resource (`04 §6`), not overhead absorbed by whoever is available |
| `M-28` | An experiment that cannot be powered at the available capacity is not run at reduced power. It is deferred, redesigned, or its effect target is raised |

`M-28` is the rule that converts underpowering from an accident into a decision. Running an underpowered experiment produces a number that looks like a result and is not one, and the number will be cited long after the caveat is forgotten.

---

## 10. Preparation for search, process rewards and reflection

None of these is built in Phase 0. All three are foreclosed by contract decisions made in Phase 0, which is why they are named now.

| Capability | What must exist first |
|---|---|
| Search over trajectories | Branch and fork parentage in the event stream; isolated snapshots per branch; per-branch verdicts (`04 §12`, `03 §8`) |
| Process reward models | Step-level attribution — which operator produced which proposal — recorded from the first episode (`04 §9`) |
| Reflection | Structured records and dead-end capture as data rather than prose (`03 §10.4`) |

Deferring the capability is correct. **Deferring the contracts it will require is not**, because the retrofit is a corpus migration rather than a feature.

---

## 11. Honest limits

1. **Credit assignment is unsolved for long runs.** Counterfactual ablation is correct and expensive; dense verifier signal helps in code and may not generalise.
2. **Statistical power bounds the programme.** The number of adequately powered experiments per year is small, and choosing which to run is a human judgement the apparatus does not make.
3. **Most measured differences will be noise** at achievable sample sizes.
4. **The flywheel is bounded by the evaluator.** In domains without cheap ground truth, everything here degrades to human adjudication with a scheduling problem — which is the central unsolved problem, and no architecture solves it.
5. **Genuine novelty may not be operationalisable** without being gameable. If so, retained-under-ablation utility is the strongest available proxy, and the programme's claim is about *useful* rather than *genuine* competence expansion. Weaker, and still worth making.
