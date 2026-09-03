"""Unit tests for ChangeSurfaceEstimator."""

import unittest

from vanguard.packages.domain.transforms.repository.change_surface import ChangeSurfaceEstimator


class TestChangeSurfaceEstimator(unittest.TestCase):

    def test_estimate_from_brief_and_traceback(self) -> None:
        estimator = ChangeSurfaceEstimator()
        brief = "Fix the bug in events/bus.py and update events/matcher.py"
        traceback = 'File "events/bus.py", line 42, in publish\nFile "events/matcher.py", line 12, in match'
        workspace_files = ["events/bus.py", "events/matcher.py", "events/utils.py"]

        estimate = estimator.estimate(brief, workspace_files=workspace_files, traceback_text=traceback)
        self.assertIn("events/bus.py", estimate.primary_files)
        self.assertIn("events/matcher.py", estimate.primary_files)
        self.assertEqual(estimate.coverage_ratio, 0.0)

        # Test coverage ratio after patch
        estimate_patched = estimator.estimate(
            brief,
            workspace_files=workspace_files,
            traceback_text=traceback,
            modified_files=["events/bus.py", "events/matcher.py"],
        )
        self.assertEqual(estimate_patched.coverage_ratio, 1.0)

    def test_estimate_records_dependency_and_test_surface_reasons(self) -> None:
        estimate = ChangeSurfaceEstimator().estimate(
            "Fix pkg/api.py",
            workspace_files=["pkg/api.py", "pkg/service.py", "tests/test_api.py"],
            implicated_files={"pkg/api.py": ("task_path",)},
            dependency_edges=[("pkg/api.py", "pkg/service.py")],
            test_associations=[("tests/test_api.py", "pkg/api.py")],
        )
        self.assertIn("pkg/service.py", estimate.related_files)
        self.assertIn("tests/test_api.py", estimate.test_files)
        self.assertIn("dependency_of:pkg/api.py", estimate.reasons["pkg/service.py"])
        self.assertIn("test_for:pkg/api.py", estimate.reasons["tests/test_api.py"])


if __name__ == "__main__":
    unittest.main()
