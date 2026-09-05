"""Fail-closed greenfield admission and scaffold baseline facts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of

__all__ = [
    "GreenfieldAssessment",
    "GreenfieldPolicy",
    "GreenfieldDecision",
    "ScaffoldBaseline",
    "assess_greenfield_workspace",
]


_IGNORED_WORKSPACE_ENTRIES = frozenset({
    ".git", ".hg", ".svn", ".vanguard", ".pytest_cache", "__pycache__",
    ".gitignore", ".editorconfig", "README.md", "TASK.md", "pyproject.toml",
    "package.json", "package-lock.json", "uv.lock",
})


@dataclass(frozen=True, slots=True)
class GreenfieldAssessment:
    workspace: str
    effectively_empty: bool
    entries: tuple[str, ...]
    escaped_entries: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ScaffoldBaseline:
    workspace: str
    decision: str
    baseline_digest: str
    entries: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GreenfieldDecision:
    admissible: bool
    reason: str
    baseline: ScaffoldBaseline | None = None


def _safe_relative(root: Path, candidate: Path) -> str | None:
    try:
        resolved = candidate.resolve(strict=False)
        relative = resolved.relative_to(root.resolve())
    except (OSError, ValueError):
        return None
    return relative.as_posix()


def assess_greenfield_workspace(workspace: str | Path) -> GreenfieldAssessment:
    """Classify a workspace without requiring a test directory to exist.

    VCS and runtime metadata are ignored, while symlinks resolving outside the
    target are reported as an escape.  Escape facts are never treated as
    harmless emptiness.
    """
    root = Path(workspace).resolve()
    if not root.is_dir():
        return GreenfieldAssessment(str(root), False, (), (str(root),))
    entries: list[str] = []
    escaped: list[str] = []
    for item in sorted(root.iterdir(), key=lambda path: path.name):
        if item.name in _IGNORED_WORKSPACE_ENTRIES:
            continue
        relative = _safe_relative(root, item)
        if relative is None:
            escaped.append(item.name)
            continue
        entries.append(relative)
    return GreenfieldAssessment(
        workspace=str(root), effectively_empty=not entries and not escaped,
        entries=tuple(entries), escaped_entries=tuple(escaped),
    )


class GreenfieldPolicy:
    """Admission policy for a newly scaffolded target.

    Structural validity alone is insufficient.  A generated smoke/contract
    test must be present in the target and must have passed behaviorally.
    """

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.baseline: ScaffoldBaseline | None = None

    def assess(self) -> GreenfieldAssessment:
        return assess_greenfield_workspace(self.workspace)

    def record_scaffold_baseline(self) -> ScaffoldBaseline:
        assessment = self.assess()
        if assessment.escaped_entries:
            raise ValueError("workspace contains a path/symlink escape")
        if not assessment.effectively_empty:
            raise ValueError("scaffold baseline requires an effectively empty workspace")
        self.baseline = ScaffoldBaseline(
            workspace=str(self.workspace), decision="scaffold_baseline_recorded",
            baseline_digest=digest_of({"workspace": str(self.workspace), "entries": ()}),
            entries=(),
        )
        return self.baseline

    def evaluate(
        self,
        *,
        structural_passed: bool,
        behavioral_passed: bool,
        smoke_test_created: bool,
        created_files: Sequence[str] = (),
        baseline: ScaffoldBaseline | None = None,
        oracle_failed_on_stub: bool | None = None,
    ) -> GreenfieldDecision:
        baseline = baseline or self.baseline
        if self.assess().escaped_entries:
            return GreenfieldDecision(False, "PATH_ESCAPE")
        if baseline is None:
            return GreenfieldDecision(False, "SCAFFOLD_BASELINE_REQUIRED")
        if not structural_passed:
            return GreenfieldDecision(False, "STRUCTURAL_EVIDENCE_REQUIRED", baseline)
        if not smoke_test_created:
            return GreenfieldDecision(False, "GENERATED_SMOKE_TEST_REQUIRED", baseline)
        if not behavioral_passed:
            return GreenfieldDecision(False, "BEHAVIORAL_EVIDENCE_REQUIRED", baseline)
        if not tuple(created_files):
            return GreenfieldDecision(False, "GENERATED_FILES_REQUIRED", baseline)
        for relative in created_files:
            candidate = self.workspace / str(relative)
            if _safe_relative(self.workspace, candidate) is None:
                return GreenfieldDecision(False, "PATH_ESCAPE", baseline)
        if oracle_failed_on_stub is False or oracle_failed_on_stub is None:
            return GreenfieldDecision(False, "VACUOUS_ORACLE", baseline)
        if behavioral_passed and _implementation_is_stub(self.workspace, created_files):
            return GreenfieldDecision(False, "VACUOUS_ORACLE", baseline)
        return GreenfieldDecision(True, "greenfield_completion_admissible", baseline)


def _implementation_is_stub(workspace: Path, created_files: Sequence[str]) -> bool:
    """True when created non-test files are missing, empty, or NotImplemented stubs."""
    impls = tuple(
        relative for relative in created_files
        if "test" not in Path(relative).as_posix().lower()
    )
    if not impls:
        return True
    for relative in impls:
        candidate = workspace / str(relative)
        if not candidate.is_file():
            return True
        text = candidate.read_text(encoding="utf-8")
        if "NotImplementedError" in text or "NotImplemented" in text:
            return True
        body = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        executable = [
            line for line in body
            if not line.startswith(("def ", "class ", "import ", "from ", "@"))
        ]
        if not executable or all(line in {"pass", "...", "return", "return None"} for line in executable):
            return True
    return False
