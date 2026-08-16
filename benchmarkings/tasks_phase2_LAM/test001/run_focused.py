"""Multi-model comparative benchmark across OpenRouter Free, Cheap Cloud, and Local Ollama."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Add router directory
repo_root = Path(__file__).resolve().parents[3]
router_dir = repo_root / "tools" / "001_LLM_API_ROUTER"
sys.path.insert(0, str(router_dir))
from providers.openrouter import OpenRouterProvider
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
2. If a cycle exists, return `([], cycle_nodes)` listing the cycle path nodes.
3. Correctly handle disconnected subgraphs and leaf nodes.
4. Keep under 45 lines of clean Python.
5. Output only code and docstring."""

MODELS_CONFIG = [
    {"provider": "openrouter", "model": "openrouter/free", "label": "Tier 2 (OpenRouter Free Router)"},
    {"provider": "openrouter", "model": "deepseek/deepseek-chat", "label": "Tier 3 (DeepSeek V3 Chat)"},
    {"provider": "openrouter", "model": "google/gemini-2.0-flash-001", "label": "Tier 4 (Gemini 2.0 Flash)"},
    {"provider": "ollama", "model": "qwen2.5:1.5b", "label": "Tier 1 (Local Ollama Qwen 2.5 1.5B)"},
]


def run_all():
    or_provider = OpenRouterProvider()
    ol_provider = OllamaProvider()

    all_results = []

    for cfg in MODELS_CONFIG:
        p_name = cfg["provider"]
        model = cfg["model"]
        label = cfg["label"]
        prov = or_provider if p_name == "openrouter" else ol_provider

        print(f"\n==================================================")
        print(f"Testing {label} [{model}]")
        print(f"==================================================")

        # Easy Task
        print(" -> Running Easy Task...", end="", flush=True)
        easy_res = prov.generate(prompt=EASY_PROMPT, model=model, temperature=0.0)
        if easy_res.error:
            print(f" ❌ Error: {easy_res.error}")
        else:
            print(f" ✔ {easy_res.latency_ms}ms, {easy_res.total_tokens} tokens")

        # Hard Task
        print(" -> Running Hard Task...", end="", flush=True)
        hard_res = prov.generate(prompt=HARD_PROMPT, model=model, temperature=0.0)
        if hard_res.error:
            print(f" ❌ Error: {hard_res.error}")
        else:
            print(f" ✔ {hard_res.latency_ms}ms, {hard_res.total_tokens} tokens")

        record = {
            "label": label,
            "provider": p_name,
            "model": model,
            "easy": {
                "ok": easy_res.error is None,
                "latency_ms": easy_res.latency_ms,
                "ttft_ms": easy_res.ttft_ms,
                "tokens": easy_res.total_tokens,
                "prompt_tokens": easy_res.prompt_tokens,
                "completion_tokens": easy_res.completion_tokens,
                "cost_usd_micros": easy_res.cost_usd_micros,
                "content": easy_res.content,
            },
            "hard": {
                "ok": hard_res.error is None,
                "latency_ms": hard_res.latency_ms,
                "ttft_ms": hard_res.ttft_ms,
                "tokens": hard_res.total_tokens,
                "prompt_tokens": hard_res.prompt_tokens,
                "completion_tokens": hard_res.completion_tokens,
                "cost_usd_micros": hard_res.cost_usd_micros,
                "content": hard_res.content,
            },
        }
        all_results.append(record)

        clean_name = f"{p_name}_{model.replace('/', '_').replace(':', '_')}"
        (OUTPUT_DIR / f"{clean_name}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        time.sleep(0.5)

    summary_file = OUTPUT_DIR / "refinement_summary.json"
    summary_file.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\n🎉 Finished! Saved all outputs to {summary_file}")


if __name__ == "__main__":
    run_all()
