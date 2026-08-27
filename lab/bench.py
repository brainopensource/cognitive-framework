#!/usr/bin/env python3
"""Benchmark tools: paired McNemar comparison and pre-M-5a append/fold baseline (M4-05, SPEC §10).

CLI:
  python3 lab/bench.py --pack-a vg-code-default --pack-b vg-code-claude-shaped --db lam.sqlite
  python3 lab/bench.py --append-fold --out benchmarks/baseline_m4.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


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


def bench_append_fold(
    event_counts: Sequence[int] = (1000, 10000),
    *,
    runs: int = 3,
) -> dict[str, Any]:
    """Measure WAL append throughput and cold fold micro-seconds per event on deterministic fixtures."""
    from vanguard.packages.adapters.stores.event_store import SqliteEventStore
    from vanguard.packages.domain.canonicalisation.digest import digest_of
    from vanguard.packages.domain.ledger.events import EventEnvelope
    from vanguard.packages.domain.ledger.reducer import compute_state_digest, reconstruct_state
    from vanguard.packages.ports.event_store import EventRange

    results: dict[str, Any] = {}
    for count in event_counts:
        append_rates: list[float] = []
        fold_rates: list[float] = []
        fold_micros_per_event: list[float] = []
        state_digests: list[str] = []

        envelopes: list[EventEnvelope] = []
        for i in range(count):
            envelopes.append(
                EventEnvelope(
                    schema_version="mhf.event/1",
                    event_id=f"evt-{i:06d}",
                    scope="episode",
                    seq=str(i),
                    occurred_at="2026-08-25T12:00:00.000Z",
                    recorded_at="2026-08-25T12:00:00.000Z",
                    principal="agent-bench",
                    principal_role="episode",
                    tenant_id="tenant-default",
                    owner_id="owner-platform",
                    confidentiality="internal",
                    retention_class="standard",
                    trainability="prohibited",
                    redaction_status="none",
                    run_id="run-bench-001",
                    episode_id="ep-bench-001",
                    trace_id="trace-bench",
                    span_id=f"span-{i}",
                    payload={"kind": "TurnStarted" if i % 2 == 0 else "EffectStarted", "turn": i // 2},
                )
            )

        for _ in range(runs):
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = Path(tmpdir) / "bench_events.sqlite3"
                store = SqliteEventStore(db_path)

                t0 = time.perf_counter()
                store.append(envelopes)
                t_append = time.perf_counter() - t0
                append_rate = count / t_append if t_append > 0 else 0.0
                append_rates.append(append_rate)
                store.close()

                store_cold = SqliteEventStore(db_path)
                t1 = time.perf_counter()
                read_res = store_cold.read(EventRange(episode_id="ep-bench-001"))
                read_envelopes = tuple(read_res.value or ())
                reduced_state = reconstruct_state(read_envelopes)
                digest = compute_state_digest(reduced_state)
                t_fold = time.perf_counter() - t1
                store_cold.close()

                fold_rate = count / t_fold if t_fold > 0 else 0.0
                micros_per_event = (t_fold * 1_000_000) / count if count > 0 else 0.0
                fold_rates.append(fold_rate)
                fold_micros_per_event.append(micros_per_event)
                state_digests.append(digest)

        assert len(set(state_digests)) == 1, "Non-deterministic fold state digests across benchmark runs"

        results[f"{count}_events"] = {
            "event_count": count,
            "runs": runs,
            "state_digest": state_digests[0],
            "append_events_per_sec_mean": sum(append_rates) / len(append_rates),
            "append_events_per_sec_max": max(append_rates),
            "fold_events_per_sec_mean": sum(fold_rates) / len(fold_rates),
            "fold_events_per_sec_max": max(fold_rates),
            "fold_micros_per_event_mean": sum(fold_micros_per_event) / len(fold_micros_per_event),
            "fold_micros_per_event_min": min(fold_micros_per_event),
        }

    report: dict[str, Any] = {
        "benchmark": "bench_append_fold",
        "milestone": "M-4",
        "timestamp": "2026-08-25T12:00:00.000Z",
        "command": "python3 lab/bench.py --append-fold --out benchmarks/baseline_m4.json",
        "environment": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
        },
        "results": results,
    }
    report["report_digest"] = digest_of(report)
    return report


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-a", help="Baseline manifest pack name")
    parser.add_argument("--pack-b", help="Comparison manifest pack name")
    parser.add_argument("--db", default="lam.sqlite", help="Path to sqlite traces db")
    parser.add_argument("--prereg", help="Path to pre-registration JSON file")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text report")
    parser.add_argument("--append-fold", action="store_true", help="Run deterministic append/fold benchmark baseline")
    parser.add_argument("--out", help="Path to save benchmark JSON output")
    args = parser.parse_args(argv)

    if args.append_fold:
        report = bench_append_fold()
        report_json = json.dumps(report, indent=2)
        if args.out:
            out_p = Path(args.out)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(report_json + "\n", encoding="utf-8")
            print(f"wrote benchmark baseline to {out_p}")
        else:
            print(report_json)
        return 0

    if not args.pack_a or not args.pack_b:
        parser.error("--pack-a and --pack-b are required when not running --append-fold")

    prereg_meta = None
    if args.prereg:
        p_path = Path(args.prereg)
        if not p_path.exists():
            print(f"Pre-registration file not found: {args.prereg}", file=sys.stderr)
            return 2
        prereg_data = json.loads(p_path.read_text(encoding="utf-8"))
        is_lam_replay = (prereg_data.get("backend") == "lam-replay")
        prereg_meta = {
            "preregistrationId": prereg_data.get("preregistrationId"),
            "hash": prereg_data.get("hash"),
            "isReplay": is_lam_replay,
            "q3Eligible": not is_lam_replay,
        }

    res = compare_packs(args.db, args.pack_a, args.pack_b)
    if prereg_meta:
        res["preregistration"] = prereg_meta
        if not prereg_meta["q3Eligible"]:
            res["q3Eligible"] = False
            res["q3Warning"] = "Backend is lam-replay; results are not Q3-eligible"

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(format_report(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
