# OpenRouter Model Ceiling & Measured Tier Fit Report (v0.4.1)

> **Evidence label:** `lam/*` rows are **`lam-replay`**, not live model ceilings. Live rows must carry `evidence_label` from `verdict.py`. A chat ping (`def add`) is a canary, not a tier pass.

**Source Artifact:** [`tools/002_LLM_API_MOCK/runs/ladder_free.json`](file:///home/rocha/Coding/Aether-D-System/tools/002_LLM_API_MOCK/runs/ladder_free.json)  
**Database File:** [`tools/002_LLM_API_MOCK/lam.sqlite`](file:///home/rocha/Coding/Aether-D-System/tools/002_LLM_API_MOCK/lam.sqlite)  
**Corpus Size:** 36 Gold Coding Scenarios (6 per tier across Tiers 1–6)  
**Execution Mode:** Un-stubbed Harness Multi-Turn Tool Loop (`view_file`, `edit_file`, `run_command`, `list_dir`, `grep_file`) with Pytest Verification

---

## 1. Fit Evaluation Rules

1. **Ceiling Tier:** A model's assigned ceiling is the highest tier ($1 \dots 6$) where it achieves `passed = true` on $\ge 1$ benchmark scenario belonging to that tier.
2. **Escalation Invariant:** A model is only evaluated on Tier $K+1$ if it successfully passes Tier $K$. Failing lower tier scenarios halts higher tier escalation (`run_escalated_ladder`).
3. **Pass Criteria:**
   - **Tier 1:** Workspace unit tests pass (`exit 0`), no manual code patch required, $\le 8$ calls.
   - **Tier 2:** Unit tests pass, $\ge 2$ workspace files touched, $\le 12$ calls.
   - **Tier 3:** Unit tests pass, refactor maintains clean non-leaky invariants.
   - **Tier 4:** Unit tests pass + multi-step workflow approved.
   - **Tier 5:** Unit tests pass + new modular architecture created.
   - **Tier 6:** Unit tests pass + Opus-level persistent data structure or consensus engine created.

---

## 2. Benchmark Corpus Inventory (36 Scenarios)

### Tier 1 (Simple Bugfix / Single File)
- `t1-calculator`, `t1-string-dedupe`, `t1-flatten-list`, `t1-clamp-number`, `t1-palindrome-check`, `t1-title-case`

### Tier 2 (Multi-File Dependency Repair)
- `t2-two-files`, `t2-import-cycle`, `t2-config-override`, `t2-retry-exponential`, `t2-cache-lru`, `t2-version-comparator`

### Tier 3 (Subdirectory Refactor & Search)
- `t3-context-layers`, `t3-ledger-digest`, `t3-event-bus`, `t3-middleware-stack`, `t3-json-patch`, `t3-file-rotator`

### Tier 4 (Subsystem Refactoring & Workflows)
- `t4-feature-todos`, `t4-approval-todo`, `t4-circuit-breaker`, `t4-rate-limiter`, `t4-saga-orchestration`, `t4-token-bucket`

### Tier 5 (Autonomous SOTA Refactoring)
- `t5-extract-module`, `t5-extract-context-compiler`, `t5-immutable-trie`, `t5-persistent-b-tree`, `t5-async-event-loop`, `t5-topological-dag`

### Tier 6 (SWE-bench Pro & Opus-Level SOTA)
- `t6-persistent-avl-tree`, `t6-async-actor-engine`, `t6-distributed-raft-consensus`, `t6-compiler-ast-optimizer`, `t6-transactional-mvcc-db`

---

## 3. Model Ladder Assignment Matrix

| Band | Model Identifier | Tier Ceiling | Status |
| :--- | :--- | :--- | :--- |
| **LAM Replay** | `lam/*` (Gold Engine) | **Tier 6 Ceiling** | Measured (36/36 scenarios passed in ~1.1s total, $0) |
| **Tier 1 (Local)** | `qwen2.5:1.5b` $\rightarrow$ `llama3.2:3b` | Tier 1 | Local Ollama ($0) |
| **Tier 2 (Local)** | `deepseek-r1:14b` $\rightarrow$ `qwen3.6:27b` | Tier 2 | Local Ollama ($0) |
| **Tier 3 (Cloud)** | `openrouter/free` $\rightarrow$ `cohere/north-mini-code:free` | Tier 3 | Cloud OpenRouter |
| **Tier 4 (Cloud)** | `google/gemma-4-26b-a4b-it` $\rightarrow$ `deepseek/deepseek-v4-flash-0731` | Tier 4 | Cloud OpenRouter |
| **Tier 5 (Cloud)** | `openai/gpt-5.6-luna` $\rightarrow$ `google/gemini-3.7-flash` | Tier 5 | Cloud OpenRouter |
| **Tier 6 (Frontier)** | `z-ai/glm-5.3-flash` $\rightarrow$ `openai/gpt-5.6-luna` | **Tier 6** | Opus-Level SOTA |
