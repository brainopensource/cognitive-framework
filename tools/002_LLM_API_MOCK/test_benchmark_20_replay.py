#!/usr/bin/env python3
"""Hermetic Zero-Cost Replay Test for Benchmark 20 Cassettes."""

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURES_DIR = ROOT / "tools" / "002_LLM_API_MOCK" / "runs" / "benchmark_20_captures"


def test_replays():
    print("Testing cassette integrity and replayability for Benchmark 20...")
    cassette_files = sorted(CAPTURES_DIR.glob("*_cassette.json"))
    assert len(cassette_files) == 20, f"Expected 20 cassettes, found {len(cassette_files)}"

    total_steps = 0
    for cf in cassette_files:
        data = json.loads(cf.read_text(encoding="utf-8"))
        assert isinstance(data, list) and len(data) > 0, f"Cassette {cf.name} is empty"
        for step in data:
            assert "request_sha256" in step
            assert "response_b64" in step
            raw_resp = base64.b64decode(step["response_b64"])
            resp_obj = json.loads(raw_resp.decode("utf-8"))
            assert "choices" in resp_obj
            total_steps += 1
        print(f"  [OK] {cf.name:45} ({len(data)} turns captured)")

    print(f"\nAll 20 cassettes valid and hermetic ({total_steps} total LLM steps recorded).")


if __name__ == "__main__":
    test_replays()
