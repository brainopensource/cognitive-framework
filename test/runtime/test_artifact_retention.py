from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.blob_store import FileBlobStore
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter
from vanguard.packages.runtime.retention import (
    ArtifactGarbageCollector,
    GarbageCollectionPolicy,
)


class TestArtifactRetention(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.blob_store = FileBlobStore(self.root / "blobs")
        self.event_store = SqliteEventStore(self.root / "events.sqlite3")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_live_referenced_artifact_is_never_deleted(self) -> None:
        content = b"critical test artifact"
        digest = self.blob_store.put(content).value

        # Record event in event store referencing this artifact
        emitter = LedgerEmitter(
            self.event_store,
            episode_id="ep-1",
            project_id="p-1",
            principal_id="actor-1",
            harness_digest="sha256:0000",
        )
        emitter.registry().emit_kind(
            "PluginDiscovered",
            run_id="run-1",
            principal="actor-1",
            payload={"manifest_digest": digest},
        )

        # Run GC with 0 grace period far in the future
        gc = ArtifactGarbageCollector()
        now = time.time() + 100000.0
        report = gc.collect(
            self.event_store,
            self.blob_store,
            policy=GarbageCollectionPolicy(grace_period_seconds=0),
            now=now,
        )

        self.assertEqual(report.total_blobs, 1)
        self.assertEqual(report.live_blobs, 1)
        self.assertEqual(report.deleted_blobs, 0)
        self.assertTrue(self.blob_store.has(digest))

    def test_orphan_within_grace_period_is_retained(self) -> None:
        content = b"temporary in-flight blob"
        digest = self.blob_store.put(content).value

        # Run GC with 1 hour grace period at current time
        gc = ArtifactGarbageCollector()
        report = gc.collect(
            self.event_store,
            self.blob_store,
            policy=GarbageCollectionPolicy(grace_period_seconds=3600.0),
        )

        self.assertEqual(report.total_blobs, 1)
        self.assertEqual(report.live_blobs, 0)
        self.assertEqual(report.retained_grace_blobs, 1)
        self.assertEqual(report.deleted_blobs, 0)
        self.assertTrue(self.blob_store.has(digest))

    def test_orphan_past_grace_period_is_deleted(self) -> None:
        content = b"abandoned orphan blob"
        digest = self.blob_store.put(content).value

        # Run GC simulating time after grace period expired
        gc = ArtifactGarbageCollector()
        now = time.time() + 7200.0  # 2 hours later
        report = gc.collect(
            self.event_store,
            self.blob_store,
            policy=GarbageCollectionPolicy(grace_period_seconds=3600.0),
            now=now,
        )

        self.assertEqual(report.total_blobs, 1)
        self.assertEqual(report.live_blobs, 0)
        self.assertEqual(report.deleted_blobs, 1)
        self.assertFalse(self.blob_store.has(digest))

    def test_dry_run_mode_does_not_delete(self) -> None:
        content = b"dry run candidate"
        digest = self.blob_store.put(content).value

        gc = ArtifactGarbageCollector()
        now = time.time() + 7200.0
        report = gc.collect(
            self.event_store,
            self.blob_store,
            policy=GarbageCollectionPolicy(grace_period_seconds=3600.0, dry_run=True),
            now=now,
        )

        self.assertEqual(report.total_blobs, 1)
        self.assertEqual(report.deleted_blobs, 0)
        self.assertEqual(report.orphan_blobs, 1)
        self.assertTrue(self.blob_store.has(digest))
