"""Opus-tier hard challenge benchmark for DeepSeek V4 Flash."""

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

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OPUS_HARD_PROMPT = """Write a complete, production-grade Persistent Immutable AVL Tree in Python with Structural Sharing and Snapshot Rollback.

Requirements:
1. **Immutability & Structural Sharing**: Nodes must be immutable (e.g. `@dataclass(frozen=True)`). `insert(key, value)` and `delete(key)` must return a new root node in O(log N) time using path copying (reusing all unaffected subtrees without cloning).
2. **Strict AVL Balance**: Maintain standard AVL balance factor invariants (-1, 0, 1) using immutable single and double rotations (Left-Left, Right-Right, Left-Right, Right-Left) in O(1) per rotation.
3. **Range Query**: `range_query(root, low, high) -> list[tuple[K, V]]` returning key-value pairs within [low, high] in O(log N + K) time.
4. **Snapshot Manager**: Implement `TreeHistory` class that stores roots by version ID/timestamp and allows rolling back or branching from any prior version.
5. **Robustness**: Handle duplicate key updates, deleting non-existent keys, and edge cases.
6. Provide clear type hints, concise docstrings, and embedded unit tests verifying immutability and balance invariants."""


def run():
    provider = OpenRouterProvider()
    model = "deepseek/deepseek-v4-flash"

    print(f"==================================================")
    print(f"Testing DeepSeek V4 Flash [{model}] on Opus-Level Challenge")
    print(f"==================================================")
    print("Sending prompt to OpenRouter...", flush=True)

    t0 = time.monotonic()
    res = provider.generate(prompt=OPUS_HARD_PROMPT, model=model, temperature=0.0)
    dur = int((time.monotonic() - t0) * 1000)

    if res.error:
        print(f"\n❌ Error with {model}: {res.error}")
        # Try fallback to deepseek-v4-flash-0731 or deepseek-v4-pro if alias not resolved
        for alt_model in ["deepseek/deepseek-v4-flash-0731", "deepseek/deepseek-v4-pro", "deepseek/deepseek-chat"]:
            print(f"\nRetrying with alternative model: {alt_model}...")
            res = provider.generate(prompt=OPUS_HARD_PROMPT, model=alt_model, temperature=0.0)
            if not res.error:
                model = alt_model
                break

    if res.error:
        print(f"\n❌ All attempts failed: {res.error}")
        return

    print(f"\n✔ Success! Generated in {res.latency_ms}ms ({res.total_tokens} tokens, cost: {res.cost_usd_micros} µUSD)")
    print("\n--- Model Response Preview (First 500 chars) ---")
    print(res.content[:500])
    print("...")

    # Save artifact
    clean_name = f"opus_challenge_{model.replace('/', '_')}"
    out_file = OUTPUT_DIR / f"{clean_name}.md"
    meta_file = OUTPUT_DIR / f"{clean_name}_meta.json"

    out_file.write_text(res.content, encoding="utf-8")
    meta_file.write_text(
        json.dumps(
            {
                "model": model,
                "latency_ms": res.latency_ms,
                "ttft_ms": res.ttft_ms,
                "tokens": res.total_tokens,
                "prompt_tokens": res.prompt_tokens,
                "completion_tokens": res.completion_tokens,
                "cost_usd_micros": res.cost_usd_micros,
                "cost_usd": res.cost_usd_micros / 1_000_000.0,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nSaved full code to {out_file}")


if __name__ == "__main__":
    run()
