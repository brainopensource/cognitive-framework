# Part VII — The Measured Ladder, and the SOTA Solution Plan

**Subject** `feat/strongforce_beta_release_v093`, HEAD `5243866b`
**Author** Claude Opus 5 · **Date** 2026-09-04
**Class** report · **Authority** descriptive · **Truth plane** AS_BUILT (measured)
**Complements** [`part1-evidence.md`](part1-evidence.md) … [`part6-antipatterns-and-framework-feedback.md`](part6-antipatterns-and-framework-feedback.md) and [`opus_solution.md`](opus_solution.md)

**What is new in this part.** Parts I–VI diagnosed the harness from source and historical
artifacts. `opus_solution.md` proved a working agent on two ad-hoc tasks. **This part runs the
project's own frozen 20-task suite** across three models and two difficulty tiers, with oracle-
integrity verification, and folds the result into a single consolidated engineering plan.

**Spend** 14,775 µUSD on the ladder; 23,174 µUSD ($0.023) cumulative across all measurement in
this review. Inside the authorised $0.10 / 100-call budget.

**Evidence** [`evidence/ladder_results.jsonl`](evidence/), `ladder_results_hard.jsonl`,
`ladder_results_glm.jsonl`, plus `matrix_runner.py` and two full ledger exports.

---

## 1. Method

**Task source.** `benchmarks/benchmark_20_suite`, `task_set_digest
sha256:796b6666…`, unmodified. Tasks 11–20 are Greenfield (PRD in `README.md`, oracle
`test/test_suite.py`); tasks 01–10 are Brownfield (spec in `docs/SPEC.md`, a seeded defect in
`src/`, and a falsifier oracle).

**Harness.** `vg-code-balanced`, profile `local`, `interactive=False`, plus the five Phase-1
fixes from [`opus_solution.md`](opus_solution.md) §4 applied **in-process only — zero repository
edits**: `NATIVE` tool-call profiles, and the missing `S8-B-04` approval threshold raised from the
hardcoded `"low"` to `"critical"`.

**Credential handling.** `ladder.py` parses `.env` in-process via `os.environ.setdefault` and never
echoes a value. `OPENROUTER_API_KEY` appears on no command line, in no log, and in no committed
artifact.

**Three integrity controls**, because a `tests-pass` oracle invites reward hacking:

1. **External oracle.** Pass/fail is computed by this report's runner executing the suite's own
   `pytest` file, never by the agent's self-report or the harness terminal state.
2. **Oracle-tamper digest.** Every `test/*.py` is SHA-256 compared against the frozen suite after
   the run. **All 9 runs: `UNTAMPERED`.**
3. **Brownfield diff review.** Each defect repair was read by hand to confirm a real fix in `src/`
   rather than a weakened assertion.

---

## 2. Results

| # | Task | Tier | Model | **Oracle** | Terminal | Turns | µUSD | Wall s | Waste |
|---|---|---|---|---|---|---:|---:|---:|---:|
| 1 | `11_kv_lru_ttl_store` | GF med | openrouter/free | **PASS** | abandoned | 12/12 | **0** | 316.6 | 5/12 |
| 2 | `12_finite_state_machine_workflow` | GF med | openrouter/free | **PASS** | abandoned | 12/12 | **0** | 129.7 | 3/12 |
| 3 | `19_markdown_section_splitter` | GF med | openrouter/free | **PASS** | abandoned | 11/12 | **0** | 183.5 | 2/11 |
| 4 | `20_event_bus_pubsub_channel` | GF med | openrouter/free | **PASS** | abandoned | 12/12 | **0** | 211.0 | 3/12 |
| 5 | `13_semver_dependency_resolver` | GF hard | deepseek-v4-flash | **PASS** | abandoned | 15/15 | 4,180 | 78.7 | 5/15 |
| 6 | `17_json_canonicalizer_jcs` | GF hard | deepseek-v4-flash | **PASS** | abandoned | 15/15 | 2,892 | 52.8 | 5/15 |
| 7 | `01_rate_limiter_lease_recovery` | **BF** | deepseek-v4-flash | **PASS** | abandoned | 15/15 | 3,640 | 86.1 | 6/15 |
| 8 | `10_graph_ppr_dangling_node_sink` | **BF** | deepseek-v4-flash | **PASS** | abandoned | 15/15 | 2,827 | 65.8 | 5/15 |
| 9 | `13_semver_dependency_resolver` | GF hard | **glm-5.3-flash** | **FAIL** | `instrument_error` | 3/15 | 1,236 | 286.3 | 0/3 |
| 10 | `17_json_canonicalizer_jcs` | GF hard | **glm-5.3-flash** | **FAIL** | `instrument_error` | 3/15 | 368 | — | 0/2 |

