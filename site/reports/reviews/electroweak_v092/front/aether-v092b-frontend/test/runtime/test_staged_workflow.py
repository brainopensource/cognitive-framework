"""Unit tests for StagedWorkflowEngine."""

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from vanguard.packages.runtime.staged_workflow import StagedWorkflowEngine, VerificationNodeRunner


class TestStagedWorkflowEngine(unittest.TestCase):

    def test_staged_workflow_execution(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "events").mkdir()
            (workspace / "events" / "bus.py").write_text("class EventBus: pass", encoding="utf-8")

            engine = StagedWorkflowEngine()
            result = engine.run_workflow(workspace, "Fix bug in events/bus.py")

            self.assertEqual(result["mode"], "auto")
            self.assertIn("events/bus.py", result["context"]["primary_files"])
            self.assertEqual(len(result["stages"]), 3)

    def test_staged_workflow_with_verification(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            engine = StagedWorkflowEngine()

            def mock_verifier(ws: Path) -> bool:
                return True

            result = engine.run_workflow(workspace, "Fix bug", test_callback=mock_verifier)
            self.assertTrue(result["context"]["verified"])


if __name__ == "__main__":
    unittest.main()
