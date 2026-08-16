# 03 — Measurement & Evidence Rules

**Purpose:** what counts as evidence, what must refuse to score, and what may be said out loud.
**Owner:** `VG-07`. This is a projection. Where they differ, `VG-07` wins.

> **Read this before producing any number.** A number produced outside these rules **is not a
> number** and may not be published, cited in a PR, or used to close a contract row.

---

## 1. Why this is strict

`VG-02 §1`: the field cannot answer *"when an agent solves a task, what solved it?"* because model,
scaffold, prompt, tools, context strategy and retry policy are confounded in every published
result. The whole architecture exists to un-confound them.

The 2026 field measures **9.5–20 points** of harness-only variance on a fixed model. That is larger
than the model effect. It also means our ambient noise is large, and a delta below our own floor is
not a result.

**We have already failed this once.** Every row of `matrix_results_tier3_token_bucket.json` reported
`pre_passed: true` and `patch_length: 0` — the oracle passed *before the agent acted*, and the agent
changed nothing. One row spent zero tokens in 0.73s and scored as a pass.

---

## 2. Evidence labels — a number without one is unpublished

| Label | Meaning | May support |
|---|---|---|
| `unit` / `property` / `must-fail` | CI | Framework correctness |
| `lam-replay` | Gold-trajectory player | That the gym matches the cassette. **Never** capability |
| `cassette-vanguard` | `CassettePlayer` on the ModelPort dialect | That the loop matches a recorded proposal |
| `single-shot-complete` | One completion | That a model emits code from a spec |
| `chat-patch-loop` | Host extracts markdown, overwrites files | That a model repairs given tests. **Not a harness measurement** |
| `lab-execute-harness` | `Runtime.execute_harness` + declared departures | The production loop with a live model |
| `product-cli` | `vg run` → daemon → same loop | Q2 dogfood |
| `sealed-evaluator` | UID 10002, digest-verified oracle | Publication-grade verdict |
| `aa-floor` / `paired-holdout` | T8 protocol | **Any lift claim at all** |

**Two disqualifiers, applied before the label:**

- `bypass` — any effect executed outside `Kernel.dispatch`. **Not evidence about Vanguard.**
- `degenerate` — precondition already satisfied, zero effects, or zero tokens. **Refuses to score.**

**Cross-plane comparison is refused** (`M-18`). LAM-replay of one pack vs live of another is the
degenerate A/A that `D-06` forbids.

---

## 3. C1–C12 — the operational definition of cheating

A run **cheats** if any hold **and** the result is labelled agentic competence.

| ID | Defect |
|---|---|
| C1 | Gold tool trace replayed |
| C2 | Solution in prompt, comments or README copied into the workspace |
| C3 | Hidden oracle visible to the worker |
| C4 | Public tests are the only oracle and encode the algorithm |
| C5 | Host-side apply bypasses the kernel |
| C6 | Pass heuristic is `calls > 1` or `"passed" in output` |
| C7 | Instrument error counted as task fail **or** pass |
| C8 | Human edited source |
| C9 | Approval auto-signed but labelled product-unsupervised |
| C10 | Compatibility key differs on an undeclared axis |
| C11 | Same instances tune prompts **and** claim lift |
| C12 | Textbook task with no private holdout |

> **C9 is not cheating if declared.** A lab departure recorded in `labDepartures` is honest. An
> undeclared one is fraud. Never drop the field from a published row.

---

## 4. Outcome algebra — fail-closed

| Outcome | Condition |
|---|---|
| `pass` | oracle exit 0 **and** public exit 0 **and** no instrument error **and** allowed paths only |
| `public_overfit` | public green, oracle red — a **harness-hacking signal**, not a near-miss |
| `fail` | oracle red, episode completed, no instrument error |
| `abandoned` | turn / token / wall bound |
| `inconclusive` | provider, sandbox, evaluator or transport failure |
| `invalid` | leak-linter fail, human source edit, or oracle visible |

