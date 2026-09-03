"""CMX-06 test-investigator role: read-only test-scope composition layer."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any, Mapping, Sequence

from ...domain.canonicalisation.digest import digest_of

READ_ONLY_TOOLS = ("fs.read", "fs.search")
MAX_TESTS = 20
ROLE_ID = "test_investigator"


def investigate_tests(
    artifact_writer: Any, *, task_digest: str,
    changed_files: Sequence[str], affected_tests: Sequence[str],
) -> Any:
    """Emit bounded test references and reject non-test paths."""
    if not task_digest:
        raise ValueError("test investigator requires a task digest")
    if len(affected_tests) > MAX_TESTS:
        raise ValueError(f"test investigator output exceeds {MAX_TESTS} entries")
    tests = []
    for path in affected_tests:
        normalized = str(PurePosixPath(str(path)))
        if not (normalized.startswith("test/") or normalized.startswith("tests/")):
            raise ValueError("test investigator may only return test-scoped paths")
        tests.append(normalized)
    changed = [str(PurePosixPath(str(path))) for path in changed_files]
    payload = {"schema": "cmx06.affected-tests/1", "taskDigest": task_digest,
               "changedFiles": changed, "tests": tests,
               "resultDigest": digest_of({"taskDigest": task_digest,
                                           "changedFiles": changed, "tests": tests})}
    return artifact_writer.capture("verification_report", payload, required=True)


def contract() -> Mapping[str, Any]:
    return {"role": ROLE_ID, "tools": READ_ONLY_TOOLS, "writes": False,
            "input": ("task-digest", "changed-files"), "maxEntries": MAX_TESTS,
            "testScopeOnly": True, "output": "verification_report"}
