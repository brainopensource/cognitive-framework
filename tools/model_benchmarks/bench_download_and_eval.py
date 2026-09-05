#!/usr/bin/env python3
"""Automated pipeline to evaluate local models with 8192 context and 2048 max_tokens."""

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

MODELS_DIR = Path("/home/rock-dev/Models")
LLAMA_SERVER = "/home/rock-dev/.local/bin/llama-server"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
HEALTH_URL = "http://127.0.0.1:8080/health"

MODELS = [
    {
        "id": "model_1",
        "name": "Qwen2.5-Coder-1.5B-Instruct",
        "tier": "Faixa 1 (0.5B–3B) - Coding",
        "file": "Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf",
    },
    {
        "id": "model_2",
        "name": "DeepSeek-R1-Distill-Qwen-1.5B",
        "tier": "Faixa 1 (0.5B–3B) - Planning/Reasoning",
        "file": "DeepSeek-R1-Distill-Qwen-1.5B-Q4_K_M.gguf",
    },
    {
        "id": "model_3",
        "name": "Qwen2.5-Coder-3B-Instruct",
        "tier": "Faixa 2 (3B–6B) - Coding",
        "file": "Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf",
    },
    {
        "id": "model_4",
        "name": "Phi-4-mini-instruct (3.8B)",
        "tier": "Faixa 2 (3B–6B) - Planning/Reasoning",
        "file": "Phi-4-mini-instruct-Q4_K_M.gguf",
    },
    {
        "id": "model_5",
        "name": "Qwen2.5-Coder-14B-Instruct",
        "tier": "Faixa 3 (6B–16B) - Coding",
        "file": "Qwen2.5-Coder-14B-Instruct-Q4_K_M.gguf",
    },
    {
        "id": "model_6",
        "name": "DeepSeek-R1-Distill-Qwen-14B",
        "tier": "Faixa 3 (6B–16B) - Planning/Reasoning",
        "file": "DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf",
    },
]

PROMPT = "python code in the chat for printing 6th fibonacci value in one line"

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(2)

def start_server(model_path: Path):
    kill_server()
    cmd = [
        LLAMA_SERVER,
        "-m", str(model_path),
        "-c", "8192",
        "-ngl", "99",
        "--host", "127.0.0.1",
        "--port", "8080",
        "--alias", "local-model",
        "--reasoning", "off",
        "--jinja"
    ]
    print(f"[SERVER] Starting llama-server with {model_path.name} (-c 8192, --reasoning off)...", flush=True)
    t0 = time.time()
    server_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for health
    while time.time() - t0 < 60:
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
    raise TimeoutError("Server failed to become healthy within 60s")

def evaluate_model(server_proc) -> dict:
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "user", "content": PROMPT}
        ],
        "temperature": 0.1,
        "max_tokens": 2048
    }
    print(f"[EVAL] Querying model with prompt: '{PROMPT}' (max_tokens: 2048, timeout: 240s)...", flush=True)
    t0 = time.time()
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            res = json.loads(resp.read().decode())
        t1 = time.time()
        dur = t1 - t0
        usage = res.get("usage", {})
        comp_tokens = usage.get("completion_tokens", 0)
        speed = comp_tokens / dur if dur > 0 else 0.0
        msg_obj = res["choices"][0]["message"]
        content = msg_obj.get("content", "")
        reasoning = msg_obj.get("reasoning_content", "")
        
        # Scoring
        score = 0
        has_print = "print" in content or "print" in reasoning
        mentions_8 = "8" in content or "8" in reasoning
        mentions_5 = "5" in content or "5" in reasoning
        has_python_code = "```python" in content or "print(" in content
        
        if has_python_code or has_print:
            score += 40
        if mentions_8 or mentions_5:
            score += 40
        if "fib" in content.lower() or "fib" in reasoning.lower():
            score += 20
            
        if score >= 80 and len(content.strip()) > 0:
            status = "PASS"
        elif score >= 40:
            status = "PARTIAL"
        else:
            status = "FAIL"
            
        print(f"[EVAL RESULT] {comp_tokens} tokens | {dur:.2f}s | {speed:.2f} tok/s | Score: {score} | Status: {status}", flush=True)
        return {
            "tokens_sec": round(speed, 2),
            "duration_sec": round(dur, 2),
            "tokens": comp_tokens,
            "score": score,
            "status": status,
            "content": content,
            "reasoning_content": reasoning[:300] if reasoning else "",
            "error": None
        }
    except Exception as e:
        print(f"[EVAL TIMEOUT/ERROR] {e}", flush=True)
        return {
            "tokens_sec": 0.0,
            "duration_sec": round(time.time() - t0, 2),
            "tokens": 0,
            "score": 0,
            "status": "FAIL",
            "content": "",
            "reasoning_content": "",
            "error": str(e)
        }

def main():
    results = []
    
    for item in MODELS:
        print(f"\n=======================================================", flush=True)
        print(f" PROCESSING: {item['name']} ({item['tier']})", flush=True)
        print(f"=======================================================", flush=True)
        
        server_proc = None
        try:
            model_path = MODELS_DIR / item["file"]
            if not model_path.exists():
                raise FileNotFoundError(f"Model file {model_path} not found")
                
            server_proc, warmup_dur = start_server(model_path)
            res = evaluate_model(server_proc)
            res["warmup_time_sec"] = round(warmup_dur, 2)
            results.append({
                "name": item["name"],
                "tier": item["tier"],
                "file": item["file"],
                "result": res
            })
        except Exception as e:
            print(f"[ERROR] Failed processing {item['name']}: {e}", flush=True)
            results.append({
                "name": item["name"],
                "tier": item["tier"],
                "file": item["file"],
                "result": {
                    "warmup_time_sec": 0.0,
                    "tokens_sec": 0.0,
                    "duration_sec": 0.0,
                    "tokens": 0,
                    "score": 0,
                    "status": "FAIL",
                    "content": "",
                    "reasoning_content": "",
                    "error": str(e)
                }
            })
        finally:
            if server_proc:
                server_proc.kill()
            kill_server()
            
    # Save results
    output_file = Path("tools/models_benchmark_2048_results.json")
    output_file.write_text(json.dumps(results, indent=2))
    print(f"\n[DONE] Saved all results to {output_file}", flush=True)

if __name__ == "__main__":
    main()
