"""Regression tests for the model-visible workspace capability namespace."""

from __future__ import annotations

import unittest

from vanguard.packages.ports.environment import EnvironmentProfile
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.root import Runtime
from vanguard.packages.runtime.wiring import _environment_map


class _HostPathEnvironment:
    def profile(self) -> Result[EnvironmentProfile]:
        return Result.success(EnvironmentProfile(
            environment_id="workspace:/tmp/private-vg-staging/task",
            kind="sandbox",
            root="/tmp/private-vg-staging/task",
        ))


class ModelVisibleEnvironmentTests(unittest.TestCase):
    def test_host_workspace_path_is_not_exposed_to_model_context(self) -> None:
        harness = Runtime.compose("vg-code-default", episode_id="env-map-test")
        rendered = _environment_map(_HostPathEnvironment(), harness)

        self.assertIn("environment=workspace", rendered)
        self.assertIn("root=/workspace", rendered)
        self.assertNotIn("/tmp/private-vg-staging/task", rendered)


if __name__ == "__main__":
    unittest.main()
