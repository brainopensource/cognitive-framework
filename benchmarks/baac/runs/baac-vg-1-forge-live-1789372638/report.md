# BaaC Evaluation Matrix — vg-1-forge (deepseek/deepseek-v4-flash-0731)
**Run ID**: `baac-vg-1-forge-live-1789372638` | **Mode**: `live` | **Date**: `2026-09-14T07:57:18Z`

| Challenge ID | Scope | Context | Tier | Status | Attribution | Turns | Tokens | Cost ($) | Duration | Diagnosis |
|---|---|---|---|---|---|---|---|---|---|---|
| `bench_greenfield_8K_tier-2_quiz_game` | `greenfield` | `8K` | `tier-2` | **FAIL** | `LLM_COGNITIVE_ERROR` | 10 | 23,725 | $0.00146 | 225.35s | test_quiz (__main__.TestQuiz.test_q |
| `bench_multi_8K_tier-2_json_todo_store` | `multi` | `8K` | `tier-2` | **UNDETERMINABLE** | `HARNESS_ERROR` | 10 | 17,021 | $0.00058 | 55.97s | test_todo (__main__.TestTodo.test_t |

## Summary KPIs
- **Overall Pass Rate**: 0/2 (0.0%)
- **TIER-2 Pass Rate**: 0/2 (0.0%)
- **Total Tokens**: 40,746
- **Total Cost**: $0.00204 USD
- **Total Duration**: 281.32s
- **Attribution Breakdown**: {'PASS': 0, 'LLM_COGNITIVE_ERROR': 1, 'HARNESS_ERROR': 1, 'BUDGET_EXHAUSTED': 0, 'DATASET_INVALID': 0}