Row 10 landed after the first draft of this part and **reproduces row 9 exactly**: same terminal
reason, same turn index, no implementation file written. Its runner row was reconstructed from the
ledger because the forensics step raised `sqlite3.OperationalError: disk I/O error` after the
episode had already ended — a fault in *this report's* harness under concurrent tmpfs access, not
in Vanguard. The ledger itself opens cleanly read-only and is the source for that row.

```
Greenfield  6/8 PASS       Brownfield  2/2 PASS       Overall  8/10 PASS
deepseek-v4-flash  4/4     openrouter/free  4/4       glm-5.3-flash  0/2  (both instrument_error)
```

**Every failure in this ladder — 2 of 2 — is the same harness defect (§3.1), not a model result.**

### 2.1 The baseline this replaces

`benchmarks/benchmark_20_suite/benchmark_20_results.json`, same suite, same harness code:

```
pass_rate_pct: 9.5    n: 21    turns: Counter({1: 21})
```

**2/21, every run terminating at turn 1.** Five configuration fixes later, free-tier models clear
medium greenfield tasks and `deepseek-v4-flash` clears RFC-8785 canonicalization and two seeded
algorithmic defects. Nothing about the model, the architecture, or the task set changed.

### 2.2 Efficiency, per oracle-verified success

| Model | µUSD/success | tok in | tok out | Wall s | Turns |
|---|---:|---:|---:|---:|---:|
| openrouter/free | **0** | 56,632 | 8,390 | 210.2 | 11.8 |
| deepseek-v4-flash-0731 | 3,385 | 77,556 | **1,944** | **70.8** | 15.0 |
| glm-5.3-flash | — (0/1) | — | — | — | 3.0 |

**Model selection, on measured evidence:**

- **`deepseek/deepseek-v4-flash-0731` is the correct pack default.** 4.3× fewer completion tokens
  than free tier, 3× faster wall-clock, and the only model that cleared the hard tier. Note it is
  also the only model the adapter runs **non-streaming** (`stream_choice = False if "deepseek" in
  name`), which §3.1 shows is not a coincidence.
- **`openrouter/free` is a genuine CI tier.** 4/4 medium greenfield at **$0.00**. Use it for smoke
  tests, protocol regression, and pre-merge gating — not for hard tasks or latency-sensitive work.
- **`glm-5.3-flash` cannot be scored at all, and this is now proven rather than suspected.** Both
  runs died at turn 3 from the identical non-retryable stream error (§3.1) having written no
  implementation file. Its capability is `undeterminable`, not `fail` — recording 0/2 as a model
  result would be exactly the confusion [`part6`](part6-antipatterns-and-framework-feedback.md)
  §N13 warns about. **A streaming model currently cannot complete a task on this harness.**

### 2.3 Proof the passes are real

**Brownfield `01_rate_limiter_lease_recovery`** — tests untampered, minimal correct fix:

```diff
     def clean_expired(self, current_time: float) -> int:
-        # BUG: Expired leases are popped from active_leases,
-        # but self.available is NOT refunded with the expired tokens!
         expired = [lid for lid, data in self.active_leases.items() if data["expires_at"] <= current_time]
         for lid in expired:
-            self.active_leases.pop(lid, None)
+            data = self.active_leases.pop(lid)
+            self.available += data["tokens"]
         return len(expired)
```

**Brownfield `10_graph_ppr_dangling_node_sink`** — a real algorithmic correction:

```diff
-                # BUG: Dangling nodes (neighbors == []) absorb probability mass!
+                else:
+                    # Dangling node: redistribute retained mass alpha * p[u]
+                    next_p[seed_node] += alpha * p[u]
```

**Greenfield `11_kv_lru_ttl_store`** — 70 lines authored from a PRD by a *free* model, using
`threading.RLock`, `time.monotonic()`, and `OrderedDict.move_to_end` for LRU with TTL expiry.
Oracle: `3 passed in 0.16s`.

One incidental observation supporting the `str_replace` recommendation in
[`part3`](part3-sota-agent-engineering.md) §5: the PPR whole-file write dropped the file's trailing
newline (`\ No newline at end of file`). Harmless here; it is the class of collateral edit an
exact-match primitive does not produce.

---

## 3. Five defects the ladder found that source review did not

