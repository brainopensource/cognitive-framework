#!/usr/bin/env python3
"""
16-Run Fractional Factorial (DoE 2^(5-1)) High-Order Benchmark Matrix for Ollama.
Location: tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix_16.py
Usage:
    python3 bench_matrix_16.py [MODEL_NAME]
"""

import ast
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import time
import urllib.request

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "docs" / "prompts" / "fibo_challenge_finetune.md"
BASE_OUTPUT_DIR = BASE_DIR / "bench_finetune"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Default model or from CLI argument
DEFAULT_MODEL = "qwen2.5:1.5b"
MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL


def get_model_folder_name(model_name: str) -> str:
    """Maps model name to a clean, isolated directory name."""
    mapping = {
        "qwen3.8:27b": "qwen_38_27B",
        "qwen2.5-coder:14b": "qwen_25C_14B",
        "qwen2.5-coder:7b-instruct-q5_K_M": "qwen_25C_7B",
        "qwen2.5:1.5b": "qwen_25_15B",
    }
    if model_name in mapping:
        return mapping[model_name]
    return model_name.replace(":", "_").replace("-", "_").replace(".", "")


MODEL_FOLDER = get_model_folder_name(MODEL_NAME)
OUTPUT_DIR = BASE_OUTPUT_DIR / MODEL_FOLDER
RUNS_DIR = OUTPUT_DIR / "runs_16"
CSV_FILE = OUTPUT_DIR / "benchmark_results_16.csv"
JSONL_FILE = OUTPUT_DIR / "benchmark_results_16.jsonl"

# Ensure isolated directories exist
RUNS_DIR.mkdir(parents=True, exist_ok=True)


def load_prompt() -> str:
    """Reads the exact challenge prompt from markdown file."""
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found at: {PROMPT_FILE}")
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def evaluate_python_code(code_str: str) -> tuple[int, str]:
    """Evaluates code quality (0-100) via AST parsing and validation rules."""
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


def generate_fractional_16_design() -> list[dict]:
    """
    Generates Resolution V Fractional Factorial Matrix (2^(5-1) = 16 runs).
    Generator: x5 = (x1 + x2 + x3 + x4) % 2 (in GF(2)).
    """
    experiments = []
    run_idx = 1

    for x1 in [0, 1]:  # num_ctx: 0=default, 1=2048
        for x2 in [0, 1]:  # suppress_thinking: 0=none, 1=strict_system
            for x3 in [0, 1]:  # greedy: 0=temp 0.7, 1=temp 0.0 + top_k 1
                for x4 in [0, 1]:  # thread_affinity: 0=default, 1=8 cores
                    # Resolution V generator:
                    x5 = (x1 + x2 + x3 + x4) % 2  # budget_cap: 0=default, 1=600 tokens

                    tags = []
                    opts = {}
                    system_prompt = None

                    if x1 == 1:
                        opts["num_ctx"] = 2048
                        tags.append("ctx2048")
                    else:
                        tags.append("ctxDef")

                    if x2 == 1:
                        system_prompt = "You are a Python compiler. Output pure code only. Do not use <think> tags. Do not explain."
                        tags.append("noThink")
                    else:
                        tags.append("stdThink")

                    if x3 == 1:
                        opts["temperature"] = 0.0
                        opts["top_k"] = 1
                        opts["top_p"] = 1.0
                        tags.append("greedy")
                    else:
                        tags.append("sampTemp07")

                    if x4 == 1:
                        opts["num_thread"] = 8
                        tags.append("thr8")
                    else:
                        tags.append("thrDef")

                    if x5 == 1:
                        opts["num_predict"] = 600
                        opts["stop"] = ["<|im_end|>", "\n# Example", "```\n"]
                        tags.append("cap600")
                    else:
                        tags.append("capDef")

                    exp_id = f"exp16_{run_idx:02d}_" + "_".join(tags)
                    experiments.append({
                        "run_index": run_idx,
                        "id": exp_id,
                        "name": f"DoE #{run_idx:02d} ({'/'.join(tags)})",
                        "flags": {
                            "flag_num_ctx_2048": x1,
                            "flag_suppress_thinking": x2,
                            "flag_greedy_decoding": x3,
                            "flag_thread_affinity_8": x4,
                            "flag_budget_cap_600": x5
                        },
                        "options": opts,
                        "system": system_prompt
                    })
                    run_idx += 1

    return experiments


