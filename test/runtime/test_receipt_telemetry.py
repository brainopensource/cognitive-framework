"""T-85: the product receipt carries measured runtime evidence.

These tests drive the real ``entrypoint.execute`` -> ``Runtime`` -> ledger
path. The only seam patched is the *model*, which is the one component a
hermetic test must supply. Stubbing ``execute_profiled`` instead would leave
the assertions describing a hand-built object rather than live telemetry,
so a regression in ``RunTelemetry`` or in the shared receipt mapping would
not be visible here.
"""

from __future__ import annotations

import pathlib
import tempfile
import unittest
from unittest.mock import patch

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.runtime import entrypoint

#: A scripted turn that reports provider usage the way a real adapter does.
REPORTED_USAGE = {"prompt_tokens": 321, "completion_tokens": 89}


def _tape() -> FakeModel:
    return FakeModel([
        {
            "kind": "finish",
            "note": "deterministic preview",
            "usage": dict(REPORTED_USAGE),
        },
    ])


def _run(tmp: str) -> dict:
    store = pathlib.Path(tmp) / "events.sqlite3"
    with patch.object(entrypoint, "FakeModel", lambda _script: _tape()):
        frame = entrypoint.execute({
            "command": "code",
            "brief": "report measured receipt telemetry",
            "workspace": tmp,
            "storePath": str(store),
            "fakeBackend": "test",
            "profile": "product",
            "interactive": False,
        })
    return frame["result"]


class TestReceiptTelemetry(unittest.TestCase):
    def test_reported_tokens_reach_the_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = _run(tmp)
        self.assertEqual(receipt["promptTokens"], REPORTED_USAGE["prompt_tokens"])
        self.assertEqual(receipt["completionTokens"], REPORTED_USAGE["completion_tokens"])

    def test_model_routes_come_from_the_live_trajectory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt = _run(tmp)
        self.assertNotEqual(receipt["modelRoutes"], [])
        self.assertEqual(receipt["modelRoutes"][0]["provider"], "fake")

    def test_verified_steps_are_ledger_derived_never_invented(self) -> None:
        """No verification happened, so the set is empty -- not fabricated."""
        with tempfile.TemporaryDirectory() as tmp:
            receipt = _run(tmp)
        self.assertEqual(receipt["verifiedStepIds"], [])
        self.assertIsNone(receipt["activeStepId"])

    def test_the_success_path_holds_no_hardcoded_telemetry_constants(self) -> None:
        source = pathlib.Path(entrypoint.__file__).read_text(encoding="utf-8")
        success = source[source.index("    # T-85."):source.index("def main() -> int:")]
        for field in ("verifiedStepIds", "modelRoutes", "promptTokens",
                      "completionTokens", "spentUsdMicros"):
            for literal in (f'"{field}": []', f'"{field}": None'):
                self.assertNotIn(
                    literal, success,
                    f"success path must not hardcode {literal}",
                )

    def test_the_receipt_is_projected_through_the_shared_mapping(self) -> None:
        """T-85 forbids a second receipt algebra beside app_service's."""
        source = pathlib.Path(entrypoint.__file__).read_text(encoding="utf-8")
        self.assertIn("_result_from_execution", source)


if __name__ == "__main__":
    unittest.main()
