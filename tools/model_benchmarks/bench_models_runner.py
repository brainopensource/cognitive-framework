#!/usr/bin/env python3
"""Automated Model Benchmark Evaluator for local llama-server."""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ENDPOINT = os.environ.get("VANGUARD_LLAMA_ENDPOINT", "http://127.0.0.1:8080/v1/chat/completions")

def query_model(prompt: str, system: str = "You are an expert software engineer. Output clean, complete, executable Python code with no markdown commentary outside code blocks.", max_tokens: int = 4096):
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens
    }
    t0 = time.time()
    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    t1 = time.time()
    duration = t1 - t0
    usage = res.get("usage", {})
    comp_tokens = usage.get("completion_tokens", 0)
    tok_s = comp_tokens / duration if duration > 0 else 0.0
    content = res["choices"][0]["message"].get("content", "")
    return content, tok_s, comp_tokens, duration

def extract_files(content: str) -> dict[str, str]:
    files = {}
    pattern = re.compile(r"```(?:python)?\s*(?:([a-zA-Z0-9_\-\.]+\.py))?\n(.*?)```", re.DOTALL)
    matches = pattern.findall(content)
    for name, code in matches:
        code = code.strip()
        if name:
            files[name.strip()] = code
        elif "def fibonacci" in code:
            files["fibonacci.py"] = code
        elif "class TestFibonacci" in code or "test_fibonacci" in code:
            files["test_fibonacci.py"] = code
        elif "def slugify" in code or "truncate_with_ellipsis" in code:
            files["string_utils.py"] = code
        elif "def process_pipeline" in code:
            files["pipeline.py"] = code
        elif "class TestPipeline" in code or "test_pipeline" in code:
            files["test_pipeline.py"] = code
    return files

