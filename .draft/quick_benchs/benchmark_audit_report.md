# Vanguard / AETHER Substrate Audit & Benchmark Evaluation Report

**Auditor**: Antigravity Autonomous Agent (Autonomous SOTA Coding & Verification Assistant)  
**Date**: 2026-09-12  
**Target Repository**: `vanguard / aether` (`feat/aether-framework-electroweak-canonical-agents`)  
**Subject HEAD**: `5224912f7fb121e0be2b723ffd2a6c605cfa9777`  
**Execution Environment**: Linux x86_64 | AMD Radeon RX 9060 XT (Vulkan Backend) | Python 3.12 (via `uv`)  
**Local Inference Engine**: Native `llama-server` (`build 10796, commit 9a4843cf2`) at `http://127.0.0.1:8080`  
**Active Model**: `Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf` (941 MB) & `~/Models/` suite  
**Replay & Simulation Engine**: Zero-Cost Hermetic LAM (LLM API Mock) Engine  

---

## 1. Executive Summary & Verification Matrix

An exhaustive evaluation and audit of the Vanguard / AETHER recursive-agency substrate, its architectural invariants, agent capability tiers, and coding challenge suites was conducted. In accordance with operational instructions, **zero production or benchmark code was modified**; all investigations and benchmarks were conducted via non-destructive inspections, read-only graph queries, and isolated execution scratchpads.

### Level 0 System Verification Gate

| Verification Dimension | Command / Falsifier | Measured Output / Metric | Status |
|---|---|---|---|
| **Boundary Enforcer** | `python3 tools/linters/check_boundaries.py` | 833 source files checked; hexagonal flow strictly intact | **PASS (GREEN)** |
| **TCB Budget Gate** | `python3 tools/linters/check_tcb_budget.py` | **1386 LOC** across 9 files (Threshold $\le 1438$, Headroom: +52 LOC) | **PASS (GREEN)** |
| **Domain Blindness (I-7)** | `python3 tools/linters/check_domain_blindness.py` | 0 AST/coding tokens in `kernel` and `domain` packages | **PASS (GREEN)** |
| **Runtime Purity (N-06)** | `python3 tools/linters/check_isolation_policy.py` | Pure declarative metadata; zero `subprocess` in `runtime/` | **PASS (GREEN)** |
| **Secret Leak Scanner** | `python3 tools/linters/scan_secrets.py` | 0 blocking secret patterns detected | **PASS (GREEN)** |
| **Code Duplication Guard** | `python3 tools/linters/check_duplication.py --enforce` | 0 forbidden duplicate surfaces | **PASS (GREEN)** |
| **Markdown Link Integrity** | `python3 tools/linters/check_markdown_links.py` | All relative links resolve | **PASS (GREEN)** |
| **Documentation Stale Paths** | `python3 tools/linters/check_stale_paths.py` | 778 files scanned; 0 obsolete `docs/` layout tokens | **PASS (GREEN)** |
| **Prompt Prefix Headroom (W12-A)** | `python3 tools/agent_plugins/cli.py prefix` | **2180 / 4096** characters (Headroom: +1916 chars) | **PASS (GREEN)** |
| **Hermetic Test Runner** | `python3 tools/agent_plugins/cli.py run test-runner` | 29 kernel dispatch tests verified in 0.147s | **PASS (GREEN)** |
| **Control & Canary Falsifiers** | `python3 -m unittest test.benchmarks.test_preregistration test.benchmarks.test_metric_veto` | 34 tests passed in 0.011s | **PASS (GREEN)** |
| **Control Corpus Integrity** | `python3 -m unittest test.benchmarks.test_control_corpus` | 8 tests passed in 0.046s (30 held-out tasks pinned) | **PASS (GREEN)** |
| **LDA Fact Graph & Doctor** | `uv run lda doctor --json` | `index_healthy: true`, 296 docs, 11,397 symbols, 91,611 relations | **PASS (GREEN)** |

---

## 2. Architecture, Modules & Invariants Review

### A. Agent Execution Kernel & Agency Loop

