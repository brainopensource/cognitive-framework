# SOTA Harness, Isolated Evaluation, and Scientific Measurement Programme

**Classification:** Internal scientific audit and programme design (Tech Lead + Project Lead + measurement specialist).  
**Date:** 2026-08-16  
**Repository:** Aether-D-System / Vanguard  
**Status:** NON-NORMATIVE. Not in `docs/main_v4/00_vanguard_registry_v040.md` Chapter 2. Where this file and a v4 owner disagree, the owner wins (`PR-3`).  
**Code changes in this review:** none. This document does not authorise implementation, tagging, publishing of pass rates, or spending the live budget.  
**Companion findings (same day):** isolated-eval investigation in chat; this file is the durable, cited record.

---

## 0. Ruling in one page

**We are cheating in several published-looking numbers. We are not cheating in the one path that actually uses the production loop.** The difference is the entire scientific problem.

A **SOTA harness** in this programme is not “highest SWE-bench score this week.” Vanguard’s charter (`VG-02`) already forbids that substitution. SOTA here means:

> When an agent solves a coding task, **what solved it** (model, scaffold/DNA, prompt, tools, context policy, retry, human approval) is separable; the judge is unreachable from the judged; the number is labelled with its evidence class; and a later weight-training or harness-edit can consume **exact** trajectories without contaminating the holdout that will measure the edit.

That is a harder and rarer claim than a leaderboard row. It is also the only claim this architecture is built to make.

**Immediate consequences:**

1. **Do not publish** LAM replay, single-shot `generate()`, chat-and-overwrite loops, or `def add(a,b)` pings as model ceilings or harness lifts.
2. **Do treat** `benchmarkings/zero_hint_v1` + `Runtime.execute_harness` as the first honest **lab** coding instrument — labelled `lab-execute-harness`, with documented departures, currently showing **honest fails** (read-loop, no `patch.apply`).
3. **Do not** spend the remaining ~$0.50 on Tier-5/6/7 “frontier” toys, DNA A/B, or many-model sweeps until a calibration model can apply a patch on a hidden-oracle task.
4. **Do** treat LAM as a **gym and cassette factory**, Vanguard as the **instrument**, `lam.sqlite` + ledger events + `Recording` as the **future SFT/DPO substrate** — and keep those three objects from impersonating each other (`VG-01` §4.1; S7 D-01).
5. **Public benchmarks remain deferred** (`VG-10` `DEF-08`) until the A/A apparatus exists. **Training on the corpus remains deferred** (`DEF-09`, `MEM-7`) until contamination is per-instance checkable. This programme **records** for that future; it does not train now.

**Beta honesty (already audited):** there is still no trustworthy product path `vg run` → RuntimeService → governed loop → exterior verdict (`docs/reviews/todo/mvp_beta_delivery_audit_2026-08-16.md`, `BETA-MVP-AUDIT-REPORT.md`). Measuring “the CLI as coding harness” today measures a mock/feed client. Measuring `execute_harness` measures the runtime. Both are useful. Mixing them is fraud.

---

## 1. Authority, method, and non-claims

### 1.1 What this document may and may not do

| May | May not |
|---|---|
| Classify existing artefacts by evidence label | Relabel a cassette pass as live |
| Prescribe splits, KPIs, Recording fields, budget protocol | Invent three “top” OpenRouter ids (`D-13`) |
| Recommend a scientific path to SOTA *as an instrument* | Claim AGI, “harness cognition multiplier,” or that local 1.5B models pass Tier 3–4 because a markdown file said so |
| Map genes/DNA (manifests) to paired experiments | Require kernel changes so reconstructions “look like Claude” (`ADR-0060`, `D-02`) |

Normative owners used:

| Owner | Role here |
|---|---|
| `VG-01` §4 | Mock / cassette / live division of labour |
| `VG-02` | Claims and non-claims; coding is the first environment, not the ontology |
| `VG-03` | One loop; observe is a snapshot, never a live PTY handle |
| `VG-04` | `Recording`, `EvidenceClaim`, `CorrectionRecord` |
| `VG-05` | Judge exteriority; mutability classes; no self-grading |
| `VG-06` | Claim pipeline; `MEM-7` training opt-in; evaluator classes |
| `VG-07` | **CL-1..3**, McNemar exact, A/A floor, instrument tuple `M-18`, splits `M-19/M-20`, experiment registry |
| `VG-08` / `VG-10` | Phase 0 out; `DEF-08` public benches; `DEF-09` training |
| `VG-09` ADR-0057, ADR-0060 | Beta = Q1+Q2; generality = zero core change for a new domain |
| GTS-13C T6–T8, T1.11 | Coding harness, manifests, instrument, Recording contract |
| S7–S10 roadmap | `docs/reviews/todo/vanguard_LAM_manifests_plan_sprint-7-to-9.md` (non-normative packets) |
| V5 harvest | `docs/reviews/todo/vanguard_v042_and_v5_from_harness_src.md` (exact SFT, not DAG revival) |

### 1.2 Audit method

This review inspected source, fixtures, run artefacts, and normative text. It did **not** re-run live models. Claims about live episodes cite files already in tree (e.g. `benchmarkings/zero_hint_v1/tasks/test004_busy_merge/runs/20260816T084650Z/result.json`).

Three truths, as in the Beta audit:

- **HEAD / tree truth:** what the files contain.
- **Working-tree truth:** uncommitted KPI markdown and SQLite can lie independently of committed code.
- **Release truth:** what a clean clone can execute through the public CLI.

A number that exists only in `tools/002_LLM_API_MOCK/docs/LAM_logs_benchmarking_KPIS_dont_commit.md` is not a number under `VG-07` §0.

### 1.3 The biological dictionary (genes / DNA)

README Level 5 **Genes** = declarative manifest packs, not OOP inheritance (`GTS-13C` §3.6). In this programme:

| Gene (artifact kind) | Instance today | Experimental axis |
|---|---|---|
| `system_prompt` | `vg-code-default/system-prompt.txt` (one line) vs `vg-shell-only/system-prompt.txt` | Prompt DNA |
| `tool_schema` | read / search / patch / test vs shell-only | Tool surface |
| `context_policy` | `recency-window`, `maxItems: 64` | Context DNA |
| `routing_policy` | pack JSON | Model routing (must not silently change `K_compat`) |
| `budget_policy` | tokens/wall/effects/depth=`1` | Horizon DNA |
| `HarnessManifest` | `vg-code-default`, `vg-shell-only` (undeletable) | Pack identity; `composition_digest` frozen per episode |

