"""ADR-0100 memory authorization falsifiers 1--5."""
from __future__ import annotations

import hashlib
import hmac
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from vanguard.packages.adapters.stores.memory_engine import DurableMemoryPort
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.runtime.memory import (
    MemoryAccess,
    MemoryAuthorizationPort,
    MemoryResult,
    RetrievalProvenance,
    require_retrieval_provenance,
)


class M8MemoryFalsifiers(unittest.TestCase):
    key = b"m8-memory-authority-key"

    def grant(self, *, tenant="t1", project="p1", category="knowledge", expiry=None, epoch=1):
        grant = {
            "grantRef": "grant-1", "issuer": "authority", "subject": "agent-1",
            "tenant": tenant, "project": project, "actions": ["read", "write", "invalidate", "retain"],
            "purpose": "context", "expiresAt": expiry or (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "revocationEpoch": epoch, "selector": {"category": category},
        }
        signature = hmac.new(self.key, digest_of(grant).encode("ascii"), hashlib.sha256).hexdigest()
        return grant, signature

    def test_fake_nonempty_grant_fails_closed(self):
        self.assertFalse(MemoryAccess("x", {"category": "knowledge"}, "t1", "p1").permitted())

    def test_cross_tenant_project_and_category_are_denied(self):
        authority = MemoryAuthorizationPort(self.key)
        grant, sig = self.grant()
        with self.assertRaises(PermissionError):
            authority.verify(grant, sig, action="read", tenant="t2", project="p1", selector={"category": "knowledge"})
        with self.assertRaises(PermissionError):
            authority.verify(grant, sig, action="read", tenant="t1", project="p2", selector={"category": "knowledge"})
        with self.assertRaises(PermissionError):
            authority.verify(grant, sig, action="read", tenant="t1", project="p1", selector={"category": "skills"})

    def test_expired_and_revoked_grants_fail_at_use_time(self):
        expired, sig = self.grant(expiry=(datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat())
        with self.assertRaises(PermissionError):
            MemoryAuthorizationPort(self.key).verify(expired, sig, action="read", tenant="t1", project="p1", selector={"category": "knowledge"})
        grant, sig = self.grant()
        authority = MemoryAuthorizationPort(self.key, revoked_epochs={"grant-1": 1})
        with self.assertRaises(PermissionError):
            authority.verify(grant, sig, action="read", tenant="t1", project="p1", selector={"category": "knowledge"})

    def test_ranker_receives_only_authorized_candidates(self):
        seen = []
        def ranker(query, candidates):
            seen.extend(candidates)
            return candidates
        grant, sig = self.grant()
        access = MemoryAuthorizationPort(self.key).verify(grant, sig, action="write", tenant="t1", project="p1", selector={"category": "knowledge"})
        with tempfile.TemporaryDirectory() as tmp:
            store = DurableMemoryPort(Path(tmp), "knowledge", ranker=ranker)
            store.write({"text": "authorized"}, access)
            read = MemoryAuthorizationPort(self.key).verify(grant, sig, action="read", tenant="t1", project="p1", selector={"category": "knowledge"})
            store.recall("authorized", read)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0][0].split(":", 1)[0], "knowledge")

    def test_context_rejects_missing_or_mismatched_provenance(self):
        with self.assertRaises(PermissionError):
            require_retrieval_provenance(MemoryResult(("knowledge:1",), None))  # type: ignore[arg-type]
        provenance = RetrievalProvenance("sha256:q", "policy", (), (), (), None, None, False)
        with self.assertRaises(PermissionError):
            require_retrieval_provenance(MemoryResult(("knowledge:1",), provenance))


if __name__ == "__main__":
    unittest.main()
