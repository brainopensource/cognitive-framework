---
id: research.ai-openrouter-llm-models-suggested
kind: research
status: reference
authority: non-canonical
summary: "SOTA reference guide and suggestions for OpenRouter LLM models."
topic:
  - ai-models
---
# OpenRouter LLM Models: Suggested SOTA Reference

## 0. Free Models

- openrouter/free
- minimax/minimax-m3:free
- z-ai/glm-5.2:free
- inclusionai/ling-3.0-tiny:free
- poolside/laguna-s-2.1:free
- cohere/north-mini-code:free
- google/gemma-4-26b-a4b-it:free
- nvidia/nemotron-3-super-120b-a12b:free
- openai/gpt-oss-20b:free

## 1. Verified Low-Cost Paid Models

- qwen/qwen3.7-flash
- qwen/qwen3.6-35b-a3b
- deepseek/deepseek-v4-flash-0731 (v2 coding)
- deepseek/deepseek-v4-flash (v2 0423)
- z-ai/glm-5.3-flash
- openai/gpt-5.6-luna
- qwen/qwen3.8-27b
- stepfun/step-3.7-flash
- xiaomi/mimo-v2.5
- xiaomi/mimo-v2.5-pro
- minimax/minimax-m3
- tencent/hy3-preview
- upstage/solar-pro4
- moonshotai/kimi-k2.7-code

## 2. Great Paid Models

- google/gemini-3.8-flash
- deepseek/deepseek-v4-pro
- moonshotai/kimi-k3
- z-ai/glm-5.3
- qwen/qwen3.8-max
- meta/muse-spark-1.2

## 3. Elite Top Models

- openai/gpt-5.6-sol


- deepseek-coder-v2:16b-instruct-q5

### IQ Tier Benchmarks

| IQ | Capability Tier | Real OpenRouter Model | Real ms | LAM ms | Real Cost | Parity Score |
|----|-----------------|-----------------------|---------|--------|-----------|--------------|
| IQ 0 | SWE Basics | `openrouter/free` | 3792 ms | 0.10 ms | $0.000000 | 90 / 100 |
| IQ 1 | SWE Easy | `poolside/laguna-s-2.1:free` | 15977 ms | 0.09 ms | $0.000000 | 90 / 100 |
| IQ 2 | SWE Medium | `nvidia/nemotron-3-super-120b-a12b:free` | 1453 ms | 0.09 ms | $0.000000 | 95 / 100 |
| IQ 3 | SWE Advanced | `stealth/ox-alpha` | 3479 ms | 0.07 ms | $0.000000 | 95 / 100 |
| IQ 4 | SWE Pro Entry | `deepseek/deepseek-v4-flash` | 3386 ms | 0.07 ms | $0.000059 | 95 / 100 |
| IQ 5 | SWE Pro Hard | `openai/gpt-5.6-luna` | 2363 ms | 0.07 ms | $0.000068 | 95 / 100 |

### Capability Tier Benchmarks

