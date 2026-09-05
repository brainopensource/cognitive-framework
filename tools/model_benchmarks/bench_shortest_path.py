#!/usr/bin/env python3
"""Benchmark 7 local models on Shortest Path with K Obstacles (Level 6.0 Graph Search)."""

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

MODELS_DIR = Path("/home/rock-dev/Models")
LLAMA_SERVER = "/home/rock-dev/.local/bin/llama-server"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
HEALTH_URL = "http://127.0.0.1:8080/health"

MODELS_TO_BENCHMARK = [
    {
        "id": "qwen_1.5b",
        "name": "Qwen2.5-Coder-1.5B-Instruct",
        "tier": "Faixa 1 (1.5B) - Coding",
        "file": "Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf",
    },
    {
        "id": "deepseek_r1_1.5b",
        "name": "DeepSeek-R1-Distill-Qwen-1.5B",
        "tier": "Faixa 1 (1.5B) - Reasoning",
        "file": "DeepSeek-R1-Distill-Qwen-1.5B-Q4_K_M.gguf",
    },
    {
        "id": "qwen_3b",
        "name": "Qwen2.5-Coder-3B-Instruct",
        "tier": "Faixa 2 (3B) - Coding",
        "file": "Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf",
    },
    {
        "id": "phi4_mini",
        "name": "Phi-4-mini-instruct (3.8B)",
        "tier": "Faixa 2 (3.8B) - Reasoning",
        "file": "Phi-4-mini-instruct-Q4_K_M.gguf",
    },
    {
        "id": "deepseek_coder_v2_lite",
        "name": "DeepSeek-Coder-V2-Lite (16B MoE)",
        "tier": "Faixa 3 (16B MoE) - Coding",
        "file": "DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf",
    },
    {
        "id": "qwen_14b",
        "name": "Qwen2.5-Coder-14B-Instruct",
        "tier": "Faixa 3 (14B) - Coding",
        "file": "Qwen2.5-Coder-14B-Instruct-Q4_K_M.gguf",
    },
    {
        "id": "deepseek_r1_14b",
        "name": "DeepSeek-R1-Distill-Qwen-14B",
        "tier": "Faixa 3 (14B) - Reasoning",
        "file": "DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf",
    },
]

INITIAL_PROMPT = """Write a Python function `shortest_path_with_k`:

```python
def shortest_path_with_k(grid: list[list[int]], k: int) -> int:
    \"\"\"
    Finds the shortest path from top-left (0, 0) to bottom-right (m-1, n-1)
    in a 2D grid of 0s (empty) and 1s (obstacle).
    You can eliminate at most k obstacles along the path.
    Return the minimum number of steps to reach the target, or -1 if impossible.
    Steps count the number of moves between cells.
    \"\"\"
```
Requirements:
1. Uses BFS or Dijkstra to find the shortest path.
2. Properly handles edge cases (e.g. 1x1 grid, impossible paths).
3. Standard library only (collections.deque, heapq, etc.).
Output only the Python code block."""

TEST_HARNESS = """
def run_falsifiers(func):
    # 1. 2x2 empty grid
    assert func([[0, 0], [0, 0]], 0) == 2, "Failed Test 1: 2x2 empty grid must be 2"
    
    # 2. Path with obstacle requiring k=1
    grid1 = [
        [0, 0, 0],
        [1, 1, 0],
        [0, 0, 0],
        [0, 1, 1],
        [0, 0, 0]
    ]
    assert func(grid1, 1) == 6, "Failed Test 2: standard path with k=1 must be 6"
    
    # 3. Impossible path
    grid2 = [
        [0, 1, 1],
        [1, 1, 1],
        [1, 0, 0]
    ]
    assert func(grid2, 1) == -1, "Failed Test 3: blocked grid must be -1"
    
    # 4. 1x1 grid
    assert func([[0]], 0) == 0, "Failed Test 4: 1x1 grid must be 0"
    
    # 5. Trap grid (requires 3D state visited: (row, col, k_remaining))
    grid_trap = [
        [0, 0, 0, 0, 0],
        [1, 1, 0, 0, 1],
        [0, 1, 0, 1, 1],
        [0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0]
    ]
    assert func(grid_trap, 1) == 8, "Failed Test 5 (TRAP): path must be 8; check if your visited set tracks remaining k"
    return True

run_falsifiers(shortest_path_with_k)
print("TESTS_ALL_PASSED")
"""

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(2)

def start_server(model_path: Path):
    kill_server()
    cmd = [
        LLAMA_SERVER,
        "-m", str(model_path),
        "-c", "4096",
        "-ngl", "99",
        "--host", "127.0.0.1",
        "--port", "8080",
        "--alias", "local-model",
        "--reasoning", "off",
        "--jinja"
    ]
    print(f"\n[SERVER] Starting {model_path.name} (-c 4096, --reasoning off)...", flush=True)
    t0 = time.time()
    server_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    while time.time() - t0 < 90:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                if data.get("status") == "ok":
                    warmup_dur = time.time() - t0
                    print(f"[SERVER] Ready in {warmup_dur:.2f}s", flush=True)
                    return server_proc, warmup_dur
        except Exception:
            time.sleep(0.5)
            
    server_proc.kill()
    raise TimeoutError("Server failed to become healthy within 90s")