These are **new**, additional to defects A–E in [`opus_solution.md`](opus_solution.md) §2, and all
were invisible until real multi-turn runs were executed.

### 3.1 Defect K — a malformed SSE chunk destroys the whole episode, non-retryably

**Both failures in the ladder**, and it is the harness, not the model. Reproduced twice, on two
different tasks, at the same turn index, with the same message.

```json
{ "kind": "EpisodeCompleted", "reason": "instrument_error", "turn": 3,
  "detail": "provider streaming response was malformed, truncated, or empty" }
```

GLM had already completed two successful `fs.read` effects and one `fs.search`. Turn 2 showed
`ttft_millis: 39064` and `completion_tokens: 2464` — a long generation over a slow stream. One bad
chunk, and **all prior work was discarded**.

`adapters/models/openrouter.py:1095` and `:1112`:

```python
if proposal is None:
    return Result.fail(
        kind="instrument_error",
        message="provider streaming response was malformed, truncated, or empty",
    )                                    # ← no retryable=True
```

Compare its sibling twelve lines earlier at `:930`:

```python
return Result.fail(kind="instrument_error", message="provider stream retries exhausted",
                   retryable=True)       # ← retryable
```

Three compounding faults in one place: (a) the retry flag is missing, so `protocol_recovery` never
engages; (b) the module *defines* `_MALFORMED_STREAM_MESSAGE` at `:943` and both call sites use a
duplicated literal instead; (c) `_EMPTY_PROPOSAL_RETRIES = 1` exists for the adjacent
empty-proposal case, so the machinery is present and simply unused here.

**Why this is a top-priority fix:** it is model-correlated by construction. deepseek is the one
model routed non-streaming, so this defect *cannot* fire for it — which means the harness is
silently biased toward its own default model and against every streaming provider. Any A/B between
deepseek and a streaming model today measures the stream parser, not the models.

**Fix:** add `retryable=True`, use the constant, and re-run GLM. ~3 lines.

**Reproduction (2/2 GLM runs):**

```
task 13  turn 3  EpisodeCompleted  instrument_error  "provider streaming response was malformed…"
task 17  turn 3  EpisodeCompleted  instrument_error  "provider streaming response was malformed…"
```

Both had completed 2–3 successful observation effects first. All of it was discarded.

### 3.2 Defect L — every effect emits `EffectStarted` twice

Adjacent, identical, same `descriptorDigest`, same `leaseId`:

```
seq 51  EffectStarted  fs.read  descriptorDigest sha256:9ebd4e69…  leaseId lease-1
seq 52  EffectStarted  fs.read  descriptorDigest sha256:9ebd4e69…  leaseId lease-1
```

Present in **all 9 runs, every model**. In a system whose central claim is `State = fold(events)`
and whose doctrine is *"every privileged side effect records durable pre-effect intent"*, a
duplicated intent record is a correctness defect in the authoritative plane, not a cosmetic one:
any reducer that counts intents, any cost fold, and any replay-derived `AgentView` double-counts.

### 3.3 Defect M — typed budgets are not populated for effects

```json
{ "kind": "BudgetReserved",  "reason": "reserved",  "reserved": {} }
{ "kind": "BudgetCommitted", "reason": "committed", "settlement": {"usd_micros": -1} }
```

Empty reservations and a `-1` sentinel settlement on **essentially every effect in every run**
(e.g. 20/20 for `17_json_canonicalizer_jcs`). Typed multi-dimensional budgets are one of the
project's headline differentiators over ordinary agent frameworks
([`part6`](part6-antipatterns-and-framework-feedback.md) §2.1). At the effect boundary they are
recording *unknown*. Model spend is metered correctly in `ProposalProduced.diagnostics`; effect
cost is not.

### 3.4 Defect N — the absent `finish` verb costs 31% of all turns

Quantifying Defect E from [`opus_solution.md`](opus_solution.md) §2.5:

```
None/finish proposals: 34 of 110 total turns = 31%
7 of 9 runs terminated by hitting max_turns, not by completing
```

Per-run waste ranges 2/11 to 6/15. The agent finishes the work, then spends a third of the
episode declaring completion into a protocol with no completion verb. This is simultaneously the
cheapest fix in the review (add an existing JSON file to three manifests) and the largest single
source of wasted spend and latency — it fully explains why free-tier runs *appear* slow at 210 s.

### 3.5 Defect G, now quantified — 178× workspace amplification

`PYTHONPYCACHEPREFIX` points inside the workspace. Measured on `13_semver_dependency_resolver`:

