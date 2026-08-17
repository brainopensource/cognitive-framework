"""W14-A: honest live brain, real driver, both modes under a proposing model.

`REQ-TRUST-001`. The two failures this wave exists to prevent are a run that
reports a pass it did not earn, and a test that reports a pass because the
backend was absent. They look the same in a summary and mean opposite things.
"""

from __future__ import annotations

import inspect
import json
import tempfile
import unittest
from pathlib import Path

import lab.run as lab_run
from vanguard.packages.kernel import (
    Constraints,
    EffectRequest,
    FailurePath,
    Mode,
    Outcome,
    Scope,
    StandardPolicy,
)
from vanguard.packages.runtime.model_selection import (
    MODEL_PORTS,
    ModelUnavailable,
    select_model,
)
from vanguard.packages.runtime.repair import StopReason

RESOURCE = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}


class MockIsTheCiBrain(unittest.TestCase):
    def test_the_default_port_is_mock(self) -> None:
        self.assertEqual(select_model().port, "mock")

    def test_mock_needs_no_network_and_no_key(self) -> None:
        selected = select_model("mock", env={})
        self.assertEqual(selected.label, "mock-scripted")

    def test_every_advertised_port_is_selectable_or_named_unavailable(self) -> None:
        for port in MODEL_PORTS:
            with self.subTest(port=port):
                try:
                    select_model(port, probe=lambda e: False, env={})
                except ModelUnavailable as unavailable:
                    self.assertTrue(unavailable.instrument_error.startswith(
                        "instrument_error:"))

    def test_an_unknown_port_is_refused_by_name(self) -> None:
        with self.assertRaises(ModelUnavailable):
            select_model("gpt-by-vibes")


class AbsentBackendsFailClosed(unittest.TestCase):
    """Skip-closed, never skip-as-pass."""

    def test_a_down_ollama_daemon_is_an_instrument_error(self) -> None:
        with self.assertRaises(ModelUnavailable) as caught:
            select_model("ollama", probe=lambda endpoint: False)
        self.assertEqual(caught.exception.instrument_error,
                         "instrument_error:ollama_unavailable")

    def test_the_daemon_is_probed_once_not_per_turn(self) -> None:
        """Discovering it is down on turn six wastes the turns before it."""

        calls: list[str] = []
        with self.assertRaises(ModelUnavailable):
            select_model("ollama", probe=lambda e: calls.append(e) or False)
        self.assertEqual(len(calls), 1)

    def test_a_live_ollama_is_labelled_with_its_tag(self) -> None:
        selected = select_model("ollama", model_name="deepseek-r1",
                                probe=lambda e: True)
        self.assertEqual(selected.label, "ollama:deepseek-r1")

    def test_a_missing_api_key_is_refused_not_defaulted(self) -> None:
        with self.assertRaises(ModelUnavailable) as caught:
            select_model("openrouter", env={})
        self.assertIn("OPENROUTER_API_KEY", caught.exception.reason)


class OnlyFreeModelsAreReachable(unittest.TestCase):
    """`D-13`: `top` stays empty until `S9-J-03` authorises spend."""

    ENV = {"OPENROUTER_API_KEY": "test-key"}

    def test_a_free_model_is_selected(self) -> None:
        selected = select_model("openrouter", env=self.ENV,
                                free_models=lambda: ["vendor/model:free"])
        self.assertEqual(selected.label, "openrouter:vendor/model:free")

    def test_a_paid_model_is_refused_even_when_named_explicitly(self) -> None:
        """A paid model reached by typo is still paid; the bill arrives anyway."""

        with self.assertRaises(ModelUnavailable) as caught:
            select_model("openrouter", model_name="vendor/expensive",
                         env=self.ENV, free_models=lambda: ["vendor/model:free"])
        self.assertIn("refusing to spend", caught.exception.reason)

    def test_an_empty_free_band_refuses_rather_than_falling_back(self) -> None:
        with self.assertRaises(ModelUnavailable) as caught:
            select_model("openrouter", env=self.ENV, free_models=lambda: [])
        self.assertIn("S9-J-03", caught.exception.reason)

    def test_deepseek_reuses_the_existing_client(self) -> None:
        """No fourth HTTP client: `deepseek` selects the adapter already here."""

        source = inspect.getsource(select_model)
        self.assertIn("OpenRouterModel", source)
        self.assertNotIn("http.client", source)


def _scope(actions, depth: int = 0) -> Scope:
    return Scope(actions=frozenset(actions), resources=(RESOURCE,),
                 constraints=Constraints(expires_at="2099-01-01T00:00:00.000Z",
                                         max_uses=100, budget_usd_micros=1_000_000,
                                         max_depth=4),
                 depth=depth)


