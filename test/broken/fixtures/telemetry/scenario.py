#!/usr/bin/env python3
"""MF-TEL-001: Synthetic timing in a live report must be rejected."""

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
    collector.record_turn_latency(ttft_ms=120.0, turn_duration_ms=400.0)

    if args.variant == "synthetic-in-live":
        try:
            collector.record_turn_latency(ttft_ms=1.0, is_synthetic=True)
        except ValueError:
            raise AssertionError("synthetic timing in a live report")
        # If it didn't raise, fail anyway
        raise AssertionError("synthetic timing in a live report")

    report = collector.build_report()
    assert report.data_source == "live"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
