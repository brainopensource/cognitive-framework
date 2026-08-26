"""M7-01 analysis-only independence report (`B-M7`).

This module consumes recorded event dictionaries and never schedules or executes
work. It is deliberately outside the runtime so the measurement cannot change
the execution semantics it is measuring.

The question M7-01 exists to answer is not "could two effects have run at
once" but "would it have been worth the complexity". Those differ, and the
gap between them is where scheduler projects usually go wrong: independence
looks abundant until the reasons for serialisation are counted. So the report
decomposes *why* each dependent pair was dependent --

* **causal**  -- one effect names the other as a predecessor;
* **resource** -- their selectors overlap, so the kernel would serialise them
  regardless of what a scheduler decided;
* **sink**    -- they contend for the same *exclusive* sink even with disjoint
  resources (two `privileged` writes serialise; two `observation` reads do
  not, and calling those a conflict would erase precisely the safe
  parallelism `milestones.md` already permits);
* **unknown** -- a selector is missing, which is counted as *dependent*, never
  as evidence for concurrency;

-- and reports cache behaviour and ledger-write contention alongside, because
a workload whose settled effects are mostly cache hits, or whose wall time is
dominated by one serialised writer, will not get faster by being parallelised.

`ADR-0092` binds the consequence: below roughly 30% useful independence the
default decision is to cancel advanced scheduling and retain I-11. Reaching
that conclusion is a success of the process. Nothing here may add concurrency,
a scheduler, workers, claims, leases, or a topology.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.selectors.independence import disjoint


def _payload(event: Mapping[str, Any]) -> Mapping[str, Any]:
    value = event.get("payload", event)
    return value if isinstance(value, Mapping) else {}


def _key(payload: Mapping[str, Any]) -> str | None:
    """Stable identity for one effect across its start and its settlement.

    The idempotency key is the intended identity, but the canonical coding
    path currently writes it as `null`, so a key-only reader finds *zero*
    effects in a real ledger and reports a vacuous 0/0. `descriptorDigest` is
    written on both halves and is equally stable, so it is used as a fallback
    -- pairing is then real, and the missing selector shows up honestly in the
    `unknown_selector` column rather than as an absence of data.
    """
    value = payload.get("idempotencyKey", payload.get("idempotency_key"))
    if value is not None:
        return str(value)
    descriptor = payload.get("descriptorDigest", payload.get("descriptor_digest"))
    return str(descriptor) if descriptor is not None else None


def _selector(payload: Mapping[str, Any]) -> Any:
    return payload.get("resource", payload.get("selector"))


def _sink(payload: Mapping[str, Any]) -> str:
    for name in ("sink", "sinkClass", "sink_class"):
        value = payload.get(name)
        if isinstance(value, str) and value:
            return value
    return "unknown"


def _millis(payload: Mapping[str, Any], *names: str) -> float | None:
    for name in names:
        value = payload.get(name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


def _cache_state(payload: Mapping[str, Any]) -> str | None:
    """Normalise the several spellings a cache observation arrives under."""
    value = payload.get("cacheState", payload.get("cache_state"))
    if isinstance(value, str) and value:
        return value
    hit = payload.get("cacheHit", payload.get("cache_hit"))
    if isinstance(hit, bool):
        return "hit" if hit else "miss"
    return None


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
    settlements: dict[str, Mapping[str, Any]] = {}
    for event in events:
        payload = _payload(event)
        key = _key(payload)
        kind = str(payload.get("kind", event.get("kind", "")))
        if not key:
            continue
        if kind == "EffectStarted":
            started[key] = payload
        elif kind in {"EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled"}:
            settlements[key] = payload

    records = []
    for key, payload in sorted(started.items()):
        if key not in settlements:
            continue
        settled_payload = settlements[key]
        record: dict[str, Any] = {
            "key": key, "selector": _selector(payload), "sink": _sink(payload),
            "predecessors": sorted(_causal_predecessors(payload)),
        }
        start = _millis(payload, "atMillis", "at_millis", "startedAtMillis")
        end = _millis(settled_payload, "atMillis", "at_millis", "settledAtMillis")
        if start is not None:
            record["started_at_millis"] = start
        if end is not None:
            record["settled_at_millis"] = end
        cache = _cache_state(settled_payload) or _cache_state(payload)
        if cache is not None:
            record["cache_state"] = cache
        writes = settled_payload.get("walWriteMillis", settled_payload.get("wal_write_millis"))
        if isinstance(writes, (int, float)) and not isinstance(writes, bool):
            record["wal_write_millis"] = float(writes)
        records.append(record)

    independent = 0
    pairs = 0
    reasons = {"causal": 0, "resource": 0, "sink": 0, "unknown_selector": 0}
    for index, left in enumerate(records):
        for right in records[index + 1:]:
            pairs += 1
            reason = _dependency_reason(left, right)
            if reason is None:
                independent += 1
            else:
                reasons[reason] += 1

    report: dict[str, Any] = {
        "protocol": "M7-01",
        "analysis_only": True,
        "settled_effects": len(records),
        "pair_count": pairs,
        "independent_pairs": independent,
        "useful_independence_fraction": independent / pairs if pairs else 0.0,
        "serialization": _serialization(records, reasons, pairs),
        "cache": _cache_behaviour(records),
        "wal_contention": _wal_contention(records),
        "effects": records,
    }
    report["report_digest"] = digest_of(report)
    return report


#: Sinks whose shared use serialises two otherwise-disjoint effects.
#: `observation` and `advisory` are non-mutating (`SinkClass`), so two of them
#: on disjoint resources are the canonical safe-parallel case, not a conflict.
#: An unrecognised sink is treated as exclusive: fail closed.
_NON_EXCLUSIVE_SINKS = frozenset({"observation", "advisory"})


def _is_exclusive(sink: str) -> bool:
    return sink not in _NON_EXCLUSIVE_SINKS and sink != "unknown"


def _dependency_reason(left: Mapping[str, Any], right: Mapping[str, Any]) -> str | None:
    """Why this pair could not have run concurrently, or `None` if it could.

    Order matters: a pair that is both causally ordered and resource-conflicting
    is reported as causal, because removing the resource conflict would not
    have freed it. Attributing it to the resource would overstate what a
    scheduler could recover.
    """
    if (left["key"] in right["predecessors"] or right["key"] in left["predecessors"]):
        return "causal"
    if left["selector"] is None or right["selector"] is None:
        return "unknown_selector"
    try:
        if not disjoint(left["selector"], right["selector"]):
            return "resource"
    except Exception:
        return "unknown_selector"
    if left["sink"] == right["sink"] and _is_exclusive(str(left["sink"])):
        return "sink"
    return None


def _serialization(records: Sequence[Mapping[str, Any]], reasons: Mapping[str, int],
                   pairs: int) -> dict[str, Any]:
    """Serialisation actually observed, against serialisation that was forced.

    Every recorded pair ran sequentially -- I-11 guarantees it -- so the
    interesting quantity is how much of that was *required*.
    """
    forced = sum(reasons.values())
    return {
        "observed_sequential_pairs": pairs,
        "forced_by_dependency": forced,
        "recoverable_pairs": pairs - forced,
        "recoverable_fraction": (pairs - forced) / pairs if pairs else 0.0,
        "reasons": dict(sorted(reasons.items())),
    }


def _cache_behaviour(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Cache hits are work that parallelism cannot make cheaper."""
    observed = [str(record["cache_state"]) for record in records if "cache_state" in record]
    hits = sum(1 for state in observed if state == "hit")
    return {
        "observed": len(observed),
        "unobserved": len(records) - len(observed),
        "hits": hits,
        "misses": len(observed) - hits,
        "hit_rate": hits / len(observed) if observed else 0.0,
    }


def _wal_contention(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Overlapping effect windows and time spent in the single ledger writer.

    Under I-11 the overlap count must be zero; a non-zero value in a recorded
    sequential workload is a finding about the recording, not permission to
    parallelise. `wal_write_share` bounds the win available at all: work that
    is already dominated by one serialised writer does not get faster by
    being spread across workers.
    """
    windows = sorted(
        (record["started_at_millis"], record["settled_at_millis"])
        for record in records
        if "started_at_millis" in record and "settled_at_millis" in record
    )
    overlaps = sum(1 for index, (_, end) in enumerate(windows[:-1])
                   if windows[index + 1][0] < end)
    span = (windows[-1][1] - windows[0][0]) if windows else 0.0
    wal = sum(float(record["wal_write_millis"]) for record in records
              if "wal_write_millis" in record)
    return {
        "measured_windows": len(windows),
        "overlapping_windows": overlaps,
        "observed_span_millis": span,
        "wal_write_millis": wal,
        "wal_write_share": wal / span if span > 0 else 0.0,
    }


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
