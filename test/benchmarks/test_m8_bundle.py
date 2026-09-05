"""FIN-A1 falsifiers for truthful dry-run and producer-signed evidence."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from benchmarks.m8_heldout.bundle_signer import CredentialLeakError, bundle_digest, sign_bundle, verify_bundle
from benchmarks.m8_heldout.canary import preflight_check
from benchmarks.m8_heldout.receipts import PromotionReceipt, RollbackReceipt
from benchmarks.protocols import write_b20_report


class TestM8Bundle(unittest.TestCase):
    def _bundle(self) -> dict[str, object]:
        return {"schema": "aether.m8-evidence-bundle/1", "run_id": "run-1", "subject_sha": "sha256:subject",
                "canary_manifest_digest": "sha256:canary", "records": [{"task_id": "t1", "disposition": "NOT_RUN"}],
                "aggregate_lift": None, "timestamp": "2026-08-31T00:00:00Z", "signer_id": "test-signer"}

    def test_dry_run_has_no_empirical_values(self) -> None:
        result = subprocess.run([sys.executable, "benchmarks/m8_heldout/runner.py", "--dry-run"], capture_output=True, text=True, check=True)
        bundle = json.loads(result.stdout)
        self.assertTrue(bundle["records"])
        self.assertEqual({row["disposition"] for row in bundle["records"]}, {"NOT_RUN"})
        for key in ("success", "lift", "regression", "cost", "tokens", "latency"):
            self.assertIsNone(bundle["empirical"][key])

    def test_b20_dry_run_has_null_pass_cost_oracle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "benchmark_20_results.json"
            report = write_b20_report(
                path,
                subject_sha="86142175fcab03ff93727ad1f5b336b22e01c66b",
                dry_run=True,
                task_ids=("01_rate_limiter_lease_recovery",),
            )
            self.assertIsNone(report["pass"])
            self.assertIsNone(report["cost"])
            self.assertIsNone(report["oracle"])
            self.assertIsNone(report["oracle_passed"])
            on_disk = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsNone(on_disk["pass"])
            self.assertIsNone(on_disk["cost"])
            self.assertIsNone(on_disk["oracle"])
            self.assertIsNone(on_disk["oracle_passed"])
            self.assertIsNone(on_disk["results"][0]["status"])
            self.assertIsNone(on_disk["results"][0]["cost_usd"])
            self.assertIsNone(on_disk["results"][0]["oracle_passed"])

        runner = subprocess.run(
            [sys.executable, "benchmarks/benchmark_20_suite/runner.py", "--dry-run"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(runner.returncode, 0, runner.stderr)
        emitted = json.loads(runner.stdout)
        self.assertIsNone(emitted["pass"])
        self.assertIsNone(emitted["cost"])
        self.assertIsNone(emitted["oracle"])
        self.assertIsNone(emitted["oracle_passed"])

    def test_signature_is_deterministic_and_verifies(self) -> None:
        bundle = self._bundle()
        private = Ed25519PrivateKey.generate()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key_path = root / "key.pem"
            key_path.write_bytes(private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
            first = sign_bundle(bundle, key_path, root / "one")
            second = sign_bundle(bundle, key_path, root / "two")
            self.assertEqual(first[1].read_bytes(), second[1].read_bytes())
            sealed = json.loads(first[0].read_text())
            self.assertEqual(sealed["bundle_digest"], bundle_digest(bundle))
            self.assertTrue(verify_bundle(sealed, first[1], private.public_key()))

    def test_tampered_bundle_fails(self) -> None:
        bundle = self._bundle()
        private = Ed25519PrivateKey.generate()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            key = root / "key.pem"
            key.write_bytes(private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
            bundle_path, sig_path = sign_bundle(bundle, key, root / "sealed")
            tampered = json.loads(bundle_path.read_text())
            tampered["run_id"] = "foreign"
            self.assertFalse(verify_bundle(tampered, sig_path, private.public_key()))

    def test_receipts_and_schema_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            PromotionReceipt("r", "s", 0.049, 0.5, 0.5)
        rollback = RollbackReceipt("r", "s", "undetermined")
        self.assertEqual(rollback.to_dict()["result"], "NEGATIVE")
        self.assertNotIn("amend", rollback.to_dict())
        with self.assertRaises(ValueError):
            bundle_digest({"run_id": "only"})

    def test_credentials_are_rejected(self) -> None:
        bundle = self._bundle()
        bundle["signer_id"] = "OPENROUTER_" + "API_KEY=" + "sk-" + ("x" * 20)
        with self.assertRaises(CredentialLeakError):
            bundle_digest(bundle)

    def test_canary_preflight_is_structured(self) -> None:
        result = preflight_check()
        self.assertTrue(result.ok, result.failures)


if __name__ == "__main__":
    unittest.main()
