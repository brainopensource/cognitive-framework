"""S-M3-B-04: drive-until-green Free→Cheap→Frontier on signed fail."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"


class SinglePlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(PACK))
        from load import load_declared_entry
        from layer0.kernel.budget import Governor
        from layer0.spi.types_gen import EpisodeView, GateDecision, Reservation, SignedVerdict

        Planner = load_declared_entry("mhf.planner.drive-until-green")
        self.governor = Governor({
            "usd_micros": 10**9, "millis": 10**9, "tokens": 10**6,
            "bytes": 0, "turns": 40, "depth": 2,
        })
        self.planner = Planner(
            governor=self.governor,
            max_repair_rounds=4,
            model_routes=("mock:free", "mock:cheap", "mock:frontier"),
        )
        self.view = EpisodeView("run-1", "ep-1", 1, "make tests green")
        self.budget = Reservation(0, 10**9, 10**6, 0, 8, 2)
        self.GateDecision = GateDecision
        self.SignedVerdict = SignedVerdict

    def test_plan_emits_patch_apply(self) -> None:
        from layer0.spi.result import Ok

        planned = self.planner.plan(self.view, self.budget)
        self.assertIsInstance(planned, Ok)
        self.assertEqual(planned.value.requests[0].verb, "patch.apply")
        self.assertEqual(self.planner.last_model, "mock:free")

    def test_verdict_fail_escalates_tier(self) -> None:
        from layer0.spi.result import Ok

        self.planner.plan(self.view, self.budget)
        self.planner.consume_verdicts(
            (self.SignedVerdict(
                verdict="fail", signature="unsigned", subject_digest="sha256:" + "0" * 64,
                evaluation_request_id="eval-1", oracle_id="oracle-1", nonce="n" * 16,
                key_id="key-1", signed_at="2026-08-20T00:00:00Z"),),
            self.GateDecision.RETRY,
        )
        planned = self.planner.plan(self.view, self.budget)
        self.assertIsInstance(planned, Ok)
        self.assertEqual(self.planner.last_model, "mock:cheap")

    def test_repair_rounds_come_from_config_not_a_hidden_constant(self) -> None:
        from layer0.spi.result import Err

        self.planner._max_repair_rounds = 1
        self.planner.plan(self.view, self.budget)
        second = self.planner.plan(self.view, self.budget)
        self.assertIsInstance(second, Err)
        self.assertEqual(second.code, "attempts_exhausted")


if __name__ == "__main__":
    unittest.main()
