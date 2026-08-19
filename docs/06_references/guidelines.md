# Vanguard Guidelines — and why that usage is the training set for meta-cognition

Vanguard is not “an agent that writes code.” It is a **meta-harness compiler**: a declarative pack plus a live `ModelPort` compile into a specialised coding agent, while an **exterior judge** that the agent cannot reach scores the episode. The one-sentence identity (`docs/SPEC.md` preamble):

> What solved it must be separable, and the judge must be unreachable from the judged.

That sentence is also the **dataset contract**. Every coding challenge you put in `benchmarkings/` is not a demo. It is a row that later waves will treat as:

- a paired A/B instance (McNemar, `docs/04_annex/MEASUREMENT.md`);
- a trajectory that, without transformation, is a DPO harvest row (Invariant **I-9**);
- a genome sample (`FrozenHarness` digest) for Phase-2 mutation (SPEC §5.2);
- **not** a self-grade, **not** a competence graph, **not** a reason to touch Layer 0.

Backend is ready. CLI/TUI is not the gate. Local Ollama (Windows host) and OpenRouter (`OPENROUTER_API_KEY`, never printed, never committed) are the two `IModelProvider` cells we can already swap **without changing the harness genome**. That swap is the first clean treatment you will ever run.

Phase-2 meta-cognition (`mhf.planner.meta-reflector`) is **not** “the agent thinks harder.” It is a second `IPlanner` at scheduler slot `outer`, invoked at optional `reflect()`, leased separately, **forbidden from touching the workspace**. It may propose manifest mutations, skill cards, and new oracle preregistrations. Fitness is the lab. Promotion is a signed pointer, not a scalar reward (`ADR-0015`). **M5’s statistical-power gate is a 200-task suite.** Everything below is how to start producing that suite honestly while teaching people the basics.

---

## 0. Mental model (four objects, one lifecycle, one tuple)

Newcomers mix four things. Keep them distinct forever.

| Object | What it *is* | What it is *not* | Where it lives today |
|---|---|---|---|
| **Challenge** | Broken workspace + public tests + hidden oracle + brief | The solution, the model, the pack | `fixture/`, `oracle/`, `prompt.txt`, `preregistration.json` |
| **Harness (genome)** | Content-addressed compile of manifest + plugins/tools/policies | The LLM | `vg-code-default` → later `FrozenHarness` digest |
| **Model route** | `ModelPort` cell: Ollama vs OpenRouter | The experiment, unless you declare it as \(\mathcal{D}\) | `--model ollama/…` vs `deepseek/deepseek-v4-flash` |
| **Runner / instrument** | Glue that copies fixture, calls `Runtime.execute_harness`, scores, writes artifacts | The kernel | `benchmarkings/zero_hint_v1/run_live_agent.py` |

Lifecycle (as-built + SPEC completion):

```text
observe → propose → authorize → effect → receipt → evaluate → (reflect)*
```

`reflect` is Phase-2. Layer 0 only knows an `IPlanner` *may* be offered the terminal receipts. **I-11:** Phase-1 scheduler is sequential. Do not fan-out “to get more data faster.” Independence groups are gated on measurement, not enthusiasm.

Every published comparison is an **instrument tuple** (`MEASUREMENT.md` §5.6):

\[
\langle \mathcal{K}_{\text{compat}},\; \mathcal{D}_{\text{treatment}},\; \mathcal{S}_{\text{strat}},\; \mathcal{M}_{\text{meta}} \rangle
\]

- \(\mathcal{K}\): same task digest, same split, same harness commit, same sampling, same evaluator image, same containment.
- \(\mathcal{D}\): **exactly one** declared axis (model route **or** pack **or** compaction — never “and also I tweaked the prompt”).
- \(\mathcal{S}\): tier, language, defect class.
- \(\mathcal{M}\): timestamps, node, operator — **excluded from equality**.

If \(\mathcal{K}\) differs in an undeclared dimension, the comparison **refuses**. That is how you teach people not to p-hack by accident.

**Two first experiments that are actually scientific:**

1. **Model A/B (same genome):** `deepseek-coder-v2:16b` (Ollama) vs `deepseek/deepseek-v4-flash` (OpenRouter). Treatment = provider/model. Harness frozen.
2. **Pack A/B (same model):** `vg-code-default` vs `vg-shell-only`. Treatment = genome. Model frozen (`M-13`).

