from __future__ import annotations

import unittest

from vanguard.packages.apps.coding.coding_plan import (
    CodingPlanError, StepStatus, parse_coding_plan, ready_steps, transition_step,
    validate_plan,
)


def plan_raw() -> dict:
    return {
        "schema": "vg.coding-plan.v1", "goal": "build", "assumptions": [],
        "steps": [
            {"id": "one", "title": "one", "dependsOn": [], "files": ["app.py"],
             "intent": "write", "acceptanceChecks": [["python3", "-m", "unittest"]]},
            {"id": "two", "title": "two", "dependsOn": ["one"], "files": ["web/app.js"],
             "intent": "write", "acceptanceChecks": [["python3", "-m", "unittest"]]},
        ],
        "finalChecks": [["python3", "-m", "unittest"]],
    }


class CodingPlanTests(unittest.TestCase):
    PREFIXES = (("python3", "-m", "unittest"),)

    def test_valid_plan_is_dependency_ordered_and_digest_stable(self) -> None:
        plan = parse_coding_plan(plan_raw())
        validate_plan(plan, allowed_command_prefixes=self.PREFIXES)
        self.assertEqual([step.step_id for step in ready_steps(plan)], ["one"])
        self.assertEqual(plan.digest, parse_coding_plan(plan_raw()).digest)

    def test_verified_requires_exterior_authority(self) -> None:
        plan = parse_coding_plan(plan_raw())
        plan = transition_step(plan, "one", StepStatus.READY)
        plan = transition_step(plan, "one", StepStatus.IN_PROGRESS)
        plan = transition_step(plan, "one", StepStatus.IMPLEMENTED)
        with self.assertRaises(CodingPlanError):
            transition_step(plan, "one", StepStatus.VERIFIED)
        plan = transition_step(plan, "one", StepStatus.VERIFIED, exterior_verified=True)
        self.assertEqual([step.step_id for step in ready_steps(plan)], ["two"])

    def test_plan_rejects_escape_cycle_unknown_dependency_and_bad_status(self) -> None:
        for mutate in (
            lambda raw: raw["steps"][0].update(files=["../escape.py"]),
            lambda raw: raw["steps"][0].update(dependsOn=["two"]),
            lambda raw: raw["steps"][0].update(dependsOn=["missing"]),
            lambda raw: raw["steps"][0].update(status="verified"),
            lambda raw: raw["steps"][0].update(acceptanceChecks=[["curl", "example.test"]]),
        ):
            with self.subTest(mutate=mutate):
                raw = plan_raw()
                mutate(raw)
                plan = parse_coding_plan(raw)
                with self.assertRaises(CodingPlanError):
                    validate_plan(plan, allowed_command_prefixes=self.PREFIXES)


if __name__ == "__main__":
    unittest.main()
