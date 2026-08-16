#!/usr/bin/env python3
"""Paired McNemar comparison of two harness packs from lam.sqlite traces.

CLI:
  python3 lab/bench.py --pack-a vg-code-default --pack-b vg-code-claude-shaped --db lam.sqlite
"""

from __future__ import annotations

import argparse
import json
import math
import sqlite3
import sys
from pathlib import Path
from typing import Any


def mcnemar(b: int, c: int) -> dict[str, Any]:
    """Exact two-sided McNemar plus χ² = (b − c)² / (b + c)."""
    n = b + c
    if n == 0:
        return {
            "b": b,
            "c": c,
            "chi2": 0.0,
            "p_value": 1.0,
            "refused": True,
            "reason": "no discordant pairs (A/A floor unobserved)",
        }
    chi2 = ((b - c) ** 2) / n
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1))
    p_value = min(1.0, 2.0 * tail / (2 ** n))
    return {
        "b": b,
        "c": c,
        "chi2": chi2,
        "p_value": p_value,
        "refused": False,
        "reason": None,
    }


def _latest_by_scenario(conn: sqlite3.Connection, pack: str) -> dict[str, sqlite3.Row]:
    rows = conn.execute(
        """
        SELECT * FROM traces
        WHERE harness = ?
        ORDER BY trace_id ASC
        """,
        (pack,),
    ).fetchall()
    latest: dict[str, sqlite3.Row] = {}
    for row in rows:
        latest[row["scenario_id"]] = row
    return latest


def compare_packs(db_path: Path | str, pack_a: str, pack_b: str) -> dict[str, Any]:
    path = Path(db_path)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        a_rows = _latest_by_scenario(conn, pack_a)
        b_rows = _latest_by_scenario(conn, pack_b)
    finally:
        conn.close()
    paired = sorted(set(a_rows) & set(b_rows))
    a_pass = b_pass = both_pass = both_fail = b_count = c_count = 0
    tokens_a = tokens_b = 0
    for sid in paired:
        ra, rb = a_rows[sid], b_rows[sid]
        pa, pb = int(ra["passed"]), int(rb["passed"])
        tokens_a += int(ra["prompt_tokens"]) + int(ra["completion_tokens"] or 0)
        tokens_b += int(rb["prompt_tokens"]) + int(rb["completion_tokens"] or 0)
        a_pass += pa
        b_pass += pb
        if pa and pb:
            both_pass += 1
        elif not pa and not pb:
            both_fail += 1
        elif pa and not pb:
            b_count += 1
        else:
            c_count += 1
    n = len(paired)
    stats = mcnemar(b_count, c_count)
    if n > 0 and (a_pass == n or a_pass == 0) and (b_pass == n or b_pass == 0) and b_count + c_count == 0:
        stats["refused"] = True
        stats["reason"] = "degenerate A/A floor (arms at 0% or 100% with zero discordance)"
    result = {
        **stats,
        "pack_a": pack_a,
        "pack_b": pack_b,
        "n_paired": n,
        "both_pass": both_pass,
        "both_fail": both_fail,
        "pass_rate_a": (a_pass / n) if n else 0.0,
        "pass_rate_b": (b_pass / n) if n else 0.0,
        "pass_rate_delta": ((a_pass - b_pass) / n) if n else 0.0,
        "tokens_a": tokens_a,
        "tokens_b": tokens_b,
        "token_efficiency_a": (a_pass / tokens_a) if tokens_a else 0.0,
        "token_efficiency_b": (b_pass / tokens_b) if tokens_b else 0.0,
        "significant": (not stats["refused"]) and stats["p_value"] < 0.05,
    }
    return result


def format_report(result: dict[str, Any]) -> str:
    lines = [
        f"pack-a: {result['pack_a']}",
        f"pack-b: {result['pack_b']}",
        f"n_paired: {result['n_paired']}",
        f"pass_rate_a: {result['pass_rate_a']:.4f}",
        f"pass_rate_b: {result['pass_rate_b']:.4f}",
        f"pass_rate_delta: {result['pass_rate_delta']:.4f}",
        f"tokens_a: {result['tokens_a']}  tokens_b: {result['tokens_b']}",
        f"contingency: a(both pass)={result['both_pass']}  b(A win)={result['b']}  c(B win)={result['c']}  d(both fail)={result['both_fail']}",
        f"chi2: {result['chi2']:.6f}",
        f"p_value: {result['p_value']:.6g}",
        f"significant_p<0.05: {result['significant']}",
    ]
    if result.get("refused"):
        lines.append(f"REFUSED: {result.get('reason')}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Paired McNemar pack comparison")
    parser.add_argument("--pack-a", required=True)
    parser.add_argument("--pack-b", required=True)
    parser.add_argument("--db", default="lam.sqlite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = compare_packs(args.db, args.pack_a, args.pack_b)
    if args.json:
        sys.stdout.write(json.dumps(result, indent=2) + "\n")
    else:
        sys.stdout.write(format_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
