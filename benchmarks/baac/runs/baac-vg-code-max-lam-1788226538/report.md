# BaaC Evaluation Matrix — vg-code-max (lam-mock)
**Run ID**: `baac-vg-code-max-lam-1788226538` | **Mode**: `lam` | **Date**: `2026-09-01T01:35:38Z`

| Challenge ID | Scope | Context | Tier | Status | Attribution | Turns | Tokens | Cost ($) | Duration | Diagnosis |
|---|---|---|---|---|---|---|---|---|---|---|
| `bench_single_2K_tier-1_calculator` | `single` | `2K` | `tier-1` | **PASS** | `PASS` | 10 | 1,900 | $0.00000 | 0.12s | All falsifiers green |
| `bench_single_2K_tier-1_fib_cli` | `single` | `2K` | `tier-1` | **PASS** | `PASS` | 10 | 1,900 | $0.00000 | 0.12s | All falsifiers green |
| `bench_single_2K_tier-1_string_dedupe` | `single` | `2K` | `tier-1` | **PASS** | `PASS` | 10 | 1,900 | $0.00000 | 0.11s | All falsifiers green |
| `bench_greenfield_8K_tier-2_quiz_game` | `greenfield` | `8K` | `tier-2` | **PASS** | `PASS` | 10 | 1,900 | $0.00000 | 0.13s | All falsifiers green |
| `bench_multi_8K_tier-2_json_todo_store` | `multi` | `8K` | `tier-2` | **PASS** | `PASS` | 10 | 1,900 | $0.00000 | 0.14s | All falsifiers green |
| `bench_multi_16K_tier-3_event_bus` | `multi` | `16K` | `tier-3` | **PASS** | `PASS` | 10 | 1,900 | $0.00000 | 0.13s | All falsifiers green |
| `bench_multi_32K_tier-4_circuit_breaker` | `multi` | `32K` | `tier-4` | **PASS** | `PASS` | 10 | 1,900 | $0.00000 | 0.14s | All falsifiers green |
| `bench_multi_64K_tier-5_immutable_trie` | `multi` | `64K` | `tier-5` | **PASS** | `PASS` | 10 | 1,900 | $0.00000 | 0.14s | All falsifiers green |
| `bench_multi_128K_tier-6_mvcc_db` | `multi` | `128K` | `tier-6` | **PASS** | `PASS` | 10 | 1,900 | $0.00000 | 0.11s | All falsifiers green |

## Summary KPIs
- **Overall Pass Rate**: 9/9 (100.0%)
- **TIER-1 Pass Rate**: 3/3 (100.0%)
- **TIER-2 Pass Rate**: 2/2 (100.0%)
- **TIER-3 Pass Rate**: 1/1 (100.0%)
- **TIER-4 Pass Rate**: 1/1 (100.0%)
- **TIER-5 Pass Rate**: 1/1 (100.0%)
- **TIER-6 Pass Rate**: 1/1 (100.0%)
- **Total Tokens**: 17,100
- **Total Cost**: $0.00000 USD
- **Total Duration**: 1.14s
- **Attribution Breakdown**: {'PASS': 9, 'LLM_COGNITIVE_ERROR': 0, 'HARNESS_ERROR': 0, 'BUDGET_EXHAUSTED': 0, 'DATASET_INVALID': 0}