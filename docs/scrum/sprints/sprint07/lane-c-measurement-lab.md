# Sprint 7 · Lane C — Measurement & Lab

**Owner:** Senior Developer C · **Backlog:** `011 §4.3`
**Write scope:** `benchmarkings/**` · `tools/002_LLM_API_MOCK/**` · `lab/**` · `test/broken/**`
**Do not touch:** `vanguard/packages/**` (raise a PR comment) · `docs/main_v4/**`

---

## The lane in one sentence

> **Make it impossible to write a benchmark that bypasses the kernel, and impossible to score a run
> that measured nothing.**

## Why this lane exists

`benchmarkings/swe_pro_tiers/matrix_results_tier3_token_bucket.json` reports, on **every row**:
`"pre_passed": true` and `"patch_length": 0`. The oracle passed *before the agent acted*, and the
agent changed nothing. One row records `turns: 1, prompt_tokens: 0, cost_usd: 0.0,
duration_s: 0.73` — **the model was never called** — and still scores `"oracle_passed": true`.

Meanwhile `run_matrix_evaluation.py` is titled *"Evaluates 3 harness manifests"*, declares
`MANIFEST_DIR` at line 36, and **never uses it again**. The three "harnesses" are three hardcoded
strings in a Python dict.

`VG-02 RSK-04` names this exactly — *"measurement theatre: vacuous passes, degenerate floors"* —
and prescribes the mitigation: **instruments that refuse rather than report.** The instrument did
not refuse. This lane makes it refuse.

**Be precise about scope.** Not all of it is theatre. `result_tier1_lru_ttl_cache.json` contains a
genuine multi-turn trajectory with real `fs.read`/`fs.write` calls. That is honest evidence about
*a model with an ad-hoc scaffold* — it is simply not evidence about Vanguard. It gets **relabelled,
not retracted.**

---

## S7-C-01 — `benchmarkings/` dependency gate · **START DAY 1**

One rule makes every bypassing runner unwritable. Do this before deleting anything, or the deletion
will be re-litigated next sprint.

- [ ] **Step 1** — failing test: `benchmarkings/` currently imports
      `vanguard.packages.adapters.models.openrouter` directly in four files, and
      `tools/check_boundaries.py` **PASSes**
- [ ] **Step 2** — add the rule: a module under `benchmarkings/**` may import
      `vanguard.packages.runtime.root` and `vanguard.packages.ports` **only**. Importing
      `vanguard.packages.adapters.*` is a build failure
- [ ] **Step 3** — run → four hits. **Expected.** They are `S7-C-03`
- [ ] **Step 4** — broken counterpart under `test/broken/`
- [ ] **Step 5** — commit

> `T10.1` made `spike/` and `slice/` disposable **by construction**, and the S4 gate proved their
> absence. `benchmarkings/` was created after that rule and was never covered by it. This closes
> the same class of hole.

---

## S7-C-02 — `benchmarkings/guard.py` refusal conditions

**Reuse, do not rebuild.** `tools/002_LLM_API_MOCK/verdict.py` already provides `pytest_passed`,
`evidence_label` and `leak_paths`. This is a shared guard every runner must call.

| Condition | Verdict |
|---|---|
| Pre-repair oracle **passes** on a repair task | `inconclusive:precondition_satisfied` |
| Zero effects applied **and** post-oracle passes | `inconclusive:no_intervention` |
| Zero prompt **and** completion tokens | `inconclusive:model_not_invoked` |
| Provider error / rate limit / socket reset | `inconclusive:instrument_error` — excluded from **numerator and denominator** (`L-07`) |
| Evaluator absent or unattested | `inconclusive:no_verdict` — never a pass |
| Containment report absent or failing | **publication blocked** (`T5.2`) |

- [ ] **Step 1** — **write the broken counterparts first.** Six planted degenerate runs, one per
      condition. Each must currently score as a pass. *That is the bug, demonstrated.*
- [ ] **Step 2** — implement `benchmarkings/guard.py`
- [ ] **Step 3** — all six counterparts now **refuse**
- [ ] **Step 4** — commit

> **The tests are the deliverable; the guard is just the code that makes them pass.** `A-10`.

---

## S7-C-03 — Delete the four bypassing runners

**Requires:** `S7-C-01`, `S7-C-02`.

- [ ] `benchmarkings/swe_pro_tiers/runner.py` — reimplements the episode loop including a **regex
      tool-call parser over prose**
