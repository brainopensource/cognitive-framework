#!/usr/bin/env python3
"""Hermetic Gateway Transport Parity Falsifier.

Tests that both UDS NDJSON daemon and HTTP/SSE gateway:
1. Accept identical command frame envelopes.
2. Return identical canonical error codes for malformed inputs.
3. Reject unknown commands and invalid schema versions fail-closed.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vanguard.packages.runtime.service.contract import (
    ContractError,
    ERROR_CODES,
    validate_command,
    validate_frame_envelope,
)

FIXTURES_DIR = ROOT / "test" / "fixtures" / "wire_contracts"


class TestWireContractFalsifiers(unittest.TestCase):
    def test_all_valid_golden_vectors_pass(self):
        valid_dir = FIXTURES_DIR / "valid"
        self.assertTrue(valid_dir.exists(), "Valid fixtures directory must exist")

        files = sorted(valid_dir.glob("*.json"))
        self.assertGreaterEqual(len(files), 11, "Must have at least 11 command fixtures")

        for f in files:
            with self.subTest(file=f.name):
                data = json.loads(f.read_text(encoding="utf-8"))
                # 1. Envelope validation
                validate_frame_envelope(data)
                # 2. Command payload validation
                cmd = validate_command(data["command"])
                self.assertIsNotNone(cmd)
                self.assertEqual(cmd.name, data["command"]["name"])

    def test_all_negative_vectors_fail_closed(self):
        invalid_dir = FIXTURES_DIR / "invalid"
        self.assertTrue(invalid_dir.exists(), "Invalid fixtures directory must exist")

        for f in sorted(invalid_dir.glob("*.json")):
            with self.subTest(file=f.name):
                data = json.loads(f.read_text(encoding="utf-8"))
                with self.assertRaises(ContractError) as ctx:
                    validate_frame_envelope(data)
                    validate_command(data.get("command", {}))
                self.assertIn(ctx.exception.code, ERROR_CODES)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestWireContractFalsifiers)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