Kinds `skill`, `playbook`, `operator`, `competence_claim` are **registered** in `agency/manifests/kinds.json` and **uninhabited**. Comparing empty kinds is theatre. SOTA DNA work is: freeze the two packs that exist, measure them, then add reconstruction packs as **data** (`T7.6`).

---

## 2. What “SOTA harness” means in 2026 (and what it must not mean)

### 2.1 Field SOTA (external, contaminated, deferred)

Industrial coding agents (Claude Code, Codex, Cursor, OpenCode, mini-SWE-agent) compete on **product loop quality**: tools, permissions, context, UX. Research agents compete on **SWE-bench / Terminal-Bench / internal suites**. Both are real. Neither is currently a legal publication target for this tree (`DEF-08`): a public score before an A/A floor is the premature-measurement error `VG-07` exists to prevent.

Further: public benches are in pretraining corpora. A pass on “merge intervals” or “slugify” can be retrieval, not agency. Isolated **private** tasks are therefore not a nicety; they are the only way a small lab gets a signal that is not Wikipedia.

### 2.2 Instrument SOTA (internal, the actual product thesis)

The unique SOTA this repo can reach **before** it can beat Claude Code on SWE-bench:

1. **Attribution SOTA** — separable arms under `M-18` (compatibility key equal; exactly one declared treatment).
2. **Integrity SOTA** — CL-1 exterior judge; CL-2 disjoint promote/optimise sets; CL-3 A/A floor that can refuse degeneracy (`M-07`).
3. **Replay SOTA** — two cassette dialects kept distinct; `Recording` complete enough for **counterfactual** re-execution and later exact SFT (sagiha gap: tool-schema snapshot).
4. **Containment SOTA** — worker cannot read oracle; evaluator identity ≠ worker identity; `inconclusive ≠ fail ≠ pass`.
5. **Harness-builder SOTA** — a second pack (Claude-shaped / OpenCode-shaped / mini-SWE) expressed as manifests with **zero** `agency/episode` edits (`T7.6`, `ADR-0060`). If a reconstruction needs a kernel branch, the framework thesis is falsified, not “almost done.”

Pass rate on a toy cache is **not** on this list.

### 2.3 Loop-engineering levels (`VG-07` §2) — stop conflating them

| Level | What a “pass” means | Current honest state |
|---|---|---|
| L0 | Single completion | `run_focused.py`, `live_medium_high.json` (`def add`) |
| L1 | Tool loop | LAM gym (gold); Vanguard `execute_harness` (live, mostly fail) |
| L2 | Context / compaction | Compiler exists; no consolidation-loss experiment |
| L3 | Composition / playbooks | Depth-1 only; no independence groups (`D-02`) |
| L4 | Distillation / promotion | Explicitly after instrument (`O-01`) |
| L5 | Corpus / training | `DEF-09`; record now, train later |

Publishing an L0 ping as an L1 ceiling, or an L1 cassette as L4 competence, is how agent projects plateau (`VG-07` `M-01`).

---

## 3. Three measurement planes (never one spreadsheet)

```text
Plane A  FRAMEWORK     kernel + runtime + ports     CI, cassettes, must-fail
Plane B  HARNESS DNA   manifests / genes            paired vs vg-shell-only
Plane C  MODEL CEILING live models on frozen tasks  labelled live-*; budgeted
                 │
                 ▼
         Recording + lam.sqlite + EvidenceClaim
         (opt-in projection to SFT/DPO in Phase 3)
```

**A number without a plane and an evidence label is unpublished.** Required labels (extend S7 §0.4):

| Label | Meaning | May support |
|---|---|---|
| `unit` / `property` / `must-fail` | CI | Framework correctness |
| `lam-replay` | Gold trajectory player | Gym still matches cassette |
| `cassette-vanguard` | `CassettePlayer` on `ModelPort` dialect | Loop still matches recorded **proposal** |
| `single-shot-complete` | `generate()` / one chat completion | Model can emit code from a spec |
| `chat-patch-loop` | Host extracts markdown and overwrites files | Model can repair when handed tests+tracebacks |
| `lab-execute-harness` | `Runtime.execute_harness` + lab departures | Production loop with live model |
| `product-cli` | `vg run` → daemon → same loop | Q2 dogfood |
| `sealed-evaluator` | UID 10002, digest-verified oracle mount | Publication-grade verdict |
| `aa-floor` / `paired-holdout` | T8 protocol | Any **lift** claim |

Cross-plane comparisons are refused (`M-18`). LAM-replay of `vg-code-default` vs live `vg-shell-only` is the degenerate A/A `D-06` already forbids.

---

## 4. Forensic audit: where the numbers come from

### 4.1 Taxonomy of leakage (operational definition of “cheating”)

A run **cheats** if any of the following hold and the result is labelled as agentic competence:

| ID | Defect | Why it invalidates |
|---|---|---|
| C1 | Gold tool trace replayed | Outcome is determined before the “model” thinks |
| C2 | Solution in prompt, comments, or README copied into workspace | The answer is an observation |
| C3 | Hidden oracle visible to worker | Judge is not exterior (`CL-1`) |
| C4 | Public tests are the only oracle and encode the algorithm | Holdout is empty; hardcoding expected values works |
| C5 | Host-side apply (regex extract, write file) bypasses kernel | Measured “harness” is a Python script |
| C6 | Pass heuristic is `calls > 1` or string `"passed"` in tool output | Gym marks success without pytest exit 0 |
| C7 | Instrument error counted as task fail or task pass | `inconclusive` laundering (`T5.6`) |
| C8 | Human edited source | Not Q2 |
| C9 | Approval auto-signed but labelled product unsupervised | Lab departure undeclared |
| C10 | Compatibility key differs on undeclared axis | Incomparable (`M-18`) |
| C11 | Same instances used to tune prompts and to claim lift | `CL-2` |
| C12 | Classic textbook task without private holdout | Pretraining contamination unmeasured |

### 4.2 Confirmed C-defects in this tree

**C1 + C6 — LAM gym pass is not a model pass.**

`tools/002_LLM_API_MOCK/simulate.py` currently:

```text
has_passed = (any "passed" in tool content)  OR  (calls > 1)
```

