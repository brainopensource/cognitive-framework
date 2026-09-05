"""T-85: the product entrypoint exposes measured runtime evidence."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from vanguard.packages.runtime import entrypoint


class TestReceiptTelemetry(unittest.TestCase):
    def test_success_receipt_projects_runtime_telemetry_and_verified_steps(self) -> None:
        execution = SimpleNamespace(
            terminal="completed",
            detail="verified",
            run_digest="sha256:run",
            receipts=(),
            events=(SimpleNamespace(payload={
                "kind": "EpisodeStateChanged",
                "verifiedStepIds": ["sha256:verification"],
            }),),
            telemetry=SimpleNamespace(
                turns=2, prompt_tokens=321, completion_tokens=89,
            ),
            trajectory={
                "model_routes_used": [{"provider": "test", "model": "frontier"}],
                "cost": {
                    "usd_micros": 17,
                    "measurement_status": {
                        "usd_micros": {"status": "measured"},
                    },
                },
            },
        )
        with tempfile.TemporaryDirectory() as tmp, patch(
            "vanguard.packages.runtime.entrypoint.Runtime.execute_profiled",
            return_value=execution,
        ):
            frame = entrypoint.execute({
                "command": "code",
                "brief": "report measured receipt telemetry",
                "workspace": str(Path(tmp)),
                "fakeBackend": "test",
                "profile": "product",
                "interactive": False,
            })

        receipt = frame["result"]
        self.assertEqual(receipt["verifiedStepIds"], ["sha256:verification"])
        self.assertEqual(receipt["modelRoutes"], [{"provider": "test", "model": "frontier"}])
        self.assertEqual(receipt["promptTokens"], 321)
        self.assertEqual(receipt["completionTokens"], 89)
        self.assertEqual(receipt["spentUsdMicros"], 17)
        self.assertNotEqual(receipt["modelRoutes"], [])


if __name__ == "__main__":
    unittest.main()
