"""CMX-05 falsifiers: thin Coding Max facade, CLI/API parity, and true resume.

These tests pin the public Coding Max product contract:

- the facade owns request/result ergonomics and preset selection only;
- CLI and API serialize from the same ``RunResult``/``StatusResult`` types;
- resume restores durable state and never replays settled effects;
- invalid presets fail closed on both surfaces;
- app code contains no provider-specific imports or escape hatches.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import inspect
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.agency.episode.state import RunTermination
from vanguard.packages.apps.coding_max import facade as facade_module
from vanguard.packages.ports.child_runtime import ChildRunPlan
from vanguard.packages.runtime.child_runtime import RuntimeChildRunner
from vanguard.packages.runtime.trajectory import assemble_trajectory
from vanguard.packages.apps.coding_max.facade import CodingMaxFacade, InvalidPreset
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime import app_service as app_service_module
from vanguard.packages.runtime import entrypoint as entrypoint_module
from vanguard.packages.runtime.app_service import ApplicationService
from vanguard.packages.runtime.cli import main as cli_main
from vanguard.packages.runtime.results import RunResult, StatusResult


def _event_kinds(state_dir: Path, run_id: str) -> list[str]:
    store = SqliteEventStore(state_dir / "events.sqlite3")
    try:
        result = store.read(EventRange(run_id=run_id))
        events = list(result.value or ())
    finally:
        store.close()
    kinds = []
    for event in events:
        payload = getattr(event, "payload", {}) or {}
        kinds.append(str(payload.get("kind") or getattr(event, "mhf_kind", "")))
    return kinds


class TestCodingMaxFacade(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp_dir.name).resolve()
        (self.workspace / "pyproject.toml").touch()
        self.state_dir = self.workspace / ".vanguard"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        (self.state_dir / "blobs").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    # ------------------------------------------------------------------
    # Facade ergonomics and preset selection
    # ------------------------------------------------------------------

    def test_invalid_preset_fails_closed_without_runtime_effect(self) -> None:
        facade = CodingMaxFacade(workspace=self.workspace)
        with self.assertRaises(InvalidPreset):
            facade.run("do a thing", preset="turbo", state_dir=self.state_dir)
        # The rejection happened before composition: no durable run exists.
        self.assertFalse((self.state_dir / "events.sqlite3").exists())

    def test_invalid_preset_fails_closed_on_cli_surface(self) -> None:
        with self.assertRaises(SystemExit):
            cli_main([
                "code", "run", "do a thing", "-w", str(self.workspace),
                "--preset", "turbo",
            ])

    def test_facade_is_usable_by_python_callers_with_injected_service(self) -> None:
        """The facade is a plain Python client; no TypeScript CLI required.

        With a scripted one-shot ``finish`` the preset completion gate refuses
        completion, so the outcome must be a typed non-success terminal —
        never a fabricated success and never a placeholder.
        """
        service = ApplicationService(workspace=self.workspace)
        facade = CodingMaxFacade(workspace=self.workspace, service=service)
        result = facade.run(
            "python-caller brief", preset="fast", run_id="run-caller-1",
            state_dir=self.state_dir, interactive=False, max_turns=6,
        )
        self.assertIsInstance(result, RunResult)
        self.assertEqual(result.run_id, "run-caller-1")
        self.assertNotEqual(result.outcome, "completed")
        self.assertIn(result.outcome, {"instrument_error", "abandoned", "failed", "incomplete"})
        status = facade.status("run-caller-1", state_dir=self.state_dir)
        self.assertIsInstance(status, StatusResult)
        self.assertEqual(status.run_id, "run-caller-1")

    # ------------------------------------------------------------------
    # CLI/API parity: one result type, one serialization
    # ------------------------------------------------------------------

    def _cli(self, argv: list[str]) -> tuple[int, object]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exit_code = cli_main(argv)
        return exit_code, json.loads(buffer.getvalue())

    def test_cli_and_api_agree_on_run_result(self) -> None:
        facade = CodingMaxFacade(workspace=self.workspace)
        api_result = facade.run(
            "parity brief", preset="fast", run_id="run-parity-api",
            state_dir=self.state_dir, interactive=False, max_turns=6,
        )
        cli_exit, cli_payload = self._cli([
            "code", "run", "parity brief", "-w", str(self.workspace),
            "--preset", "fast", "--run-id", "run-parity-cli",
            "--non-interactive", "--max-turns", "6",
        ])
        self.assertEqual(set(cli_payload), set(api_result.to_dict()))
        for key in ("outcome", "phase", "turns"):
            self.assertEqual(cli_payload[key], api_result.to_dict()[key], key)
        # Missingness parity: an absent measurement is named, never a zero.
        if api_result.observed_cost is None:
            self.assertIn("observedCost", api_result.missing)

    def test_preset_finish_without_evidence_is_never_completed(self) -> None:
        """The CMX-04 completion gate holds at the product boundary.

        A scripted one-shot ``finish`` carries no inspection, patch, or
        verification evidence.  Both surfaces must refuse to report it as a
        completed outcome, and the CLI must exit non-zero.
        """
        facade = CodingMaxFacade(workspace=self.workspace)
        api_result = facade.run(
            "evidence-free brief", preset="balanced", run_id="run-gate-api",
            state_dir=self.state_dir, interactive=False, max_turns=6,
        )
        self.assertNotEqual(api_result.outcome, "completed")
        cli_exit, cli_payload = self._cli([
            "code", "run", "evidence-free brief", "-w", str(self.workspace),
            "--preset", "balanced", "--run-id", "run-gate-cli",
            "--non-interactive", "--max-turns", "6",
        ])
        self.assertNotEqual(cli_payload["outcome"], "completed")
        self.assertNotEqual(cli_exit, 0)

    def test_cli_and_api_agree_on_status_evidence_and_cost(self) -> None:
        facade = CodingMaxFacade(workspace=self.workspace)
        facade.run(
            "projection parity brief", preset="fast", run_id="run-parity-2",
            state_dir=self.state_dir, interactive=False, max_turns=6,
        )
        for command in ("status", "evidence", "cost"):
            cli_exit, cli_payload = self._cli([
                "code", command, "run-parity-2", "-w", str(self.workspace),
            ])
            self.assertEqual(cli_exit, 0, command)
            if command == "status":
                api_payload = facade.status(
                    "run-parity-2", state_dir=self.state_dir).to_dict()
            elif command == "evidence":
                api_payload = facade.evidence(
                    "run-parity-2", state_dir=self.state_dir).to_dict()
            else:
                api_payload = facade.cost(
                    "run-parity-2", state_dir=self.state_dir).to_dict()
            self.assertEqual(cli_payload, api_payload, command)

    def test_cli_code_commands_honor_state_dir(self) -> None:
        """`--state-dir` lets the CLI address the same durable state as the API."""
        facade = CodingMaxFacade(workspace=self.workspace)
        custom_state = self.workspace / "custom-state"
        facade.run(
            "state-dir brief", preset="fast", run_id="run-sd-1",
            state_dir=custom_state, interactive=False, max_turns=6,
        )
        exit_code, payload = self._cli([
            "code", "status", "run-sd-1", "-w", str(self.workspace),
            "--state-dir", str(custom_state),
        ])
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["runId"], "run-sd-1")
        self.assertNotEqual(payload["status"], "not_found")
        # Without the flag, the default state dir must not see this run.
        _, default_payload = self._cli([
            "code", "status", "run-sd-1", "-w", str(self.workspace),
        ])
        self.assertEqual(default_payload["status"], "not_found")

    # ------------------------------------------------------------------
    # True cold resume
    # ------------------------------------------------------------------

    def test_resume_of_terminal_run_preserves_state_without_new_effects(self) -> None:
        facade = CodingMaxFacade(workspace=self.workspace)
        facade.run(
            "resume parity brief", preset="fast", run_id="run-resume-1",
            state_dir=self.state_dir, interactive=False, max_turns=6,
        )
        kinds_before = _event_kinds(self.state_dir, "run-resume-1")
        result = facade.resume("run-resume-1", state_dir=self.state_dir)
        kinds_after = _event_kinds(self.state_dir, "run-resume-1")

        self.assertEqual(kinds_before, kinds_after, "terminal resume appended events")
        self.assertEqual(kinds_after.count("EpisodeStarted"), 1)
        self.assertEqual(result.phase, "complete")
        self.assertIn("terminal", result.detail)
        # The durable objective is the original brief, not a synthetic prompt.
        store = SqliteEventStore(self.state_dir / "events.sqlite3")
        try:
            events = list(store.read(EventRange(run_id="run-resume-1")).value or ())
        finally:
            store.close()
        for event in events:
            payload = getattr(event, "payload", {}) or {}
            for value in payload.values():
                if isinstance(value, str):
                    self.assertFalse(
                        value.startswith("Resume run "),
                        "synthetic resume prompt leaked into durable events",
                    )

    _COMPLETED_RUNNER = r"""
