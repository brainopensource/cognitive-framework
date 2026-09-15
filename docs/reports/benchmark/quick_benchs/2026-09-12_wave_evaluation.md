# Executive Audit & Benchmark Evaluation: AETHER / Vanguard Substrate

**Date**: 2026-09-12  
**Branch**: `feat/aether-framework-electroweak-canonical-agents`  
**Subject HEAD (end of run)**: `1b97c66b4d5eb8b4f303a5e784a2ad6b37995404`  
**Dirty flag**: yes (untracked `.draft/quick_benchs/` evidence only; challenge sources were not mutated)  
**Control preregistration**: `UNFROZEN` — this report is engineering evidence, **not** an MS-CONTROL score  
**Harness under test**: `vg-code-balanced` via BaaC `ForgeFacade` + autofix-swe-loop proficiency  
**Local engine**: `llama-server` build 10796 (`9a4843cf2`) at `http://127.0.0.1:8080`, alias `local-model`  
**Local GGUF**: `Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf` (Q4_K_M, n_ctx=4096, n_params=1.54B)  
**Paid models**: `deepseek/deepseek-v4-flash-0731`, `z-ai/glm-5.3-flash` (OpenRouter)  
**Paid cap**: **$0.10 / 150 API calls**. Measured spend: **$0.004378** across **56 turn-slots**.

Card schema: [`CARD_TEMPLATE.md`](CARD_TEMPLATE.md). Raw JSON: [`evidence/`](evidence/).

This run **did not** mix LAM replay into live pass-rates. `openrouter/free` was not used as a published identity.

---

## 1. System Invariants & Level 0 Verification Gate

All architectural linters, bounded falsifiers, and LDA doctor were re-executed on this subject.

| Gate Dimension | Diagnostic Command | Result / Invariant Assertion | Status |
|---|---|---|---|
| Boundary Enforcer | `python3 tools/linters/check_boundaries.py` | 833 source files checked; hexagonal flow intact | **PASS** |
| TCB Budget Gate | `python3 tools/linters/check_tcb_budget.py` | **1386 LOC** / 9 files (threshold ≤ 1438, headroom +52) | **PASS** |
| Domain Blindness (I-7) | `python3 tools/linters/check_domain_blindness.py` | 0 AST / coding / pytest tokens in kernel and domain | **PASS** |
| Runtime Purity (N-06) | `python3 tools/linters/check_isolation_policy.py` | runtime remains declarative; proc.exec plugins declared | **PASS** |
| Secret Scanner | `python3 tools/linters/scan_secrets.py` | 0 blocking secret patterns (`.env` untracked, mode `0600`) | **PASS** |
| Code Duplication | `python3 tools/linters/check_duplication.py --enforce` | 0 forbidden duplicate surfaces | **PASS** |
| Markdown Links | `python3 tools/linters/check_markdown_links.py` | local relative links resolve | **PASS** |
| Documentation Paths | `python3 tools/linters/check_stale_paths.py` | 778 files scanned; 0 obsolete `docs/` layout tokens | **PASS** |
| Prompt Prefix (W12-A) | `python3 tools/agent_plugins/cli.py prefix` | **2180 / 4096** chars (headroom +1916). Stdout including banner = 2229 | **PASS** |
| Hermetic Test Runner | `python3 .agents/skills/test-runner/scripts/run_test.py` kernel dispatch | **29/29** in **0.154s**, timeout unused | **PASS** |
| Control Falsifiers | `unittest test.benchmarks.test_preregistration test_metric_veto test_control_corpus test_control_accounting` | **60/60** in **0.062s**; unfrozen control cannot be scored | **PASS** |
| LDA Graph Health | `uv run lda doctor --json` | `index_healthy: true`; 296 docs, 11,406 symbols, 91,526 relations | **PASS** with hygiene **WARN** |

LDA notes (not gate failures): 26 low-signal symbol paths (sampled), 13 duplicate document pairs, 1 authority conflict, 132 undocumented symbols. Indexed `freshness.head` during doctor was `4a24f2c9daa3`, which **does not match** the workspace HEAD at report time (`1b97c66b`). Indexes route; they do not override Git.

`.env`: present, mode `0600`, gitignored, key name present. Value was never printed or logged.

---

## 2. Master Challenge & Corpus Gate Check (Anti-Poisoning / Anti-Cheating)

Automated scan + baseline oracle execution over **37** challenges (`audit_corpus.py`). BaaC zero-state: `python3 -m benchmarks.baac.cli verify` → **9/9**.

