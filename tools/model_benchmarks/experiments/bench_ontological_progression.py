#!/usr/bin/env python3
"""
Empirical Benchmark: Ontological Progression Comparison
Compares 3 operational tiers using an under-powered local model (Qwen2.5-Coder-1.5B):
- Mode 0: Sem Skills/Techniques (Blind / Zero-Shot)
- Mode 1: Com Technique 1 (Spec-Driven CodeGen Open-Loop)
- Mode 2: Com Proficiency (Autofix SWE Closed Loop with Falsifiers & Multi-turn Feedback)
"""

import sys
import os
import re
import json
import time
import shutil
import urllib.request
import subprocess
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path("/home/rock-dev/Coding/cognitive-framework")
MODEL_PATH = "/home/rock-dev/Models/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf"
LLAMA_SERVER = "/home/rock-dev/.local/bin/llama-server"
HEALTH_URL = "http://127.0.0.1:8080/health"
COMPLETIONS_URL = "http://127.0.0.1:8080/v1/chat/completions"

FIXTURE_SRC = REPO_ROOT / "tools/model_benchmarks/fixtures/sliding_window_limiter.py"
FIXTURE_TEST = REPO_ROOT / "tools/model_benchmarks/fixtures/test_sliding_window_limiter.py"
TEST_CMD = f"python3 {FIXTURE_TEST}"

# Skill / Technique / Proficiency imports
RUN_TEST_SCRIPT = REPO_ROOT / ".agents/skills/test-runner/scripts/run_test.py"
T1_SCRIPT = REPO_ROOT / ".agents/techniques/spec-driven-codegen/scripts/generate_grounded_patch.py"
T2_SCRIPT = REPO_ROOT / ".agents/techniques/tdd-falsifier/scripts/run_falsifier.py"
PROFICIENCY_SCRIPT = REPO_ROOT / ".agents/proficiencies/autofix-swe-loop/scripts/autofix_harness.py"

sys.path.insert(0, str(RUN_TEST_SCRIPT.parent))
from run_test import run_isolated_test

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(1)

def ensure_server() -> subprocess.Popen:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=1) as resp:
            if json.loads(resp.read().decode()).get("status") == "ok":
                return None
    except Exception:
        pass

    kill_server()
    cmd = [
        LLAMA_SERVER,
        "-m", MODEL_PATH,
        "-c", "4096",
        "-ngl", "99",
        "--host", "127.0.0.1",
        "--port", "8080",
        "--alias", "local-model",
        "--reasoning", "off",
        "--jinja"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=1) as resp:
                if json.loads(resp.read().decode()).get("status") == "ok":
                    return proc
        except Exception:
            time.sleep(0.5)
    proc.kill()
    raise RuntimeError("Failed to start llama-server")

def reset_fixture():
    """Restores the seeded defect in the fixture file."""
    buggy_code = '''"""
Sliding Window Rate Limiter module.
Used as a benchmark fixture for SWE agent self-healing tests.
"""

from typing import List

class SlidingWindowLimiter:
    """
    Limits requests to max_requests within a rolling window_seconds.
    """
    def __init__(self, max_requests: int, window_seconds: float):
        if max_requests <= 0:
            raise ValueError("max_requests must be > 0")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps: List[float] = []

    def allow(self, now: float) -> bool:
        """
        Determines whether an action at timestamp `now` is permitted under rate limits.
        Any timestamp t where t <= (now - window_seconds) must be pruned.
        
        [SEEDED BUG]: Uses strict '<' instead of '<=', causing boundary events 
        at exactly (now - window_seconds) to linger and falsely throttle.
        Additionally, appends `now` before checking capacity!
        """
        cutoff = now - self.window_seconds
        # Bug: < instead of <= leaves boundary timestamps in the list
        self.timestamps = [t for t in self.timestamps if t > cutoff]
        
        # Bug: appends before checking length
        self.timestamps.append(now)
        if len(self.timestamps) > self.max_requests:
            return False
        return True

    def reset(self) -> None:
        self.timestamps.clear()
'''
    with open(FIXTURE_SRC, "w", encoding="utf-8") as f:
        f.write(buggy_code)