class BothModesHoldUnderAProposingModel(unittest.TestCase):
    """W14 item 6, against the real `StandardPolicy`. No mock kernel."""

    SCOPE = _scope({"fs.read", "patch.apply", "proc.exec"})

    def _policy(self, mode: Mode) -> StandardPolicy:
        return StandardPolicy(
            parent_scope=self.SCOPE, mode=mode, approval_required_above="low",
            risk_of={"fs.read": "low", "patch.apply": "medium", "proc.exec": "high"})

    def _request(self, action: str) -> EffectRequest:
        return EffectRequest(action=action, resource=RESOURCE, args={"x": 1},
                             principal="agent-1", run_id="run-modes")

    def test_interactive_suspends_a_privileged_proposal(self) -> None:
        for action in ("patch.apply", "proc.exec"):
            with self.subTest(action=action):
                decision = self._policy(Mode.INTERACTIVE).authorize(
                    self._request(action), widens_capability=False,
                    requested_scope=self.SCOPE)
                self.assertIs(decision.outcome, Outcome.REQUIRE_APPROVAL)

    def test_benchmark_denies_the_same_proposal(self) -> None:
        for action in ("patch.apply", "proc.exec"):
            with self.subTest(action=action):
                decision = self._policy(Mode.BENCHMARK).authorize(
                    self._request(action), widens_capability=False,
                    requested_scope=self.SCOPE)
                self.assertIs(decision.outcome, Outcome.REJECT)
                self.assertIs(decision.failure, FailurePath.DENIED_ASK_FAIL_CLOSED)

    def test_a_low_risk_verb_is_unaffected_in_both_modes(self) -> None:
        for mode in (Mode.INTERACTIVE, Mode.BENCHMARK):
            with self.subTest(mode=mode):
                decision = self._policy(mode).authorize(
                    self._request("fs.read"), widens_capability=False,
                    requested_scope=self.SCOPE)
                self.assertIs(decision.outcome, Outcome.ALLOW)


class TheDriverRunsRatherThanReports(unittest.TestCase):
    """The defect this wave repaired: `lab/run.py` fabricated its result."""

    def test_the_driver_calls_the_session(self) -> None:
        source = inspect.getsource(lab_run)
        self.assertIn("HarnessSession", source)
        self.assertIn("drive_until_green", source)

    def test_it_no_longer_hardcodes_a_completed_status(self) -> None:
        """Checked in the function body, not the module docstring — which
        quotes the removed literal on purpose, as the record of what was
        there."""

        source = inspect.getsource(lab_run.run_lab_task)
        self.assertNotIn('"status": "completed"', source)
        self.assertNotIn('"turnCount": 1', source)

    def test_it_wraps_no_second_loop_around_the_engine(self) -> None:
        source = inspect.getsource(lab_run)
        self.assertNotIn("while True", source)
        self.assertNotIn("EpisodeEngine(", source)

    def test_a_missing_task_dir_is_inconclusive_not_completed(self) -> None:
        result = lab_run.run_lab_task("vg-code-default", "/nowhere/at/all")
        self.assertEqual(result["outcome"], "inconclusive:workspace_missing")

    def test_an_unavailable_backend_is_an_instrument_error_not_a_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = lab_run.run_lab_task(
                "vg-code-default", tmp, model_port="openrouter")
            self.assertEqual(result["outcome"], StopReason.INSTRUMENT_ERROR)
            self.assertNotEqual(result["outcome"], StopReason.ORACLE_GREEN)

    def test_the_cli_exposes_the_required_switches(self) -> None:
        source = inspect.getsource(lab_run.main)
        for switch in ("--model", "--interactive", "--benchmark",
                       "--max-turns", "--jsonl-out"):
            self.assertIn(switch, source)

    def test_a_non_green_run_exits_non_zero(self) -> None:
        source = inspect.getsource(lab_run.main)
        self.assertIn("ORACLE_GREEN", source)


class TheExporterOpensNoStore(unittest.TestCase):
    """W14 item 7: the projection reads the JSONL it is handed."""

    SOURCE = (Path(__file__).resolve().parents[2] / "tools"
              / "export_coding_session.py").read_text(encoding="utf-8")

    def test_it_names_no_database(self) -> None:
        for forbidden in ("sqlite3", "connect("):
            self.assertNotIn(forbidden, self.SOURCE)

    def test_it_reads_only_the_jsonl_it_was_given(self) -> None:
        self.assertIn("--jsonl", self.SOURCE)


if __name__ == "__main__":
    unittest.main()