Do not mix them in one table and call it “the system got better.”

---

## 1. Folder layout — challenge once, genomes hashed, models as routes

Shared **challenge** (the instance). Two **route profiles** (not two copies of the bug). Runs are append-only.

```text
benchmarkings/
  cursor_composer_challenge/          # THE INSTANCE (task_digest)
    README.md                         # human teaching: what is visible, what is sealed
    FAMILY.md                         # preregistered hypotheses, alpha, stopping rule (M-06)
    run_episode.py                    # instrument — must not import kernel internals
    splits.json                       # DEV | HOLDOUT | (later SEALED)
    challenge/
      prompt.txt
      preregistration.json            # allowed paths, tools, turn/token ceilings, oracle digest
      fixture/initial/                # model-visible: source + public tests
      oracle/                         # UID-10002 plane; never copied into worker

  cursor_composer_s_dscv2-16b/        # ROUTE PROFILE A  (D = model)
    model.json
    runs/<utc>/                       # result.json, trajectory-shaped events, final.diff

  cursor_composer_s_dsv4f-OR/         # ROUTE PROFILE B
    model.json
    runs/<utc>/
```

`model.json` is **not** a harness. It is a route cell:

```json
{
  "label": "cursor_composer_s_dscv2-16b",
  "provider": "ollama",
  "model": "deepseek-coder-v2:16b",
  "endpoint": "http://127.0.0.1:11434/v1/chat/completions",
  "sampling": {"temperature": 0.0, "maxTokens": 2048},
  "treatment": "model_route"
}
```

```json
{
  "label": "cursor_composer_s_dsv4f-OR",
  "provider": "openrouter",
  "model": "deepseek/deepseek-v4-flash",
  "endpoint": "https://openrouter.ai/api/v1/chat/completions",
  "sampling": {"temperature": 0.0, "maxTokens": 2048},
  "treatment": "model_route"
}
```

Secret: `OPENROUTER_API_KEY` from process env or repo-root `.env` via `load_api_key` (mode `0600`, untracked, no interpolation). **Never log it.** Ollama uses a dummy key at the OpenAI-compat waist; the endpoint is local.

Record in every `result.json`:

- `harness` + `gene_digests` (already in `zero_hint_v1`);
- `model.fingerprint` (provider, id, endpoint class);
- `labDepartures` (auto-approve, SkipEvaluator, maxTokens) so you do not later pretend this was UID-10002;
- `evidence_label` (`lab-execute-harness` vs `live-ollama` vs `live-openrouter`).

That is how I-9 starts before `mhf.trajectory/1` is fully wired: **the row exists even if the schema name is still lab JSON.**

---

## 2. Step 1 — Author the challenge as an evaluation subject, not a puzzle with a key in the drawer

A Phase-1 coding instance is an `EvaluationSubject` with a preregistered oracle (`IEvaluationGate.preregister`). Pedagogy:

**Visible to the inner agent (worker, UID 10001):**

- `fixture/initial/**`
- `prompt.txt` as `TaskContext.brief` (not as a workspace file, so it cannot be grepped as “the answer”)
- public tests — behaviour, not algorithm names, not FIXME arrows

**Invisible forever to the inner agent:**

- `oracle/`
- `FAMILY.md`, `preregistration.json`, `runs/`
- any golden patch

**Visible only to the exterior judge (and, later, to the outer reflector as *signed verdict + trajectory*, never as workspace):**

- oracle tests
- allowed-path lint
- containment report

This is Invariant **I-5**. If the model can `fs.read` the oracle, you did not run Vanguard; you ran a leak.

**Defect classes worth teaching (and later stratifying in \(\mathcal{S}\)):**

| Class | Why it produces signal | Example already in-tree |
|---|---|---|
| Fencepost / window | Public tests pass a tumbling implementation; oracle needs any closed window | `test002_rate_window` |
| Representation | Float vs integer cents | `test003_invoice_cents` |
| Multi-file coupling | Patch two modules; public tests under-specify edges | `test005_named_amounts` |
| Concurrency + time | Needs lock + monotonic clock | `tasks_phase3` token bucket |

**Do not** store the solution. The “answer” is the **posterior over trajectories** given the oracle. For DPO (M6) you need *divergent* trajectories on the **same** `(task_digest, harness_digest, context_digest prefix)` with opposite signed verdicts. A unique golden patch produces almost no rejected pairs.

