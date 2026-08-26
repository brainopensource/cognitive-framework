"""M7-01 analysis-only independence report.

This module consumes recorded event dictionaries and never schedules or executes
work. It is deliberately outside the runtime so the measurement cannot change
the execution semantics it is measuring.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.selectors.independence import disjoint


def _payload(event: Mapping[str, Any]) -> Mapping[str, Any]:
    value = event.get("payload", event)
    return value if isinstance(value, Mapping) else {}


def _key(payload: Mapping[str, Any]) -> str | None:
    value = payload.get("idempotencyKey", payload.get("idempotency_key"))
    return str(value) if value is not None else None


def _selector(payload: Mapping[str, Any]) -> Any:
    return payload.get("resource", payload.get("selector"))


def _sink(payload: Mapping[str, Any]) -> str:
    return str(payload.get("sink", payload.get("sinkClass", "unknown")))


def _causal_predecessors(payload: Mapping[str, Any]) -> frozenset[str]:
    values = payload.get("causalPredecessors", payload.get("causal_predecessors", ()))
    if isinstance(values, str):
        return frozenset((values,))
    if isinstance(values, (list, tuple, set, frozenset)):
        return frozenset(str(value) for value in values)
    return frozenset()


def analyze_events(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Return a deterministic M7-01 report from recorded effect events.

    Only effects with a usable idempotency key and selector participate. Pairs
    with missing selectors are counted as conservatively dependent, never
    treated as evidence for concurrency.
    """
    started: dict[str, Mapping[str, Any]] = {}
    settled: set[str] = set()
    for event in events:
        payload = _payload(event)
        key = _key(payload)
        kind = str(payload.get("kind", event.get("kind", "")))
        if not key:
            continue
        if kind == "EffectStarted":
            started[key] = payload
        elif kind in {"EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled"}:
            settled.add(key)

    records = [
        {"key": key, "selector": _selector(payload), "sink": _sink(payload),
         "predecessors": sorted(_causal_predecessors(payload))}
        for key, payload in sorted(started.items())
        if key in settled
    ]
    independent = 0
    pairs = 0
    for index, left in enumerate(records):
        for right in records[index + 1:]:
            pairs += 1
            causal = (left["key"] in right["predecessors"] or
                      right["key"] in left["predecessors"])
            safe = (left["selector"] is not None and right["selector"] is not None and
                    disjoint(left["selector"], right["selector"]) and not causal)
            independent += int(safe)

    report: dict[str, Any] = {
        "protocol": "M7-01",
        "analysis_only": True,
        "settled_effects": len(records),
        "pair_count": pairs,
        "independent_pairs": independent,
        "useful_independence_fraction": independent / pairs if pairs else 0.0,
        "effects": records,
    }
    report["report_digest"] = digest_of(report)
    return report


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: python3 lab/m701_independence.py EVENTS.json", file=sys.stderr)
        return 2
    source = Path(args[0])
    raw = json.loads(source.read_text(encoding="utf-8"))
    events = raw.get("events", raw) if isinstance(raw, (dict, list)) else []
    if not isinstance(events, list) or not all(isinstance(item, Mapping) for item in events):
        print("events input must be a JSON array or {events: [...]}", file=sys.stderr)
        return 2
    print(json.dumps(analyze_events(events), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
