#!/usr/bin/env python3
"""Automated pipeline to download and evaluate DeepSeek-Coder-V2-Lite and Mistral-Small-24B."""

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

NEW_MODELS = [
    {
        "id": "deepseek_coder_v2_lite",
        "name": "DeepSeek-Coder-V2-Lite-Instruct (16B MoE)",
        "tier": "16B MoE (2.4B active) - Coding",
        "repo": "bartowski/DeepSeek-Coder-V2-Lite-Instruct-GGUF",
        "file": "DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf",
        "context_size": "8192"
    },
    {
        "id": "mistral_small_24b",
        "name": "Mistral-Small-24B-Instruct-2501",
        "tier": "24B Dense - Tool Calling / Reasoning",
        "repo": "bartowski/Mistral-Small-24B-Instruct-2501-GGUF",
        "file": "Mistral-Small-24B-Instruct-2501-Q4_K_M.gguf",
        "context_size": "4096" # 4096 guarantees it fits in 16GB VRAM alongside 14.3GB weights
    }
]

PROMPT = "python code in the chat for printing 6th fibonacci value in one line"

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(2)

def download_model(repo: str, filename: str) -> Path:
    target_path = MODELS_DIR / filename
    if target_path.exists() and target_path.stat().st_size > 100_000_000:
        print(f"[DOWNLOAD] {filename} already exists ({target_path.stat().st_size / (1024*1024):.1f} MB). Skipping.", flush=True)
        return target_path

    print(f"[DOWNLOAD] Downloading {filename} from {repo}...", flush=True)
    cmd = [
        "hf", "download", repo, filename,
        "--local-dir", str(MODELS_DIR)
    ]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"[DOWNLOAD ERROR] Failed to download {filename}: {proc.stderr}", flush=True)
        raise RuntimeError(f"Download failed: {proc.stderr}")
        
    dur = time.time() - t0
    size_mb = target_path.stat().st_size / (1024*1024)
    speed_mb_s = size_mb / dur if dur > 0 else 0
    print(f"[DOWNLOAD] Downloaded {filename} ({size_mb:.1f} MB) in {dur:.1f}s ({speed_mb_s:.1f} MB/s)", flush=True)
    return target_path

def start_server(model_path: Path, context_size: str):
    kill_server()
    cmd = [
        LLAMA_SERVER,
        "-m", str(model_path),
        "-c", context_size,
        "-ngl", "99",
        "--host", "127.0.0.1",
        "--port", "8080",
        "--alias", "local-model",
        "--reasoning", "off",
        "--jinja"
    ]
    print(f"[SERVER] Starting llama-server with {model_path.name} (-c {context_size}, --reasoning off)...", flush=True)
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
    
    for item in NEW_MODELS:
        print(f"\n=======================================================", flush=True)
        print(f" PROCESSING: {item['name']} ({item['tier']})", flush=True)
        print(f"=======================================================", flush=True)
        
        server_proc = None
        try:
            model_path = download_model(item["repo"], item["file"])
            server_proc, warmup_dur = start_server(model_path, item["context_size"])
            res = evaluate_model(server_proc)
            res["warmup_time_sec"] = round(warmup_dur, 2)
            results.append({
                "name": item["name"],
                "tier": item["tier"],
                "file": item["file"],
                "context_size": item["context_size"],
                "result": res
            })
        except Exception as e:
            print(f"[ERROR] Failed processing {item['name']}: {e}", flush=True)
            results.append({
                "name": item["name"],
                "tier": item["tier"],
                "file": item["file"],
                "context_size": item["context_size"],
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
            
    output_file = Path("tools/models_benchmark_new_results.json")
    output_file.write_text(json.dumps(results, indent=2))
    print(f"\n[DONE] Saved all results to {output_file}", flush=True)

if __name__ == "__main__":
    main()