def append_record_atomic(record: dict):
    """Appends record immediately to CSV and JSONL with explicit flush."""
    # JSONL
    with open(JSONL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()

    # CSV
    csv_exists = CSV_FILE.exists() and CSV_FILE.stat().st_size > 0
    keys = list(record.keys())

    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if not csv_exists:
            writer.writeheader()
        writer.writerow(record)
        f.flush()


def run_experiment(exp: dict, prompt: str, model_name: str) -> dict:
    """Executes single test against Ollama, saves raw code and records tabular record."""
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": exp.get("options", {})
    }
    if exp.get("system"):
        payload["system"] = exp["system"]

    print(f"[{exp['run_index']:02d}/16] 🚀 Running: {exp['name']}...")
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

    # Save raw unedited code
    output_py_file = RUNS_DIR / f"{exp['id']}.py"
    with open(output_py_file, "w", encoding="utf-8") as f:
        f.write(raw_response)

    # Automated Quality Score
    score, feedback = evaluate_python_code(raw_response)

    # Record Schema
    record = {
        "timestamp_iso": datetime.now().isoformat(),
        "run_index": exp["run_index"],
        "run_id": exp["id"],
        "model_name": model_name,
        **exp["flags"],  # Binary 0/1 features for Machine Learning
        "prompt_tokens": prompt_count,
        "prompt_tps": round(prompt_tps, 2),
        "eval_tokens": eval_count,
        "eval_tps": round(eval_tps, 2),
        "wall_time_sec": round(wall_sec, 2),
        "auto_score": score,
        "auto_feedback": feedback,
        "output_file": str(output_py_file.relative_to(BASE_DIR))
    }

    # Immediate Atomic Save
    append_record_atomic(record)

    print(f"        ⏱️ Speed: {eval_tps:.2f} t/s | Latency: {wall_sec:.2f}s | Score: {score}/100 [Saved]")
    return record


def get_executed_run_ids() -> set[str]:
    """Reads existing CSV to see which parameter combinations have already been benchmarked."""
    if not CSV_FILE.exists() or CSV_FILE.stat().st_size == 0:
        return set()
    executed = set()
    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if "run_id" in r:
                executed.add(r["run_id"])
    return executed


def main():
    prompt = load_prompt()
    requested_runs = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    
    all_experiments = generate_fractional_16_design()
    executed_ids = get_executed_run_ids()
    existing_count = len(executed_ids)

    # Filter out experiments that were already run
    unexecuted = [e for e in all_experiments if e["id"] not in executed_ids]

    if not unexecuted:
        print(f"ℹ️ All 16 DoE parameter space combinations already executed ({existing_count} total). Performing next round of high-order replicates...", flush=True)
        unexecuted = all_experiments

    # Select the next complementary batch of experiments
    experiments = unexecuted[:requested_runs]
    for i, e in enumerate(experiments):
        e["run_index"] = existing_count + i + 1

    print("=" * 75, flush=True)
    print(f"🧪 EXECUTING COMPLEMENTARY DoE BENCHMARK ({len(experiments)} RUNS)", flush=True)
    print(f"Target Model  : {MODEL_NAME}", flush=True)
    print(f"Previously Run: {existing_count} points in parameter space", flush=True)
    print(f"New Points    : {len(experiments)} unvisited points", flush=True)
    print(f"CSV Storage   : {CSV_FILE}", flush=True)
    print("=" * 75, flush=True)

    records = []
    for exp in experiments:
        try:
            print(f"[{exp['run_index']:02d}/{existing_count + len(experiments)}] 🚀 Running: {exp['name']}...", flush=True)
            r = run_experiment(exp, prompt, MODEL_NAME)
            records.append(r)
        except Exception as e:
            print(f"❌ Error in {exp['name']}: {e}", flush=True)

    # Summary Table
    print("\n" + "=" * 75, flush=True)
    print(f"📊 DoE BENCHMARK SUMMARY TABLE: {MODEL_NAME}", flush=True)
    print("=" * 75 + "\n", flush=True)
    print("| # | Run ID | Tokens/s | Latência | Nota (0-100) | Avaliação |", flush=True)
    print("| :---: | :--- | :---: | :---: | :---: | :--- |", flush=True)
    for r in records:
        print(f"| {r['run_index']:02d} | **{r['run_id']}** | **{r['eval_tps']} t/s** | **{r['wall_time_sec']}s** | **{r['auto_score']}/100** | {r['auto_feedback']} |", flush=True)

    print("\n✅ Dataset gravado com sucesso em:", CSV_FILE, flush=True)


if __name__ == "__main__":
    main()
