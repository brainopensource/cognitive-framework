# 001 LLM API ROUTER

Universal Multi-Provider LLM Router & Comparative Benchmarking CLI for Vanguard.

## Features
- **Multi-Provider Support**: Switch seamlessly between `openrouter`, `ollama` (local GPU), and `mock`.
- **Markdown Prompt Ingestion**: Accepts prompt strings or paths to `.md` files.
- **Dual Artifact Output**: Saves `<timestamp>_response.md` and `<timestamp>_meta.json` with exact token count, TTFT, latency, and integer micro-USD costs.
- **Streaming & Raw Mode**: Supports `--stream` for real-time tokens and `--raw-only` for programmatic pipelines.

## Examples

### 1. Local Free Benchmarking (Ollama)
```bash
python3 tools/001_LLM_API_ROUTER/llm_switch.py \
  -p ollama \
  -m qwen25 \
  -msg tools/001_LLM_API_ROUTER/prompts/default_task.md
```

### 2. Cloud Provider Testing (OpenRouter)
```bash
python3 tools/001_LLM_API_ROUTER/llm_switch.py \
  -p openrouter \
  -m deepseek/deepseek-v4-flash-0731 \
  -msg "write quicksort in Python" \
  --stream
```

### 3. Offline Pipeline Mock
```bash
python3 tools/001_LLM_API_ROUTER/llm_switch.py \
  -p mock \
  -msg "test prompt"
```
