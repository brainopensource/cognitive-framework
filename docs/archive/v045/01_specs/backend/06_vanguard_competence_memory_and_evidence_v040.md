---
id: VG-06
file: 06_vanguard_competence_memory_and_evidence_v040.md
title: "Vanguard v4.0 — Competence, Memory & Evidence"
version: 4.0.0
status: NORMATIVE
authority_scope: >
  The competence graph lifecycle; the four memory stores and the claim pipeline;
  contradiction handling; verification and evaluator classes; verifier
  invariants; promotion, demotion and activation; substrate invariance and
  migration; the outer loop of distillation and selection.
supersedes: none (v4 is the first version of this document)
superseded_by: none
budget_words: 4000
owners: [Tech Lead, Research Lead]
last_reviewed: 2026-08-14
---

# Vanguard v4.0 — Competence, Memory & Evidence

> **One sentence.** Competence is the persistent object of the system: an immutable graph of artifacts, an evidence graph that says where each holds and what would refute it, and an activation policy that decides which of them apply right now.

---

## 0. What this document owns

The lifecycle: how something observed becomes something believed, how something believed becomes something used, and how something used stops being used. Contract shapes belong to `04 §10`; measurement statistics to `07 §5`; the kernel boundary that keeps the verifier exterior to all of it to `05 §7`.

---

## 1. The governing asymmetry

> **Reading memory is cheap and safe. Writing memory is expensive and dangerous.**

A bad retrieval wastes tokens in one turn. A bad write persists, is recalled, appears confirmed by its own recall, and corrupts every future run. The asymmetry justifies an asymmetric gate — but not the gate the first version of this design proposed.

That version required a passing objective verdict before any write. It is the right instinct and the wrong mechanism, because a run that passes its tests proves the *change* was correct; it proves nothing about the *lesson* the agent extracted from it. "This codebase always uses dependency injection" can be written during a run that passed for entirely unrelated reasons. The verdict gates the artifact, never the generalisation.

> **`MEM-1`.** A passing verdict does not imply a semantically valid claim.

The replacement is not a weaker gate. It is a staged one.

---

## 2. The four stores

| Store | Contents | Admission |
|---|---|---|
| Working | The current episode view | Automatic, ephemeral |
| Episodic | Events, observations, receipts | Integrity plus data policy |
| Semantic claims | Scoped assertions | Extraction plus evidence policy |
| Competence | Reusable representations, operators, methods, primitives | Ablation, transfer and activation policy |

Four problems, not one: **retention** (what is kept), **retrieval** (what surfaces when), **integration** (how it enters context), and **degradation** (how it stops being trusted). Systems that treat memory as a single vector-database problem have solved retrieval and ignored the other three — and degradation is the one that decides whether the library compounds or ossifies.

---

## 3. The claim pipeline

```
episode evidence
  → candidate claim              (extraction: origin, validity, counterpoints, expiry)
  → schema, provenance, validity check
  → contradiction search
  → corroboration or reproduction
  → quarantine
  → activation, for a bounded domain
  → continuous outcome attribution
  → demotion or expiry
```

Four stages of standing, and authority is never acquired automatically:

1. **Episodic** — any complete trajectory may be retained, subject to data policy.
2. **Candidate claim** — an extracted observation carrying origin, validity domain, counterpoints and an expiry.
3. **Corroborated claim** — independent evidence, re-execution, or repetition across distinct contexts.
4. **Active competence** — ablation shows utility *outside* the cases it was derived from, no safety regression, and an expiry and demotion plan exists.

Failures, dead ends and abstentions also produce useful claims. What they may never do is acquire authority automatically.

| # | Rule |
|---|---|
| `MEM-2` | Claims preserve environment, code version, evaluator, protocol and validity domain |
| `MEM-3` | A failure may produce a dead-end claim; it receives no authority over effects |
| `MEM-4` | Recall enters context as **data without instruction authority** |
| `MEM-5` | Every recall is recorded with its candidates, scores, selected records and outcome attribution |
| `MEM-6` | Automatic activation requires a staleness policy and a demotion path |
| `MEM-7` | The training corpus is a **separate, opt-in projection**. Episodic retention grants no training licence |

`MEM-4` is the memory-side expression of the authority predicate (`05 §5`): a recalled record is content, and content never authorises. `MEM-5` is what makes the question *"did memory change the outcome?"* answerable at all — without the recall ledger it is unanswerable, and an unanswerable question about a subsystem is how that subsystem escapes evaluation indefinitely.

