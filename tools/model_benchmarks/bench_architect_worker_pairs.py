#!/usr/bin/env python3
"""Benchmark Architect/Worker Pairs on RFC-4180 CSV Parser Challenge."""

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

TEST_HARNESS = r'''
def run_falsifiers(func):
    # 1. Basic test
    res1 = func("a,b,c\n1,2,3")
    assert res1 == [["a", "b", "c"], ["1", "2", "3"]], f"Failed Test 1 (Basic): expected [['a','b','c'],['1','2','3']], got {res1}"
    
    # 2. Comma inside quoted field
    res2 = func('"nome, completo",idade\n"Silva, Joao",30')
    assert res2 == [["nome, completo", "idade"], ["Silva, Joao", "30"]], f"Failed Test 2 (Comma in quotes): got {res2}"
    
    # 3. Line break inside quoted field
    res3 = func('id,descricao\n1,"linha 1\nlinha 2"\n2,fim')
    assert res3 == [["id", "descricao"], ["1", "linha 1\nlinha 2"], ["2", "fim"]], f"Failed Test 3 (Newline in quotes): got {res3}"
    
    # 4. Escaped quotes via ""
    res4 = func('tag,"ele disse ""ola"""\n1,ok')
    assert res4 == [["tag", 'ele disse "ola"'], ["1", "ok"]], f"Failed Test 4 (Escaped quotes): got {res4}"
    
    # 5. Empty cell at end and with quotes
    res5 = func('a,"",c\n,,')
    assert res5 == [["a", "", "c"], ["", "", ""]], f"Failed Test 5 (Empty cells): got {res5}"
    return True

run_falsifiers(parse_csv)
print("TESTS_ALL_PASSED")
'''

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(1.5)

def start_server(model_file: str, context: int = 4096, reasoning_off: bool = True):
    kill_server()
    model_path = MODELS_DIR / model_file
    cmd = [
        LLAMA_SERVER,
        "-m", str(model_path),
        "-c", str(context),
        "-ngl", "99",
        "--host", "127.0.0.1",
        "--port", "8080",
        "--alias", "local-model",
        "--jinja"
    ]
    if reasoning_off:
        cmd.extend(["--reasoning", "off"])
        
    print(f"\n[SERVER] Launching {model_file} (ctx={context}, reasoning_off={reasoning_off})...", flush=True)
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    while time.time() - t0 < 60:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=1) as resp:
                if json.loads(resp.read().decode()).get("status") == "ok":
                    ready_time = time.time() - t0
                    print(f"[SERVER] Ready in {ready_time:.2f}s", flush=True)
                    return proc, ready_time
        except Exception:
            time.sleep(0.5)
            
    proc.kill()
    raise TimeoutError(f"Server {model_file} timed out starting")

