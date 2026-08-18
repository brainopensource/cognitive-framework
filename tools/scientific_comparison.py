#!/usr/bin/env python3
"""Rigorous Scientific Comparison across 3 Ollama Models with Identical Inputs.

Task: Implement a thread-safe Rate Limiter (Token Bucket algorithm) with
refill rate, capacity, concurrency locking, and telemetry.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

TASK_BRIEF_MD = """# Problem Specification: Token Bucket Rate Limiter

## Goal
Implement a thread-safe `TokenBucketRateLimiter` class in Python.

## Requirements:
1. `__init__(self, capacity: int, refill_rate_per_sec: float)`: Initialize bucket with max capacity and refill rate in tokens per second.
2. `acquire(self, tokens: int = 1) -> bool`: Atomically check and consume tokens. If enough tokens are available, return True and decrement; otherwise return False.
3. Thread-safety: Must use `threading.Lock` or `threading.RLock`.
4. Token Refill: Tokens must refill continuously based on elapsed time (`time.monotonic()` or `time.time()`).
5. Metrics: Track total `allowed_requests` and `denied_requests`.
"""

SYSTEM_PROMPT = """You are a Principal Software Engineer at Vanguard. 
Implement the requested Python class cleanly, without unnecessary markdown fluff, with complete thread safety and accurate timing logic.
"""

UNIT_TEST_CODE = """import unittest
import time
import threading
from solution import TokenBucketRateLimiter

class TestTokenBucket(unittest.TestCase):
    def test_basic_acquire_and_capacity(self):
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate_per_sec=10.0)
        self.assertTrue(limiter.acquire(5))
        self.assertFalse(limiter.acquire(1))
        self.assertEqual(limiter.allowed_requests, 1)
        self.assertEqual(limiter.denied_requests, 1)

    def test_refill_over_time(self):
        limiter = TokenBucketRateLimiter(capacity=2, refill_rate_per_sec=10.0)
        self.assertTrue(limiter.acquire(2))
        self.assertFalse(limiter.acquire(1))
        time.sleep(0.25) # 0.25s * 10 tokens/s = 2.5 tokens refilled (capped at 2)
        self.assertTrue(limiter.acquire(2))

    def test_thread_safety(self):
        limiter = TokenBucketRateLimiter(capacity=100, refill_rate_per_sec=0.0)
        threads = []
        for _ in range(10):
            t = threading.Thread(target=lambda: [limiter.acquire(1) for _ in range(10)])
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(limiter.allowed_requests, 100)
        self.assertFalse(limiter.acquire(1))

if __name__ == '__main__':
    unittest.main()
"""

# Pricing estimates per 1M tokens (USD)
PRICING_ESTIMATES = {
    "qwen2.5:1.5b": {"prompt_per_1m": 0.05, "completion_per_1m": 0.10},
    "deepseek-r1:14b": {"prompt_per_1m": 0.20, "completion_per_1m": 0.80},
    "qwen3.6:27b": {"prompt_per_1m": 0.35, "completion_per_1m": 1.40},
}


def call_ollama(model: str, prompt: str, system: str) -> dict[str, Any]:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 1024,
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    duration = time.perf_counter() - start

    eval_count = data.get("eval_count", 0)
    prompt_eval_count = data.get("prompt_eval_count", 0)
    eval_duration_ns = data.get("eval_duration", 1)
    prompt_eval_duration_ns = data.get("prompt_eval_duration", 1)

    gen_tps = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else 0
    prompt_tps = (prompt_eval_count / (prompt_eval_duration_ns / 1e9)) if prompt_eval_duration_ns > 0 else 0

    return {
        "model": model,
        "total_latency_s": round(duration, 3),
        "eval_count": eval_count,
        "prompt_eval_count": prompt_eval_count,
        "tokens_per_sec": round(gen_tps, 2),
        "prompt_tokens_per_sec": round(prompt_tps, 2),
        "raw_response": data.get("response", ""),
    }


def extract_python_code(text: str) -> str:
    # Look for ```python ... ```
    match = re.search(r"```(?:python)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def evaluate_code(code_str: str) -> tuple[int, str]:
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        (ws / "solution.py").write_text(code_str, encoding="utf-8")
        (ws / "test_solution.py").write_text(UNIT_TEST_CODE, encoding="utf-8")
        res = subprocess.run([sys.executable, "-m", "unittest", "test_solution.py"], cwd=ws, capture_output=True, text=True)
        return res.returncode, (res.stderr or res.stdout).strip()


def main():
    models = ["qwen2.5:1.5b", "deepseek-r1:14b", "qwen3.6:27b"]
    results = []

    print("=== SCIENTIFIC EVALUATION ACROSS 3 MODELS ===")
    print(f"IDENTICAL INPUT PROMPT TO ALL MODELS:\n{TASK_BRIEF_MD}\n")

    for model in models:
        print(f"Testing model: {model}...")
        try:
            raw_res = call_ollama(model, TASK_BRIEF_MD, SYSTEM_PROMPT)
            code = extract_python_code(raw_res["raw_response"])
            exit_code, test_output = evaluate_code(code)
            
            # Score
            score = 10 if exit_code == 0 else 0
            if exit_code != 0 and "TokenBucketRateLimiter" in code:
                score = 5 # partial credit if structure exists but test failed

            # Estimate cost
            pricing = PRICING_ESTIMATES.get(model, {"prompt_per_1m": 0.1, "completion_per_1m": 0.5})
            cost_usd = (
                (raw_res["prompt_eval_count"] / 1_000_000.0) * pricing["prompt_per_1m"]
                + (raw_res["eval_count"] / 1_000_000.0) * pricing["completion_per_1m"]
            )

            results.append({
                "model": model,
                "latency_s": raw_res["total_latency_s"],
                "gen_tps": raw_res["tokens_per_sec"],
                "prompt_tps": raw_res["prompt_tokens_per_sec"],
                "prompt_tokens": raw_res["prompt_eval_count"],
                "completion_tokens": raw_res["eval_count"],
                "cost_usd": round(cost_usd, 7),
                "test_pass": exit_code == 0,
                "score": score,
                "kpi_quality_per_sec": round(score / max(raw_res["total_latency_s"], 0.001), 3),
                "extracted_code": code,
                "raw_response": raw_res["raw_response"],
            })
            print(f"  -> Exit Code: {exit_code} (Pass: {exit_code == 0}) | Latency: {raw_res['total_latency_s']}s | Cost: ${cost_usd:.6f}")
        except Exception as exc:
            print(f"  -> Error testing {model}: {exc}")

    out_file = Path(__file__).resolve().parents[1] / "scientific_comparison_results.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved scientific results to: {out_file}")


if __name__ == "__main__":
    main()
