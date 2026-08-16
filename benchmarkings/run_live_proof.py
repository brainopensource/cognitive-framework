"""Honest Zero-Hint Live LLM Harness Benchmark Execution."""

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

# Problem Workspace: Defect in get() where TTL condition isn't checked
CHALLENGE_WORKSPACE = {
    "cache.py": """import time
from collections import OrderedDict

class TTLCache:
    def __init__(self, capacity: int = 2, ttl: float = 1.0):
        self.capacity = capacity
        self.ttl = ttl
        self.cache = OrderedDict()

    def get(self, key: str, now: float = 10.0) -> str:
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


def run_honest_benchmark():
    print("🚀 Running Honest Zero-Hint Live LLM Benchmark (No Prompt Leakage)...")
    model = "nvidia/nemotron-3.5-lightning:free"

    tmp_workspace = Path(tempfile.mkdtemp(prefix="honest-proof-"))
    for filename, content in CHALLENGE_WORKSPACE.items():
        p = tmp_workspace / filename
        p.write_text(content, encoding="utf-8")

    print(f"📁 Workspace created at: {tmp_workspace}")

    # Step 1: Run pytest to capture baseline failure
    proc0 = subprocess.run([sys.executable, "-m", "pytest"], cwd=tmp_workspace, capture_output=True, text=True)
    print(f"🔴 Baseline Pytest Failure Captured (exit {proc0.returncode})")

    # Honest Zero-Hint Prompts: NO solution algorithm in the text!
    messages = [
        {
            "role": "system",
            "content": "You are OpenCode, an autonomous software engineering agent. Your objective is to inspect the workspace, diagnose failing unit tests, and fix the codebase.",
        },
        {
            "role": "user",
            "content": f"The test suite in test_cache.py is failing with stdout:\n{proc0.stdout}\nFix cache.py so all unit tests pass. Output the complete updated cache.py in a ```python ``` block.",
        },
    ]

    t0 = time.monotonic()
    resp = openrouter_complete(model, messages)
    usage = resp.get("usage", {})
    choices = resp.get("choices", [])
    completion_msg = choices[0]["message"]["content"] if choices else ""
    print(f"🟢 Live Model Response Received ({usage.get('prompt_tokens', 0)} prompt tok, {usage.get('completion_tokens', 0)} comp tok)")

    # Extract code from model output
    match = re.search(r"```python\s*(.*?)\s*```", completion_msg, re.DOTALL)
    if match:
        extracted_code = match.group(1)
        (tmp_workspace / "cache.py").write_text(extracted_code, encoding="utf-8")
        print("✍️ Model-generated patch written to cache.py")

    # Step 2: Run pytest to evaluate model patch
    post_proc = subprocess.run([sys.executable, "-m", "pytest"], cwd=tmp_workspace, capture_output=True, text=True)
    passed = post_proc.returncode == 0
    wall_s = round(time.monotonic() - t0, 3)

    print(f"✅ Honest Pytest Evaluation: exit {post_proc.returncode} (passed={passed}) in {wall_s}s")

    proof_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_tested": model,
        "prompt_leaks": "NONE (Zero-Hint Prompt)",
        "passed": passed,
        "llm_calls": 1,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "wall_latency_s": wall_s,
        "pytest_stdout": post_proc.stdout,
        "model_reasoning_preview": completion_msg[:500],
    }

    proof_file = BENCHMARK_DIR / "live_proof_result.json"
    proof_file.write_text(json.dumps(proof_data, indent=2), encoding="utf-8")
    print(f"🎉 Honest Proof Artifact Saved to {proof_file}")


if __name__ == "__main__":
    run_honest_benchmark()
