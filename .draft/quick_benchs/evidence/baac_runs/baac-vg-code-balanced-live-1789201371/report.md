# BaaC Evaluation Matrix — vg-code-balanced (deepseek/deepseek-v4-flash-0731)
**Run ID**: `baac-vg-code-balanced-live-1789201371` | **Mode**: `live` | **Date**: `2026-09-12T08:22:51Z`

| Challenge ID | Scope | Context | Tier | Status | Attribution | Turns | Tokens | Cost ($) | Duration | Diagnosis |
|---|---|---|---|---|---|---|---|---|---|---|
| `bench_single_2K_tier-1_calculator` | `single` | `2K` | `tier-1` | **PASS** | `PASS` | 8 | 12,972 | $0.00041 | 24.54s | All falsifiers green |
| `bench_single_2K_tier-1_fib_cli` | `single` | `2K` | `tier-1` | **PASS** | `PASS` | 8 | 12,251 | $0.00025 | 12.04s | All falsifiers green |
| `bench_single_2K_tier-1_string_dedupe` | `single` | `2K` | `tier-1` | **PASS** | `PASS` | 8 | 12,226 | $0.00035 | 24.53s | All falsifiers green |

## Summary KPIs
- **Overall Pass Rate**: 3/3 (100.0%)
- **TIER-1 Pass Rate**: 3/3 (100.0%)
- **Total Tokens**: 37,449
- **Total Cost**: $0.00100 USD
- **Total Duration**: 61.11s
- **Attribution Breakdown**: {'PASS': 3, 'LLM_COGNITIVE_ERROR': 0, 'HARNESS_ERROR': 0, 'BUDGET_EXHAUSTED': 0, 'DATASET_INVALID': 0}