1. **`vanguard/packages/kernel/dispatch.py` (The 13-Stage Dispatch Pipeline S0–S12)**:
   - **Invariant I-1 (Single Path)**: There is exactly one entry point from an `EffectRequest` to execution (`Kernel.dispatch`).
   - **Pipeline Sequencing**:
     - `S0 ENTER` $\to$ `S1 PARSE` $\to$ `S2 RESOLVE` (resolves adapter before any resource lease, preventing stranded reservations per defect `K-04`).
     - `S3 DESCRIBE` $\to$ `S4 CLASSIFY` $\to$ `S5 AUTHORIZE` $\to$ `S6 GRANT`.
     - `S7 RESERVE`: Acquires governor lease against run budget.
     - `S8 VERIFY` $\to$ `S8a INTENT`: Writes durable `EffectStarted` event and `fsync`s before adapter execution (`K-47`). A crash between dispatch and emit leaves the effect *undeterminable* rather than invisible.
     - `S9 DISPATCH` $\to$ `S10 COMMIT` (debits reality, including overruns per `K-07`).
     - `S11 RELEASE` in `finally` block: Lease released before `S12 EMIT` (`K-06`).
   - **Descriptor Binding (`K-15`)**: Grants and suspension tokens strictly bind the SHA-256 digest of canonicalized request arguments; an authorization cannot be transplanted onto a different action.

2. **`vanguard/packages/agency/episode/engine.py` (The EpisodeEngine Turn Loop)**:
   - **Split Emission**: The loop appends `ProposalProduced` directly because proposals happen outside dispatch; grants, denials, and receipts are strictly appended by the kernel.
   - **Domain & Evaluator Independence**: The engine imports zero evaluators and zero domain/coding logic (`ICD §3`, `VG-03 §6.2`).
   - **Recursive Delegation (`S8-B-01`)**: Subagent `spawn()` executes an attenuated child episode under typed budget conservation. Child budgets strictly debit the parent remaining headroom.

3. **`vanguard/packages/apps/coding_max/facade.py` (CodingMax Facade)**:
   - Thin client of `ApplicationService`. Holds no private preset inventory (`_CatalogPresets` lazily projects `pack_catalog`).
   - Explicit `max_turns` can only monotonically attenuate loop bounds; never widen them.

### B. Universal Agent Capability Layer (`.agents/`)

- **4-Tier Ontological Hierarchy**:
  1. *Skills (Atomic)*: `test-runner`, `lda-navigator`, `llama-cpp`, `lam-engine`, `spec-driven-codegen`, `tdd-falsifier`. Hermetic, zero internal loops.
  2. *Techniques (Open-Loop)*: `spec-driven-codegen` (LDA context + LLM synthesis), `tdd-falsifier` (LDA test mapping + isolated test runner).
  3. *Proficiencies (Closed-Loop FSMs)*: `autofix-swe-loop` (Technique 1 + Technique 2 + AST delta re-indexing + fail-closed rollback).
  4. *Mastery (Horizon)*: Dynamic metacognitive routing.
- **W12-A Invariant**: Catalog prefix is strictly bounded to $\le 4096$ characters. Measured: **2180 characters** across 10 registered capabilities.

### C. Model Adapters & Inference Standards

- **Ollama Deprecation**: Completely eliminated from the system. Zero daemon footprint.
- **Local Model Standard**: `vanguard/packages/adapters/models/llama_cpp.py` implements OpenAI-compatible HTTP driver connecting to `llama-server` on `127.0.0.1:8080`. Offloads 99 layers to AMD Radeon GPU via Vulkan (`-ngl 99`).
- **Remote Model Standard**: `openrouter.py` with token economics, rate limiting, and timeout enforcement.
- **LAM Engine (`lam.py` / `cassette.py`)**: Offline hermetic replay with 0ms network latency and $0.00 spend. Over 3.67 million tokens saved to date.

### D. Control Canary & Benchmark Boundary (`benchmarks/ladder/`)

- **Manifest Admission Boundary (`control.py:125`)**: Enforces frozen membership ($N=30$ for L2 control), SHA-256 pinning of source trees and test oracles, and explicit resource ceilings.
- **Evidence Reconciliation (`evidence.py:118`)**: Reconciles evidence rows against frozen manifests. Missingness never shrinks the denominator; unrun or undetermined slots remain recorded.
- **False-Completion Hard Veto (`metrics.py:128`)**: If false-completion rate $FC > 0$, the metric engine raises `MetricVeto`, immediately disqualifying any capability claims.

---

## 3. Master Challenge & Corpus Gate Check (Anti-Poisoning & Anti-Cheating)

An automated AST and execution audit of all 37 challenge repositories across three suites (`baac`, `benchmark_20_suite`, and `greenfield`) was conducted.

### Corpus Health Overview

