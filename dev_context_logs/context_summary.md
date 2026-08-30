# 🧭 Executive Repository Context & Intelligence Packet (Tier 1)

> **Branch**: `feat/beta-release_electroweak-v091` | **HEAD**: `7d46c7f5528cf23a7b6cfcd6e02ece4d7f32e6a0`  
> **Tier-2 Raw Logs**: `dev_context_logs/` (100% granular evidence preserved)

---

## 1. System Gates & Invariants (`PASS`)
- **TCB Budget**: `1384` LOC across `9` files (Threshold $\le 1438$, Headroom: +54 LOC)
- **Boundary Checks**: 597 files checked, strict hexagonal flow enforced
- **Suite 1**: 97 tests passed in 0.562s (OK)
- **Suite 2**: 121 tests passed in 1.459s (OK)
- **Suite 3**: 416 tests passed in 8.565s (OK (skipped=6))
*Detailed log*: [`dev_context_logs/04_tests.txt`](dev_context_logs/04_tests.txt)

---

## 2. Hexagonal Architectural Topology
| Subsystem | Location | LOC | Files | Architectural Role |
|---|---|---|---|---|
| **Domain** | `vanguard/packages/domain` | 9,541 | 50 | Pure value objects & wire contracts |
| **Ports** | `vanguard/packages/ports` | 1,510 | 15 | Hexagonal port interfaces & SPI protocols |
| **Kernel** | `vanguard/packages/kernel` | 1,767 | 9 | TCB 13-stage dispatch & capability attenuation |
| **Agency** | `vanguard/packages/agency` | 3,388 | 15 | Turn loop, context compiler, subagent spawn |
| **Runtime** | `vanguard/packages/runtime` | 23,391 | 87 | Lifecycle, composition, SQLite event store |
| **Adapters** | `vanguard/packages/adapters` | 10,549 | 56 | Model adapters (OpenRouter/Ollama), bwrap sandbox |
*Detailed structural map*: [`dev_context_logs/10_code_map.txt`](dev_context_logs/10_code_map.txt)

---

## 3. Clustered Failure Signature Matrix
| Signature Pattern | Total Hits | Primary Area | Failure Remediation Focus |
|---|---|---|---|
| `NO_PATCH` | 129 | `benchmarks` | Benchmark failure signature tracking |
| `max_turns` | 89 | `vanguard` | Benchmark failure signature tracking |
| `malformed` | 81 | `vanguard` | Benchmark failure signature tracking |
| `abandoned` | 45 | `benchmarks` | Benchmark failure signature tracking |
| `COMPLETED` | 44 | `benchmarks` | Benchmark failure signature tracking |
| `DATASET_INVALID` | 38 | `benchmarks` | Benchmark failure signature tracking |
| `provider_error` | 1 | `benchmarks` | Benchmark failure signature tracking |
*Full 1.6MB raw grep log*: [`dev_context_logs/18_failure_evidence.txt`](dev_context_logs/18_failure_evidence.txt)

---

## 4. Deterministic Harness Baselines ($0 Spend)
- **LAM Simulation**: 36/36 gold scenarios simulated ($0.00 spend, deterministic replay)
  *Trace*: [`dev_context_logs/14_lam_simulation.txt`](dev_context_logs/14_lam_simulation.txt)
- **Frontier Benchmark**: Dry-run completed with zero paid LLM calls
  *Trace*: [`dev_context_logs/16_frontier_dryrun.txt`](dev_context_logs/16_frontier_dryrun.txt)

---

## 5. Read-Only Databases & Event Stores
| Database File | Tables | Key Table Row Counts |
|---|---|---|
| `benchmarks/frontier_v090/runs/tier1_lru_ttl_cache-vg-code-v090-react-control-9e64iiva/.vanguard/events.sqlite3` | 2 | `events` (244 rows), `sqlite_sequence` (1 rows) |
| `tools/002_LLM_API_MOCK/lam.sqlite` | 7 | `budget_events` (0 rows), `episodes` (9 rows), `mock_calls` (629 rows), `model_ceilings` (33 rows) |
*Full database schema dump*: [`dev_context_logs/13_sqlite_summary.txt`](dev_context_logs/13_sqlite_summary.txt)
