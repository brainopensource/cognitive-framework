"""S33: thin coding CLI/backend bridge (`REQ-TRUST-001`).

Proves request validation, free-band default, exit-code mapping, and the
scripted adaptive greenfield projection path without network or spend.
"""

from __future__ import annotations

import io
import json
import os
import unittest
from pathlib import Path

from vanguard.packages.apps.coding.coding_entrypoint import (
    EXIT_BUDGET,
    EXIT_INVALID,
    EXIT_NON_GREEN,
    EXIT_ORACLE_GREEN,
    EXIT_UNAVAILABLE,
    exit_code_for,
    load_band_models,
    request_to_config,
    run_entrypoint,
)
from vanguard.packages.apps.coding.coding_coordinator import CodingRunConfig


class ExitCodes(unittest.TestCase):
    def test_distinct_exit_codes(self) -> None:
        self.assertEqual(exit_code_for("oracle_green"), EXIT_ORACLE_GREEN)
        self.assertEqual(exit_code_for("verification_failed"), EXIT_NON_GREEN)
        self.assertEqual(exit_code_for("invalid_request"), EXIT_INVALID)
        self.assertEqual(exit_code_for("unavailable"), EXIT_UNAVAILABLE)
        self.assertEqual(exit_code_for("budget_exhausted"), EXIT_BUDGET)


class RequestValidation(unittest.TestCase):
    def test_budget_and_planner_flags_reach_config_exactly(self) -> None:
        free = load_band_models("free")
        config = request_to_config({
            "command": "code",
            "workspace": ".",
            "brief": "Build it",
            "plannerModel": "deepseek/deepseek-v4-flash",
            "executorBand": "free",
            "recoveryModels": ["deepseek/deepseek-v4-flash"],
            "maxTurnsPerEpisode": 40,
            "maxEpisodes": 12,
            "maxReplans": 2,
            "budgetUsdMicros": 50_000,
            "interactive": True,
        })
        assert isinstance(config, CodingRunConfig)
        self.assertEqual(config.planner_model, "deepseek/deepseek-v4-flash")
        self.assertEqual(config.executor_models, free)
        self.assertEqual(config.recovery_models, ("deepseek/deepseek-v4-flash",))
        self.assertEqual(config.budget_usd_micros, 50_000)
        self.assertEqual(config.max_turns_per_episode, 40)
        self.assertEqual(config.max_episodes, 12)
        self.assertEqual(config.max_replans, 2)
        self.assertTrue(config.interactive)
        high = load_band_models("high")
        self.assertTrue(set(config.executor_models).isdisjoint(high))

    def test_frontier_band_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            request_to_config({
                "command": "code",
                "workspace": ".",
                "executorBand": "high",
                "budgetUsdMicros": 50_000,
            })


