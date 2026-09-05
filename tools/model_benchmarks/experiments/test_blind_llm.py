import json
import urllib.request
import subprocess
import time
from pathlib import Path

LLAMA_SERVER = "/home/rock-dev/.local/bin/llama-server"
ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
HEALTH_URL = "http://127.0.0.1:8080/health"
MODELS_DIR = Path("/home/rock-dev/Models")

def kill_server():
    subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)
    time.sleep(1)

kill_server()
cmd = [
    LLAMA_SERVER,
    "-m", str(MODELS_DIR / "Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf"),
    "-c", "4096", "-ngl", "99", "--host", "127.0.0.1", "--port", "8080",
    "--alias", "local-model", "--reasoning", "off", "--jinja"
]
proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(30):
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=1) as resp:
            if json.loads(resp.read().decode()).get("status") == "ok":
                break
    except Exception:
        time.sleep(0.5)

# PURE BLIND PROMPT (NO LDA, NO BIASED NOISE, NO PRE-LOADED CONTEXT)
prompt = """Answer the question based on your understanding of the Vanguard / AETHER cognitive framework codebase:
How does monotonic capability attenuation work in Vanguard, which exact file implements it, and which exact unit test file and test function proves that an escalation attempt fails? Be specific."""

req = {
    "model": "local-model",
    "messages": [
        {"role": "system", "content": "You are a software engineer answering questions about the codebase."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.1,
    "max_tokens": 500
}

t0 = time.time()
data_bytes = json.dumps(req).encode('utf-8')
http_req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(http_req, timeout=30) as resp:
    res = json.loads(resp.read().decode())
t_gen = time.time() - t0

kill_server()

ans = res["choices"][0]["message"]["content"]
tokens = res["usage"]["completion_tokens"]
print(f"Blind Generation Time: {t_gen:.2f}s ({tokens} tokens)")
print("\n=== BLIND ANSWER (NO CONTEXT) ===")
print(ans)