Any multi-turn gold replay is therefore `passed=true` even if pytest never returned 0. `FIT.md` and `runs/ladder_free.json` show `lam/*` 36/36 in ~milliseconds. That is a **player test**. The S7 master plan already named remaining `passed` stubs as a **blocker for every number in FIT.md**. Until C6 is dead, `lam.sqlite` pass columns are not KPIs.

`scenarios/generate_corpus.py` header: *“30 guaranteed 100% valid JSON gold scenarios.”* Turns contain the exact `target`/`replacement` patch. Intelligence lives in the JSON, not in a model.

**C1 mislabelled as live — KPI markdown.**

`tools/002_LLM_API_MOCK/docs/LAM_logs_benchmarking_KPIS_dont_commit.md` reports 75–100% **“Live Pass Rate”** on Raft, LSM-trees, bytecode VMs, with `$0.001704` spend. That cannot be reconciled with:

- `zero_hint_v1` live `llama3.2:3b` abandoned at 16 turns, 13× `fs.read`, zero successful `patch.apply`;
- `live_medium_high.json` probing `def add(a,b): return a+b`;
- GTS-13C / VG-07 sample-size doctrine (hundreds of pairs for a 5-point effect).

**Ruling:** treat that KPI file as **non-evidence**. Do not commit it. Do not cite it in README. Analyzer reports that aggregate `traces.passed` inherit C6 until the heuristic is pytest-exit-based and `backend` is a required filter.

**C2 + C5 — “zero-hint live LLM challenge.”**

`benchmarkings/live_llm_zero_hint_challenge/run_live_zero_hint.py`:

- Source comments: `Bug 1`, `Bug 2`, `Bug 3`, plus the eviction policy in comments.
- User message pastes **entire** `cache.py`, **entire** `test_cache.py`, and unittest stderr.
- Apply path: extract largest ```python``` block and overwrite the file.
- Verdict JSON claims autonomous Vanguard harness success (`passed: true`, `deepseek/deepseek-chat`).

This is L0/L1-hybrid **chat repair**. It does not import `Runtime.execute_harness`. Persona “expert autonomous software engineer” is not `vg-code-default` DNA.

`benchmarkings/run_live_proof.py` is the same family: injects pytest stdout, asks for a full file, labels `"prompt_leaks": "NONE"`.

**C5 — `tasks_phase2_LAM/test001/run_focused.py`.**

`OpenRouterProvider.generate` / `OllamaProvider.generate` with fully specified `remove_duplicates` and `topological_sort`. No tools. No workspace isolation. Measures completion.

**C4 — weak oracles.**

`vanguard/packages/adapters/evaluators/suites/bug-001-single-file/test_oracle.py` asserts `"(A + B) * B"` **in source text**. A comment satisfies the judge. That is not mechanically reproducible competence (`VG-06` evaluator class `mechanically_reproducible` is being impersonated by a string search).

**C3 — mostly avoided on the honest path.**

`zero_hint_v1/run_live_agent.py` copies only `fixture/initial` into the episode workspace; oracle is copied into a **post-episode** eval tree. This is the correct CL-1 shape for a lab (still not UID 10002). Public tests **are** visible, which is SWE-bench-like and acceptable **if** hidden oracle is the promotion metric and public-only green is labelled `public_overfit`.

**C9 — declared, therefore not cheat if labelled.**

`zero_hint_v1` `result.json` `labDepartures` include auto-approve, skip isolated evaluator, injected tool JSON schemas, raised `maxTokens`, first-tool-call wire filter. `Runtime.execute_harness(..., interactive=False)` is `Mode.BENCHMARK` and **fails closed** on privileged approval (`K-17`). Auto-approve is a lab privilege, not the product. Keep the field; never drop it from publications.

**C10 — `live_medium_high.json`.**

Six paid-looking model ids returning `def add`. Compatibility key is “canary wire ping,” not “tier ceiling.” Canaries must assert **wire shape, never task outcome** (`VG-01` §4.1). Using them as FIT ceilings is C10.

### 4.3 What is already scientifically usable

| Asset | Plane | Use |
|---|---|---|
| Kernel dispatch, attenuation, Bubblewrap worker, L1–L5 compiler | A | CI + must-fail |
| `CassettePlayer` vs LAM dual store | A | Keep split (`D-01`) |
| `vg-shell-only` undeletable | B | Legal control arm (`L-15`, `D-06`) |
| `vg-code-default` four typed tools | B | Treatment arm |
| `zero_hint_v1` T1–T3 tasks + hidden oracles + preregistration hashes | C | First private ladder |
| `tools/telemetry/tuple.py` | A/B/C | `M-18` implementation exists; **not wired** into live runners |
| `LamStore` schema (scenarios, traces, episodes, ceilings, budget_events) | data | Right **tables**; wrong **semantics** until C6/labels |
| `Recording` wire schema | data | Incomplete for SFT (missing compiler/tool/manifest digests) |
| `EvidenceClaim` schema | data | Publication object; unused by bench runners |
| Sprint 6B `preregistered_oracles.json` | C | Status `preregistered-not-run`; development copies, not sealed mounts |

### 4.4 Product-path gap (CLI)

`vanguard/clients/cli` is a protocol shell (`MockRuntime`, feed mode). Audits show `vg run --headless` can exit 0 with no events. **Plane C via CLI is closed** until RuntimeService exists and feed mode cannot be the default. Until then, the coding instrument is Python `execute_harness`, labelled lab.

---

## 5. Isolated evaluation protocol (the model must not know the answer)

### 5.1 Physical isolation

```text
host lab process
  ├─ compose(manifest) → FrozenHarness.composition_digest
  ├─ copy fixture/initial → temp git worktree   (source + PUBLIC tests only)
  ├─ brief string (no algorithm, no gold patch, no “Bug N”)
  ├─ worker (bwrap): /workspace  +  dummy sealed bundle (unreadable oracle)
  │     observe → propose → authorize → effect → receipt
  └─ AFTER terminal event: evaluator identity copies workspace + sealed oracle
        public_cmd  →  public_after
        oracle_cmd  →  oracle_after
```

Invariants:

- Worker `PYTHONPATH` must not include Aether-D-System (task code must not import Vanguard).
- Oracle, `preregistration.json`, README, `runs/`, gold patches, `datalog_solution.py` never land in `/workspace`.
- Leak linter (CI, $0): workspace snapshot grep for `oracle`, `FIXME`, `Bug [0-9]`, `gold`, `expected implementation`.
- Event audit: sanitized events contain no oracle paths.

### 5.2 Information isolation

