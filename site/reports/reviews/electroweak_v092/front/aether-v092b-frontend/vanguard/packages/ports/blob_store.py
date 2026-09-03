"""Content-addressed blob storage (`S10-A-03`, `T10.2`).

Owning contract: `VG-03 §7`, `ICD §4`.

Every artifact the system reasons about is referenced by digest, not by path
(`CT-53`: no mutable field inside a content-addressed artifact). Until now
there was nowhere for those bytes to live, which is why `O-02` had nowhere to
land: a memory or retrieval feature needs somewhere to put what it remembers
before it can be about anything.

The port is deliberately small. A store that can `put`, `get` and answer `has`
is enough to hold evidence; anything richer belongs to whoever reads it.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .event_store import Result

__all__ = ["BlobStorePort"]


@runtime_checkable
class BlobStorePort(Protocol):
    """Bytes addressed by their own digest.

    The digest is computed by the store, never supplied by the caller: a store
    that trusts a caller's digest is a store whose addresses can lie.
    """

    def put(self, data: bytes) -> Result[str]:
        """Store `data`. Returns its `sha256:` digest."""

    def get(self, digest: str) -> Result[bytes]:
        """Return the bytes for `digest`, or a typed failure when absent."""

    def has(self, digest: str) -> bool:
        """True when `digest` is present. Never raises."""
