# 🧭 Executive Repository Context & Intelligence Packet (Tier 1)

> **Branch**: `feat/aether-framework-electroweak-canonical-agents` | **HEAD**: `5224912f7fb121e0be2b723ffd2a6c605cfa9777`  
> **Tier-2 Raw Logs**: `dev_context_logs/` (100% granular evidence preserved)

---

## 1. System Gates & Invariants (`PASS`)
- **TCB Budget**: `N/A` LOC across `N/A` files (Threshold $\le 1438$, Headroom: +N/A LOC)
- **Boundary Checks**: 0 files checked, strict hexagonal flow enforced
*Detailed log*: [`dev_context_logs/04_tests.txt`](dev_context_logs/04_tests.txt)

---

## 2. Hexagonal Architectural Topology
| Subsystem | Location | LOC | Files | Architectural Role |
|---|---|---|---|---|
| **Domain** | `vanguard/packages/domain` | 10,634 | 55 | Pure value objects & wire contracts |
| **Ports** | `vanguard/packages/ports` | 1,582 | 15 | Hexagonal port interfaces & SPI protocols |
| **Kernel** | `vanguard/packages/kernel` | 1,769 | 9 | TCB 13-stage dispatch & capability attenuation |
| **Agency** | `vanguard/packages/agency` | 8,300 | 27 | Turn loop, context compiler, subagent spawn |
| **Runtime** | `vanguard/packages/runtime` | 27,074 | 93 | Lifecycle, composition, SQLite event store |
| **Adapters** | `vanguard/packages/adapters` | 12,350 | 61 | Model adapters (OpenRouter/Ollama), bwrap sandbox |
*Detailed structural map*: [`dev_context_logs/10_code_map.txt`](dev_context_logs/10_code_map.txt)

---

## 3. Clustered Failure Signature Matrix
| Signature Pattern | Total Hits | Primary Area | Failure Remediation Focus |
|---|---|---|---|
| `max_turns` | 531 | `benchmarks` | Benchmark failure signature tracking |
| `NO_PATCH` | 185 | `benchmarks` | Benchmark failure signature tracking |
| `abandoned` | 157 | `benchmarks` | Benchmark failure signature tracking |
| `DATASET_INVALID` | 128 | `benchmarks` | Benchmark failure signature tracking |
| `malformed` | 116 | `vanguard` | Benchmark failure signature tracking |
| `COMPLETED` | 109 | `benchmarks` | Benchmark failure signature tracking |
| `provider_error` | 4 | `benchmarks` | Benchmark failure signature tracking |
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
| `.lda/index.db` | 14 | `doc_sections` (6146 rows), `documents` (297 rows), `entities` (13533 rows), `files` (2099 rows) |
| `.vanguard/events.sqlite3` | 2 | `events` (33500 rows), `sqlite_sequence` (1 rows) |
| `.vanguard/runtime.db` | 6 | `active_runs` (4 rows), `checkpoints` (0 rows), `command_inbox` (17 rows), `event_outbox` (0 rows) |
| `tools/002_LLM_API_MOCK/lam.sqlite` | 7 | `budget_events` (0 rows), `episodes` (9 rows), `mock_calls` (965 rows), `model_ceilings` (33 rows) |
*Full database schema dump*: [`dev_context_logs/13_sqlite_summary.txt`](dev_context_logs/13_sqlite_summary.txt)