def run_mode_0_blind() -> Dict[str, Any]:
    print("\n" + "="*70)
    print("[MODE 0] Sem Skills/Techniques (Blind / Zero-Shot)")
    print("="*70)
    reset_fixture()
    
    t0 = time.time()
    blind_prompt = """You are a Python programmer.
Write a python class SlidingWindowLimiter with:
- __init__(max_requests: int, window_seconds: float)
- allow(now: float) -> bool
- reset() -> None
Make sure requests older than window_seconds are evicted, and denied requests do not consume quota.
Provide ONLY the python code inside ```python ... ```."""

    req_data = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": "You are a concise code assistant. Output only python code."},
            {"role": "user", "content": blind_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 800
    }
    
    t_llm0 = time.time()
    req = urllib.request.Request(
        COMPLETIONS_URL,
        data=json.dumps(req_data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        llm_resp = json.loads(resp.read().decode())
    t_llm = time.time() - t_llm0

    content = llm_resp["choices"][0]["message"]["content"]
    tokens = llm_resp.get("usage", {}).get("completion_tokens", 0)
    
    # Extract code
    code_match = re.search(r"```(?:python)?\s*\n?(.*?)(?:```|$)", content, re.DOTALL)
    code = code_match.group(1).strip() if code_match else content.strip()

    # Apply to fixture
    with open(FIXTURE_SRC, "w", encoding="utf-8") as f:
        f.write(code)

    # Test
    test_result = run_isolated_test(TEST_CMD, timeout=10.0)
    total_time = round(time.time() - t0, 3)

    return {
        "mode": "0_blind",
        "name": "Sem Skills (Blind / Zero-Shot)",
        "success": test_result["success"],
        "turns": 1,
        "total_tokens": tokens,
        "latency_seconds": total_time,
        "llm_latency": round(t_llm, 3),
        "test_status": test_result["summary"],
        "failure_reason": test_result["failures"][0]["traceback"].splitlines()[-1] if test_result.get("failures") else (
            test_result["stderr"].splitlines()[-1] if not test_result["success"] else "N/A"
        )
    }

def run_mode_1_technique() -> Dict[str, Any]:
    print("\n" + "="*70)
    print("[MODE 1] Com Technique 1 (Spec-Driven CodeGen Open-Loop)")
    print("="*70)
    reset_fixture()

    t0 = time.time()
    with open(FIXTURE_SRC, "r", encoding="utf-8") as f:
        current_code = f.read()

TASK_DESC = "Fix SlidingWindowLimiter: denied requests must not consume quota or be appended to timestamps, and boundary events at (now - window_seconds) must be evicted."

def run_mode_1_technique() -> Dict[str, Any]:
    print("\n" + "="*70)
    print("[MODE 1] Com Technique 1 (Spec-Driven CodeGen Open-Loop)")
    print("="*70)
    reset_fixture()

    t0 = time.time()
    with open(FIXTURE_SRC, "r", encoding="utf-8") as f:
        current_code = f.read()

    # Run Technique 1 via script
    cmd = [
        "python3", str(T1_SCRIPT),
        "--task", TASK_DESC,
        "--target-file", str(FIXTURE_SRC),
        "--no-auto-server",
        "--json"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        t1_out = json.loads(res.stdout)
    except Exception:
        print("T1 script failed to output JSON, stdout:", res.stdout, "stderr:", res.stderr)
        return {"mode": "1_technique", "name": "Com Technique 1 (Spec-Driven Open-Loop)", "success": False, "turns": 1, "total_tokens": 0, "latency_seconds": 0, "test_status": "SCRIPT_ERROR"}

    candidate_code = t1_out.get("generated_code", "")
    tokens = t1_out.get("completion_tokens", 0)

    # Apply candidate code to fixture
    with open(FIXTURE_SRC, "w", encoding="utf-8") as f:
        f.write(candidate_code)

    # Test open-loop (one shot, no feedback loop)
    test_result = run_isolated_test(TEST_CMD, timeout=10.0)
    total_time = round(time.time() - t0, 3)

    return {
        "mode": "1_technique",
        "name": "Com Technique 1 (Spec-Driven Open-Loop)",
        "success": test_result["success"],
        "turns": 1,
        "total_tokens": tokens,
        "latency_seconds": total_time,
        "llm_latency": t1_out.get("llm_latency", 0.0),
        "test_status": test_result["summary"],
        "failure_reason": test_result["failures"][0]["traceback"].splitlines()[-1] if test_result.get("failures") else (
            test_result["stderr"].splitlines()[-1] if not test_result["success"] else "N/A"
        )
    }

def run_mode_2_proficiency() -> Dict[str, Any]:
    print("\n" + "="*70)
    print("[MODE 2] Com Proficiency (Autofix SWE Closed Loop)")
    print("="*70)
    reset_fixture()

    t0 = time.time()
    
    cmd = [
        "python3", str(PROFICIENCY_SCRIPT),
        "--task", TASK_DESC,
        "--target-file", str(FIXTURE_SRC),
        "--test-cmd", TEST_CMD,
        "--max-turns", "3",
        "--json"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        prof_out = json.loads(res.stdout)
    except Exception as e:
        print("Proficiency script stdout:", res.stdout, "stderr:", res.stderr)
        return {"mode": "2_proficiency", "name": "Com Proficiency (Closed-Loop Autofix)", "success": False, "turns": 0, "total_tokens": 0, "latency_seconds": 0, "test_status": "SCRIPT_ERROR", "failure_reason": str(e)}

    success = prof_out.get("status") == "RESOLVED"
    return {
        "mode": "2_proficiency",
        "name": "Com Proficiency (Closed-Loop Autofix)",
        "success": success,
        "turns": prof_out.get("total_turns", 0),
        "total_tokens": prof_out.get("total_tokens", 0),
        "latency_seconds": prof_out.get("total_duration_seconds", 0.0),
        "test_status": "OK" if success else "FAILED_ROLLED_BACK",
        "failure_reason": "N/A (All tests passed)" if success else "Max turns exceeded without passing falsifier",
        "history": prof_out.get("history", [])
    }

def main():
    print("="*70)
    print("STARTING EMPIRICAL BENCHMARK: AGENT ONTOLOGICAL PROGRESSION")
    print("Hardware: AMD Radeon RX 9060 XT (Vulkan) | Model: Qwen2.5-Coder-1.5B (180 tok/s)")
    print("="*70)

    server_proc = ensure_server()
    results = []

    try:
        # Run all 3 modes
        r0 = run_mode_0_blind()
        results.append(r0)
        print(f"Result Mode 0: Success={r0['success']}, Latency={r0['latency_seconds']}s, Status={r0['test_status']}")

        r1 = run_mode_1_technique()
        results.append(r1)
        print(f"Result Mode 1: Success={r1['success']}, Latency={r1['latency_seconds']}s, Status={r1['test_status']}")

        r2 = run_mode_2_proficiency()
        results.append(r2)
        print(f"Result Mode 2: Success={r2['success']}, Turns={r2['turns']}, Latency={r2['latency_seconds']}s, Status={r2['test_status']}")

    finally:
        kill_server()
        reset_fixture()

    # Save results JSON
    out_json = REPO_ROOT / "tools/model_benchmarks/results/ontological_progression_benchmark.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*85)
    print("COMPARATIVE BENCHMARK RESULTS (Qwen2.5-Coder-1.5B Local Model)")
    print("="*85)
    header = f"| {'Abordagem / Paradigma':<40} | {'Status':<8} | {'Turns':<5} | {'Latência':<10} | {'Tokens':<8} |"
    sep = f"|{'-'*42}|{'-'*10}|{'-'*7}|{'-'*12}|{'-'*10}|"
    print(sep)
    print(header)
    print(sep)
    for r in results:
        status_sym = "PASS ✅" if r["success"] else "FAIL ❌"
        row = f"| {r['name']:<40} | {status_sym:<8} | {r['turns']:<5} | {r['latency_seconds']:<8.2f}s | {r['total_tokens']:<8} |"
        print(row)
    print(sep)

    print("\n[DETAILED ERROR ATTRIBUTION]")
    for r in results:
        print(f"• {r['name']}:")
        print(f"  Status: {r['test_status']}")
        print(f"  Diagnostics: {r.get('failure_reason', 'N/A')}")
        if r.get("history"):
            for h in r["history"]:
                print(f"    - Turn {h['turn']}: Falsifier={h['falsifier_status']} ({h['falsifier_summary']}) in {h['duration_seconds']}s")

if __name__ == "__main__":
    main()
