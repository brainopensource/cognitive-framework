"""M-5 T0 witness memoisation. Narrows work; never widens authority."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from typing import Any, Mapping, Optional

def jcs(o: Any) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode()

def digest_of(o: Any) -> str:
    return "sha256:" + hashlib.sha256(jcs(o)).hexdigest()

# All seven bind the key. Omitting ANY one makes the memo unsound:
# it would let a witness computed under weaker assurance, an older
# toolchain, or a different checker satisfy a stronger obligation.
MEMO_FIELDS = ("obligation", "input_digests", "environment_digest",
               "checker_identity", "toolchain_version",
               "assurance_level", "policy_version")

@dataclass(frozen=True, slots=True)
class MemoEntry:
    witness_digest: str
    origin_run_id: str
    outcome: str

def memo_key(**kw: Any) -> str:
    missing = [f for f in MEMO_FIELDS if f not in kw]
    if missing:
        raise ValueError(f"memo key missing required field(s): {missing}")
    return digest_of({f: kw[f] for f in MEMO_FIELDS})

class WitnessMemo:
    """Content-addressed. Bounded. A hit is still re-verified downstream."""
    def __init__(self, capacity: int = 4096) -> None:
        self._d: dict[str, MemoEntry] = {}
        self._cap = capacity

    def get(self, key: str) -> Optional[MemoEntry]:
        return self._d.get(key)

    def put(self, key: str, e: MemoEntry) -> None:
        if len(self._d) >= self._cap:           # FIFO evict; bounded RAM
            self._d.pop(next(iter(self._d)))
        self._d[key] = e
