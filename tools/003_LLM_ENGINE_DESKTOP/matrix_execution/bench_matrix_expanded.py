#!/usr/bin/env python3
"""
High-Dimensional Multi-Scale Benchmark Matrix (LHS 16-Sample Cross-Check) for Ollama.
Location: tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix_expanded.py
Usage:
    python3 bench_matrix_expanded.py [MODEL_NAME]
"""

import ast
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import random
import sys
import time
import urllib.request

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "docs" / "prompts" / "fibo_challenge_finetune.md"
BASE_OUTPUT_DIR = BASE_DIR / "bench_finetune"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

DEFAULT_MODEL = "qwen2.5:1.5b"
MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL


def get_model_folder_name(model_name: str) -> str:
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
RUNS_DIR = OUTPUT_DIR / "runs_expanded"
CSV_FILE = OUTPUT_DIR / "benchmark_results_expanded.csv"
JSONL_FILE = OUTPUT_DIR / "benchmark_results_expanded.jsonl"

RUNS_DIR.mkdir(parents=True, exist_ok=True)


def load_prompt() -> str:
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found at: {PROMPT_FILE}")
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def evaluate_python_code(code_str: str) -> tuple[int, str]:
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


# 16-Sample Latin Hypercube Cross-Check Design across 5 Context Tiers & Hardware Threads
EXPANDED_16_EXPERIMENTS = [
    # Tier 1: Context 2048
    {"ctx": 2048, "threads": 8, "temp": 0.0, "min_p": 0.0, "rep_pen": 1.0, "think": True, "budget": 600},
    {"ctx": 2048, "threads": 4, "temp": 0.2, "min_p": 0.05, "rep_pen": 1.1, "think": False, "budget": 1000},
    {"ctx": 2048, "threads": 16, "temp": 0.7, "min_p": 0.0, "rep_pen": 1.0, "think": True, "budget": None},
    
    # Tier 2: Context 4096
    {"ctx": 4096, "threads": 8, "temp": 0.0, "min_p": 0.05, "rep_pen": 1.1, "think": True, "budget": 600},
    {"ctx": 4096, "threads": 16, "temp": 0.2, "min_p": 0.0, "rep_pen": 1.0, "think": False, "budget": 600},
    {"ctx": 4096, "threads": 4, "temp": 0.7, "min_p": 0.05, "rep_pen": 1.1, "think": True, "budget": 1000},
    
    # Tier 3: Context 8192
    {"ctx": 8192, "threads": 8, "temp": 0.2, "min_p": 0.0, "rep_pen": 1.1, "think": True, "budget": 600},
    {"ctx": 8192, "threads": 4, "temp": 0.0, "min_p": 0.05, "rep_pen": 1.0, "think": False, "budget": None},
    {"ctx": 8192, "threads": 16, "temp": 0.7, "min_p": 0.0, "rep_pen": 1.1, "think": True, "budget": 600},
    
    # Tier 4: Context 16384
    {"ctx": 16384, "threads": 8, "temp": 0.0, "min_p": 0.0, "rep_pen": 1.0, "think": True, "budget": 600},
    {"ctx": 16384, "threads": 16, "temp": 0.2, "min_p": 0.05, "rep_pen": 1.1, "think": False, "budget": 1000},
    {"ctx": 16384, "threads": 4, "temp": 0.7, "min_p": 0.0, "rep_pen": 1.0, "think": True, "budget": None},
    
    # Tier 5: Context 32768 (Full Window Scale)
    {"ctx": 32768, "threads": 8, "temp": 0.0, "min_p": 0.05, "rep_pen": 1.1, "think": True, "budget": 600},
    {"ctx": 32768, "threads": 4, "temp": 0.2, "min_p": 0.0, "rep_pen": 1.0, "think": False, "budget": 600},
    {"ctx": 32768, "threads": 16, "temp": 0.7, "min_p": 0.05, "rep_pen": 1.1, "think": True, "budget": 1000},
    
    # Validation Anchor (Golden Baseline)
    {"ctx": 2048, "threads": 8, "temp": 0.0, "min_p": 0.05, "rep_pen": 1.05, "think": True, "budget": 600}
]


