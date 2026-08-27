# Master Benchmark & Autonomous Coding Qualification Guide for AETHER / Vanguard

## 1. Title & Purpose
**Purpose:** Evaluating LLMs on multi-turn autonomous coding tasks across 7 difficulty tiers with immutable SQLite-WAL auditability.

This benchmark suite rigorously tests an LLM's capacity to understand complex codebases, synthesize accurate edits, handle edge cases, and autonomously correct itself across a wide array of technical domains, spanning from basic algorithms to consensus protocols and compiler design. All execution and validation logs are cryptographically tracked using an immutable SQLite-WAL mechanism to guarantee reproducibility and auditability.

---

## 2. The 20 Tiered Benchmark Challenges Index

The benchmark suite consists of 20 distinct challenges spread across 7 difficulty tiers. These are sourced and orchestrated via `benchmarks/swe_bench/challenges.py`.

### **Tier 1 (Elementary / 1-File Fixes)**
- `tier1_lru_ttl_cache`: Implementing a time-aware LRU cache.
- `tier1_ring_buffer_stream`: Managing circular buffer streams.
- `tier1_version_semver_parser`: Parsing and validating semantic version strings.

### **Tier 2 (Event & State Machines)**
- `tier2_event_bus`: Constructing a pub/sub event bus mechanism.
- `tier2_fsm_workflow_engine`: Managing state transitions and workflow logic.
- `tier2_retry_exponential_backoff`: Implementing fault-tolerant retry logic.
- `tier2_web_reactive_signals`: Creating reactive primitives for web components.

### **Tier 3 (Concurrency & Invariants)**
- `tier3_token_bucket`: Rate-limiting implementation using the token bucket algorithm.
- `tier3_rw_lock_priority`: Managing read/write locks with priority queueing.
- `tier3_connection_pool`: Creating an efficient database/resource connection pool.
- `tier3_api_idempotency_middleware`: Ensuring safe retries across distributed APIs.

### **Tier 4 (Graph Algorithms & Routing)**
- `tier4_dag_resolver`: Resolving dependency graphs and detecting cycles.
- `tier4_trie_prefix_router`: Building high-performance route matching engines.
- `tier4_stream_window_aggregator`: Calculating real-time aggregates over stream windows.
- `tier4_web_vdom_reconciler`: Implementing a virtual DOM diffing algorithm.

### **Tier 5 (AST Parsers & Compilers)**
- `tier5_jsonpath_query_compiler`: Compiling JSONPath queries into executable plans.
- `tier5_datalog_engine`: Creating a minimal logic programming engine.
- `tier5_sql_micro_planner`: Implementing query planning and optimization.
- `tier5_ds_autograd_engine`: Building automatic differentiation for neural networks.

### **Tier 6 (Distributed Systems & Consensus)**
- `tier6_vector_clock_causality`: Managing logical time in distributed environments.
- `tier6_raft_state_machine`: Implementing leader election and log replication logic.
- `tier6_gossip_membership`: Creating peer-to-peer membership protocols.

### **Tier 7 (Greenfield & Storage Engines)**
- `tier7_greenfield_kv_lsm_tree`: Building a log-structured merge-tree key-value store from scratch.
- `tier7_greenfield_bytecode_vm`: Constructing a custom bytecode interpreter.
- `tier7_hle_zk_poly_commitment_verifier`: Implementing zero-knowledge cryptographic primitives.

---

## 3. How to Run & Reproduce (CLI Commands)

The benchmark execution is managed via the internal runner script.

**Execute a Single Challenge:**
```bash
python3 tools/runners/run_swe_challenge.py --challenge tier3_connection_pool --model z-ai/glm-5.3-flash
```

**Execute an Entire Tier Suite:**
```bash
python3 tools/runners/run_swe_challenge.py --tiers 1,2,3 --model "openrouter/free"
```

**Retain Debug Artifacts for Post-Mortem Analysis:**
Append the `--keep-dir` flag to prevent the sandbox environment from being wiped after completion.
```bash
python3 tools/runners/run_swe_challenge.py --challenge tier6_raft_state_machine --model z-ai/glm-5.3-flash --keep-dir
```

