"""Blob durability: write → fsync → emit(digest). Closing D-19."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

from layer0.spi.types_gen import EventKind
from .canonical import digest_bytes
from .emitter import LedgerEmitter

__all__ = ["BlobStore", "BlobWriteError"]


class BlobWriteError(RuntimeError):
    """Raised when the blob is not durably on disk; no ledger event is emitted."""


class BlobStore:
    def __init__(self, root: Path, emitter: LedgerEmitter, *, fsync: Callable[[int], None] | None = None) -> None:
        self._root = root
        self._emitter = emitter
        self._fsync = fsync or os.fsync

    def write_blob(
        self,
        data: bytes,
        *,
        run_id: str,
        principal: str,
    ) -> str:
        digest = digest_bytes(data)
        hex_name = digest.split(":", 1)[1]
        path = self._root / hex_name
        self._root.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
        try:
            os.write(fd, data)
            self._fsync(fd)
        except Exception as exc:
            raise BlobWriteError(str(exc)) from exc
        finally:
            os.close(fd)
        self._emitter.emit_kind(
            EventKind.CHECKPOINT_CREATED,
            run_id=run_id,
            principal=principal,
            payload={"blob_digest": digest},
            idempotency_key=digest,
        )
        return digest
