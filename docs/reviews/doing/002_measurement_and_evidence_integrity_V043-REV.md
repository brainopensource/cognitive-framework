# 002 — Measurement & Evidence Integrity

**Status:** NON-NORMATIVE. Where this file and a v4 owner disagree, the owner wins (`PR-3`).
**Date:** 2026-08-16 · **Branch/HEAD:** `sprints7-8/integration` @ `0238b1a`
**Owns:** the triage of every existing benchmark artifact, the evidence-class labelling regime,
the A/A programme, and the rules that make the instrument refuse rather than report.
**Authority cited:** `VG-02 §10 RSK-04/05/06`, `VG-07`, `GTS-13C` T8, Ch. 8, Ch. 10 Q3.
**Predecessor:** `docs/reviews/todo/sota_harness_scientific_benchmarking_programme_2026-08-16.md`
reached the same central conclusion on the same day and was not actioned. This document
supersedes its triage section with concrete per-file rulings.

---

## 1. Why this is the first report after the ruling

`VG-02 §11.5` states that most measured differences will be noise at achievable sample sizes,
and that *"the temptation to believe a favourable result is strongest precisely when you
designed the change."* The 2026 literature is now unambiguous that this programme's core
premise is correct **and** that its measurement burden is heavier than assumed:

- Holding the model fixed and varying only the harness widens a 4.9-point spread across six
  frontier models to **9.5 points**; independent monitoring reports **11–15 points** of
  scaffold-only variation on SWE-bench Verified.
  ([SWE-bench 2026: benchmarks vs scaffolding](https://www.digitalapplied.com/blog/swe-bench-verified-june-2026-benchmark-vs-scaffolding-analysis),
  [Harness-Bench](https://arxiv.org/pdf/2605.27922),
  [Stop Comparing LLM Agents Without Disclosing the Harness](https://arxiv.org/pdf/2605.23950))

Read that twice. **The harness effect is larger than the model effect**, which is exactly the
instrument problem `VG-02 §1` was written to solve — the field validated the thesis. It also
means that any harness comparison we publish carries a 10–20 point *ambient* variance from
scaffold details, and a delta smaller than our noise floor is not a result. We do not currently
know our noise floor.

That is why `T8.1` says *"No delta is interpretable until this number exists."* It does not
exist. Everything below follows from that.

---

## 2. Triage: every measurement artifact in the tree

Classification per `VG-01 §4.1` labelling: a number without an evidence label is unpublished.

### 2.1 Evidence classes (adopt these verbatim)

| Class | Definition | May be published as |
|---|---|---|
| `lab-execute-harness` | Produced by `Runtime.execute_harness` on the composed manifest, every effect through `Kernel.dispatch`, exterior evaluator | A harness measurement, with declared departures |
| `cassette` | Replay of a recorded provider trajectory through the real loop | A determinism/regression measurement. **Never** a capability measurement |
| `lam-replay` | Mock-provider replay | Engineering smoke only. Never published |
| `live-<provider>-<tier>` | Real provider, real cost, through the real loop | A capability measurement of *that* model under *that* harness |
| `bypass` | Anything that executed an effect outside `Kernel.dispatch` | **Not evidence about Vanguard.** May be published only as evidence about a raw model, labelled as such |
| `degenerate` | Pre-condition already satisfied, or zero effects applied, or zero tokens spent | **Refuses to score.** Emits `inconclusive` |

### 2.2 Per-artifact ruling

| Artifact | Class | Ruling |
|---|---|---|
| `benchmarkings/swe_pro_tiers/matrix_results_tier3_token_bucket.json` | `bypass` + `degenerate` | **RETRACT.** Every row `pre_passed:true`, `patch_length:0`; one row `turns:1, tokens:0, cost:0, 0.73s` scored `oracle_passed:true`. The "3 harness manifests" are three hardcoded prompt strings (`HARNESS_SPECS`); `MANIFEST_DIR` is declared at line 36 and never used |
| `benchmarkings/swe_pro_tiers/result_tier{1,2,3,4}_*.json` | `bypass` | **RELABEL, do not retract.** These contain genuine multi-turn trajectories with real `fs.read`/`fs.write` and real content (verified in `result_tier1_lru_ttl_cache.json`). They are honest evidence about *DeepSeek with an ad-hoc scaffold*. They are **not** evidence about Vanguard. Move to `benchmarkings/_external_model_probes/` |
| `benchmarkings/frontier_tier5_datalog_engine/EVALUATION_REPORT.md` | `bypass` | **RELABEL.** Reports pre-fail 5/5 → post-pass 5/5, which is a genuine non-degenerate signal. But it was produced outside the kernel path, so it measures a model, not a harness. Retitle accordingly |
| `benchmarkings/live_llm_zero_hint_challenge/LIVE_LLM_VERDICT.json` | `bypass` | `pre_test_exit:1 → post_test_exit:0`, `turns_used:1` — non-degenerate, single-shot. Relabel as a model probe |
| `benchmarkings/live_proof_result.json` | `bypass` | `passed:false`, `llm_calls:1`, empty `pytest_stdout`. An honest fail of a one-shot probe. Relabel; keep as a negative-control example |
| `benchmarkings/zero_hint_v1/run_live_agent.py` | `lab-execute-harness` | **KEEP AND PROMOTE.** This is the only runner that calls `Runtime.execute_harness`. It is the seed of the real instrument |
| `tools/run_dogfood_r9.py` | `lab-execute-harness` | Keep. Uses `execute_harness` + LAM + Bubblewrap |
| `lab/bench.py`, `lab/diff.py`, `lab/build.py` | — | Correct location (`LT-8`: offline, imports nothing, imported by nothing). Verify that property still holds in CI |

**Retraction protocol.** Do not delete retracted results. Move them to
`benchmarkings/_retracted/` with a sibling `RETRACTION.md` naming the defect, the date, and the
rule that now prevents it. `VG-02 §11.9` values negative results; a retraction with a stated
cause is a stronger artifact than a quiet deletion, and it is the only way the corpus stays
trustworthy after the fact (`RSK-05` touch-ledger discipline applies to our own outputs too).

---

## 3. The two mechanisms that would have prevented all of this

Both already exist in the specification. Neither was applied to `benchmarkings/`.

### 3.1 The dependency gate (`T10.1`) never reached the benchmark tree

`T10.1` enforces the import lattice as a build failure and makes `spike/`/`slice/` unimportable.
`benchmarkings/` was created after that rule and was never covered by it. Result: four runners
that import `OpenRouterModel` directly and reimplement the loop.

**Rule to add to `tools/check_boundaries.py` today:**

```
A module under benchmarkings/ may import from vanguard.packages.runtime.root
(Runtime, TaskContext, RunResult) and from vanguard.packages.ports only.
Importing vanguard.packages.adapters.* from benchmarkings/ is a build failure.
```

That single rule makes a bypassing benchmark impossible to write, which is stronger than any
amount of review discipline. It is the same mechanism that made `spike/` disposable by
construction (`ADR-0047`).

### 3.2 The refusing instrument (`RSK-04`) was never given a refusal condition

The codebase already knows how to refuse: `test/contracts/readers/__init__.py:40` raises
`ReaderUnavailable("node is required: SC-7 evidence needs both readers, and a run without the
TypeScript reader proves nothing about cross-language agreement")` rather than skipping.
`root.py:529` deliberately has **no** `FakeEvaluator` row because *"absence is inconclusive, not
a pass"*. That instinct is right and it is the project's best cultural asset.

It simply was not applied to the benchmark scorer. **Add these refusal conditions as a shared
`benchmarkings/guard.py` that every runner must call:**

| Condition | Verdict |
|---|---|
| Pre-repair oracle **passes** on a repair task | `inconclusive:precondition_satisfied` — the task was already solved; no information |
| Zero effects applied (`patch_length == 0`) and post-oracle passes | `inconclusive:no_intervention` |
| Zero prompt tokens and zero completion tokens | `inconclusive:model_not_invoked` |
| Provider error, rate limit, socket reset, unbuildable image | `inconclusive:instrument_error` (`L-07`, `FT-01`) — excluded from **both** numerator and denominator |
| Evaluator unavailable or unattested | `inconclusive:no_verdict` — never a pass |
| Containment report absent or failing | **Publication blocked** (`T5.2`) |

`A-10`: a gate that cannot fail is not a gate. Each of these ships with a `test/broken/`
counterpart that must fail — plant a degenerate run and assert the scorer refuses it. That test
is the actual deliverable; the guard is just the code that makes it pass.

---

## 4. The A/A programme — the only work that unblocks Q3

`GTS-13C` Ch. 10 Q3 asks for a per-task-class A/A floor computed against `vg-shell-only`, a
paired comparison, and a verifier–deployment gap number. Nothing else in the measurement layer
is worth building first, because every other number is uninterpretable without the floor.

### 4.1 Minimum honest A/A design

| Element | Specification | Why |
|---|---|---|
| Arms | `vg-shell-only` vs **itself**, identical manifest digest | `T8.1`. The floor is the variance of the instrument, not of a change |
| Task classes | ≥3, from `benchmarkings/tasks_phase*` and the three real bugs of `T0.1` | `T8.1` requires per-class; classes differ in variance by more than arms do |
| Repeats | N chosen so the floor's CI half-width is below the smallest delta we intend to claim. Record N and the MDE **before running** | `RSK-06` underpowered claims |
| Temperature | Fixed and recorded; a non-zero temperature is a *deliberate* variance source and must be declared | `NC-06` — determinism is by recording and replay, not assumption |
| Degenerate detection | The floor **refuses to report** if any arm produces a degenerate row, or if between-run variance is zero (a zero floor means the instrument is not exercising anything) | `RSK-04`, `T8.1` |
| Instrument-error rate | Reported **per arm**. Asymmetry is a confound, not a footnote | `T5.6`, `ADR-0031` |
| Pre-registration | Hypotheses, primary metric, alpha, stopping rule, manifest digest — hashed **before any arm runs** | `T8.4`, `L-08` |

### 4.2 Then, and only then, the paired runner

`T8.2`: both arms attempt the same instances; analysis over discordant pairs only. McNemar
exact for paired binary; paired bootstrap for cost and latency; survival methods for timeouts.
`T8.3` is explicit that *"McNemar alone is not a statistics strategy"* — because timeouts are
censored observations and treating a timeout as a failure biases exactly the arm that is slower,
which is usually the more capable one.

### 4.3 The verifier–deployment gap (`T8.7`) — build the dashboard early, feed it late

The 2026 literature makes this urgent rather than aspirational:

- A benchmark of 13 frontier models found exploit rates from 0% to 13.9%, with RL post-training
  strongly associated with higher reward hacking, and **72% of hacking episodes carrying explicit
  chain-of-thought rationale** framing the exploit as legitimate problem-solving.
  ([Reward Hacking Benchmark](https://arxiv.org/html/2605.02964v1))
- RLVR-trained models develop a growing *"hacking gap"* between extensional and isomorphic
  reward that emerges mid-training; training against an isomorphic verifier keeps the gap near
  zero. ([LLMs Gaming Verifiers](https://arxiv.org/html/2604.15149))
- ML-engineering agent benchmarks now log agent edits and file accesses and compare
  agent-visible metrics against reference metrics computed from pristine code under lock.
  ([RewardHackingAgents](https://arxiv.org/html/2603.11337))

**What this means concretely for us.** Our `T5.4` double probe (tracked inputs unchanged **and**
no untracked additions under evaluator input paths) is the correct primitive and is ahead of
most of the field — `ADR-0029` already caught the shadow-file case that a tracked-file diff
misses. Two additions the literature justifies:

1. **Isomorphic perturbation of the oracle.** For each task class, hold a semantically
   equivalent but syntactically different oracle. A candidate that passes the tracked oracle and
   fails its isomorph has fit the oracle, not the problem. Score the divergence as the gap.
2. **Agent-visible vs reference metric separation.** The number the agent can observe must never
   be the number that promotes it. Our architecture already gives this for free — the evaluator
   is a separate identity — but only if the loop cannot read the verdict, which
   `meta_loop.py` currently violates (`001 §3.1`).

The gap dashboard freezes promotions automatically when it widens (`T8.7`). Build the freeze
mechanism now, while there is nothing to freeze; retrofitting an automatic freeze onto a live
promotion pipeline is how the freeze becomes advisory.

### 4.4 Seeded sabotage (`T8.8`) is not optional and is cheap

Plant candidates that exploit the proxy — a patch that special-cases the test inputs, a patch
that writes a shadow conftest, a patch that monkeypatches the assertion. Confirm the pipeline
rejects each. `A-10` again: a gate never proven able to fail is not a gate. This is a day of
work and it is the difference between claiming reward-hacking resistance and having it.

---

## 5. What we may and may not say about v0.4.3

A short list the team can hold to, because the failure mode is not lying — it is a true sentence
read as a stronger one.

**May say:**
- "Every privileged effect on the product path traverses one capability-mediated dispatch
  sequence, and we have fault-injection tests for every exit." *(once `001 §5` step 1–2 land)*
- "The evaluator runs under a separate OS identity and image digest, and no capability the
  episode holds resolves to it."
- "Our wire contracts are RFC 8785-canonical with N golden triples and a per-kind decidable
  selector inclusion relation."
- "Here is a trajectory. Here is which component was active. Here is what it cost."

**May not say, and must actively correct if said:**
- ~~"We evaluated three harness manifests."~~ — three prompt strings were evaluated (§2.2).
- ~~"Model X passes tier-3 under harness Y."~~ — the task passed before the agent acted.
- ~~"The harness improves outcomes."~~ — no floor, no pairing, no pre-registration.
- ~~"Sprint 10 complete: 100% test pass."~~ — a green suite is not the MVP gate (`GTS-13C` Ch. 10).
- ~~"Self-correcting agent loop shipped."~~ — the loop that self-corrects grades itself
  (`001 §3.1`), which is the one thing the architecture forbids.

---

## 6. Sequenced measurement backlog

| # | Item | Blocks | Effort |
|---|---|---|---|
| M1 | `benchmarkings/` dependency gate as a CI build failure | everything | 0.5 d |
| M2 | `benchmarkings/guard.py` refusal conditions + `test/broken/` counterparts | Q3 | 2 d |
| M3 | Retraction sweep: relabel/move every artifact per §2.2, write `RETRACTION.md` | credibility | 1 d |
| M4 | Promote `zero_hint_v1/run_live_agent.py` to the single benchmark entrypoint; delete the four bypassing runners | Q3 | 2 d |
| M5 | Pre-registration artifact + hash-before-run enforcement (`T8.4`) | Q3 | 2 d |
| M6 | A/A runner, ≥3 task classes, against `vg-shell-only`, refusing when degenerate (`T8.1`) | **Q3** | 1 wk |
| M7 | Paired runner + McNemar/bootstrap/survival module (`T8.2`, `T8.3`) | Q3 | 1 wk |
| M8 | Split discipline + touch ledger + per-instance membership check (`T8.5`) | `RSK-05` | 3 d |
| M9 | Isomorphic-oracle perturbation per task class (§4.3) | `RSK-02` | 3 d |
| M10 | Seeded-sabotage suite (`T8.8`) | `RSK-02` | 1 d |
| M11 | Verifier–deployment gap dashboard + automatic promotion freeze (`T8.7`) | GA | 1 wk |

M1–M4 are one engineer-week and convert the measurement layer from actively misleading to
merely incomplete. That is the highest-return week available in the entire programme.

---

## Sources

- [SWE-bench in 2026: Benchmarks vs Scaffolding Reality](https://www.digitalapplied.com/blog/swe-bench-verified-june-2026-benchmark-vs-scaffolding-analysis)
- [Harness-Bench: Measuring Harness Effects](https://arxiv.org/pdf/2605.27922)
- [Stop Comparing LLM Agents Without Disclosing the Harness](https://arxiv.org/pdf/2605.23950)
- [Reward Hacking Benchmark: Measuring Exploits in LLM Agents with Tool Use](https://arxiv.org/html/2605.02964v1)
- [LLMs Gaming Verifiers: RLVR can Lead to Reward Hacking](https://arxiv.org/html/2604.15149)
- [RewardHackingAgents: Benchmarking Evaluation Integrity for LLM ML-Engineering Agents](https://arxiv.org/html/2603.11337)
- [Verification Horizon: Coding Agent Reward Limits](https://www.emergentmind.com/papers/2606.26300)
- [From Question Answering to Task Completion: A Survey on Agent System and Harness Design](https://arxiv.org/pdf/2606.20683)
