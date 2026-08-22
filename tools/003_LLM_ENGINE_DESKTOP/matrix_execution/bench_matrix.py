#!/usr/bin/env python3
"""
Scientific Matrix Benchmarking & Data Science Pipeline for Ollama Inference.
Location: tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix.py
"""

import ast
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import time
import urllib.request

# Paths configuration
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "docs" / "prompts" / "fibo_challenge_finetune.md"
OUTPUT_DIR = BASE_DIR / "bench_finetune"
RUNS_DIR = OUTPUT_DIR / "runs"
CSV_FILE = OUTPUT_DIR / "benchmark_results.csv"
JSONL_FILE = OUTPUT_DIR / "benchmark_results.jsonl"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3.8:27b"

# Ensure directories exist
RUNS_DIR.mkdir(parents=True, exist_ok=True)


def load_prompt() -> str:
    """Reads the exact challenge prompt from markdown file."""
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found at: {PROMPT_FILE}")
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def evaluate_python_code(code_str: str) -> tuple[int, str]:
    """
    Evaluates generated code quality from 0 to 100 based on AST and requirements.
    """
    score = 0
    feedback = []

    clean_code = code_str
    if "```python" in clean_code:
        clean_code = clean_code.split("```python")[1].split("```")[0].strip()
    elif "```" in clean_code:
        clean_code = clean_code.split("```")[1].split("```")[0].strip()

    try:
        parsed = ast.parse(clean_code)
        score += 30
        feedback.append("Syntax: OK")
    except SyntaxError as e:
        feedback.append(f"Syntax: Error ({e.msg})")
        return max(score, 10), " | ".join(feedback)

    has_target_func = False
    has_type_hints = False
    for node in ast.walk(parsed):
        if isinstance(node, ast.FunctionDef) and node.name == "get_nth_fibonacci":
            has_target_func = True
            if node.returns is not None:
                has_type_hints = True

    if has_target_func:
        score += 25
        feedback.append("Func: Present")
    else:
        feedback.append("Func: Missing")

    if has_type_hints:
        score += 15
        feedback.append("Types: Yes")
    else:
        feedback.append("Types: No")

    if "ValueError" in code_str:
        score += 15
        feedback.append("Validation: OK")
    else:
        feedback.append("Validation: No ValueError")

    if not code_str.startswith("```") and "Sure!" not in code_str and "<think>" not in code_str:
        score += 15
        feedback.append("Purity: Pure Code")
    else:
        feedback.append("Purity: Has Markdown/Talk")

    return score, " | ".join(feedback)


# Test Matrix Experiments
MATRIX_EXPERIMENTS = [
    {
        "id": "run_01_baseline",
        "name": "Baseline (Defaults)",
        "description": "Standard default Ollama parameters",
        "options": {}
    },
    {
        "id": "run_02_context_trimmed",
        "name": "Context Trimmed (2048)",
        "description": "Reduces KV cache allocation to 2048",
        "options": {"num_ctx": 2048}
    },
    {
        "id": "run_03_thinking_suppressed",
        "name": "Thinking Suppressed (System Prompt)",
        "description": "Strict system prompt suppressing thinking traces",
        "system": "You are a Python compiler. Output pure code only. Do not use <think> tags. Do not explain.",
        "options": {}
    },
    {
        "id": "run_04_greedy_sampling",
        "name": "Greedy Decoding (temp=0.0)",
        "description": "Deterministic greedy search (top_k=1, temp=0.0)",
        "options": {"temperature": 0.0, "top_k": 1, "top_p": 1.0}
    },
    {
        "id": "run_05_thread_affinity",
        "name": "CPU Thread Alignment (8 Cores)",
        "description": "Pins execution to the 8 physical cores of 5800X3D",
        "options": {"num_thread": 8}
    },
    {
        "id": "run_06_budget_stop_control",
        "name": "Budget & Stop Tokens",
        "description": "num_predict=400 with stop tokens",
        "options": {"num_predict": 400, "stop": ["<|im_end|>", "\n# Example", "```\n"]}
    }
]


