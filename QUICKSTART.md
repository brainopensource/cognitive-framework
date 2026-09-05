---
id: quickstart-guide
class: guide
authority: operational
canonical_for:
  - quickstart
  - cli-usage
status: living
owner: developer-experience
version: "0.9.3"
last_verified: 2026-09-04
supersedes: []
superseded_by: null
---

# Vanguard CLI (`vg`) — Quickstart & Benchmark Guide

This guide walks through installing, configuring, and operating the Vanguard interactive CLI (`vg`) and runtime engine. It includes reproducible recipes for automated benchmarks, interactive TUI sessions, and step-by-step walkthroughs of the L0 smoke triad workloads.

---

## 1. Prerequisites

Ensure your host environment meets the baseline requirements:

- **Linux / macOS** (Tested on Linux x86_64).
- **Node.js $\ge$ 20.0.0** (`node --version`).
- **Python $\ge$ 3.10** (Tested on Python 3.12, managed via [uv](https://github.com/astral-sh/uv)).
- **Git** installed and available in `PATH`.

---

## 2. Installation & CLI Setup

The Vanguard CLI is a TypeScript/Node client (`vanguard/clients/cli/`) that interfaces directly with the Python runtime kernel via [`vanguard/packages/runtime/entrypoint.py`](vanguard/packages/runtime/entrypoint.py).

### Step 1: Install Python & Node Dependencies
From the repository root:

```bash
# 1. Synchronize Python virtual environment
uv sync

# 2. Install TypeScript & workspace dependencies
npm ci
```

### Step 2: Build and Link the CLI
Run the automated installation script:

```bash
bash vanguard/clients/cli/install.sh
```

This compiles `@vanguard/cli` with `tsc` and installs launcher wrappers for `vg` and `aether` into `~/.local/bin/`.

Ensure `~/.local/bin` is in your environment `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Verify that the CLI is accessible:

```bash
vg --help
```

---

## 3. Environment & Provider Configuration

Vanguard enforces a fail-closed secret loader ([`vanguard/packages/adapters/models/env_loader.py`](vanguard/packages/adapters/models/env_loader.py)). Secret files must be untracked regular files with mode `0600` or stricter.

### Step 1: Configure `.env`
In the root of the repository:

```bash
# Add your OpenRouter API key
echo "OPENROUTER_API_KEY=sk-or-v1-your-key-here" > .env

# Lock file permissions (REQUIRED: fail-closed if permissions are loose)
chmod 600 .env
```

### Step 2: Export Key in Shell
Before invoking `vg`, export the API key to your shell session:

```bash
export OPENROUTER_API_KEY=$(grep '^OPENROUTER_API_KEY=' .env | cut -d= -f2)
```

### Step 3: Validate Model Readiness
Run the internal provider probe:

```bash
python3 -c "from vanguard.packages.runtime.model_selection import inspect_model_providers; print([p for p in inspect_model_providers() if p['port'] == 'openrouter'])"
```
*Expected Output:*
```python
[{'port': 'openrouter', 'readiness': 'ready', 'detail': 'configured with API key', 'hasCredentials': True}]
```

---

## 4. Centralized Model Hierarchy

Model access is governed strictly by [`vanguard/packages/adapters/models/models_registry.json`](vanguard/packages/adapters/models/models_registry.json):

| Tier | Purpose | Models & Aliases | Cost Profile |
|---|---|---|---|
| **Tier 1 (Free)** | Basic tasks & dry runs | `openrouter/free`, `minimax/minimax-m3:free` | $0.00 / MTok |
| **Tier 2 (Flash)** | **Default Coding Model** | `deepseek/deepseek-v4-flash-0731`, `z-ai/glm-5.3-flash` | ~$0.14 / MTok prompt |
| **Tier 3 (Pro)** | Complex architecture / refactors | `deepseek/deepseek-v4-pro`, `openai/gpt-5.6-luna` | ~$0.45 / MTok prompt |
| **Tier 4 (Frontier)** | Highest precision reasoning | `google/gemini-3.8-flash` | ~$0.15 / MTok prompt |
| **Local (llama.cpp)** | **Zero-Cost Offline Inference** | `local-model`, `llama_cpp`, `llama` | $0.00 / Local GPU |

> [!TIP]
> When running paid tier models (Tiers 2–4), always pass `--budget-usd <N>` to authorize the spend envelope. Local models (`local-model`) run entirely offline with zero API cost.

---

## 5. Execution Modes

### Mode A: Automated Benchmark Execution (Headless)
Used for automated evaluation, headless CI runs, and coding benchmarks:

```bash
vg code /path/to/target/workspace \
  --brief "TASK.md" \
  --planner deepseek/deepseek-v4-flash-0731 \
  --budget-usd 1 \
  --benchmark \
  --headless
```

- `--brief <file or text>`: Specifies task instructions.
- `--planner <model>`: Explicit model identifier from the registry.
- `--budget-usd 1`: Unlocks the paid tier spend reservation.
- `--benchmark`: Automatically resolves standard approval policy for `patch.apply` and `proc.exec` without prompting for interactive approval on each mutation.
- `--headless`: Emits structured JSON streaming projections rather than the interactive Ink TUI.

---

### Mode B: Interactive Visual TUI (Human-in-the-Loop)
Used for interactive pair programming where human operators review diffs and approve mutations:

```bash
cd /path/to/target/workspace
vg
```
*Or from anywhere specifying a path and prompt:*
```bash
vg code /path/to/target/workspace --brief "Implement feature X and test it"
```
In interactive mode, every mutating action (`patch.apply`, `proc.exec`) generates an interactive approval prompt (`[y]es / [n]o`) before any change touches the file system.

---

## 6. Real Benchmark Walkthroughs (L0 Smoke Triad)

Here are the exact configurations and verification steps from the isolated test benchmarks located in `/home/rock-dev/Coding/cognitive-framework-benchs/`:

### Example 1: Greenfield Module & CLI (`P0-FIB`)

1. **Workspace Setup**:
   ```bash
   mkdir -p /path/to/benchs/fibo && cd /path/to/benchs/fibo
   git init
   ```
2. **Create `TASK.md`**:
   ```markdown
   # P0-FIB: Fibonacci Module, CLI and Tests
   Create `fibonacci.py` with `fibonacci(n: int) -> int` raising `ValueError` on `n < 0`.
   Add CLI execution via `python3 fibonacci.py <n>`.
   Provide `test_fibonacci.py` with comprehensive unit tests.
   Run tests with `python3 -m unittest test_fibonacci.py`.
   ```
3. **Execute with `vg code`**:
   ```bash
   vg code /path/to/benchs/fibo \
     --brief "TASK.md" \
     --planner deepseek/deepseek-v4-flash-0731 \
     --budget-usd 1 \
     --benchmark \
     --headless
   ```
4. **Verify Result**:
   ```bash
   python3 -m unittest test_fibonacci.py
   # Output: Ran 6 tests in 0.000s — OK
   ```

---

### Example 2: Seeded Defect Fix (`P0-BUG`)

1. **Workspace Setup**:
   ```bash
   mkdir -p /path/to/benchs/bugfix && cd /path/to/benchs/bugfix
   git init
   ```
2. **Seed Defect in `string_utils.py`**:
   ```python
   def truncate_with_ellipsis(text: str, max_length: int) -> str:
       if len(text) <= max_length: return text
       if max_length <= 3: return text[:max_length]
       cutoff = max_length - 4  # Off-by-one bug
       return text[:cutoff] + "..."
   ```
3. **Run Pre-Oracle Test (Fails)**:
   ```bash
   python3 -m unittest test_string_utils.py
   # Output: FAILED (failures=2)
   ```
4. **Execute Repair with `vg code`**:
   ```bash
   vg code /path/to/benchs/bugfix \
     --brief "TASK.md" \
     --planner deepseek/deepseek-v4-flash-0731 \
     --budget-usd 1 \
     --benchmark \
     --headless
   ```
5. **Inspect Diff & Verify Post-Oracle (Passes)**:
   ```bash
   git diff string_utils.py
   # - cutoff = max_length - 4
   # + cutoff = max_length - 3

   python3 -m unittest test_string_utils.py
   # Output: Ran 5 tests in 0.000s — OK
   ```

---

### Example 3: Data Transform Pipeline (`P0-CSV`)

1. **Workspace Setup**:
   ```bash
   mkdir -p /path/to/benchs/pandas && cd /path/to/benchs/pandas
   git init
   ```
2. **Create `TASK.md`**:
   ```markdown
   # P0-CSV: Data Pipeline
   Create `pipeline.py` with `process_pipeline(input_path: str, output_path: str) -> None`.
   Validate schema: `id,category,amount,active`.
   Filter `active == true`, aggregate sum of `amount` grouped by `category`, rounded to 1 decimal.
   Output sorted CSV with headers `category,total_amount`.
   Write unit tests in `test_pipeline.py`.
   ```
3. **Execute with `vg code`**:
   ```bash
   vg code /path/to/benchs/pandas \
     --brief "TASK.md" \
     --planner deepseek/deepseek-v4-flash-0731 \
     --budget-usd 1 \
     --benchmark \
     --headless
   ```
4. **Verify Result**:
   ```bash
   python3 -m unittest test_pipeline.py
   # Output: Ran 3 tests in 0.001s — OK
   ```

---

## 7. Local LLM Execution via Native `llama.cpp`

Vanguard supports local model inference via native `llama.cpp` (`llama-server`). Following strict repository governance rules ([`.agents/skills/llama-cpp/SKILL.md`](.agents/skills/llama-cpp/SKILL.md)), Ollama is strictly forbidden and deprecated across the repository.

### Starting `llama-server` (Vulkan / ROCm GPU Offload)
Launch `llama-server` using your local GGUF models:

```bash
# Recommended for 16GB GPUs (e.g. AMD RX 9060 XT) - SOTA 4-bit precision:
~/.local/bin/llama-server \
  -m /path/to/Models/Qwen3.8-27B-UD-Q4_K_S.gguf \
  -c 4096 \
  -ngl 99 \
  --host 127.0.0.1 \
  --port 8080 \
  --alias local-model \
  --reasoning off \
  --jinja
```

> [!IMPORTANT]
> **Why `--reasoning off` is Critical for Local Models:**
> Modern reasoning models (e.g., Qwen3.8, DeepSeek-R1 derivatives) emit internal `<think>` tokens by default. Without `--reasoning off`, the model expends 1,500–2,000 tokens on internal monologues, frequently exhausting the `max_tokens` budget before code blocks finish emitting. Passing `--reasoning off` drops latency from ~88s down to 10–35s while maintaining high code quality. If deep reasoning is explicitly needed, ensure `-c 8192` or higher is allocated and clients authorize `max_tokens >= 4096`.

### Running `vg` with Local Model
```bash
# Point CLI or environment to local endpoint:
export VANGUARD_LLAMA_ENDPOINT="http://127.0.0.1:8080/v1/chat/completions"

vg code /path/to/target/workspace \
  --brief "TASK.md" \
  --planner local-model \
  --benchmark \
  --headless
```

---

## 8. Empirical Local Model Benchmark Results (AMD RX 9060 XT 16GB)

A comprehensive benchmark suite was executed on an AMD Radeon RX 9060 XT (16 GB VRAM) using native `llama.cpp` (`llama-server`) with Vulkan GPU offloading (`-ngl 99`, `--reasoning off`).

### 8.1. Multi-Tier Open-Weights Model Matrix (0.5B to 27B)

The table below evaluates the primary open-weights models across their designated architectural sweet spots using standardized prompt evaluation (`"python code in the chat for printing 6th fibonacci value in one line"` with `max_tokens: 2048`):

| Model | Architecture & Role | GGUF File Size | Context | Warmup (s) | Speed (tok/s) | Latency (s) | Score | Status | Operational Profile |
|---|---|---|---|---|---|---|---|---|---|
| **Qwen2.5-Coder-1.5B** | 1.5B Dense (Coding) | 941 MB | 8192 | 1.01s | **166.15** | 1.17s | 100 | **PASS** | Sub-3B syntax speed champion. Instantaneous generation (<1.2s) for live IDE completions. |
| **DeepSeek-R1-Distill-1.5B** | 1.5B Dense (Reasoning) | 1.1 GB | 8192 | 1.00s | **169.37** | 2.26s | 100 | **PASS** | Completes compact CoT reasoning (~200 tokens) and emits working code block within 2.3s. |
| **Qwen2.5-Coder-3B** | 3.1B Dense (Coding) | 1.8 GB | 8192 | 1.50s | **92.02** | **0.71s** | 100 | **PASS** | **Lowest total latency (0.71s).** High syntactic density with minimal memory footprint. |
| **Phi-4-mini (3.8B)** | 3.8B Dense (Reasoning) | 2.4 GB | 8192 | 2.00s | **87.98** | 2.31s | 85 | **PASS** | Strong logic; generated both inline recursive functions and a lambda one-liner expression. |
| **DeepSeek-Coder-V2-Lite** | 16B MoE *(2.4B active)* | 9.7 GB | 8192 | 3.57s | **109.81** | 2.80s | 100 | **PASS** | **MoE Velocity Champion:** Generates at **~110 tok/s** (faster than 3B dense) with 16B code quality. |
| **Qwen2.5-Coder-14B** | 14.7B Dense (Coding) | 8.4 GB | 8192 | 5.09s | **28.85** | 2.74s | 100 | **PASS** | **SOTA 14B Coding:** Emitted direct array slice `print([0, 1, 1, 2, 3, 5, 8][5])` with zero preambles. |
| **DeepSeek-R1-Distill-14B** | 14.7B Dense (Reasoning) | 8.4 GB | 8192 | 6.19s | **30.37** | 67.43s | 70 | **PARTIAL** | Massive reasoning depth; spent full 2048 token budget on number theory and sequence indices. |
| **Mistral-Small-24B-2501** | 24B Dense (Tool Calling) | 13.4 GB | 4096 | 5.07s | **21.23** | 10.83s | 100 | **PASS** | **Tool-Calling SOTA:** Fits within 16GB VRAM at 4k context (~15.2 GB total VRAM). Flawless one-liner. |
| **Qwen3.8-27B-Q4_K_S** | 27B Dense (Precision) | 15.0 GB | 4096 | 10.2s | **13.74** | 16.63s | 100 | **PASS** | Full 16GB VRAM saturation (93.6%). 100% pass rate across multi-file triad benchmarks. |

---

### 8.2. 27B Quantization Frontier (L0 Triad Tasks)

Evaluation of `Qwen3.8-27B` across all 3 multi-file project tasks (`fibo`, `bugfix`, `pandas`):

| Model Quant | Weight Size | VRAM Footprint | Speed (tok/s) | Triad Pass Rate | Avg Score | Status & Failure Analysis |
|---|---|---|---|---|---|---|
| **`IQ1_M` (1-bit)** | 6.3 GB | 7.5 GB (44%) | **29.86** | 0 / 3 (0%) | 10 / 100 | **FAIL:** Severe quant degradation; looped in reasoning and truncated before closing files. |
| **`Q2_K_XL` (2-bit)** | 9.2 GB | 12.38 GB (72%) | **22.85** | 2 / 3 (66.7%) | 93.3 / 100 | **PASS:** `fibo` & `bugfix` 100% clean; `pandas` code was correct but test omitted `import csv`. |
| **`Q4_K_S` (4-bit)** | 15.0 GB | 16.01 GB (93.6%) | **13.74** | **3 / 3 (100%)** | **100 / 100** | **PERFECT:** 20/20 unit tests across all 3 suites passed on the first attempt without errors. |

---

### 8.3. Architectural Insights & Sizing Rules

1. **The MoE Velocity Breakthrough:**
   - Sparse Mixture-of-Experts (`DeepSeek-Coder-V2-Lite`) delivers the ultimate speed-to-intelligence ratio: **109.81 tok/s** with an **8192 token context** while consuming only 9.7 GB of VRAM. It operates 4x faster than equivalent dense 14B models while retaining 16B parameter depth.
2. **Dense Coding Precision Sweet Spot:**
   - `Qwen2.5-Coder-14B` is the most reliable dense model under 16GB VRAM for autonomous agent dispatch (`vg code`), providing immediate, syntactically exact code blocks at **~29 tok/s**.
3. **Tool Calling & JSON Schemas:**
   - `Mistral-Small-24B-Instruct-2501` is the open-weights reference for structured tool calling. To keep it fully offloaded to GPU on 16GB hardware, configure context to **`-c 4096`**, ensuring total VRAM allocation stays under 15.5 GB.
4. **Reasoning Models (DeepSeek-R1 Distillations):**
   - Distilled R1 models natively prioritize reasoning tokens (`reasoning_content`). For simple tasks, smaller distillations (`1.5B`) conclude their thoughts within ~200 tokens and emit code cleanly. Larger distillations (`14B`) require **`max_tokens >= 4096`** or an explicit anti-thinking directive to prevent token budget exhaustion before code emission.
5. **Workspace Containment Invariant:**
   - Any workspace directory invoked with `proc.exec` or automated testing must include `.vanguard/workspace.toml` containing `root = "."` to satisfy containment boundary invariants.

---

## 9. Inspecting Results & Audit Trails

Every Vanguard run is deterministically recorded in an immutable SQLite event store:

1. **Check Git Status**:
   ```bash
   git status
   git diff
   ```
2. **Inspect the Immutable Audit Ledger**:
   ```bash
   sqlite3 .vanguard/events.sqlite3 "SELECT seq, kind FROM events ORDER BY seq DESC LIMIT 15;"
   ```
3. **Replay or Trace Run**:
   ```bash
   vg trace <run-id> --headless
   ```

---

## 10. Invariants & Operational Rules to Remember

1. **Sandbox Command Allowlist**:
   When invoking `proc.exec` commands in code-default harnesses, only allowlisted binaries are permitted:
   `('pytest', 'ruff', 'git', 'python3', 'python', 'ls', 'find')`.
   Non-allowlisted binaries (e.g. `pwd`, `bash`, `curl`) will be rejected with an `EffectFailed: adapter_error`.
2. **No Patchless Finishes**:
   Admission requires a verified patch digest when mutation capability is active. Calling `finish` without applying code changes or without passing test receipts will fail closed.
3. **Fail-Closed Secrets**:
   The `.env` file must never be tracked by Git and must have permissions `0600` or stricter. Permissive permissions will result in key loading refusal.
