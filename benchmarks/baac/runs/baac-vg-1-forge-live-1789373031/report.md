# BaaC Evaluation Matrix — vg-1-forge (deepseek/deepseek-v4-flash-0731)
**Run ID**: `baac-vg-1-forge-live-1789373031` | **Mode**: `live` | **Date**: `2026-09-14T08:03:51Z`

| Challenge ID | Scope | Context | Tier | Status | Attribution | Turns | Tokens | Cost ($) | Duration | Diagnosis |
|---|---|---|---|---|---|---|---|---|---|---|
| `bench_greenfield_8K_tier-2_quiz_game` | `greenfield` | `8K` | `tier-2` | **FAIL** | `LLM_COGNITIVE_ERROR` | 10 | 28,724 | $0.00189 | 139.44s | test_quiz (__main__.TestQuiz.test_q |
| `bench_multi_8K_tier-2_json_todo_store` | `multi` | `8K` | `tier-2` | **FAIL** | `LLM_COGNITIVE_ERROR` | 10 | 19,923 | $0.00119 | 100.21s | test_todo (__main__.TestTodo.test_t |

## Summary KPIs
- **Overall Pass Rate**: 0/2 (0.0%)
- **TIER-2 Pass Rate**: 0/2 (0.0%)
- **Total Tokens**: 48,647
- **Total Cost**: $0.00308 USD
- **Total Duration**: 239.65s
- **Attribution Breakdown**: {'PASS': 0, 'LLM_COGNITIVE_ERROR': 2, 'HARNESS_ERROR': 0, 'BUDGET_EXHAUSTED': 0, 'DATASET_INVALID': 0}