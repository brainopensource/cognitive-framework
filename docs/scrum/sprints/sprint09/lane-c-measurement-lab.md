# Sprint 9 · Lane C — Measurement & Lab (primary lane)

**Owner:** Senior C · **Backlog:** `011 §6` · **Refinement:** **REFINED AND OPEN (2026-08-16)**
**Commit prefix:** `[lane-c]`

## ▶ YOUR S9 FIRST TASK: `S9-C-01` — **NOT BLOCKED. START NOW, IN PARALLEL WITH SPRINT 8.**

**You lead Sprint 9.** Lanes A and B support you, and both of their S9 first tasks are blocked on
Sprint 8 — yours is not. `S9-C-01` → `S9-C-02` → `S9-C-03` is the spine of the sprint and every
step runs against `tools/002_LLM_API_MOCK` and `vg-shell-only`. None of it needs Sprint 8.

**DoD command:** `python3 -m unittest discover -s test/lab -t .` — green, **and** a lift computed
across differing `K_compat` **refuses**.

**Binding limits while you work ahead:**

- **Nobody publishes a delta.** Build the instrument; do not report a result through it.
- **No cloud spend of any amount** until the Project Lead signs `S9-J-03`.
- **Never `band=top`.** `models.json` keeps `top: []`; `models_for_band("top")` refuses and that
  refusal is asserted by `test/tools/test_lam_models.py`. Do not name frontier ids.
- **An A/A floor from LAM replay is not a floor** — replay is deterministic, variance ≈ 0, and the
  run invents significance (`D-06`, `CL-3`). Build against replay; never report a floor from it.
- **Fail closed on placeholder digests.** `harness_commit: "v0.5.0"` and
  `evaluator_image_digest: "sha256:evaluator_default"` are lies on a published row.

> A degenerate floor is a **valid outcome**; the runner refuses rather than printing zero variance.
> If the floor swallows the deltas we meant to claim, `RSK-06` requires reducing claim ambition —
> **not** raising N until something is significant.

---

---

## S9-C-01 — Wire the `M-18` instrument tuple

`tools/telemetry/tuple.py` **implements `M-18` and is wired into nothing.** The mechanism that
would refuse incomparable lifts exists and is dark.

- [ ] Failing test: a lift computation across differing `K_compat` must **refuse**
- [ ] Emit the tuple into every `result.json`: `K_compat` (benchmark id, split hash, model
      fingerprint, sampling, harness commit, agent hash, evaluator image digest, containment
      digest, substrate, runner, schema version) · `D_treatment` · `S_strat` · `M_meta`
      (excluded from equality)
- [ ] **Fail closed on placeholder digests.** `harness_commit: "v0.5.0"` and
      `evaluator_image_digest: "sha256:evaluator_default"` are **lies** on a published row
- [ ] Commit

## S9-C-02 — Pre-registration, hashed before any arm runs

- [ ] Artifact: hypotheses, primary metric, alpha, correction, manifest digests, model id,
      stopping rule, corpus split ids, instrument-error policy
- [ ] CI rejects an arm run with no prior hash
- [ ] Fix the status drift: files say `preregistered_not_executed` while `runs/` exist. Status must
      update to `executed-lab` with run ids, or the preregistration is decorative
- [ ] Commit

## S9-C-03 — The A/A runner

- [ ] Identical manifest against **itself**, N repeats, ≥3 task classes, against `vg-shell-only`
- [ ] **Refuses** when any arm is degenerate, or when the floor is exactly zero
- [ ] Temperature fixed and recorded; a non-zero temperature is a declared variance source
- [ ] Per-arm instrument-error rate reported (`M-16`)
- [ ] Commit

## S9-C-04 — Statistics module

- [ ] McNemar exact for paired binary; both discordant counts, effect size, CI
- [ ] Paired bootstrap for cost and latency
- [ ] **Survival methods for timeouts and censoring** — treating a timeout as a failure biases the
      slower arm, which is usually the more capable one
- [ ] **No p-values at n<20.** At n∈{1,2,3} report a case study with full traces (`M-28`)
- [ ] Commit

## S9-C-05 — Splits and touch ledger

- [ ] `DEV / HOLDOUT / SEALED / LIVE / DEPLOYMENT`
- [ ] Contamination is **one-way**: using HOLDOUT to tune a prompt **burns it to DEV forever**, and
      the burn is recorded
- [ ] Per-instance corpus membership checkable before any `DEF-09` training
- [ ] Commit

## S9-C-06 — Oracle hardening

`adapters/evaluators/suites/bug-001-single-file/test_oracle.py` asserts `"(A + B) * B"` **in source
text** — a comment satisfies the judge. That is a string search impersonating a
`mechanically_reproducible` evaluator class.

- [ ] Failing test: a comment-only patch currently **passes**. That is the bug
- [ ] Replace with property / metamorphic oracles, extra numeric cases not in the public tests, and
      a mutation check (a known-wrong patch **must** fail)
- [ ] Isomorphic perturbation per task class: a candidate that passes the tracked oracle and fails
      its semantic isomorph has fit the oracle, not the problem. Score the divergence as the gap
- [ ] Commit

## S9-C-07 — Seeded-sabotage suite

- [ ] Plant: a patch that special-cases test inputs · a patch that writes a shadow `conftest.py` ·
      a patch that monkeypatches the assertion
- [ ] Confirm the pipeline **rejects each**
- [ ] Commit

> One day of work, and it is the difference between claiming reward-hacking resistance and having
> it. `A-10`.

## Budget protocol (binding)

Calibration first. Local Ollama is the default spend; cloud is a scarce instrument.

| Step | Spend | Stop if |
|---|---|---|
| Ollama light, T1, max-turns 8 | $0 | record the tool histogram either way |
| Ollama heavy, T1 | $0 | **no `patch.apply` after two models → harness/tool-schema defect. Do not buy cloud** |
| One free cloud id, T1 only | ≤ cents | T1 fail or HTTP errors |
| Same id, T2 | remaining | — |
| DNA A/B | only if a model can patch | n=3 is a case study |

**Hard stop:** remaining budget ≤ 0 → no paid calls without a recorded Project Lead waiver.