| Tier | Capability Tier | Real OpenRouter Model | Real ms | LAM ms | Real Cost | Parity Score |
|------|-----------------|----------------------|---------|--------|-----------|--------------|
| Tier 0 | SWE Basics | `openrouter/free` | 27348 ms | 0.08 ms | $0.000000 | 98 / 100 |
| Tier 1 | SWE Easy | `poolside/laguna-s-2.1:free` | 5833 ms | 0.07 ms | $0.000000 | 98 / 100 |
| Tier 2 | SWE Medium | `nvidia/nemotron-3-super-120b-a12b:free` | 1270 ms | 0.06 ms | $0.000000 | 98 / 100 |
| Tier 3 | SWE Advanced | `stealth/ox-alpha` | 7540 ms | 0.05 ms | $0.000000 | 98 / 100 |
| Tier 4 | SWE Complex | `deepseek/deepseek-v4-flash` | 5406 ms | 0.05 ms | $0.000082 | 98 / 100 |
| Tier 5 | SWE Concurrency | `deepseek/deepseek-v4-flash` | 4679 ms | 0.05 ms | $0.000090 | 98 / 100 |
| Tier 6 | SWE Consensus | `stealth/ox-alpha` | 2905 ms | 0.05 ms | $0.000000 | 98 / 100 |
| Tier 7 | Pro Entry | `stealth/ox-alpha` | 13117 ms | 0.06 ms | $0.000000 | 93 / 100 |
| Tier 8 | Pro Mid | `stealth/ox-alpha` | 12520 ms | 0.05 ms | $0.000000 | 98 / 100 |
| Tier 9 | Pro Hard | `openai/gpt-5.6-luna` | 2743 ms | 0.07 ms | $0.000068 | 98 / 100 |
| Tier 10 | Pro Frontier | `openai/gpt-5.6-luna` | 2116 ms | 0.05 ms | $0.000117 | 93 / 100 |







   ┌──────┬──────────────────┬──────────────────────────────────────────┬──────────┬───────────┬──────────────┬──────────────┐
    │ IQ   │ Capability Tier  │ Real OpenRouter Model                    │ Real ms  │ LAM ms    │ Real Cost    │ Parity Score │
    ├──────┼──────────────────┼──────────────────────────────────────────┼──────────┼───────────┼──────────────┼──────────────┤
    │ IQ 0 │ SWE Basics       │ `openrouter/free`                        │ 3792 ms  │ 0.10 ms   │ $0.000000    │ 90 / 100     │
    │ IQ 1 │ SWE Easy         │ `poolside/laguna-s-2.1:free`             │ 15977 ms │ 0.09 ms   │ $0.000000    │ 90 / 100     │
    │ IQ 2 │ SWE Medium       │ `nvidia/nemotron-3-super-120b-a12b:free` │ 1453 ms  │ 0.09 ms   │ $0.000000    │ 95 / 100     │
    │ IQ 3 │ SWE Advanced     │ `stealth/ox-alpha`                       │ 3479 ms  │ 0.07 ms   │ $0.000000    │ 95 / 100     │
    │ IQ 4 │ SWE Pro Entry    │ `deepseek/deepseek-v4-flash`             │ 3386 ms  │ 0.07 ms   │ $0.000059    │ 95 / 100     │
    │ IQ 5 │ SWE Pro Hard     │ `openai/gpt-5.6-luna`                    │ 2363 ms  │ 0.07 ms   │ $0.000068    │ 95 / 100     │
    └──────┴──────────────────┴──────────────────────────────────────────┴──────────┴───────────┴──────────────┴──────────────┘



    ┌─────────┬──────────────────┬──────────────────────────────────────────┬───────────┬───────────┬──────────────┬──────────────┐
    │ Tier    │ Capability Tier  │ Real OpenRouter Model                    │ Real ms   │ LAM ms    │ Real Cost    │ Parity Score │
    ├─────────┼──────────────────┼──────────────────────────────────────────┼───────────┼───────────┼──────────────┼──────────────┤
    │ Tier 0  │ SWE Basics       │ `openrouter/free`                        │ 27348 ms  │ 0.08 ms   │ $0.000000    │ 98 / 100     │
    │ Tier 1  │ SWE Easy         │ `poolside/laguna-s-2.1:free`             │ 5833 ms   │ 0.07 ms   │ $0.000000    │ 98 / 100     │
    │ Tier 2  │ SWE Medium       │ `nvidia/nemotron-3-super-120b-a12b:free` │ 1270 ms   │ 0.06 ms   │ $0.000000    │ 98 / 100     │
    │ Tier 3  │ SWE Advanced     │ `stealth/ox-alpha`                       │ 7540 ms   │ 0.05 ms   │ $0.000000    │ 98 / 100     │
    │ Tier 4  │ SWE Complex      │ `deepseek/deepseek-v4-flash`             │ 5406 ms   │ 0.05 ms   │ $0.000082    │ 98 / 100     │
    │ Tier 5  │ SWE Concurrency  │ `deepseek/deepseek-v4-flash`             │ 4679 ms   │ 0.05 ms   │ $0.000090    │ 98 / 100     │
    │ Tier 6  │ SWE Consensus    │ `stealth/ox-alpha`                       │ 2905 ms   │ 0.05 ms   │ $0.000000    │ 98 / 100     │
    │ Tier 7  │ Pro Entry        │ `stealth/ox-alpha`                       │ 13117 ms  │ 0.06 ms   │ $0.000000    │ 93 / 100     │
    │ Tier 8  │ Pro Mid          │ `stealth/ox-alpha`                       │ 12520 ms  │ 0.05 ms   │ $0.000000    │ 98 / 100     │
    │ Tier 9  │ Pro Hard         │ `openai/gpt-5.6-luna`                    │ 2743 ms   │ 0.07 ms   │ $0.000068    │ 98 / 100     │
    │ Tier 10 │ Pro Frontier     │ `openai/gpt-5.6-luna`                    │ 2116 ms   │ 0.05 ms   │ $0.000117    │ 93 / 100     │
    └─────────┴──────────────────┴──────────────────────────────────────────┴───────────┴───────────┴──────────────┴──────────────┘


