"""Refinement benchmark runner across OpenRouter free models."""

from __future__ import annotations

import datetime
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

# Add router directory
repo_root = Path(__file__).resolve().parents[3]
router_dir = repo_root / "tools" / "001_LLM_API_ROUTER"
sys.path.insert(0, str(router_dir))
from providers.openrouter import OpenRouterProvider

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EASY_PROMPT = """Write a Python function named `remove_duplicates(items: list) -> list` that removes duplicates from a list while strictly preserving the original order of first occurrence.
Requirements:
1. Preserve first-seen order.
2. Safely handle empty lists and duplicates.
3. Keep under 15 lines of clean code.
4. Output only code and docstring."""

HARD_PROMPT = """Write a Python function named `topological_sort(graph: dict[str, list[str]]) -> tuple[list[str], list[str] | None]` that returns a topological order of dependency keys.
Requirements:
1. If a valid DAG, return `(sorted_nodes, None)`.
2. If a cycle exists, return `([], cycle_nodes)` listing the cycle path nodes.
3. Correctly handle disconnected subgraphs and leaf nodes.
4. Keep under 45 lines of clean Python.
5. Output only code and docstring."""

CANDIDATE_FREE_MODELS = [
    "openrouter/free",
    "liquid/lfm-2.5-2.6b:free",
    "google/gemma-4-26b-a4b-it:free",
    "deepseek/deepseek-chat",
    "google/gemini-2.0-flash-001",
]


def run_benchmark():
    provider = OpenRouterProvider()
    if not provider.api_key:
        print("[ERROR] No OPENROUTER_API_KEY available.")
        return

    results = []

    print(f"=== Starting OpenRouter Refinement Benchmark ({len(CANDIDATE_FREE_MODELS)} candidate models) ===")

    for model in CANDIDATE_FREE_MODELS:
        print(f"\n--- Testing Model: {model} ---")

        # 1. Easy Task
        print("  Running Easy Task (Array Deduplication)...", end="", flush=True)
        easy_res = provider.generate(prompt=EASY_PROMPT, model=model, temperature=0.0)
        if easy_res.error:
            print(f" ❌ Failed: {easy_res.error[:80]}")
        else:
            print(f" ✔ Success ({easy_res.latency_ms}ms, {easy_res.total_tokens} tokens)")

        # 2. Hard Task
        print("  Running Hard Task (Topological Sort + Cycle Path)...", end="", flush=True)
        hard_res = provider.generate(prompt=HARD_PROMPT, model=model, temperature=0.0)
        if hard_res.error:
            print(f" ❌ Failed: {hard_res.error[:80]}")
        else:
            print(f" ✔ Success ({hard_res.latency_ms}ms, {hard_res.total_tokens} tokens)")

        record = {
            "model": model,
            "easy": {
                "ok": easy_res.error is None,
                "error": easy_res.error,
                "latency_ms": easy_res.latency_ms,
                "ttft_ms": easy_res.ttft_ms,
                "tokens": easy_res.total_tokens,
                "content": easy_res.content,
            },
            "hard": {
                "ok": hard_res.error is None,
                "error": hard_res.error,
                "latency_ms": hard_res.latency_ms,
                "ttft_ms": hard_res.ttft_ms,
                "tokens": hard_res.total_tokens,
                "content": hard_res.content,
            },
        }
        results.append(record)

        # Save individual model output
        clean_name = model.replace("/", "_").replace(":", "_")
        model_out = OUTPUT_DIR / f"{clean_name}.json"
        model_out.write_text(json.dumps(record, indent=2), encoding="utf-8")
        time.sleep(1)  # Rate limit safety

    # Save summary manifest
    summary_path = OUTPUT_DIR / "refinement_summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n🎉 Refinement benchmark complete! Results saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    run_benchmark()
