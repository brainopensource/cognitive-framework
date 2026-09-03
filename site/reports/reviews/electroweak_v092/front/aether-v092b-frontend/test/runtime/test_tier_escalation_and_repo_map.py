"""Tests for modular tier escalation and repo map index observation.

REQ-TRUST-001, S6B-MD-004, S10-A-03.
"""

from __future__ import annotations

import dataclasses
import tempfile
import unittest
from pathlib import Path
from typing import Any

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.adapters.stores.repo_index import InMemoryRepoIndex
from vanguard.packages.agency.context.layers import Layer
from vanguard.packages.ports.environment import EnvironmentProfile
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.determinism import SystemClock
from vanguard.packages.runtime.model_selection import select_model
from vanguard.packages.runtime.tier_escalation import ModelRole, RoleAwareRouter
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)


class _FakeEnv:
    def profile(self) -> Result[Any]:
        return Result.success(EnvironmentProfile(
            environment_id="fake:/workspace", kind="memory", root="/workspace"))

    def observe(self, req: Any, grant: Any = None) -> Result[Any]:
        return Result.success(None)

    def apply(self, req: Any, grant: Any = None) -> Result[Any]:
        return Result.success(None)

    def dispose(self) -> Result[None]:
        return Result.success(None)


class TestTierEscalationAndRepoMap(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo_dir = Path(self._tmp.name)
        (self.repo_dir / "src").mkdir()
        (self.repo_dir / "src" / "main.py").write_text("def run():\n    return 42\n")
        (self.repo_dir / "TASK.md").write_text("Fix the calculation in main.py")

    def test_repo_map_is_included_in_session_environment(self) -> None:
        base_harness = Runtime.compose("vg-code-default", episode_id="test-ep-1")
        harness = dataclasses.replace(base_harness, index_component="repo_index.json")
        index = InMemoryRepoIndex({
            "src/main.py": "def run():\n    return 42\n",
        })
        store = SqliteEventStore(":memory:")
        ports = SessionPorts(
            model=FakeModel([]),
            environment=_FakeEnv(),
            clock=SystemClock(),
            store=store,
            index=index,
            interactive=True,
        )
        task = TaskContext(
            brief="Fix calculation",
            repo_path=self.repo_dir,
            run_id="test-run",
            episode_id="test-ep-1",
            max_turns=2,
        )
        session = HarnessSession(harness, ports, task)
        env_blocks = [b.text for b in session.operator._compiler._prefix if b.layer == Layer.ENVIRONMENT]
        env_text = "\n".join(env_blocks)
        self.assertIn("=== Workspace Repository Map ===", env_text)
        self.assertIn("src/main.py", env_text)
        self.assertIn("function run:1", env_text)

    def test_select_model_router_port(self) -> None:
        selected = select_model("router", env={"OPENROUTER_API_KEY": "test-key"})
        self.assertEqual(selected.port, "router")
        self.assertTrue(selected.label.startswith("router:"))

    def test_role_router_records_reason_and_refuses_unapproved_paid_model(self) -> None:
        router = RoleAwareRouter(bands={"free": ("openrouter/free",),
                                        "medium": ("deepseek/deepseek-v4-flash",)})
        executor = router.choose(ModelRole.EXECUTOR, episode_id="ep-1",
                                 reason="ready_step")
        self.assertEqual(executor.band, "free")
        self.assertEqual(executor.reason, "ready_step")
        self.assertTrue(executor.pricing_known)
        with self.assertRaises(ValueError):
            router.choose(ModelRole.ARCHITECT, episode_id="ep-2",
                          reason="initial_plan", allow_paid=False)


if __name__ == "__main__":
    unittest.main()
