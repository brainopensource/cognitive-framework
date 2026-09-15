"""Linter falsifiers for Q-01 corpus quarantine metadata and admission."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.linters.check_corpus_quarantine import (
    check_admission,
    check_metadata,
    main,
)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _attestation(member_id: str, role: str) -> str:
    from benchmarks.ladder.quarantine import digest_canonical
    return digest_canonical({"id": member_id, "role": role, "origin": "sha256:" + "ab" * 32})


def _valid_member(member_id: str, role: str, *, tombstone: str | None = None) -> dict:
    from benchmarks.ladder.quarantine import digest_canonical
    seed = abs(hash(member_id)) % (16 ** 8)
    source = "sha256:" + f"{seed:08x}" + ("11" if role != "HOLDOUT" else "22") * 28
    oracle = "sha256:" + f"{seed:08x}" + ("33" if role != "HOLDOUT" else "44") * 28
    return {
        "id": member_id,
        "aliases": [],
        "origin": source,
        "source_fingerprint": source,
        "oracle_fingerprint": oracle,
        "task_fingerprint": digest_canonical(
            {"id": member_id, "aliases": [], "source": source, "oracle": oracle}
        ),
        "stratum": "single_file",
        "role": role,
        "exposure_tombstone": tombstone,
        "attestation": _attestation(member_id, role),
    }


class TestCorpusQuarantineLinter(unittest.TestCase):
    def test_metadata_rejects_plaintext_commitment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = {
                "schema": "aether.corpus-quarantine/1",
                "holdout_admission": "UNACCEPTED",
                "expected_holdout": {
                    "n": 30,
                    "strata": {
                        "brownfield": 10,
                        "greenfield": 11,
                        "multi_file": 5,
                        "multi_turn": 1,
                        "single_file": 3,
                    },
                },
                "members": [
                    {
                        **_valid_member("dev-1", "DEV"),
                        "brief": "implement the hidden oracle",
                    }
                ],
                "entrypoints": [],
            }
            registry_path = root / "benchmarks" / "ladder" / "corpus_registry.json"
            _write_json(registry_path, registry)
            (root / "benchmarks" / "ladder" / "control_preregistration.json").write_text(
                json.dumps({"schema": "aether.control-preregistration/1", "status": "UNFROZEN"}),
                encoding="utf-8",
            )
            errors = check_metadata(root, registry_path=registry_path, scan_entrypoints=False)
            self.assertTrue(any("plaintext" in error.lower() or "brief" in error.lower() for error in errors))

    def test_metadata_rejects_uncovered_loader(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry_path = root / "benchmarks" / "ladder" / "corpus_registry.json"
            _write_json(
                registry_path,
                {
                    "schema": "aether.corpus-quarantine/1",
                    "holdout_admission": "UNACCEPTED",
                    "expected_holdout": {
                        "n": 30,
                        "strata": {
                            "brownfield": 10,
                            "greenfield": 11,
                            "multi_file": 5,
                            "multi_turn": 1,
                            "single_file": 3,
                        },
                    },
                    "members": [_valid_member("dev-1", "DEV")],
                    "entrypoints": [],
                },
            )
            rogue = root / "benchmarks" / "rogue_loader.py"
            rogue.parent.mkdir(parents=True, exist_ok=True)
            rogue.write_text(
                "from benchmarks.baac.lib.state import materialize_scratch_workspace\n"
                "def run(src, dest):\n"
                "    materialize_scratch_workspace(src, dest)\n",
                encoding="utf-8",
            )
            errors = check_metadata(root, registry_path=registry_path, scan_entrypoints=True)
            self.assertTrue(any("uncovered" in error.lower() or "loader" in error.lower() for error in errors))

    def test_admission_rejects_wrong_holdout_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            members = [_valid_member(f"eval-{index}", "HOLDOUT") for index in range(29)]
            registry_path = root / "benchmarks" / "ladder" / "corpus_registry.json"
            _write_json(
                registry_path,
                {
                    "schema": "aether.corpus-quarantine/1",
                    "holdout_admission": "PENDING",
                    "expected_holdout": {
                        "n": 30,
                        "strata": {
                            "brownfield": 10,
                            "greenfield": 11,
                            "multi_file": 5,
                            "multi_turn": 1,
                            "single_file": 3,
                        },
                    },
                    "members": members,
                    "entrypoints": [],
                },
            )
            errors = check_admission(root, registry_path=registry_path, scan_entrypoints=False)
            self.assertTrue(any("30" in error or "count" in error.lower() or "n=" in error for error in errors))

    def test_repository_metadata_mode_is_clean(self) -> None:
        self.assertEqual(main(["--metadata"]), 0)


if __name__ == "__main__":
    unittest.main()