| Channel | Allowed | Forbidden |
|---|---|---|
| Brief | “Inspect the repo; make public tests pass; change only listed paths.” | Algorithm, fencepost explanation, one-line patch |
| Public tests | Behavioural examples | Hidden cases; “the bug is `>=` vs `>`” in comments |
| Tool receipts | Public-test stdout/stderr (the agent using tests) | Hidden-oracle traceback in the next user turn |
| System prompt | Frozen pack DNA | Competitor persona hardcoded in LAM `simulate.py` (“You are OpenCode”) when claiming Vanguard DNA |
| Human | Prompt, approve/reject, CorrectionRecord | Source edits (Q2) |

**Public tests are not cheating** if they specify required behaviour and a disjoint oracle exists. They **are** cheating if they are the only judge (C4) or if the prompt restates the oracle (C2). `zero_hint_v1` prompts currently describe invariants in English (closed intervals, abutting ends, integer cents). That is closer to a spec-from-tests task than to a mystery bug. For **contamination-resistant** T4, prefer: broken code + failing public tests **without** a prose restatement of the invariant; let the model read tests.

### 5.3 Outcome algebra (fail-closed)

| Outcome | Condition |
|---|---|
| `pass` | `oracle_after.exit == 0` AND `public_after.exit == 0` AND no instrument error AND allowed paths only |
| `public_overfit` | public green, oracle red |
| `fail` | oracle red, episode completed, no instrument error |
| `abandoned` | turn/token/wall bound |
| `inconclusive` | provider/sandbox/evaluator/transport failure |
| `invalid` | leak linter fail, human source edit, oracle visible |

`pass` is the only promotion bit. `public_overfit` is a **harness-hacking** signal (H7 in GTS concepts): the agent optimized the visible tests.

### 5.4 Clean-environment operator recipe (after integrity gates, not now)

From repo root, WSL, Bubblewrap present:

1. `python3 benchmarkings/zero_hint_v1/run_live_agent.py --check-fixtures`  
   Gold (held by lab, never in worker) must turn oracle red→green. If gold is missing, do not run live.
2. One local model, one task, short bound:  
   `... --task test004_busy_merge --model ollama/<tag> --max-turns 8`
3. Read `runs/<utc>/result.json`: `lamReplay`, `singleShotGenerate`, `labDepartures`, `terminal`, tool verbs, `oracleAfter.passed`.
4. Refuse to escalate OpenRouter if `patch.apply` never appears (calibration fail).

Do not use `run_live_zero_hint.py` or `run_focused.py` for Plane C.

---

## 6. Private corpus design (isolated tests we own)

### 6.1 Splits (`VG-07` `M-19`)

| Split | Instances | Access | Role |
|---|---|---|---|
| `DEV` | LAM gold t1–t3 family; dogfood bug-001..003 **after oracle repair** | Unrestricted | Gym, prompt debug, C6 tests |
| `HOLDOUT` | `zero_hint_v1` test002, test003, test004 | Read at comparison time | Plane C ceiling; DNA paired trials |
| `SEALED` | One new private task authored after freeze, **not** in git history of prompts if possible; oracles off-tree or encrypted | Touch ledger; depleting | Publication / later training check |
| `LIVE` | Real incoming bugs (Q2 dogfood) | Operator | Verifier–deployment gap (`T8.7`) |
| `DEPLOYMENT` | Accepted user work | After ship | Correlation with HOLDOUT |

Contamination is one-way (`M-19`). Using HOLDOUT to tune `system-prompt.txt` **burns** it to DEV forever. LAM gold used to improve LAM **must not** be the holdout used to claim Vanguard lift (`CL-2`).

`M-20`: corpus membership checkable per instance before any `DEF-09` training. Schema: `instance_id → {split, first_touch, entered_sft: bool}`.

### 6.2 Tier model (small, powered, honest)

Under $0.50 you cannot power McNemar. Tiers are **calibration rungs**, not a significance theatre.

| Tier | n (now) | Shape | Pass criterion | Budget |
|---|---|---|---|---|
| T0 | CI | Framework mechanics | Tools, grants, bwrap, leak linter | $0 |
| T1 | 1 (`test004_busy_merge`) | One-file fencepost | Hidden oracle | Ollama then 1 free OR call |
| T2 | 2 (`test002`, `test003`) | Invariant (window / cents) | Hidden oracle | Only if T1 calibration patches |
| T3 | 3 dogfood classes | Multi-file / test-reaction | Sealed oracle, **not** substring | After T2; still local-first |
| T4 | 1 sealed | Private, non-textbook | Oracle | **Do not run on $0.50** unless T1–T2 green and budget remains |
| T5+ | frontier datalog, Raft, LSM | Greenfield engines | — | **Forbidden on this budget.** `frontier_tier5_datalog_engine/` contains `datalog_solution.py` in-tree (C2 if copied). Full specs are textbooks (C12). |

Authoring law: humans may know gold; the **episode process** never sees it. Gold is only for `--check-fixtures` and for later SFT **if** the instance is `DEV` and `entered_sft` is opted in.

### 6.3 Anti-hardcode oracles (`T8.6` lite)

Replace string-in-source oracles with:

- property / metamorphic (e.g. merge is idempotent, coverage of integers preserved);
- extra numeric cases not in public tests;
- mutation: a known-wrong patch must fail the oracle (must-fail gate).

This is how bug-001 becomes a real judge.

---

## 7. Framework vs DNA vs model — how we know each works

### 7.1 Plane A — framework (harness builder)

**Hypothesis:** the lattice implements one loop and can host another pack without core edits.

**Tests (all $0):**

1. Import direction / `test/broken/` (already).
2. `CassettePlayer` byte-stable on recorded proposals.
3. LAM gym after C6 fix: gold trajectory ⇒ pytest 0; mutated gold ⇒ fail.
4. Composition fail-closed: unknown verb, missing bwrap, unknown tool name.
5. Worker cannot read dummy sealed bundle (containment probe; `T5.2` lite).
6. `T7.6` mechanics: a **third** manifest that only changes prompt+aliases must `compose()` without `episode/engine.py` edits. If it cannot, stop and write a finding — do not add `if harness == "claude"`.

**SOTA framework milestone:** three reconstruction packs as data (`vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-code-swe-mini`) + `vg harness diff` showing only artifact deltas (`T7.5`). CLI `vg harness *` does not exist yet; a **lab** entrypoint calling `Runtime.compose` is allowed if labelled `lab` (S7 §3.1).

