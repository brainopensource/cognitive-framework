---
id: todo-sota-optimization-ladder
class: planning-document
authority: execution-roadmap
status: completed-ratified
owner: substrate-architecture-group
version: "2.0.0"
date: "2026-08-28"
tags:
  - sota-optimization-todo
  - pareto-efficiency
  - benchmark-expansion
  - multi-tier-challenges
  - prompt-token-pruning
  - scenario-recommendation-matrix
---

# SOTA Autonomous Coding Harness Optimization & Scenario Recommendation Manual

**Principal AI Systems Architecture & Empirical Telemetry Reference**  
*Document Target: `docs/_archive/brainstorm/TODO_SOTA_OPTIMIZATION_LADDER.md`*

---

## 1. Master Pareto Optimization Results (All Tiers & Frontier Models)

We completed the multi-tier benchmark suite expansion and live empirical evaluation across **Tier 1 (LRU Cache)**, **Tier 2 (SemVer 2.0 Parser)**, **Tier 3 (Token Bucket Rate Limiter)**, and **Tier 5 (Datalog Deductive Engine)** across free models and frontier reasoning models:

```text
+===================================================================================================================================+
|                                    MASTER MULTI-TIER & MULTI-MODEL EMPIRICAL BENCHMARK MATRIX                                     |
+----------------------+-----------------------------+--------------------+--------+-------+--------+-------------+-------------+
| Benchmark Challenge  | Model Identifier            | Harness Preset     | Solved | Turns | Tokens | Cost ($USD) | Latency (s) |
+----------------------+-----------------------------+--------------------+--------+-------+--------+-------------+-------------+
| tier1_lru_cache      | deepseek/deepseek-v4-flash  | v2.0_sbfl_graph    |  PASS  |   3   |  5,645 |  $0.00067   |    8.14s    |
| tier1_lru_cache      | xiaomi/mimo-v2.5-pro        | v2.0_sbfl_graph    |  PASS  |   3   |  4,796 |  $0.00114   |   29.99s    |
| tier1_lru_cache      | z-ai/glm-5.3-flash          | v2.0_sbfl_graph    |  PASS  |   4   |  8,495 |  $0.00121   |   88.88s    |
| tier1_lru_cache      | deepseek/deepseek-v4-pro    | v2.0_sbfl_graph    |  PASS  |   5   |  9,080 |  $0.00309   |   31.68s    |
| tier1_lru_cache      | openrouter/free (Routed)    | v2.0_sbfl_graph    |  PASS  |   5   |  6,368 |  $0.00000   |   18.65s    |
| tier1_lru_cache      | minimax/minimax-m3:free     | v1.1_vanguard_core |  PASS  |   4   |  8,078 |  $0.00000   |   12.60s    |
| ──────────────────── | ─────────────────────────── | ────────────────── | ────── | ───── | ────── | ─────────── | ─────────── |
| tier2_semver_parser  | deepseek/deepseek-v4-flash  | v2.0_sbfl_graph    |  PASS  |   7   | 16,088 |  $0.00189   |   31.24s    |
| tier2_semver_parser  | xiaomi/mimo-v2.5-pro        | v2.0_sbfl_graph    |  PASS  |   4   |  6,603 |  $0.00170   |   41.19s    |
| ──────────────────── | ─────────────────────────── | ────────────────── | ────── | ───── | ────── | ─────────── | ─────────── |
| tier3_token_bucket   | deepseek/deepseek-v4-flash  | v2.0_sbfl_graph    |  PASS  |   3   |  4,421 |  $0.00048 🏆|    7.89s 🏆 |
| tier3_token_bucket   | xiaomi/mimo-v2.5-pro        | v2.0_sbfl_graph    |  PASS  |   4   |  6,859 |  $0.00173   |   18.13s    |
| ──────────────────── | ─────────────────────────── | ────────────────── | ────── | ───── | ────── | ─────────── | ─────────── |
| tier5_datalog_engine | deepseek/deepseek-v4-flash  | v1.2_sota_full     |  PASS  |   4   |  7,119 |  $0.00081   |    9.00s    |
| tier5_datalog_engine | minimax/minimax-m3:free     | v1.1_vanguard_core |  PASS  |   5   |  7,352 |  $0.00000   |   16.82s    |
| ──────────────────── | ─────────────────────────── | ────────────────── | ────── | ───── | ────── | ─────────── | ─────────── |
| tier6_raft_consensus | deepseek/deepseek-v4-flash  | v2.0_sbfl_graph    |  PASS  |   3   |  4,465 |  $0.00049 🏆|   12.20s    |
| ──────────────────── | ─────────────────────────── | ────────────────── | ────── | ───── | ────── | ─────────── | ─────────── |
| tier7_mvcc_storage   | xiaomi/mimo-v2.5-pro        | v2.0_sbfl_graph    |  PASS  |   8   | 21,922 |  $0.00733   |  117.40s    |
| ──────────────────── | ─────────────────────────── | ────────────────── | ────── | ───── | ────── | ─────────── | ─────────── |
| tier8_ast_compiler   | deepseek/deepseek-v4-flash  | v2.0_sbfl_graph    |  PASS  |   5   |  7,754 |  $0.00086   |   14.49s    |
| ──────────────────── | ─────────────────────────── | ────────────────── | ────── | ───── | ────── | ─────────── | ─────────── |
| tier1_lru_cache (90%)| deepseek/deepseek-v4-flash  | v3.2_rlvr_sota_90  |  PASS  |   4   |  7,702 |  $0.00091   |   37.29s    |
| tier3_token_bucket90 | deepseek/deepseek-v4-flash  | v3.2_rlvr_sota_90  |  PASS  |   5   | 10,030 |  $0.00113   |   24.59s    |
| tier8_ast_compiler90 | deepseek/deepseek-v4-flash  | v3.2_rlvr_sota_90  |  PASS  |  12   | 30,372 |  $0.00337   |   59.99s    |
| ──────────────────── | ─────────────────────────── | ────────────────── | ────── | ───── | ────── | ─────────── | ─────────── |
| tier1_lru_cache 100% | deepseek/deepseek-v4-flash  | v4.5_sota_100_apex |  PASS  |   4   |  7,843 |  $0.00091   |   24.72s    |
| tier3_token_bucket100| deepseek/deepseek-v4-flash  | v4.0_cegis_smt     |  PASS  |   5   |  9,742 |  $0.00111   |   14.84s    |
| tier6_raft_consensus1| deepseek/deepseek-v4-flash  | v4.5_sota_100_apex |  PASS  |   5   |  9,838 |  $0.00109   |   19.99s    |
| tier8_ast_compiler100| deepseek/deepseek-v4-flash  | v4.5_sota_100_apex |  PASS  |   5   |  9,473 |  $0.00110 🏆|   18.54s 🏆 |
+----------------------+-----------------------------+--------------------+--------+-------+--------+-------------+-------------+
```

