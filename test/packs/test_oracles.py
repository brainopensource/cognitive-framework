"""Preregistered oracles, signed verdicts, anti-cheat (planner cannot self-grade)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"


class OracleSuiteTests(unittest.TestCase):
    def test_registry_is_preregistered_not_run(self) -> None:
        registry = json.loads((PACK / "oracles" / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["status"], "preregistered-not-run")
        self.assertTrue(registry["oracles"])

    def test_unsigned_verdicts_cannot_pass_the_gate(self) -> None:
        import sys
        sys.path.insert(0, str(PACK / "oracles"))
        from gate import PackOracleGate
        from layer0.spi.types_gen import GateDecision, SignedVerdict

        gate = PackOracleGate()
        decision = gate.gate((SignedVerdict(verdict="pass", signature="unsigned"),))
        self.assertEqual(decision, GateDecision.ABANDON)

    def test_signed_pass_is_accepted(self) -> None:
        import sys
        sys.path.insert(0, str(PACK / "oracles"))
        from gate import PackOracleGate, sign_verdict
        from layer0.spi.result import Ok
        from layer0.spi.types_gen import GateDecision, OracleSpec, SignedVerdict

        private = Ed25519PrivateKey.generate()
        priv_bytes = private.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_bytes = private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        signature = sign_verdict({"outcome": "pass"}, priv_bytes)
        gate = PackOracleGate(public_key=pub_bytes)
        self.assertEqual(
            gate.gate((SignedVerdict(verdict="pass", signature=signature),)),
            GateDecision.PASS,
        )
        self.assertIsInstance(gate.preregister(OracleSpec(id="coding-oracle@3")), Ok)


if __name__ == "__main__":
    unittest.main()
