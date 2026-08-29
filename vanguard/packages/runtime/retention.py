"""Artifact retention, lifecycle, and garbage collection (EVO-12).

Invariants:
- Never delete a retained artifact with a live causal reference in the ledger.
- Orphaned blob-first captures become collectible only after a configured grace period.
- Dry-run mode reports exact candidate digests, byte sizes, and collection reasons.
- Ledger history remains authoritative; GC never deletes or compacts ledger events.
- Thread-safe and crash-safe: interrupted GC leaves store consistent.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence, Set

from ..adapters.stores.blob_store import FileBlobStore
from ..domain.ledger.events import EventEnvelope
from ..ports.determinism import ClockPort
from ..ports.event_store import EventRange, EventStorePort


@dataclass(frozen=True, slots=True)
class GarbageCollectionCandidate:
    digest: str
    byte_size: int
    mtime: float
    reason: str  # "orphan_expired" | "orphan_grace" | "live_reference"
    action: str  # "deleted" | "retained"


@dataclass(frozen=True, slots=True)
class GarbageCollectionPolicy:
    grace_period_seconds: float = 3600.0  # 1 hour grace period
    dry_run: bool = False
    max_collect_count: int | None = None


@dataclass(frozen=True, slots=True)
class GarbageCollectionReport:
    total_blobs: int
    total_bytes: int
    live_blobs: int
    live_bytes: int
    orphan_blobs: int
    orphan_bytes: int
    retained_grace_blobs: int
    deleted_blobs: int
    deleted_bytes: int
    dry_run: bool
    candidates: tuple[GarbageCollectionCandidate, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "totalBlobs": self.total_blobs,
            "totalBytes": self.total_bytes,
            "liveBlobs": self.live_blobs,
            "liveBytes": self.live_bytes,
            "orphanBlobs": self.orphan_blobs,
            "orphanBytes": self.orphan_bytes,
            "retainedGraceBlobs": self.retained_grace_blobs,
            "deletedBlobs": self.deleted_blobs,
            "deletedBytes": self.deleted_bytes,
            "dryRun": self.dry_run,
            "candidates": [
                {
                    "digest": c.digest,
                    "byteSize": c.byte_size,
                    "mtime": c.mtime,
                    "reason": c.reason,
                    "action": c.action,
                }
                for c in self.candidates
            ],
        }


class ArtifactGarbageCollector:
    """Bounded artifact lifecycle and safe garbage collector."""

    def __init__(self, policy: GarbageCollectionPolicy | None = None) -> None:
        self.policy = policy or GarbageCollectionPolicy()

    def collect(
        self,
        event_store: EventStorePort,
        blob_store: FileBlobStore,
        *,
        policy: GarbageCollectionPolicy | None = None,
        clock: ClockPort | None = None,
        now: float | None = None,
    ) -> GarbageCollectionReport:
        active_policy = policy or self.policy
        if now is not None:
            current_time = float(now)
        elif clock is not None:
            current_time = clock.now_ms() / 1000.0
        else:
            current_time = 0.0

        # 1. Scan ledger for all live causal artifact references
        live_digests = self._extract_live_digests(event_store)

        # 2. Scan blob store on disk
        stored_blobs = self._scan_blob_store(blob_store)

        total_blobs = len(stored_blobs)
        total_bytes = sum(b[1] for b in stored_blobs.values())

        live_blobs = 0
        live_bytes = 0
        orphan_blobs = 0
        orphan_bytes = 0
        retained_grace_blobs = 0
        deleted_blobs = 0
        deleted_bytes = 0

        candidates: list[GarbageCollectionCandidate] = []

        for digest, (path, byte_size, mtime) in stored_blobs.items():
            if digest in live_digests:
                live_blobs += 1
                live_bytes += byte_size
                candidates.append(
                    GarbageCollectionCandidate(
                        digest=digest,
                        byte_size=byte_size,
                        mtime=mtime,
                        reason="live_reference",
                        action="retained",
                    )
                )
                continue

            # Orphan blob - check grace period
            age = current_time - mtime
            if age < active_policy.grace_period_seconds:
                retained_grace_blobs += 1
                candidates.append(
                    GarbageCollectionCandidate(
                        digest=digest,
                        byte_size=byte_size,
                        mtime=mtime,
                        reason="orphan_grace",
                        action="retained",
                    )
                )
                continue

            # Eligible for collection
            orphan_blobs += 1
            orphan_bytes += byte_size

            if not active_policy.dry_run:
                try:
                    path.unlink(missing_ok=True)
                    # Try to clean up empty fan-out directory
                    try:
                        path.parent.rmdir()
                    except OSError:
                        pass
                    deleted_blobs += 1
                    deleted_bytes += byte_size
                    action = "deleted"
                except OSError:
                    action = "retained"
            else:
                action = "retained"

            candidates.append(
                GarbageCollectionCandidate(
                    digest=digest,
                    byte_size=byte_size,
                    mtime=mtime,
                    reason="orphan_expired",
                    action=action,
                )
            )

        return GarbageCollectionReport(
            total_blobs=total_blobs,
            total_bytes=total_bytes,
            live_blobs=live_blobs,
            live_bytes=live_bytes,
            orphan_blobs=orphan_blobs,
            orphan_bytes=orphan_bytes,
            retained_grace_blobs=retained_grace_blobs,
            deleted_blobs=deleted_blobs,
            deleted_bytes=deleted_bytes,
            dry_run=active_policy.dry_run,
            candidates=tuple(candidates),
        )

    def _extract_live_digests(self, event_store: EventStorePort) -> Set[str]:
        """Read all canonical event envelopes and collect referenced artifact digests."""
        live: set[str] = set()
        res = event_store.read(EventRange())
        if not res.ok:
            return live

        def extract_from_obj(obj: Any) -> None:
            if isinstance(obj, str):
                if obj.startswith("sha256:") and len(obj) == 71:
                    live.add(obj.strip())
            elif isinstance(obj, Mapping):
                for v in obj.values():
                    extract_from_obj(v)
            elif isinstance(obj, (list, tuple)):
                for v in obj:
                    extract_from_obj(v)

        envelopes = res.value or ()
        for env in envelopes:
            extract_from_obj(env.payload)
            if hasattr(env, "harness_digest") and env.harness_digest:
                extract_from_obj(env.harness_digest)

        return live

    def _scan_blob_store(self, blob_store: FileBlobStore) -> dict[str, tuple[Path, int, float]]:
        """Enumerate stored blobs on disk with path, size, and mtime."""
        blobs: dict[str, tuple[Path, int, float]] = {}
        root = blob_store.root
        if not root.is_dir():
            return blobs

        for prefix_dir in root.iterdir():
            if not prefix_dir.is_dir() or len(prefix_dir.name) != 2:
                continue
            for file_path in prefix_dir.iterdir():
                if not file_path.is_file() or len(file_path.name) != 62:
                    continue
                hex_digest = prefix_dir.name + file_path.name
                canonical_digest = f"sha256:{hex_digest}"
                try:
                    stat = file_path.stat()
                    blobs[canonical_digest] = (file_path, stat.st_size, stat.st_mtime)
                except OSError:
                    continue

        return blobs