```text
Total Audited Challenges:       37
  ├── BaaC (Benchmark as Code):   9 challenges (Tiers 1–6)
  ├── Benchmark 20 Suite:        20 challenges (10 Brownfield, 10 Greenfield)
  └── Greenfield Suite:           8 challenges (Dogfood & Qualification)

Initial State Breakdown:
  ├── Initial RED (Expected):    33 challenges (Genuine defects or unimplemented modules)
  ├── Initial GREEN (Premature):  2 challenges (04_sqlite_wal_checkpoint_lock, 05_token_budget_clamping_drift)
  ├── Initial TIMEOUT / HANG:     1 challenge  (dogfood-02-subprocess-timeout-censoring)
  └── Static / No Test Oracle:    1 challenge  (greenfield-v0450-webapp)
```

### Critical Gate Check Findings

1. **Zero Poisoning / Cheating in BaaC (100% SOTA Integrity)**:
   - All 9 challenges in `benchmarks/baac/challenges/` have exact zero-state manifests verified by SHA-256.
   - Trivial assertions (`assert True`): **0**.
   - Solution leakage in `TASK.md`: **0**.
   - Oracles run in separate directories and test genuine external contracts.

2. **Issue Found: Toothless Math Oracle in `05_token_budget_clamping_drift`**:
   - *Intended Bug*: Float precision drift over repeated micro-reserve/refund transactions in `BudgetGovernor`.
   - *Flaw in Test*: The test in `test_budget_falsifier.py` executes:
     ```python
     for _ in range(1000):
         gov.reserve(0.00001)
         gov.refund(0.00001)
     ```
     Because each subtraction is immediately followed by an identical addition of the same float value, IEEE 754 floating-point arithmetic cancels out exactly to `1.0`. As a result, the test **passes on the buggy float implementation**, failing to falsify the bug!
   - *Audit Recommendation*: Restructure the test to perform 1000 accumulations of disparate fractions (e.g. `0.1 + 0.2`) before refunding, or compare against `Decimal`.

3. **Issue Found: Flaky Concurrency in `04_sqlite_wal_checkpoint_lock`**:
   - *Intended Bug*: Missing `PRAGMA busy_timeout` leading to `sqlite3.OperationalError: database is locked`.
   - *Flaw in Test*: `test_concurrent_store.py` runs 2 threads (50 writes and 10 checkpoints). On high-speed NVMe storage and Python's GIL, all 50 writes complete between checkpoints without triggering lock contention, causing the test to pass on the buggy code.
   - *Audit Recommendation*: Increase write concurrency (e.g. 5 concurrent writer threads with 500 events) to reliably induce SQLite database locking.

4. **Issue Found: Infinite Loop in `dogfood-02-subprocess-timeout-censoring`**:
   - `src/worker.py` contains `while i < len(items): results.append(items[i] * 2)` with no `i += 1`.
   - This test was intentionally designed to test subprocess timeout censoring. When run without timeout bounds, it hangs indefinitely. This validates why `test-runner` enforces hard subprocess timeout protection (`timeout=15.0`).

5. **Operational Finding: Root Test Import Pathing**:
   - In `benchmark_20_suite`, test files use `from src.<module> import ...`. Running `python3 -m unittest /path/to/test.py` from repository root causes Python's loader to treat path slashes as module dots. All benchmark drivers MUST execute tests with `PYTHONPATH=<task_root>` and `cwd=<task_root>`.

---

## 4. Standardized Benchmark Audit Cards (10 Evaluated Challenges)

The following 10 benchmark evaluations use a uniform schema and standardized table format:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                             STANDARDIZED BENCHMARK CARD SCHEMA                          │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Challenge ID & Stratum     4. Test Execution & Falsifier Transition                  │
│ 2. Number of Files in Task    5. Quantitative KPIs (Tokens/sec, Total Tokens, Latency)  │
│ 3. Gate Check (Poison/Cheat)  6. Result Quality & Rollback Analysis                     │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Benchmark 1: `bench_single_2K_tier-1_calculator`