| Suite | Count | Notes |
|---|---|---|
| BaaC | 9 | Tiers 1–6; SHA-256 `manifest.sha256` on every challenge |
| Benchmark 20 Suite | 20 | 10 brownfield + 10 greenfield |
| Greenfield | 8 | dogfood + qualification + one static webapp |

**Initial falsifier color (unmodified sources):**

| Color | Count | Meaning |
|---|---|---|
| RED | 33 | Genuine failing oracle — expected for a repair/synthesis task |
| GREEN | 2 | Baseline already passes — premature-green / toothless-oracle risk |
| TIMEOUT | 1 | Hang without runner timeout |
| NO_ORACLE | 1 | No in-tree executable test |

Poison scan: **trivial `assert True` = 0**. **Task-prose solution leaks = 0**.

### Key gate findings

1. **BaaC integrity (CLEAN).** All 9 challenges have verified zero-state manifests. Oracles live under `oracle/verify.py` and are not copied into the agent scratch tree. Baseline RED examples: calculator `8 != 15`; fib `None != 0`; dedupe `None != 'abcd'`.
2. **`05_token_budget_clamping_drift` — WARN (toothless oracle).** Intended defect: float `BudgetGovernor`. Oracle loops `reserve(0.00001)` then immediate `refund(0.00001)` × 1000. Symmetric IEEE-754 cancelation returns exactly `1.0`, so the **buggy float implementation is GREEN**. Gate: premature-green.
3. **`04_sqlite_wal_checkpoint_lock` — WARN (flaky / under-stressed).** Intended defect: missing `PRAGMA busy_timeout`. Oracle uses 2 threads (50 writes, 10 checkpoints). On this host the test is **GREEN** (0 errors) despite the missing timeout. Contention is not reliably produced.
4. **`dogfood-02-subprocess-timeout-censoring` — PASS as designed hang.** `process_items` has `while i < len(items):` with no `i += 1`. Corpus runner killed the process at **4.0s, exit 124**. Timeout protection is required; an unbounded unittest would hang.
5. **`greenfield-v0450-webapp` — STATIC.** No executable oracle in-tree.

These two GREEN rows **must not enter a live pass-rate denominator** as repaired successes.

---

## 3. Standardized Benchmark Evaluation Cards

Evidence labels are explicit. LAM 9/9 is protocol replay, not model skill.

### Benchmark 1: `bench_single_2K_tier-1_calculator`

- **Suite & Tier:** baac | Tier-1 single-file formula repair
- **Files in Challenge:** 6 (`TASK.md`, `challenge.yaml`, `manifest.sha256`, `src/__init__.py`, `src/calculator.py`, `oracle/verify.py`)
- **Gate Check:** **PASS (CLEAN)**. Zero trivial asserts, zero leaked oracle. SHA-256 zero-state OK.
- **Initial Falsifier:** **FAIL (RED)** — `AssertionError: 8 != 15` on `calculate_value(2, 3)` (`(A+B)+B` vs `(A+B)*B`)
- **Falsifier Command:** `python3 oracle/verify.py --workspace <scratch>`

#### 1a. LAM replay (`REPLAY`) — `vg-code-balanced` × `lam-mock`

- **Result Quality:** **PASS**. Attribution `PASS`. 6 turns, 1,140 tokens, **$0.00**, 0.09s.
- **False-Completion:** 0. This is cassette/mock protocol, **not** a quality score.

#### 1b. Local skill loop (`LIVE-LOCAL`) — autofix-swe-loop × Qwen2.5-Coder-1.5B

- **Result Quality:** **PASS (GREEN)** in **1 turn**. Formula corrected to `(A + B) * B`.
- **Caveat:** generated file also injected a `TestCase` class above the function (oracle still imported `calculate_value` and passed). Skill-loop quality ≠ clean patch hygiene.
- **Latency:** 1.630s total; turn 1.587s; LDA delta **0.238s**.
- **Tokens:** 96 completion | **60.5 tok/s** wall-clock.
- **Turn waste W:** 0 | False-completion: 0.0
- **Repo fidelity:** in-tree `calculator.py` left byte-identical (scratch-only).

#### 1c. Local Forge harness (`LIVE-LOCAL`) — `vg-code-balanced` × `local-model` on port 8080

