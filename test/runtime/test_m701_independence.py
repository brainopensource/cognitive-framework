"""M7-01 analysis must be deterministic and fail closed."""

from __future__ import annotations

import unittest

from lab.m701_independence import analyze_events


def _event(kind: str, key: str, **payload: object) -> dict[str, object]:
    return {"payload": {"kind": kind, "idempotencyKey": key, **payload}}


class M701IndependenceTests(unittest.TestCase):
    def test_report_is_deterministic_and_requires_settlement(self) -> None:
        events = [
            _event("EffectStarted", "a", sink="observation",
                   resource={"kind": "fs", "root": "/workspace", "paths": ["/workspace/a"]}),
            _event("EffectStarted", "b", sink="observation",
                   resource={"kind": "fs", "root": "/workspace", "paths": ["/workspace/b"]}),
            _event("EffectCompleted", "a"),
            _event("EffectCompleted", "b"),
            _event("EffectStarted", "orphan", sink="observation",
                   resource={"kind": "fs", "root": "/workspace", "paths": ["/workspace/c"]}),
        ]
        first = analyze_events(events)
        second = analyze_events(list(reversed(events)))
        self.assertEqual(first, second)
        self.assertEqual(first["settled_effects"], 2)
        self.assertEqual(first["independent_pairs"], 1)
        self.assertEqual(first["useful_independence_fraction"], 1.0)

    def test_missing_selector_is_not_concurrency_evidence(self) -> None:
        events = [
            _event("EffectStarted", "a", sink="observation"),
            _event("EffectStarted", "b", sink="observation", resource={
                "kind": "fs", "root": "/workspace", "paths": ["/workspace/b"]}),
            _event("EffectCompleted", "a"),
            _event("EffectCompleted", "b"),
        ]
        report = analyze_events(events)
        self.assertEqual(report["pair_count"], 1)
        self.assertEqual(report["independent_pairs"], 0)

    def test_causal_edge_overrides_disjoint_resources(self) -> None:
        events = [
            _event("EffectStarted", "a", sink="observation", resource={
                "kind": "fs", "root": "/workspace", "paths": ["/workspace/a"]}),
            _event("EffectStarted", "b", sink="observation", causalPredecessors=["a"], resource={
                "kind": "fs", "root": "/workspace", "paths": ["/workspace/b"]}),
            _event("EffectCompleted", "a"),
            _event("EffectCompleted", "b"),
        ]
        self.assertEqual(analyze_events(events)["independent_pairs"], 0)


if __name__ == "__main__":
    unittest.main()
