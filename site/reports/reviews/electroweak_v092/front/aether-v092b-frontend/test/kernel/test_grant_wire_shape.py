"""TSK-SPEC-008 / S060-B-06: kernel grant payload is the wire shape.

Kernel grant = actions + resources + purposeDigest (X-07 code half).
REQ-TRUST-001.
"""

from __future__ import annotations

import unittest

from vanguard.packages.kernel.grants import Grant

from . import fakes


class GrantWireShape(unittest.TestCase):
    def test_payload_carries_actions_resources_and_purpose_digest(self) -> None:
        grant = Grant(
            grant_id="grant-1",
            principal="agent-1",
            descriptor_digest="sha256:" + "a" * 64,
            scope=fakes.child_scope(),
            expires_at="2026-08-18T00:00:00.000Z",
            purpose_digest="sha256:" + "b" * 64,
        )
        payload = grant.payload()
        for key in ("grantId", "descriptorDigest", "purposeDigest",
                    "actions", "resources"):
            self.assertIn(key, payload)
        self.assertIsInstance(payload["actions"], list)
        self.assertIsInstance(payload["resources"], list)
        self.assertTrue(payload["actions"])