- **Result Quality:** **UNDETERMINABLE**. Attribution **`HARNESS_ERROR`**.
- **Output:** `changedFiles: []`, empty diff. Oracle still `8 != 15`.
- **Latency:** 8.80s | 4 turns (cap 4)
- **Tokens:** prompt 7,401 + completion 1,455 = **8,856** | **165.3 completion tok/s** wall-clock
- **Interpretation:** the same 1.5B **can** fix the formula via free-form codegen (1b) but **did not land a patch** through Forge tool calling.

#### 1d. Paid Forge (`LIVE-HOSTED`) — DeepSeek V4 Flash

- **Result Quality:** **PASS**. Diff: `resultado = (A + B) * B`. Extra file `verify_fix.py` also written.
- **Turns:** 8 / 8 (Forge did not early-stop after a 1-line fix — **turn waste**)
- **Tokens:** 11,688 prompt + 1,284 completion = 12,972 | **52.3 tok/s** wall-clock
- **Cost:** **$0.000406** | 24.54s

#### 1e. Paid Forge (`LIVE-HOSTED`) — GLM-5.3-flash

- **Result Quality:** **PASS**. Same one-line formula fix. No extra `verify_fix.py`.
- **Tokens:** 10,216 + 1,083 = 11,299 | **52.2 tok/s**
- **Cost:** **$0.001099** | 20.73s

---

### Benchmark 2: `bench_single_2K_tier-1_string_dedupe`

- **Suite & Tier:** baac | Tier-1 adjacent-duplicate collapse
- **Files in Challenge:** 6
- **Gate Check:** **PASS (CLEAN)**
- **Initial Falsifier:** **FAIL (RED)** — `None != 'abcd'` (`pass` stub)

#### 2a. LAM `REPLAY`: PASS, 6 turns, $0.00, 0.10s  
#### 2b. Local autofix `LIVE-LOCAL`: **PASS**, 1 turn, 55 tokens, 1.488s, LDA delta 0.118s, **38.0 tok/s**  
#### 2c. Paid DeepSeek `LIVE-HOSTED`: **PASS**. Iterative `prev` scan. 11,175 + 1,051 = 12,226 tokens, 24.53s, **$0.000351**, 8/8 turns.

---

### Benchmark 3: `bench_single_2K_tier-1_fib_cli`

- **Suite & Tier:** baac | Tier-1 CLI + iterative Fibonacci
- **Gate Check:** **PASS (CLEAN)**
- **Initial Falsifier:** **FAIL (RED)** — `None != 0` on `fib(0)`

#### 3a. LAM `REPLAY`: PASS, $0.00, 0.09s  
#### 3b. Local autofix `LIVE-LOCAL`: **PASS**, 1 turn, 118 tokens, 1.757s, LDA delta 0.113s, **68.9 tok/s**  
#### 3c. Paid DeepSeek `LIVE-HOSTED`: **PASS**. Iterative `fib`, `--n` argparse, `ValueError` on `n < 0`. 11,142 + 1,109 = 12,251 tokens, 12.04s, **$0.000248**, 8/8 turns.

---

### Benchmark 4: `bench_multi_8K_tier-2_json_todo_store`

- **Suite & Tier:** baac | Tier-2 JSON store
- **Gate Check:** **PASS (CLEAN)**. Baseline class is `pass`.
- **Initial Falsifier:** **FAIL (RED)** — missing `TodoStore` API

#### 4a. LAM `REPLAY`: PASS (injected solution), $0.00 — **not** a quality score  
#### 4b. Paid DeepSeek `LIVE-HOSTED`: **UNDETERMINABLE / HARNESS_ERROR**. 8 turns, 11,861 + 1,781 = 13,642 tokens, **$0.000306**, **`changedFiles: []`**. Capable model spent tokens and wrote **nothing**.  
#### 4c. Paid GLM-5.3-flash `LIVE-HOSTED`: **FAIL / LLM_COGNITIVE_ERROR**. Did write `src/todo.py` (+ extra `verify_todo.py`). Oracle: `TypeError: unhashable type: 'dict'` — `add()` returned a dict; `complete(id1)` hashed that dict. 10,120 + 1,587 = 11,707 tokens, 33.62s, **$0.001698**.

Isolation: DeepSeek **no write** (harness/tool application). GLM **wrote wrong API** (model cognition). Harness **can** apply patches on this task; DeepSeek failed to emit an applied write.

---

### Benchmark 5: `bench_greenfield_8K_tier-2_quiz_game`

- **Suite & Tier:** baac | Tier-2 greenfield quiz engine
- **Gate Check:** **PASS (CLEAN)**
- **Initial Falsifier:** **FAIL (RED)** — missing `QuizEngine`
- **LAM `REPLAY`:** PASS, $0.00
- **Paid DeepSeek `LIVE-HOSTED`:** **UNDETERMINABLE / HARNESS_ERROR**. 8 turns, 12,421 tokens, **$0.000270**, **no files changed**. Same no-write signature as todo.

