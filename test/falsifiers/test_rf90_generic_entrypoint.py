"""RF-90 (ADR-0089): code, explain, and doctor share one entrypoint."""

from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from vanguard.packages.agency.episode.state import RunTermination
from vanguard.packages.runtime import entrypoint


class _StubTelemetry:
    """Only the fields the public projection reads."""

    turns = 3
    prompt_tokens = None
    completion_tokens = None


class _StubExecution:
    """An execution result whose termination is injected, not scripted.

    NT-B04 is a projection contract, so the falsifier injects the termination
    directly rather than persuading a model to refuse. That keeps the assertion
    on the mapping under test and off the episode loop.
    """

    def __init__(self, terminal: RunTermination) -> None:
        self.terminal = terminal
        self.receipts = ()
        self.events = ()
        self.telemetry = _StubTelemetry()
        self.run_digest = "sha256:" + "0" * 64
        self.state_digest = None
        self.detail = "injected termination"
        self.trajectory = {}
        self.composition_digest = None


class RF90GenericEntrypointFalsifier(unittest.TestCase):
    def test_doctor_is_available_without_model_or_network(self) -> None:
        frame = entrypoint.execute({"command": "doctor"})
        self.assertEqual(frame["type"], "result")
        self.assertEqual(frame["result"]["phase"], "doctor")
        self.assertIsNotNone(frame["result"]["planDigest"])

    def test_code_and_explain_resolve_the_shared_manifest_entrypoint(self) -> None:
        self.assertEqual(entrypoint._manifest("code").name, "manifest.json")
        self.assertEqual(entrypoint._manifest("explain").name, "manifest.json")
        self.assertIn("vg-code-balanced", str(entrypoint._manifest("code")))
        self.assertIn("vg-code-explain", str(entrypoint._manifest("explain")))

    def test_code_with_fake_backend_executes_cleanly(self) -> None:
        frame = entrypoint.execute({
            "command": "code",
            "brief": "test brief",
            "workspace": ".",
            "fakeBackend": "greenfield-adaptive",
            "profile": "product",
        })
        self.assertEqual(frame["type"], "result")
        # The fake backend emits a bare finish, which must be rejected without
        # patch and verification receipts.
        self.assertNotEqual(frame["result"]["outcome"], "completed")

    def test_resume_command_executes_without_explicit_brief(self) -> None:
        frame = entrypoint.execute({
            "command": "resume",
            "runId": "run-test-resume",
            "workspace": ".",
            "fakeBackend": "greenfield-adaptive",
            "profile": "product",
        })
        self.assertEqual(frame["type"], "result")
        self.assertNotEqual(frame["result"]["outcome"], "completed")


class RF90EntrypointTerminalProjection(unittest.TestCase):
    """NT-B04 at the stdio entrypoint, one of the two public surfaces."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self._tmp.name).resolve()
        (self.workspace / "pyproject.toml").touch()
        self.state_dir = self.workspace / ".vanguard"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        (self.state_dir / "blobs").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _execute(self, terminal: RunTermination, **overrides: object) -> dict:
        request = {
            "command": "code",
            "brief": "terminal projection brief",
            "workspace": str(self.workspace),
            "storePath": str(self.state_dir / "events.sqlite3"),
            "injectedModel": object(),
            "profile": "product",
            "maxTurnsPerEpisode": 4,
        }
        request.update(overrides)

        def _stub(*_args: object, **_kwargs: object) -> _StubExecution:
            return _StubExecution(terminal)

        with mock.patch.object(entrypoint.Runtime, "execute_profiled", _stub):
            return entrypoint.execute(request)

    def test_an_abstained_run_is_never_reported_as_completed(self) -> None:
        """A refusal keeps its own name at the stdio boundary."""
        frame = self._execute(RunTermination.ABSTAINED)
        self.assertEqual(frame["result"]["outcome"], "abstained")
        self.assertNotEqual(frame["result"]["outcome"], "completed")
        complete = [p for p in frame["result"]["projections"] if p["kind"] == "complete"]
        self.assertEqual([p["outcome"] for p in complete], ["abstained"])

    def test_resume_preserves_abstention_too(self) -> None:
        """The resume command projects through the same rule."""
        frame = self._execute(
            RunTermination.ABSTAINED, command="resume", runId="run-abstain-resume")
        self.assertEqual(frame["result"]["outcome"], "abstained")

    def test_an_admitted_completion_remains_successful(self) -> None:
        """The repair must not over-correct: `completed` still means completed."""
        frame = self._execute(RunTermination.COMPLETED)
        self.assertEqual(frame["result"]["outcome"], "completed")

    def test_other_terminals_are_carried_through_unchanged(self) -> None:
        for terminal in (RunTermination.ESCALATED, RunTermination.CANCELLED,
                         RunTermination.BUDGET_EXHAUSTED):
            with self.subTest(terminal=terminal.value):
                frame = self._execute(terminal)
                self.assertEqual(frame["result"]["outcome"], terminal.value)

    def test_the_entrypoint_owns_no_terminal_mapping_of_its_own(self) -> None:
        """Mutation sensitivity: a re-introduced local copy fails here."""
        source = inspect.getsource(entrypoint)
        self.assertNotIn('{"completed", "abstained"}', source)
        self.assertEqual(source.count("def project_terminal_outcome"), 0)
        self.assertIn("project_terminal_outcome(result.terminal)", source)


if __name__ == "__main__":
    unittest.main()
