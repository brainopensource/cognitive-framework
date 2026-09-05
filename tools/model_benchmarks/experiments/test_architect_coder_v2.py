import json
import subprocess
import time
import urllib.request

LLAMA_SERVER = "/home/rock-dev/.local/bin/llama-server"
CODER_V2_PATH = "/home/rock-dev/Models/DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf"
HEALTH_URL = "http://127.0.0.1:8080/health"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(1)

kill_server()
cmd = [
    LLAMA_SERVER,
    "-m", CODER_V2_PATH,
    "-c", "4096",
    "-ngl", "99",
    "--host", "127.0.0.1",
    "--port", "8080",
    "--alias", "local-model",
    "--reasoning", "off",
    "--jinja"
]
print("Starting DeepSeek-Coder-V2-Lite as Architect...")
proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for _ in range(60):
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=1) as resp:
            if json.loads(resp.read().decode()).get("status") == "ok":
                break
    except Exception:
        time.sleep(0.5)

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
        {"role": "system", "content": "You are a Principal Software Architect. Output strictly structured architectural specifications without executable Python code."},
        {"role": "user", "content": ARCHITECT_PROMPT}
    ],
    "temperature": 0.2,
    "max_tokens": 1500
}

t_req = time.time()
data_bytes = json.dumps(req).encode('utf-8')
http_req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(http_req, timeout=60) as resp:
    res = json.loads(resp.read().decode())

dur = time.time() - t_req
msg = res["choices"][0]["message"]
content = msg.get("content", "")
print(f"Architect generated in {dur:.2f}s | Tokens: {res['usage']}")

with open("tools/coder_v2_plan.txt", "w") as f:
    f.write(content)

print("=== DEEPSEEK-CODER-V2 ARCHITECT PLAN ===")
print(content[:1200])

kill_server()