**Adversarial ablation at activation.** Before a claim becomes active competence, it is evaluated by someone — or something — attempting to show that its apparent utility is memorisation of its derivation cases. A claim that survives that attempt is admitted; one that does not is quarantined, not deleted.

### 3.1 Contradiction

Do not overwrite the older claim. Record a `contradicts` edge, run a resolution operator, and scope both by validity. **Two claims can be simultaneously correct in different versions or environments**, and a store that resolves contradiction by overwriting destroys exactly the evidence needed to notice that.

---

## 4. Verification

### 4.1 An evaluator is not a universal judge

An evaluator produces a **claim**, and the claim's strength depends on its predicate.

| Class | Example | Can support |
|---|---|---|
| `mechanically_reproducible` | Compiler, test suite, schema validator | Conformance to that instrument |
| `externally_grounded` | API read-back, sensor, confirmed transaction | An observed external effect |
| `human_adjudicated` | Blind review | Quality under a stated rubric |
| `learned_proxy` | Critic or process-reward model | Ranking and triage |
| `composite` | Checks plus humans plus environment | Whatever the protocol defines |

> **`V-01`.** No class receives abstract authority as "objective". A claim is scoped to its predicate, and a report that says *"the change is correct"* rather than *"the suite passed under this protocol"* has overstated its instrument.

| # | Rule |
|---|---|
| `V-02` | Rankers order candidates. **Only the verifier admits** |
| `V-03` | Corpus admission requires a mechanically reproducible verdict; structural and proxy verdicts may rank and never admit |
| `V-04` | A proxy's drift against human judgement is monitored; unmonitored drift demotes it |

`V-02` exists because a learned scorer that admits is a second judge, and a second judge inside the mutable surface defeats the whole partition.

### 4.2 Verifier unreachability

For the set of paths owned by the verifier — its implementation, its image, its injected inputs, and the measurement protocol — no request of any effect class held by any agent may target them. Enforced in **three independent layers**, so that no single failure defeats it: static architecture test (`05 [AT-02]`, `05 [AT-12]`), dispatch-time rejection before policy evaluation (`05 [K-03]`), and read-only mounting of injected inputs.

### 4.3 The double probe

Read-only mounting is necessary and **not sufficient**, because a candidate can add a *new* file that shadows the grader.

```
inputsUnmodified :=  tracked evaluator inputs unchanged
                  ∧  no untracked additions under the evaluator input paths
```

> **The second probe is the one that gets forgotten.** In the prototype, a candidate that planted a configuration file under an input glob was invisible to the tracked-file diff — the file was untracked — and scored as passing on the measured path.

Both probes are **required fields** on the verdict's evidence. A verifier that cannot compute them cannot construct a verdict.

### 4.4 Inconclusive as a first-class state

Three outcomes, not two: the change is correct per an instrument that worked; the change is wrong per an instrument that worked; **the instrument did not work**.

| # | Rule |
|---|---|
| `V-05` | Provider errors, socket resets, unbuildable images and perimeter crashes yield *inconclusive* |
| `V-06` | Inconclusive runs are excluded from resolve-rate numerators **and** denominators |
| `V-07` | The per-arm instrument-error rate is reported, and asymmetry is a confound rather than a footnote |
| `V-08` | A wrong-but-real answer is a failure. The guard must not shrink the denominator |
| `V-09` | A verifier that cannot verify emits *inconclusive*, never a pass. **Fail closed** |

**Why this is an integrity control and not accounting hygiene.** In the prototype, a provider error produced an empty completion, which produced no edit, which produced a test run against an unmodified workspace, which produced a *failure*. Both arms ended in a report, so the asymmetry was invisible. An attacker who can induce rate limits on one arm can therefore **manufacture a lift result**.

---

## 5. Promotion, activation and demotion

### 5.1 Hard constraints, then frontier, then activation

Three stages, in order. Collapsing them is how a cheaper-but-slightly-worse candidate becomes unpromotable and a faster-but-unsafe one becomes promotable.

**Stage 1 — hard constraints.** Never negotiable, never traded: capability containment; evaluator integrity; privacy and licensing policy; absence of TCB mutation; the risk budget; declared safety non-regression; data-split and contamination rules. A candidate violating any of these is rejected regardless of its performance.

