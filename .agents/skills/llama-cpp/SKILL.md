---
name: llama-cpp
description: Autonomous agent guide and operational standard for local LLM inference using native llama.cpp / llama-server. Ollama is strictly forbidden and deprecated across the repository.
version: "1.0.0"
authority: operational
---

# LLAMA.CPP / LLAMA-SERVER — Standard Local LLM Engine

This repository standardizes strictly on **`llama.cpp` (`llama-server`)** for all local model execution. 
**DO NOT use or propose Ollama.** Ollama has been removed from this system and codebase.

---

## 1. Hardware & Environment Facts

- **GPU Acceleration**: Vulkan backend via AMD Radeon RX 9060 XT (16 GB VRAM).
- **Binary Location**: `~/.local/bin/llama-server` (in user PATH).
- **Shared Libraries**: `~/.local/lib/llama.cpp/`.
- **GGUF Models Directory**: `~/Models/`
  - `Qwen3.8-27B-UD-Q2_K_XL.gguf` (9.2 GB - recommended 27B local model)
  - `Qwen3.8-27B-UD-IQ1_M.gguf` (6.3 GB)
  - `Qwen3.8-27B-UD-Q4_K_S.gguf` (15 GB)

---

## 2. Launching `llama-server`

To start local inference on the AMD GPU:

```bash
llama-server \
  -m ~/Models/Qwen3.8-27B-UD-Q2_K_XL.gguf \
  -c 8192 \
  -ngl 99 \
  --host 127.0.0.1 \
  --port 8080 \
  --alias local-model \
  --jinja
```

- `-ngl 99`: Offloads all layers to Vulkan VRAM.
- `-c 8192`: Context window.
- `--port 8080`: Standard local port for `llama-server`.
- `--jinja`: Enables tokenizer chat template formatting for tool calling.

---

## 3. Invoking Local Inference via Vanguard CLI

When running the Vanguard / AETHER CLI against local models, use:

```bash
# Using the local alias:
node vanguard/clients/cli/dist/src/main.js code <WORKSPACE> --provider local

# Or explicitly targeting llama_cpp:
node vanguard/clients/cli/dist/src/main.js code <WORKSPACE> --provider llama_cpp --planner local-model
```

The CLI connects directly to `http://127.0.0.1:8080/v1/chat/completions` using the standard OpenAI specification via `vanguard/packages/adapters/models/llama_cpp.py`.

---

## 4. Invariant Rules for Autonomous Agents

1. **NEVER execute `ollama` or check for `ollama`**: The daemon is removed and will fail.
2. **NEVER try to run `/usr/local/lib/ollama/llama-server`**: That binary is an internal artifact and will fail to link GPU drivers. Use `~/.local/bin/llama-server` instead.
3. **NEVER invent new local provider adapters**: Use `vanguard/packages/adapters/models/llama_cpp.py` which reuses the standard OpenAI specification.
