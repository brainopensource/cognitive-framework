#!/usr/bin/env python3
"""MF-TEL-001: Synthetic timing in a live report must be rejected by the collector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.telemetry.collector import TelemetryCollector


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("reference", "synthetic-in-live"), required=True)
    args = parser.parse_args()

    collector = TelemetryCollector(run_id="live_run_01", data_source="live")
    collector.record_turn_latency(ttft_ms=120, turn_duration_ms=400)

    if args.variant == "synthetic-in-live":
        collector.record_turn_latency(ttft_ms=1, is_synthetic=True)
        print("synthetic timing accepted in a live report")
        return 0

    report = collector.build_report()
    assert report.data_source == "live"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
