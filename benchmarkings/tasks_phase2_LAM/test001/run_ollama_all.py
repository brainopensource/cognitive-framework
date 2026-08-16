"""Exhaustive Local Ollama Benchmark across Tiers 1 and 2 models."""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

# Add router directory
repo_root = Path(__file__).resolve().parents[3]
router_dir = repo_root / "tools" / "001_LLM_API_ROUTER"
sys.path.insert(0, str(router_dir))
from providers.ollama import OllamaProvider

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
2. If a cycle exists, return `([], cycle_nodes)` listing the cycle path nodes in order.
3. Correctly handle disconnected subgraphs and leaf nodes.
4. Keep under 45 lines of clean Python.
5. Output only code and docstring."""

OLLAMA_MODELS = [
    {"model": "qwen2.5:1.5b", "tier": 1, "label": "Tier 1: Qwen 2.5 1.5B (Minimal)"},
    {"model": "llama3.2:3b", "tier": 1, "label": "Tier 1: Llama 3.2 3B (Small)"},
    {"model": "deepseek-r1:14b", "tier": 2, "label": "Tier 2: DeepSeek R1 14B (Reasoning)"},
    {"model": "qwen3.6:27b", "tier": 2, "label": "Tier 2: Qwen 3.6 27B (Large Mid)"},
]


def test_ollama_model(provider: OllamaProvider, model_info: dict) -> dict:
    model = model_info["model"]
    tier = model_info["tier"]
    label = model_info["label"]

    print(f"\n========================================================")
    print(f"Testing {label} [{model}]")
    print(f"========================================================")

    # 1. Easy Task
    print(" -> Running Easy Task (Array Deduplication)...", end="", flush=True)
    t0 = time.monotonic()
    easy_res = provider.generate(prompt=EASY_PROMPT, model=model, temperature=0.0)
    dur_easy = int((time.monotonic() - t0) * 1000)
    if easy_res.error:
        print(f" ❌ Error: {easy_res.error}")
    else:
        print(f" ✔ {dur_easy}ms, {easy_res.total_tokens} tokens")

    # 2. Hard Task
    print(" -> Running Hard Task (Topological Sort + Cycle)...", end="", flush=True)
    t0 = time.monotonic()
    hard_res = provider.generate(prompt=HARD_PROMPT, model=model, temperature=0.0)
    dur_hard = int((time.monotonic() - t0) * 1000)
    if hard_res.error:
        print(f" ❌ Error: {hard_res.error}")
    else:
        print(f" ✔ {dur_hard}ms, {hard_res.total_tokens} tokens")

    record = {
        "label": label,
        "tier": tier,
        "model": model,
        "easy": {
            "ok": easy_res.error is None,
            "error": easy_res.error,
            "latency_ms": easy_res.latency_ms,
            "tokens": easy_res.total_tokens,
            "prompt_tokens": easy_res.prompt_tokens,
            "completion_tokens": easy_res.completion_tokens,
            "content": easy_res.content,
        },
        "hard": {
            "ok": hard_res.error is None,
            "error": hard_res.error,
            "latency_ms": hard_res.latency_ms,
            "tokens": hard_res.total_tokens,
            "prompt_tokens": hard_res.prompt_tokens,
            "completion_tokens": hard_res.completion_tokens,
            "content": hard_res.content,
        },
    }

    clean_name = f"ollama_{model.replace('/', '_').replace(':', '_')}"
    out_path = OUTPUT_DIR / f"{clean_name}.json"
    out_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def main():
    provider = OllamaProvider()
    print(f"Connected to Ollama Host: {provider.host}")

    results = []
    for m in OLLAMA_MODELS:
        res = test_ollama_model(provider, m)
        results.append(res)

    summary_file = OUTPUT_DIR / "ollama_full_evaluation.json"
    summary_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n🎉 Finished all 4 Ollama local models! Saved to {summary_file}")


if __name__ == "__main__":
    main()