# BENCH LM - SEPTEMBER 2026

| Rank | Model | Vendor | Status | Type | Context | Price | Score |
|------|-------|--------|--------|------|---------|-------|-------|
| 1 | Claude Mythos 5 | Anthropic | Current | Reasoning | 1M+ | $10.00 / $50.00 | 83.4 |
| 2 | Claude Fable 5 | Anthropic | Current | Reasoning | 1M+ | $10.00 / $50.00 | 83.15 |
| 3 | Claude Opus 5 | Anthropic | Current | Reasoning | — | $5.00 / $25.00 | 83.06 |
| 4 | GPT-5.6 Sol | OpenAI | Current | Reasoning | 1.05M | $5.00 / $30.00 | 82.2 |
| 5 | Kimi K3 | Moonshot AI | Current | Reasoning | 1.05M | $3.00 / $15.00 | 80.61 |
| 6 | Qwen3.8 Max | Alibaba | Current | Reasoning | 1M | Not listed | 79.22 |
| 7 | Hy4 preview | Tencent | Current | Reasoning | 1M | $0.00 / $0.00 | 79.16 |
| 8 | Muse Spark 1.1 | Meta | Superseded | Reasoning | 1M | Not listed | 77.14 |
| 9 | Claude Opus 4.8 | Anthropic | Superseded | Reasoning | 1M | $5.00 / $25.00 | 76.6 |
| 10 | Gemini 3.6 Flash | Google | Superseded | Reasoning | 1M | $1.50 / $7.50 | 75.66 |
| 11 | Grok 4.5 | xAI | Superseded | Reasoning | 500K | $2.00 / $6.00 | 75.65 |
| 12 | GPT-5.4 | OpenAI | Superseded | Reasoning | 1.05M | $2.50 / $15.00 | 73.56 |
| 13 | GPT-5.6 Terra | OpenAI | Current | Reasoning | 1.05M | $2.50 / $15.00 | 72.95 |
| 14 | GPT-5.5 | OpenAI | Superseded | Reasoning | 1M | $5.00 / $30.00 | 72.92 |
| 15 | Claude Opus 4.7 (Adaptive) | Anthropic | Superseded | Reasoning | 1M | $5.00 / $25.00 | 72.58 |
| 16 | Qwen3.8-27B | Alibaba | Current | Reasoning | 262K | $0.00 / $0.00 | 72.51 |
| 17 | Claude Opus 4.7 | Anthropic | Current | Standard | 1M | $5.00 / $25.00 | 72.33 |
| 18 | Qwen3.7 Max | Alibaba | Superseded | Reasoning | 1M | Not listed | 71.79 |
| 19 | Muse Spark | Meta | Superseded | Reasoning | 262K | Not listed | 71.02 |
| 20 | MiMo-V2.5-Pro | Xiaomi | Current | Reasoning | 1M | Not listed | 69.41 |
| 21 | MiniMax M3 | MiniMax | Current | Standard | 1M | $0.30 / $1.20 | 68.73 |
| 22 | dots3-note Preview | Dots Studio | Current | Reasoning | 512K | $0.00 / $0.00 | 68.66 |
| 23 | Ornith-1.5-397B | Ornith AI | Current | Reasoning | 262K | $0.00 / $0.00 | 68.6 |
| 24 | Claude Opus 4.6 | Anthropic | Superseded | Standard | 1M | $5.00 / $25.00 | 68.26 |
| 25 | Hy3 | Tencent | Superseded | Reasoning | 256K | $0.00 / $0.00 | 68.16 |
| 26 | Gemini 3 Pro | Google | Established | Standard | 2M | $2.00 / $12.00 | 67.64 |
| 27 | GPT-5.6 Luna | OpenAI | Current | Reasoning | 1.05M | $1.00 / $6.00 | 67.35 |
| 28 | GPT-5.2 Pro | OpenAI | Established | Reasoning | 400K | $21.00 / $168.00 | 67.3 |
| 29 | MiMo-V2-Pro | Xiaomi | Superseded | Reasoning | 1M | Not listed | 67.15 |
| 30 | GLM-5.1 | Z.AI | Superseded | Reasoning | 203K | $1.40 / $4.40 | 67.04 |
| 31 | Inkling | Thinking Machines Lab | Current | Standard | 1M | $1.87 / $4.68 | 67.02 |
| 32 | GPT-5.4 nano | OpenAI | Current | Reasoning | 400K | $0.20 / $1.25 | 66.78 |
| 33 | GLM-5-Turbo | Z.AI | Established | Reasoning | 200K | $1.20 / $4.00 | 66.3 |
| 34 | GPT-5.3 Codex | OpenAI | Established | Reasoning | 400K | $1.75 / $14.00 | 66.16 |
| 35 | Qwen3.7 Plus | Alibaba | Current | Reasoning | 1M | Not listed | 65.93 |
| 36 | GLM-5 | Z.AI | Superseded | Standard | 200K | $1.00 / $3.20 | 65.89 |
| 37 | Gemini 3.5 Flash-Lite | Google | Current | Reasoning | 1M | $0.30 / $2.50 | 65.5 |
| 38 | Claude Opus 4.6 (Adaptive) | Anthropic | Established | Reasoning | 1M | Not listed | 65.06 |
| 39 | Claude Sonnet 5 | Anthropic | Current | Reasoning | 1M | $2.00 / $10.00 | 65.02 |
| 40 | Qwen3.6 Plus | Alibaba | Superseded | Reasoning | 1M | Not listed | 64.99 |
| 41 | Claude Sonnet 4.6 | Anthropic | Superseded | Standard | 200K | $3.00 / $15.00 | 64.77 |
| 42 | Gemini 3.5 Flash | Google | Superseded | Reasoning | 1M | $1.50 / $9.00 | 64.73 |
| 43 | GPT-5.5 Pro | OpenAI | Current | Reasoning | 1M | $30.00 / $180.00 | 64.43 |
| 44 | Grok 4.3 | xAI | Superseded | Reasoning | 1M | $1.25 / $2.50 | 64.25 |
| 45 | Inkling-Small | Thinking Machines Lab | Current | Standard | 1M | $0.58 / $1.44 | 64.02 |
| 46 | Claude Opus 4.5 | Anthropic | Established | Standard | 200K | $5.00 / $25.00 | 63.91 |
| 47 | Grok 4.6 | xAI | Current | Reasoning | 500K | $2.00 / $6.00 | 63.42 |
| 48 | GLM-5.2 | Z.AI | Superseded | Reasoning | 1M | $1.40 / $4.40 | 63.4 |
| 49 | MiniMax M2.7 | MiniMax | Superseded | Standard | 200K | $0.30 / $1.20 | 63.29 |
| 50 | GLM-5.3 | Z.AI | Current | Reasoning | 1M | $0.00 / $0.00 | 62.84 |

