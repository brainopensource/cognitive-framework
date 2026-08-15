"""Content digests over canonical bytes — Python reader.

Owning contract: VG-04 `CT-09` (`sha256:` plus 64 lowercase hex), `SC-2`
(every digest is computed over the RFC 8785 canonical form).
"""

from __future__ import annotations

import hashlib
from typing import Any

from .jcs import canonical_bytes

__all__ = ["digest_bytes", "digest_of"]


def digest_bytes(payload: bytes) -> str:
    """`sha256:<64 lowercase hex>` over raw bytes (`CT-09`)."""
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def digest_of(value: Any) -> str:
    """Digest of a JSON value over its canonical form — the only supported path."""
    return digest_bytes(canonical_bytes(value))
