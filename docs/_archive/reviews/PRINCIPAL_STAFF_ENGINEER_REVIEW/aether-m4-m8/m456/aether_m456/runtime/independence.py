"""M-7 Deliverable B: independence analysis over the manifest selector algebra.

Concurrency is only safe where effects are genuinely independent. This derives
independence from selectors already declared in the packs -- NOT from intuition
and NOT from observed behaviour, which would be circular.

    independent(a, b) <=>  selector_disjoint(a, b)
                       AND not (privileged(a) and privileged(b))
                       AND no shared idempotency key

The output that matters is the INDEPENDENT FRACTION. If it is small, M-7 is not
worth building, and that is a valid and valuable result -- it saves the project
a scheduler, a leasing protocol, and a concurrency recovery surface.
"""
from __future__ import annotations
import posixpath
from dataclasses import dataclass
from itertools import combinations
from typing import Any, Iterable, Mapping, Sequence

@dataclass(frozen=True, slots=True)
class EffectRef:
    verb: str
    sink: str                      # observation | privileged
    selector: Mapping[str, Any]
    idempotency_key: str | None = None

def _norm(p: str) -> str:
    return posixpath.normpath(p).rstrip("/") or "/"

def _path_overlap(a: str, b: str) -> bool:
    a, b = _norm(a), _norm(b)
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")

def selector_disjoint(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    """Conservative: unknown selector kinds are treated as OVERLAPPING.

    Fail-closed matters here. Wrongly calling two effects disjoint admits a
    concurrent write race; wrongly calling them overlapping only costs speed.
    """
    if a.get("kind") != b.get("kind"):
        return True                                  # different resource domains
    kind = a.get("kind")
    if kind == "fs":
        pa = a.get("paths") or [a.get("root", "/")]
        pb = b.get("paths") or [b.get("root", "/")]
        return not any(_path_overlap(x, y) for x in pa for y in pb)
    if kind == "network":
        ha, hb = a.get("hosts", ["*"]), b.get("hosts", ["*"])
        if "*" in ha or "*" in hb: return False
        return not (set(ha) & set(hb))
    if kind == "formal":
        pa = a.get("paths") or [a.get("root", "/")]
        pb = b.get("paths") or [b.get("root", "/")]
        return not any(_path_overlap(x, y) for x in pa for y in pb)
    return False                                     # unknown kind -> assume overlap

def independent(a: EffectRef, b: EffectRef) -> bool:
    if a.idempotency_key and a.idempotency_key == b.idempotency_key:
        return False
    if a.sink == "privileged" and b.sink == "privileged":
        return False                                 # two writers never race
    return selector_disjoint(a.selector, b.selector)

@dataclass(frozen=True, slots=True)
class IndependenceReport:
    total_pairs: int
    independent_pairs: int
    blocked_by_sink: int
    blocked_by_selector: int
    blocked_by_idempotency: int

    @property
    def fraction(self) -> float:
        return self.independent_pairs / self.total_pairs if self.total_pairs else 0.0

    def verdict(self, threshold: float = 0.30) -> str:
        if self.total_pairs == 0:
            return "NO DATA — cannot decide M-7"
        if self.fraction >= threshold:
            return (f"fraction {self.fraction:.1%} >= {threshold:.0%}: "
                    "concurrency MAY be worth measuring")
        return (f"fraction {self.fraction:.1%} < {threshold:.0%}: "
                "M-7 NOT justified — recommend keeping I-11")

    def summary(self) -> str:
        return "\n".join([
            f"pairs analysed        : {self.total_pairs}",
            f"independent           : {self.independent_pairs} ({self.fraction:.1%})",
            f"blocked: both privileged   {self.blocked_by_sink}",
            f"blocked: selector overlap  {self.blocked_by_selector}",
            f"blocked: shared idem key   {self.blocked_by_idempotency}",
            f"\nverdict: {self.verdict()}"])

def analyse(effects: Sequence[EffectRef]) -> IndependenceReport:
    ok = sink = sel = idem = 0
    for a, b in combinations(effects, 2):
        if a.idempotency_key and a.idempotency_key == b.idempotency_key:
            idem += 1
        elif a.sink == "privileged" and b.sink == "privileged":
            sink += 1
        elif not selector_disjoint(a.selector, b.selector):
            sel += 1
        else:
            ok += 1
    return IndependenceReport(ok + sink + sel + idem, ok, sink, sel, idem)
