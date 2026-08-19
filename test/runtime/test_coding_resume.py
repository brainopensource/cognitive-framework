from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.apps.coding.coding_coordinator import (
    CodingRunConfig, CodingRunCoordinator, resume_coding_task,
)
from test.runtime.test_coding_coordinator import _Result, _plan


class CodingResumeTests(unittest.TestCase):
    def test_resume_uses_snapshot_plan_without_replanning(self) -> None:
        calls: list[str] = []

        def runner(role, model, episode_id, brief):
            calls.append(role.value)
            return _Result()

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            config = CodingRunConfig("resume-1", workspace, "build", max_episodes=8)
            coordinator = CodingRunCoordinator(
                config, planner=_plan, run_episode=runner,
                verify_step=lambda plan, step: False,
                verify_final=lambda plan, step: True,
                workspace_digest=lambda path: "sha256:workspace",
            )
            coordinator.run()
            snapshot = coordinator.snapshot()
            calls.clear()
            result = resume_coding_task(
                "resume-1", workspace=workspace, snapshot=snapshot, config=config,
                planner=lambda brief: self.fail("resume must not invoke planner"),
                run_episode=runner, verify_step=lambda plan, step: True,
                verify_final=lambda plan, step: True,
                workspace_digest=lambda path: "sha256:workspace",
            )
        self.assertNotIn("architect", calls)
        self.assertEqual(result.outcome, "oracle_green")

    def test_resume_refuses_changed_workspace_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            config = CodingRunConfig("resume-2", workspace, "build")
            coordinator = CodingRunCoordinator(
                config, planner=_plan, run_episode=lambda *args: _Result(),
                verify_step=lambda plan, step: False, verify_final=lambda plan, step: True,
                workspace_digest=lambda path: "before",
            )
            coordinator.run()
            with self.assertRaises(ValueError):
                resume_coding_task(
                    "resume-2", workspace=workspace, snapshot=coordinator.snapshot(), config=config,
                    planner=_plan, run_episode=lambda *args: _Result(),
                    verify_step=lambda plan, step: True, verify_final=lambda plan, step: True,
                    workspace_digest=lambda path: "after",
                )


if __name__ == "__main__":
    unittest.main()
