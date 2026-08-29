"""Cross-file completeness verification checking that implicated files were reviewed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class CompletenessReport:
    is_complete: bool
    missing_inspections: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def check_multi_file_completeness(
    implicated_files: Sequence[str],
    inspected_files: Sequence[str],
    modified_files: Sequence[str],
) -> CompletenessReport:
    """Verify that all files implicated by task context or dependencies were inspected."""
    inspected_set = set(inspected_files)
    missing = [f for f in implicated_files if f not in inspected_set]

    warnings: list[str] = []
    for mod in modified_files:
        if mod not in inspected_set:
            warnings.append(f"Modified file '{mod}' was never explicitly inspected")

    if missing:
        warnings.append(f"{len(missing)} implicated files were not inspected before completion")

    return CompletenessReport(
        is_complete=len(missing) == 0 and len(warnings) == 0,
        missing_inspections=tuple(missing),
        warnings=tuple(warnings),
    )