---

### Benchmark 6: `01_rate_limiter_lease_recovery`

- **Suite & Tier:** benchmark_20_suite | brownfield token conservation
- **Files:** 5 (`docs/SPEC.md`, `initial_state.sha256`, `src/governor.py`, `src/rate_limiter.py`, `test/test_limiter.py`)
- **Gate Check:** **PASS (CLEAN)**
- **Initial Falsifier:** **FAIL (RED)** via `PYTHONPATH=. python3 -m unittest test/test_limiter.py` (discover-on-`test/` is not importable without `__init__.py`)
- **Agent Mode:** gate/audit only this wave (no paid spend)
- **Tokens:** 0 | False-completion: 0.0

---

### Benchmark 7: `04_sqlite_wal_checkpoint_lock`

- **Suite & Tier:** benchmark_20_suite | brownfield concurrency
- **Gate Check:** **WARN (FLAKY / UNDER-STRESSED)**
- **Initial Falsifier:** **PASS (GREEN)** — missing `busy_timeout` not triggered
- **Agent Mode:** audit / inspect (0 tokens). Do not score as an agent win.

---

### Benchmark 8: `05_token_budget_clamping_drift`

- **Suite & Tier:** benchmark_20_suite | brownfield float drift
- **Gate Check:** **WARN (TOOTHLESS ORACLE)**
- **Initial Falsifier:** **PASS (GREEN)** on buggy float code (symmetric reserve/refund)
- **Agent Mode:** audit / inspect (0 tokens)

---

### Benchmark 9: `dogfood-02-subprocess-timeout-censoring`

- **Suite & Tier:** greenfield | designed infinite loop
- **Gate Check:** **PASS (ADVERSARIAL HANG)**
- **Initial Falsifier:** **TIMEOUT** — corpus runner **4.0s, exit 124**
- **Skill:** test-runner timeout protection is the product under test, not coding repair
- **Tokens:** 0 | False-completion: 0.0

---

### Benchmark 10: `lam_synthetic_replay_50`

- **Suite & Tier:** `tools/002_LLM_API_MOCK` | hermetic simulation
- **Gate Check:** **PASS (HERMETIC REPLAY)**
- **Result:** **50/50** successful responses, 0.64ms total, 0.012ms/call, **$0.00**
- **BaaC LAM cycle (same wave):** **9/9 PASS**, 10,260 tokens simulated, 0.83s, $0.00, zero-state clean after reset
- **Label:** `REPLAY` only

---

## 4. Aggregate Comparison Table

Live rows only below the replay separator. Do not average LAM with DeepSeek.

| Benchmark / Challenge | Stratum | Gate | Agent / Model | Pre → Post | Tok/s (wall) | Tokens | Latency | Cost | False-comp |
|---|---|---|---|---|---|---|---|---|---|
| calculator | single | PASS | LAM replay | RED → GREEN* | n/a | 1,140 | 0.09s | $0 | 0 |
| calculator | single | PASS | Autofix 1.5B | RED → GREEN | 60.5 | 96 | 1.63s | $0 | 0 |
| calculator | single | PASS | Forge 1.5B | RED → no-write | 165.3 | 8,856 | 8.80s | $0 | 0 |
| calculator | single | PASS | Forge DeepSeek | RED → GREEN | 52.3 | 12,972 | 24.54s | $0.000406 | 0 |
| calculator | single | PASS | Forge GLM-5.3 | RED → GREEN | 52.2 | 11,299 | 20.73s | $0.001099 | 0 |
| string_dedupe | single | PASS | Autofix 1.5B | RED → GREEN | 38.0 | 55 | 1.49s | $0 | 0 |
| string_dedupe | single | PASS | Forge DeepSeek | RED → GREEN | 42.8 | 12,226 | 24.53s | $0.000351 | 0 |
| fib_cli | single | PASS | Autofix 1.5B | RED → GREEN | 68.9 | 118 | 1.76s | $0 | 0 |
| fib_cli | single | PASS | Forge DeepSeek | RED → GREEN | 92.1 | 12,251 | 12.04s | $0.000248 | 0 |
| json_todo_store | multi | PASS | Forge DeepSeek | RED → no-write | 157.1 | 13,642 | 11.34s | $0.000306 | 0 |
| json_todo_store | multi | PASS | Forge GLM-5.3 | RED → FAIL (dict id) | 47.2 | 11,707 | 33.62s | $0.001698 | 0 |
| quiz_game | greenfield | PASS | Forge DeepSeek | RED → no-write | 109.8 | 12,421 | 9.84s | $0.000270 | 0 |
| 04 sqlite wal | brownfield | WARN | audit | GREEN (flaky) | n/a | 0 | 0.05s | $0 | 0 |
| 05 budget drift | brownfield | WARN | audit | GREEN (toothless) | n/a | 0 | 0.00s | $0 | 0 |
| dogfood-02 hang | greenfield | PASS | test-runner | HANG → TIMEOUT | n/a | 0 | 4.00s | $0 | 0 |
| lam_synthetic_50 | simulation | PASS | LAM | GREEN → GREEN | ≫1e6 eq. | 50 calls | 0.00064s | $0 | 0 |

