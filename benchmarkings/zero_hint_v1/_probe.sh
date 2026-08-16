#!/usr/bin/env bash
set -euo pipefail
cd /home/rocha/Coding/Aether-D-System
python3 --version
python3 benchmarkings/zero_hint_v1/run_live_agent.py --write-preregistration
python3 benchmarkings/zero_hint_v1/run_live_agent.py --check-fixtures
echo "---env---"
if test -x /usr/bin/bwrap; then echo bwrap=yes; else echo bwrap=no; fi
if test -n "${OPENROUTER_API_KEY:-}"; then echo or_key=environ; else echo or_key=no_environ; fi
if test -f .env; then echo dotenv=present; else echo dotenv=absent; fi
if curl -sS --max-time 2 http://127.0.0.1:11434/api/tags > /tmp/ollama_tags.json; then
  python3 -c 'import json; d=json.load(open("/tmp/ollama_tags.json")); print("ollama", [m.get("name") for m in d.get("models", [])])'
else
  echo ollama=down
fi
python3 - <<'PY'
from pathlib import Path
import subprocess, sys
root = Path("benchmarkings/zero_hint_v1/tasks/test003_invoice_cents/fixture/initial")
r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=root, capture_output=True, text=True)
print("invoice_initial", r.returncode)
print((r.stderr or r.stdout)[-800:])
print("trunc 3*1.15*100", int(3 * float("1.15") * 100))
print("trunc 3*19.99*100", int(3 * float("19.99") * 100))
PY
