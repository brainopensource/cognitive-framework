#!/usr/bin/env python3
"""
Technique 1: Spec-Driven Code Generation
Combines lda-navigator (symbolic AST retrieval + invariant grounding)
with llama-cpp (local neural code synthesis) to produce grounded, surgical code patches.
"""

import os
import sys
import json
import time
import re
import argparse
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_MODEL = "/home/rock-dev/Models/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf"
LLAMA_SERVER_BIN = "/home/rock-dev/.local/bin/llama-server"

def is_server_healthy(port: int = 8080) -> bool:
    url = f"http://127.0.0.1:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=1) as resp:
            data = json.loads(resp.read().decode())
            return data.get("status") == "ok"
    except Exception:
        return False

def ensure_server(model_path: str, port: int = 8080) -> Optional[subprocess.Popen]:
    if is_server_healthy(port):
        return None  # Already running

    cmd = [
        LLAMA_SERVER_BIN,
        "-m", model_path,
        "-c", "4096",
        "-ngl", "99",
        "--host", "127.0.0.1",
        "--port", str(port),
        "--alias", "local-model",
        "--reasoning", "off",
        "--jinja"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for ready
    for _ in range(30):
        if is_server_healthy(port):
            return proc
        time.sleep(0.5)
    
    proc.kill()
    raise RuntimeError("Failed to launch llama-server within timeout")

def retrieve_lda_context(query: str, budget: int = 2500) -> Dict[str, Any]:
    t0 = time.time()
    res = subprocess.run(
        ["uv", "run", "lda", "context", query, "--budget", str(budget), "--json"],
        capture_output=True,
        text=True
    )
    t_retrieval = time.time() - t0
    if res.returncode != 0 or not res.stdout.strip():
        # Fallback to plan
        res_plan = subprocess.run(
            ["uv", "run", "lda", "plan", query, "--budget", str(budget), "--json"],
            capture_output=True,
            text=True
        )
        try:
            data = json.loads(res_plan.stdout)
            data["_retrieval_latency"] = t_retrieval
            return data
        except Exception:
            return {"symbols": [], "tests": [], "_retrieval_latency": t_retrieval, "raw": res.stderr}
    try:
        data = json.loads(res.stdout)
        data["_retrieval_latency"] = t_retrieval
        return data
    except Exception:
        return {"symbols": [], "tests": [], "_retrieval_latency": t_retrieval, "raw": res.stdout}

def generate_patch(
    task: str,
    target_file: Optional[str] = None,
    target_code: Optional[str] = None,
    error_feedback: Optional[str] = None,
    model_path: str = DEFAULT_MODEL,
    port: int = 8080,
    budget: int = 2500,
    auto_manage_server: bool = True
) -> Dict[str, Any]:
    owned_proc = None
    if auto_manage_server:
        owned_proc = ensure_server(model_path, port)

    try:
        # 1. Retrieve LDA facts
        lda_facts = retrieve_lda_context(task, budget=budget)
        
        # Extract symbols & test references
        symbols = [f"{s.get('title', '')} at {s.get('locator', '')}" for s in lda_facts.get("symbols", [])]
        tests = [f"{t.get('title', '')} at {t.get('locator', '')}" for t in lda_facts.get("tests", [])]
        
        # Read target file content if provided
        file_content = target_code or ""
        if not file_content and target_file and os.path.exists(target_file):
            with open(target_file, "r", encoding="utf-8") as f:
                file_content = f.read()

        # Build prompt
        facts_block = ""
        if symbols or tests:
            facts_block = "\n[ARCHITECTURAL CONTEXT]\n"
            if symbols:
                facts_block += "Relevant Symbols:\n" + "\n".join(f"- {s}" for s in symbols[:5]) + "\n"
            if tests:
                facts_block += "Test Falsifiers:\n" + "\n".join(f"- {t}" for t in tests[:5]) + "\n"

        code_block = ""
        if file_content:
            code_block = f"\n[CURRENT CODE REQUIRING FIX ({target_file or 'target'})]\n```python\n{file_content}\n```\n"

        feedback_block = ""
        if error_feedback:
            feedback_block = f"\n[ACTIVE TEST FAILURES / TRACEBACKS]\n{error_feedback}\n"

        prompt = f"""Task: Repair defect in {target_file or 'target module'}
Description: {task}
{facts_block}{code_block}{feedback_block}
[MANDATORY REPAIR INSTRUCTIONS]
1. Rewrite the complete class/module to fix the defect and make failing tests pass.
2. In allow(now: float):
   - Evict expired timestamps: keep only t where t > (now - window_seconds).
   - If capacity is reached (len(self.timestamps) >= self.max_requests), return False WITHOUT appending now.
   - Otherwise, append now and return True.
3. Output ONLY the code enclosed in ```python ... ``` without conversational commentary.
"""

        req_body = {
            "model": "local-model",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an automated code repair system. You output ONLY valid Python code inside a markdown code block ```python ... ```. Never output conversational explanations."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 1024
        }

        t_llm_start = time.time()
        url = f"http://127.0.0.1:{port}/v1/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(req_body).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            llm_resp = json.loads(resp.read().decode())
        t_llm = time.time() - t_llm_start

        raw_content = llm_resp["choices"][0]["message"]["content"]
        tokens = llm_resp.get("usage", {}).get("completion_tokens", 0)
        speed = round(tokens / t_llm, 1) if t_llm > 0 else 0.0

        # Extract code block robustly
        code_match = re.search(r"```(?:python)?\s*\n?(.*?)(?:```|$)", raw_content, re.DOTALL)
        extracted_code = code_match.group(1).strip() if code_match else raw_content.strip()

        return {
            "task": task,
            "target_file": target_file,
            "symbols_count": len(symbols),
            "tests_count": len(tests),
            "retrieval_latency": round(lda_facts.get("_retrieval_latency", 0.0), 3),
            "llm_latency": round(t_llm, 3),
            "completion_tokens": tokens,
            "tokens_per_second": speed,
            "generated_code": extracted_code,
            "raw_output": raw_content
        }
    finally:
        if owned_proc:
            owned_proc.kill()

def main():
    parser = argparse.ArgumentParser(description="Technique 1: Spec-Driven Code Generation")
    parser.add_argument("--task", required=True, help="Task description or defect explanation")
    parser.add_argument("--target-file", help="Path to file being modified")
    parser.add_argument("--error-feedback", help="Feedback or traceback from prior test failure")
    parser.add_argument("--model-path", default=DEFAULT_MODEL, help="Path to GGUF model")
    parser.add_argument("--port", type=int, default=8080, help="llama-server port")
    parser.add_argument("--budget", type=int, default=2500, help="LDA token budget")
    parser.add_argument("--no-auto-server", action="store_true", help="Don't auto start/kill llama-server")
    parser.add_argument("--json", action="store_true", help="Output full JSON result")

    args = parser.parse_args()

    result = generate_patch(
        task=args.task,
        target_file=args.target_file,
        error_feedback=args.error_feedback,
        model_path=args.model_path,
        port=args.port,
        budget=args.budget,
        auto_manage_server=not args.no_auto_server
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"=== Spec-Driven CodeGen Result ===")
        print(f"Latency: LDA {result['retrieval_latency']}s | LLM {result['llm_latency']}s ({result['tokens_per_second']} tok/s)")
        print(f"Tokens: {result['completion_tokens']}")
        print(f"\n--- Generated Code ---\n")
        print(result["generated_code"])

if __name__ == "__main__":
    main()