**`pass` is the only promotion bit.** `inconclusive` is excluded from **numerator and denominator**
(`L-07`) — otherwise induced rate limits can manufacture a lift.

---

## 5. The refusal conditions your runner must call

`benchmarkings/guard.py`. Every runner calls it; there is no opt-out.

| Trigger | Verdict |
|---|---|
| Pre-repair oracle passes on a repair task | `inconclusive:precondition_satisfied` |
| Zero effects applied and post-oracle passes | `inconclusive:no_intervention` |
| Zero prompt and completion tokens | `inconclusive:model_not_invoked` |
| Provider/transport failure | `inconclusive:instrument_error` |
| Evaluator absent or unattested | `inconclusive:no_verdict` |
| Containment report absent or failing | **publication blocked** |

Each ships with a planted counterpart that must be refused. **The tests are the deliverable.**

---

## 6. Splits — contamination is one-way

| Split | Access | Role |
|---|---|---|
| `DEV` | Unrestricted | Gym, prompt debugging |
| `HOLDOUT` | Read at comparison time only | Ceiling; DNA paired trials |
| `SEALED` | Touch ledger; depleting | Publication / training check |
| `LIVE` | Operator | Verifier–deployment gap |
| `DEPLOYMENT` | After ship | Correlation with HOLDOUT |

**Using HOLDOUT to tune a prompt burns it to DEV forever.** One peek burns it. The touch ledger
records the burn — record it honestly; an unrecorded burn poisons every later comparison silently.

---

## 7. Statistics

- **No p-values below n≈20.** At n∈{1,2,3} report a **case study with full traces** (`M-28`).
- McNemar exact for paired binary — report **both** discordant counts, effect size and CI.
- Paired bootstrap for cost and latency.
- **Survival methods for timeouts** — treating a timeout as failure biases the slower arm, usually
  the more capable one.
- Pre-register hypotheses, primary metric, alpha, correction, stopping rule, manifest digests —
  **hashed before any arm runs**. Optional stopping is forbidden.
- Report per-arm instrument-error rate. **Asymmetry is a confound, not a footnote.**

---

## 8. Citation hygiene — this applies to us

Every externally sourced number carries its **evidence class and scope**, or it is not cited.

Two real examples of the failure, both from internal prose:

- *"Isolated subagents yield up to 90% benchmark improvements and cut token bloat 84%."*
  **False as stated.** The 90.2% was a multi-agent system vs single-agent on **one vendor's
  internal research eval** — not a public benchmark, unrelated to capability leases. The 84% was
  **context compaction** on a 100-turn eval, not subagents.
- *"78.4% token reuse"* — appears in internal KPI markdown with no measurement behind it.

A programme whose thesis is *"what solved it?"* cannot launder its own citations. This is `C10`
applied to prose.

---

## 9. Budget protocol

Calibration first. Local Ollama is the default spend; cloud is a scarce instrument.

1. Ollama light, T1, max-turns 8 — record the tool histogram either way.
2. Ollama heavy, T1. **If no `patch.apply` after two models → a harness/tool-schema defect. Do not
   buy cloud.** Cloud does not fix a dialect bug.
3. One free cloud id, T1 only.
4. T2 only if T1 passed.
5. DNA A/B only if a model can patch.

**Hard stop:** remaining ≤ 0 → no paid calls without a recorded Project Lead waiver. Treat
provider "free" as **unknown pricing** until `pricing_known=true` on the receipt.

---

## 10. What may and may not be said

**May:** "every privileged effect traverses one capability-mediated dispatch sequence" · "the
evaluator runs under a separate OS identity, unreachable from every capability the episode holds" ·
"here is a trajectory, here is which component was active, here is what it cost".

**May not:** "we evaluated three harness manifests" (unless they demonstrably differ) · "model X
passes tier N" (unless non-degenerate) · "the harness improves outcomes" (without floor + pairing +
pre-registration) · "SOTA" · "AGI-like".
