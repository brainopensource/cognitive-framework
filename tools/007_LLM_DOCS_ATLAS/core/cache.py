"""Multi-Tier Caching Engine for LDA.

Implements a 3-tier cache hierarchy:
1. Index Cache: File content SHA-256 delta tracking.
2. Packet Cache: Budgeted ContextPacket instances keyed by (task, budget, strategy, git_head_sha).
3. Session Cache: In-memory multi-turn agent working memory with zero-overhead invalidation.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class FileCache:
    """Persistent on-disk cache stored under .lda/cache/."""

    def __init__(self, directory: Path) -> None:
        self.directory = Path(directory)

    def key(self, *parts: object) -> str:
        return hashlib.sha256("\0".join(map(str, parts)).encode("utf-8")).hexdigest()

    def read(self, key: str) -> Any | None:
        path = self.directory / f"{key}.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None

    def write(self, key: str, value: Any) -> None:
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            (self.directory / f"{key}.json").write_text(
                json.dumps(value, sort_keys=True), encoding="utf-8"
            )
        except OSError as e:
            logger.warning("Failed to write to FileCache: %s", e)


class PacketCache:
    """Speculative ContextPacket cache keyed strictly to git_head_sha."""

    def __init__(self, cache_dir: Path) -> None:
        self.disk_cache = FileCache(cache_dir / "packets")
        self._memory_cache: Dict[str, Tuple[str, Any]] = {}  # key -> (head_sha, packet_dict)

    def _compute_key(
        self,
        task: str,
        budget: int,
        strategy: str,
        include_skeletons: bool,
        head_sha: Optional[str],
    ) -> str:
        return self.disk_cache.key(
            task.strip().lower(),
            str(budget),
            strategy,
            str(include_skeletons),
            head_sha or "NO_HEAD",
        )

    def get(
        self,
        task: str,
        budget: int,
        strategy: str,
        include_skeletons: bool,
        head_sha: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached packet if git HEAD matches strictly."""
        cache_key = self._compute_key(task, budget, strategy, include_skeletons, head_sha)

        # 1. Check in-memory session cache
        if cache_key in self._memory_cache:
            cached_sha, packet = self._memory_cache[cache_key]
            if cached_sha == (head_sha or "NO_HEAD"):
                return packet

        # 2. Check disk cache
        packet = self.disk_cache.read(cache_key)
        if packet and isinstance(packet, dict):
            prov = packet.get("provenance", {})
            if prov.get("source_head_sha") == head_sha:
                self._memory_cache[cache_key] = (head_sha or "NO_HEAD", packet)
                return packet

        return None

    def put(
        self,
        task: str,
        budget: int,
        strategy: str,
        include_skeletons: bool,
        head_sha: Optional[str],
        packet_dict: Dict[str, Any],
    ) -> None:
        """Store packet in memory and disk cache."""
        cache_key = self._compute_key(task, budget, strategy, include_skeletons, head_sha)
        self._memory_cache[cache_key] = (head_sha or "NO_HEAD", packet_dict)
        self.disk_cache.write(cache_key, packet_dict)

    def clear(self) -> None:
        """Clear memory cache."""
        self._memory_cache.clear()