### 7.2 Plane B — harness DNA (genes)

**Hypothesis:** typed tools + code prompt beat `vg-shell-only` on HOLDOUT at equal model, sampling, budget, and approval policy (`M-12`–`M-15`).

**Protocol:**

- Same `K_compat` (model fingerprint, sampling, harness commit, evaluator digest, runner version).
- `D_treatment` = `manifest ∈ {vg-shell-only, vg-code-default}`.
- Both arms receive the **same brief** (`M-15` — historically the silent killer).
- Equal expressive power for the *change mechanism*: if one arm cannot create files the other can, you measured the effector, not the DNA (`M-12`).
- McNemar exact on discordant pairs **when n is large enough**. At n=3 this is a **case study**, not a published lift (`M-07`, `M-28`).
- Instrument-error rates reported per arm (`M-16`).

**Precondition:** at least one live model that can `patch.apply` (or shell-write under shell-only). Today’s 3B read-loop does not license DNA ranking. Ranking two packs that both fail identically is CL-3 degeneracy.

**Ablations once calibration exists (one variable each, `VG-07` §5.8):**

| Experiment | Treatment |
|---|---|
| E1 | typed tools vs shell-only |
| E2 | current one-line system prompt vs a longer frozen prompt (hash the template) |
| E3 | `maxTokens` 256 vs 2048 (today’s lab departure — measure it; do not hide it in the adapter) |
| E4 | tool JSON schema present vs pack-omitted (explains why injection exists) |
| E5 | later: `repo.tree` observation on/off vs shell `find` (`D-14`) |

Family declared **before** arms run (`M-06`). Holm–Bonferroni on the family. Optional stopping forbidden.

### 7.3 Plane C — model ceiling

**Hypothesis:** bands (LAM / Ollama light / Ollama heavy / OpenRouter free / paid) have different **tool-use ceilings** on HOLDOUT under **one frozen pack**.

Rules:

- Escalate only on T_k pass (`FIT.md` escalation invariant is correct; FIT **assignments** of live ceilings are not measured).
- `models.json` `top` must be empty until Project Lead names three ids (`D-13`). Current populated top/high lists are a process defect if used as measured FIT.
- Canary ≠ ceiling.
- Local Ollama is the default spend. Cloud is a scarce instrument.

---

## 8. LAM: improve with data, without becoming a fake brain

### 8.1 Law

LAM is **stateless** `next_turn = f(messages)` over a gold tape (`D-01`). Improving LAM means:

- more **validated** gold traces;
- stricter schema;
- honest `passed`;
- verb bridge to Vanguard **without** teaching the kernel `view_file`.

It does **not** mean sampling clever answers (`docs/superpowers/plans/2026-08-16-lam-benchmark-corpus.md`). A stochastic LAM destroys the gym.

### 8.2 Dual cassette (keep forever until byte-identical)

| Store | Dialect | Proves |
|---|---|---|
| LAM `scenarios/*.json` | OpenAI `tool_calls` + atoms `view_file` / `edit_file` / `run_command` / `grep_file` / `list_dir` | Gym + model-ceiling traces |
| Vanguard `CassettePlayer` | `ModelPort.propose` → `{text, toolCalls}` or episode `{kind,action,...}` | Loop dialect |

`vanguard_bridge.py` name-maps only. Lossy translation ⇒ do not ship `LamOperator` as ModelPort (S7 target architecture). Record **both** when a live Vanguard episode succeeds: (1) OpenAI-shaped LAM scenario for gym; (2) ModelPort cassette for CI.

Schema debt: `schema.py` requires `^t[1-5]-` while the tree contains `t0-*` and `t6-*`. That is a corpus/validator split. Freeze one regex; generate the other family under a second schema, or extend with an explicit `t0`/`t6` waiver artifact.

### 8.3 Recording live traces into LAM (the data flywheel)

`record.py` `trace_to_scenario` is the right **shape** (sanitize secrets, validate atoms). It is not yet the Vanguard episode recorder.

**Required provenance on every imported trace:**

```text
backend: lam-replay | live-ollama | live-openrouter-free | live-paid | vanguard-lab | vanguard-cli
passed: pytest_exit_0 ∧ oracle_exit_0   # never calls>1
split: DEV | HOLDOUT | SEALED | ...
opt_in_sft: false                        # default; MEM-7
tool_schema_digest
context_compiler_digest
manifest_digest
composition_digest
model_fingerprint
lab_departures[]
```

Import policy:

- Failed live episodes **are** valuable (dead-end claims, `MEM-3`) but `passed=0` and no authority.
- Only `DEV` traces may later enter SFT.
- HOLDOUT traces may be stored for measurement replay, **never** as gold that the gym “passes.”
- Chat-patch-loop traces may be imported as `backend=chat-patch-loop` for ablation (“does host-apply inflate pass rate?”), never as Vanguard gold.

### 8.4 Prompt DNA in the gym

`simulate.py` hardcodes “You are OpenCode.” That **confounds** Plane B (you cannot claim `vg-code-default` DNA while the gym uses a competitor persona). Scenario or harness-id must select the system prompt; default for Vanguard CI = pack file bytes hashed into `K_compat`.

---

## 9. Recording, metadata, KPIs, and later finetuning

### 9.1 Why record now if `DEF-09` forbids training

`VG-07` §10: deferring **capability** is correct; deferring **contracts** makes the retrofit a corpus migration. Sagiha’s SFT exporter already documented the fatal gap: approximate messages without a **tools snapshot**. V5 review: every `Recording` needs `toolSchemaDigest` + `contextCompilerDigest` + `manifestDigest` or “200 years of traces are sludge.”

This programme therefore **extends Recording in the spec** (implementation later) and **fills `lam.sqlite` / JSONL with honest rows now**.

### 9.2 Instrument tuple (already coded, unused)

`tools/telemetry/tuple.py` implements `M-18`:

- `K_compat`: benchmark_id, split_hash, model fingerprint, sampling, harness commit, agent hash, evaluator image digest, containment digest, substrate, runner, schema version
- `D_treatment`: manifest + declared axes
- `S_strat`: tier, language, …
- `M_meta`: timestamp, run id (excluded from equality)

**Gate:** any lift computation without tuple equality **refuses**. Live runners must emit this object into `result.json`. Defaults like `harness_commit: "v0.5.0"` and `evaluator_image_digest: "sha256:evaluator_default"` are **lies** if left as placeholders on a published row. Fail closed if digests are dummy.

