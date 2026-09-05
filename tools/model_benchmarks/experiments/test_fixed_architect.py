import json
import urllib.request
import re
import subprocess
import time

LLAMA_SERVER = "/home/rock-dev/.local/bin/llama-server"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
HEALTH_URL = "http://127.0.0.1:8080/health"

def start_server(model_file):
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(1)
    cmd = [
        LLAMA_SERVER, "-m", f"/home/rock-dev/Models/{model_file}",
        "-c", "4096", "-ngl", "99", "--host", "127.0.0.1", "--port", "8080",
        "--alias", "local-model", "--reasoning", "off", "--jinja"
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=1) as resp:
                if json.loads(resp.read().decode()).get("status") == "ok":
                    return p
        except Exception:
            time.sleep(0.5)
    return p

ARCHITECT_PROMPT = r"""You are a Principal Software Architect.
Provide the exact pseudocode for parsing RFC-4180 CSV without `import csv`:

CRITICAL SCANNER STRUCTURE:
Walk index `i` from 0 to len(content).
When `in_quotes` is True:
1. If content[i] == '"' and i + 1 < len(content) and content[i+1] == '"':
   append '"' to current_field, increment i by 2.
2. Else if content[i] == '"':
   in_quotes = False, increment i by 1.
3. Else:
   append content[i] to current_field, increment i by 1.

When `in_quotes` is False:
1. If content[i] == '"':
   in_quotes = True, increment i by 1.
2. Else if content[i] == ',':
   append current_field to current_record, current_field = "", increment i by 1.
3. Else if content[i:i+2] == '\r\n':
   append current_field to current_record, append current_record to records, current_record = [], current_field = "", increment i by 2.
4. Else if content[i] == '\n':
   append current_field to current_record, append current_record to records, current_record = [], current_field = "", increment i by 1.
5. Else:
   append content[i] to current_field, increment i by 1.

After loop finishes:
If len(content) > 0:
   append current_field to current_record
   append current_record to records

Output ONLY:
[INVARIANTS]
[PSEUDOCODE]
"""

# Generate plan with Qwen-14B
start_server("Qwen2.5-Coder-14B-Instruct-Q4_K_M.gguf")
req = {
    "model": "local-model",
    "messages": [
        {"role": "system", "content": "You are a Principal Software Architect."},
        {"role": "user", "content": ARCHITECT_PROMPT}
    ],
    "temperature": 0.1,
    "max_tokens": 1000
}
t0 = time.time()
data_bytes = json.dumps(req).encode('utf-8')
http_req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(http_req, timeout=40) as resp:
    res = json.loads(resp.read().decode())
arch_time = time.time() - t0
arch_plan = res["choices"][0]["message"]["content"]
arch_toks = res["usage"]["completion_tokens"]
print(f"Architect produced plan in {arch_time:.2f}s ({arch_toks} tokens)")

# Now test Worker 1: Qwen-1.5B
start_server("Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf")
worker_prompt = f"""[ARCHITECTURE PSEUDOCODE]
{arch_plan}

[TASK]
Implement `parse_csv(content: str) -> list[list[str]]` in pure Python following the pseudocode.
If not content: return []
Return ONLY python code in a ```python ... ``` block."""

req_w = {
    "model": "local-model",
    "messages": [
        {"role": "system", "content": "You are an expert Python developer."},
        {"role": "user", "content": worker_prompt}
    ],
    "temperature": 0.1,
    "max_tokens": 1000
}
t0 = time.time()
data_bytes = json.dumps(req_w).encode('utf-8')
http_req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(http_req, timeout=20) as resp:
    res_w = json.loads(resp.read().decode())
w_time = time.time() - t0
w_toks = res_w["usage"]["completion_tokens"]
w_code = res_w["choices"][0]["message"]["content"]
print(f"Worker 1.5B produced code in {w_time:.2f}s ({w_toks} tokens, {w_toks/w_time:.1f} tok/s)")

subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)

# Test code
patterns = [r'```python\s*(.*?)\s*```', r'```\s*(.*?)\s*```']
clean_code = w_code
for p in patterns:
    m = re.search(p, w_code, re.DOTALL)
    if m and "def parse_csv" in m.group(1):
        clean_code = m.group(1).strip()
        break

print("=== CODE WRITTEN BY 1.5B ===")
print(clean_code)

test_harness = '''
res1 = parse_csv("a,b,c\\n1,2,3")
assert res1 == [["a", "b", "c"], ["1", "2", "3"]], f"Failed Test 1: got {res1}"

res2 = parse_csv('"nome, completo",idade\\n"Silva, Joao",30')
assert res2 == [["nome, completo", "idade"], ["Silva, Joao", "30"]], f"Failed Test 2: got {res2}"

res3 = parse_csv('id,descricao\\n1,"linha 1\\nlinha 2"\\n2,fim')
assert res3 == [["id", "descricao"], ["1", "linha 1\\nlinha 2"], ["2", "fim"]], f"Failed Test 3: got {res3}"

res4 = parse_csv('tag,"ele disse ""ola"""\\n1,ok')
assert res4 == [["tag", 'ele disse "ola"'], ["1", "ok"]], f"Failed Test 4: got {res4}"

res5 = parse_csv('a,"",c\\n,,')
assert res5 == [["a", "", "c"], ["", "", ""]], f"Failed Test 5: got {res5}"
print(">>> ALL 5 TESTS PASSED ON TURNO 1! <<<")
'''

res_eval = subprocess.run(["python3", "-c", clean_code + "\n" + test_harness], capture_output=True, text=True)
print("\n=== EVALUATION RESULT ===")
print("STDOUT:", res_eval.stdout)
print("STDERR:", res_eval.stderr)
