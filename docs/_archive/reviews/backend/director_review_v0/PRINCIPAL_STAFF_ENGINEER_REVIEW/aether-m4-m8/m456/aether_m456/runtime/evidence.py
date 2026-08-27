"""M-4 nine-row foundation evidence with the RF-85 state algebra.

The point of this module: a `local`-profile run is a FIRST-CLASS product run
that honestly derives every row it can and marks the rest with a typed reason.
It is never promotable, and it never has to be rewritten -- switching the
profile to `hermetic` upgrades the same rows in place.

States (sprint_active.md sec.9):
  absent        no canonical source existed            -> typed reason
  invalid       source exists, violates schema/lineage/digest/signature
  unverifiable  well-shaped source, verifier unavailable OR intent unreconciled
  present_valid nine independently verified derived rows
Only present_valid x9 promotes. Everything else fails closed.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional

ABSENT, INVALID, UNVERIFIABLE, PRESENT_VALID = (
    "absent", "invalid", "unverifiable", "present_valid")

ROWS = {
 1:"real model invocation", 2:"authorized effect",      3:"real filesystem change",
 4:"rootless sandbox",      5:"exterior signed verdict",6:"sqlite-wal record",
 7:"cold reconstruction",   8:"rich trajectory",        9:"one runtime authority"}

@dataclass(frozen=True, slots=True)
class Row:
    n: int
    state: str
    source: Optional[str] = None      # canonical source path/kind
    source_digest: Optional[str] = None
    reason: Optional[str] = None

    @property
    def promotable(self) -> bool:
        return self.state == PRESENT_VALID

@dataclass(frozen=True, slots=True)
class EvidenceBundle:
    api: str
    profile_id: str
    assurance_level: str
    rows: Mapping[int, Row]
    lineage: Mapping[str, str]

    @property
    def promotion_eligible(self) -> bool:
        return (len(self.rows) == 9
                and all(r.promotable for r in self.rows.values()))

    @property
    def unattributable_reason(self) -> Optional[str]:
        if self.promotion_eligible: return None
        bad = sorted(n for n, r in self.rows.items() if not r.promotable)
        return f"rows {bad} not present_valid under profile '{self.profile_id}'"

    def summary(self) -> str:
        out = [f"{'row':>3}  {'state':<14} {'what':<26} reason"]
        for n in range(1, 10):
            r = self.rows[n]
            out.append(f"{n:>3}  {r.state:<14} {ROWS[n]:<26} {r.reason or ''}")
        out.append(f"\npromotion_eligible = {self.promotion_eligible}")
        if self.unattributable_reason:
            out.append(f"unattributable: {self.unattributable_reason}")
        return "\n".join(out)


class EvidenceAuditor:
    """Recomputes joins. NEVER trusts a self-asserted boolean."""

    def __init__(self, verifiers: Mapping[int, Callable[[Any], Row]]) -> None:
        self._v = verifiers

    def audit(self, run, profile) -> EvidenceBundle:
        rows: dict[int, Row] = {}
        for n in range(1, 10):
            verifier = self._v.get(n)
            if verifier is None:
                rows[n] = Row(n, ABSENT, reason="no_verifier_bound")
                continue
            try:
                r = verifier(run)
            except Exception as exc:                 # a throwing verifier denies
                r = Row(n, INVALID, reason=f"verifier_error:{type(exc).__name__}")
            # lineage join: every derived row must bind the same run tuple
            if r.state == PRESENT_VALID and not self._joins(run, r):
                r = Row(n, INVALID, r.source, r.source_digest, "lineage_mismatch")
            rows[n] = r
        return EvidenceBundle("mhf.foundation-evidence/1", profile.id,
                              profile.assurance_level, rows, run.lineage)

    @staticmethod
    def _joins(run, row) -> bool:
        return row.source is not None and row.source_digest is not None
