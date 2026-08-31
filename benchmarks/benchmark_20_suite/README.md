# Benchmark 20 Suite (Vanguard Empirical Evaluation)

The **Benchmark 20 Suite** evaluates the Vanguard Harness and autonomous coding capabilities across 20 decoupled challenges (10 Brownfield + 10 Greenfield).

---

## 1. Centralized Model Configuration Policy

All benchmarks in Vanguard strictly adhere to the **Centralized Unified Model Registry** in [`vanguard/packages/adapters/models/config.py`](../../vanguard/packages/adapters/models/config.py) and [`vanguard/packages/adapters/models/models_registry.json`](../../vanguard/packages/adapters/models/models_registry.json).

- **No Hardcoded Literals**: Benchmark runners never declare model names directly in Python source code.
- **Fail-Closed Policy**: Any unlisted or disabled model alias is rejected with `ModelPolicyError`.
- **Authoritative Tiers & Pricing**: All token rates and model resolution flow through `resolve_model()` and `get_default_paid_model()`.

---

## 2. Dataset Structure

```text
benchmarks/benchmark_20_suite/
├── 01_rate_limiter_lease_recovery/       # Brownfield: Concurrency Governor capacity leak
├── 02_ed25519_signature_replay/          # Brownfield: Approval verifier timestamp/nonce
├── 03_trait_attenuation_escalation/      # Brownfield: Child capability escalation
├── 04_sqlite_wal_checkpoint_lock/        # Brownfield: SQLite WAL busy_timeout contention
├── 05_token_budget_clamping_drift/       # Brownfield: Float drift in TCB budget
├── 06_fts5_stale_index_rebuild/          # Brownfield: Cascade FTS5 symbol deletion
├── 07_context_lost_in_middle_prune/      # Brownfield: Context header & docstring retention
├── 08_evaluator_oracle_timeout/          # Brownfield: Sandbox process group SIGKILL & TIMEOUT
├── 09_model_port_streaming_chunk_drop/   # Brownfield: SSE EOF final buffer flush
├── 10_graph_ppr_dangling_node_sink/      # Brownfield: PPR dangling node mass redistribution
├── 11_kv_lru_ttl_store/                  # Greenfield: Thread-safe LRU + TTL Store
├── 12_finite_state_machine_workflow/     # Greenfield: Guarded Deterministic FSM
├── 13_semver_dependency_resolver/        # Greenfield: SemVer 2.0.0 Dependency Solver
├── 14_merkle_tree_ledger/                # Greenfield: Cryptographic Merkle Tree Ledger
├── 15_circuit_breaker_proxy/             # Greenfield: Resilient Circuit Breaker Proxy
├── 16_submodular_greedy_packer/          # Greenfield: Submodular Knapsack Feature Packer
├── 17_json_canonicalizer_jcs/            # Greenfield: RFC-8785 JSON Canonicalizer (JCS)
├── 18_token_bucket_hierarchical/         # Greenfield: Hierarchical Token Bucket Limiter
├── 19_markdown_section_splitter/         # Greenfield: Structured Markdown Chunker
├── 20_event_bus_pubsub_channel/          # Greenfield: PubSub Event Bus with DLQ
├── reset_suite.py                        # Cryptographic Reset & SHA-256 state verifier
├── runner.py                             # Execution Harness with centralized config
└── benchmark_20_results.json             # Empirical telemetry & evaluation matrix
```

---

## 3. Cryptographic State Reset & Replay

### Reset to Initial Broken State
```bash
python3 benchmarks/benchmark_20_suite/reset_suite.py
```
Validates SHA-256 digests against `initial_state.sha256` for all Brownfield challenges and clears Greenfield workspaces to guarantee zero cross-contamination.

### Hermetic Cassette Replay ($0.00 Cost)
All live LLM requests and responses are captured in `tools/002_LLM_API_MOCK/runs/benchmark_20_captures/` and `tools/002_LLM_API_MOCK/lam.sqlite`.
To verify hermetic replay:
```bash
python3 tools/002_LLM_API_MOCK/test_benchmark_20_replay.py
```
