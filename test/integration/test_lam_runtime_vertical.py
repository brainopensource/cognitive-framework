"""Production composition vertical slice for the offline LAM provider."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.models.lam import LamModelAdapter
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import Runtime, TaskContext
from vanguard.packages.agency import RunTermination


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"


class _Verifier:
    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        return Result.success(Verdict(
            outcome="claims",
            claims=({"claim": "vertical_slice", "holds": True},),
            reason=protocol.name,
        ))


class _RecordingLam:
    def __init__(self) -> None:
        self.inner = LamModelAdapter(model_name="lam/t0-vanguard-vertical")
        self.contexts: list[dict] = []

    def propose(self, context, tools, sampling):
        self.contexts.append(dict(context))
        return self.inner.propose(context, tools, sampling)


class TestLamRuntimeVertical(unittest.TestCase):
    def test_read_patch_test_finish_uses_production_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "src").mkdir()
            (repo / "src/value.py").write_text("VALUE = 1\n", encoding="utf-8")
            (repo / "test_value.py").write_text(
                "import unittest\nfrom src.value import VALUE\n\n"
                "class TestValue(unittest.TestCase):\n"
                "    def test_value(self):\n"
                "        self.assertEqual(VALUE, 2)\n\n"
                "if __name__ == '__main__':\n"
                "    unittest.main()\n",
                encoding="utf-8",
            )
            model = _RecordingLam()
            signer = OperatorSigner(b"lam-runtime-approval-key")
            result = Runtime.execute_harness(
                MANIFEST,
                TaskContext(
                    brief="Repair the value bug and verify the test suite.",
                    repo_path=repo,
                    run_id="lam-runtime-run",
                    episode_id="lam-runtime-episode",
                    principal="agent-1",
                    max_turns=6,
                ),
                model=model,
                approver=lambda challenge: signer.approve(challenge, reviewer="operator"),
                approval_key=signer.public_bytes,
                verifier=_Verifier(),
                sandbox_mode="host-dev",
            )

            self.assertIs(result.terminal, RunTermination.COMPLETED,
                          f"terminal={result.terminal} detail={result.detail} "
                          f"receipts={result.receipts} "
                          f"events={[ (event.kind, event.reason, event.payload) for event in result.events ]} "
                          f"contexts={model.contexts}")
            self.assertEqual((repo / "src/value.py").read_text(encoding="utf-8"), "VALUE = 2\n",
                             f"receipts={result.receipts} events={[(e.kind, e.reason, e.payload) for e in result.events]}")
            self.assertEqual([receipt.verb for receipt in result.receipts],
                             ["fs.read", "patch.apply", "proc.exec"])
            self.assertEqual(result.verdict.outcome, "claims")
            self.assertGreaterEqual(len(model.contexts), 4)
            l5 = [layer["content"] for layer in model.contexts[1]["layers"]
                  if layer["layer"] == "L5"]
            self.assertTrue(l5)
            self.assertIn("VALUE = 1", "\n".join(l5))


if __name__ == "__main__":
    unittest.main()
