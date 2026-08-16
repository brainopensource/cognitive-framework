# 002 LLM API MOCK (LAM)

Stateless OpenAI-compatible mock of an agentic coding provider.

```bash
python3 tools/002_LLM_API_MOCK/simulate.py
python3 tools/002_LLM_API_MOCK/server.py   # POST http://127.0.0.1:8787/v1/chat/completions
python3 -m unittest test.tools.test_llm_api_mock
```

Model ids: `lam/t1-calculator`, `lam/t2-two-files`, `lam/t3-context-layers`, `lam/t4-feature-todos`, `lam/t5-extract-module`.

The engine is **stateless**: the next assistant turn is selected from the accumulated `role=tool` count (and a pytest/passed user message for the stop turn). Same history ⇒ same completion on a fresh process.

Live OpenRouter pings: `python3 tools/002_LLM_API_MOCK/live_probe.py` (needs `OPENROUTER_API_KEY`; free models only on the $0.50 wave).