- [ ] `benchmarkings/swe_pro_tiers/run_matrix_evaluation.py` — `MANIFEST_DIR` declared, unused
- [ ] `benchmarkings/run_agentic_live_challenge.py`
- [ ] `benchmarkings/run_live_proof.py`
- [ ] **Verify:** `grep -rn "OpenRouterModel" benchmarkings/` returns only the promoted runner
- [ ] Commit

---

## S7-C-04 — Retraction sweep

**Retract, do not delete.** `VG-02 §11.9` values corrected and negative results. A retraction with a
stated cause is a stronger artifact than a quiet deletion — and it is the only way the corpus stays
trustworthy after the fact.

- [ ] **Step 1** — `benchmarkings/_retracted/` + `RETRACTION.md` per artifact: the defect, the
      date, and **the rule that now prevents it**
- [ ] **Step 2** — move degenerate results (`matrix_results_*.json`) there
- [ ] **Step 3** — move non-degenerate bypass results (`result_tier*.json`,
      `EVALUATION_REPORT.md`, `LIVE_LLM_VERDICT.json`, `live_proof_result.json`) to
      `benchmarkings/_external_model_probes/`, **relabelled as model probes, not harness results**
- [ ] **Step 4** — apply the 9-label regime (`002 §2.1`) to every surviving artifact
- [ ] **Step 5** — commit

---

## S7-C-05 — Promote the honest runner

- [ ] `benchmarkings/zero_hint_v1/run_live_agent.py` becomes the **sole** benchmark entrypoint —
      it is the only one that calls `Runtime.execute_harness`
- [ ] Label every result `lab-execute-harness`; record `labDepartures` explicitly (auto-approve,
      skipped isolated evaluator, injected tool schemas, raised `maxTokens`)
- [ ] Coordinate with Lane B (`S7-B-04`) to emit `gene_digests` into `K_compat`
- [ ] Commit

> A declared lab departure is **not** cheating (`C9`). An undeclared one is. Never drop the field
> from a published row.

---

## S7-C-06 — `models.json` `top` fail-closed

`D-13` requires `top: []` until the Project Lead names three ids in the Decision Register. It
currently holds **4 ids**, and the bands have drifted to `tier1_local…tier6_cloud` alongside
`free/medium/high/top`.

- [ ] **Step 1** — failing test: `models_for_band("top")` must raise
      `"Project Lead must name three top OpenRouter model ids in models.json before band=top"`
- [ ] **Step 2** — set `top: []`; implement the raise
- [ ] **Step 3** — reconcile the two band vocabularies into one; record which is authoritative
- [ ] **Step 4** — commit

---

## S7-C-07 — Remove the LAM competitor persona

`tools/002_LLM_API_MOCK/simulate.py` hardcodes a system prompt saying *"You are OpenCode."* Any
Plane-B DNA claim made while the gym runs a competitor persona is **confounded** — you cannot claim
to measure `vg-code-default` DNA under someone else's prompt.

- [ ] **Step 1** — failing test: the simulated system prompt must equal the pack's
      `system-prompt.txt` bytes
- [ ] **Step 2** — parameterise by scenario / harness id; default to the pack bytes, hashed into
      `K_compat`
- [ ] **Step 3** — commit

---

## What this lane may **not** do this sprint

| Forbidden | Why |
|---|---|
| Spend the live budget | Calibration-first. No cloud spend before Sprint 9's pre-registration |
| Compute or publish any lift | No A/A floor exists. `T8.1`: *"no delta is interpretable until this number exists"* |
| Print p-values | n∈{1,2,3} is a case study. `M-28` |
| Run an A/A on LAM replay | Deterministic → variance ≈ 0 → **invents significance** for any live arm (`D-06`, `CL-3`) |
| Mark any Active MVP Contract row `covered` from gym evidence | The gym proves mechanics, never competence |

## Stop conditions

| Signal | Action |
|---|---|
| A guard condition would reject a run everyone considers valid | **Stop.** Either the condition is wrong or the run is. Decide explicitly, record it |
| Retraction would remove the only evidence for a `covered` contract row | **Stop.** That row was covered by bypass evidence — a governance finding |
| The honest runner produces zero passes | **Not a stop.** That is a *result*, and it is the calibration signal Sprint 9 needs |

## Definition of done for the lane

```bash
python3 tools/check_boundaries.py                 # benchmarkings rule active
python3 tools/run_broken_tests.py                 # six guard counterparts refuse
ls benchmarkings/_retracted/RETRACTION.md         # exists
grep -rn "OpenRouterModel" benchmarkings/         # only the promoted runner
python3 -m unittest test.tools -v                 # LAM tests green
```
