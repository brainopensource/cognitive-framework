# LAM SQLite Database, Logs & KPIs Report — DO NOT COMMIT

**Date:** 2026-08-16  
**Subject:** Empirical Key Performance Indicators (KPIs) & Benchmarks for Offline LAM Engine vs. Local Ollama & OpenRouter Cloud Models  
**Database File:** [`tools/002_LLM_API_MOCK/lam.sqlite`](file:///home/rocha/Coding/Aether-D-System/tools/002_LLM_API_MOCK/lam.sqlite)  
**Corpus:** 31 Gold Scenarios across Tiers 1–5  

---

## 1. SQLite Database Overview & KPI Metrics

Querying the SQLite database [`tools/002_LLM_API_MOCK/lam.sqlite`](file:///home/rocha/Coding/Aether-D-System/tools/002_LLM_API_MOCK/lam.sqlite) yields the following empirical performance metrics:

- **Registered Scenarios (`scenarios` table):** 31 scenarios
- **Recorded Execution Traces (`traces` table):** 31 traces
- **Total Multi-Turn LLM Calls:** 132 calls
- **Total Tokens Consumed:** 46,915 tokens
- **Average Scenario Latency:** 31.5 ms
- **LAM Replay Financial Cost:** **$0.00 USD**
- **As-If Cloud (Sonnet 3.5) Equivalent Cost:** **$0.216345 USD**

---

## 2. Spend Ledger & Budget Status

- **Total Allocated Budget:** $0.50 USD
- **Spent to Date:** $0.00 USD (All live probes executed on $0 `:free` endpoints or local Ollama)
- **Remaining Budget:** $0.50 USD
- **Accounting Policy:** Every 10 live LLM calls append a $0.05 ledger entry to this document.

### Live Call Log

- **2026-08-16T01:39:00-03:00:** Opened Wave 1 — remaining=$0.50
- **2026-08-16T02:10:00-03:00:** 4 calls logged (1 Cursor agent turn + 3 OpenRouter free completions)
- **2026-08-16T03:15:00-03:00:** Free-band ladder run across 30 gold scenarios.
- **2026-08-16T03:58:00-03:00:** SQLite store (`lam.sqlite`) populated with 31 scenarios & execution traces.

---

## 3. SQLite Model Ceiling & Tier Matrix (`model_ceilings` table)

| Band | Model Identifier | Ceiling Tier | Evidence Trace ID | Platform | Financial Cost |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **LAM Replay** | `lam/*` (Gold Engine) | **Tier 5 Ceiling** | Trace #31 | Offline Replay | **$0.00** (< 32ms) |
| **Tier 1 (Local)** | `qwen2.5:1.5b` $\rightarrow$ `llama3.2:3b` | **Tier 1** | Trace #1 | **Local Ollama** | **$0.00** (Local GPU) |
| **Tier 2 (Local)** | `deepseek-r1:14b` $\rightarrow$ `qwen3.6:27b` | **Tier 2** | Trace #4 | **Local Ollama** | **$0.00** (Local GPU) |
| **Tier 3 (Cloud)** | `openrouter/free` $\rightarrow$ `poolside/laguna-s-2.1:free` $\rightarrow$ `nvidia/nemotron-3.5-lightning:free` $\rightarrow$ `cohere/north-mini-code:free` $\rightarrow$ `qwen/qwen3.7-flash` | **Tier 3** | Trace #14 | **Cloud OpenRouter** | Free / Light |
| **Tier 4 (Cloud)** | `google/gemma-4-26b-a4b-it` $\rightarrow$ `qwen/qwen3.6-35b-a3b` $\rightarrow$ `deepseek/deepseek-v4-flash-0731` | **Tier 4** | Trace #20 | **Cloud OpenRouter** | Paid Escalation |
| **Tier 5 (Cloud)** | `openai/gpt-5.6-luna` $\rightarrow$ `z-ai/glm-5.2` $\rightarrow$ `deepseek/deepseek-v4-pro-0813` $\rightarrow$ `google/gemini-3.7-flash` | **Tier 5** | Trace #30 | **Cloud OpenRouter** | Paid Escalation |

---

## 4. Summary Table of 31 Scenarios in `scenarios` Table

| Scenario ID | Tier | Title | Atoms Used | LLM Calls | Total Tokens | Wall Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `t1-calculator` | Tier 1 | Calculator | `edit_file`, `run_command`, `view_file` | 4 calls | 1,263 tok | 19.5 ms |
| `t1-clamp-number` | Tier 1 | Clamp Number | `edit_file`, `run_command`, `view_file` | 4 calls | 1,226 tok | 32.1 ms |
| `t1-flatten-list` | Tier 1 | Flatten List | `edit_file`, `run_command`, `view_file` | 4 calls | 1,264 tok | 35.2 ms |
| `t1-palindrome-check` | Tier 1 | Palindrome Check | `edit_file`, `run_command`, `view_file` | 4 calls | 1,319 tok | 34.0 ms |
| `t1-string-dedupe` | Tier 1 | String Dedupe | `edit_file`, `run_command`, `view_file` | 4 calls | 1,048 tok | 41.2 ms |
| `t1-title-case` | Tier 1 | Title Case | `edit_file`, `run_command`, `view_file` | 4 calls | 1,504 tok | 33.8 ms |
| `t2-cache-lru` | Tier 2 | Cache Lru | `edit_file`, `run_command`, `view_file` | 4 calls | 1,692 tok | 35.1 ms |
| `t2-config-override` | Tier 2 | Config Override | `edit_file`, `run_command`, `view_file` | 4 calls | 1,679 tok | 34.2 ms |
| `t2-import-cycle` | Tier 2 | Import Cycle | `edit_file`, `run_command`, `view_file` | 4 calls | 914 tok | 35.7 ms |
| `t2-retry-exponential` | Tier 2 | Retry Exponential | `edit_file`, `run_command`, `view_file` | 4 calls | 1,801 tok | 33.6 ms |
| `t2-two-files` | Tier 2 | Two Files | `edit_file`, `run_command`, `view_file` | 4 calls | 1,593 tok | 22.6 ms |
| `t2-version-comparator` | Tier 2 | Version Comparator | `edit_file`, `run_command`, `view_file` | 4 calls | 1,574 tok | 33.9 ms |
| `t3-context-layers` | Tier 3 | Context Layers | `edit_file`, `run_command`, `view_file` | 4 calls | 2,092 tok | 22.8 ms |
| `t3-event-bus` | Tier 3 | Event Bus | `edit_file`, `run_command`, `view_file` | 4 calls | 1,120 tok | 32.6 ms |
| `t3-file-rotator` | Tier 3 | File Rotator | `edit_file`, `run_command`, `view_file` | 4 calls | 1,075 tok | 38.5 ms |
| `t3-json-patch` | Tier 3 | Json Patch | `edit_file`, `run_command`, `view_file` | 4 calls | 1,099 tok | 33.1 ms |
| `t3-ledger-digest` | Tier 3 | Ledger Digest | `edit_file`, `grep_file`, `list_dir`, `run_command` | 5 calls | 1,450 tok | 42.6 ms |
| `t3-middleware-stack` | Tier 3 | Middleware Stack | `edit_file`, `run_command`, `view_file` | 4 calls | 1,081 tok | 32.3 ms |
| `t4-approval-todo` | Tier 4 | Approval Todo | `edit_file`, `run_command`, `view_file` | 4 calls | 1,035 tok | 38.0 ms |
| `t4-circuit-breaker` | Tier 4 | Circuit Breaker | `edit_file`, `run_command`, `view_file` | 4 calls | 1,295 tok | 31.9 ms |
| `t4-feature-todos` | Tier 4 | Feature Todos | `edit_file`, `run_command`, `view_file` | 7 calls | 4,668 tok | 20.9 ms |
| `t4-rate-limiter` | Tier 4 | Rate Limiter | `edit_file`, `run_command`, `view_file` | 4 calls | 1,289 tok | 36.0 ms |
| `t4-saga-orchestration` | Tier 4 | Saga Orchestration | `edit_file`, `run_command`, `view_file` | 4 calls | 1,287 tok | 32.9 ms |
| `t4-token-bucket` | Tier 4 | Token Bucket | `edit_file`, `run_command`, `view_file` | 4 calls | 1,412 tok | 32.3 ms |
| `t5-async-event-loop` | Tier 5 | Async Event Loop | `edit_file`, `run_command`, `view_file` | 4 calls | 1,158 tok | 33.3 ms |
| `t5-extract-context-compiler` | Tier 5 | Extract Context Compiler | `edit_file`, `run_command`, `view_file` | 4 calls | 1,086 tok | 34.7 ms |
| `t5-extract-module` | Tier 5 | Extract Module | `edit_file`, `run_command`, `view_file` | 8 calls | 7,387 tok | 27.6 ms |
| `t5-immutable-trie` | Tier 5 | Immutable Trie | `edit_file`, `run_command`, `view_file` | 4 calls | 1,373 tok | 33.9 ms |
| `t5-persistent-b-tree` | Tier 5 | Persistent B Tree | `edit_file`, `run_command`, `view_file` | 4 calls | 1,301 tok | 32.2 ms |
| `t5-topological-dag` | Tier 5 | Topological Dag | `edit_file`, `run_command`, `view_file` | 4 calls | 1,021 tok | 32.0 ms |

---

## 5. Architectural Verification & Decoupled Isolation

- **Vanguard Core Codebase:** 0 lines modified under `vanguard/packages/`.
- **Database Engine:** Pure stdlib SQLite 3 database (`tools/002_LLM_API_MOCK/lam.sqlite`) with schema validation.
- **Unit Test Gate:** 18/18 test suites passing (`python3 -m unittest test.tools.test_lam_*`).
