"""Lane A M-8 durability and lifecycle coverage."""

from __future__ import annotations

import hashlib
import hmac
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from vanguard.packages.adapters.stores.memory_engine import DurableMemoryPort
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.ports.memory import MemoryAuthorizationPort


class DurableMemoryPortTests(unittest.TestCase):
    key = b"durable-memory-test-key"
    now = datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc)

    def access(self, *, category: str = "knowledge", actions: list[str] | None = None,
               action: str = "read"):
        grant = {
            "grantRef": "grant-durable",
            "issuer": "authority",
            "subject": "agent",
            "tenant": "tenant-a",
            "project": "project-a",
            "actions": actions or ["read", "write", "invalidate", "retain"],
            "purpose": "test",
            "expiresAt": "2026-08-28T12:00:00Z",
            "revocationEpoch": 1,
            "selector": {"category": category},
        }
        signature = hmac.new(self.key, digest_of(grant).encode("ascii"), hashlib.sha256).hexdigest()
        return MemoryAuthorizationPort(self.key).verify(
            grant, signature, action=action, tenant="tenant-a", project="project-a",
            selector={"category": category}, now=self.now,
        )

    def test_restart_recovery_and_deterministic_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "store"
            read = self.access()
            write = self.access(actions=["read", "write", "invalidate", "retain"])
            port = DurableMemoryPort(root, "knowledge", clock=lambda: "2026-08-27T12:00:00Z")
            record_id = port.write({"text": "Durable causal memory fact", "source": "fixture"}, write)
            result = port.recall("causal memory", read)
            self.assertEqual(result.record_ids, (record_id,))
            self.assertIn("tokenizer=unicode-word/1", result.provenance.policy_identity)
            port.close()

            reopened = DurableMemoryPort(root, "knowledge", clock=lambda: "2026-08-27T12:00:00Z")
            self.assertEqual(reopened.recall("causal memory", read).record_ids, (record_id,))
            reopened._db.execute("DELETE FROM memory_terms")
            self.assertEqual(reopened.rebuild_index(), 1)
            self.assertEqual(reopened.recall("causal memory", read).record_ids, (record_id,))
            fact = reopened._db.execute("SELECT fact_kind FROM memory_facts WHERE record_id=?", (record_id,)).fetchone()
            self.assertEqual(fact[0], "ClaimRecorded")
            reopened.close()

    def test_causal_notification_failure_quarantines_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "store"

            def broken(_: object) -> None:
                raise RuntimeError("canonical writer unavailable")

            port = DurableMemoryPort(root, "knowledge", fact_emitter=broken,
                                     clock=lambda: "2026-08-27T12:00:00Z")
            with self.assertRaises(IOError):
                port.write({"text": "must be quarantined"}, self.access(actions=["write"], action="write"))
            self.assertEqual(port.recall("must", self.access()).record_ids, ())
            quarantined = port._db.execute(
                "SELECT quarantined FROM memory_records"
            ).fetchone()[0]
            self.assertEqual(quarantined, 1)
            port.close()

    def test_legal_hold_and_quarantine_interval_protect_gc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            port = DurableMemoryPort(Path(tmp), "knowledge", quarantine_seconds=60,
                                     clock=lambda: "2026-08-27T12:00:00Z")
            access = self.access(actions=["read", "write", "invalidate", "retain"])
            held = port.write({"text": "held fact"}, access)
            disposable = port.write({"text": "disposable fact"}, access)
            port.set_legal_hold(held, access)
            port.invalidate(held, access)
            port.invalidate(disposable, access)
            self.assertEqual(port.gc(access, dry_run=True), 1)
            self.assertEqual(port.gc(access, now="2026-08-27T12:00:30Z"), 1)
            self.assertIsNotNone(port._db.execute(
                "SELECT record_id FROM memory_records WHERE record_id=?", (held,)).fetchone())
            self.assertEqual(port.gc(access, now="2026-08-27T12:02:00Z"), 0)
            port.close()

    def test_backup_restore_verifies_checksum_and_survives_new_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "base"
            backup = Path(tmp) / "backup"
            restored = Path(tmp) / "restored"
            access = self.access(actions=["read", "write", "invalidate", "retain"])
            port = DurableMemoryPort(base, "knowledge", clock=lambda: "2026-08-27T12:00:00Z")
            port.write({"text": "backup survives restart"}, access)
            port.backup(backup)
            manifest = json.loads((backup / "backup.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schemaVersion"], 2)
            port.close()
            restored_port = DurableMemoryPort.restore_backup(backup, restored, "knowledge")
            self.assertEqual(restored_port.recall("survives", self.access()).texts,
                             ("backup survives restart",))
            restored_port.close()


if __name__ == "__main__":
    unittest.main()
