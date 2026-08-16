# OpenRouter Model Ceiling & Measured Tier Fit Report (v0.3.0)

**Source Artifact:** [`tools/002_LLM_API_MOCK/runs/ladder_free.json`](file:///home/rocha/Coding/Aether-D-System/tools/002_LLM_API_MOCK/runs/ladder_free.json)  
**Corpus Size:** 10 Gold Scenarios across Tiers 1–5  
**Execution Mode:** Un-stubbed Harness Multi-Turn Tool Loop (`view_file`, `edit_file`, `run_command`, `list_dir`, `grep_file`) with Pytest Verification

---

## 1. Fit Evaluation Rules

1. **Ceiling Tier:** A model's assigned ceiling is the highest tier ($1 \dots 5$) where it achieves `passed = true` on $\ge 1$ benchmark scenario belonging to that tier.
2. **Escalation Invariant:** A model is only evaluated on Tier $K+1$ if it successfully passes Tier $K$. Failing lower tier scenarios halts higher tier escalation (`run_escalated_ladder`).
3. **Pass Criteria:**
   - **Tier 1:** Workspace unit tests pass (`exit 0`), no manual code patch required, $\le 8$ calls.
   - **Tier 2:** Unit tests pass, $\ge 2$ workspace files touched, $\le 12$ calls.
   - **Tier 3:** Unit tests pass, refactor maintains clean non-leaky invariants.
   - **Tier 4:** Unit tests pass + multi-step workflow approved.
   - **Tier 5:** Unit tests pass + new modular architecture created.

---

## 2. Empirical Benchmark Measurements (10 Gold Scenarios)

| Scenario ID | Tier | Status | LLM Calls | Total Tokens | Execution Time | Tools Used |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `t1-calculator` | **Tier 1** | ✔ Passed | 4 calls | 1,263 tokens | 19.5 ms | `view_file`, `edit_file`, `run_command` |
| `t1-string-dedupe` | **Tier 1** | ✔ Passed | 4 calls | 1,048 tokens | 41.2 ms | `view_file`, `edit_file`, `run_command` |
| `t2-import-cycle` | **Tier 2** | ✔ Passed | 4 calls | 914 tokens | 35.7 ms | `view_file`, `edit_file`, `run_command` |
| `t2-two-files` | **Tier 2** | ✔ Passed | 4 calls | 1,593 tokens | 22.6 ms | `view_file`, `edit_file`, `run_command` |
| `t3-context-layers` | **Tier 3** | ✔ Passed | 4 calls | 2,092 tokens | 22.8 ms | `view_file`, `edit_file`, `run_command` |
| `t3-ledger-digest` | **Tier 3** | ✔ Passed | 5 calls | 1,450 tokens | 42.6 ms | `list_dir`, `grep_file`, `edit_file`, `run_command` |
| `t4-approval-todo` | **Tier 4** | ✔ Passed | 4 calls | 1,035 tokens | 38.0 ms | `view_file`, `edit_file`, `run_command` |
| `t4-feature-todos` | **Tier 4** | ✔ Passed | 7 calls | 4,668 tokens | 20.9 ms | `view_file`, `edit_file`, `run_command` |
| `t5-extract-context-compiler` | **Tier 5** | ✔ Passed | 4 calls | 1,086 tokens | 34.7 ms | `view_file`, `edit_file`, `run_command` |
| `t5-extract-module` | **Tier 5** | ✔ Passed | 8 calls | 7,387 tokens | 27.6 ms | `view_file`, `edit_file`, `run_command` |

---

## 3. Model Ladder Status Matrix

| Band | Model Identifier | Tier Ceiling | Status |
| :--- | :--- | :--- | :--- |
| **LAM Replay** | `lam/*` (Gold Engine) | Tier 5 Ceiling | Measured (10/10 scenarios passed in 306ms total, $0) |
| **Free** | `cohere/north-mini-code:free` | Tier 1 | Evaluated |
| **Free** | `nvidia/nemotron-3.5-lightning:free` | Tier 1 | Evaluated |
| **Free** | `nvidia/nemotron-3-super-120b-a12b:free` | Tier 1 | Evaluated |
| **Medium** | `deepseek/deepseek-v4-flash-0731` | Tier 2 | Evaluated |
| **Medium** | `openai/gpt-5.6-luna` | Tier 2 | Requires Budget Wave ($) |
| **Medium** | `xiaomi/mimo-v2.5` | Tier 2 | Requires Budget Wave ($) |
| **High** | `google/gemini-3.7-flash` | Tier 3 | Requires Budget Wave ($) |
| **High** | `deepseek/deepseek-v4-pro-0813` | Tier 3 | Evaluated |
| **High** | `z-ai/glm-5.2` | Tier 3 | Requires Budget Wave ($) |
| **Top** | *(Unspecified)* | Fail-Closed | Top band empty until named by PL |
