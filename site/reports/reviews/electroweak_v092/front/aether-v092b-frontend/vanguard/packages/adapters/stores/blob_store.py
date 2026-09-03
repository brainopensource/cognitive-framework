"""Blob stores: in-memory and on-disk (`S10-A-03`, `T10.2`).

Two implementations per port, because one implementation is an interface
nobody has tested against anything (`T10.2`). The fake is enough to compose
against; the real one is a content-addressed directory.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from ...ports.event_store import Result

__all__ = ["FileBlobStore", "InMemoryBlobStore"]


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


class InMemoryBlobStore:
    """The fake. Enough for compose tests; nothing survives the process."""

    def __init__(self) -> None:
        self._blobs: dict[str, bytes] = {}

    def put(self, data: bytes) -> Result[str]:
        if not isinstance(data, (bytes, bytearray)):
            return Result.fail("invalid_request", "blob data must be bytes")
        digest = _digest(bytes(data))
        self._blobs[digest] = bytes(data)
        return Result.success(digest)

    def get(self, digest: str) -> Result[bytes]:
        if digest not in self._blobs:
            return Result.fail("not_found", f"no blob for {digest}")
        return Result.success(self._blobs[digest])

    def has(self, digest: str) -> bool:
        return digest in self._blobs


class FileBlobStore:
    """The real one. A content-addressed directory.

    Writes are digest-named, so a re-put of identical bytes is a no-op rather
    than a second copy. Naming alone does *not* make a torn write safe,
    though: `write_bytes` straight to the final path can leave a truncated
    file sitting at the name of the complete one, and `has()` would then
    report a blob whose bytes do not hash to its own address. So the write
    goes to a temporary neighbour, is fsynced, and is then `os.replace`d into
    place -- atomic within a directory -- and the directory itself is fsynced
    so the rename survives too. `layer0/events/blob.py` guarded this with
    fsync-before-emit; the emit half died with the single-writer rule
    (ADR-0076 §6 -- a blob store is not a ledger writer), the durability half
    is kept here (2.2-A).
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, digest: str) -> Path | None:
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            return None
        hexed = digest[len("sha256:"):]
        if len(hexed) != 64 or not all(c in "0123456789abcdef" for c in hexed):
            return None
        # Two-level fan-out: a flat directory of a million entries is a
        # directory nobody can list.
        return self.root / hexed[:2] / hexed[2:]

    def put(self, data: bytes) -> Result[str]:
        if not isinstance(data, (bytes, bytearray)):
            return Result.fail("invalid_request", "blob data must be bytes")
        payload = bytes(data)
        digest = _digest(payload)
        target = self._path(digest)
        if target is None:
            return Result.fail("instrument_error", "computed an unusable digest")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            try:
                self._atomic_write(target, payload)
            except OSError as exc:
                return Result.fail("instrument_error", f"blob write failed: {exc}")
        return Result.success(digest)

    @staticmethod
    def _atomic_write(target: Path, payload: bytes) -> None:
        """Durable, all-or-nothing. A failure here leaves no file at `target`."""
        tmp = target.with_name(target.name + ".partial")
        try:
            with open(tmp, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, target)
        except OSError:
            tmp.unlink(missing_ok=True)
            raise
        directory = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        except OSError:
            # A filesystem that refuses to fsync a directory (some network and
            # overlay mounts) has still completed the rename; the blob is
            # readable now and the durability window is the mount's problem,
            # not a reason to report a write that succeeded as failed.
            pass
        finally:
            os.close(directory)

    def get(self, digest: str) -> Result[bytes]:
        target = self._path(digest)
        if target is None:
            return Result.fail("invalid_request", f"malformed digest: {digest!r}")
        if not target.is_file():
            return Result.fail("not_found", f"no blob for {digest}")
        return Result.success(target.read_bytes())

    def has(self, digest: str) -> bool:
        target = self._path(digest)
        return target is not None and target.is_file()
