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

# Step 1: Query LDA (Symbolic Retrieval)
print("[STEP 1: LDA SYMBOLIC RETRIEVAL] Querying LDA fact graph...")
t_lda_start = time.time()
res_lda = subprocess.run([
    "uv", "run", "lda", "context", "monotonic capability attenuation",
    "--budget", "1500", "--json"
], capture_output=True, text=True)
lda_data = json.loads(res_lda.stdout)
t_lda = time.time() - t_lda_start

# Extract grounded context
symbols = [s["title"] + " at " + s["locator"] for s in lda_data.get("symbols", [])]
tests = [t["title"] + " at " + t["locator"] for t in lda_data.get("tests", [])]
print(f"LDA retrieved {len(symbols)} symbols and {len(tests)} test falsifiers in {t_lda:.2f}s.")

# Step 2: Start local model (Neural Reasoning & Synthesis)
kill_server()
print("\n[STEP 2: LOCAL LLM VIA LLAMA.CPP] Launching Qwen-1.5B (180 tok/s)...")
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

# Prompt with Grounded Facts from LDA
prompt = f"""You are the Vanguard Code Intelligence Assistant.
Answer the question based SOLELY on the grounded facts retrieved by the LDA graph below.
Do not hallucinate or invent non-existent mechanisms. Include exact file citations.

[GROUNDED LDA FACTS]
Primary Symbols:
{chr(10).join(f"- {s}" for s in symbols)}

Test Falsifiers:
{chr(10).join(f"- {t}" for t in tests)}

Code AST Extract:
```python
# vanguard/packages/kernel/attenuation.py
def attenuate(parent: Scope, request: Scope) -> AttenuationResult:
    # Narrow request under parent, or deny (K-23, K-25, K-26)
    ...
class Constraints:
    def narrower_than(self, other: 'Constraints') -> tuple[bool, str]: ...
```

[QUESTION]
How does monotonic capability attenuation work in Vanguard, which file implements it, and which tests prove that an escalation attempt fails? Be concise."""

req = {
    "model": "local-model",
    "messages": [
        {"role": "system", "content": "You are a precise, grounded code assistant. You cite exact files and functions."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.1,
    "max_tokens": 500
}

t_llm_start = time.time()
data_bytes = json.dumps(req).encode('utf-8')
http_req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(http_req, timeout=30) as resp:
    res_llm = json.loads(resp.read().decode())
t_llm = time.time() - t_llm_start

kill_server()

msg = res_llm["choices"][0]["message"]["content"]
tokens = res_llm["usage"]["completion_tokens"]
speed = tokens / t_llm

print("\n[RESULT: NEURAL-SYMBOLIC EXPLANATION]")
print(msg)
print(f"\nTelemetry:")
print(f"- LDA Retrieval: {t_lda:.2f}s")
print(f"- LLM Generation: {t_llm:.2f}s ({tokens} tokens @ {speed:.1f} tok/s)")
print(f"- Total Pipeline Latency: {t_lda + t_llm:.2f}s")
