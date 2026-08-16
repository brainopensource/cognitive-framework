# 002 LLM API MOCK

Lightweight, standalone mock LLM stub and HTTP server.

## Features
- Provides generic OpenAPI / OpenAI / Ollama compatible JSON payloads for offline stubbing and pipeline validation.
- Zero external dependencies (uses standard library `http.server` & `json`).

## Usage
### 1. In Python code
```python
from stub import MockLLMStub

stub = MockLLMStub()
response = stub.generate(prompt="hello", model="mock-model")
print(response["choices"][0]["message"]["content"])
```

### 2. Run Local HTTP Stub Server
```bash
python3 tools/002_LLM_API_MOCK/mock_server.py --port 11435
```