| Dimension | Audit Metric & Observed Evidence |
|---|---|
| **Challenge ID** | `bench_single_2K_tier-1_calculator` |
| **Suite & Tier** | `baac` | Tier-1 Single-File Formula Repair |
| **Files in Challenge** | **6 files** (`TASK.md`, `challenge.yaml`, `manifest.sha256`, `src/__init__.py`, `src/calculator.py`, `oracle/verify.py`) |
| **Input Gate Check** | **PASS (CLEAN)**. Zero trivial assertions, zero leaked oracle code in `TASK.md`. Verified SHA-256 zero-state manifest. |
| **Initial Falsifier** | `FAIL (RED)` — `AssertionError: 8 != 15` on `calculate_value(2, 3)`. |
| **Agent Capability** | **Coding / SWE Repair (`autofix-swe-loop`)** via local Qwen 1.5B on Vulkan GPU |
| **Falsifier Command** | `python3 oracle/verify.py --workspace <task_dir>` |
| **Result Quality** | **PASS (GREEN) — RESOLVED in 1 turn**. Generated exact formula `(A + B) * B`. |
| **Execution Latency** | **1.450s** total loop duration (LLM latency: 1.297s, LDA delta: 0.114s) |
| **Token Throughput** | **113.5 tokens/sec** |
| **Total Tokens** | **34 completion tokens** (Prompt: 412 tokens, Total: 446 tokens) |
| **Cache & Compression** | AST token-bounded context slicing (`budget=2000`), Unified KV cache on GPU |
| **Turn Waste ($W$)** | **0** (1 valid action, 0 null/rambling turns) |
| **False-Completion** | **0.0** (Claim validated by ground-truth oracle exit code 0) |
| **Rollback Fidelity** | N/A (Resolved on turn 1) |

---

### Benchmark 2: `bench_single_2K_tier-1_string_dedupe`

| Dimension | Audit Metric & Observed Evidence |
|---|---|
| **Challenge ID** | `bench_single_2K_tier-1_string_dedupe` |
| **Suite & Tier** | `baac` | Tier-1 Single-File Algorithmic String Dedupe |
| **Files in Challenge** | **6 files** (`TASK.md`, `challenge.yaml`, `manifest.sha256`, `src/__init__.py`, `src/dedupe.py`, `oracle/verify.py`) |
| **Input Gate Check** | **PASS (CLEAN)**. Pure algorithmic specification; zero test leakage. |
| **Initial Falsifier** | `FAIL (RED)` — `AssertionError: None != 'abcd'` (unimplemented `pass` in `dedupe.py`). |
| **Agent Capability** | **Coding / SWE Repair (`autofix-swe-loop`)** |
| **Falsifier Command** | `python3 oracle/verify.py --workspace <task_dir>` |
| **Result Quality** | **PASS (GREEN) — RESOLVED in 1 turn**. Correct adjacent duplicate removal with boundary check `i == 0 or s[i] != s[i-1]`. |
| **Execution Latency** | **1.839s** total loop duration (LDA delta: 0.115s) |
| **Token Throughput** | **132.8 tokens/sec** |
| **Total Tokens** | **55 completion tokens** (Prompt: 430 tokens, Total: 485 tokens) |
| **Cache & Compression** | Unified KV cache, sub-30ms AST delta re-indexing |
| **Turn Waste ($W$)** | **0** (1 turn, 1 valid patch) |
| **False-Completion** | **0.0** (Confirmed green by oracle) |
| **Rollback Fidelity** | N/A (Resolved on turn 1) |

---

### Benchmark 3: `bench_single_2K_tier-1_fib_cli`

| Dimension | Audit Metric & Observed Evidence |
|---|---|
| **Challenge ID** | `bench_single_2K_tier-1_fib_cli` |
| **Suite & Tier** | `baac` | Tier-1 CLI Argument Parsing & Fibonacci Math |
| **Files in Challenge** | **6 files** (`TASK.md`, `challenge.yaml`, `manifest.sha256`, `src/__init__.py`, `src/fib.py`, `oracle/verify.py`) |
| **Input Gate Check** | **PASS (CLEAN)**. Clean requirement specifying input validation and iterative Fibonacci. |
| **Initial Falsifier** | `FAIL (RED)` — `AssertionError: None != 0` on `fib(0)`. |
| **Agent Capability** | **Coding / SWE Repair (`autofix-swe-loop`)** |
| **Falsifier Command** | `python3 oracle/verify.py --workspace <task_dir>` |
| **Result Quality** | **PASS (GREEN) — RESOLVED in 1 turn**. Implemented $O(N)$ iterative loop with `ValueError` guard on $N < 0$. |
| **Execution Latency** | **1.832s** total loop duration (LDA delta: 0.113s) |
| **Token Throughput** | **141.2 tokens/sec** |
| **Total Tokens** | **99 completion tokens** (Prompt: 468 tokens, Total: 567 tokens) |
| **Cache & Compression** | AST line slicing within 2000 token budget |
| **Turn Waste ($W$)** | **0** |
| **False-Completion** | **0.0** (Ground-truth verified) |
| **Rollback Fidelity** | N/A (Resolved on turn 1) |

---

### Benchmark 4: `bench_multi_8K_tier-2_json_todo_store`

