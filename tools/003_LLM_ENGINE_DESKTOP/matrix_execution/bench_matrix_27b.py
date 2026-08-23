#!/usr/bin/env python3
"""
Targeted Memory Spillover & Multi-Thread Benchmark for Qwen 3.8 27B on AMD Radeon 16GB.
Location: tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix_27b.py
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

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "docs" / "prompts" / "fibo_challenge_finetune.md"
OUTPUT_DIR = BASE_DIR / "bench_finetune" / "qwen_38_27B"
RUNS_DIR = OUTPUT_DIR / "runs_spillover"
CSV_FILE = OUTPUT_DIR / "benchmark_results_spillover.csv"
JSONL_FILE = OUTPUT_DIR / "benchmark_results_spillover.jsonl"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3.8:27b"

RUNS_DIR.mkdir(parents=True, exist_ok=True)


def load_prompt() -> str:
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


EXPERIMENTS_27B = [
    {"name": "Run 1 (ctx2k / 8 Cores / Greedy)", "ctx": 2048, "threads": 8, "temp": 0.0, "budget": 800},
    {"name": "Run 2 (ctx2k / 16 SMT Threads / Greedy)", "ctx": 2048, "threads": 16, "temp": 0.0, "budget": 800},
    {"name": "Run 3 (ctx2k / 4 Cores / Greedy)", "ctx": 2048, "threads": 4, "temp": 0.0, "budget": 800},
    {"name": "Run 4 (ctx4k / 8 Cores / Spillover Tier 1)", "ctx": 4096, "threads": 8, "temp": 0.0, "budget": 800},
    {"name": "Run 5 (ctx8k / 8 Cores / Spillover Tier 2)", "ctx": 8192, "threads": 8, "temp": 0.0, "budget": 800},
    {"name": "Run 6 (ctx16k / 16 Threads / Max Spillover)", "ctx": 16384, "threads": 16, "temp": 0.0, "budget": 800},
]


def append_record(record: dict):
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


def main():
    prompt = load_prompt()
    print("=" * 80)
    print(f"🔥 EXECUTING MEMORY SPILLOVER & CPU THREAD BENCHMARK ON {MODEL_NAME}")
    print(f"Hardware: AMD Radeon 16GB VRAM + AMD Ryzen 7 5800X3D (8C/16T)")
    print("=" * 80)

    records = []
    for idx, exp in enumerate(EXPERIMENTS_27B, start=1):
        opts = {
            "num_ctx": exp["ctx"],
            "num_thread": exp["threads"],
            "temperature": exp["temp"],
            "top_k": 1,
            "top_p": 1.0,
            "num_predict": exp["budget"],
            "stop": ["<|im_end|>", "\n# Example", "```\n"]
        }
        sys_prompt = "You are a Python compiler. Output pure code only. Do not use <think> tags. Do not explain."
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": opts,
            "system": sys_prompt
        }

        print(f"[{idx}/6] 🚀 Testing: {exp['name']} (ctx={exp['ctx']}, threads={exp['threads']})...")
        req = urllib.request.Request(
            OLLAMA_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        start = time.perf_counter()
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
        wall_sec = time.perf_counter() - start

        eval_count = res.get("eval_count", 0)
        eval_dur_sec = res.get("eval_duration", 1) / 1e9
        eval_tps = eval_count / eval_dur_sec if eval_dur_sec > 0 else 0
        raw_code = res.get("response", "")

        out_file = RUNS_DIR / f"run_27b_{idx:02d}_ctx{exp['ctx']}_thr{exp['threads']}.py"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(raw_code)

        score, feedback = evaluate_python_code(raw_code)

        record = {
            "timestamp_iso": datetime.now().isoformat(),
            "run_index": idx,
            "model_name": MODEL_NAME,
            "num_ctx": exp["ctx"],
            "num_thread": exp["threads"],
            "eval_tokens": eval_count,
            "eval_tps": round(eval_tps, 2),
            "wall_time_sec": round(wall_sec, 2),
            "auto_score": score,
            "auto_feedback": feedback,
            "output_file": str(out_file.relative_to(BASE_DIR))
        }
        append_record(record)
        records.append(record)
        print(f"       ⏱️ Speed: {eval_tps:.2f} t/s | Latency: {wall_sec:.2f}s | Score: {score}/100 [Saved]")

    print("\n" + "=" * 80)
    print("📊 27B MEMORY SPILLOVER & THREAD BENCHMARK SUMMARY")
    print("=" * 80)
    print("| # | Context Size | Threads CPU | Velocidade (TPS) | Latência Total | Nota AST |")
    print("| :-: | :----------: | :---------: | :--------------: | :------------: | :------: |")
    for r in records:
        print(f"| {r['run_index']:02d} | **{r['num_ctx']} tokens** | {r['num_thread']} threads | **{r['eval_tps']} t/s** | **{r['wall_time_sec']}s** | **{r['auto_score']}/100** |")

    print("\n✅ Resultados salvos em:", CSV_FILE)


if __name__ == "__main__":
    main()