def run_benchmark(model_tag: str, target_dir: Path) -> dict:
    results = {"model": model_tag, "tasks": {}}
    
    # -------------------------------------------------------------
    # 1. FIBO
    # -------------------------------------------------------------
    fibo_dir = target_dir / "fibo"
    fibo_dir.mkdir(parents=True, exist_ok=True)
    fibo_prompt = """Create a Python module fibonacci.py and a unit test file test_fibonacci.py.

Requirements:
1. fibonacci.py:
   - Function fibonacci(n: int) -> int returning n-th Fibonacci number (fib(0)=0, fib(1)=1, fib(n)=fib(n-1)+fib(n-2)).
   - Raises ValueError for n < 0.
   - CLI entrypoint: python3 fibonacci.py <n> prints the result to stdout.
2. test_fibonacci.py:
   - Uses unittest.TestCase to verify base cases (0, 1, 2, 10), negative input raising ValueError, and CLI invocation.

Format output as two code blocks:
```python fibonacci.py
...
```
```python test_fibonacci.py
...
```"""
    print(f"[{model_tag}] Running FIBO task...", flush=True)
    try:
        content, speed, tokens, dur = query_model(fibo_prompt)
        extracted = extract_files(content)
        for fname, code in extracted.items():
            (fibo_dir / fname).write_text(code)
        
        # Test execution
        test_file = fibo_dir / "test_fibonacci.py"
        if test_file.exists() and (fibo_dir / "fibonacci.py").exists():
            proc = subprocess.run(["python3", "-m", "unittest", "test_fibonacci.py"], cwd=fibo_dir, capture_output=True, text=True, timeout=15)
            passed = proc.returncode == 0
            test_out = proc.stderr or proc.stdout
        else:
            passed = False
            test_out = "Missing generated files"

        score = 0
        if (fibo_dir / "fibonacci.py").exists():
            score += 40
            f_text = (fibo_dir / "fibonacci.py").read_text()
            if "ValueError" in f_text: score += 10
            if "sys.argv" in f_text or "argparse" in f_text: score += 10
        if test_file.exists():
            score += 20
        if passed:
            score += 20

        results["tasks"]["fibo"] = {
            "passed": passed, "score": score, "tokens_sec": round(speed, 2),
            "tokens": tokens, "duration_sec": round(dur, 2), "notes": test_out.strip().splitlines()[-1] if test_out.strip() else ""
        }
    except Exception as e:
        results["tasks"]["fibo"] = {"passed": False, "score": 0, "tokens_sec": 0, "error": str(e)}

    # -------------------------------------------------------------
    # 2. BUGFIX
    # -------------------------------------------------------------
    bug_dir = target_dir / "bugfix"
    bug_dir.mkdir(parents=True, exist_ok=True)
    bug_prompt = """Here is string_utils.py which has a seeded bug in truncate_with_ellipsis:
```python
\"\"\"String manipulation utilities.\"\"\"

def slugify(text: str) -> str:
    \"\"\"Convert text to a clean URL-friendly slug.\"\"\"
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\\w\\s-]", "", text)
    return re.sub(r"[-\\s]+", "-", text)

def truncate_with_ellipsis(text: str, max_length: int) -> str:
    \"\"\"Truncate text to max_length including ellipsis '...'.
    
    If text length is less than or equal to max_length, return text unchanged.
    If max_length <= 3, return text[:max_length].
    Otherwise, truncate so that the total string length including '...' equals max_length.
    \"\"\"
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        return text[:max_length]
    # BUG: Off-by-one error cuts off too short or too long
    cutoff = max_length - 4
    return text[:cutoff] + "..."
```
Fix the bug in truncate_with_ellipsis so that:
- If len(text) <= max_length, returns text unchanged.
- If max_length <= 3, returns text[:max_length].
- Otherwise, returns text[:max_length - 3] + "..." so that the total string length equals max_length.
Return the complete fixed string_utils.py (including slugify) in a code block:
```python string_utils.py
...
```"""
    print(f"[{model_tag}] Running BUGFIX task...", flush=True)
    try:
        content, speed, tokens, dur = query_model(bug_prompt)
        extracted = extract_files(content)
        if "string_utils.py" in extracted:
            (bug_dir / "string_utils.py").write_text(extracted["string_utils.py"])
        
        test_file = bug_dir / "test_string_utils.py"
        if test_file.exists() and (bug_dir / "string_utils.py").exists():
            proc = subprocess.run(["python3", "-m", "unittest", "test_string_utils.py"], cwd=bug_dir, capture_output=True, text=True, timeout=15)
            passed = proc.returncode == 0
            test_out = proc.stderr or proc.stdout
        else:
            passed = False
            test_out = "Missing test or string_utils.py"

        score = 0
        if (bug_dir / "string_utils.py").exists():
            s_text = (bug_dir / "string_utils.py").read_text()
            if "max_length - 3" in s_text: score += 60
            elif "max_length" in s_text: score += 30
        if passed:
            score = 100

        results["tasks"]["bugfix"] = {
            "passed": passed, "score": score, "tokens_sec": round(speed, 2),
            "tokens": tokens, "duration_sec": round(dur, 2), "notes": test_out.strip().splitlines()[-1] if test_out.strip() else ""
        }
    except Exception as e:
        results["tasks"]["bugfix"] = {"passed": False, "score": 0, "tokens_sec": 0, "error": str(e)}

    # -------------------------------------------------------------
    # 3. PANDAS / CSV
    # -------------------------------------------------------------
    csv_dir = target_dir / "pandas"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_prompt = """Create pipeline.py and test_pipeline.py using Python's standard csv module.

Requirements:
1. pipeline.py:
   - process_pipeline(input_path: str, output_path: str) -> None
   - Validates input CSV has columns: id, category, amount, active.
   - Raises ValueError if required columns are missing or if amount cannot be parsed as float.
   - Filters rows where active is "true" (case-insensitive).
   - Groups by category, sums amount as total_amount rounded to 1 decimal place.
   - Sorts by category ascending.
   - Writes output CSV with headers category,total_amount.
2. test_pipeline.py:
   - Tests process_pipeline with sample data and asserts expected output.
   - Tests ValueError on missing columns and bad numeric data.

Format output as two code blocks:
```python pipeline.py
...
```
```python test_pipeline.py
...
```"""
    print(f"[{model_tag}] Running PANDAS/CSV task...", flush=True)
    try:
        content, speed, tokens, dur = query_model(csv_prompt)
        extracted = extract_files(content)
        for fname, code in extracted.items():
            (csv_dir / fname).write_text(code)
        
        test_file = csv_dir / "test_pipeline.py"
        if test_file.exists() and (csv_dir / "pipeline.py").exists():
            proc = subprocess.run(["python3", "-m", "unittest", "test_pipeline.py"], cwd=csv_dir, capture_output=True, text=True, timeout=15)
            passed = proc.returncode == 0
            test_out = proc.stderr or proc.stdout
        else:
            passed = False
            test_out = "Missing generated files"

        score = 0
        if (csv_dir / "pipeline.py").exists():
            p_text = (csv_dir / "pipeline.py").read_text()
            if "process_pipeline" in p_text: score += 30
            if "ValueError" in p_text: score += 20
            if "total_amount" in p_text: score += 20
        if test_file.exists():
            score += 10
        if passed:
            score = 100

        results["tasks"]["pandas"] = {
            "passed": passed, "score": score, "tokens_sec": round(speed, 2),
            "tokens": tokens, "duration_sec": round(dur, 2), "notes": test_out.strip().splitlines()[-1] if test_out.strip() else ""
        }
    except Exception as e:
        results["tasks"]["pandas"] = {"passed": False, "score": 0, "tokens_sec": 0, "error": str(e)}

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-tag", required=True)
    parser.add_argument("--target-dir", required=True)
    args = parser.parse_args()
    res = run_benchmark(args.model_tag, Path(args.target_dir))
    print(json.dumps(res, indent=2))