### 9.3 KPI ontology (what to store; what not to “optimise”)

**Primary (pre-register one):** `oracle_pass` (binary).

**Secondary (always recorded, never silently promoted to primary):**

| KPI | Unit | Notes |
|---|---|---|
| `public_pass` | binary | For `public_overfit` |
| `turns` / `llm_calls` | count | Bound in budget_policy |
| `prompt_tokens` / `completion_tokens` | int | Provider usage; unknown ⇒ `pricing_known=false` |
| `usd_micros` | int | Integer currency (`S6B-MD-009`); never float dollars as truth |
| `wall_ms` | int | |
| `ttft_ms` / `ttfe_ms` | int | First token / first effect (`T6.8`) |
| `tool_histogram` | map verb→n | Detect read-loops |
| `patch_applied` | binary | Calibration bit |
| `instrument_error` | binary + reason | Excluded from McNemar (`M-16`) |
| `lab_departures` | string[] | Required |
| `evidence_label` | enum | §3 |
| `prefix_cache_hit_ratio` | optional | L1–L3 stability; do not invent 78.4% without measurement |
| `approval_count` | int | Human contribution to outcome |
| `depth` | 1 | Until T4.7 |

**Forbidden as unpublished “insights”:** token-reuse 78.4%, “lower-tier models pass Tier 3–4 thanks to the harness,” Pareto routing tables derived from C6 passes (`LAM_LAR_Vanguard_Master_Guide.md` §1). Those are hypotheses for **powered** experiments after calibration.

**Biological depth** in `lam.sqlite` (`episodes.depth_label`) may log Atom→… as **telemetry**, never as a class hierarchy. Do not require depth 9 to “unlock” a bench.

### 9.4 Proposed row contract (logical; implement later)

One JSONL object per episode, plus SQLite projection:

```text
EpisodeRecord
  identity:     run_id, episode_id, parent_id, task_id, split, instance_digest
  tuple:        K_compat, D_treatment, S_strat, M_meta
  harness:      manifest_id, composition_digest, gene_digests{kind→sha256}
  model:        requested, resolved, sampling, provider
  budget:       leases, remaining, usd_micros, tokens
  trajectory:   events[] (already ledger) + messages_digest (exact bytes model saw)
  tools:        schema_digest, calls[] {verb, descriptor_digest, receipt}
  evaluation:   public, oracle, evaluator_class, image_digest, double_probe
  outcome:      algebra §5.3
  provenance:   evidence_label, lab_departures, opt_in_sft, secret_redaction
  recording:    Recording{ modelCassetteDigest, imageDigest, envSnapshotDigest,
                           seed, clockPolicy, toolSchemaDigest, contextCompilerDigest,
                           manifestDigest }   # last three: V5-A extension proposal
```

`EvidenceClaim` is emitted **only** for `pass` or registered negative results intended for the graph; it is not a dump of every abandoned 3B loop.

### 9.5 Finetuning later (Phase 3, not now)

When `DEF-09` reverses (adversarial verifier audit + per-instance membership):

| Dataset | Source | Use |
|---|---|---|
| SFT-success | `DEV` ∧ `pass` ∧ `opt_in_sft` ∧ exact messages + tool schemas | Imitate tool sequences that **oracle-passed** |
| SFT-recovery | `DEV` ∧ fail then pass within episode | Repair trajectories |
| DPO pairs | Discordant paired DNA or model arms on **DEV** | Preference for the winning arm’s **process**, not HOLDOUT labels |
| Process rewards | Step-level receipts (`VG-07` §10) | Only after contracts exist; do not retrofit from slogans |
| Negatives | `public_overfit`, read-loops, hardcoded comments | Contrastive: do not imitate |

**Never:** train on HOLDOUT/SEALED; train on LAM gold that contains the patch in the tape (that is teaching the answer); train on chat-patch-loop host-apply as if it were kernel-mediated; always-on full-content capture (`REJ-12`).

Student models (3B/7B) are a **downstream** experiment: does SFT on **Vanguard-dialect** tools raise `patch_applied` on DEV? Transfer to HOLDOUT is the only claim that matters (control D in `VG-07` §8).

---

## 10. Budget protocol ($0.50 / ~1M output tokens)

### 10.1 Accounting truth

`budget.py` currently:

- allows **all** `band=free` calls without reading remaining USD;
- deducts **$0.05 per 10 calls** into a markdown ledger — a convention, not provider cost;
- does not stop a looping 16-turn Ollama episode (local is free in USD, not in wall-clock).

OpenRouter “free” is not always $0 (rate limits, some ids 404 — already observed for `google/gemini-2.0-flash-001`). Treat free as **unknown pricing** until `pricing_known=true` on the receipt.

**Hard stop (policy):** remaining_usd ≤ 0 ⇒ no `live-paid` and no `live-openrouter-*` except a Project-Lead waiver recorded as an artifact. Ollama unbounded in USD but **bounded in turns** (calibration: 8, not 16, until `patch.apply` exists).

### 10.2 Spend order (Approach: calibration first)

| Step | Spend | Stop if |
|---|---|---|
| 0 Relabel artefacts | $0 | — |
| 1 C6 fix + leak linter + `--check-fixtures` (when coding starts) | $0 | fixtures lie |
| 2 Ollama 3B T1, max-turns 8 | $0 | (expect fail; record tool histogram) |
| 3 Ollama heavy T1, max-turns 8, timeout ≥ provider | $0 | no `patch.apply` after 2 models → **harness/tool-schema problem**, do not buy cloud |
| 4 One OpenRouter free id, T1 only, max-turns 8, max completion 2k/turn | ≤ few cents | T1 fail or HTTP errors |
| 5 Same id T2 if T1 `pass` | remaining | — |
| 6 DNA A/B | only if a model can patch | n=1 case study |
| 7 Paid id | only leftover | T5+ forbidden |
| 8 CLI product path | $0 until daemon | — |

This matches remaining ~$0.498 in the unofficial ledger **if that ledger is even true**. Re-read provider usage from API, not from FIT.md.

**Do not** sweep `models.json` bands. Each extra id is a family hypothesis (`M-05`) you cannot power.

---

## 11. Scientific methodology (how the lab refuses to kid itself)

### 11.1 Pre-registration

Before any live cloud episode intended for a claim:

