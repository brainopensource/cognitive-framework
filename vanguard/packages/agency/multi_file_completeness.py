"""Caller-aware completion admission for multi-file change (`T-83b`).

A public symbol does not end at the file that defines it. Editing one and
finishing while its call sites are unread is a change that was never closed --
the edited file's own tests can pass over callers that no longer compile, or
that still hold the old contract. This module owns the rule that closes that
gap, and nothing else.

`ADR-0107` (D-1) assigns lane B the `CallerAdmissionEvidence` value type at this
seam and fixes its field inventory as the cross-lane contract. The evidence is
**observational input, never a verdict**: the admission boundary here also
demands exterior verification of the same candidate, treats omissions and
unresolved coverage as non-admissible, and invalidates receipts whose bound
subject has moved.

The module is pure. It holds no port, opens no file, parses nothing, runs
nothing and ranks nothing; it imports only frozen value types (`Symbol`,
`WorkspaceEpoch`) and returns a typed verdict. The runtime session stays the
integration owner: it enumerates callers through `IndexPort` under C's
`IndexSelection`, records receipts, and applies what this returns.

Four refusals are load-bearing and deliberately not collapsed into one:

* **Unresolved coverage is not an empty caller graph.** A missing, stale,
  truncated or unbound index sets `unresolved_coverage`, which yields
  `CALLER_COVERAGE_UNRESOLVED` -- never "zero callers, therefore complete".
  Absence of evidence is the one thing an index may not be read as.
* **A known-but-unhandled caller is an omission.** The session records each one
  as `OMITTED_CALLER_PREFIX + path`; those yield
  `UNINSPECTED_CALLERS_REMAINING`, distinct from every other omission.
* **Receipts are bound to a candidate.** A receipt naming an earlier tree
  describes a tree this proposal has superseded. A later edit invalidates it
  (`INSPECTION_EVIDENCE_STALE`); time does not re-earn it.
* **Inspection is not proof of behaviour.** Reading every caller admits nothing
  on its own; exterior verification must have succeeded on the exact submitted
  candidate (`VERIFICATION_NOT_BOUND_TO_CANDIDATE`).

Refusals caused by an unusable index carry `consumes_reasoning_retry = False`:
the model did not reason badly, the environment failed to supply evidence, and
burning a retry there converts an infrastructure fault into an agent failure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..domain.workspace_epoch import WorkspaceEpoch
from ..ports.index import Symbol

__all__ = [
    "CALLER_ADMISSION_OK",
    "CALLER_COVERAGE_UNRESOLVED",
    "INSPECTION_EVIDENCE_STALE",
    "NO_PUBLIC_SYMBOL_CHANGE",
    "OMITTED_CALLER_PREFIX",
    "UNINSPECTED_CALLERS_REMAINING",
    "VERIFICATION_NOT_BOUND_TO_CANDIDATE",
    "CallerAdmissionEvidence",
    "CallerAdmissionVerdict",
    "evaluate_caller_admission",
    "omit_uninspected_caller",
]

CALLER_ADMISSION_OK = "CALLER_ADMISSION_OK"
CALLER_COVERAGE_UNRESOLVED = "CALLER_COVERAGE_UNRESOLVED"
INSPECTION_EVIDENCE_STALE = "INSPECTION_EVIDENCE_STALE"
NO_PUBLIC_SYMBOL_CHANGE = "NO_PUBLIC_SYMBOL_CHANGE"
UNINSPECTED_CALLERS_REMAINING = "UNINSPECTED_CALLERS_REMAINING"
VERIFICATION_NOT_BOUND_TO_CANDIDATE = "VERIFICATION_NOT_BOUND_TO_CANDIDATE"

#: `ADR-0107` fixes `omissions` as a tuple of strings, so a caller the index
#: knows about but the episode never handled is carried as a prefixed omission
#: rather than as a sixth field. That keeps the cross-lane field inventory exact
#: while still letting this policy separate "a caller is missing" from every
#: other reason the evidence is incomplete.
OMITTED_CALLER_PREFIX = "uninspected_caller:"


def omit_uninspected_caller(caller: Symbol | str) -> str:
    """Build the omission entry for a known caller with no current receipt."""
    return OMITTED_CALLER_PREFIX + str(getattr(caller, "path", caller))


@dataclass(frozen=True, slots=True)
class CallerAdmissionEvidence:
    """What the episode observed about the callers of its changed public symbols.

    Field inventory is `ADR-0107`'s cross-lane contract and is not extended here.

    ``inspection_receipts`` and ``update_receipts`` pair each handled caller with
    the candidate tree digest it was handled against; that binding is what lets a
    later edit invalidate the evidence without this policy knowing what changed.
    ``candidate_identity`` is the submitted candidate as (task digest,
    composition digest, whole submitted tree digest).
    """

    changed_public_symbols: tuple[Symbol, ...] = ()
    inspected_callers: tuple[Symbol, ...] = ()
    updated_callers: tuple[Symbol, ...] = ()
    inspection_receipts: tuple[tuple[Symbol, str], ...] = ()
    update_receipts: tuple[tuple[Symbol, str], ...] = ()
    omissions: tuple[str, ...] = ()
    candidate_identity: tuple[str, str, str] = ("", "", "")
    source_identity: WorkspaceEpoch | None = None
    unresolved_coverage: bool = False

    @property
    def candidate_tree_digest(self) -> str:
        """The submitted tree every receipt must be bound to."""
        return self.candidate_identity[2] if len(self.candidate_identity) > 2 else ""

    @property
    def uninspected_callers(self) -> tuple[str, ...]:
        """Known callers the episode never inspected or updated."""
        return tuple(sorted({
            item[len(OMITTED_CALLER_PREFIX):]
            for item in self.omissions
            if item.startswith(OMITTED_CALLER_PREFIX)
        }))

    @property
    def other_omissions(self) -> tuple[str, ...]:
        """Every omission that is not a named uninspected caller."""
        return tuple(sorted({
            item for item in self.omissions
            if not item.startswith(OMITTED_CALLER_PREFIX)
        }))


@dataclass(frozen=True, slots=True)
class CallerAdmissionVerdict:
    """Typed outcome. ``reason`` is the contract; the text is model feedback."""

    admissible: bool
    reason: str
    rejection_feedback: str | None = None
    uninspected_callers: tuple[str, ...] = ()
    stale_receipts: tuple[str, ...] = ()
    omissions: tuple[str, ...] = ()
    consumes_reasoning_retry: bool = True
    diagnostics: Mapping[str, Any] = field(default_factory=dict)


def _paths(symbols: Sequence[Any]) -> tuple[str, ...]:
    return tuple(sorted({str(getattr(item, "path", item)) for item in symbols}))


def _bound_and_stale(
    receipts: Sequence[tuple[Any, str]], candidate_tree_digest: str,
) -> tuple[set[str], set[str]]:
    """Split receipts into those bound to this candidate and those superseded."""
    bound: set[str] = set()
    stale: set[str] = set()
    for symbol, digest in receipts:
        path = str(getattr(symbol, "path", symbol))
        if digest == candidate_tree_digest and candidate_tree_digest:
            bound.add(path)
        else:
            stale.add(path)
    return bound, stale


def evaluate_caller_admission(
    evidence: CallerAdmissionEvidence,
    *,
    verification_passed: bool = False,
    verification_candidate_identity: tuple[str, str, str] | None = None,
) -> CallerAdmissionVerdict:
    """Decide whether a public-symbol change has closed its caller surface.

    A change touching no public symbol is outside this policy's subject and is
    admitted *by this policy* -- the other completion gates still apply. Anything
    else must show resolved coverage, no omission, every known caller carrying an
    inspection or update receipt bound to the submitted candidate, and exterior
    verification that succeeded on that same candidate.
    """
    symbols = tuple(evidence.changed_public_symbols)
    if not symbols:
        return CallerAdmissionVerdict(True, NO_PUBLIC_SYMBOL_CHANGE)

    candidate = evidence.candidate_tree_digest
    if not candidate:
        return CallerAdmissionVerdict(
            False,
            VERIFICATION_NOT_BOUND_TO_CANDIDATE,
            "ADMISSION GATE REJECTION: the completion evidence names no "
            "submitted candidate tree, so no receipt can be bound to it.",
            diagnostics={"cause": "candidate_identity_unbound"},
        )

    if evidence.unresolved_coverage:
        return CallerAdmissionVerdict(
            False,
            CALLER_COVERAGE_UNRESOLVED,
            "ADMISSION GATE REJECTION: caller coverage for the changed public "
            "symbols is unresolved -- the index was absent, stale, truncated or "
            "unbound. Refresh it and re-observe the callers; an index that could "
            "not answer is not an empty caller graph.",
            omissions=evidence.omissions,
            consumes_reasoning_retry=False,
            diagnostics={
                "cause": "unresolved_coverage",
                "changed_public_symbols": _paths(symbols),
                "source_identity": (
                    evidence.source_identity.digest()
                    if evidence.source_identity is not None else ""
                ),
            },
        )

    inspected_bound, inspected_stale = _bound_and_stale(
        evidence.inspection_receipts, candidate)
    updated_bound, updated_stale = _bound_and_stale(
        evidence.update_receipts, candidate)
    covered = inspected_bound | updated_bound
    stale = tuple(sorted((inspected_stale | updated_stale) - covered))

    # A caller named in `inspected_callers`/`updated_callers` with no receipt
    # bound to this candidate is unproven, not covered: the list says what the
    # episode claims, the receipts say what it can show.
    claimed = set(_paths(evidence.inspected_callers)) | set(_paths(evidence.updated_callers))
    unreceipted = tuple(sorted(claimed - covered))

    uninspected = evidence.uninspected_callers
    outstanding = tuple(sorted(set(uninspected) | set(unreceipted)))
    if outstanding:
        # Split by *why*. Never-read and invalidated-by-a-later-edit are
        # different failures calling for different next moves -- read it, versus
        # re-read it -- so they get different typed reasons.
        revisit = tuple(sorted(set(outstanding) & set(stale)))
        never_read = tuple(path for path in outstanding if path not in revisit)
        if never_read:
            return CallerAdmissionVerdict(
                False,
                UNINSPECTED_CALLERS_REMAINING,
                "ADMISSION GATE REJECTION: the changed public symbols still have "
                f"uninspected callers: {', '.join(never_read)}. Inspect or update "
                "each one on the current candidate before finishing.",
                uninspected_callers=outstanding,
                stale_receipts=stale,
                omissions=evidence.omissions,
                diagnostics={"never_inspected": never_read,
                             "invalidated_by_later_edit": revisit},
            )
        return CallerAdmissionVerdict(
            False,
            INSPECTION_EVIDENCE_STALE,
            "ADMISSION GATE REJECTION: a later edit invalidated the inspection of "
            f"{', '.join(revisit)}. Those callers were read against a tree this "
            "candidate has superseded; re-read them before finishing.",
            uninspected_callers=outstanding,
            stale_receipts=stale,
            omissions=evidence.omissions,
            diagnostics={"invalidated_by_later_edit": revisit},
        )

    other = evidence.other_omissions
    if other:
        return CallerAdmissionVerdict(
            False,
            CALLER_COVERAGE_UNRESOLVED,
            "ADMISSION GATE REJECTION: the completion evidence is incomplete: "
            f"{', '.join(other)}. An omitted observation is unresolved coverage, "
            "not a closed change surface.",
            omissions=evidence.omissions,
            consumes_reasoning_retry=False,
            diagnostics={"cause": "omitted_observations"},
        )

    if not verification_passed:
        return CallerAdmissionVerdict(
            False,
            VERIFICATION_NOT_BOUND_TO_CANDIDATE,
            "ADMISSION GATE REJECTION: inspecting the callers is not evidence "
            "that they still work. Exterior verification must succeed on the "
            "submitted candidate.",
            stale_receipts=stale,
            diagnostics={"cause": "verification_absent_or_failed"},
        )
    if tuple(verification_candidate_identity or ()) != tuple(evidence.candidate_identity):
        return CallerAdmissionVerdict(
            False,
            VERIFICATION_NOT_BOUND_TO_CANDIDATE,
            "ADMISSION GATE REJECTION: the verification receipt was produced "
            "against a different candidate than the one submitted. A tree "
            "mutated after verification cannot reuse that verdict; re-verify.",
            stale_receipts=stale,
            diagnostics={
                "cause": "post_verification_tree_mutation",
                "verification_candidate_identity": tuple(verification_candidate_identity or ()),
                "candidate_identity": tuple(evidence.candidate_identity),
            },
        )

    return CallerAdmissionVerdict(
        True,
        CALLER_ADMISSION_OK,
        stale_receipts=stale,
        diagnostics={"covered_callers": tuple(sorted(covered))},
    )
