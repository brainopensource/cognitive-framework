"""Q-01 authorization-domain falsifiers for corpus quarantine.

Hermetic synthetic sealed stores only. Real T-51 member bytes are never
copied into these fixtures.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from benchmarks.ladder.quarantine import (
    QuarantineError,
    SealedStore,
    admit_development,
    admit_evaluation,
    digest_canonical,
    fingerprint_bytes,
    fingerprint_tree,
    guard_capture,
    load_registry,
    materialize,
    promote_to_holdout,
    refuse_unfrozen_scoring,
    validate_registry_document,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "benchmarks" / "ladder" / "corpus_registry.json"
SUITE_PATH = REPO_ROOT / "benchmarks" / "ladder" / "l2_thirty" / "suite.json"
FORBIDDEN_PLAINTEXT_KEYS = {
    "brief",
    "prompt",
    "problem",
    "solution",
    "oracle_text",
    "patch",
    "source_text",
    "task_text",
    "content",
    "body",
}


def _attestation(payload: dict) -> str:
    return digest_canonical(payload)


def _member(
    *,
    member_id: str,
    role: str,
    source_fp: str,
    oracle_fp: str,
    stratum: str = "greenfield",
    aliases: list[str] | None = None,
    tombstone: str | None = None,
    attestation: str | None = None,
) -> dict:
    origin = source_fp
    task_fp = digest_canonical(
        {
            "id": member_id,
            "aliases": sorted(aliases or []),
            "source": source_fp,
            "oracle": oracle_fp,
        }
    )
    record = {
        "id": member_id,
        "aliases": list(aliases or []),
        "origin": origin,
        "source_fingerprint": source_fp,
        "oracle_fingerprint": oracle_fp,
        "task_fingerprint": task_fp,
        "stratum": stratum,
        "role": role,
        "exposure_tombstone": tombstone,
        "attestation": attestation
        or _attestation({"id": member_id, "role": role, "origin": origin}),
    }
    return record


def _registry(members: list[dict], entrypoints: list[dict] | None = None) -> dict:
    return {
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
        "members": members,
        "entrypoints": list(entrypoints or []),
    }


class TestQuarantineFailClosed(unittest.TestCase):
    def test_missing_identity_is_rejected(self) -> None:
        registry = _registry(
            [_member(member_id="dev-a", role="DEV", source_fp="sha256:" + "aa" * 32,
                     oracle_fp="sha256:" + "bb" * 32)]
        )
        broken = dict(registry)
        broken["members"] = [{k: v for k, v in registry["members"][0].items() if k != "id"}]
        errors = validate_registry_document(broken)
        self.assertTrue(any("identity" in error.lower() or "id" in error.lower() for error in errors))

    def test_missing_role_is_rejected(self) -> None:
        registry = _registry(
            [_member(member_id="dev-a", role="DEV", source_fp="sha256:" + "aa" * 32,
                     oracle_fp="sha256:" + "bb" * 32)]
        )
        broken = dict(registry)
        member = dict(registry["members"][0])
        member.pop("role")
        broken["members"] = [member]
        errors = validate_registry_document(broken)
        self.assertTrue(any("role" in error.lower() for error in errors))

    def test_missing_attestation_is_rejected(self) -> None:
        registry = _registry(
            [_member(member_id="dev-a", role="DEV", source_fp="sha256:" + "aa" * 32,
                     oracle_fp="sha256:" + "bb" * 32)]
        )
        broken = dict(registry)
        member = dict(registry["members"][0])
        member.pop("attestation")
        broken["members"] = [member]
        errors = validate_registry_document(broken)
        self.assertTrue(any("attestation" in error.lower() or "receipt" in error.lower() for error in errors))


class TestQuarantineNegativeControls(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.dev_bytes = b"synthetic-dev-source-v1"
        self.holdout_bytes = b"synthetic-holdout-source-v1"
        self.dev_fp = fingerprint_bytes(self.dev_bytes)
        self.holdout_fp = fingerprint_bytes(self.holdout_bytes)
        self.oracle_fp = fingerprint_bytes(b"synthetic-oracle")
        exposed = _member(
            member_id="old-exposed",
            role="EXPOSED",
            source_fp=self.dev_fp,
            oracle_fp=self.oracle_fp,
            aliases=["old-exposed-alias"],
            tombstone=_attestation({"id": "old-exposed", "irreversible": True}),
        )
        holdout = _member(
            member_id="eval-fresh",
            role="HOLDOUT",
            source_fp=self.holdout_fp,
            oracle_fp=fingerprint_bytes(b"holdout-oracle"),
            stratum="single_file",
        )
        self.registry = _registry([exposed, holdout])
        self.store = SealedStore(self.root / "sealed")
        self.store.write_member("eval-fresh", {"src.txt": self.holdout_bytes})

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_rejects_alias_of_exposed_as_holdout(self) -> None:
        spoof = _member(
            member_id="new-holdout",
            role="HOLDOUT",
            source_fp=fingerprint_bytes(b"other"),
            oracle_fp=self.oracle_fp,
            aliases=["old-exposed-alias"],
        )
        registry = _registry([self.registry["members"][0], spoof])
        errors = validate_registry_document(registry)
        self.assertTrue(any("alias" in error.lower() or "closure" in error.lower() for error in errors))

    def test_rejects_rename_of_exposed_as_holdout(self) -> None:
        renamed = _member(
            member_id="renamed-holdout",
            role="HOLDOUT",
            source_fp=self.dev_fp,
            oracle_fp=self.oracle_fp,
        )
        registry = _registry([self.registry["members"][0], renamed])
        errors = validate_registry_document(registry)
        self.assertTrue(any("fingerprint" in error.lower() or "closure" in error.lower() or "origin" in error.lower() for error in errors))

    def test_rejects_copied_content_fingerprint(self) -> None:
        copied = _member(
            member_id="copied-holdout",
            role="HOLDOUT",
            source_fp=self.dev_fp,
            oracle_fp=fingerprint_bytes(b"different-oracle"),
        )
        registry = _registry([self.registry["members"][0], copied])
        errors = validate_registry_document(registry)
        self.assertTrue(any("cop" in error.lower() or "fingerprint" in error.lower() or "closure" in error.lower() for error in errors))

    def test_rejects_symlink_escape(self) -> None:
        outside = self.root / "outside.txt"
        outside.write_bytes(self.holdout_bytes)
        escaped = self.store.member_path("eval-fresh") / "link.txt"
        os.symlink(outside, escaped)
        dest = self.root / "workspace"
        with self.assertRaisesRegex(QuarantineError, "symlink"):
            materialize(
                identity="eval-fresh",
                destination=dest,
                registry=self.registry,
                purpose="evaluation",
                store=self.store,
                authority="eval-run-1",
                frozen_manifest={"status": "FROZEN", "subject_sha": "abc" * 8},
            )

    def test_rejects_role_spoofing(self) -> None:
        spoofed = dict(self.registry["members"][0])
        spoofed["role"] = "HOLDOUT"
        registry = _registry([spoofed, self.registry["members"][1]])
        errors = validate_registry_document(registry)
        self.assertTrue(any("spoof" in error.lower() or "tombstone" in error.lower() or "exposed" in error.lower() for error in errors))

    def test_rejects_removed_exposure_tombstone(self) -> None:
        stripped = dict(self.registry["members"][0])
        stripped["exposure_tombstone"] = None
        registry = _registry([stripped, self.registry["members"][1]])
        errors = validate_registry_document(registry)
        self.assertTrue(any("tombstone" in error.lower() for error in errors))

    def test_rejects_absent_receipt(self) -> None:
        with self.assertRaisesRegex(QuarantineError, "receipt|attestation"):
            admit_evaluation(
                "eval-fresh",
                registry=self.registry,
                authority=None,
                frozen_manifest={"status": "FROZEN", "subject_sha": "abc" * 8},
                store=self.store,
            )

    def test_rejects_dev_capture_of_holdout(self) -> None:
        with self.assertRaisesRegex(QuarantineError, "HOLDOUT|capture"):
            guard_capture(task_id="eval-fresh", registry=self.registry)

    def test_rejects_unfrozen_scoring(self) -> None:
        with self.assertRaisesRegex(QuarantineError, "unfrozen"):
            refuse_unfrozen_scoring(
                ["eval-fresh"],
                {"status": "UNFROZEN", "subject_sha": None},
                registry=self.registry,
            )

    def test_captured_development_data_cannot_migrate_to_holdout(self) -> None:
        with self.assertRaisesRegex(QuarantineError, "EXPOSED|migrate|HOLDOUT"):
            promote_to_holdout("old-exposed", registry=self.registry)


class TestQuarantinePositiveControls(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.dev_dir = self.root / "fresh-dev"
        self.dev_dir.mkdir()
        (self.dev_dir / "src.txt").write_bytes(b"fresh-dev-only")
        self.store = SealedStore(self.root / "sealed")
        holdout_fp = fingerprint_bytes(b"authorized-eval")
        oracle_fp = fingerprint_bytes(b"authorized-oracle")
        self.store.write_member("eval-auth", {"src.txt": b"authorized-eval"})
        self.registry = _registry(
            [
                _member(
                    member_id="fresh-dev",
                    role="DEV",
                    source_fp=fingerprint_tree(self.dev_dir),
                    oracle_fp=fingerprint_bytes(b"dev-oracle"),
                ),
                _member(
                    member_id="eval-auth",
                    role="HOLDOUT",
                    source_fp=holdout_fp,
                    oracle_fp=oracle_fp,
                    stratum="single_file",
                ),
            ]
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_fresh_dev_fixture_admits(self) -> None:
        admitted = admit_development(
            "fresh-dev",
            source=self.dev_dir,
            registry=self.registry,
        )
        self.assertEqual(admitted["role"], "DEV")
        dest = self.root / "dev-ws"
        materialize(
            identity="fresh-dev",
            destination=dest,
            registry=self.registry,
            purpose="development",
            store=SealedStore(self.dev_dir.parent),
        )
        self.assertTrue((dest / "src.txt").is_file())

    def test_authorized_synthetic_evaluation_admits(self) -> None:
        admitted = admit_evaluation(
            "eval-auth",
            registry=self.registry,
            authority="eval-run-authorized",
            frozen_manifest={"status": "FROZEN", "subject_sha": "def" * 8},
            store=self.store,
        )
        self.assertEqual(admitted["role"], "HOLDOUT")
        dest = self.root / "eval-ws"
        materialize(
            identity="eval-auth",
            destination=dest,
            registry=self.registry,
            purpose="evaluation",
            store=self.store,
            authority="eval-run-authorized",
            frozen_manifest={"status": "FROZEN", "subject_sha": "def" * 8},
        )
        self.assertEqual((dest / "src.txt").read_bytes(), b"authorized-eval")
        refuse_unfrozen_scoring(
            ["eval-auth"],
            {"status": "FROZEN", "subject_sha": "def" * 8},
            registry=self.registry,
        )


class TestCommittedRegistryCommitments(unittest.TestCase):
    def test_committed_registry_is_loadable_and_unaccepted(self) -> None:
        registry = load_registry(REGISTRY_PATH)
        self.assertEqual(registry["schema"], "aether.corpus-quarantine/1")
        self.assertEqual(registry["holdout_admission"], "UNACCEPTED")
        errors = validate_registry_document(registry)
        self.assertEqual(errors, [])

    def test_old_thirty_are_exposed_not_holdout(self) -> None:
        registry = load_registry(REGISTRY_PATH)
        suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
        exposed = {row["id"] for row in registry["members"] if row["role"] == "EXPOSED"}
        holdout = {row["id"] for row in registry["members"] if row["role"] == "HOLDOUT"}
        old_ids = {task["id"] for task in suite["tasks"]}
        self.assertEqual(exposed, old_ids)
        self.assertEqual(holdout, set())
        self.assertEqual(len(exposed), 30)

    def test_public_commitments_have_no_plaintext_keys(self) -> None:
        raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

        def walk(node: object) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    self.assertNotIn(key, FORBIDDEN_PLAINTEXT_KEYS)
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(raw)

    def test_registry_does_not_embed_old_member_bytes(self) -> None:
        registry_text = REGISTRY_PATH.read_text(encoding="utf-8")
        suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
        for task in suite["tasks"]:
            oracle_path = REPO_ROOT / task["oracle"]["path"]
            if not oracle_path.is_file():
                continue
            text = oracle_path.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                snippet = line.strip()
                if len(snippet) >= 32 and not snippet.startswith("#"):
                    self.assertNotIn(snippet, registry_text)


if __name__ == "__main__":
    unittest.main()
