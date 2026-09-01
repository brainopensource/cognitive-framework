"""RF-23 / NOVA-1: an invoked trajectory is attributable and economic truth."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)


class RF23TrajectoryContent(unittest.TestCase):
    """Primary M-2 content gate from ADR-0078; intentionally red pre-NOVA-1."""

    def test_invoked_turn_is_attributable_measured_and_conserved(self) -> None:
        harness = Runtime.compose("vg-code-default", episode_id="ep-rf23")
        session = HarnessSession(
            harness,
            SessionPorts(
                model=ScriptedModel([finish("record one measured turn")]),
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=SqliteEventStore(":memory:"),
                interactive=False,
            ),
            TaskContext(
                brief="exercise trajectory accounting",
                repo_path=Path("/workspace"),
                project_id="project-rf23",
                run_id="run-rf23",
                episode_id="ep-rf23",
                principal="agent-rf23",
            ),
        )

        result = session.run()
        row: dict[str, Any] = dict(result.trajectory or {})
        self.assertEqual(len(row.get("turns", ())), 1)

        # Keep all assertions visible in one named falsifier. A developer gets
        # the whole missing-contract list from one run instead of fixing the
        # first absent key and discovering the next one in serial.
        failures: list[str] = []
        routes = row.get("model_routes_used")
        if not isinstance(routes, list) or not routes:
            failures.append("model_routes_used must identify the invoked provider/model")
        else:
            for route in routes:
                if not route.get("provider") or not route.get("model"):
                    failures.append("every model route needs provider and model")
                if not route.get("model_fingerprint") and not route.get(
                    "fingerprint_unavailable_reason"
                ):
                    failures.append("fingerprint absence needs a bounded reason")

        execution_digest = row.get("execution_digest")
        if not execution_digest or execution_digest == row.get("harness_digest"):
            failures.append("execution_digest (D_R) must exist and differ in subject from D_H")
        if row.get("state_digest") != result.state_digest:
            failures.append("trajectory must bind the final reduced state digest")

        turns = row.get("turns") or []
        dimensions = ("usd_micros", "tokens", "bytes", "millis")
        positive_measured = False
        for turn in turns:
            route = turn.get("model_route") or {}
            if not route.get("provider") or not route.get("model"):
                failures.append("each invoked turn must carry its own provider/model route")
            if not route.get("model_fingerprint") and not route.get(
                "fingerprint_unavailable_reason"
            ):
                failures.append("each turn needs a fingerprint or bounded absence reason")
            cost = turn.get("cost") or {}
            status = cost.get("measurement_status") or {}
            for dimension in dimensions:
                marker = status.get(dimension) or {}
                state = marker.get("status")
                value = cost.get(dimension)
                if state not in {"measured", "estimated", "unavailable"}:
                    failures.append(f"turn cost {dimension} lacks explicit measurement status")
                if state == "unavailable" and not marker.get("reason"):
                    failures.append(f"unavailable {dimension} needs a bounded reason")
                if state in {"measured", "estimated"} and isinstance(value, int) and value > 0:
                    positive_measured = True
        if not positive_measured:
            failures.append("an invoked turn needs at least one positive measured dimension")

        total = row.get("cost") or {}
        total_status = total.get("measurement_status") or {}
        for dimension in dimensions:
            available = all(
                (turn.get("cost", {}).get("measurement_status", {}).get(dimension, {}).get("status")
                 in {"measured", "estimated"})
                for turn in turns
            )
            if available:
                values = [turn.get("cost", {}).get(dimension) for turn in turns]
                if not all(isinstance(value, int) and not isinstance(value, bool)
                           for value in values):
                    failures.append(f"available turn {dimension} must be an integer")
                else:
                    expected = sum(values)
                    if total.get(dimension) != expected:
                        failures.append(f"episode {dimension} does not conserve turn charges")
            elif total_status.get(dimension, {}).get("status") != "unavailable":
                failures.append(f"episode {dimension} must propagate unavailable status")

        event_range = row.get("event_range") or {}
        if not all(event_range.get(key) is not None for key in ("first_seq", "last_seq", "count")):
            failures.append("trajectory must bind its final ledger event range")
        if row.get("verdict") is None and not row.get("verdict_absence_reason"):
            failures.append("a null verdict needs a typed absence reason; null is never pass")

        self.assertEqual(failures, [], "RF-23 remains red:\n- " + "\n- ".join(failures))


if __name__ == "__main__":
    unittest.main()