Preregistration is a **hashed artifact** (`M-06`): hypotheses, primary metric (`oracle_green ∧ path_subset ∧ public_green`), α, Holm family, stopping rule, max turns. Optional stopping after peeking at OpenRouter cost is a different test than the one whose p-value you will quote.

---

## 3. Step 2 — Reuse the genome; do not invent a MetaLoopEngine

For teaching and for the 200-task grind, compile **`vg-code-default`**.

That pack is already A-5: tools (`fs.read`, `fs.search`, `patch.apply`, `proc.exec`), L1 system prompt, aliases, skills (`pytest-green`, `read-receipt-before-repatch`), grant ceiling on `/workspace`, `coding-oracle@3` named as evaluator.

**Harness = f(manifest, plugins).** Two identical manifests + plugin digests ⇒ byte-identical digest ⇒ attributable A/B. If a student “improves the prompt in the runner,” they have silently moved \(\mathcal{D}\) off the genome and **contaminated** every later mutation experiment.

When you *do* want a custom pack (M4 parity): clone `vg-code-*` as data only. Zero `layer0/` / `kernel/` diffs (**I-7**). Skills are distilled procedures that enter through the mutation+lab pipeline (§5.4), not markdown pasted into the brief.

**Lab honesty (`zero_hint_v1` already documents this):**

1. Auto-approval of privileged diffs (no human). `interactive=True` + lab signer. `interactive=False` is `Mode.BENCHMARK` and **fails closed** on approval (K-17) — do not “fix” that to make CI green.
2. Oracle after the episode, not IsolatedEvaluator UID 10002 — label it.
3. `maxTokens` raised from adapter default 256.

Those are \(\mathcal{M}\) and lab-departure flags, not reasons to claim M3’s `oracle_green` gate.

---

## 4. Step 3 — The runner is an instrument, not cognition

Fork `benchmarkings/zero_hint_v1/run_live_agent.py`. It already:

1. Loads the instance.
2. Copies fixture → temp git repo; `leak_paths()` fail-closed.
3. Records public tests **failing** (precondition; `guard.py` refuses `pre_passed`).
4. Injects `OpenRouterModel` at the lab seam (`verdict.openrouter_model`) — **entrypoint never imports adapters** if you keep that seam.
5. Calls `Runtime.execute_harness(manifest, TaskContext(...), model=, approver=, verifier=SkipEvaluator)`.
6. Scores public + oracle; writes `final.diff`, `result.json`, sanitised events.

**Kernel path:** `observe` compiles L1–L5 → `propose` on `ModelPort` → kernel authorize (grants, attenuation, budget) → sandbox effect → receipt → (lab) evaluate.

WSL2 → Windows Ollama: `127.0.0.1:11434` if mirrored; else `OLLAMA_HOST` from default route / `resolv.conf` nameserver (`tools/001_LLM_API_ROUTER/providers/ollama.py`). Confirm `deepseek-coder-v2:16b` in `/api/tags` before burning OpenRouter budget.

LAM `generate()` scripts (`tasks_phase2_LAM`) are **not** this instrument. They produce completion text, not tool-loop trajectories. Mixing them into the 200-task suite is contamination (`M-20`) of the worst kind: you will train DPO on a different causal graph than production.

---

## 5. How the code comes into existence (and why that graph is the meta-cognitive prior)

The inner agent does not “output a file.” It emits **proposals** that become **one leased effect per turn** (kernel). Typical successful n-gram:

```text
fs.search → fs.read* → patch.apply → proc.exec(unittest) → (read receipt) → patch.apply* → proc.exec
```

`final.diff` is the workspace posterior. `receipts[].verb` is the **procedure**. Skill harvest (§5.4) mines n-grams with **verdict-conditional lift**, not “the model said pytest-green in English.”

Prefix attribution (SPEC §7): DPO pairs at the **turn** where two trajectories sharing a context digest diverge. That is why you must store per-turn `context_digest`, proposal, receipts, cost — not only the terminal diff.

**Calibration later (SPEC §5.3):** \(P(\text{pass}\mid\text{action}, \text{context})\) from ledger history; action score \( \mathbb{E}[\text{verdict gain}] - \lambda \cdot \text{reservation} \). Brier score per `harness_digest`. Your early runs are the prior. If you only keep `PASS/FAIL` booleans, you cannot calibrate; you can only mutate blindly.