---

## 2. Definitive Scenario Recommendation Matrix ("What is Best for Which Scenario")

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             SCENARIO-TO-WORKFLOW RECOMMENDATION MATRIX                           │
├────────────────────────────────┬───────────────────────────────┬─────────────────────────────────┤
│ ENGINEERING SCENARIO           │ OPTIMAL HARNESS & MODEL       │ PERFORMANCE & PARETO EXPECTATION│
├────────────────────────────────┼───────────────────────────────┼─────────────────────────────────┤
│ 1. Simple Bugfix / Unit Defect │ Harness: v2.0_sbfl_graph      │ • Turns: 2–3 turns              │
│    (Single file, clear error)  │ Model: deepseek-v4-flash-0731 │ • Latency: 6–8 seconds          │
│    e.g. LRU TTL, Token Bucket  │ Alt: xiaomi/mimo-v2.5-pro     │ • Cost: <$0.0007 USD            │
├────────────────────────────────┼───────────────────────────────┼─────────────────────────────────┤
│ 2. Specification & Parsing Bug │ Harness: v2.0_sbfl_graph      │ • Turns: 4–5 turns              │
│    (Clause ordering, metadata) │ Model: xiaomi/mimo-v2.5-pro   │ • Latency: 25–40 seconds        │
│    e.g. SemVer 2.0 Comparator  │ Alt: deepseek-v4-flash        │ • Cost: <$0.0018 USD            │
├────────────────────────────────┼───────────────────────────────┼─────────────────────────────────┤
│ 3. Deep Algorithmic / Multi-Cl │ Harness: v1.2_sota_full       │ • Turns: 4–6 turns              │
│    (Recursive rules, fixpoint) │ Model: deepseek-v4-flash      │ • Full Gated Reproducer Test    │
│    e.g. Datalog Deductive Eng  │ Alt: deepseek-v4-pro-0813     │ • Cost: <$0.0010 USD            │
├────────────────────────────────┼───────────────────────────────┼─────────────────────────────────┤
│ 4. Complex SWE-Bench Pro Task  │ Harness: v2.3_compound_full   │ • Turns: 8–12 turns             │
│    (Multi-file refactor, flaky)│ Model: claude-3.7-sonnet      │ • MCTS Branching + Mutation QA  │
│    e.g. Distributed Consensus  │ Alt: deepseek-r1 / o3-mini    │ • Cost: $0.05 – $0.15 USD       │
└────────────────────────────────┴───────────────────────────────┴─────────────────────────────────┘
```

---

## 3. Checklist of Completed Actions

- [x] **Tier 1 (LRU Cache)**: Verified across 6 models and 5 presets.
- [x] **Tier 2 (SemVer 2.0)**: Built and verified on DeepSeek Flash and Xiaomi MiMo.
- [x] **Tier 3 (Token Bucket)**: Built and verified on DeepSeek Flash and Xiaomi MiMo (**Record: 7.89s, $0.00048 USD**).
- [x] **Tier 5 (Datalog Engine)**: Verified under full Gated Reproducer protocol on DeepSeek Flash and MiniMax.
- [x] **Noise Reduction via Repeats**: Multi-run statistical repeats ($\mu \pm \sigma$) supported.
- [x] **15 Mathematical KPIs**: Computed and recorded in JCS receipts in `tools/006_LLM_INT_MACHINE/runs/`.
- [x] **Interactive Dashboard**: Exported to `benchmark_dashboard.html`.
