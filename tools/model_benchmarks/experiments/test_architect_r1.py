import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

LLAMA_SERVER = "/home/rock-dev/.local/bin/llama-server"
R1_14B_PATH = "/home/rock-dev/Models/DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf"
HEALTH_URL = "http://127.0.0.1:8080/health"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(2)

kill_server()
cmd = [
    LLAMA_SERVER,
    "-m", R1_14B_PATH,
    "-c", "8192",
    "-ngl", "99",
    "--host", "127.0.0.1",
    "--port", "8080",
    "--alias", "local-model",
    "--jinja"
]
print("Starting R1-14B with -c 8192 (Reasoning ON)...")
t0 = time.time()
proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ready = False
while time.time() - t0 < 60:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "ok":
                ready = True
                break
    except Exception:
        time.sleep(0.5)

if not ready:
    proc.kill()
    print("Failed to start")
    exit(1)

print(f"R1-14B ready in {time.time() - t0:.2f}s")

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
7. An empty content string or trailing line breaks should be handled cleanly.

RULES:
1. DO NOT write executable Python code. No Python function syntax.
2. Provide a clear character-by-character scanner algorithm (using a pointer/index `i` over `content`).
3. Format your answer in 4 strict blocks:
[STATES AND INVARIANTS]
[EDGE-CASE TRAPS]
[STEP-BY-STEP PSEUDOCODE]
[EDGE-CASE TRACE]
"""

req = {
    "model": "local-model",
    "messages": [
        {"role": "system", "content": "You are a Principal Software Architect. Follow instructions strictly."},
        {"role": "user", "content": ARCHITECT_PROMPT}
    ],
    "temperature": 0.2,
    "max_tokens": 3072
}

print("Sending architect request...")
t_req = time.time()
data_bytes = json.dumps(req).encode('utf-8')
http_req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(http_req, timeout=180) as resp:
    res = json.loads(resp.read().decode())

dur = time.time() - t_req
usage = res.get("usage", {})
msg = res["choices"][0]["message"]
reasoning = msg.get("reasoning_content", "")
content = msg.get("content", "")

print(f"Completed in {dur:.2f}s | Usage: {usage}")
print(f"Reasoning length: {len(reasoning)} chars")
print(f"Content length: {len(content)} chars")
print("=== CONTENT PREVIEW ===")
print(content[:1500])

with open("tools/r1_plan.txt", "w") as f:
    f.write(content)

kill_server()
