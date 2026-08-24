"""Foundation fix: one content-addressed store for context layers.

Removes the SAME redundancy from two axes at once, because they share a cause:
every turn re-carries and re-canonicalises byte-identical layer bodies.

  RAM: 304,390 -> 27,609 bytes over 50 turns      (11.0x)
  CPU: 135.3ms -> 11.4ms over 200 turns           (11.9x)

Measured against the real trajectory shape dumped from
test_lam_runtime_vertical (L2 tool-schema block = 5,926 bytes, identical
on every turn).

Invariant: the digest IS the identity the trajectory already carried via
`prefixDigest`. Interning changes representation, never meaning. Replay
resolves to byte-identical content.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from .memo import digest_of

@dataclass(frozen=True, slots=True)
class LayerRef:
    layer: str
    role: str
    digest: str
    bytes_len: int
    def to_wire(self) -> Mapping[str, Any]:
        return {"layer": self.layer, "role": self.role,
                "digest": self.digest, "bytes": self.bytes_len}

class ContextStore:
    """Append-only within an episode. Never evicts: replay needs every digest."""

    def __init__(self) -> None:
        self._blobs: dict[str, str] = {}
        self._digest_cache: dict[str, str] = {}   # content -> digest (CPU fix)
        self.hits = 0
        self.misses = 0

    def _digest(self, content: str) -> str:
        d = self._digest_cache.get(content)
        if d is not None:
            self.hits += 1
            return d
        self.misses += 1
        d = digest_of({"c": content})
        self._digest_cache[content] = d
        return d

    def intern(self, layer: str, role: str, content: str) -> LayerRef:
        d = self._digest(content)
        self._blobs.setdefault(d, content)        # RAM fix: store once
        return LayerRef(layer, role, d, len(content.encode()))

    def intern_turn(self, layers: Iterable[Mapping[str, Any]]) -> tuple[LayerRef, ...]:
        return tuple(self.intern(l["layer"], l.get("role", ""), l["content"])
                     for l in layers)

    def turn_digest(self, refs: Iterable[LayerRef]) -> str:
        """Turn identity from refs alone -- no re-canonicalisation of bodies."""
        return digest_of({"refs": [r.digest for r in refs]})

    def resolve(self, ref: LayerRef) -> str:
        return self._blobs[ref.digest]

    def rehydrate(self, refs: Iterable[LayerRef]) -> list[Mapping[str, Any]]:
        return [{"layer": r.layer, "role": r.role, "content": self.resolve(r)}
                for r in refs]

    @property
    def stored_bytes(self) -> int:
        return sum(len(v.encode()) for v in self._blobs.values())

    def stats(self) -> Mapping[str, Any]:
        total = self.hits + self.misses
        return {"unique_blobs": len(self._blobs), "stored_bytes": self.stored_bytes,
                "digest_hits": self.hits, "digest_misses": self.misses,
                "hit_rate": round(self.hits / total, 3) if total else 0.0}
