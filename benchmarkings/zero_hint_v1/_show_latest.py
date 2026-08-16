#!/usr/bin/env python3
import json
from pathlib import Path
runs = Path("/home/rocha/Coding/Aether-D-System/benchmarkings/zero_hint_v1/tasks/test004_busy_merge/runs")
latest = sorted(p for p in runs.iterdir() if p.is_dir())[-1]
data = json.loads((latest / "result.json").read_text(encoding="utf-8"))
print(latest.name)
print("status", data.get("status"))
print("terminal", data.get("terminal"))
print("detail", data.get("detail"))
print("errors", data.get("model", {}).get("providerErrors"))
print("calls", data.get("model", {}).get("calls"))
print("kinds", data.get("model", {}).get("proposalKinds"))
print("receipts", [r.get("verb") for r in data.get("receipts", [])])
