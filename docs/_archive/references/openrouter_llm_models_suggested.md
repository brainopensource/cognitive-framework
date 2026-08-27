# OpenRouter LLM Models: Suggested SOTA Reference

## 0. Free Models

- stealth/ox-alpha
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

- deepseek/deepseek-v4-flash-0731 (v2 coding)
- deepseek/deepseek-v4-flash (v2 0423)
- openai/gpt-5.6-luna
- qwen/qwen3.8-27b
- stepfun/step-3.7-flash
- xiaomi/mimo-v2.5
- xiaomi/mimo-v2.5-pro
- google/gemini-3.7-flash
- minimax/minimax-m3
- tencent/hy3-preview
- upstage/solar-pro4
- google/gemini-3.7-flash
- moonshotai/kimi-k2.7-code

## 2. Great Paid Models

- deepseek/deepseek-v4-pro
- moonshotai/kimi-k3
- z-ai/glm-5.3
- qwen/qwen3.8-max
- meta/muse-spark-1.2

## 3. Elite Top Models

- openai/gpt-5.6-sol


## 4. Local Models

- qwen2.5:1.5b
- qwen2.5-coder:7b
- deepseek-coder-v2:16b-instruct-q5







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