| Dimension | Audit Metric & Observed Evidence |
|---|---|
| **Challenge ID** | `bench_multi_8K_tier-2_json_todo_store` |
| **Suite & Tier** | `baac` | Tier-2 Multi-File JSON Storage & Schema |
| **Files in Challenge** | **6 files** (`TASK.md`, `challenge.yaml`, `manifest.sha256`, `src/__init__.py`, `src/todo.py`, `oracle/verify.py`) |
| **Input Gate Check** | **PASS (CLEAN)**. Multi-file persistence contract; temporary file isolation in oracle. |
| **Initial Falsifier** | `FAIL (RED)` — `ImportError: cannot import name 'TodoStore' from 'todo'`. |
| **Agent Capability** | **Multi-Turn SWE Repair & Fail-Closed Rollback** |
| **Falsifier Command** | `python3 oracle/verify.py --workspace <task_dir>` |
| **Result Quality** | **FAIL $\to$ ROLLED BACK**. Agent synthesized JSON CRUD logic but omitted `self.filepath = filepath` assignment in `__init__`, raising `AttributeError` on `_save()`. |
| **Execution Latency** | **7.288s** across 3 full turns |
| **Token Throughput** | **152.4 tokens/sec** average |
| **Total Tokens** | **824 completion tokens** across 3 turns (279 + 266 + 279) |
| **Cache & Compression** | AST delta indexing refreshed in 0.116s, 0.115s, and 0.119s |
| **Turn Waste ($W$)** | **0** (Every turn executed an actionable code synthesis proposal) |
| **False-Completion** | **0.0** (Did NOT claim success; failure admitted truthfully) |
| **Rollback Fidelity** | **100% BYTE-FOR-BYTE IDENTICAL**. Target file restored to pre-turn state upon turn budget exhaustion. |

---

### Benchmark 5: `01_rate_limiter_lease_recovery`

| Dimension | Audit Metric & Observed Evidence |
|---|---|
| **Challenge ID** | `01_rate_limiter_lease_recovery` |
| **Suite & Tier** | `benchmark_20_suite` | Brownfield Bug Repair (Token Conservation) |
| **Files in Challenge** | **5 files** (`docs/SPEC.md`, `initial_state.sha256`, `src/governor.py`, `src/rate_limiter.py`, `test/test_limiter.py`) |
| **Input Gate Check** | **PASS (CLEAN)**. Formal invariant specification (`K-09`). Test checks exact token refund on lease expiry. |
| **Initial Falsifier** | `FAIL (RED)` — `AssertionError: 60 != 100 : Leakage detected: expected 100 available, got 60`. |
| **Agent Capability** | **Planning (`lda plan`) & SWE Repair (`autofix-swe-loop`)** |
| **Falsifier Command** | `PYTHONPATH=. python3 -m unittest test.test_limiter` |
| **Result Quality** | **Planning: 100% ACCURATE** (found `RateLimiter` at lines 4–33, callers, and test command in 0.82s). **Coding: ROLLED BACK**. 1.5B model generated Python 3 comprehension scoping error (`data` accessed outside list comprehension). |
| **Execution Latency** | **7.022s** across 3 turns |
| **Token Throughput** | **156.2 tokens/sec** |
| **Total Tokens** | **804 completion tokens** (268 tokens $\times$ 3 turns) |
| **Cache & Compression** | LDA AST delta indexing in 0.116s; token-bounded prompt injection |
| **Turn Waste ($W$)** | **0** (3 active attempts, 0 null actions) |
| **False-Completion** | **0.0** (Fail-closed verdict preserved) |
| **Rollback Fidelity** | **100% BYTE-FOR-BYTE IDENTICAL**. Target file restored to pristine buggy baseline. |

---

### Benchmark 6: `04_sqlite_wal_checkpoint_lock`

| Dimension | Audit Metric & Observed Evidence |
|---|---|
| **Challenge ID** | `04_sqlite_wal_checkpoint_lock` |
| **Suite & Tier** | `benchmark_20_suite` | Brownfield Concurrency Lock |
| **Files in Challenge** | **5 files** (`docs/SPEC.md`, `initial_state.sha256`, `src/event_store.py`, `test/test_concurrent_store.py`) |
| **Input Gate Check** | **WARN (FLAKY / UNDER-SPECIFIED TEST)**. The intended bug is missing `PRAGMA busy_timeout`. However, the test workload (50 writes, 10 checkpoints) is too light to induce lock contention on fast NVMe storage, allowing buggy code to pass. |
| **Initial Falsifier** | `PASS (GREEN)` — Premature pass due to insufficient concurrency stress. |
| **Agent Capability** | **Gate Check Auditing & Code Inspection** |
| **Falsifier Command** | `PYTHONPATH=. python3 -m unittest test.test_concurrent_store` |
| **Result Quality** | Identified root cause: SQLite GIL interleaving on Linux allows sequential writes without locking. Test requires $\ge 5$ concurrent threads to reliably falsify. |
| **Execution Latency** | **0.045s** test run duration |
| **Token Throughput** | N/A (Static inspection and test audit) |
| **Total Tokens** | 0 tokens (Prevented wasteful inference on false-green test) |
| **Cache & Compression** | N/A |
| **Turn Waste ($W$)** | **0** |
| **False-Completion** | **0.0** |
| **Rollback Fidelity** | Preserved |

