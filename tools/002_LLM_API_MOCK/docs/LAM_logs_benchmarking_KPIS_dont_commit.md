# Spend ledger — DO NOT COMMIT

Total budget: 0.50 USD
Spent: 0.00 USD
Remaining: 0.50 USD
Accounting: every 10 LLM calls = 0.05 USD (this agent session + outbound OpenRouter completions)
Wave: 1
LLM calls this wave: 4
  - 1 Cursor agent turn (this LAM build)
  - 3 OpenRouter free completions (T1 one-liner)

## Log

- 2026-08-16T01:39:00-03:00  opened wave 1  remaining=0.50
- 2026-08-16T02:10:00-03:00  calls=4  no debit yet (debit every 10)  remaining=0.50
- OpenRouter free T1 probe (actual provider billed $0 on :free ids):
  - nvidia/nemotron-3-super-120b-a12b:free  ok  5.2s  106 tokens  `def add(a,b): return a+b`  fits T1
  - nvidia/nemotron-3.5-lightning:free  ok  1.4s  271 tokens  hit max_tokens on a think-trace  weak T1 hygiene
  - cohere/north-mini-code:free  ok  4.9s  87 tokens  `def add(a,b): return a+b`  fits T1
- Paid medium/high/top not fired this wave (protect the $0.50 cap; 3 top ids were never named). Next wave can ping them.

## LAM (zero-cost) tier cascade — as-if Sonnet USD

| tier | scenario | llm_calls | total_tokens | avg tok/call | LAM USD | if-sonnet USD | avg $/call | wall_ms |
|------|----------|-----------|--------------|--------------|---------|---------------|------------|---------|
| 1 | t1-calculator | 4 | 1263 | 315.8 | 0 | 0.006837 | 0.001709 | ~17 |
| 2 | t2-two-files | 4 | 1593 | 398.2 | 0 | 0.008115 | 0.002029 | ~17 |
| 3 | t3-context-layers | 4 | 2092 | 523.0 | 0 | 0.010668 | 0.002667 | ~16 |
| 4 | t4-feature-todos | 7 | 4668 | 666.9 | 0 | 0.020844 | 0.002978 | ~17 |
| 5 | t5-extract-module | 8 | 7387 | 923.4 | 0 | 0.030849 | 0.003856 | ~17 |

LAM total for all 5 tiers: 27 calls, 17003 tokens, 0.00 USD, ~0.077 as-if-sonnet, <20ms each.

When this file hits Spent=0.50 / Remaining=0.00, stop paid calls and revert to Ollama + this refinements log.
