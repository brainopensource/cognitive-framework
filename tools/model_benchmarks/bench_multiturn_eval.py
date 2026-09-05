#!/usr/bin/env python3
"""Multi-turn interactive feedback benchmark for Phi-4-mini and DeepSeek-R1-14B with 16k context."""

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

MODELS_TO_TEST = [
    {
        "id": "phi4_mini",
        "name": "Phi-4-mini-instruct (3.8B)",
        "file": "Phi-4-mini-instruct-Q4_K_M.gguf",
        "previous_score": 85,
    },
    {
        "id": "deepseek_r1_14b",
        "name": "DeepSeek-R1-Distill-Qwen-14B",
        "file": "DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf",
        "previous_score": 70,
    }
]

INITIAL_PROMPT = "python code in the chat for printing 6th fibonacci value in one line"

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(2)

def start_server(model_path: Path):
    kill_server()
    cmd = [
        LLAMA_SERVER,
        "-m", str(model_path),
        "-c", "16384",
        "-ngl", "99",
        "--host", "127.0.0.1",
        "--port", "8080",
        "--alias", "local-model",
        "--reasoning", "off",
        "--jinja"
    ]
    print(f"\n[SERVER] Starting llama-server with {model_path.name} (-c 16384)...", flush=True)
    t0 = time.time()
    server_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for health (up to 90s)
    while time.time() - t0 < 90:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                if data.get("status") == "ok":
                    warmup_dur = time.time() - t0
                    print(f"[SERVER] Server is healthy and ready in {warmup_dur:.2f}s", flush=True)
                    return server_proc, warmup_dur
        except Exception:
            time.sleep(0.5)
            
    server_proc.kill()
    raise TimeoutError("Server failed to become healthy within 90s")

def extract_code(content: str) -> str:
    # Look for python code blocks
    matches = re.findall(r"```(?:python)?\n(.*?)```", content, re.DOTALL)
    if matches:
        # Prefer the one with print or the last one
        for m in matches:
            if "print" in m:
                return m.strip()
        return matches[-1].strip()
        
    # Look for single line with print
    lines = [line.strip() for line in content.splitlines() if line.strip().startswith("print(")]
    if lines:
        return lines[-1]
        
    return content.strip()

def execute_code(code_str: str) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            ["python3", "-c", code_str],
            capture_output=True,
            text=True,
            timeout=5
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Execution timed out (5s)"
    except Exception as e:
        return -1, "", str(e)

def evaluate_multiturn(model_info: dict) -> dict:
    model_path = MODELS_DIR / model_info["file"]
    server_proc, warmup = start_server(model_path)
    
    conversation = [
        {"role": "user", "content": INITIAL_PROMPT}
    ]
    
    turns_data = []
    total_tokens_all_turns = 0
    passed = False
    
    try:
        for turn_idx in range(1, 5):
            print(f"\n--- Turn {turn_idx} for {model_info['name']} ---", flush=True)
            t0 = time.time()
            payload = {
                "model": "local-model",
                "messages": conversation,
                "temperature": 0.1,
                "max_tokens": 4096
            }
            req = urllib.request.Request(
                ENDPOINT,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=240) as resp:
                res = json.loads(resp.read().decode())
                
            dur = time.time() - t0
            usage = res.get("usage", {})
            comp_tokens = usage.get("completion_tokens", 0)
            speed = comp_tokens / dur if dur > 0 else 0.0
            msg_obj = res["choices"][0]["message"]
            content = msg_obj.get("content", "")
            reasoning = msg_obj.get("reasoning_content", "")
            
            total_tokens_all_turns += comp_tokens
            
            # Extract code to execute
            code_to_run = extract_code(content)
            # If content is empty (e.g. if thought didn't close or was placed in reasoning)
            if not code_to_run and reasoning:
                code_to_run = extract_code(reasoning)
                
            retcode, stdout, stderr = execute_code(code_to_run)
            
            print(f"Tokens: {comp_tokens} (reasoning chars: {len(reasoning)}, content chars: {len(content)}) | Speed: {speed:.1f} t/s | Time: {dur:.2f}s", flush=True)
            print(f"Extracted code:\n```python\n{code_to_run}\n```", flush=True)
            print(f"Execution: retcode={retcode} | stdout='{stdout}' | stderr='{stderr}'", flush=True)
            
            success = (retcode == 0) and ("8" in stdout or "5" in stdout)
            
            turn_record = {
                "turn": turn_idx,
                "duration_sec": round(dur, 2),
                "tokens": comp_tokens,
                "tokens_sec": round(speed, 2),
                "reasoning_chars": len(reasoning),
                "content_chars": len(content),
                "code": code_to_run,
                "retcode": retcode,
                "stdout": stdout,
                "stderr": stderr,
                "success": success
            }
            turns_data.append(turn_record)
            
            if success:
                print(f"[SUCCESS] Model passed on Turn {turn_idx} with output '{stdout}'!", flush=True)
                passed = True
                break
            else:
                # Feedback prompt
                feedback = (
                    f"The code execution failed or did not print the expected Fibonacci value.\n"
                    f"Exit code: {retcode}\n"
                    f"STDOUT: {stdout}\n"
                    f"STDERR: {stderr}\n"
                    f"Please provide the corrected Python code that executes cleanly and prints the 6th Fibonacci value in one line."
                )
                print(f"[FEEDBACK] Injecting error feedback for Turn {turn_idx + 1}...", flush=True)
                conversation.append({"role": "assistant", "content": content or f"```python\n{code_to_run}\n```"})
                conversation.append({"role": "user", "content": feedback})
                
        final_score = 100 if passed else 50
        status = "PASS" if passed else "FAIL"
        
        return {
            "name": model_info["name"],
            "warmup_sec": round(warmup, 2),
            "passed": passed,
            "turns_needed": len(turns_data),
            "final_score": final_score,
            "status": status,
            "total_tokens_all_turns": total_tokens_all_turns,
            "turns": turns_data
        }
    finally:
        server_proc.kill()
        kill_server()

def main():
    results = []
    for m in MODELS_TO_TEST:
        res = evaluate_multiturn(m)
        results.append(res)
        
    out_file = Path("tools/multiturn_eval_results.json")
    out_file.write_text(json.dumps(results, indent=2))
    print(f"\n[DONE] Saved multi-turn results to {out_file}", flush=True)

if __name__ == "__main__":
    main()
