"""T-01 / T-02 falsifiers for B20 enumerator membership and subject binding."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.protocols import (
    B20MembershipError,
    enumerate_b20_membership,
    task_set_digest,
    write_b20_report,
)


_REPO = Path(__file__).resolve().parents[2]
_SUITE = _REPO / "benchmarks" / "benchmark_20_suite"
_PREREG = _REPO / "benchmarks" / "sota_preregistration.json"


def _write_task(root: Path, task_id: str, *, oracle: str = "test/test_oracle.py") -> None:
    oracle_path = root / task_id / oracle
    oracle_path.parent.mkdir(parents=True, exist_ok=True)
    oracle_path.write_text("assert True\n", encoding="utf-8")


def _write_membership(root: Path, tasks: list[dict[str, str]], digest: str | None = None) -> None:
    ids = [str(task["id"]) for task in tasks]
    payload = {
        "schema": "aether.b20.membership/1",
        "tasks": tasks,
        "task_set_digest": digest if digest is not None else task_set_digest(ids),
    }
    (root / "membership.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class TestB20Membership(unittest.TestCase):
    def test_pycache_directory_is_not_a_task(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_task(root, "01_real_task")
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "x.pyc").write_bytes(b"\0")
            (root / ".pytest_cache").mkdir()
            (root / "tmp").mkdir()
            _write_membership(root, [{"id": "01_real_task", "oracle": "test/test_oracle.py", "kind": "Brownfield"}])
            membership = enumerate_b20_membership(root)
            self.assertEqual(membership.task_ids, ("01_real_task",))
            self.assertNotIn("__pycache__", membership.task_ids)
            self.assertNotIn(".pytest_cache", membership.task_ids)
            self.assertNotIn("tmp", membership.task_ids)

    def test_directory_names_are_insufficient_without_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_task(root, "01_real_task")
            with self.assertRaises(B20MembershipError):
                enumerate_b20_membership(root)

    def test_hidden_tmp_missing_oracle_duplicate_and_digest_mismatch_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_task(root, "01_real_task")
            (root / ".hidden_task").mkdir()
            (root / "tmp").mkdir()
            _write_membership(
                root,
                [
                    {"id": "01_real_task", "oracle": "test/missing_oracle.py", "kind": "Brownfield"},
                    {"id": "01_real_task", "oracle": "test/test_oracle.py", "kind": "Brownfield"},
                ],
            )
            with self.assertRaises(B20MembershipError):
                enumerate_b20_membership(root)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_task(root, "01_real_task")
            _write_membership(
                root,
                [{"id": "01_real_task", "oracle": "test/test_oracle.py", "kind": "Brownfield"}],
                digest="sha256:" + ("0" * 64),
            )
            with self.assertRaises(B20MembershipError):
                enumerate_b20_membership(root)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_task(root, "01_real_task")
            _write_membership(root, [{"id": "__pycache__", "oracle": "test/test_oracle.py", "kind": "Brownfield"}])
            with self.assertRaises(B20MembershipError):
                enumerate_b20_membership(root)

    def test_digest_is_order_independent_and_matches_frozen_twenty_names(self) -> None:
        prereg = json.loads(_PREREG.read_text(encoding="utf-8"))
        expected = list(prereg["task_sets"]["B1"]["membership"])
        self.assertEqual(len(expected), 20)
        self.assertEqual(task_set_digest(expected), task_set_digest(list(reversed(expected))))
        membership = enumerate_b20_membership(_SUITE)
        self.assertEqual(list(membership.task_ids), sorted(expected))
        self.assertEqual(membership.digest, task_set_digest(expected))
        self.assertNotIn("__pycache__", membership.task_ids)

    def test_missing_subject_sha_refuses_b20_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "benchmark_20_results.json"
            with self.assertRaises(ValueError) as ctx:
                write_b20_report(path, subject_sha="", dry_run=True, task_ids=("01_real_task",))
            self.assertIn("subject_sha", str(ctx.exception).lower())
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
