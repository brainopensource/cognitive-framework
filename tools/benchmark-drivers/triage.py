#!/usr/bin/env python3
"""Deterministic benchmark triage and failure attribution driver (Invariant I10).

Classifies run failures from SQLite event stores and run results into a standard taxonomy:
  llm | provider | protocol | harness | framework | dataset | oracle | mixed | unknown
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Mapping

# Ensure repository root is in python path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from packs.code_default.middleware.attribution.trajectory_classifier import (
    AttributionRecord,
    classify_trajectory_failure,
)


def triage_run_directory(run_dir: Path) -> dict[str, Any]:
    """Triage a single run directory containing events.sqlite3 or report artifacts."""
    run_dir = Path(run_dir).resolve()
    events: list[dict[str, Any]] = []

    sqlite_path = run_dir / "events.sqlite3"
    if sqlite_path.is_file():
        try:
            conn = sqlite3.connect(str(sqlite_path))
            cur = conn.cursor()
            cur.execute("SELECT seq, event_type, payload FROM events ORDER BY seq ASC")
            for row in cur.fetchall():
                payload_obj = {}
                try:
                    payload_obj = json.loads(row[2]) if row[2] else {}
                except Exception:
                    pass
                events.append({
                    "seq": row[0],
                    "type": row[1],
                    "payload": payload_obj,
                })
            conn.close()
        except Exception:
            pass

    # Extract last outcome/detail from events or summary
    outcome = "unknown"
    detail = ""
    for ev in reversed(events):
        if ev.get("type") in {"RunCompleted", "EpisodeTerminated", "RunFailed"}:
            payload = ev.get("payload", {})
            outcome = payload.get("terminal") or payload.get("outcome") or ev.get("type")
            detail = payload.get("detail") or payload.get("reason") or ""
            break

    attribution: AttributionRecord = classify_trajectory_failure(events, outcome=outcome, detail=detail)

    return {
        "run_dir": str(run_dir),
        "total_events": len(events),
        "outcome": outcome,
        "detail": detail,
        "attribution": {
            "class": attribution.classification,
            "confidence_ppm": attribution.confidence_ppm,
            "evidence_codes": list(attribution.evidence_codes),
            "detail": attribution.detail,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic benchmark triage projection")
    parser.add_argument("target_dir", help="Path to run directory or directory of benchmark runs")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    target = Path(args.target_dir).resolve()
    if not target.is_dir():
        print(f"Error: {target} is not a directory", file=sys.stderr)
        return 1

    # Check if target is a single run dir or parent of runs
    if (target / "events.sqlite3").is_file():
        results = [triage_run_directory(target)]
    else:
        results = []
        for sub in sorted(target.iterdir()):
            if sub.is_dir() and (sub / "events.sqlite3").is_file():
                results.append(triage_run_directory(sub))

    if not results:
        results = [triage_run_directory(target)]

    counts: dict[str, int] = {}
    for r in results:
        cls_name = r["attribution"]["class"]
        counts[cls_name] = counts.get(cls_name, 0) + 1

    summary = {
        "total_runs": len(results),
        "counts": counts,
        "results": results,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"=== Triage Summary ({len(results)} runs) ===")
        for cls_name, cnt in sorted(counts.items()):
            print(f"  {cls_name.ljust(12)}: {cnt}")
        print("======================================")

    return 0


if __name__ == "__main__":
    sys.exit(main())
