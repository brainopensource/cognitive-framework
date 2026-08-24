"""S20: the runner is frozen and a live model completes tool-calling turns.

`REQ-TRUST-001`. The v0.4.5 question is not "did the model score" — it is
"can a live model reach the loop at all, and when it cannot, does the harness
say why in words that name a cause".
"""

from __future__ import annotations

import inspect
import unittest
from unittest.mock import patch

from vanguard.packages.adapters.models.ollama import _tool_payload
from vanguard.packages.runtime import lab_driver
from vanguard.packages.runtime.model_selection import (
    DEFAULT_LOCAL_TIMEOUT_SECONDS,
    ModelUnavailable,
    select_model,
)


class ProviderShapeIsSent(unittest.TestCase):
    """A manifest tool must reach the endpoint in function-calling shape."""

    MANIFEST_TOOL = {
        "name": "read", "verb": "fs.read", "description": "Read a file.",
        "schema": {"type": "object", "properties": {"path": {"type": "string"}},
                   "required": ["path"]},
    }

    def test_a_manifest_tool_becomes_a_function(self) -> None:
        payload = _tool_payload(self.MANIFEST_TOOL)
        self.assertEqual(payload["type"], "function")
        self.assertEqual(payload["function"]["name"], "read")
        self.assertIn("path", payload["function"]["parameters"]["properties"])

    def test_the_manifest_shape_is_not_forwarded_raw(self) -> None:
        """Forwarding `{name, verb, schema}` produced HTTP 500 on every call."""

        payload = _tool_payload(self.MANIFEST_TOOL)
        self.assertNotIn("verb", payload)
        self.assertNotIn("schema", payload)

    def test_a_tool_already_in_provider_shape_passes_through(self) -> None:
        provider = {"type": "function", "function": {"name": "x", "parameters": {}}}
        self.assertEqual(_tool_payload(provider), provider)

    def test_a_tool_without_a_schema_still_renders(self) -> None:
        payload = _tool_payload({"name": "noop", "verb": "x.noop"})
        self.assertEqual(payload["function"]["parameters"]["type"], "object")


class ProbeAndTimeoutAreInstrumentConcerns(unittest.TestCase):
    def test_a_reasoning_model_gets_a_generous_ceiling(self) -> None:
        """60s turned a long think block into `timed out`, which read like a
        model scoring zero."""

        self.assertGreaterEqual(DEFAULT_LOCAL_TIMEOUT_SECONDS, 300.0)

    def test_the_selected_model_carries_the_timeout(self) -> None:
        selected = select_model("ollama", probe=lambda e: True,
                                model_name="any:tag", timeout_seconds=123.0)
        self.assertEqual(selected.model.timeout_seconds, 123.0)

    def test_an_absent_tag_is_refused_by_name(self) -> None:
        with patch(
            "vanguard.packages.runtime.model_selection._ollama_tags",
            return_value=("installed:tag",),
        ), self.assertRaises(ModelUnavailable) as caught:
            select_model("ollama", model_name="definitely-not-pulled")
        self.assertIn("not pulled", caught.exception.reason)


class TheProvidersReasonSurvives(unittest.TestCase):
    """S20-A-01: `model_not_invoked` is the shape of a failure, not its cause."""

    def test_the_driver_prefers_the_run_detail_on_an_instrument_error(self) -> None:
        source = inspect.getsource(lab_driver.run_lab_task)
        self.assertIn("INSTRUMENT_ERROR", source)
        self.assertIn('getattr(last, "detail"', source)

    def test_the_driver_still_reports_a_named_outcome(self) -> None:
        result = lab_driver.run_lab_task("vg-code-default", "/nowhere/at/all")
        self.assertEqual(result["outcome"], "inconclusive:workspace_missing")
        self.assertTrue(result["detail"])


class TheEntrypointsAreFrozen(unittest.TestCase):
    """S20-A-05. Two entrypoints, no daemon invented."""

    def test_the_module_entrypoint_has_a_main(self) -> None:
        self.assertTrue(callable(lab_driver.main))

    def test_the_shim_delegates_to_the_module(self) -> None:
        from pathlib import Path

        shim = (Path(__file__).resolve().parents[2] / "benchmarks" / "run.py"
                ).read_text(encoding="utf-8")
        self.assertIn("vanguard.packages.runtime.lab_driver", shim)
        self.assertNotIn("HarnessSession", shim)

    def test_no_daemon_was_invented(self) -> None:
        source = inspect.getsource(lab_driver)
        for forbidden in ("socket", "daemon", "serve_forever"):
            self.assertNotIn(forbidden, source)

    def test_every_frozen_flag_is_present(self) -> None:
        source = inspect.getsource(lab_driver.main)
        for flag in ("--pack", "--task-dir", "--model", "--interactive",
                     "--benchmark", "--max-turns", "--jsonl-out"):
            self.assertIn(flag, source)


if __name__ == "__main__":
    unittest.main()