```
workspace/cache/   5.7 MB   248 .pyc files
workspace/src/      20 KB
workspace/test/      8 KB
```

**5.7 MB of build artifacts around 32 KB of actual content.** This is not a housekeeping issue:
`changed_files` and `workspace_digest` are the inputs `AdmissionGate` and every diff-based oracle
depend on. While 248 spurious files land in the tree on every run, `before_digest != after_digest`
carries no information, and the greenfield admission rule proposed in §4 (`changed_files ≠ ∅`)
would pass on `.pyc` churn alone. **Fix this before implementing that rule.**

### 3.6 Defect O — the enforced budget ceiling does not match the manifest

`EpisodeStarted` records `budgetCeiling: {usd_micros: 1000000, millis: 1800000, tokens: 64000}`.
`packs/code-default/harness.yaml` declares `usd_micros: 250000`. The enforced ceiling is **4× the
declared one**, and the manifest's `turns` and `depth` dimensions are absent from the recorded
ceiling entirely. Composition is not carrying the declared budget through to the governor.

---

## 4. What this changes about the plan

The consolidated priority, superseding [`part5-roadmap.md`](part5-roadmap.md) §Sprint-order where
they differ. Measurement moved three items and demoted one.

| Rank | Item | Why it moved | Effort |
|---|---|---|---|
| 1 | `finish` verb in all presets (**Defect E/N**) | Measured at 31% of all turns; the file already exists | ~1 h |
| 2 | Retryable malformed stream (**Defect K**) | The only ladder failure; silently biases every model comparison | ~3 lines |
| 3 | Native tool-call profiles (**Defect A**) | Precondition for everything | ~20 lines |
| 4 | `S8-B-04` approval threshold (**Defect C**) | Precondition; removes a hardcoded literal that already carries a TODO | ~30 lines |
| 5 | Terminal state must reflect reality | **8/8 inversion** — see §5 | ~40 lines |
| 6 | `init` writes `workspace.toml` + `git init` (**Defect D**) | Verification cannot run without it | ~20 lines |
| 7 | Duplicate `EffectStarted` (**Defect L**) | Ledger integrity — the authoritative plane | ~10 lines |
| 8 | Effect budget settlement (**Defect M**) | A headline capability recording `unknown` | ~1 d |
| 9 | Budget ceiling passthrough (**Defect O**) | Declared ≠ enforced | ~2 h |
| 10 | Freeze suite + `results.jsonl` + `bench compare` | §6 — already prototyped here | ~1 d |
| — | *Demoted:* `str_replace` edit primitive | Real, but whole-file `patch.apply` passed 8/9. **Not** the blocker Part III assumed | later |
| — | *Demoted:* LDA `IndexPort` wiring | Real leverage, but 2/2 brownfield passed on grep alone at this repo scale | later |

The two demotions are the most important corrections in this part. [`part2`](part2-diagnosis.md)
ranked the edit primitive and retrieval as D1/D2. **Measurement does not support that ranking at
this task scale.** Unified diff and regex search were sufficient for 8 of 9 oracle passes. They
will matter at repository scale; they are not what is standing between this project and a working
product, and spending a sprint on them before the ten items above would repeat the exact
prioritisation error the project has already made once.

---

## 5. The terminal-state inversion is now the headline defect

**8 of 8 oracle-verified passes reported a failure terminal state.** Every single one.

```
oracle PASS  →  terminal "abandoned"     8/8
runs ended by max_turns rather than completion   7/9
```

This is not cosmetic. It is the reason every historical number in this repository is wrong in the
same direction, and it explains three previously unexplained artifacts:

| Artifact | Reading |
|---|---|
| `NO_PATCH` 123 rows | Work performed, never admitted |
| `live_27_attempts.json` `PASS 16` vs `live_27_*_report.json` `NO_PATCH 27` | Two planes disagreeing about one run — the oracle saw success, the harness reported failure |
| `benchmark_20_results.json` 9.5% | An instrument reading, not a capability measurement |

The fix is the `finish` verb plus admission that accepts a greenfield success shape
(`exit_code == 0 ∧ changed_files ≠ ∅` where no test suite is declared, retaining
`executed_test_count > 0` wherever one exists). Until then **no benchmark this project runs can be
believed, in either direction** — and that includes these results, which is precisely why §1's
external oracle exists.

---

## 6. The instrument, dogfooded

