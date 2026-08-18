"""`S050-C-02`: `--in-place` operator writes.

Isolation stays the default for measurement -- a benchmark arm that could
inherit another arm's edits is not a measurement (`lab_driver.py` comment at
the staging copy). `--in-place` / `isolate=False` is an explicit, labelled
departure from that default, not a second code path with its own semantics:
the only difference is which directory becomes the episode's workspace.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import vanguard.packages.runtime.lab_driver as lab_run

TASK = (Path(__file__).resolve().parents[2] / "lab" / "tasks" /
        "dogfood-01-multi-turn-file-rollback")


class InPlaceWrites(unittest.TestCase):
    def test_isolated_is_still_the_default(self) -> None:
        result = lab_run.run_lab_task("vg-code-default", TASK, max_attempts=1)

        self.assertNotIn("in_place", result["labDepartures"])

    def test_isolated_run_never_copies_the_source_fixture_in_place(self) -> None:
        """Default mode must run against a copy, never the fixture itself."""
        with patch.object(lab_run.shutil, "copytree",
                          wraps=lab_run.shutil.copytree) as copytree:
            lab_run.run_lab_task("vg-code-default", TASK, max_attempts=1)

        self.assertTrue(copytree.called)
        # The fixture directory itself is never the destination of a run.
        self.assertNotEqual(str(TASK), str(copytree.call_args.args[0]))

    def test_in_place_mutates_the_given_workspace_and_is_labelled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "task"
            import shutil as _shutil
            _shutil.copytree(TASK, workspace)

            with patch.object(lab_run.shutil, "copytree") as copytree:
                result = lab_run.run_lab_task(
                    "vg-code-default", workspace, max_attempts=1, isolate=False)

            # No staging copy for the run's own workspace: it mutates the
            # directory it was given.
            copytree.assert_not_called()
            self.assertIn("in_place", result["labDepartures"])
            self.assertEqual(result["taskDir"], str(workspace))

    def test_the_cli_exposes_in_place(self) -> None:
        import inspect

        source = inspect.getsource(lab_run.main)
        self.assertIn("--in-place", source)


if __name__ == "__main__":
    unittest.main()