def append_record_atomic(record: dict):
    with open(JSONL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()

    csv_exists = CSV_FILE.exists() and CSV_FILE.stat().st_size > 0
    keys = list(record.keys())

    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if not csv_exists:
            writer.writeheader()
        writer.writerow(record)
        f.flush()


def run_experiment(idx: int, cfg: dict, prompt: str, model_name: str) -> dict:
    opts = {
        "num_ctx": cfg["ctx"],
        "num_thread": cfg["threads"],
        "temperature": cfg["temp"],
        "min_p": cfg["min_p"],
        "repeat_penalty": cfg["rep_pen"]
    }
    if cfg["temp"] == 0.0:
        opts["top_k"] = 1
        opts["top_p"] = 1.0

    if cfg["budget"]:
        opts["num_predict"] = cfg["budget"]
        opts["stop"] = ["<|im_end|>", "\n# Example", "```\n"]

    system_prompt = "You are a Python compiler. Output pure code only. Do not use <think> tags. Do not explain." if cfg["think"] else None

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": opts
    }
    if system_prompt:
        payload["system"] = system_prompt

    tag = f"ctx{cfg['ctx']}_thr{cfg['threads']}_t{cfg['temp']}_minp{cfg['min_p']}_rp{cfg['rep_pen']}_{'noThk' if cfg['think'] else 'stdThk'}_{'cap'+str(cfg['budget']) if cfg['budget'] else 'unlim'}"
    exp_id = f"exp_exp_{idx:02d}_{tag}"

    print(f"[{idx:02d}/16] 🚀 Running: ctx={cfg['ctx']} | thr={cfg['threads']} | temp={cfg['temp']} | think={cfg['think']} | budget={cfg['budget']}...")
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

    output_py_file = RUNS_DIR / f"{exp_id}.py"
    with open(output_py_file, "w", encoding="utf-8") as f:
        f.write(raw_response)

    score, feedback = evaluate_python_code(raw_response)

    record = {
        "timestamp_iso": datetime.now().isoformat(),
        "run_index": idx,
        "run_id": exp_id,
        "model_name": model_name,
        "num_ctx": cfg["ctx"],
        "num_thread": cfg["threads"],
        "temperature": cfg["temp"],
        "min_p": cfg["min_p"],
        "repeat_penalty": cfg["rep_pen"],
        "suppress_thinking": 1 if cfg["think"] else 0,
        "budget_cap": cfg["budget"] if cfg["budget"] else 0,
        "prompt_tokens": prompt_count,
        "prompt_tps": round(prompt_tps, 2),
        "eval_tokens": eval_count,
        "eval_tps": round(eval_tps, 2),
        "wall_time_sec": round(wall_sec, 2),
        "auto_score": score,
        "auto_feedback": feedback,
        "output_file": str(output_py_file.relative_to(BASE_DIR))
    }

    append_record_atomic(record)
    print(f"        ⏱️ Speed: {eval_tps:.2f} t/s | Latency: {wall_sec:.2f}s | Score: {score}/100 [Saved]")
    return record


def main():
    prompt = load_prompt()
    print("=" * 80)
    print(f"🧪 MULTI-SCALE EXPANDED DoE MATRIX (2K TO 32K CONTEXT + RYZEN THREADS)")
    print(f"Target Model  : {MODEL_NAME}")
    print(f"Output Dir    : {OUTPUT_DIR}")
    print(f"Total Runs    : 16 Latin Hypercube Samples")
    print(f"CSV Storage   : {CSV_FILE}")
    print("=" * 80)

    records = []
    for idx, cfg in enumerate(EXPANDED_16_EXPERIMENTS, start=1):
        try:
            r = run_experiment(idx, cfg, prompt, MODEL_NAME)
            records.append(r)
        except Exception as e:
            print(f"❌ Error in Run #{idx}: {e}")

    print("\n" + "=" * 80)
    print(f"📊 EXPANDED DoE BENCHMARK SUMMARY TABLE: {MODEL_NAME}")
    print("=" * 80 + "\n")
    print("| # | Context | Cores | Temp | Think | Tokens/s | Latência | Nota |")
    print("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for r in records:
        print(f"| {r['run_index']:02d} | **{r['num_ctx']}** | {r['num_thread']}C | {r['temperature']} | {'Sim' if r['suppress_thinking']==1 else 'Não'} | **{r['eval_tps']} t/s** | **{r['wall_time_sec']}s** | **{r['auto_score']}** |")

    print("\n✅ Dataset expandido gravado em:", CSV_FILE)


if __name__ == "__main__":
    main()
