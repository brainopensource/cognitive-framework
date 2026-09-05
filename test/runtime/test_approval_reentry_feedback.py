from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock

from vanguard.packages.kernel import FailurePath
from vanguard.packages.runtime.session import _record
from vanguard.packages.runtime.session import HarnessSession


class _Operator:
    def __init__(self) -> None:
        self.notes: list[dict[str, object]] = []

    def note(self, **note: object) -> None:
        self.notes.append(note)


class TestApprovalReentryFeedback(unittest.TestCase):
    def test_redundant_verification_narrows_the_live_engine(self) -> None:
        session = HarnessSession.__new__(HarnessSession)
        session._completion_verification = SimpleNamespace(passed=True)
        session._completion_redundant_verifications = 1
        session._completion_allowed_tools = None
        session._completion_scaffold_baseline = False
        session._active_episode_engine = MagicMock()
        session.run_plan = None
        session.harness = SimpleNamespace(composition_digest="sha256:composition")
        session.task = SimpleNamespace(run_id="run-1", brief="finish it")
        session.operator = _Operator()
        session._workspace_digest = lambda: "sha256:workspace"
        request = SimpleNamespace(
            action="proc.exec",
            args={"argv": ["python3", "-m", "unittest", "discover"]},
        )
        result = SimpleNamespace(
            failure=FailurePath.OK,
            outcome=SimpleNamespace(
                status="ok", detail="[exit 0] Ran 3 tests\nOK",
                result_digest="sha256:verification",
            ),
        )

        session._observe_completion_dispatch(request, result)

        allowed = frozenset({"agency.finish", "fs.read", "fs.search"})
        self.assertEqual(session._completion_allowed_tools, allowed)
        session._active_episode_engine.restrict_completion_tools.assert_called_once_with(
            tuple(sorted(allowed))
        )

    def test_proc_exec_success_becomes_verification_evidence(self) -> None:
        session = HarnessSession.__new__(HarnessSession)
        session._completion_verification = None
        session.run_plan = None  # BEP-01: run_plan is None-guarded in _observe_completion_dispatch
        session.harness = SimpleNamespace(composition_digest="sha256:composition")  # fallback when run_plan is None
        session.task = SimpleNamespace(run_id="run-1", brief="fix it")
        session._workspace_digest = lambda: "sha256:workspace"
        request = SimpleNamespace(
            action="proc.exec",
            args={"argv": ["python3", "-m", "unittest", "discover"]},
        )
        result = SimpleNamespace(
            failure=FailurePath.OK,
            outcome=SimpleNamespace(
                status="ok",
                detail="[exit 0] Ran 3 tests\nOK",
                result_digest="sha256:verification",
            ),
        )

        session._observe_completion_dispatch(request, result)

        self.assertIsNotNone(session._completion_verification)
        self.assertTrue(session._completion_verification.passed)
        self.assertEqual(
            session._completion_verification.workspace_digest,
            "sha256:workspace",
        )

    def test_failed_approved_dispatch_is_visible_to_the_next_model_turn(self) -> None:
        operator = _Operator()
        request = SimpleNamespace(action="proc.exec")
        result = SimpleNamespace(
            failure=FailurePath.ADAPTER_ERROR,
            outcome=None,
            detail="worker containment probes are unverified",
        )
        calls = [(request, result)]

        _record([], operator, calls, admit_context=True)

        self.assertEqual(calls, [])
        self.assertEqual(len(operator.notes), 1)
        self.assertEqual(operator.notes[0]["source"], "tool_result")
        self.assertIn("proc.exec", str(operator.notes[0]["text"]))
        self.assertIn("containment probes", str(operator.notes[0]["text"]))

    def test_non_reentry_recording_does_not_duplicate_failure_context(self) -> None:
        operator = _Operator()
        calls = [(
            SimpleNamespace(action="proc.exec"),
            SimpleNamespace(
                failure=FailurePath.ADAPTER_ERROR,
                outcome=None,
                detail="failed",
            ),
        )]

        _record([], operator, calls)

        self.assertEqual(operator.notes, [])


if __name__ == "__main__":
    unittest.main()
