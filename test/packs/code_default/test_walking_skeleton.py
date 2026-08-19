"""S-M3-B-07: compose() + discovered plugins, no hardcoded toolkit imports in Layer-0."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"


class WalkingSkeletonTests(unittest.TestCase):
    def test_compose_then_one_turn_via_manifest_entries(self) -> None:
        sys.path.insert(0, str(PACK))
        from load import compile_pack, load_declared_entry
        from layer0.kernel.budget import Governor
        from layer0.spi.result import Ok
        from layer0.spi.types_gen import EffectContext, EpisodeView, Reservation

        frozen = compile_pack()
        self.assertEqual(frozen.id, "code-default")
        self.assertIn("planner", frozen.resolved_refs)

        tmp = tempfile.TemporaryDirectory()
        try:
            workspace = Path(tmp.name)
            (workspace / "src").mkdir()
            (workspace / "src" / "app.py").write_text("# seed\n", encoding="utf-8")
            Planner = load_declared_entry("mhf.planner.drive-until-green")
            Toolkit = load_declared_entry("mhf.toolkit.ast-patch")
            Gate = load_declared_entry("mhf.eval.oracle-gate")
            planner = Planner(
                governor=Governor({
                    "usd_micros": 10**6, "millis": 10**9, "tokens": 10**6,
                    "bytes": 0, "turns": 8, "depth": 2,
                }),
                max_repair_rounds=4,
            )
            toolkit = Toolkit(workspace)
            gate = Gate()
            planned = planner.plan(EpisodeView("run-w", "ep-w", 1, "fix"), Reservation(0, 10**6, 8000, 0, 4, 2))
            self.assertIsInstance(planned, Ok)
            receipt = toolkit.execute(
                planned.value.requests[0],
                EffectContext(principal="walker", run_id="run-w", episode_id="ep-w"),
            )
            self.assertIsInstance(receipt, Ok)
            planner.observe((receipt.value,), EpisodeView("run-w", "ep-w", 1, "fix"))
            from layer0.spi.types_gen import EvaluationSubject

            asked = gate.request(EvaluationSubject(run_id="run-w", episode_id="ep-w"))
            self.assertIsInstance(asked, Ok)
        finally:
            tmp.cleanup()

    def test_layer0_and_runtime_do_not_hardcode_pack_toolkits(self) -> None:
        import re

        pattern = re.compile(r"import.*ast_patch|import.*terminal_runner")
        hits: list[str] = []
        for root in (ROOT / "layer0", ROOT / "vanguard" / "packages" / "runtime"):
            for path in root.rglob("*.py"):
                text = path.read_text(encoding="utf-8")
                if pattern.search(text):
                    hits.append(str(path))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