import json, sys
from vanguard.packages.runtime.app_service import ApplicationService

workspace, run_id = sys.argv[1], sys.argv[2]
app = ApplicationService(workspace=workspace)
result = app.run(
    brief="fresh-process continuation brief",
    profile_id="local",
    run_id=run_id,
    state_dir=None,
    interactive=False,
    max_turns=6,
)
print(json.dumps({
    "outcome": result.outcome,
    "task_digest": result.task_digest,
    "composition_digest": result.composition_digest,
}))
"""

    _FRESH_RESUMER = r"""
import json, sys
from vanguard.packages.runtime.app_service import ApplicationService

workspace, run_id = sys.argv[1], sys.argv[2]
app = ApplicationService(workspace=workspace)
result = app.resume(run_id=run_id, state_dir=None)
print(json.dumps({
    "outcome": result.outcome,
    "phase": result.phase,
    "detail": result.detail,
    "task_digest": result.task_digest,
    "composition_digest": result.composition_digest,
    "next_action": result.next_action,
}))
"""

    def test_fresh_process_resume_does_not_replay_settled_effects(self) -> None:
        run_id = "run-fresh-1"
        env = {**os.environ, "PYTHONPATH": str(ROOT)}
        first = subprocess.run(
            [sys.executable, "-c", self._COMPLETED_RUNNER,
             str(self.workspace), run_id],
            cwd=ROOT, env=env, capture_output=True, text=True, check=False,
        )
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        first_payload = json.loads(first.stdout.strip().splitlines()[-1])
        # The fresh process uses the deterministic one-shot finish path.  It
        # has no patch or verification receipt, therefore it must settle
        # without claiming completion before resume proves terminal recovery.
        self.assertNotEqual(first_payload["outcome"], "completed")

        kinds_after_run = _event_kinds(self.state_dir, run_id)

        second = subprocess.run(
            [sys.executable, "-c", self._FRESH_RESUMER,
             str(self.workspace), run_id],
            cwd=ROOT, env=env, capture_output=True, text=True, check=False,
        )
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        resume_payload = json.loads(second.stdout.strip().splitlines()[-1])

        # Cold resume restored identity and terminal semantics...
        self.assertEqual(resume_payload["phase"], "complete")
        self.assertEqual(resume_payload["task_digest"], first_payload["task_digest"])
        self.assertEqual(
            resume_payload["composition_digest"],
            first_payload["composition_digest"],
        )
        # ...without replaying any settled effect.
        kinds_after_resume = _event_kinds(self.state_dir, run_id)
        self.assertEqual(kinds_after_run, kinds_after_resume)
        self.assertEqual(kinds_after_resume.count("EpisodeStarted"), 1)

    # ------------------------------------------------------------------
    # Dependency boundary: no provider or escape hatches in app code
    # ------------------------------------------------------------------

    def test_app_code_has_no_provider_specific_imports_or_escape_hatches(self) -> None:
        app_dir = ROOT / "vanguard" / "packages" / "apps" / "coding_max"
        sources = sorted(app_dir.glob("*.py"))
        self.assertTrue(sources, "facade package must exist")
        forbidden = (
            "openrouter", "api_key", "apikey", "urllib", "requests",
            "httpx", "socket", "subprocess", "adapters", "http://", "https://",
        )
        for source in sources:
            text = source.read_text(encoding="utf-8").lower()
            for token in forbidden:
                self.assertNotIn(token, text, f"{source.name} contains {token!r}")


class _StubTelemetry:
    """Only the fields the public projection reads."""

    turns = 2
    prompt_tokens = None
    completion_tokens = None


class _StubExecution:
    """An execution result whose termination is injected, not scripted."""

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


class TestProductTerminalProjection(unittest.TestCase):
    """NT-B04 / EW-9.1 at the application service and the Coding Max facade.

    The facade is a thin client of ``ApplicationService`` and therefore has no
    mapping to correct: it inherits truthfulness by consuming the shared rule
    through the ``RunResult`` it returns. These tests pin exactly that, so a
    facade that grew its own terminal branch would fail here as loudly as a
    runtime surface that grew a second copy.
    """

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp_dir.name).resolve()
        (self.workspace / "pyproject.toml").touch()
        self.state_dir = self.workspace / ".vanguard"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        (self.state_dir / "blobs").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    @staticmethod
    def _injecting(terminal: RunTermination):
        def _stub(*_args: object, **_kwargs: object) -> _StubExecution:
            return _StubExecution(terminal)

        return mock.patch.object(
            app_service_module.Runtime, "execute_profiled", _stub)

    def _service_run(self, terminal: RunTermination, run_id: str) -> RunResult:
        service = ApplicationService(workspace=self.workspace)
        with self._injecting(terminal):
            return service.run(
                brief="terminal projection brief", profile_id="local",
                run_id=run_id, model=object(), state_dir=self.state_dir,
                interactive=False, max_turns=4,
            )

    def _entrypoint_frame(self, terminal: RunTermination, run_id: str) -> dict:
        def _stub(*_args: object, **_kwargs: object) -> _StubExecution:
            return _StubExecution(terminal)

        with mock.patch.object(entrypoint_module.Runtime, "execute_profiled", _stub):
            return entrypoint_module.execute({
                "command": "code", "brief": "sweep brief",
                "workspace": str(self.workspace), "runId": run_id,
                "storePath": str(self.state_dir / "events.sqlite3"),
                "injectedModel": object(), "profile": "product",
                "maxTurnsPerEpisode": 4,
            })

    def _facade_run(self, terminal: RunTermination, run_id: str) -> RunResult:
        facade = CodingMaxFacade(workspace=self.workspace)
        with self._injecting(terminal):
            return facade.run(
                "terminal projection brief", preset="fast", run_id=run_id,
                model=object(), state_dir=self.state_dir, interactive=False,
                max_turns=4,
            )

    def test_application_service_never_relabels_abstention_as_completion(self) -> None:
        result = self._service_run(RunTermination.ABSTAINED, "run-abstain-svc")
        self.assertEqual(result.outcome, "abstained")
        self.assertNotEqual(result.outcome, "completed")
        self.assertEqual(result.terminal_state, "abstained")

    def test_the_facade_inherits_the_truthful_projection(self) -> None:
        result = self._facade_run(RunTermination.ABSTAINED, "run-abstain-facade")
        self.assertEqual(result.outcome, "abstained")
        self.assertNotEqual(result.outcome, "completed")

    def test_an_admitted_completion_remains_successful(self) -> None:
        """No over-correction: an admitted `completed` is still a success."""
        self.assertEqual(
            self._service_run(RunTermination.COMPLETED, "run-done-svc").outcome,
            "completed")
        self.assertEqual(
            self._facade_run(RunTermination.COMPLETED, "run-done-facade").outcome,
            "completed")

    def test_other_terminals_are_carried_through_unchanged(self) -> None:
        for index, terminal in enumerate((RunTermination.ESCALATED,
                                          RunTermination.CANCELLED,
                                          RunTermination.BUDGET_EXHAUSTED)):
            with self.subTest(terminal=terminal.value):
                result = self._service_run(terminal, f"run-terminal-{index}")
                self.assertEqual(result.outcome, terminal.value)

    def test_the_facade_carries_no_terminal_mapping_or_execution_branch(self) -> None:
        """The facade stays thin; a third mapping fails this outright."""
        source = inspect.getsource(facade_module)
        self.assertNotIn("abstained", source)
        self.assertNotIn("completed", source)
        self.assertNotIn("terminal", source)
        self.assertEqual(source.count("def project_terminal_outcome"), 0)

    def test_exactly_one_projection_rule_serves_every_public_surface(self) -> None:
        """One rule, named consumers, no independent copies.

        This is the structural half of the invariant. The behavioural half —
        which is what actually protects the contract — is
        ``test_no_product_or_benchmark_surface_reports_a_refusal_as_success``
        below; this test only pins that the surfaces reach the shared rule by
        name instead of re-deriving it.
        """
        rule = app_service_module.project_terminal_outcome
        self.assertIs(entrypoint_module.project_terminal_outcome, rule)
        sources = {
            "app_service": inspect.getsource(app_service_module),
            "entrypoint": inspect.getsource(entrypoint_module),
            "facade": inspect.getsource(facade_module),
        }
        self.assertEqual(
            sum(text.count("def project_terminal_outcome") for text in sources.values()),
            1,
            "the terminal projection rule must be defined exactly once",
        )
        for name, text in sources.items():
            with self.subTest(module=name):
                self.assertNotIn('{"completed", "abstained"}', text)
        for method in (ApplicationService.run, ApplicationService.resume):
            with self.subTest(method=method.__name__):
                body = inspect.getsource(method)
                self.assertIn("project_terminal_outcome(", body)
                self.assertNotIn('{"completed", "abstained"}', body)

    # ------------------------------------------------------------------
    # The behavioural cross-surface invariant
    # ------------------------------------------------------------------

    def _child_projection(self, terminal: RunTermination) -> object:
        plan = ChildRunPlan(
            child_episode_id="ep-child-1", parent_episode_id="ep-parent-1",
            run_id="run-1", project_id="project-1", principal="agent-child",
            composition_digest="sha256:" + "3" * 64,
            goal_digest="sha256:" + "4" * 64,
            authority=("fs.read",), resources=(), depth=1, max_depth=2,
            max_turns=4, budget={}, lineage=("ep-parent-1",),
            idempotency_key="idem-1",
        )

        class _ChildResult:
            def __init__(self) -> None:
                self.terminal = terminal
                self.receipts = ()
                self.events = ()
                self.run_digest = "sha256:" + "1" * 64
                self.activation_digest = ""
                self.state_digest = "sha256:" + "2" * 64
                self.detail = ""
                self.trajectory = None

        runner = RuntimeChildRunner.__new__(RuntimeChildRunner)
        return RuntimeChildRunner._project(runner, plan, _ChildResult())

    def _trajectory_outcome(self, terminal: RunTermination, schema: str) -> str:
        from vanguard.packages.runtime.root import TaskContext

        return assemble_trajectory(
            task=TaskContext(brief="x", repo_path=Path(ROOT), run_id="r",
                             episode_id="e"),
            harness_digest="sha256:" + "0" * 64, terminal=terminal,
            receipts=(), contexts=(), events=(), verdict=None,
            schema_version=schema,
        )["outcome"]

    def test_no_product_or_benchmark_surface_reports_a_refusal_as_success(self) -> None:
        """NT-B04 swept behaviourally across every surface it names.

        For every termination in the vocabulary, each surface is executed and
        its emitted success value is read back. The invariant is one line:
        a surface reads as success **iff** the run actually completed. A
        `TaskDisposition` is never consulted or produced anywhere in the
        sweep, so termination and disposition stay orthogonal by construction.
        """
        for index, terminal in enumerate(RunTermination):
            completed = terminal is RunTermination.COMPLETED
            with self.subTest(terminal=terminal.value):
                # 1. stdio entrypoint frame
                frame = self._entrypoint_frame(terminal, f"run-sweep-e-{index}")
                self.assertEqual(frame["result"]["outcome"] == "completed", completed)
                complete_projections = [
                    p for p in frame["result"]["projections"] if p["kind"] == "complete"]
                self.assertEqual(
                    [p["outcome"] == "completed" for p in complete_projections],
                    [completed])

                # 2. application service
                svc = self._service_run(terminal, f"run-sweep-s-{index}")
                self.assertEqual(svc.outcome == "completed", completed)
                self.assertEqual(svc.terminal_state == "completed", completed)

                # 3. Coding Max facade
                fac = self._facade_run(terminal, f"run-sweep-f-{index}")
                self.assertEqual(fac.outcome == "completed", completed)

                # 4. the serialized wire form both the CLI and the API emit
                self.assertEqual(fac.to_dict()["outcome"] == "completed", completed)

                # 5. child delegation adapter
                child = self._child_projection(terminal)
                self.assertEqual(bool(child.ok), completed)
                self.assertEqual(child.outcome == "completed", completed)
                self.assertEqual(child.terminal, terminal.value.upper())

                # 6/7. benchmark writer, both frozen schema versions
                for schema in ("mhf.trajectory/1", "mhf.trajectory/2"):
                    self.assertEqual(
                        self._trajectory_outcome(terminal, schema) == "completed",
                        completed, schema)

    def test_the_refusal_case_is_covered_by_the_sweep(self) -> None:
        """Guard the guard: the vocabulary must still contain a refusal."""
        self.assertIn(RunTermination.ABSTAINED, set(RunTermination))
        self.assertGreater(len(set(RunTermination)), 2)


if __name__ == "__main__":
    unittest.main()