---

### Benchmark 7: `05_token_budget_clamping_drift`

| Dimension | Audit Metric & Observed Evidence |
|---|---|
| **Challenge ID** | `05_token_budget_clamping_drift` |
| **Suite & Tier** | `benchmark_20_suite` | Brownfield Float Precision Drift |
| **Files in Challenge** | **5 files** (`docs/SPEC.md`, `initial_state.sha256`, `src/budget.py`, `test/test_budget_falsifier.py`) |
| **Input Gate Check** | **WARN (TOOTHLESS ORACLE / UNDER-SPECIFIED)**. `src/budget.py` uses native Python `float`. However, `test_repeated_micro_transactions_zero_drift` does immediate `reserve(0.00001)` then `refund(0.00001)` in a loop, which mathematically cancels out in IEEE 754 float arithmetic. Test reports PASS on buggy code! |
| **Initial Falsifier** | `PASS (GREEN)` — Defect undetected by checked-in test. |
| **Agent Capability** | **Gate Check Auditing & Arithmetic Falsification** |
| **Falsifier Command** | `PYTHONPATH=. python3 -m unittest test.test_budget_falsifier` |
| **Result Quality** | Audited and demonstrated that sequential symmetrical float operations do not accumulate drift. Oracle must be updated to accumulate asymmetric micro-transactions to falsify float arithmetic. |
| **Execution Latency** | **0.002s** test duration |
| **Token Throughput** | N/A |
| **Total Tokens** | 0 tokens (Inference bypassed due to toothless test) |
| **Cache & Compression** | N/A |
| **Turn Waste ($W$)** | **0** |
| **False-Completion** | **0.0** |
| **Rollback Fidelity** | Preserved |

---

### Benchmark 8: `11_kv_lru_ttl_store`

| Dimension | Audit Metric & Observed Evidence |
|---|---|
| **Challenge ID** | `11_kv_lru_ttl_store` |
| **Suite & Tier** | `benchmark_20_suite` | Greenfield Synthesis (LRU & Monotonic TTL Cache) |
| **Files in Challenge** | **3 files** (`README.md`, `src/__init__.py`, `test/test_suite.py`) |
| **Input Gate Check** | **PASS (CLEAN)**. Greenfield specification. Zero source code provided; rigorous unit test suite covering eviction, monotonic TTL expiration, deletion, and size. |
| **Initial Falsifier** | `FAIL (RED)` — `ImportError: cannot import name 'LRUTTLStore' from 'src.store'`. |
| **Agent Capability** | **Greenfield Spec-Driven Synthesis (`generate_grounded_patch`)** |
| **Falsifier Command** | `PYTHONPATH=. python3 -m unittest test.test_suite` |
| **Result Quality** | **MULTI-TURN PROGRESSION**: Turn 1 failed due to missing `Any` import. Turn 2 resolved typing import and passed `test_delete_and_size`, but failed eviction method name (`self.evict()` undefined). Turn 3 exhausted. |
| **Execution Latency** | **3.485s** (Turn 1) + **3.210s** (Turn 2) + **3.450s** (Turn 3) |
| **Token Throughput** | **167.5 tokens/sec** |
| **Total Tokens** | **883 completion tokens** (294 + 290 + 299) |
| **Cache & Compression** | Unified KV cache; 2500 token budget |
| **Turn Waste ($W$)** | **0** |
| **False-Completion** | **0.0** (Zero false claims) |
| **Rollback Fidelity** | **100% BYTE-FOR-BYTE IDENTICAL**. Target file restored to empty baseline. |

---

### Benchmark 9: `dogfood-02-subprocess-timeout-censoring`

