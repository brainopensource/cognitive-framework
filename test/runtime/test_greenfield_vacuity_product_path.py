"""T-81: red-on-stub evidence must reach the public completion policy."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.kernel import FailurePath
from vanguard.packages.runtime.entrypoint import _completion_policy, _manifest
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext


def _result(exit_code: int, tests: int = 1):
    return SimpleNamespace(
        failure=FailurePath.OK,
        outcome=SimpleNamespace(
            status="ok" if exit_code == 0 else "failed",
            detail=f"[exit {exit_code}] Ran {tests} test{'s' if tests != 1 else ''}",
            result_digest=f"sha256:result-{exit_code}",
        ),
    )


class TestGreenfieldVacuityProductPath(unittest.TestCase):
    def test_stub_red_then_implementation_green_is_required_by_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            harness = Runtime.compose("vg-code-default", episode_id="ep-greenfield")
            session = HarnessSession(
                harness,
                SessionPorts(
                    model=FakeModel([]),
                    environment=FakeEnvironment(),
                    clock=FakeClock(),
                    store=SqliteEventStore(":memory:"),
                    interactive=False,
                    completion_policy=_completion_policy(_manifest("code")),
                ),
                TaskContext(
                    brief="Create a greenfield project from scratch",
                    repo_path=root,
                    run_id="run-greenfield",
                    episode_id="ep-greenfield",
                ),
            )

            (root / "app.py").write_text("def fibonacci(n):\n    pass\n", encoding="utf-8")
            (root / "test_app.py").write_text(
                "def test_fibonacci():\n    assert False\n", encoding="utf-8"
            )
            for relative in ("app.py", "test_app.py"):
                session._observe_completion_dispatch(
                    SimpleNamespace(action="patch.apply", args={"path": relative}),
                    _result(0),
                )
            test_request = SimpleNamespace(
                action="proc.exec",
                args={"argv": ["python3", "-m", "unittest", "test_app.py"]},
            )
            session._observe_completion_dispatch(test_request, _result(1))
            self.assertTrue(session._completion_oracle_failed_on_stub)

            (root / "app.py").write_text(
                "def fibonacci(n):\n    return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)\n",
                encoding="utf-8",
            )
            session._observe_completion_dispatch(
                SimpleNamespace(action="patch.apply", args={"path": "app.py"}),
                _result(0),
            )
            session._observe_completion_dispatch(test_request, _result(0))
            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertTrue(verdict.admissible, verdict.reason)

    def test_green_without_observed_stub_failure_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = HarnessSession(
                Runtime.compose("vg-code-default", episode_id="ep-vacuous"),
                SessionPorts(
                    model=FakeModel([]), environment=FakeEnvironment(), clock=FakeClock(),
                    store=SqliteEventStore(":memory:"), interactive=False,
                    completion_policy=_completion_policy(_manifest("code")),
                ),
                TaskContext(
                    brief="Create a greenfield project from scratch", repo_path=root,
                    run_id="run-vacuous", episode_id="ep-vacuous",
                ),
            )
            (root / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
            (root / "test_app.py").write_text("def test_value():\n    assert True\n", encoding="utf-8")
            for relative in ("app.py", "test_app.py"):
                session._observe_completion_dispatch(
                    SimpleNamespace(action="patch.apply", args={"path": relative}), _result(0)
                )
            session._observe_completion_dispatch(
                SimpleNamespace(
                    action="proc.exec",
                    args={"argv": ["python3", "-m", "unittest", "test_app.py"]},
                ),
                _result(0),
            )
            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertFalse(verdict.admissible)
            self.assertEqual(verdict.reason, "VACUOUS_ORACLE")


if __name__ == "__main__":
    unittest.main()
