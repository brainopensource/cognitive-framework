"""Order 9 evidence portability and observation-bound producer checks."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.runners.build_evidence_bundle import build_m6
from tools.linters.verify_evidence import _bytes_at_evidence


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

    def test_evidence_local_resolver_rejects_escape_and_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle.json"
            bundle.write_text("{}", encoding="utf-8")
            (root / "inside.bin").write_bytes(b"inside")
            self.assertEqual(_bytes_at_evidence(bundle, "inside.bin"), b"inside")
            self.assertIsNone(_bytes_at_evidence(bundle, "../outside.bin"))
            self.assertIsNone(_bytes_at_evidence(bundle, str(root / "inside.bin")))


if __name__ == "__main__":
    unittest.main()
