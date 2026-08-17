"""Deterministic prompt-prefix cache metric for cassette replay."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vanguard.packages.domain.canonicalisation.digest import digest_of


def prefix_digest(record: Mapping[str, Any]) -> str:
    """Digest only the prefix-shaped fields; turn-specific content is excluded."""
    context = record.get("context") or {}
    return digest_of({
        "system": context.get("system", context.get("systemCore", "")),
        "tools": record.get("tools") or [],
    })


def measure_replay(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(records)
    if not rows:
        raise ValueError("fixed replay must contain at least one model call")
    digests = [prefix_digest(row) for row in rows]
    usages = [(row.get("usage") or row.get("proposal", {}).get("usage")) for row in rows]
    reported = [usage for usage in usages if isinstance(usage, Mapping) and "cached_tokens" in usage]
    cached_calls = sum(1 for usage in reported if int(usage.get("cached_tokens", 0) or 0) > 0)
    result: dict[str, Any] = {
        "dataSource": "cassette",
        "calls": len(rows),
        "prefixDigests": digests,
        "prefixDigestStable": len(set(digests)) == 1,
        "providerCacheHitRate": (cached_calls / len(reported)) if reported else None,
        "providerCacheReports": len(reported),
    }
    if not reported:
        result["limitation"] = "provider did not report cached_tokens; prefix-digest stability is the observable metric"
    return result


def measure_fixed_replay(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("fixed replay must be a JSON array")
    return measure_replay(data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("replay", type=Path)
    args = parser.parse_args()
    print(json.dumps(measure_fixed_replay(args.replay), indent=2, sort_keys=True))
