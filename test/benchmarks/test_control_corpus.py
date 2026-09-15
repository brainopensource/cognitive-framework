"""Integrity falsifiers for the fixed L2 control corpus.

The corpus is data, rather than a runtime registry.  Keep its validation here so
preparation remains hermetic and does not add a production dependency.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SUITE_PATH = REPOSITORY_ROOT / "benchmarks/ladder/l2_thirty/suite.json"
ALLOWED_POOL_PREFIXES = (
    "benchmarks/benchmark_20_suite/",
    "benchmarks/baac/challenges/",
    "benchmarks/greenfield/",
    "benchmarks/frontier_v090/fixtures/",
)
FORBIDDEN_PATH_PARTS = {
    ".git",
    "__pycache__",
    "artifacts",
    "m8_heldout",
    "runs",
}
EXPECTED_CLASS_COUNTS = {
    "brownfield": 10,
    "greenfield": 11,
    "multi_file": 5,
    "multi_turn": 1,
    "single_file": 3,
}


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_source_tree(source_path: str, oracle_path: str) -> str:
    root = REPOSITORY_ROOT / source_path
    digest = hashlib.sha256()
    for path in sorted(path for path in root.rglob("*") if path.is_file()):
        relative_path = path.relative_to(REPOSITORY_ROOT).as_posix()
        if relative_path == oracle_path:
            continue
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def _is_candidate_path(relative_path: str) -> bool:
    path = Path(relative_path)
    return (
        not path.is_absolute()
        and any(relative_path.startswith(prefix) for prefix in ALLOWED_POOL_PREFIXES)
        and not any(part in FORBIDDEN_PATH_PARTS for part in path.parts)
        and not relative_path.endswith((".pyc", ".sqlite", ".sqlite3"))
    )


def validate_suite(suite: object) -> None:
    if not isinstance(suite, dict):
        raise ValueError("suite must be an object")
    if suite.get("schema") != "aether.l2-suite/1":
        raise ValueError("unexpected schema")
    if suite.get("n") != 30:
        raise ValueError("L2 suite must schedule exactly 30 tasks")

    tasks = suite.get("tasks")
    classes = suite.get("classes")
    if not isinstance(tasks, list) or not isinstance(classes, dict):
        raise ValueError("tasks and classes must be present")
    if len(tasks) != 30:
        raise ValueError("membership count must be exactly 30")

    task_ids: list[str] = []
    class_ids: list[str] = []
    for stratum, members in classes.items():
        if not isinstance(stratum, str) or not isinstance(members, list):
            raise ValueError("malformed class membership")
        class_ids.extend(members)
    if {name: len(members) for name, members in classes.items()} != EXPECTED_CLASS_COUNTS:
        raise ValueError("insufficient class mix")

    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("malformed task record")
        task_id = task.get("id")
        stratum = task.get("stratum")
        source = task.get("source")
        oracle = task.get("oracle")
        if not isinstance(task_id, str) or not isinstance(stratum, str):
            raise ValueError("malformed task membership")
        if not isinstance(source, dict) or not isinstance(oracle, dict):
            raise ValueError("malformed task digests")
        if stratum not in classes or task_id not in classes[stratum]:
            raise ValueError("task is absent from its declared class")
        task_ids.append(task_id)

        source_path = source.get("path")
        source_digest = source.get("sha256")
        oracle_path = oracle.get("path")
        oracle_digest = oracle.get("sha256")
        if (
            not isinstance(source_path, str)
            or not isinstance(source_digest, str)
            or not isinstance(oracle_path, str)
            or not isinstance(oracle_digest, str)
        ):
            raise ValueError("malformed source or oracle record")
        if not all(_is_candidate_path(path) for path in [source_path, oracle_path]):
            raise ValueError("generated, excluded, or non-candidate path")
        source_root = REPOSITORY_ROOT / source_path
        if not source_root.is_dir() or not (REPOSITORY_ROOT / oracle_path).is_file():
            raise ValueError("missing source or oracle")
        if any(
            any(part in FORBIDDEN_PATH_PARTS for part in path.relative_to(source_root).parts)
            for path in source_root.rglob("*")
        ):
            raise ValueError("generated, excluded, or non-candidate path")
        if _sha256_source_tree(source_path, oracle_path) != source_digest:
            raise ValueError("source digest mismatch")
        if _sha256_file(REPOSITORY_ROOT / oracle_path) != oracle_digest:
            raise ValueError("oracle digest mismatch")

    if len(set(task_ids)) != len(task_ids) or len(set(class_ids)) != len(class_ids):
        raise ValueError("duplicate task identifier")
    if set(task_ids) != set(class_ids):
        raise ValueError("class membership must cover the scheduled tasks")


class TestControlCorpus(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))

    def test_frozen_suite_is_complete_and_digest_bound(self) -> None:
        validate_suite(self.suite)

    def test_rejects_count_other_than_thirty(self) -> None:
        suite = deepcopy(self.suite)
        suite["n"] = 29
        with self.assertRaisesRegex(ValueError, "exactly 30"):
            validate_suite(suite)

    def test_rejects_malformed_membership(self) -> None:
        suite = deepcopy(self.suite)
        suite["tasks"][0].pop("stratum")
        with self.assertRaisesRegex(ValueError, "malformed task membership"):
            validate_suite(suite)

    def test_rejects_duplicate_ids(self) -> None:
        suite = deepcopy(self.suite)
        duplicate = suite["tasks"][0]["id"]
        suite["tasks"][1]["id"] = duplicate
        suite["classes"]["brownfield"][1] = duplicate
        with self.assertRaisesRegex(ValueError, "duplicate task identifier"):
            validate_suite(suite)

    def test_rejects_missing_oracle(self) -> None:
        suite = deepcopy(self.suite)
        suite["tasks"][0]["oracle"]["path"] = "benchmarks/benchmark_20_suite/missing.py"
        with self.assertRaisesRegex(ValueError, "missing source or oracle"):
            validate_suite(suite)

    def test_rejects_l0_or_l1_contamination(self) -> None:
        suite = deepcopy(self.suite)
        suite["tasks"][0]["source"]["path"] = "benchmarks/ladder/l0_triad/p0_fib"
        with self.assertRaisesRegex(ValueError, "excluded|non-candidate"):
            validate_suite(suite)

    def test_rejects_generated_cache_entry(self) -> None:
        suite = deepcopy(self.suite)
        suite["tasks"][0]["source"]["path"] = "benchmarks/frontier_v090"
        with self.assertRaisesRegex(ValueError, "generated|excluded|non-candidate"):
            validate_suite(suite)

    def test_rejects_insufficient_class_mix(self) -> None:
        suite = deepcopy(self.suite)
        suite["classes"]["single_file"].pop()
        with self.assertRaisesRegex(ValueError, "insufficient class mix"):
            validate_suite(suite)


if __name__ == "__main__":
    unittest.main()