def extract_code(content: str) -> str:
    matches = re.findall(r"```(?:python)?\n(.*?)```", content, re.DOTALL)
    if matches:
        for m in matches:
            if "def shortest_path_with_k" in m:
                return m.strip()
        return matches[-1].strip()
    return content.strip()

def test_code_snippet(code_snippet: str) -> tuple[bool, str]:
    full_script = f"{code_snippet}\n{TEST_HARNESS}"
    try:
        proc = subprocess.run(
            ["python3", "-c", full_script],
            capture_output=True,
            text=True,
            timeout=5
        )
        if proc.returncode == 0 and "TESTS_ALL_PASSED" in proc.stdout:
            return True, "All 5 falsifiers passed!"
        else:
            err = proc.stderr.strip() or proc.stdout.strip()
            # Return last line of traceback
            lines = err.splitlines()
            relevant = "\n".join(lines[-4:]) if len(lines) >= 4 else err
            return False, relevant
    except subprocess.TimeoutExpired:
        return False, "Execution timed out (5s, potential infinite loop in BFS)"
    except Exception as e:
        return False, str(e)

def run_model_benchmark(model_info: dict) -> dict:
    model_path = MODELS_DIR / model_info["file"]
    if not model_path.exists():
        return {"name": model_info["name"], "error": f"File {model_info['file']} not found"}
        
    server_proc, warmup = start_server(model_path)
    
    conversation = [
        {"role": "user", "content": INITIAL_PROMPT}
    ]
    
    turns_data = []
    passed = False
    total_tokens = 0
    total_time = 0.0
    
    try:
        for turn_idx in range(1, 5):
            print(f"[TURN {turn_idx}] Querying {model_info['name']} (timeout 240s)...", flush=True)
            t0 = time.time()
            payload = {
                "model": "local-model",
                "messages": conversation,
                "temperature": 0.1,
                "max_tokens": 2048
            }
            req = urllib.request.Request(
                ENDPOINT,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=240) as resp:
                res = json.loads(resp.read().decode())
                
            dur = time.time() - t0
            total_time += dur
            usage = res.get("usage", {})
            comp_tokens = usage.get("completion_tokens", 0)
            total_tokens += comp_tokens
            speed = comp_tokens / dur if dur > 0 else 0.0
            msg_obj = res["choices"][0]["message"]
            content = msg_obj.get("content", "")
            reasoning = msg_obj.get("reasoning_content", "")
            
            code = extract_code(content)
            if not code and reasoning:
                code = extract_code(reasoning)
                
            success, message = test_code_snippet(code)
            print(f" -> Turn {turn_idx}: {comp_tokens} tok | {speed:.1f} t/s | {dur:.2f}s | Success: {success} | Details: {message[:100]}", flush=True)
            
            turns_data.append({
                "turn": turn_idx,
                "tokens": comp_tokens,
                "duration_sec": round(dur, 2),
                "tokens_sec": round(speed, 2),
                "success": success,
                "message": message,
                "code_sample": code[:150] + "..." if len(code) > 150 else code
            })
            
            if success:
                passed = True
                break
            else:
                feedback = (
                    f"Your implementation of shortest_path_with_k failed the automated tests:\n"
                    f"{message}\n\n"
                    f"Please fix the algorithm so that all tests pass. Make sure your visited state accurately accounts for remaining obstacle eliminations (k)."
                )
                conversation.append({"role": "assistant", "content": content or f"```python\n{code}\n```"})
                conversation.append({"role": "user", "content": feedback})
                
        return {
            "name": model_info["name"],
            "tier": model_info["tier"],
            "file": model_info["file"],
            "warmup_sec": round(warmup, 2),
            "passed": passed,
            "turns_needed": len(turns_data) if passed else 4,
            "total_tokens": total_tokens,
            "total_time_sec": round(total_time, 2),
            "avg_speed_tok_s": round(total_tokens / total_time, 2) if total_time > 0 else 0.0,
            "status": "PASS" if passed else "FAIL",
            "turns": turns_data
        }
    finally:
        server_proc.kill()
        kill_server()

def main():
    results = []
    print(f"Starting Shortest Path (Level 6.0) Benchmark across 7 models...", flush=True)
    for m in MODELS_TO_BENCHMARK:
        print(f"\n==================================================", flush=True)
        print(f" BENCHMARKING: {m['name']} ({m['tier']})", flush=True)
        print(f"==================================================", flush=True)
        try:
            res = run_model_benchmark(m)
            results.append(res)
        except Exception as e:
            print(f"[ERROR] Failed {m['name']}: {e}", flush=True)
            results.append({
                "name": m["name"],
                "tier": m["tier"],
                "file": m["file"],
                "warmup_sec": 0.0,
                "passed": False,
                "turns_needed": 4,
                "total_tokens": 0,
                "total_time_sec": 0.0,
                "avg_speed_tok_s": 0.0,
                "status": "FAIL",
                "error": str(e)
            })
            
    out_path = Path("tools/shortest_path_results.json")
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\n[DONE] Saved all results to {out_path}", flush=True)

if __name__ == "__main__":
    main()