**Stage 2 — the frontier.** For performance, cost, latency, transfer and calibration: estimate effects with uncertainty, reject hard-constraint violations, admit candidates that are not clearly dominated, and **retain alternatives with distinct trade-offs**. Requiring that no dimension ever worsen eliminates cheaper or faster solutions that are preferable in low-risk contexts — which is most contexts.

**Stage 3 — activation.** Which frontier member applies is a per-context policy decision, not a global ranking.

> A scalar objective is not merely imprecise here; it is self-reinforcing through the corpus. Whatever the scalar rewards becomes what gets recorded, which becomes what gets trained on, which becomes what the next generation optimises harder.

### 5.2 Promotion criteria

An artifact becomes active for domain D only when **all** hold:

- its interface and dependencies are valid;
- an evidence claim exists for D;
- evaluation used tasks **not** used in its derivation;
- ablation without it degrades the outcome beyond practical uncertainty;
- there is no safety regression;
- validity and staleness are defined;
- substrate dependence is known;
- activation is reversible.

**Novelty is observable, never an optimisation target.** Any operational novelty metric — distance from prior artifacts, surprise under a model — is trivially gamed by generating unusual junk. The system may report novelty; it may never optimise it.

### 5.3 Demotion and anti-ossification

The greatest risk in a system that accumulates competence is not forgetting true knowledge. It is **retaining knowledge past the conditions that made it true** — a library of workarounds for model weaknesses that no longer exist, applied with full confidence.

| # | Rule |
|---|---|
| `V-10` | Every active artifact carries non-empty invalidation conditions (`04 §10.3`), automatically checked where the condition is machine-checkable |
| `V-11` | Continuous outcome attribution demotes artifacts correlated with degraded results |
| `V-12` | Model replacement triggers re-evaluation of every active artifact, not a confidence carry-forward |
| `V-13` | Retirement removes from the activation set and **preserves lineage** (`04 [CT-36]`) |

---

## 6. The outer loop

The inner loop solves a task. The outer loop improves the thing that solves tasks.

```
run episodes → verify → distil candidates → evaluate against baseline and
incumbent → promote under §5 → attribute outcomes → demote → repeat
```

**Distillation** extracts a candidate artifact from verified episodes — a playbook, an operator brief, a representation. **Selection** is a contextual bandit over the frontier: which active artifact applies to this task class, learned from outcomes rather than declared.

**Why this compounds and prompt-tuning does not.** A tuned prompt is a point estimate against one model, one task distribution and one moment. An artifact with an evidence block, a validity domain, invalidation conditions and an ablation record is a *claim with a lifecycle*: it can be re-tested, scoped, demoted and superseded. The first decays silently; the second decays visibly, which is the only kind of decay a system can act on.

---

## 7. Substrate invariance

An artifact that works only because of a specific model's quirk is not competence — it is a workaround with good marketing. The distinction is testable.

**The substrate profile** — provider, model identity and fingerprint, adapter version, capability probe results, context window, tool protocol, sampling controls, measurement time and probe-suite digest — travels with every claim and is part of the instrument tuple (`07 §5`).

**Migration protocol**, run whenever the substrate changes:

1. freeze the activation set under the current substrate;
2. measure the new substrate with the probe suite;
3. re-execute a stratified sample **without retuning**;
4. classify each artifact as portable, degraded or incompatible;
5. permit compatibility adapters as **new artifacts**, never as silent mutation of the original;
6. repeat after tuning, separately and labelled as such;
7. report performance, cost and calibration deltas.

> **"Survived the model change" means retention of effect under protocol** — not that the file still loads.

**Substrate debt** is tracked explicitly: the count and proportion of active artifacts whose portability has not been re-measured since the current substrate was adopted. It is a reported metric with a refresh cadence, because an unmeasured activation set silently becomes a set of assumptions.

---

## 8. Honest limits

1. **The flywheel is bounded by the evaluator.** In domains without cheap ground truth, this entire chapter degrades to human adjudication with a scheduling problem.
2. **Ablation is the only trustworthy attribution and it is expensive.** Every promotion decision costs a counterfactual run, which is why the evaluation budget is a first-class dimension (`04 §6`).
3. **A claim from a genuinely passing run can still encode a bad generalisation.** Mitigation is statistical — attribution and demotion — not architectural. This residual is accepted and named rather than engineered away.
4. **Transfer claims require ablation and holdout.** Claimed transfer without both is memorisation with better marketing.