| Dimension | Audit Metric & Observed Evidence |
|---|---|
| **Challenge ID** | `dogfood-02-subprocess-timeout-censoring` |
| **Suite & Tier** | `greenfield` | Robustness & Subprocess Timeout Falsifier |
| **Files in Challenge** | **4 files** (`AGENTS.md`, `TASK.md`, `src/worker.py`, `test_worker.py`) |
| **Input Gate Check** | **PASS (DESIGNED ADVERSARIAL BUG)**. `src/worker.py` contains a `while i < len(items):` infinite loop (missing increment `i += 1`). Intended to verify test runner timeout protection. |
| **Initial Falsifier** | `FAIL (TIMEOUT/HANG)` — Process execution hangs without timeout bounds. |
| **Agent Capability** | **Hermetic Test Runner Timeout Protection (`test-runner`)** |
| **Falsifier Command** | `python3 -m unittest test_worker.py` |
| **Result Quality** | **VERIFIED RESILIENT**: Under standard runner, process hung indefinitely. Under `test-runner` skill with `timeout=3.0`, subprocess was terminated gracefully with exit code 124, returning structured failure report. |
| **Execution Latency** | **3.001s** (Enforced timeout) |
| **Token Throughput** | N/A |
| **Total Tokens** | 0 tokens |
| **Cache & Compression** | Process isolation via `subprocess.Popen` |
| **Turn Waste ($W$)** | **0** |
| **False-Completion** | **0.0** |
| **Rollback Fidelity** | Preserved |

---

### Benchmark 10: `lam_synthetic_replay_50`

| Dimension | Audit Metric & Observed Evidence |
|---|---|
| **Challenge ID** | `lam_synthetic_replay_50` |
| **Suite & Tier** | `tools/002_LLM_API_MOCK` | Hermetic Synthetic Simulation & Cassette Replay |
| **Files in Challenge** | **254 synthetic scenario fixtures** in `tools/002_LLM_API_MOCK/scenarios/` |
| **Input Gate Check** | **PASS (HERMETIC REPLAY)**. Deterministic request/response cassettes bound to SHA-256 digests. |
| **Initial Falsifier** | `PASS (GREEN)` — 100% replay fidelity. |
| **Agent Capability** | **Zero-Cost Simulation Engine (`lam-engine`)** |
| **Falsifier Command** | `python3 tools/002_LLM_API_MOCK/cli.py bench --count 50` |
| **Result Quality** | **50/50 successful responses (100.0%)**. |
| **Execution Latency** | **0.46ms total execution time** (Average latency: **0.009ms per call**) |
| **Token Throughput** | **> 1,000,000 tokens/sec equivalent** (in-memory hash join) |
| **Total Tokens** | **38,200 tokens simulated** ($0.0000 spend, zero network I/O) |
| **Cache & Compression** | SQLite indexed lookup in `lam.sqlite` |
| **Turn Waste ($W$)** | **0** |
| **False-Completion** | **0.0** |
| **Rollback Fidelity** | Hermetic isolation |

---

## 5. Summary KPI Evaluation Table

The following aggregate table compares performance, token throughput, and quality metrics across all 10 evaluated benchmarks:

| Benchmark / Challenge | Stratum | Files | Gate Check | Agent Mode | Pre $\to$ Post | Tokens/Sec | Total Tokens | Latency | Rollback | False Compl. |
|---|---|:---:|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `bench_single_2K_tier-1_calculator` | Single-File | 6 | PASS | Autofix (Local) | RED $\to$ GREEN | **113.5** | 34 | 1.45s | N/A | **0.0** |
| `bench_single_2K_tier-1_string_dedupe` | Single-File | 6 | PASS | Autofix (Local) | RED $\to$ GREEN | **132.8** | 55 | 1.84s | N/A | **0.0** |
| `bench_single_2K_tier-1_fib_cli` | Single-File | 6 | PASS | Autofix (Local) | RED $\to$ GREEN | **141.2** | 99 | 1.83s | N/A | **0.0** |
| `bench_multi_8K_tier-2_json_todo_store` | Multi-File | 6 | PASS | Autofix (Local) | RED $\to$ ROLLBACK | **152.4** | 824 | 7.29s | **100%** | **0.0** |
| `01_rate_limiter_lease_recovery` | Brownfield | 5 | PASS | LDA + Autofix | RED $\to$ ROLLBACK | **156.2** | 804 | 7.02s | **100%** | **0.0** |
| `04_sqlite_wal_checkpoint_lock` | Brownfield | 5 | WARN (Flaky) | Audit / Inspect | GREEN (Flaky) | N/A | 0 | 0.05s | Preserved | **0.0** |
| `05_token_budget_clamping_drift` | Brownfield | 5 | WARN (Oracle) | Audit / Inspect | GREEN (Toothless) | N/A | 0 | 0.00s | Preserved | **0.0** |
| `11_kv_lru_ttl_store` | Greenfield | 3 | PASS | Codegen (Local) | RED $\to$ ROLLBACK | **167.5** | 883 | 10.14s | **100%** | **0.0** |
| `dogfood-02-subprocess-timeout-censoring` | Greenfield | 4 | PASS (Hang) | Test-Runner | HANG $\to$ TIMEOUT | N/A | 0 | 3.00s | Preserved | **0.0** |
| `lam_synthetic_replay_50` | Simulation | 254 | PASS | LAM Replay | GREEN $\to$ GREEN | **>1M eq.** | 38,200 | 0.00s | N/A | **0.0** |

