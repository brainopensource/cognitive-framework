"""Durable engineering state (`spec §34`, `§35`, `§39`).

`spec §39` is the rule that shapes this module: *large payloads become
artifacts; events carry hashes/references.* A repository map, a full test log,
or a context snapshot inlined into an event would put megabytes into an
append-only store and make the ledger unreadable.

So every payload here goes through the substrate's existing `ArtifactWriter`
(`runtime/artifacts.py`), which is already content-addressed, redacts secrets,
and refuses orphans. This module supplies only the *vocabulary* -- which roles
exist, what each carries, and how a checkpoint references them.

Nothing here writes to the event store. Emission stays where it already is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of

__all__ = [
    "ArtifactRole",
    "EngineeringState",
    "StateWriter",
]


class ArtifactRole:
    """Roles this harness writes (`spec §34` reference names).

    Strings rather than an enum because `ArtifactWriter.capture` takes a role
    string and the substrate owns that vocabulary; introducing a parallel enum
    would create two spellings of the same concept.
    """

    TASK = "coding_max.task"
    PROFILE = "coding_max.profile"
    REPO_MAP = "coding_max.repo_map"
    PLAN = "coding_max.plan"
    TODO = "coding_max.todo"
    CONTEXT_SNAPSHOT = "coding_max.context"
    HYPOTHESES = "coding_max.hypotheses"
    DISCOVERIES = "coding_max.discoveries"
    FAILED_ATTEMPTS = "coding_max.failed_attempts"
    PATCH = "coding_max.patch"
    TEST_LOG = "coding_max.test_log"
    VERIFICATION = "coding_max.verification"
    REVIEW = "coding_max.review"
    CONTROLLER = "coding_max.controller"


@dataclass
class EngineeringState:
    """The durable working state of one coding run (`spec §34`).

    Held as references wherever the payload is large. `repo_map_ref` is a
    digest, not a map: restoring a run should not require re-reading a
    megabyte of derived structure to learn what file was being edited.
    """

    task: str = ""
    objective: str = ""
    profile_digest: str = ""
    repo_map_ref: str = ""
    plan_digest: str = ""
    todo_digest: str = ""
    hypotheses: tuple[str, ...] = ()
    discoveries: tuple[str, ...] = ()
    inspected_files: tuple[str, ...] = ()
    edited_files: tuple[str, ...] = ()
    failed_attempts: tuple[Mapping[str, Any], ...] = ()
    patch_refs: tuple[str, ...] = ()
    test_log_refs: tuple[str, ...] = ()
    verification_digest: str = ""
    failure_history: tuple[str, ...] = ()
    recovery_history: tuple[str, ...] = ()
    context_epoch: int = 0
    head: str = ""

    # -- mutation (append-only in spirit; the ledger is the real record) --

    def record_hypothesis(self, text: str) -> None:
        if text and text not in self.hypotheses:
            self.hypotheses = self.hypotheses + (text,)

    def record_discovery(self, text: str) -> None:
        """A fact learned about the repository.

        Kept distinct from a hypothesis on purpose: a discovery is evidence
        that survives a replan, while a hypothesis is precisely the thing a
        replan may discard. Collapsing them is how a run keeps re-deriving
        facts it already paid for.
        """
        if text and text not in self.discoveries:
            self.discoveries = self.discoveries + (text,)

    def record_edit(self, path: str) -> None:
        if path and path not in self.edited_files:
            self.edited_files = self.edited_files + (path,)

    def record_inspection(self, path: str) -> None:
        if path and path not in self.inspected_files:
            self.inspected_files = self.inspected_files + (path,)

    def record_failed_attempt(
        self, *, failure_class: str, detail: str, action: str = ""
    ) -> None:
        """`spec §34`: failed attempts are state, not noise.

        Without them a resumed run has no way to avoid repeating an approach
        that already failed, and `RecoveryPolicy`'s "never repeat a spent
        strategy" rule would silently reset at every checkpoint boundary.
        """
        self.failed_attempts = self.failed_attempts + ({
            "failureClass": failure_class, "detail": detail[:500],
            "action": action, "index": len(self.failed_attempts),
        },)
        if failure_class:
            self.failure_history = self.failure_history + (failure_class,)
        if action:
            self.recovery_history = self.recovery_history + (action,)

    # -- serialisation ---------------------------------------------------

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "objective": self.objective,
            "profileDigest": self.profile_digest,
            "repoMapRef": self.repo_map_ref,
            "planDigest": self.plan_digest,
            "todoDigest": self.todo_digest,
            "hypotheses": list(self.hypotheses),
            "discoveries": list(self.discoveries),
            "inspectedFiles": list(self.inspected_files),
            "editedFiles": list(self.edited_files),
            "failedAttempts": [dict(a) for a in self.failed_attempts],
            "patchRefs": list(self.patch_refs),
            "testLogRefs": list(self.test_log_refs),
            "verificationDigest": self.verification_digest,
            "failureHistory": list(self.failure_history),
            "recoveryHistory": list(self.recovery_history),
            "contextEpoch": self.context_epoch,
            "head": self.head,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    @classmethod
    def from_canonical_dict(cls, raw: Mapping[str, Any]) -> "EngineeringState":
        return cls(
            task=str(raw.get("task", "")),
            objective=str(raw.get("objective", "")),
            profile_digest=str(raw.get("profileDigest", "")),
            repo_map_ref=str(raw.get("repoMapRef", "")),
            plan_digest=str(raw.get("planDigest", "")),
            todo_digest=str(raw.get("todoDigest", "")),
            hypotheses=tuple(raw.get("hypotheses", []) or ()),
            discoveries=tuple(raw.get("discoveries", []) or ()),
            inspected_files=tuple(raw.get("inspectedFiles", []) or ()),
            edited_files=tuple(raw.get("editedFiles", []) or ()),
            failed_attempts=tuple(dict(a) for a in raw.get("failedAttempts", []) or ()),
            patch_refs=tuple(raw.get("patchRefs", []) or ()),
            test_log_refs=tuple(raw.get("testLogRefs", []) or ()),
            verification_digest=str(raw.get("verificationDigest", "")),
            failure_history=tuple(raw.get("failureHistory", []) or ()),
            recovery_history=tuple(raw.get("recoveryHistory", []) or ()),
            context_epoch=int(raw.get("contextEpoch", 0) or 0),
            head=str(raw.get("head", "")),
        )

    def render(self, *, max_chars: int = 2000) -> str:
        """Compact briefing for a resumed or replanned turn.

        This is what makes a long task survivable: the worker rejoins with the
        facts and the dead ends, not with a replay of every prior message.
        """
        lines: list[str] = ["# Engineering state"]
        if self.objective:
            lines.append(f"objective: {self.objective}")
        if self.head:
            lines.append(f"head: {self.head[:12]}")
        if self.discoveries:
            lines.append("\n## Established facts")
            lines += [f"  - {d}" for d in self.discoveries[:12]]
        if self.hypotheses:
            lines.append("\n## Open hypotheses")
            lines += [f"  - {h}" for h in self.hypotheses[:8]]
        if self.edited_files:
            lines.append(f"\nedited: {', '.join(self.edited_files[:12])}")
        if self.failed_attempts:
            lines.append("\n## Already tried and failed (do not repeat)")
            for attempt in self.failed_attempts[-6:]:
                lines.append(
                    f"  - [{attempt.get('failureClass')}] "
                    f"{attempt.get('action') or 'attempt'}: {attempt.get('detail')}")
        text = "\n".join(lines)
        if len(text) <= max_chars:
            return text
        return text[:max_chars].rsplit("\n", 1)[0] + "\n  … (state truncated)"


class StateWriter:
    """Persists engineering state through the substrate's `ArtifactWriter`.

    The writer is optional. On the legacy path (`artifacts is None`) every
    method is a no-op returning an empty reference, matching how
    `_LayeredOperator._capture` already behaves in `runtime/session.py`. A run
    without artifact capture must still run; it simply cannot be resumed.
    """

    def __init__(self, artifacts: Any = None) -> None:
        self._artifacts = artifacts
        self._refs: dict[str, str] = {}

    @property
    def available(self) -> bool:
        return self._artifacts is not None

    def capture(
        self,
        role: str,
        payload: Any,
        *,
        turn: int = 0,
        labels: Mapping[str, Any] | None = None,
    ) -> str:
        """Write one payload and return its reference digest."""
        if self._artifacts is None:
            return ""
        body = payload.to_canonical_dict() if hasattr(payload, "to_canonical_dict") \
            else payload
        try:
            ref = self._artifacts.capture(role, body, turn=turn, labels=dict(labels or {}))
        except Exception:  # noqa: BLE001 - a capture failure must not end a run
            return ""
        digest = str(getattr(ref, "digest", "") or getattr(ref, "content_digest", "") or "")
        if digest:
            self._refs[role] = digest
        return digest

    def capture_state(self, state: EngineeringState, *, turn: int = 0) -> str:
        return self.capture(
            ArtifactRole.CONTROLLER, state, turn=turn,
            labels={"stateDigest": state.digest(), "contextEpoch": state.context_epoch},
        )

    def capture_test_log(
        self, verification: Any, *, turn: int = 0
    ) -> str:
        """Test output is the single largest payload a coding run produces.

        Captured whole as an artifact and referenced by digest, so the event
        carries a pointer while the evidence stays recoverable in full --
        which is what `spec §57.10` means by reconstructable from artifacts.
        """
        return self.capture(
            ArtifactRole.TEST_LOG, verification, turn=turn,
            labels={"passed": bool(getattr(verification, "passed", False))},
        )

    def references(self) -> Mapping[str, str]:
        return dict(self._refs)
