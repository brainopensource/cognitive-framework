# 002 LLM API MOCK (LAM)

A standalone, dependency-free, high-performance mock server for multi-turn LLM APIs (OpenAI, OpenRouter, and Ollama wire protocols).

## Key Features

1. **Stateless Multi-Turn Replay (No Server-Side Sessions):**
   - Automatically detects prior conversational turns in the prompt history and advances to the next turn ($K \to K+1$).
   - Counts `role: "tool"` observation messages to advance tool-calling scripts.
2. **4-Tier Capability Ladder:**
   - **Tier 1 (Toy / Syntax error / Buggy):** `qwen2.5:1.5b`, `llama3.2:3b`.
   - **Tier 2 (Cheap / Off-by-one / Recovers on feedback):** `qwen3.6:27b`, `deepseek-r1:14b`, `openrouter/free`.
   - **Tier 3 (Mid-Tier / Strong single-turn coding):** `deepseek/deepseek-chat`, `google/gemini-2.0-flash-001`.
   - **Tier 4 (Frontier SOTA / Tool-calling & patches):** `anthropic/claude-3.5-sonnet`, `openai/gpt-4o`.
3. **Pure Markdown/JSON Answer Bank:**
   - Scenarios and responses are plain `.md` and `.json` files in `answer_bank/`. No Python code edits needed to add new benchmarks or coding tasks.
4. **Wire Protocol Compatibility:**
   - Supports `/v1/chat/completions`, `/chat/completions`, and `/api/generate` (Ollama).
   - Supports non-streaming JSON and Server-Sent Events (`SSE`) streaming chunks with optional `--latency-ms`.

---

## Quickstart

### 1. Launch the Mock Server
```bash
python3 tools/002_LLM_API_MOCK/mock_server.py --port 4141
```

### 2. Test Multi-Turn Interaction (Turn 1 -> Turn 2 Cascade)

#### Turn 1: Initial Prompt
```bash
curl -s http://127.0.0.1:4141/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Mock-Tier: 2" \
  -d '{
    "model": "qwen3.6:27b",
    "messages": [
      {"role": "user", "content": "Write calculated_value = (A + B) * B in Python"}
    ]
  }' | jq '.choices[0].message.content'
```
*Output (Tier 2 Turn 1 makes a deliberate arithmetic bug: `(A + B) + B`):*
```python
resultado = (A + B) + B
print(f"the value is {resultado:.2f}")
```

#### Turn 2: Feed back the error (Simulating Harness Test Failure)
```bash
curl -s http://127.0.0.1:4141/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Mock-Tier: 2" \
  -d '{
    "model": "qwen3.6:27b",
    "messages": [
      {"role": "user", "content": "Write calculated_value = (A + B) * B in Python"},
      {"role": "assistant", "content": "resultado = (A + B) + B\nprint(f\"the value is {resultado:.2f}\")"},
      {"role": "user", "content": "Test failed! You added B instead of multiplying by B."}
    ]
  }' | jq '.choices[0].message.content'
```
*Output (Tier 2 Turn 2 fixes the bug based on feedback: `(A + B) * B`):*
```python
# Corrected: Multiplying the sum of A and B by B
resultado = (A + B) * B
print(f"the value is {resultado:.2f}")
```

---

## Running Unit & Integration Tests

```bash
python3 tools/002_LLM_API_MOCK/test_mock.py
```