---

## 6. AI Agent Capability Analysis & Qualitative Findings

### 1. Planning Capability (`lda-navigator`)
- **Strengths**: `uv run lda plan` is exceptional. For the brownfield query `"fix lease recovery in rate limiter"`, it scored 0.824 confidence, identified the exact target class (`RateLimiter`) and methods (`acquire`, `release`), extracted the blast radius (3 upstream callers), and surfaced the exact falsifier command in under **0.82 seconds**.
- **Context Compaction**: Replaces multi-thousand line file dumps with AST line slices, reducing token overhead by **~80%**.

### 2. Coding & SWE Repair (`spec-driven-codegen` & `autofix-swe-loop`)
- **Local Model Performance**: Native `llama-server` on Vulkan AMD GPU demonstrated outstanding speeds between **113.5 and 167.5 tokens/second**.
- **Single-File Coding Competence**: For elementary algorithmic tasks (`calculator`, `dedupe`, `fib`), the local Qwen 1.5B model achieved **100% pass rates in 1 single turn**.
- **Multi-File & Scoping Limitations on Small Models**: On multi-turn brownfield and multi-file tasks (`todo_store`, `rate_limiter`), the 1.5B parameter model exhibited classic small-model failure modes:
  - Forgetting instance variable assignments (`self.filepath = filepath`).
  - Accessing list comprehension iteration variables outside comprehension scope in Python 3.12.
- **Fail-Closed Rollback Guarantee**: The framework's fail-closed rollback protocol functioned with **100% reliability**. When turns exhausted or tests failed, mutated files were restored byte-for-byte to their pristine baseline, leaving zero workspace corruption.

### 3. Explaining Capability (`vanguard/packages/runtime/explain.py`)
- **Strict 3-Question Audit Contract**: Evaluated `explain_artifact` for `vg why <artifact>`. Adheres strictly to the architectural law:
  1. *What activated it?* Derived from ledger events (`ArtifactCreated`, `ActivationChanged`).
  2. *What does it predict?* Derived from active `Claim` models.
  3. *What would demote it?* Derived from demotion predicates.
- **Absence is Never Smoothed**: Un-evidenced artifacts explicitly report absence rather than returning misleading empty summaries. All 14 unit tests in `test/runtime/test_explain_artifact.py` pass cleanly.

### 4. Verification & Canary Bounds (`benchmarks/ladder/`)
- **Truthful Control Accounting (RUN-02 / RUN-03)**: Validated that missing outcomes are tracked separately and never shrink the 30-slot denominator.
- **Metric Veto**: Verified that a non-zero false completion rate instantly raises `MetricVeto`, preventing capability inflation.

---

## 7. Recommendations & Immediate Engineering Actions

1. **Harden Brownfield Test Oracles**:
   - **`05_token_budget_clamping_drift`**: Replace the symmetrical loop in `test_budget_falsifier.py` with an asymmetric floating-point accumulation sequence that actually falsifies IEEE 754 drift on unrounded floats.
   - **`04_sqlite_wal_checkpoint_lock`**: Increase the concurrency load in `test_concurrent_store.py` to 5+ concurrent threads writing 500+ records to reliably trigger SQLite database locking on fast NVMe Linux systems.
2. **Model Recommendations for Complex Tasks**:
   - For single-file math and CLI tasks, `Qwen2.5-Coder-1.5B` at 150+ tokens/sec is extraordinarily fast and capable.
   - For multi-file architecture, stateful OOP, and complex Python 3 variable scoping, use `Qwen2.5-Coder-14B` (`~/Models/Qwen2.5-Coder-14B-Instruct-Q4_K_M.gguf`) or `Qwen3.8-27B-UD-Q2_K_XL.gguf` to prevent instance variable omissions.
3. **Benchmark Test Runner Pathing**:
   - Ensure all benchmark harnesses explicitly configure `PYTHONPATH` to task workspace directories to prevent `ModuleNotFoundError: No module named 'src'` when executing tests from repository root.

---
<!-- GOAL_COMPLETE -->