def run_experiment(exp: dict, prompt: str) -> dict:
    """Executes single test against Ollama, saves raw code and records tabular record."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": exp.get("options", {})
    }
    if "system" in exp:
        payload["system"] = exp["system"]

    print(f"🚀 Running {exp['name']}...")
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    start_wall = time.perf_counter()
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    end_wall = time.perf_counter()

    wall_sec = end_wall - start_wall
    eval_count = res.get("eval_count", 0)
    eval_dur_sec = res.get("eval_duration", 1) / 1e9
    prompt_count = res.get("prompt_eval_count", 0)
    prompt_dur_sec = res.get("prompt_eval_duration", 1) / 1e9
    raw_response = res.get("response", "")

    eval_tps = eval_count / eval_dur_sec if eval_dur_sec > 0 else 0
    prompt_tps = prompt_count / prompt_dur_sec if prompt_dur_sec > 0 else 0

    # 1. Save raw unedited code
    output_py_file = RUNS_DIR / f"{exp['id']}.py"
    with open(output_py_file, "w", encoding="utf-8") as f:
        f.write(raw_response)

    # 2. Automated Quality Score
    score, feedback = evaluate_python_code(raw_response)

    # 3. Build Data Science Schema Row
    opts = exp.get("options", {})
    record = {
        "timestamp_iso": datetime.now().isoformat(),
        "run_id": exp["id"],
        "experiment_name": exp["name"],
        "model_name": MODEL_NAME,
        "num_ctx": opts.get("num_ctx", "default"),
        "num_thread": opts.get("num_thread", "default"),
        "temperature": opts.get("temperature", "default"),
        "top_k": opts.get("top_k", "default"),
        "top_p": opts.get("top_p", "default"),
        "num_predict": opts.get("num_predict", "default"),
        "has_system_prompt": "Yes" if "system" in exp else "No",
        "prompt_tokens": prompt_count,
        "prompt_tps": round(prompt_tps, 2),
        "eval_tokens": eval_count,
        "eval_tps": round(eval_tps, 2),
        "wall_time_sec": round(wall_sec, 2),
        "auto_score": score,
        "auto_feedback": feedback,
        "output_file": str(output_py_file.relative_to(BASE_DIR)),
        "manual_pass": "",  # Empty for manual excel evaluation
        "manual_notes": ""  # Empty for manual excel evaluation
    }

    print(f"   ⏱️  Speed: {eval_tps:.2f} t/s | Latency: {wall_sec:.2f}s | Score: {score}/100")
    return record


def save_datasets(records: list[dict]):
    """Appends records to both CSV (Excel-ready) and JSONL (Full Metadata)."""
    # Append to JSONL
    with open(JSONL_FILE, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Write / Append to CSV
    csv_exists = CSV_FILE.exists()
    keys = list(records[0].keys())

    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if not csv_exists:
            writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"\n📊 Datasets updated successfully:")
    print(f"   - Excel / CSV Table : {CSV_FILE}")
    print(f"   - JSONL Full Dataset: {JSONL_FILE}")


def main():
    prompt = load_prompt()
    print("=" * 70)
    print("🧪 EXECUTING SCIENTIFIC LLM BENCHMARK MATRIX & DATASET LOGGER")
    print(f"Model Target : {MODEL_NAME}")
    print(f"Prompt Source: {PROMPT_FILE}")
    print("=" * 70)

    records = []
    for exp in MATRIX_EXPERIMENTS:
        try:
            r = run_experiment(exp, prompt)
            records.append(r)
        except Exception as e:
            print(f"❌ Error in {exp['name']}: {e}")

    if records:
        save_datasets(records)

    # Print summary table
    print("\n" + "=" * 70)
    print("📊 BENCHMARK SUMMARY TABLE")
    print("=" * 70 + "\n")
    print("| Experimento | Tokens/s | Latência | Nota (0-100) | Avaliação Auto |")
    print("| :--- | :---: | :---: | :---: | :--- |")
    for r in records:
        print(f"| **{r['experiment_name']}** | **{r['eval_tps']} t/s** | {r['wall_time_sec']}s | **{r['auto_score']}/100** | {r['auto_feedback']} |")


if __name__ == "__main__":
    main()
