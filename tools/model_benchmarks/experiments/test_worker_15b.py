import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

LLAMA_SERVER = "/home/rock-dev/.local/bin/llama-server"
QWEN_15B_PATH = "/home/rock-dev/Models/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf"
HEALTH_URL = "http://127.0.0.1:8080/health"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(1)

kill_server()
cmd = [
    LLAMA_SERVER,
    "-m", QWEN_15B_PATH,
    "-c", "4096",
    "-ngl", "99",
    "--host", "127.0.0.1",
    "--port", "8080",
    "--alias", "local-model",
    "--reasoning", "off",
    "--jinja"
]
print("Starting Qwen-1.5B Worker...")
proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for _ in range(60):
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=1) as resp:
            if json.loads(resp.read().decode()).get("status") == "ok":
                break
    except Exception:
        time.sleep(0.5)

with open("tools/qwen14b_plan.txt") as f:
    plan = f.read()

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

def run_in_sandbox(code_str: str) -> tuple[bool, str]:
    full_code = code_str + "\n" + TEST_HARNESS
    try:
        res = subprocess.run(
            ["python3", "-c", full_code],
            capture_output=True,
            text=True,
            timeout=5.0
        )
        if res.returncode == 0 and "TESTS_ALL_PASSED" in res.stdout:
            return True, "All tests passed!"
        err = res.stderr if res.stderr else res.stdout
        return False, err.strip()
    except subprocess.TimeoutExpired:
        return False, "Execution timed out (5s)"
    except Exception as e:
        return False, str(e)

WORKER_PROMPT = f"""[ARCHITECTURE SPECIFICATION & PSEUDOCODE]
A Principal Software Architect designed the following solution and pseudocode for parsing RFC-4180 CSV without `import csv`:

{plan}

[YOUR TASK]
Implement the function `parse_csv(content: str) -> list[list[str]]` in pure Python following the architect's pseudocode and invariants faithfully.

RULES:
1. Do NOT import csv or any external libraries.
2. Return ONLY the complete, executable Python code inside a ```python ... ``` block.
3. Be careful with index bounds when checking `content[i+1]` (e.g. `i + 1 < len(content)`)."""

messages = [
    {"role": "system", "content": "You are an expert Python developer. You strictly translate architectural pseudocode into robust, executable Python code."},
    {"role": "user", "content": WORKER_PROMPT}
]

print("\n--- Starting Worker Evaluation (Up to 4 turns) ---")
passed = False
for turn in range(1, 5):
    print(f"\n[TURN {turn}] Generating code with Qwen-1.5B Worker...")
    req = {
        "model": "local-model",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1500
    }
    t0 = time.time()
    data_bytes = json.dumps(req).encode('utf-8')
    http_req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(http_req, timeout=30) as resp:
        res = json.loads(resp.read().decode())
    
    dur = time.time() - t0
    toks = res["usage"]["completion_tokens"]
    speed = toks / dur if dur > 0 else 0
    ans = res["choices"][0]["message"]["content"]
    code = extract_code(ans)
    
    print(f"[TURN {turn}] Generated {toks} tokens in {dur:.2f}s ({speed:.1f} tok/s)")
    
    success, msg = run_in_sandbox(code)
    if success:
        print(f"[TURN {turn}] >>> SUCCESS! All falsifiers passed! <<<")
        passed = True
        break
    else:
        print(f"[TURN {turn}] >>> FAILED: {msg[:150]}")
        feedback = f"The implementation failed tests:\n{msg}\n\nPlease fix the bug, ensuring edge cases (index out of range, quotes, empty fields) are properly handled, and return the complete updated Python code."
        messages.append({"role": "assistant", "content": ans})
        messages.append({"role": "user", "content": feedback})

kill_server()
print(f"\nFINAL STATUS: {'PASS' if passed else 'FAIL'}")