def call_api(messages: list, max_tokens: int = 2048, temperature: float = 0.2) -> tuple[dict, float]:
    payload = {
        "model": "local-model",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        res = json.loads(resp.read().decode())
    dur = time.time() - t0
    return res, dur

def extract_code(text: str) -> str:
    patterns = [
        r'```python\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
    ]
    for p in patterns:
        m = re.search(p, text, re.DOTALL)
        if m:
            c = m.group(1).strip()
            if "def parse_csv" in c:
                return c
    return text.strip()

def evaluate_code(code_str: str) -> tuple[bool, str]:
    full_code = code_str + "\n" + TEST_HARNESS
    try:
        proc = subprocess.run(
            ["python3", "-c", full_code],
            capture_output=True,
            text=True,
            timeout=3.0
        )
        if proc.returncode == 0 and "TESTS_ALL_PASSED" in proc.stdout:
            return True, "All tests passed!"
        
        # Capture error
        err = proc.stderr.strip() if proc.stderr else proc.stdout.strip()
        return False, err
    except subprocess.TimeoutExpired:
        return False, "Execution timed out (3s)"
    except Exception as e:
        return False, str(e)

ARCHITECT_PROMPT = """You are a Principal Software Architect.
Your task is EXCLUSIVELY CONCEPTUAL AND ARCHITECTURAL.
Your response will guide a junior Python coder that will translate your logic into code.

PROBLEM:
Write a Python function `parse_csv(content: str) -> list[list[str]]` in pure Python (WITHOUT `import csv`):
1. Fields are separated by commas ','.
2. Records are separated by line breaks ('\\n' or '\\r\\n').
3. Fields enclosed in double quotes ("...") can contain commas and line breaks.
4. Two consecutive double quotes ("") inside a quoted field represent a single literal double quote character.
5. Surrounding quotes of a quoted field must NOT be in the output string.
6. Empty cells (e.g. ',,' or '""') must evaluate to empty strings ''.
7. Empty content ("") must return [].

CRITICAL INVARIANTS:
1. Scanner Loop: Walk index `i` from 0 to len(content). Maintain `in_quotes = False`, `current_field = ""`, `current_record = []`, `records = []`.
2. Escaped Quotes: While `in_quotes`, if `content[i] == '"'` and `i + 1 < len(content)` and `content[i+1] == '"'`: append `"` to `current_field`, increment `i += 2`.
3. Quote Toggle: While `in_quotes`, if single `'"'`: set `in_quotes = False`, increment `i += 1`. Outside quotes, if `'"'`: set `in_quotes = True`, increment `i += 1`.
4. Comma Outside Quotes: `current_record.append(current_field); current_field = ""; i += 1`.
5. Newline Outside Quotes: handle both `\r\n` (skip 2 chars) and `\n` (skip 1 char): `current_record.append(current_field); records.append(current_record); current_record = []; current_field = ""`.
6. Loop Termination: After the while loop finishes, if `content` is not empty (len(content) > 0): append `current_field` to `current_record`, and append `current_record` to `records`.

RULES:
1. DO NOT write executable Python code. No Python function syntax.
2. Provide clean pseudocode and state invariants.
3. Format in 3 clear sections:
[STATES AND INVARIANTS]
[PSEUDOCODE]
[EDGE-CASE BEHAVIOR]
"""

def run_experiment():
    results = []
    
    # 1. Generate Architectural Plan using Qwen2.5-Coder-14B
    print("=== STEP 1: GENERATING ARCHITECTURAL SPECIFICATION WITH QWEN-14B ===")
    arch_server, arch_warmup = start_server("Qwen2.5-Coder-14B-Instruct-Q4_K_M.gguf", context=4096, reasoning_off=True)
    arch_res, arch_dur = call_api([
        {"role": "system", "content": "You are a Principal Software Architect. Output strictly structured architectural specifications without executable Python code."},
        {"role": "user", "content": ARCHITECT_PROMPT}
    ], max_tokens=1500)
    
    arch_plan = arch_res["choices"][0]["message"]["content"]
    arch_tokens = arch_res["usage"]["completion_tokens"]
    arch_speed = arch_tokens / arch_dur
    print(f"Architect generated plan in {arch_dur:.2f}s ({arch_tokens} tokens, {arch_speed:.1f} tok/s)")
    kill_server()
    
    with open("tools/canonical_architect_plan.txt", "w") as f:
        f.write(arch_plan)
        
    workers = [
        {
            "pair_name": "Par 1: Qwen-14B (Architect) + Qwen-1.5B (Worker)",
            "worker_name": "Qwen2.5-Coder-1.5B-Instruct",
            "worker_file": "Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf",
            "worker_tier": "1.5B Dense"
        },
        {
            "pair_name": "Par 2: Qwen-14B (Architect) + DeepSeek-Coder-V2-Lite (Worker)",
            "worker_name": "DeepSeek-Coder-V2-Lite (16B MoE)",
            "worker_file": "DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf",
            "worker_tier": "16B MoE (2.4B active)"
        }
    ]
    
    for w in workers:
        print(f"\n=======================================================")
        print(f"EVALUATING: {w['pair_name']}")
        print(f"=======================================================")
        
        w_proc, w_warmup = start_server(w["worker_file"], context=4096, reasoning_off=True)
        
        initial_worker_prompt = f"""[ARCHITECTURE SPECIFICATION & PSEUDOCODE]
A Principal Software Architect designed the following solution and pseudocode for parsing RFC-4180 CSV without `import csv`:

{arch_plan}

[YOUR TASK]
Implement the function `parse_csv(content: str) -> list[list[str]]` in pure Python following the architect's pseudocode and invariants faithfully.

RULES:
1. Do NOT import csv or any external libraries.
2. Return ONLY the complete, executable Python code inside a ```python ... ``` block.
3. No conversational preambles or explanations."""

        messages = [
            {"role": "system", "content": "You are a precise Python engineer. Translate architectural pseudocode directly into clean, bug-free Python code."},
            {"role": "user", "content": initial_worker_prompt}
        ]
        
        turn_records = []
        pair_passed = False
        total_w_tokens = 0
        total_w_time = 0.0
        
        for turn in range(1, 5):
            print(f"\n[Turn {turn}/4] Worker generating Python code...")
            res, dur = call_api(messages, max_tokens=1500)
            toks = res["usage"]["completion_tokens"]
            speed = toks / dur if dur > 0 else 0
            ans = res["choices"][0]["message"]["content"]
            code = extract_code(ans)
            
            total_w_tokens += toks
            total_w_time += dur
            
            passed, err_msg = evaluate_code(code)
            
            turn_records.append({
                "turn": turn,
                "duration_sec": round(dur, 2),
                "tokens": toks,
                "speed_tok_s": round(speed, 1),
                "passed": passed,
                "error": "" if passed else err_msg[:300]
            })
            
            print(f"[Turn {turn}] Generated {toks} tokens in {dur:.2f}s ({speed:.1f} tok/s) -> {'PASS' if passed else 'FAIL'}")
            
            if passed:
                print(f">>> SUCCESS! {w['worker_name']} PASSED all 5 RFC-4180 falsifiers on Turn {turn}!")
                pair_passed = True
                break
            else:
                print(f"Error: {err_msg[:120]}")
                feedback = f"""Your implementation failed the automated tests:
{err_msg}

Please fix the error while strictly preserving the architect's pseudocode and return the complete updated Python code in a ```python ... ``` block."""
                messages.append({"role": "assistant", "content": ans})
                messages.append({"role": "user", "content": feedback})
                
        kill_server()
        
        results.append({
            "pair_name": w["pair_name"],
            "architect": {
                "name": "Qwen2.5-Coder-14B-Instruct",
                "warmup_sec": round(arch_warmup, 2),
                "time_sec": round(arch_dur, 2),
                "tokens": arch_tokens,
                "speed_tok_s": round(arch_speed, 1)
            },
            "worker": {
                "name": w["worker_name"],
                "tier": w["worker_tier"],
                "warmup_sec": round(w_warmup, 2),
                "total_time_sec": round(total_w_time, 2),
                "total_tokens": total_w_tokens,
                "avg_speed_tok_s": round(total_w_tokens / total_w_time, 1) if total_w_time > 0 else 0,
                "turns_needed": len(turn_records),
                "passed": pair_passed,
                "status": "PASS" if pair_passed else "FAIL",
                "turns": turn_records
            },
            "total_latency_sec": round(arch_dur + total_w_time, 2),
            "total_tokens": arch_tokens + total_w_tokens,
            "overall_status": "PASS" if pair_passed else "FAIL"
        })
        
    with open("tools/architect_worker_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n\n=======================================================")
    print("EXPERIMENT COMPLETED! SUMMARY TABLE:")
    print("=======================================================")
    for r in results:
        w = r["worker"]
        a = r["architect"]
        print(f"Pair: {r['pair_name']}")
        print(f"  Status: {r['overall_status']} (Turns: {w['turns_needed']})")
        print(f"  Architect Time: {a['time_sec']}s ({a['tokens']} toks, {a['speed_tok_s']} t/s)")
        print(f"  Worker Time:    {w['total_time_sec']}s ({w['total_tokens']} toks, {w['avg_speed_tok_s']} t/s)")
        print(f"  Total Latency:  {r['total_latency_sec']}s | Total Tokens: {r['total_tokens']}")
        print("-------------------------------------------------------")

if __name__ == "__main__":
    run_experiment()
