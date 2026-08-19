from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from layer0.events.blob import BlobStore, BlobWriteError
from layer0.events.store import MemoryLedger


class BlobOrderingTests(unittest.TestCase):
    def test_write_fsync_then_emit(self) -> None:
        ledger = MemoryLedger()
        order: list[str] = []

        def fsync(fd: int) -> None:
            order.append("fsync")
            os.fsync(fd)

        original_emit = ledger.emitter.emit_kind

        def tracked_emit(*args, **kwargs):  # type: ignore[no-untyped-def]
            order.append("emit")
            return original_emit(*args, **kwargs)

        ledger.emitter.emit_kind = tracked_emit  # type: ignore[method-assign]
        with tempfile.TemporaryDirectory() as tmp:
            store = BlobStore(Path(tmp), ledger.emitter, fsync=fsync)
            digest = store.write_blob(b"hello", run_id="r", principal="p")
        self.assertTrue(digest.startswith("sha256:"))
        self.assertEqual(order, ["fsync", "emit"])
        self.assertEqual(len(ledger.envelopes), 1)

    def test_failed_fsync_does_not_emit(self) -> None:
        ledger = MemoryLedger()

        def boom(_fd: int) -> None:
            raise OSError("disk full")

        with tempfile.TemporaryDirectory() as tmp:
            store = BlobStore(Path(tmp), ledger.emitter, fsync=boom)
            with self.assertRaises(BlobWriteError):
                store.write_blob(b"hello", run_id="r", principal="p")
        self.assertEqual(ledger.envelopes, ())
