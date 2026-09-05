import subprocess
import time
import json
import urllib.request

LLAMA_SERVER = "/home/rock-dev/.local/bin/llama-server"
R1_14B_PATH = "/home/rock-dev/Models/DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf"
HEALTH_URL = "http://127.0.0.1:8080/health"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(1)

kill_server()
cmd = [
    LLAMA_SERVER,
    "-m", R1_14B_PATH,
    "-c", "8192",
    "-ngl", "99",
    "--host", "127.0.0.1",
    "--port", "8080",
    "--alias", "local-model",
    "--reasoning-budget", "1024",
    "--jinja"
]
print("Starting R1-14B with --reasoning-budget 1024...")
proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for _ in range(60):
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=1) as resp:
            if json.loads(resp.read().decode()).get("status") == "ok":
                break
    except Exception:
        time.sleep(0.5)

req = {
    "model": "local-model",
    "messages": [
        {"role": "user", "content": "You are a software architect. In 200 words, provide the state machine invariants and pseudocode for parsing RFC-4180 CSV with quotes, escaped quotes, and newlines."}
    ],
    "temperature": 0.2,
    "max_tokens": 1500
}

t0 = time.time()
data_bytes = json.dumps(req).encode('utf-8')
http_req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(http_req, timeout=120) as resp:
    res = json.loads(resp.read().decode())

dur = time.time() - t0
msg = res["choices"][0]["message"]
print(f"Time: {dur:.2f}s | Tokens: {res['usage']}")
print("Reasoning len:", len(msg.get("reasoning_content", "")))
print("Content len:", len(msg.get("content", "")))
print("Content sample:\n", msg.get("content", "")[:400])

kill_server()