**Outer loop (when it exists):** sees signed verdict + trajectory; **cannot** `patch.apply` the challenge. If your teaching materials show a “reflector that edits `limiter.py`,” you have violated capability-shaped meta-cognition and taught the wrong ontology.

---

## 6. Teaching sequence (so humans produce comparable rows)

| Lesson | They run | They learn | Dataset residue |
|---|---|---|---|
| T0 Fixture hygiene | `--check-fixtures` | Public tests red; no oracle leak | Discard |
| T1 One live episode | Ollama, 8–16 turns, `vg-code-default` | Tools are kernel-mediated; abandon ≠ fail | `runs/` with `evidence_label` |
| T2 Paired model | Same task, Ollama vs OpenRouter, identical sampling | \(\mathcal{D}=\) route; \(\mathcal{K}\) equal | Discordant pair |
| T3 Paired pack | Same model, `vg-code-default` vs `vg-shell-only` | Genome is the treatment (`PAIRING.md`) | Pack-discordant pair |
| T4 Guard literacy | Read `guard.py` refusals | `instrument_error` is excluded from numerator **and** denominator (`M-16`) | Honest N |
| T5 Split discipline | Tag DEV vs HOLDOUT | HOLDOUT is not a playground (`M-19`) | Uncontaminated promotion set |
| T6 Trajectory shape | Diff two `events.sanitized.json` | Cognition is a ledger fold (`I-4`) | I-9-shaped JSON |

**Curriculum anti-goals (SPEC §9):** no cosmology, no playbook DAG, no “the agent improved itself,” no always-on full-content capture (`REJ-12` — corpus is opt-in policy).

---

## 7. Dataset factory toward M5 (200 tasks) and M6 (DPO)

**Power (`MEASUREMENT.md`):** detecting a ~5-point effect against a realistic A/A floor needs **low hundreds of paired instances**. M5’s 200-task suite is not a round number; it is the minimum honest N for McNemar on discordant pairs. A/A on the **same** manifest; floor at 0% or 100% is **refused** (`M-07`).

**Factory rules:**

1. **Instance generation:** many small, stratified defects (parse, money, intervals, multi-file, later concurrency). Prefer *families* of 10–20 variants of one shape over 200 unique novels (reduces authoring cost; keep \(\mathcal{S}\) labelled so you do not overfit one shape).
2. **Split:** DEV for teaching and prompt-pack iteration; HOLDOUT locked for promotion; SEALED unused until publication protocol.
3. **Contamination ledger:** any instance whose trajectory entered a training corpus is **permanently** dead for eval (`M-20`). Tag `corpus_member: false` until M6 opt-in.
4. **Comparable arms only:** same `maxTokens`, temperature, turn ceiling, bwrap presence. Asymmetric HTTP timeouts are instrument error, not model failure.
5. **Cost non-vacuous (`M-17`):** Ollama USD = 0 is allowed if you still record tokens/ms; do not claim cost non-inferiority when every cell is zero.
6. **Primary metric for coding:** `oracle_green ∧ public_green ∧ changed ⊆ allowedPaths ∧ containment`. Public-only green with oracle red = `public_overfit` (already in `zero_hint_v1`).
7. **Secondary (process) metrics for meta-cognition later:** tool histogram, repair rounds, prefix-hit, Brier when priors exist, reservation vector `{usd_micros, millis, tokens, bytes, turns, depth}`.

**Prototype algorithms on DEV only:**

| Prototype | What you vary | Fitness |
|---|---|---|
| Escalation policy | Free → local 16b → flash | verdict gain − λ cost |
| Compaction | L4/L5 strategies | pass rate at equal token budget |
| Skill card on/off | `pytest-green` included | McNemar vs undeletable baseline |
| Edit format | unified diff vs later AST-anchored | M-12: equal expressive power |

Promotion to default pack pointer = **M5**: one mutation beats baseline, p < 0.05 exact McNemar, A/A floor respected, family preregistered. Not “looks better on three tasks.”

**M6 harvest:** pair on `(task_digest, harness_digest, context_digest prefix)`; chosen = signed pass, rejected = signed fail; anti-cheat lint; JSONL for DPO + SFT from passes. Then cassette-replay regression. Fine-tune **tier-1/2 local** models so the escalation curve falls — that is the economic thesis, not “train a frontier.”

