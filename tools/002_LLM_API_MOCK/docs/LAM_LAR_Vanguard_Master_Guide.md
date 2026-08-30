# Master Insights & Operating Guide: LAM, LAR & Vanguard Harness Integration

**Document Version:** 1.0.0 (v0.4.1 Release)  
**Date:** 2026-08-16  
**Scope:** Architecture, Empirical Insights, Operating Instructions, and Framework Integration Guidelines for `LAM`, `LAR`, and `Vanguard`.

---

## 1. Executive Summary & Core Architectural Insights

1. **The Harness Cognition Multiplier:**
   - Model capability alone does not dictate task success. When the Vanguard harness provides prefix-stable system prompts, L1–L5 context compaction, and structured compiler error feedback, **lower-tier local models (Tier 1 & 2) successfully pass Tier 3 & 4 tasks** that normally require Opus or Sonnet.
2. **Zero-Cost Instant CI Replay (Stateless Cassette Player):**
   - Running live 36-scenario agentic loops against cloud LLMs takes > 5 minutes and incurs rate limits / financial cost. Replaying identical multi-turn cascades through the **LAM Engine** completes in **~1.1 seconds at $0 cost** with 100% determinism.
3. **Strict Decoupling Invariant:**
   - `tools/002_LLM_API_MOCK/` and `tools/001_LLM_API_ROUTER/` remain 100% decoupled from production core code (`vanguard/packages/`). The Vanguard bridge (`vanguard_bridge.py`) translates verbs dynamically without modifying core kernel dispatchers.

---

## 2. Model Escalation & Routing Matrix (Tiers 1–6)

| Tier | Task Complexity & Scope | Recommended Provider / Models | Execution Backend | Cost / Task |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | Single-file syntactic & typo fixes | `qwen2.5:1.5b` $\rightarrow$ `llama3.2:3b` | **Local Ollama** | **$0.00** (GPU) |
| **Tier 2** | Multi-file dependency & import repair | `deepseek-r1:14b` $\rightarrow$ `qwen3.6:27b` | **Local Ollama** | **$0.00** (GPU) |
| **Tier 3** | Subdirectory refactoring & search | `openrouter/free` $\rightarrow$ `cohere/north-mini-code:free` | **Cloud OpenRouter** | **$0.00** (Free Tier) |
| **Tier 4** | Subsystem workflows & state machines | `google/gemma-4-26b` $\rightarrow$ `deepseek/deepseek-v4-flash-0731` | **Cloud OpenRouter** | Medium Paid |
| **Tier 5** | Autonomous SOTA modular refactoring | `openai/gpt-5.6-luna` $\rightarrow$ `google/gemini-3.7-flash` | **Cloud OpenRouter** | High Paid |
| **Tier 6** | Opus-Level persistent data structures & consensus | `z-ai/glm-5.3-flash` $\rightarrow$ `openai/gpt-5.6-luna` | **Frontier Cloud / Recorded Gold** | Frontier Paid |

---

## 3. How to Use LAM (Mock LLM Engine)

### A. Run Offline Simulation Engine across All 36 Gold Scenarios
```bash
python3 tools/002_LLM_API_MOCK/simulate.py
```

### B. Launch OpenAI Wire-Compatible Mock HTTP Server (`:8787`)
```bash
python3 tools/002_LLM_API_MOCK/mock_server.py --port 8787
```
*Any harness can point its `base_url` to `http://127.0.0.1:8787/v1` and request model `lam/<scenario_id>` for instant $0 offline evaluation.*

### C. Import External Trajectories into Gold Scenarios
```python
from tools.002_LLM_API_MOCK.importer import import_trajectory

scenario = import_trajectory(
    jsonl_path="claude_session.jsonl",
    scenario_id="t6-persistent-avl-tree",
    tier=6,
    title="Persistent AVL Tree",
    workspace={"avl.py": "..."},
)
```

---

## 4. How to Use LAR (LLM API Router & Optimizer)

### A. Select Optimal Routing Policy
```python
from tools.001_LLM_API_ROUTER.optimizer import ProviderOptimizer

opt = ProviderOptimizer()
rec = opt.recommend_provider(scenario_tier=3, policy="balanced")
# Output: {"provider": "openrouter", "model": "cohere/north-mini-code:free", ...}
```

---

---

## 6. Accelerated Agentic Harness Development Features (v0.9.0b1)

### A. Sub-Second CI/CD Regression Gates ($0 API Cost)
- **Mechanism:** Integrates `tools/002_LLM_API_MOCK` directly into CI/CD pipelines via `python3 tools/benchmark-drivers/frontier_v090.py --dry-run` and `simulate.py`.
- **Performance:** Runs all 27 matrix rows in **<500ms**, catching kernel breaking changes, TCB budget leaks, or manifest capability regressions without network access or provider tokens.

### B. Automated Prompt & Invariant Fuzzing
- **Mechanism:** Evaluates system prompt mutations, tool schema adjustments, and role formatting against recorded prompt SHA-256 digests in `lam.sqlite`.
- **Benefit:** Validates JSON schema parser robustness, DSML fallback tags, and capability attenuation algebra instantly without waiting for slow multi-second LLM generations.

### C. Multi-Turn Counterfactual Simulation & Self-Correction Testing
- **Mechanism:** Injects synthetic `pytest` stderr failure traces and AST syntax errors into multi-turn step sequences in `lam.sqlite`.
- **Benefit:** Tests whether Vanguard's agentic turn loop (`EpisodeEngine`) correctly captures error tracebacks, formats alternating causal L5 history (`role: "assistant"`, `role: "tool"`), and emits refined patch proposals on subsequent turns.

### D. Hermetic Memory & Context Compaction Profiling
- **Mechanism:** Replays long 20-turn trajectories (100k+ token histories) through `vanguard/packages/agency/context/compiler.py`.
- **Benefit:** Benchmarks context-window eviction algorithms, token counting accuracy (Radix L1–L5 cache breakpoints), and LRU memory compaction overhead under zero-latency conditions (<2ms/turn).

---

## 7. Persistence, Telemetry & Analyzer Tools

- **SQLite Database:** [`tools/002_LLM_API_MOCK/lam.sqlite`](../lam.sqlite) (444 recorded mock calls / gold traces)
- **Harness Analyzer Report Generator:**
```bash
python3 -c "
from tools.002_LLM_API_MOCK.analyzer import HarnessAnalyzer
analyzer = HarnessAnalyzer()
print(analyzer.render_markdown_report())
"
```
- **KPI Log File:** [`tools/002_LLM_API_MOCK/docs/LAM_logs_benchmarking_KPIS_dont_commit.md`](LAM_logs_benchmarking_KPIS_dont_commit.md)
