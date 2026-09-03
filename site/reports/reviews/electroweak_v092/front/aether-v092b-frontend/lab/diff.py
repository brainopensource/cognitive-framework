#!/usr/bin/env python3
"""Side-by-side terminal diffs of tool cascades between two lam.sqlite traces.

CLI:
  python3 lab/diff.py --trace-a <id> --trace-b <id> [--db lam.sqlite]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


def _load_trace(db_path: Path | str, trace_id: int) -> dict[str, Any]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT * FROM traces WHERE trace_id = ?", (trace_id,)).fetchone()
    finally:
        conn.close()
    if row is None:
        raise KeyError(f"unknown trace_id {trace_id}")
    data = dict(row)
    raw = data.get("cascade") or "[]"
    try:
        cascade = json.loads(raw) if isinstance(raw, str) else list(raw)
    except json.JSONDecodeError:
        cascade = []
    data["cascade"] = list(cascade)
    data["tokens"] = int(data.get("prompt_tokens") or 0) + int(data.get("completion_tokens") or 0)
    return data


def render_diff(db_path: Path | str, trace_a: int, trace_b: int) -> str:
    a = _load_trace(db_path, trace_a)
    b = _load_trace(db_path, trace_b)
    left = a["cascade"]
    right = b["cascade"]
    width = max(24, max((len(str(x)) for x in left), default=8), max((len(str(x)) for x in right), default=8))
    header_l = f"A#{trace_a} {a.get('harness') or ''}".strip()
    header_r = f"B#{trace_b} {b.get('harness') or ''}".strip()
    lines = [
        f"{header_l:<{width}} | {header_r}",
        f"{'-' * width}-+-{'-' * width}",
        f"{'tokens=' + str(a['tokens']):<{width}} | tokens={b['tokens']}",
        f"{'passed=' + str(a.get('passed')):<{width}} | passed={b.get('passed')}",
        f"{'-' * width}-+-{'-' * width}",
    ]
    n = max(len(left), len(right))
    for i in range(n):
        lv = left[i] if i < len(left) else ""
        rv = right[i] if i < len(right) else ""
        mark = " " if lv == rv else "*"
        lines.append(f"{mark}{str(lv):<{width - 1}} | {rv}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diff two execution traces")
    parser.add_argument("--trace-a", type=int, required=True)
    parser.add_argument("--trace-b", type=int, required=True)
    parser.add_argument("--db", default="lam.sqlite")
    args = parser.parse_args(argv)
    sys.stdout.write(render_diff(args.db, args.trace_a, args.trace_b))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
