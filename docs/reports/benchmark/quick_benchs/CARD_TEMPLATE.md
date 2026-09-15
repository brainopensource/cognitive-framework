# Benchmark Evaluation Card Template

Use one card per (challenge × harness × model × evidence_label) row.
Do not mix `REPLAY` / `LAM` / `LIVE-LOCAL` / `LIVE-HOSTED` into a single pass-rate.
Provider outage, HTTP error, missing credentials, or zero model calls → `not_run` (outside the quality denominator).
False-completion (`disposition=passed` with no patch / no oracle digest) vetoes every rate, lift, and cost claim.

```text
### Benchmark N: <challenge_id>

- Suite & Tier:
- Files in Challenge: <count> (<paths>)
- Gate Check: PASS | WARN | STATIC | FAIL — poisoning / leaked oracle / trivial assert / premature-green
- Initial Falsifier: RED | GREEN | TIMEOUT | NO_ORACLE — command + assertion
- Agent Capability: <manifest / skill / product path>
- Evidence Label: REPLAY | LIVE-LOCAL | LIVE-HOSTED
- Model Identity: <exact id, not openrouter/free> | provider | quant | ctx | sampling
- Falsifier Command:
- Result Quality: PASS | FAIL | ROLLBACK | UNDETERMINABLE | not_run
- Attribution: PASS | LLM_COGNITIVE_ERROR | HARNESS_ERROR | BUDGET_EXHAUSTED | DATASET_INVALID
- Output: changed files, unified diff digest / excerpt
- Latency: total_s | llm_s | lda_delta_s
- Tokens: prompt | completion | cached | total | tokens/s (wall-clock)
- Cache & Compression: KV cache_n | AST delta | context budget
- Turns: used / max | turn waste W | time to first valid write
- False-Completion: 0.0 required
- Rollback Fidelity: N/A | 100% byte-identical | diverged
- Cost: usd | local wall-clock proxy
```