---

## 4. Multi-Model Verified Scoreboard

| Model | Tested Tiers | Challenges Run | Avg Turns | Avg Tokens | Avg Time (s) | Cost ($) | Oracle Pass Rate |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| `z-ai/glm-5.3-flash` | **T4, T5, T6, T7** | `dag_resolver`, `jsonpath_compiler`, `vector_clock`, `kv_lsm_tree` | 7.5 | 35,975 | 110.0s | < $0.03 | **100% (4/4)** |
| `openrouter/free` | **T1, T2, T3** | `ring_buffer_stream`, `retry_exponential_backoff`, `token_bucket` | 5.0 | 22,598 | 94.7s | $0.00 | **100% (3/3)** |
| `minimax/minimax-m3:free` | **T6, T7** | `vector_clock_causality`, `greenfield_kv_lsm_tree` | 20.0 | 73,892 | 203.3s | $0.00 | **100% (2/2)** |
| `thinkingmachines/inkling:free` | **T4, T7** | `dag_resolver`, `greenfield_kv_lsm_tree` | 0.0 | 0 | 6.1s | $0.00 | **0% (0/2 - HTTP 403)** |

---

## 5. Telemetry, KPIs & Time Distribution Audit

The benchmark runner aggressively profiles execution to identify bottlenecks in the autonomous agent loop. 

### **Full Time Split Analysis:**
1. **LLM Network Wait Time:** $\approx 76.3\%$ 
2. **Harness Git Diff / Workspace Prep:** $\approx 23.5\%$
3. **TCB Kernel S0-S12 & Local Tool Dispatch:** $0.2\%$

### **Complete KPI Table:**
| KPI Metric | Average Value |
| :--- | :--- |
| **Tokens per Challenge** | ~30,000 |
| **Turns per Challenge** | ~6.4 |
| **Pure Kernel Latency** | ~18ms |
| **In-Memory Throughput** | ~42,000 tok/s |

---

## 6. Rust Acceleration Projection & Architecture Roadmap

Currently, the workspace preparation and diffing engine consume roughly **23.5%** of execution time. This is primarily driven by Python subprocess calls to the `git` CLI and native Python AST parsing logic.

**Roadmap Initiative:** 
Replace Python Git CLI and AST parsing with Rust native PyO3 modules leveraging `libgit2` and `Tree-sitter`.

**Projected Impact:**
- **Per-Turn Harness Overhead:** Reduction from $2.46\text{s}$ down to $\approx 0.02\text{s} - 0.1\text{s}$.
- **Harness Latency Reduction:** $>90\%$ improvement.
- **Total Task Speedup:** Average task duration projected to drop from $103.5\text{s}$ to $\approx 79.5\text{s}$.

*Conclusion:* This transition makes the agent framework almost **100% bound solely by model streaming speed**, pushing systemic overhead towards negligible thresholds.

---

## 7. How the Autonomous Cognitive Loop Works (Technical Lifecycle)

The execution loop follows a strict, verifiable lifecycle ensuring deterministic and secure behavior:

1. **Workspace Isolation:** A clean, ephemeral chroot/jail-style directory is created for the challenge.
2. **Context Assembly:** The harness builds the initial prompt containing the challenge specification and repository topology.
3. **Model Proposal:** The LLM generates a chain-of-thought and proposes discrete tool actions (e.g., editing files, running tests).
4. **Kernel S0-S12 Gate:** The proposal is routed through the Trusted Computing Base (TCB) where it undergoes 13 security and budget checks (S0-S12), signed by an Ed25519 verifiable key.
5. **Tool Execution:** Approved tools are executed within the isolated workspace.
6. **Multi-Turn Self-Correction Feedback:** Output from tool execution (e.g., test failures, lint errors) is fed back into the context. The model iterates and self-corrects based on this feedback.
7. **Test Oracle Scoring:** Once the model yields or exhausts its turn budget, the hidden test suite (the oracle) is run against the final codebase.
8. **SQLite-WAL Immutability:** The entire chain—proposals, diffs, kernel approvals, and oracle scores—is finalized and appended to the immutable SQLite Write-Ahead Log.
