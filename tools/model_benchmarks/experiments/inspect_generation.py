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

with open("tools/canonical_architect_plan.txt") as f:
    plan = f.read()

prompt = f"""[ARCHITECTURE SPECIFICATION & PSEUDOCODE]
{plan}

[TASK]
Implement `parse_csv(content: str) -> list[list[str]]` in pure Python following the pseudocode.
IMPORTANT:
- After the while loop, if `content` is not empty, you MUST do:
    current_record.append(current_field)
    records.append(current_record)
  Do NOT check `if current_field:` because empty fields like `""` or `,,` must also be appended!

Return ONLY python code."""

p = start_server("DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf")
req = {
    "model": "local-model",
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.1,
    "max_tokens": 1000
}
data_bytes = json.dumps(req).encode('utf-8')
http_req = urllib.request.Request(ENDPOINT, data=data_bytes, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(http_req, timeout=30) as resp:
    res = json.loads(resp.read().decode())

subprocess.run(["pkill", "-9", "-f", "llama-server"], capture_output=True)

code = res["choices"][0]["message"]["content"]
print("CODE GENERATED:")
print(code)