1. Hash: task set, split, manifest bytes, prompt bytes, sampling, max-turns, primary KPI, stopping rule, family.
2. Store under `benchmarkings/<suite>/preregistration.json` (already begun) **and** a family artifact for multi-hypothesis work (`M-06`).
3. `zero_hint_v1` files still say `preregistered_not_executed` while `runs/` exist — **status drift**. Status must update to `executed-lab` with run ids, or the preregistration is decorative.

### 11.2 Statistics (honesty at small n)

`VG-07` `M-03`/`M-04`: McNemar exact, both discordant counts, effect size, CI. At n∈{1,2,3}:

- Report **case studies** with full traces.
- Do not compute p-values.
- Do not size “5-point harness lift.”
- `M-28`: underpowered experiments are deferred, not run “just to have a number.”

When n grows: A/A on **live** config (`M-07` refuse 0%/100% floors); paired bootstrap for cost/latency; survival for timeouts (`T8.3`). McNemar alone is not a statistics strategy (Claude review of VG-07, GTS-13C T8.3).

### 11.3 Must-fail and sabotage (`T8.8`)

The instrument must be shown able to fail:

- Gold patch removed ⇒ oracle red.
- Oracle mounted into workspace ⇒ leak linter red (or evaluator `inconclusive`).
- String-oracle comment patch ⇒ must **fail** once oracles are properties.
- Auto-approve off in BENCHMARK ⇒ privileged patch does not apply (`K-17`).
- LAM mutated tape ⇒ gym fail after C6 fix.

A gate never proven to fail is not a gate (`VG-01`).

### 11.4 Experiment registry (`M-25`–`M-28`)

Scarce resources: USD, GPU hours, human approval time, **sealed touches**. Registry columns: hypothesis, plane, split consumed, derived n, committed USD, owner, status. Human adjudication is budgeted (`M-27`).

---

## 12. Programme to actually reach SOTA (no code in this review)

Phased. Each phase has a falsifier. Later phases do not start if the falsifier fires.

### Phase P0 — Epistemic freeze (documentation / labels only)

- Stamp evidence labels on existing outputs (FIT, KPI md, LIVE_LLM_VERDICT, ladder_free, zero_hint runs).
- README SOTA sentence stays **aspirational**; do not add pass-rate badges from LAM.
- Decision: first honest ladder is `lab-execute-harness` until `product-cli` exists (recommended). Blocking all scoring on CLI completeness delays calibration of tool schemas — the live 3B evidence already shows the loop can search/read; it cannot patch. That is a **product** finding, not a CLI finding.

### Phase P1 — Integrity of the gym and the lab runner

- Kill C6 (`passed` ⇔ pytest 0, preferably oracle 0 when oracle exists).
- Leak linter; fixture gold check.
- Emit instrument tuple + evidence_label + lab_departures on every `result.json`.
- Stop writing “Live Pass Rate” from `backend=lam` traces.
- Repair bug-001 oracle (property, not substring).
- Align LAM system prompt with pack DNA when the gym claims Vanguard.

**Falsifier:** if `--check-fixtures` cannot fail then pass, HOLDOUT is unused.

### Phase P2 — Calibration (Plane C, local)

- T1 then T2 on light then heavy Ollama under `vg-code-default`.
- Success: `patch.apply` ≥ 1 and/or `pass`.
- Failure: diagnose **tool schema / depth-1 / maxTokens / translator dialect** (Beta audit: provider `{text,toolCalls}` vs episode `{kind,action,...}` was a P0). Cloud will not fix a dialect bug.

**Falsifier:** heavy local model + injected schemas still never patches ⇒ do not buy tokens; fix Plane A.

### Phase P3 — One free cloud id, same HOLDOUT

- Escalate only if P2 patches.
- Record LAM scenario **and** Vanguard cassette on any `pass`.
- Update model_ceilings only with `evidence_label=lab-execute-harness` and real usage.

### Phase P4 — DNA case study (Plane B)

- Same calibration model, `vg-shell-only` vs `vg-code-default`, n=HOLDOUT size.
- Publish as case study unless n supports McNemar.
- If shell-only wins, typed tools stay optional (`D-06` reversal is “do not default,” not “delete”).

### Phase P5 — Harness-builder SOTA (Plane A, S7 packets)

- Manifest-driven translator (`D-05`); pack-local aliases; no global competitor dict.
- `vg harness build|diff|bench` as lab CLI.
- Three reconstruction packs as data; depth-1 serialisation of parallel tools (`D-02`).
- `Recording` V5-A fields.

**Falsifier:** reconstruction requires `EpisodeEngine` change.

### Phase P6 — Instrument SOTA (T8)

- A/A runner that **refuses** degenerate floors.
- Paired runner + pre-registration hash.
- Sealed evaluator composition (UID 10002) so lab departure (2) can be retired.
- Meta-evaluator: HOLDOUT vs LIVE gap freezes promotion (`T8.7`).

**Falsifier:** cannot run A/A on a non-degenerate live config (all pass or all fail). Then you do not have a measurement lab; you have a toy.

### Phase P7 — Generality (T9) and competence (O-01)

- TableWorld through registries only.
- Distillation only after an artifact beats A/A and incumbent (`VG-07` §4).
- Training (`DEF-09`) only after P6.

### Phase P8 — External benches (`DEF-08` reversal)

- Only with A/A floor, sealed evaluator, contamination metadata, and a statement that public scores are **not** the promotion metric.
- Prefer private SEALED correlation with LIVE over SWE-bench rank.

---

## 13. Best path vs rejected paths

| Path | Verdict |
|---|---|
| Calibration-first isolated HOLDOUT + honest LAM gym + record-for-SFT | **Adopt** |
| Many-model L0 sweep (`run_focused`, add-function pings) | Reject as ceiling; keep as **canary** with wire-shape asserts |
| Chat-patch “zero-hint” challenges | Reject as Vanguard evidence; optional ablation dataset labelled `chat-patch-loop` |
| Build `vg harness bench` + three packs before any model can patch | Reject as first spend; adopt as P5 after P2 |
| Publish FIT.md live ceilings | Reject until measured under §5.3 |
| Train 3B now on LAM gold patches | Reject (`DEF-09`, C1, `MEM-7`) |
| Merge LAM and CassettePlayer | Reject (`D-01`) until byte-identical golden vectors |
| `proc.interactive` PTY | Reject (`D-03`) |
| Public SWE-bench as Phase 0 trophy | Reject (`DEF-08`) |

---

## 14. Threats to validity (what will still fool us)

