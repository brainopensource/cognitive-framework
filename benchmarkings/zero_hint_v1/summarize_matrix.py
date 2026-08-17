#!/usr/bin/env python3
"""Summarize latest 2x2 matrix runs from zero_hint_v1 result.json files."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS_DIR = Path(__file__).resolve().parent / "tasks"
MATRIX = [
    ("vg-code-default", "deepseek/deepseek-v4-flash"),
    ("vg-code-default", "openai/gpt-4o-mini"),
    ("vg-code-claude-shaped", "deepseek/deepseek-v4-flash"),
    ("vg-code-claude-shaped", "openai/gpt-4o-mini"),
]
TASKS = ["test003_invoice_cents", "test005_named_amounts"]


def load_latest(task_id: str, manifest: str, model: str) -> dict | None:
    runs_dir = TASKS_DIR / task_id / "runs"
    candidates = []
    for run in sorted(runs_dir.iterdir()):
        if not run.is_dir():
            continue
        path = run / "result.json"
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("manifest") == manifest and data.get("model", {}).get("model") == model:
            candidates.append((run.name, data))
    return candidates[-1][1] if candidates else None


def main() -> None:
    print("manifest | model | task | status | terminal | calls | patch | read | search | public | oracle | usd | ms")
    totals: dict[tuple[str, str], dict[str, float]] = {}
    for manifest, model in MATRIX:
        key = (manifest, model)
        totals[key] = {"usd": 0.0, "calls": 0, "patch": 0, "pass": 0}
        for task in TASKS:
            data = load_latest(task, manifest, model)
            if data is None:
                print(f"{manifest} | {model} | {task} | MISSING")
                continue
            verbs = Counter(r.get("verb") for r in data.get("receipts") or [])
            model_block = data.get("model", {})
            usd = (model_block.get("usdMicros") or 0) / 1_000_000
            totals[key]["usd"] += usd
            totals[key]["calls"] += model_block.get("calls") or 0
            totals[key]["patch"] += verbs.get("patch.apply", 0)
            if data.get("status") == "PASS":
                totals[key]["pass"] += 1
            print(
                " | ".join(
                    [
                        manifest,
                        model.split("/")[-1],
                        task.replace("test", ""),
                        data.get("status", "?"),
                        data.get("terminal", "?"),
                        str(model_block.get("calls", 0)),
                        str(verbs.get("patch.apply", 0)),
                        str(verbs.get("fs.read", 0)),
                        str(verbs.get("fs.search", 0)),
                        "Y" if data.get("publicTestsAfter", {}).get("passed") else "N",
                        "Y" if data.get("oracleAfter", {}).get("passed") else "N",
                        f"{usd:.4f}",
                        str(data.get("elapsedMs", 0)),
                    ]
                )
            )
    print("\n=== cell totals (2 tasks) ===")
    for manifest, model in MATRIX:
        t = totals[(manifest, model)]
        print(
            f"{manifest} x {model}: pass={int(t['pass'])}/2 "
            f"calls={int(t['calls'])} patch={int(t['patch'])} usd=${t['usd']:.4f}"
        )


if __name__ == "__main__":
    main()
