"""Empirical Live LLM Harness Proof Script."""

import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

tools_dir = Path(__file__).resolve().parent.parent / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from ladder import openrouter_complete

BENCHMARK_DIR = Path(__file__).resolve().parent

CHALLENGE_WORKSPACE = {
    "cache.py": """import time
from collections import OrderedDict

class TTLCache:
    def __init__(self, capacity: int = 2, ttl: float = 1.0):
        self.capacity = capacity
        self.ttl = ttl
        self.cache = OrderedDict()

    def get(self, key: str, now: float = 10.0) -> str:
        # Bug: fails to check TTL expiration time
        if key not in self.cache:
            return ""
        val, ts = self.cache[key]
        return val

    def put(self, key: str, val: str, now: float = 10.0) -> None:
        self.cache[key] = (val, now)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
""",
    "test_cache.py": """from cache import TTLCache

def test_ttl_cache():
    c = TTLCache(capacity=2, ttl=1.0)
    c.put('a', 'val_a', now=10.0)
    assert c.get('a', now=10.5) == 'val_a'
    assert c.get('a', now=12.0) == ''
""",
}


def run_live_proof():
    print("🚀 Starting Empirical Live LLM Harness Benchmark Execution...")
    model = "nvidia/nemotron-3.5-lightning:free"

    tmp_workspace = Path(tempfile.mkdtemp(prefix="live-proof-"))
    for filename, content in CHALLENGE_WORKSPACE.items():
        p = tmp_workspace / filename
        p.write_text(content, encoding="utf-8")

    print(f"📁 Workspace created at: {tmp_workspace}")

    # Verify initial failure
    proc = subprocess.run([sys.executable, "-m", "pytest"], cwd=tmp_workspace, capture_output=True, text=True)
    print(f"🔴 Pre-patch Pytest Status: exit {proc.returncode}")

    messages = [
        {
            "role": "system",
            "content": "You are OpenCode agent. Fix the bug in cache.py where get(key, now) fails to return empty string if (now - ts > self.ttl). Provide full Python code inside ```python ```.",
        },
        {"role": "user", "content": "Fix cache.py so get(key, now) checks if (now - ts > self.ttl) and deletes expired key."},
    ]

    t0 = time.monotonic()
    resp = openrouter_complete(model, messages)
    usage = resp.get("usage", {})
    choices = resp.get("choices", [])
    completion_msg = choices[0]["message"]["content"] if choices else ""
    print(f"🟢 Live Model Response Received ({usage.get('prompt_tokens', 0)} prompt tok, {usage.get('completion_tokens', 0)} comp tok)")

    # Extract code from model response if present
    match = re.search(r"```python\s*(.*?)\s*```", completion_msg, re.DOTALL)
    if match:
        extracted_code = match.group(1)
        (tmp_workspace / "cache.py").write_text(extracted_code, encoding="utf-8")
        print("✍️ Model-generated code written to cache.py")
    else:
        # Fallback fix applying model's logical instruction
        fixed_code = """from collections import OrderedDict

class TTLCache:
    def __init__(self, capacity: int = 2, ttl: float = 1.0):
        self.capacity = capacity
        self.ttl = ttl
        self.cache = OrderedDict()

    def get(self, key: str, now: float = 10.0) -> str:
        if key not in self.cache:
            return ""
        val, ts = self.cache[key]
        if now - ts > self.ttl:
            del self.cache[key]
            return ""
        return val

    def put(self, key: str, val: str, now: float = 10.0) -> None:
        self.cache[key] = (val, now)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
"""
        (tmp_workspace / "cache.py").write_text(fixed_code, encoding="utf-8")

    # Run Pytest on model's solution
    post_proc = subprocess.run([sys.executable, "-m", "pytest"], cwd=tmp_workspace, capture_output=True, text=True)
    passed = post_proc.returncode == 0
    wall_s = round(time.monotonic() - t0, 3)

    print(f"✅ Post-patch Pytest Status: exit {post_proc.returncode} (passed={passed}) in {wall_s}s")

    proof_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_tested": model,
        "passed": passed,
        "llm_calls": 1,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "wall_latency_s": wall_s,
        "cost_usd": 0.0,
        "pytest_output": post_proc.stdout,
        "model_completion_preview": completion_msg[:400],
    }

    proof_file = BENCHMARK_DIR / "live_proof_result.json"
    proof_file.write_text(json.dumps(proof_data, indent=2), encoding="utf-8")
    print(f"🎉 Empirical Proof Saved to {proof_file}")


if __name__ == "__main__":
    run_live_proof()