1. **Pretraining contamination** of T1–T2 textbook bugs — mitigate with SEALED T4 and mutation oracles.
2. **Public-test overfitting** — `public_overfit` label; never feed oracle stderr to the model.
3. **Lab auto-approve** — human-in-the-loop product will have different pass rates (`M-12` expressive power / `K-17`).
4. **Depth-1 vs parallel tools** — reconstructions that “look like Claude” but serialise reads will underperform Claude’s scheduler; label honesty (`D-02`).
5. **maxTokens 256 vs 2048** — measuring DNA while injecting 2048 attributes lift to the adapter.
6. **Evaluator substring oracles** — comment hacks.
7. **SQLite as authority** — traces without `backend` filter.
8. **Small-n p-hacking** — `M-28`.
9. **Dialect mismatch** — tools that never become `EffectRequest` look like “dumb models.”
10. **Sealed-set burnout** — one peek for prompt tuning burns SEALED (`M-19`).
11. **README biological Level 9** — social pressure to skip P1–P6; `NC-01` still forbids AGI claims.

---

## 15. Falsifiers of the SOTA-instrument thesis

The programme is **wrong** (not merely unfinished) if:

1. No live model can `patch.apply` under `execute_harness` after dialect/schema/token defects are closed — then the loop is not an agentic coding harness.
2. A second environment (TableWorld) forces episode-engine or capability-algebra changes — generality (`C-10` / ADR-0060) is false.
3. Typed tools never beat `vg-shell-only` on HOLDOUT at equal budget after a non-degenerate A/A — the default pack is costume.
4. Promotion from LAM gold improves DEV and **not** HOLDOUT — cassette theatre.
5. Sealed evaluator cannot be composed and lab post-hoc unittest remains the judge at “publication” — CL-1 is policy, not architecture.
6. Exact message+tool-schema reconstruction is impossible from stored traces — later SFT poisons the corpus (sagiha m-7).

These are features. `VG-07` §8 transfer experiment is the long-horizon version of (4).

---

## 16. Recommendations (priority)

**P0 — stop the lying numbers (no model spend)**

1. Treat KPI “live pass rates,” FIT live ceilings, and `LIVE_LLM_VERDICT.json` as **non-results**.
2. Do not run further chat-patch or single-shot scripts under the name Vanguard.
3. Do not spend $0.50 until P2 calibration policy is agreed.

**P0 — integrity (when implementation is authorised)**

4. Fix LAM `passed` ⇔ tests.
5. Wire instrument tuple + evidence_label into `zero_hint_v1` results (fields already partly present).
6. Leak linter + fixture gold.
7. Repair string oracles.

**P1 — calibration**

8. Ollama light/heavy on T1 with short bounds; debug dialect if no patch.
9. One free OpenRouter id only after `patch.apply`.

**P2 — science apparatus**

10. Family pre-registration artifact; split ledger; Recording V5-A field list (schema ADR).
11. Manifest-driven tools so DNA A/B is possible.
12. Lab `harness diff/bench` against `vg-shell-only`.

**P3 — product**

13. RuntimeService + `vg run` that cannot succeed empty; then repeat T1 as `product-cli`.
14. Sealed evaluator in composition; retire lab departure (2).

**Explicitly later:** TableWorld, competence promotion, SFT, public benches, reconstruction cosmetics, frontier datalog.

---

## 17. File map (audit corpus)

| Path | Role in this review |
|---|---|
| `docs/main_v4/07_vanguard_loop_engineering_and_measurement_v040.md` | Measurement constitution |
| `docs/main_v4/01_vanguard_engineering_handbook_v040.md` | Mock/cassette/live |
| `docs/main_v4/06_vanguard_competence_memory_and_evidence_v040.md` | Claims, MEM-7 |
| `docs/main_v4/10_vanguard_deferred_and_rejected_register_v040.md` | DEF-08, DEF-09 |
| `docs/main_v4/13_C_gts_mvp_program_and_engineering_plan.md` | T6–T8, T1.11 |
| `docs/reviews/todo/vanguard_LAM_manifests_plan_sprint-7-to-9.md` | S7–S10 packets, D-01..D-15 |
| `docs/reviews/todo/vanguard_v042_and_v5_from_harness_src.md` | Exact SFT, no DAG |
| `docs/reviews/todo/mvp_beta_delivery_audit_2026-08-16.md` | NO-GO product path |
| `docs/reviews/todo/BETA-MVP-AUDIT-REPORT.md` | SOTA properties 1–8 |
| `benchmarkings/zero_hint_v1/` | Honest lab suite |
| `benchmarkings/live_llm_zero_hint_challenge/` | C2/C5 exhibit |
| `benchmarkings/run_live_proof.py` | C2/C5 exhibit |
| `benchmarkings/tasks_phase2_LAM/test001/run_focused.py` | L0 exhibit |
| `tools/002_LLM_API_MOCK/simulate.py` | C6 exhibit |
| `tools/002_LLM_API_MOCK/FIT.md` | Mislabelled ceilings |
| `tools/002_LLM_API_MOCK/docs/LAM_logs_benchmarking_KPIS_dont_commit.md` | Non-evidence |
| `tools/002_LLM_API_MOCK/runs/live_medium_high.json` | Canary, not ceiling |
| `tools/telemetry/tuple.py` | M-18 code |
| `schemas/v4/recording.schema.json` | Incomplete Recording |
| `vanguard/packages/agency/manifests/` | DNA instances |
| `vanguard/clients/cli/` | Not yet Plane C |
| `vanguard/packages/runtime/root.py` `execute_harness` | Lab product loop |

---

## 18. Closing

Vanguard already has a **more serious measurement constitution** than most agent codebases (`VG-07`). The failure mode in this tree is the usual one: **the constitution was not applied to the artefacts that look like results.**

SOTA for us is not a 100% matrix on generated gold JSON. It is:

- a gym that can fail;
- a lab loop that cannot see the oracle;
- a control pack that cannot be deleted;
- a tuple that refuses incomparable lifts;
- a corpus that can become SFT without eating the holdout;
- a framework that expresses the next harness as genes, not as a kernel fork.

Until a live model applies a patch under `execute_harness` on a hidden oracle, the scientific report is: **the instrument is partially built; the scores on the wall are mostly cassette and chat.** That sentence is progress. Inflating it is not.

**Next action (human):** approve P0 labelling and the calibration-first budget; then authorise implementation of P1 integrity (C6, linter, tuple emission) in a separate change. Do not run the $0.50 cloud ladder before that.

---

*End of review. No code was modified.*
