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
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.apps.coding_max.facade import CodingMaxFacade, InvalidPreset
from vanguard.packages.ports.event_store import EventRange
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
        self.assertEqual(first_payload["outcome"], "completed")

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


if __name__ == "__main__":
    unittest.main()