\*LAM GREEN is mock-injected solutions.

**Paid envelope:** $0.004378 / $0.10 (4.4% of cap). Turn-slots 56 / 150. Remaining headroom $0.0956 and ~94 slots unused.

**Tiny completion probe (llama-server `/v1/chat/completions`):** prompt **1313.6 tok/s**, decode **116.6 tok/s**, `cache_n=5` / 36 prompt tokens.

---

## 5. Isolation: harness vs LLM (the point of the paid wave)

| Observation | What it isolates |
|---|---|
| Autofix 1.5B **solves** calculator/dedupe/fib in 1 turn | The **task is solvable** by a small local coder when the loop is free-form generate-and-replace |
| Forge 1.5B on calculator: 4 turns, **0 files changed**, `HARNESS_ERROR` | Tool-calling / patch application through `vg-code-balanced` **fails for this 1.5B**, not the math |
| Forge DeepSeek & GLM on calculator: **PASS**, correct one-line formula | The **same Forge path works** when the model emits valid write tools |
| Forge always reports **turns = max_turns (8)** even after a 1-line fix | Missing **early-stop** after oracle-green; turn waste `W` is structural, not DeepSeek being slow |
| DeepSeek extra `verify_fix.py` on calculator | Harness allows **undeclared extra files**; oracle still green |
| DeepSeek on todo/quiz: tokens spent, **0 writes**, `HARNESS_ERROR` | Not classified as LLM cognitive error because **no patch landed**. Could be dialect, create-file grant, or model not emitting applied tools |
| GLM on todo: **wrote** `TodoStore` but `add()` returned a dict → oracle `TypeError` | Once writes land, remaining miss is **LLM API mismatch**, not a silent harness no-op |
| Two B20 tasks GREEN on buggy code | **Oracle poisoning / under-specification**, not agent success |

**Honest summary:** the coding harness is **not** blocked on single-file repair when a paid tool-calling model is used. Small local 1.5B **cannot** be used to score Forge quality. Multi-file / greenfield still fails: DeepSeek did not apply writes; GLM applied a cognitively wrong store. That split is the first useful harness-vs-LLM signal. It is **not** an L2 control freeze (`UNFROZEN`, n ≪ 30, false-completion veto still 0).

---

## 6. Agent capability notes

1. **Planning (LDA):** `lda doctor` healthy; graph usable. Index HEAD lagged Git during the run — refresh with `uv run lda index --delta` before trusting line numbers on a new SHA.
2. **Protocol (`REPLAY`):** LAM 50/50 and BaaC cycle 9/9 prove oracles, zero-state reset, and Forge episode plumbing at $0. They **do not** prove coding skill.
3. **Skill loop (autofix):** fast local GREEN on three tier-1 tasks; patches can be dirty (tests inlined into source). Rollback path was not newly falsified this wave (all three resolved).
4. **Product-shaped harness (`vg-code-balanced` + Forge):** paid single-file GREEN; local 1.5B no-write; paid multi-file mixed (no-write vs wrong write). Always burned 8 turns.
5. **Oracle hardening still needed:** `05` needs asymmetric micro-transactions; `04` needs ≥5 threads or a deterministic lock injector; dogfood-02 must only run under a timeout wrapper.

---

## 7. What this report does **not** claim

- MS-CONTROL closed, Wilson LB, or a published pass-rate over the frozen 30-task L2 suite
- Equivalence between autofix-swe-loop and `vg code` product path
- That `openrouter/free` is a stable model identity
- That LAM 100% transfers to live models
- That remaining $0.095 of budget was required — it was left unused after the isolation questions were answered
