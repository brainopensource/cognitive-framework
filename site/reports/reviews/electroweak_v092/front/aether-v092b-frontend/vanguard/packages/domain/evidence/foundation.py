"""`mhf.foundation-evidence/1` — the derived M-4 bundle (`ADR-0088 Decision 2`).

M-4 adds no architecture. What M-3C owes it is a *derived* artifact contract:
a bundle whose header cross-binds one lineage, and whose every row names the
canonical source it was computed from.

The rule this file exists to enforce is that a row is **derived or absent**.
There is no third state. A caller cannot assert `signature_verified: true`; it
supplies the artifact the claim was read from, and the row carries that
artifact's digest. A claim with no source is `absent` with a typed reason, and
absent never counts toward the gate — an unsupported claim must not be
indistinguishable from a satisfied one.

Verification of a populated bundle remains `evidence/audit.py`'s job. This
module builds the thing that gets verified, and refuses to build a dishonest
one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..canonicalisation.digest import digest_of
from .audit import REQUIRED_ROW_COUNT, REQUIRED_ROW_NAMES

API = "mhf.foundation-evidence/1"


class FoundationEvidenceError(ValueError):
    """A bundle that cannot be built honestly."""


@dataclass(frozen=True, slots=True)
class EvidenceRow:
    """One of the nine required observations, and where it came from."""

    number: int
    name: str
    #: Digest of the canonical artifact this row was derived from. Empty only
    #: when the row is absent.
    source_digest: str = ""
    #: `derived` or `absent`. Never `asserted`: there is no such state.
    status: str = "absent"
    #: Why the row could not be derived. Required whenever status is `absent`.
    absence_reason: str = ""
    #: The derived observation itself, already read off the source.
    observation: Mapping[str, Any] = field(default_factory=dict)
    #: Canonical artifact from which the observation was derived. The digest
    #: is recomputed here; callers cannot attest their own source digest.
    source: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.number not in REQUIRED_ROW_NAMES:
            raise FoundationEvidenceError(f"row {self.number} is not one of the nine")
        if self.name != REQUIRED_ROW_NAMES[self.number]:
            raise FoundationEvidenceError(
                f"row {self.number} must be named {REQUIRED_ROW_NAMES[self.number]!r}")
        if self.status not in {"derived", "absent"}:
            raise FoundationEvidenceError(
                f"row {self.number} status must be derived or absent, not {self.status!r}")
        if self.status == "derived":
            if not self.source:
                raise FoundationEvidenceError(
                    f"row {self.number} claims derivation with no source artifact")
            recomputed = digest_of(dict(self.source))
            if self.source_digest and self.source_digest != recomputed:
                raise FoundationEvidenceError(
                    f"row {self.number} source digest does not match its artifact")
            object.__setattr__(self, "source_digest", recomputed)
        if self.status == "absent" and not self.absence_reason:
            raise FoundationEvidenceError(
                f"row {self.number} is absent with no reason; silent absence is "
                "indistinguishable from a pass")

    @property
    def derived(self) -> bool:
        return self.status == "derived"

    def identity(self) -> Mapping[str, Any]:
        return {
            "number": self.number,
            "name": self.name,
            "status": self.status,
            "source_digest": self.source_digest,
            "absence_reason": self.absence_reason,
            "observation": dict(self.observation),
            "source": dict(self.source),
        }


def absent(number: int, reason: str) -> EvidenceRow:
    """The honest row for an observation this run cannot support."""
    return EvidenceRow(number, REQUIRED_ROW_NAMES[number], status="absent",
                       absence_reason=reason)


def derived(number: int, source: Mapping[str, Any], observation: Mapping[str, Any]) -> EvidenceRow:
    """A row computed from a named canonical artifact."""
    return EvidenceRow(number, REQUIRED_ROW_NAMES[number], status="derived",
                       observation=dict(observation), source=dict(source))


@dataclass(frozen=True, slots=True)
class FoundationEvidence:
    """The bundle header plus its nine rows, bound to exactly one lineage."""

    project_id: str
    run_id: str
    episode_id: str
    composition_digest: str
    activation_digest: str
    run_digest: str
    #: Ledger event range this run occupies, as `{first_seq, last_seq, count}`.
    event_range: Mapping[str, Any]
    #: Digest of the terminal link of the project hash chain.
    terminal_chain_digest: str
    #: Preregistered task and oracle identity. Preregistration is what stops a
    #: subject from being chosen after the result is known.
    task_digest: str
    oracle: str | None
    preregistration_digest: str
    rows: tuple[EvidenceRow, ...]
    #: Experiment identity, when this run belongs to one. Never collapsed into
    #: `D_H` or `D_R`.
    experiment_digest: str | None = None
    api: str = API
    bundle_digest: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.project_id or not self.run_id or not self.episode_id:
            raise FoundationEvidenceError("a bundle binds one project, run, and episode")
        if not self.composition_digest or not self.activation_digest or not self.run_digest:
            raise FoundationEvidenceError("a bundle binds D_H, activation, and D_R")
        if not self.task_digest or not self.preregistration_digest:
            raise FoundationEvidenceError("a bundle binds task and preregistration digests")
        numbers = [row.number for row in self.rows]
        if sorted(numbers) != list(range(1, REQUIRED_ROW_COUNT + 1)):
            raise FoundationEvidenceError(
                f"a bundle carries exactly the nine rows; got {sorted(numbers)}")
        object.__setattr__(self, "rows", tuple(sorted(self.rows, key=lambda r: r.number)))
        object.__setattr__(self, "bundle_digest", digest_of({
            "api": self.api,
            "header": dict(self.header()),
            "rows": [row.identity() for row in self.rows],
        }))

    def header(self) -> Mapping[str, Any]:
        """Everything the bundle cross-binds, in one place."""
        return {
            "project_id": self.project_id,
            "run_id": self.run_id,
            "episode_id": self.episode_id,
            "composition_digest": self.composition_digest,
            "activation_digest": self.activation_digest,
            "run_digest": self.run_digest,
            "experiment_digest": self.experiment_digest,
            "event_range": dict(self.event_range),
            "terminal_chain_digest": self.terminal_chain_digest,
            "task_digest": self.task_digest,
            "oracle": self.oracle,
            "preregistration_digest": self.preregistration_digest,
            "row_source_digests": {
                str(row.number): row.source_digest for row in self.rows},
        }

    @property
    def absent_rows(self) -> tuple[EvidenceRow, ...]:
        return tuple(row for row in self.rows if not row.derived)

    @property
    def complete(self) -> bool:
        """Whether all nine rows were derived. Never a claim that they passed."""
        return not self.absent_rows

    def to_wire(self) -> Mapping[str, Any]:
        return {"api": self.api, "header": dict(self.header()),
                "rows": [dict(row.identity()) for row in self.rows],
                "bundle_digest": self.bundle_digest}


def build_foundation_evidence(
    *,
    lineage: Mapping[str, Any],
    task_digest: str,
    oracle: str | None,
    preregistration_digest: str,
    event_range: Mapping[str, Any],
    terminal_chain_digest: str,
    rows: Sequence[EvidenceRow],
    experiment_digest: str | None = None,
) -> FoundationEvidence:
    """Assemble a bundle from a `RunPlan.lineage()` and whatever rows exist.

    Rows that were not supplied are filled in as `absent`, with a reason that
    names the gate they belong to. Filling a gap with a default `true` is the
    one thing this contract exists to make impossible.
    """
    supplied = {row.number: row for row in rows}
    duplicates = [n for n in supplied if sum(1 for r in rows if r.number == n) > 1]
    if duplicates:
        raise FoundationEvidenceError(f"rows are declared twice: {sorted(set(duplicates))}")
    complete = tuple(
        supplied.get(number)
        or absent(number, f"{REQUIRED_ROW_NAMES[number]} was not derived from a canonical source")
        for number in range(1, REQUIRED_ROW_COUNT + 1)
    )
    return FoundationEvidence(
        project_id=str(lineage.get("project_id", "")),
        run_id=str(lineage.get("run_id", "")),
        episode_id=str(lineage.get("episode_id", "")),
        composition_digest=str(lineage.get("composition_digest", "")),
        activation_digest=str(lineage.get("activation_digest", "")),
        run_digest=str(lineage.get("run_digest", "")),
        event_range=dict(event_range),
        terminal_chain_digest=terminal_chain_digest,
        task_digest=task_digest,
        oracle=oracle,
        preregistration_digest=preregistration_digest,
        rows=complete,
        experiment_digest=experiment_digest,
    )