---

## 8. Commands (basics you actually type)

From repo root, WSL:

```bash
# T0 — fixture is red and leak-free
python3 benchmarkings/zero_hint_v1/run_live_agent.py --check-fixtures

# T1 — local Windows Ollama (WSL client)
# export OLLAMA_HOST=http://<windows-host>:11434   # if 127.0.0.1 fails
python3 benchmarkings/zero_hint_v1/run_live_agent.py \
  --task test005_named_amounts \
  --manifest vg-code-default \
  --model ollama/deepseek-coder-v2:16b \
  --max-turns 16

# T2 — same instance, OpenRouter (key from env or .env, never printed)
python3 benchmarkings/zero_hint_v1/run_live_agent.py \
  --task test005_named_amounts \
  --manifest vg-code-default \
  --model deepseek/deepseek-v4-flash \
  --max-turns 16
```

When the custom factory exists, `--profile` + `--out-dir` only change \(\mathcal{M}\) (path), not \(\mathcal{K}\). Copy artifacts into `cursor_composer_s_dscv2-16b/runs/` vs `…_dsv4f-OR/runs/`.

Integrity (teaching “the moat is CI”):

```bash
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/scan_secrets.py
```

---

## 9. What not to do (honour table, operationalised)

| Temptation | Why it destroys the next waves |
|---|---|
| Single-shot `generate()` as “the benchmark” | No tools, no receipts, wrong causal graph for DPO |
| Golden patch in the fixture | No rejected pairs; agent copies instead of searches |
| Outer loop that edits the workspace | Meta-cognition must be capability-shaped (SPEC §5.1) |
| Unpaired “Ollama on easy / Flash on hard” | You measured the sample (`M-02`) |
| Peek HOLDOUT to tune skills | Irreversible contamination (`M-19`) |
| Claim PASS on HTTP 404 / empty completion | Instrument error; exclude from N (`M-16`) |
| New kernel feature “for reflection” | A-6 / ADR-M0-12: plugin at `outer`, never `MetaLoopEngine` |
| Scalar “reward” to pick a pack | Promotion is a frontier partial order (`REJ-11`) |
| Cosmology / 14-tier mind | ADR-M0-10; I-10 |

---

## 10. Are we on the right path? Evaluation that can fail

A path check is a **gate**, not a narrative.

| Wave | Question | Falsifier |
|---|---|---|
| Now (instrument) | Can we emit comparable paired rows with gene digests and no leaks? | `leak_paths` hits; \(\mathcal{K}\) incomparable; keys in logs |
| M3 | `code-default` ≥ v0.4.5 on dogfood + `zero_hint_v1` under paired McNemar; ≥1 un-mocked `oracle_green` | McNemar non-significant or instrument-dominated N |
| M5 | 200-task suite; one genome mutation beats baseline p<0.05 | Underpowered N; A/A degenerate; HOLDOUT used in training |
| M6 | Fine-tuned local ≥ free-tier pass at **lower** USD/episode | Pass rate up only because eval set leaked into SFT |
| Meta-cognition | Outer episode never holds `patch.apply` on the task workspace; `ReflectionProduced` is ledgered | Reflector writes `limiter.py` |

If T1–T2 cannot produce two `result.json` files with identical `gene_digests` and different `model.provider`, **stop**. You are not ready to discuss active inference.

---

## 11. Recommended first instance (same as last time, now justified)

Reuse `test005_named_amounts` or `test003_invoice_cents` as the **walking skeleton** of the *dataset factory*, not of the plugin runtime (that skeleton is M2’s echo plugin). Prove:

- fixture red, oracle sealed;
- Ollama 16b and Flash both traverse `execute_harness`;
- artifacts land in the two named folders;
- students can point at `gene_digests` vs `model` and say which is \(\mathcal{K}\) and which is \(\mathcal{D}\).

Then clone the instance shape 10× on DEV. Do not design the meta-reflector until HOLDOUT exists and A/A is non-degenerate.

---

**Bottom line for the next waves:** teach people to author **sealed instances**, compile **hashed genomes**, swap **model routes**, and emit **I-9 trajectories**. Meta-cognition is a leased outer planner that mutates genomes against a lab that already knows how to say *no*. The 16b vs Flash split is the first honest \(\mathcal{D}\). Everything else is a plugin, an event kind with an emitter, and a paired measurement — or it does not enter.