*Showing 50 of 400*









  ───────────────────────────────┼──────────────────────┼──────────────────┼────────────┼────────────┼───────┼────────────┼─────────────┼────────────────────────────────────────────────
   nvidia/nemotron-3-super       │ LRU TTL Expiry Bug   │ 398.90 ms        │ YES        │ YES        │ 1.0   │ 404        │ $0.000000   │ "The method now correctly checks whether the
                                 │                      │                  │            │            │       │            │             │ entry’s time-to-live has elapsed based on..."
   nvidia/nemotron-3-super       │ Mutex Race Condition │ 396.41 ms        │ YES        │ YES        │ 1.0   │ 412        │ $0.000000   │ "The function get_or_set(key, val) has a
                                 │                      │                  │            │            │       │            │             │ check-then-act race condition. With lock..."
   nvidia/nemotron-3.5-lightning │ LRU TTL Expiry Bug   │ 442.12 ms        │ YES        │ YES        │ 1.0   │ 404        │ $0.000000   │ "Role: Vanguard CodeFix & Critic-Reviser. The
                                 │                      │                  │            │            │       │            │             │ bug is that is_expired always returns
                                 │                      │                  │            │            │       │            │             │ False..."
   nvidia/nemotron-3.5-lightning │ Mutex Race Condition │ 470.93 ms        │ YES        │ YES        │ 1.0   │ 412        │ $0.000000   │ "Role: Vanguard CodeFix & Critic-Reviser.
                                 │         