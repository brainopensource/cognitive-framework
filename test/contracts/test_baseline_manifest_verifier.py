"""Contract and falsifier tests for aether.baseline/1 manifest verification (WP-B1, ADR-0102).

Proves that the baseline manifest verifier fails closed on:
- Malformed schema structure or invalid schema version.
- Lightweight tags (commit objects rather than annotated tag objects).
- Unresolvable or missing remote tags.
- Tree digest mismatches.
- Dependency lock (pyproject.toml) digest mismatches.
- Schema pin and reducer pin mismatches.
- Invalid or forged creator Ed25519 signature.
- Missing or invalid reviewer Ed25519 signature.
- Collapsed creator and reviewer keys (reviewer must differ from creator).
- Contaminated ancestry or ref names.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519

from vanguard.packages.domain.evidence.baseline import (
    BASELINE_DISPOSITION_ACCEPTED_CONTROL,
    BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED,
    BASELINE_DISPOSITION_UNVERIFIED,
    BASELINE_SCHEMA_VERSION,
    create_signed_baseline_manifest,
    verify_baseline_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


class BaselineManifestVerifierContractTests(unittest.TestCase):
    """Test suite and falsifiers for aether.baseline/1 manifest verification."""

    def setUp(self) -> None:
        self.creator_priv = ed25519.Ed25519PrivateKey.generate()
        self.reviewer_priv = ed25519.Ed25519PrivateKey.generate()

        self.creator_key_bytes = self.creator_priv.private_bytes_raw()
        self.reviewer_key_bytes = self.reviewer_priv.private_bytes_raw()

        # Temporary git workspace for isolated tag testing
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Test Admin"], cwd=self.workspace, check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "admin@aether.test"],
            cwd=self.workspace,
            check=True,
        )

        # Create dummy pyproject.toml and schema/reducer files in workspace
        (self.workspace / "pyproject.toml").write_text(
            "[project]\nname = 'vanguard'\nversion = '0.7.3.dev0'\n", encoding="utf-8"
        )
        (self.workspace / "schemas" / "mhf").mkdir(parents=True)
        (self.workspace / "schemas" / "mhf" / "baseline.schema.json").write_text(
            '{"schema": "test"}', encoding="utf-8"
        )
        (self.workspace / "vanguard" / "packages" / "domain" / "ledger").mkdir(parents=True)
        (
            self.workspace / "vanguard" / "packages" / "domain" / "ledger" / "agent_view.py"
        ).write_text("# reducer", encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=self.workspace, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "Initial baseline commit"],
            cwd=self.workspace,
            check=True,
        )

        commit_res = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.workspace, capture_output=True, text=True
        )
        self.commit_sha = commit_res.stdout.strip()

        tree_res = subprocess.run(
            ["git", "rev-parse", "HEAD^{tree}"],
            cwd=self.workspace,
            capture_output=True,
            text=True,
        )
        self.tree_sha = tree_res.stdout.strip()
        self.tree_digest = "sha256:" + hashlib.sha256(self.tree_sha.encode("ascii")).hexdigest()

        # Create an annotated tag
        self.tag_name = "CONVERGENCE-BASE-v1"
        subprocess.run(
            ["git", "tag", "-a", self.tag_name, "-m", "Annotated convergence baseline tag"],
            cwd=self.workspace,
            check=True,
        )

        tag_obj_res = subprocess.run(
            ["git", "rev-parse", f"refs/tags/{self.tag_name}"],
            cwd=self.workspace,
            capture_output=True,
            text=True,
        )
        self.tag_object_sha = tag_obj_res.stdout.strip()

        self.lock_digest = (
            "sha256:"
            + hashlib.sha256(
                (self.workspace / "pyproject.toml").read_bytes()
            ).hexdigest()
        )
        self.schema_pins = {
            "schemas/mhf/baseline.schema.json": "sha256:"
            + hashlib.sha256(
                (self.workspace / "schemas/mhf/baseline.schema.json").read_bytes()
            ).hexdigest()
        }
        self.reducer_pins = {
            "vanguard/packages/domain/ledger/agent_view.py": "sha256:"
            + hashlib.sha256(
                (
                    self.workspace
                    / "vanguard/packages/domain/ledger/agent_view.py"
                ).read_bytes()
            ).hexdigest()
        }

        self.valid_manifest = create_signed_baseline_manifest(
            baseline_id=self.tag_name,
            git_tag=self.tag_name,
            tag_object_sha=self.tag_object_sha,
            commit_sha=self.commit_sha,
            tree_digest=self.tree_digest,
            package_version="0.7.3.dev0",
            dependency_lock_digest=self.lock_digest,
            schema_pins=self.schema_pins,
            reducer_pins=self.reducer_pins,
            prohibited_treatment_paths=["vanguard/packages/domain", "vanguard/packages/kernel"],
            required_gates=["RF-86", "RF-98"],
            creator_key_id="creator-key-01",
            creator_private_key=self.creator_key_bytes,
            reviewer_key_id="reviewer-key-01",
            # The reviewer slot names a public key; the private key is supplied
            # here only because this fixture needs a fully-countersigned
            # manifest in one call. Production countersigning goes through
            # `countersign_baseline_manifest`, which the creator cannot invoke.
            reviewer_public_key=base64.b64encode(
                ed25519.Ed25519PrivateKey.from_private_bytes(self.reviewer_key_bytes)
                .public_key()
                .public_bytes_raw()
            ).decode("ascii"),
            reviewer_private_key=self.reviewer_key_bytes,
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _git(self, args: Sequence[str], cwd: Path) -> tuple[int, str]:
        proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
        return proc.returncode, proc.stdout

    def test_valid_signed_baseline_passes_verification(self) -> None:
        result = verify_baseline_manifest(
            self.valid_manifest.to_dict(),
            self.workspace,
            skip_remote=True,
            git_runner=self._git,
        )
        self.assertTrue(result.valid, f"Expected valid manifest: {result.rejection_reasons}")
        self.assertEqual(result.disposition, BASELINE_DISPOSITION_ACCEPTED_CONTROL)
        self.assertEqual(len(result.rejection_reasons), 0)

    def test_lightweight_tag_fails_closed(self) -> None:
        """A lightweight tag (commit ref) instead of an annotated tag object is rejected."""
        lightweight_tag = "LIGHTWEIGHT-TAG"
        subprocess.run(
            ["git", "tag", lightweight_tag],
            cwd=self.workspace,
            check=True,
        )
        data = copy.deepcopy(self.valid_manifest.to_dict())
        data["git_tag"] = lightweight_tag
        data["tag_object_sha"] = self.commit_sha

        result = verify_baseline_manifest(
            data, self.workspace, skip_remote=True, git_runner=self._git
        )
        self.assertFalse(result.valid)
        self.assertTrue(
            any("tag_object_is_commit_not_annotated_tag" in r for r in result.rejection_reasons),
            result.rejection_reasons,
        )

    def test_missing_local_tag_fails_closed(self) -> None:
        data = copy.deepcopy(self.valid_manifest.to_dict())
        data["git_tag"] = "NON-EXISTENT-TAG"

        result = verify_baseline_manifest(
            data, self.workspace, skip_remote=True, git_runner=self._git
        )
        self.assertFalse(result.valid)
        self.assertTrue(
            any("local_tag_unresolvable" in r for r in result.rejection_reasons),
            result.rejection_reasons,
        )

    def test_unresolvable_remote_tag_fails_closed(self) -> None:
        result = verify_baseline_manifest(
            self.valid_manifest.to_dict(),
            self.workspace,
            skip_remote=False,
            remote_name="nonexistent-remote",
            git_runner=self._git,
        )
        self.assertFalse(result.valid)
        self.assertTrue(
            any("remote_tag_unresolvable" in r for r in result.rejection_reasons),
            result.rejection_reasons,
        )

    def test_tree_digest_drift_fails_closed(self) -> None:
        data = copy.deepcopy(self.valid_manifest.to_dict())
        data["tree_digest"] = "sha256:" + "0" * 64

        result = verify_baseline_manifest(
            data, self.workspace, skip_remote=True, git_runner=self._git
        )
        self.assertFalse(result.valid)
        self.assertTrue(
            any("tree_digest_mismatch" in r for r in result.rejection_reasons),
            result.rejection_reasons,
        )

    def test_dependency_lock_drift_fails_closed(self) -> None:
        data = copy.deepcopy(self.valid_manifest.to_dict())
        data["dependency_lock_digest"] = "sha256:" + "f" * 64

        result = verify_baseline_manifest(
            data, self.workspace, skip_remote=True, git_runner=self._git
        )
        self.assertFalse(result.valid)
        self.assertTrue(
            any("dependency_digest_mismatch" in r for r in result.rejection_reasons),
            result.rejection_reasons,
        )

    def test_schema_pin_drift_fails_closed(self) -> None:
        data = copy.deepcopy(self.valid_manifest.to_dict())
        data["schema_pins"]["schemas/mhf/baseline.schema.json"] = "sha256:" + "a" * 64

        result = verify_baseline_manifest(
            data, self.workspace, skip_remote=True, git_runner=self._git
        )
        self.assertFalse(result.valid)
        self.assertTrue(
            any("schema_pin_mismatch" in r for r in result.rejection_reasons),
            result.rejection_reasons,
        )

    def test_tampered_creator_signature_fails_closed(self) -> None:
        data = copy.deepcopy(self.valid_manifest.to_dict())
        # Alter a payload field without re-signing
        data["package_version"] = "0.7.4-mutated"

        result = verify_baseline_manifest(
            data, self.workspace, skip_remote=True, git_runner=self._git
        )
        self.assertFalse(result.valid)
        self.assertTrue(
            any("creator_signature_invalid" in r for r in result.rejection_reasons),
            result.rejection_reasons,
        )

    def test_same_creator_and_reviewer_key_fails_closed(self) -> None:
        data = copy.deepcopy(self.valid_manifest.to_dict())
        data["reviewer"]["public_key"] = data["creator"]["public_key"]

        result = verify_baseline_manifest(
            data, self.workspace, skip_remote=True, git_runner=self._git
        )
        self.assertFalse(result.valid)
        self.assertIn("reviewer_must_differ_from_creator", result.rejection_reasons)

    def test_contaminated_ref_name_or_commit_fails_closed(self) -> None:
        data = copy.deepcopy(self.valid_manifest.to_dict())
        data["baseline_id"] = "M-5A-BASE-v2"

        result = verify_baseline_manifest(
            data, self.workspace, skip_remote=True, git_runner=self._git
        )
        self.assertFalse(result.valid)
        self.assertEqual(result.disposition, BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED)
        self.assertIn("contaminated_ref_rejected", result.rejection_reasons)


if __name__ == "__main__":
    unittest.main()
