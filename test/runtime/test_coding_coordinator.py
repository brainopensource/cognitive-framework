from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.apps.coding.coding_coordinator import CodingRunConfig, run_coding_task
from vanguard.packages.apps.coding.coding_plan import parse_coding_plan, validate_plan


def _plan(_brief: str):
    plan = parse_coding_plan({
        "schema": "vg.coding-plan.v1", "goal": "build", "assumptions": [],
        "steps": [
            {"id": "server", "title": "server", "dependsOn": [], "files": ["server.py"],
             "intent": "create", "acceptanceChecks": [["python3", "-m", "unittest"]]},
            {"id": "ui", "title": "ui", "dependsOn": ["server"], "files": ["static/app.js"],
             "intent": "create", "acceptanceChecks": [["python3", "-m", "unittest"]]},
        ], "finalChecks": [["python3", "-m", "unittest"]],
    })
    validate_plan(plan, allowed_command_prefixes=(("python3", "-m", "unittest"),))
    return plan


class _Result:
    detail = ""
    telemetry = type("Telemetry", (), {"turns": 1})()


class CoordinatorTests(unittest.TestCase):
    def test_planner_precedes_dependency_ordered_executor_and_final_oracle(self) -> None:
        calls = []

        def runner(role, model, episode_id, brief):
            calls.append((role.value, episode_id, brief))
            return _Result()

        with tempfile.TemporaryDirectory() as tmp:
            result = run_coding_task(
                CodingRunConfig("run-1", Path(tmp), "build", max_episodes=8),
                planner=_plan, run_episode=runner,
                verify_step=lambda plan, step: True,
                verify_final=lambda plan, step: True,
            )
        self.assertEqual(result.outcome, "oracle_green")
        self.assertEqual([call[0] for call in calls], ["architect", "executor", "executor", "reviewer"])
        self.assertIn("server", calls[1][2])
        self.assertIn("ui", calls[2][2])
        self.assertEqual(len({call[1] for call in calls}), len(calls))

    def test_failed_exterior_step_never_becomes_green(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_coding_task(
                CodingRunConfig("run-2", Path(tmp), "build"), planner=_plan,
                run_episode=lambda *args: _Result(),
                verify_step=lambda plan, step: False,
                verify_final=lambda plan, step: True,
            )
        self.assertEqual(result.outcome, "verification_failed")
        self.assertEqual(result.verified_step_ids, ())


if __name__ == "__main__":
    unittest.main()