`evidence/matrix_runner.py` is a working prototype of the honest schema
[`part2`](part2-diagnosis.md) §D7 asked for. It already emits, per run:

```json
{"suite_digest":"sha256:796b6666…","suite_size":20,"task_id":"…","task_kind":"Brownfield",
 "model":"…","provenance":"live","model_real":true,"cost_provenance":"metered",
 "disposition":"PASS","terminal":"abandoned","turns":15,"max_turns":15,
 "tokens_prompt":…,"tokens_completion":…,"usd_micros":3640,"wall_s":86.1,
 "proposals":[…],"denials":[…],"effects":[…],"oracle_tail":"…"}
```

Three fields earn their place and are not in any existing report format:

- **`disposition` is externally computed** and structurally separate from `terminal`. Had this
  existed, the inversion would have been visible on day one.
- **Oracle-tamper digest** — without it, a `tests-pass` oracle is unfalsifiable.
- **`proposals[]`** — the `None/finish` count in this array *is* the Defect N metric. Turn waste
  becomes a standing measurement rather than a discovery.

**Adopt this as the results schema.** Add `n`/`suite_size` refusal (`pass_rate` is refused when
`n < suite_size`), poison aggregates containing `model_real: false` into `undeterminable`, and make
a second `*_report.json` under `benchmarks/` a lint failure.

---

## 7. Building agents on this: the two packs to write

For "greenfield project from a prompt" and "fix this repo", the framework's answer is a manifest,
not Python. Measured guidance:

**`vg-greenfield`** — validated shape from rows 1–6:
`read` · `search` · `patch` · `test` · **`finish`** (from `vg-code-max-v3luna/finish-tool.json`);
`turns: 20` (rows 1–4 needed 11–12; hard rows saturated 15); admission on
`exit_code == 0 ∧ changed_files ≠ ∅`; brief that names the oracle path explicitly — every passing
run read the oracle test file as its second action, and that is what made a PRD tractable.

**`vg-brownfield`** — validated shape from rows 7–8: identical tools, plus a brief instructing
*read the spec and the failing test first, then apply the smallest correct fix, never weaken an
assertion*. Both defect repairs followed `read src → read test → patch → run tests` unprompted.

**For a Svelte or npm project**, one more change is mandatory and was not measured here: the
`proc.exec` selector allows only `git,pytest,ruff,python3`. No `npm`, no `node`, no `mkdir`, no
`ls`. Node-ecosystem greenfield is **structurally impossible** until that selector widens — or,
preferably, until `bash` runs inside the existing bubblewrap perimeter with the allowlist demoted
to the `hermetic` profile ([`part3`](part3-sota-agent-engineering.md) §4.2).

---

## 8. Limits of this evidence

Stated plainly, because the project's best property is not overclaiming:

1. **n = 10, one attempt per cell.** No variance estimate, no paired statistics. This establishes
   *the harness can pass real tasks*, not a pass rate. `bench compare` needs the full 20 × k design.
2. **9 of 20 suite tasks.** Tasks 02–09, 14–16, 18 were not run.
3. **GLM has zero usable data points.** Both runs died on Defect K; its capability is untested.
4. **The fixes were applied in-process**, not landed. A real implementation must reproduce this
   through the manifest and composition path, with falsifiers.
5. **No local-model evidence.** The only `llama-server` here is ollama's bundled copy, which
   reports `no usable GPU found` and runs a 27B at 4.26 tok/s. A Vulkan build with `--jinja` and a
   ≥7B coder is required before local runs mean anything.
6. **Single repository scale.** These tasks are 1–3 files. The demotion of the edit primitive and
   the index in §4 is scoped to that; both claims should be re-tested at repository scale.

---

## 9. Conclusion

The measurement inverts the project's working assumption. The substrate was never the problem and
the models were never the problem: a **free** model solved four medium greenfield tasks and
`deepseek-v4-flash` solved RFC-8785 canonicalization, semver constraint resolution, and two seeded
algorithmic defects — 8 of 10 oracle-verified, zero test tampering, for 1.5 cents. **Both
failures were the same harness defect.**

What stood in the way was a two-key dictionary, a hardcoded `"low"`, a missing TOML file, an absent
`finish` verb, a parser speaking a different dialect than the prompt it ships with, and a
non-retryable stream error. Every diagnosis in this report was reconstructed **purely from
`events.sqlite3`**, with no instrumentation added — which is the event-sourced architecture
earning its cost, and the strongest available argument for keeping it exactly as it is.

Ten fixes, roughly a week, no subsystem deleted. Then publish the number.
