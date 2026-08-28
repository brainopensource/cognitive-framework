"""Order 9 evidence portability and observation-bound producer checks."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.runners.build_evidence_bundle import build_m6
from tools.linters.verify_evidence import _bytes_at_evidence
from vanguard.packages.runtime.governance.approvals import (
    ApprovalAuthority,
    ApprovalChallenge,
    OperatorSigner,
)


ROOT = Path(__file__).resolve().parents[2]


class Order9EvidenceProducerTests(unittest.TestCase):
    def test_m6_refuses_caller_supplied_legacy_counters(self) -> None:
        with self.assertRaises(ValueError):
            build_m6("dev-a", {"run": 57, "failures": 0})

    def test_m6_binds_observed_report_and_runtime_surface(self) -> None:
        report = {
            "schema": "aether.m6-falsifier-report/1",
            "command": ["python3", "-m", "unittest"],
            "returncode": 0,
            "tests": 57,
            "failures": 0,
            "fresh_process": True,
            "depth_3": True,
            "kill_tree": True,
        }
        with tempfile.TemporaryDirectory() as directory:
            evidence_root = Path(directory)
            envelope = build_m6(
                "dev-a", report, subject_root=ROOT, evidence_root=evidence_root)
            names = {material.name for material in envelope.materials}
            self.assertTrue({"runtime", "pack", "configuration", "workload"} <= names)
            report_material = next(
                material for material in envelope.materials
                if material.name == "workload")
            self.assertTrue(report_material.ref.startswith("artifacts/"))
        self.assertEqual(envelope.pins["runtimeDigest"], next(
                material.digest for material in envelope.materials
                if material.name == "runtime"))

    def test_rf95_run_signer_matches_raw_public_key_authority(self) -> None:
        """The profiled runner's ephemeral signer must be verifiable by bytes."""
        signer = OperatorSigner(b"rf95-approval-regression")
        challenge = ApprovalChallenge(
            approval_id="approval-1",
            process_id="episode-1",
            action="patch.apply",
            normalized_diff="--- a/src/calc.py\n+++ b/src/calc.py\n",
            args_digest="sha256:" + "a" * 64,
            descriptor_digest="sha256:" + "b" * 64,
            principal="operator",
            expires_at="2099-12-31T23:59:59.000Z",
        )
        decision = signer.approve(challenge, reviewer="operator")
        self.assertTrue(ApprovalAuthority(signer.public_bytes).verify(decision))

    def test_evidence_local_resolver_is_fenced_to_the_declared_artifact_root(self) -> None:
        """Bundle-local bytes satisfy run outputs only, never source materials.

        Lane B narrowed this resolver in Order 10: an unfenced version would
        let a file dropped beside the bundle stand in for a runtime module or
        schema the pinned commit never contained.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle.json"
            bundle.write_text("{}", encoding="utf-8")
            artifacts = root / "artifacts" / "M-6"
            artifacts.mkdir(parents=True)
            (artifacts / "inside.bin").write_bytes(b"inside")
            (root / "beside.bin").write_bytes(b"beside")
            fence = "artifacts/M-6"
            self.assertEqual(
                _bytes_at_evidence(bundle, "artifacts/M-6/inside.bin", fence), b"inside")
            self.assertIsNone(_bytes_at_evidence(bundle, "beside.bin", fence))
            self.assertIsNone(_bytes_at_evidence(bundle, "artifacts/M-6/inside.bin", ""))
            self.assertIsNone(_bytes_at_evidence(bundle, "../outside.bin", fence))
            self.assertIsNone(
                _bytes_at_evidence(bundle, str(artifacts / "inside.bin"), fence))


if __name__ == "__main__":
    unittest.main()