class FakeBackends(unittest.TestCase):
    """`S050-C-01`: the scripted backends are test-only. `run_entrypoint`
    reaches them only behind an explicit `VANGUARD_ALLOW_FAKE=1` opt-in."""

    def setUp(self) -> None:
        self._had = os.environ.get("VANGUARD_ALLOW_FAKE")
        os.environ["VANGUARD_ALLOW_FAKE"] = "1"
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        if self._had is None:
            os.environ.pop("VANGUARD_ALLOW_FAKE", None)
        else:
            os.environ["VANGUARD_ALLOW_FAKE"] = self._had

    def test_fake_backend_is_refused_without_the_opt_in(self) -> None:
        os.environ.pop("VANGUARD_ALLOW_FAKE", None)
        try:
            code, _, result = self._run({
                "command": "code", "workspace": ".", "fakeBackend": "non-green",
                "executorBand": "free", "budgetUsdMicros": 0,
            })
            self.assertEqual(code, EXIT_INVALID)
            self.assertIn("VANGUARD_ALLOW_FAKE", result["detail"])
        finally:
            os.environ["VANGUARD_ALLOW_FAKE"] = "1"

    def _run(self, request: dict) -> tuple[int, list[dict], dict]:
        buf = io.StringIO()
        code = run_entrypoint(request, writer=buf)
        lines = [json.loads(line) for line in buf.getvalue().splitlines() if line.strip()]
        projections = [line["projection"] for line in lines if line.get("type") == "projection"]
        result = next(line["result"] for line in lines if line.get("type") == "result")
        return code, projections, result

    def test_adaptive_fake_path_emits_required_transitions(self) -> None:
        code, projections, result = self._run({
            "command": "code",
            "workspace": ".",
            "brief": "Build a task app",
            "plannerModel": "deepseek/deepseek-v4-flash",
            "executorBand": "free",
            "recoveryModels": ["deepseek/deepseek-v4-flash"],
            "budgetUsdMicros": 50_000,
            "fakeBackend": "greenfield-adaptive",
            "headless": True,
            "json": True,
        })
        self.assertEqual(code, EXIT_ORACLE_GREEN)
        kinds = [item["kind"] for item in projections]
        for required in (
            "plan", "step", "read", "write", "test", "escalate", "diagnose",
            "resume", "verified", "oracle", "complete",
        ):
            self.assertIn(required, kinds)
        self.assertEqual(result["outcome"], "oracle_green")
        self.assertEqual(result["spentUsdMicros"], 13400)
        routes = result["modelRoutes"]
        self.assertTrue(any(route.get("role") == "architect" for route in routes))
        self.assertTrue(any(route.get("reason") == "descend_after_recovery" for route in routes))

    def test_non_green_and_budget_have_distinct_exits(self) -> None:
        non_green_code, _, non_green = self._run({
            "command": "code", "workspace": ".", "fakeBackend": "non-green",
            "executorBand": "free", "budgetUsdMicros": 0,
        })
        budget_code, _, budget = self._run({
            "command": "code", "workspace": ".", "fakeBackend": "budget-exhausted",
            "executorBand": "free", "budgetUsdMicros": 1000,
        })
        unavailable_code, _, _ = self._run({
            "command": "code", "workspace": ".", "fakeBackend": "unavailable",
            "executorBand": "free", "budgetUsdMicros": 0,
        })
        self.assertEqual(non_green_code, EXIT_NON_GREEN)
        self.assertEqual(budget_code, EXIT_BUDGET)
        self.assertEqual(unavailable_code, EXIT_UNAVAILABLE)
        self.assertEqual(non_green["outcome"], "verification_failed")
        self.assertEqual(budget["outcome"], "budget_exhausted")

    def test_explain_cites_observed_paths(self) -> None:
        code, projections, result = self._run({
            "command": "explain",
            "workspace": ".",
            "question": "Explain the authorization path",
        })
        self.assertEqual(code, EXIT_ORACLE_GREEN)
        self.assertTrue(any(
            item.get("kind") == "read" and "dispatch.py" in str(item.get("path"))
            for item in projections
        ))
        self.assertIn("dispatch", result["detail"])

    def test_invalid_request_exits_2(self) -> None:
        code, _, result = self._run({
            "command": "explain",
            "workspace": ".",
            "question": "",
        })
        self.assertEqual(code, EXIT_INVALID)
        self.assertEqual(result["outcome"], "invalid_request")

    def test_no_model_routing_loop_in_entrypoint_source(self) -> None:
        root = Path(__file__).resolve().parents[2] / "vanguard" / "packages"
        source = root / "apps" / "coding" / "coding_entrypoint.py"
        if not source.is_file():
            source = root / "runtime" / "coding_entrypoint.py"
        text = source.read_text(encoding="utf-8")
        for banned in (
            "OpenRouterModel(",
            "OllamaModel(",
            "Kernel.dispatch",
            "bubblewrap",
            "while True:\n            route",
        ):
            self.assertNotIn(banned, text)


class LiveBinder(unittest.TestCase):
    """`TSK-HAR-004`: `--live` composes HarnessSession; it does not hard-refuse."""

    def test_live_without_fake_backend_reaches_lab_driver(self) -> None:
        from unittest.mock import patch

        fake_lab = {
            "outcome": "instrument_error:openrouter_unavailable",
            "attempts": 1,
            "turns": 0,
            "detail": "OPENROUTER_API_KEY is not set",
            "grantId": None,
            "promptTokens": None,
            "completionTokens": None,
        }

        with patch(
            "vanguard.packages.runtime.lab_driver.run_lab_task",
            return_value=fake_lab,
        ) as mocked:
            buf = io.StringIO()
            code = run_entrypoint({
                "command": "code",
                "workspace": ".",
                "brief": "TASK.md",
                "live": True,
                "executorBand": "free",
                "budgetUsdMicros": 0,
                "plannerModel": "cohere/north-mini-code:free",
            }, writer=buf)
        self.assertTrue(mocked.called)
        self.assertEqual(code, EXIT_UNAVAILABLE)
        result = next(
            json.loads(line)["result"]
            for line in buf.getvalue().splitlines()
            if line.strip() and json.loads(line).get("type") == "result"
        )
        self.assertEqual(result["outcome"], "unavailable")


if __name__ == "__main__":
    unittest.main()
