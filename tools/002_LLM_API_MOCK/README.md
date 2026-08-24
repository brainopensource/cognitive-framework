# 002 LLM API MOCK (LAM)

Stateless OpenAI & Ollama dual-wire mock, replay engine, and recording proxy for reproducible agentic coding tests.

```bash
# Run 36 Gold Scenarios (~1.1s, $0)
python3 tools/002_LLM_API_MOCK/simulate.py

# Launch Unified LAM HTTP Server (OpenAI & Ollama wire)
python3 tools/002_LLM_API_MOCK/server.py --port 8787

# Probe WSL2 -> Windows 11 Ollama reachability
python3 tools/002_LLM_API_MOCK/stub.py

# Run Hermetic Mock & Evidence Tests
python3 -m unittest test.tools.test_llm_api_mock
```

## Modes & Evidence Labels

1. **`lam-replay` (Mode A, Default):** Fast deterministic turn playback from gold scenarios based on tool observation counts. Carries `X-Evidence-Label: lam-replay`. Used for CI and harness tests; strictly barred from M-4 / RF-85 evidence.
2. **`ollama-live` (Mode B, WSL2 / Local):** Proxies non-`lam/*` calls to upstream Ollama (e.g. `LAM_UPSTREAM=http://192.168.15.1:11434`), logging request/response hashes, timing, and token metrics to `lam.sqlite`. Carries `X-Evidence-Label: ollama-live`.
3. **`cassette-exact` (Mode C):** Byte-for-byte playback of recorded HTTP traces via `--cassette`. Carries `X-Evidence-Label: cassette-exact`.

## HTTP Routes

- `GET /health`: Server health, active mode, evidence label, and scenario count.
- `GET /v1/models` / `GET /models`: Model catalog listing `lam/*` gold models and tier aliases.
- `GET /api/tags`: Ollama tags route (proxies to upstream if configured, else lists `lam/*`).
- `POST /v1/chat/completions`: OpenAI-compatible endpoint with JSON completion & SSE streaming.
- `POST /api/chat` & `POST /api/generate`: Ollama-compatible endpoint with function-calling support.

## WSL2 Host Probe & Direct Ollama Usage

From inside WSL2:
```bash
# Auto-detect Windows host IP and probe port 11434
python3 tools/002_LLM_API_MOCK/stub.py

# Export suggested environment variables
export VANGUARD_OLLAMA_ENDPOINT=http://<WINDOWS_HOST>:11434/api/chat
export LAM_UPSTREAM=http://<WINDOWS_HOST>:11434
```

