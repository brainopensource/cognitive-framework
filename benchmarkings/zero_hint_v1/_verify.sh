#!/usr/bin/env bash
set -u
cd /home/rocha/Coding/Aether-D-System
python3 benchmarkings/zero_hint_v1/run_live_agent.py --write-preregistration
python3 benchmarkings/zero_hint_v1/run_live_agent.py --check-fixtures
echo "---env---"
test -x /usr/bin/bwrap && echo bwrap=yes || echo bwrap=no
test -n "${OPENROUTER_API_KEY:-}" && echo or_key=environ || echo or_key=no_environ
test -f .env && echo dotenv=present || echo dotenv=absent
if curl -sS --max-time 2 http://127.0.0.1:11434/api/tags > /tmp/ollama_tags.json; then
  python3 -c 'import json; d=json.load(open("/tmp/ollama_tags.json")); print("ollama", [m.get("name") for m in d.get("models", [])])'
else
  echo ollama=down
fi
python3 - <<'PY'
import subprocess, sys, tempfile, shutil
from pathlib import Path

def run(cwd, argv):
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True).returncode

suite = Path("benchmarkings/zero_hint_v1/tasks")
for task, source, gold in [
    ("test002_rate_window", "rate_limit.py", '''
from collections import defaultdict
class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        if max_requests < 1:
            raise ValueError("max_requests must be at least 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._seen = defaultdict(list)
    def allow(self, key, now):
        if not isinstance(key, str) or not key:
            raise ValueError("key is required")
        q = self._seen[key]
        low = now - self.window_seconds
        q[:] = [t for t in q if t >= low]
        if len(q) >= self.max_requests:
            return False
        q.append(now)
        return True
'''),
    ("test003_invoice_cents", "invoicing.py", '''
import re
_PRICE = re.compile(r"^(0|[1-9][0-9]*)\\.([0-9]{2})$")
def line_cents(quantity, unit_price):
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 0:
        raise ValueError("quantity must be a non-negative integer")
    if not isinstance(unit_price, str) or _PRICE.fullmatch(unit_price) is None:
        raise ValueError("unit_price must be a two-decimal dollar amount")
    dollars, cents = unit_price.split(".")
    return quantity * (int(dollars) * 100 + int(cents))
def invoice_cents(lines):
    return sum(line_cents(q, p) for q, p in lines)
'''),
    ("test004_busy_merge", "busy.py", '''
def merge_busy(intervals):
    if not intervals:
        return []
    ordered = sorted(intervals)
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = merged[-1]
        if start > last_end:
            merged.append((start, end))
        else:
            merged[-1] = (last_start, max(last_end, end))
    return merged
'''),
]:
    src = suite / task / "fixture/initial"
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "ws"
        shutil.copytree(src, dest)
        (dest / source).write_text(gold, encoding="utf-8")
        shutil.copytree(suite / task / "oracle", dest / "oracle")
        pub = run(dest, [sys.executable, "-m", "unittest", "discover", "-s", "tests"])
        ora = run(dest, [sys.executable, "-m", "unittest", "discover", "-s", "oracle", "-p", "test_*.py"])
        print(task, "gold_public", pub, "gold_oracle", ora)
PY
