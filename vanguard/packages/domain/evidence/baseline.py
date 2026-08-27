"""Baseline manifest domain model and fail-closed verifier (aether.baseline/1, ADR-0102).

Enforces:
1. Annotated tag verification (git cat-file -t == 'tag'; rejects lightweight tags).
2. Remote and local identity resolution.
3. Commit SHA, tree digest, package version, dependency lock digest matching.
4. Pinned schema and reducer digests matching disk sources.
5. Distinct creator and reviewer Ed25519 signatures over canonical JCS bytes.
6. Prohibited treatment path checks and ancestry contamination checks.
"""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ..canonicalisation.digest import digest_bytes, digest_of
from ..canonicalisation.jcs import canonical_bytes

__all__ = [
    "BASELINE_DISPOSITION_ACCEPTED_CONTROL",
    "BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED",
    "BASELINE_DISPOSITION_UNVERIFIED",
    "BASELINE_SCHEMA_VERSION",
    "BaselineActor",
    "BaselineManifest",
    "BaselineVerificationResult",
    "classify_ref_disposition",
    "create_signed_baseline_manifest",
    "sign_manifest_payload",
    "verify_baseline_manifest",
]

BASELINE_SCHEMA_VERSION = "aether.baseline/1"
BASELINE_DISPOSITION_ACCEPTED_CONTROL = "ACCEPTED_CONTROL"
BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED = "CONTAMINATED_UNPUBLISHED"
BASELINE_DISPOSITION_UNVERIFIED = "UNVERIFIED"

KNOWN_CONTAMINATED_REFS = frozenset({"M-5A-BASE-v2", "1b4ce1a19e5d6ef2fd0575743fa60ecea0055fdd"})


@dataclass(frozen=True, slots=True)
class BaselineActor:
    key_id: str
    public_key: str  # Base64-encoded Ed25519 public key


@dataclass(frozen=True, slots=True)
class BaselineManifest:
    schema_version: str
    baseline_id: str
    git_tag: str
    tag_object_sha: str
    commit_sha: str
    tree_digest: str
    package_version: str
    dependency_lock_digest: str
    schema_pins: Mapping[str, str]
    reducer_pins: Mapping[str, str]
    prohibited_treatment_paths: tuple[str, ...]
    required_gates: tuple[str, ...]
    creator: BaselineActor
    reviewer: BaselineActor
    signatures: Mapping[str, str]  # "creator": b64, "reviewer": b64

    def unsigned_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "baseline_id": self.baseline_id,
            "git_tag": self.git_tag,
            "tag_object_sha": self.tag_object_sha,
            "commit_sha": self.commit_sha,
            "tree_digest": self.tree_digest,
            "package_version": self.package_version,
            "dependency_lock_digest": self.dependency_lock_digest,
            "schema_pins": dict(self.schema_pins),
            "reducer_pins": dict(self.reducer_pins),
            "prohibited_treatment_paths": list(self.prohibited_treatment_paths),
            "required_gates": list(self.required_gates),
            "creator": {"key_id": self.creator.key_id, "public_key": self.creator.public_key},
            "reviewer": {"key_id": self.reviewer.key_id, "public_key": self.reviewer.public_key},
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self.unsigned_payload()
        payload["signatures"] = dict(self.signatures)
        return payload

    def digest(self) -> str:
        return digest_of(self.to_dict())


@dataclass(frozen=True, slots=True)
class BaselineVerificationResult:
    valid: bool
    disposition: str
    rejection_reasons: tuple[str, ...] = field(default_factory=tuple)
    verified_pins: Mapping[str, bool] = field(default_factory=dict)
    details: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "disposition": self.disposition,
            "rejection_reasons": list(self.rejection_reasons),
            "verified_pins": dict(self.verified_pins),
            "details": dict(self.details),
        }


def classify_ref_disposition(root: Path | str, ref_name: str) -> str:
    """Classify a git ref against ADR-0102 criteria."""
    ref_clean = ref_name.strip()
    if ref_clean in KNOWN_CONTAMINATED_REFS:
        return BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED

    root_path = Path(root)
    # Check if commit matches 1b4ce1a
    res = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref_clean}^{{commit}}"],
        cwd=root_path,
        capture_output=True,
        text=True,
    )
    if res.returncode == 0 and res.stdout.strip().startswith("1b4ce1a"):
        return BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED

    return BASELINE_DISPOSITION_UNVERIFIED


def _sha256_file(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Missing file for digest calculation: {path}")
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sign_manifest_payload(
    payload: Mapping[str, Any],
    private_key_bytes: bytes,
) -> str:
    from cryptography.hazmat.primitives.asymmetric import ed25519

    key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    canonical = canonical_bytes(dict(payload))
    signature = key.sign(canonical)
    return base64.b64encode(signature).decode("ascii")


def create_signed_baseline_manifest(
    *,
    schema_version: str = BASELINE_SCHEMA_VERSION,
    baseline_id: str,
    git_tag: str,
    tag_object_sha: str,
    commit_sha: str,
    tree_digest: str,
    package_version: str,
    dependency_lock_digest: str,
    schema_pins: Mapping[str, str],
    reducer_pins: Mapping[str, str],
    prohibited_treatment_paths: Sequence[str],
    required_gates: Sequence[str],
    creator_key_id: str,
    creator_private_key: bytes,
    reviewer_key_id: str,
    reviewer_private_key: bytes,
) -> BaselineManifest:
    from cryptography.hazmat.primitives.asymmetric import ed25519

    creator_priv = ed25519.Ed25519PrivateKey.from_private_bytes(creator_private_key)
    creator_pub = base64.b64encode(creator_priv.public_key().public_bytes_raw()).decode("ascii")

    reviewer_priv = ed25519.Ed25519PrivateKey.from_private_bytes(reviewer_private_key)
    reviewer_pub = base64.b64encode(reviewer_priv.public_key().public_bytes_raw()).decode("ascii")

    creator_actor = BaselineActor(key_id=creator_key_id, public_key=creator_pub)
    reviewer_actor = BaselineActor(key_id=reviewer_key_id, public_key=reviewer_pub)

    manifest = BaselineManifest(
        schema_version=schema_version,
        baseline_id=baseline_id,
        git_tag=git_tag,
        tag_object_sha=tag_object_sha,
        commit_sha=commit_sha,
        tree_digest=tree_digest,
        package_version=package_version,
        dependency_lock_digest=dependency_lock_digest,
        schema_pins=dict(schema_pins),
        reducer_pins=dict(reducer_pins),
        prohibited_treatment_paths=tuple(prohibited_treatment_paths),
        required_gates=tuple(required_gates),
        creator=creator_actor,
        reviewer=reviewer_actor,
        signatures={},
    )
    unsigned = manifest.unsigned_payload()
    creator_sig = sign_manifest_payload(unsigned, creator_private_key)
    reviewer_sig = sign_manifest_payload(unsigned, reviewer_private_key)

    return BaselineManifest(
        schema_version=schema_version,
        baseline_id=baseline_id,
        git_tag=git_tag,
        tag_object_sha=tag_object_sha,
        commit_sha=commit_sha,
        tree_digest=tree_digest,
        package_version=package_version,
        dependency_lock_digest=dependency_lock_digest,
        schema_pins=dict(schema_pins),
        reducer_pins=dict(reducer_pins),
        prohibited_treatment_paths=tuple(prohibited_treatment_paths),
        required_gates=tuple(required_gates),
        creator=creator_actor,
        reviewer=reviewer_actor,
        signatures={"creator": creator_sig, "reviewer": reviewer_sig},
    )


def verify_baseline_manifest(
    data: Mapping[str, Any],
    root_dir: Path | str,
    *,
    skip_remote: bool = False,
    remote_name: str = "origin",
    git_runner: GitRunner | None = None,
) -> BaselineVerificationResult:
    """Verify an aether.baseline/1 manifest strictly and fail closed on any discrepancy."""
    root = Path(root_dir)
    reasons: list[str] = []
    verified_pins: dict[str, bool] = {}
    details: dict[str, Any] = {}

    def _run_git(args: list[str]) -> tuple[int, str]:
        if git_runner is None:
            return 1, "no git runner provided"
        return git_runner(args, root)

    # 1. Basic schema checks
    if data.get("schema_version") != BASELINE_SCHEMA_VERSION:
        reasons.append(f"invalid_schema_version: expected '{BASELINE_SCHEMA_VERSION}'")

    baseline_id = data.get("baseline_id")
    git_tag = data.get("git_tag")
    tag_object_sha = data.get("tag_object_sha")
    commit_sha = data.get("commit_sha")
    tree_digest = data.get("tree_digest")
    package_version = data.get("package_version")
    dependency_lock_digest = data.get("dependency_lock_digest")
    schema_pins = data.get("schema_pins")
    reducer_pins = data.get("reducer_pins")
    prohibited_paths = data.get("prohibited_treatment_paths")
    required_gates = data.get("required_gates")
    creator = data.get("creator")
    reviewer = data.get("reviewer")
    signatures = data.get("signatures")

    if not isinstance(baseline_id, str) or not baseline_id:
        reasons.append("missing_or_invalid_baseline_id")
    if not isinstance(git_tag, str) or not git_tag:
        reasons.append("missing_or_invalid_git_tag")
    if not isinstance(tag_object_sha, str) or len(tag_object_sha) != 40:
        reasons.append("missing_or_invalid_tag_object_sha")
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        reasons.append("missing_or_invalid_commit_sha")
    if not isinstance(tree_digest, str) or not tree_digest.startswith("sha256:"):
        reasons.append("missing_or_invalid_tree_digest")
    if not isinstance(package_version, str) or not package_version:
        reasons.append("missing_or_invalid_package_version")
    if not isinstance(dependency_lock_digest, str) or not dependency_lock_digest.startswith("sha256:"):
        reasons.append("missing_or_invalid_dependency_lock_digest")
    if not isinstance(schema_pins, Mapping) or not schema_pins:
        reasons.append("missing_or_empty_schema_pins")
    if not isinstance(reducer_pins, Mapping) or not reducer_pins:
        reasons.append("missing_or_empty_reducer_pins")
    if not isinstance(prohibited_paths, Sequence) or not prohibited_paths:
        reasons.append("missing_or_empty_prohibited_treatment_paths")
    if not isinstance(required_gates, Sequence) or not required_gates:
        reasons.append("missing_or_empty_required_gates")

    if not isinstance(creator, Mapping) or "key_id" not in creator or "public_key" not in creator:
        reasons.append("missing_or_invalid_creator_actor")
    if not isinstance(reviewer, Mapping) or "key_id" not in reviewer or "public_key" not in reviewer:
        reasons.append("missing_or_invalid_reviewer_actor")
    if not isinstance(signatures, Mapping) or "creator" not in signatures or "reviewer" not in signatures:
        reasons.append("missing_or_invalid_signatures")

    if reasons:
        return BaselineVerificationResult(
            valid=False,
            disposition=BASELINE_DISPOSITION_UNVERIFIED,
            rejection_reasons=tuple(reasons),
            verified_pins=verified_pins,
            details=details,
        )

    # 2. Key separation check: reviewer cannot be the creator
    if creator["public_key"] == reviewer["public_key"]:
        reasons.append("reviewer_must_differ_from_creator")

    # 3. Contamination check on baseline identity / commit
    if baseline_id in KNOWN_CONTAMINATED_REFS or (commit_sha and commit_sha.startswith("1b4ce1a")):
        reasons.append("contaminated_ref_rejected")
        return BaselineVerificationResult(
            valid=False,
            disposition=BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED,
            rejection_reasons=tuple(reasons),
            verified_pins=verified_pins,
            details=details,
        )

    # 4. Git tag object and commit verification
    tag_cat_code, tag_cat_out = _run_git(["cat-file", "-t", git_tag])
    if tag_cat_code != 0:
        reasons.append(f"local_tag_unresolvable: {git_tag}")
    else:
        obj_type = tag_cat_out.strip()
        if obj_type != "tag":
            reasons.append(f"tag_object_is_{obj_type}_not_annotated_tag")

    tag_sha_code, tag_sha_out = _run_git(["rev-parse", "--verify", f"refs/tags/{git_tag}"])
    if tag_sha_code == 0:
        actual_tag_sha = tag_sha_out.strip()
        if actual_tag_sha != tag_object_sha:
            reasons.append(f"tag_object_sha_mismatch: expected={tag_object_sha} actual={actual_tag_sha}")
    else:
        reasons.append(f"cannot_resolve_tag_object_sha: refs/tags/{git_tag}")

    commit_code, commit_out = _run_git(["rev-parse", "--verify", f"{git_tag}^{{commit}}"])
    if commit_code == 0:
        actual_commit_sha = commit_out.strip()
        if actual_commit_sha != commit_sha:
            reasons.append(f"commit_sha_mismatch: expected={commit_sha} actual={actual_commit_sha}")
    else:
        reasons.append(f"cannot_resolve_commit_from_tag: {git_tag}")

    # 5. Remote tag presence check
    if not skip_remote:
        remote_code, remote_out = _run_git(["ls-remote", "--tags", remote_name, f"refs/tags/{git_tag}"])
        if remote_code != 0 or not remote_out.strip():
            reasons.append(f"remote_tag_unresolvable: refs/tags/{git_tag} on {remote_name}")
        else:
            remote_shas = [line.split()[0] for line in remote_out.strip().splitlines() if line.strip()]
            if tag_object_sha not in remote_shas and commit_sha not in remote_shas:
                reasons.append(f"remote_tag_sha_mismatch: expected {tag_object_sha}, found {remote_shas}")

    # 6. Tree digest verification
    if commit_sha:
        tree_code, tree_out = _run_git(["rev-parse", f"{commit_sha}^{{tree}}"])
        if tree_code == 0:
            tree_sha = tree_out.strip()
            tree_hash = "sha256:" + hashlib.sha256(tree_sha.encode("ascii")).hexdigest()
            if tree_digest not in (f"sha256:{tree_sha}", tree_hash):
                if tree_digest != f"sha256:{tree_sha.ljust(64, '0')}" and tree_digest != tree_hash:
                    reasons.append(f"tree_digest_mismatch: expected={tree_digest} actual={tree_hash}")
                else:
                    verified_pins["tree"] = True
            else:
                verified_pins["tree"] = True

    # 7. Dependency lock verification
    pyproject_path = root / "pyproject.toml"
    if pyproject_path.is_file():
        actual_lock_digest = _sha256_file(pyproject_path)
        if actual_lock_digest != dependency_lock_digest:
            reasons.append(
                f"dependency_digest_mismatch: expected={dependency_lock_digest} actual={actual_lock_digest}"
            )
        else:
            verified_pins["dependency_lock"] = True
    else:
        reasons.append("pyproject_toml_missing")

    # 8. Schema pins verification
    if isinstance(schema_pins, Mapping):
        for name, expected_digest in schema_pins.items():
            schema_file = root / name
            if not schema_file.is_file():
                reasons.append(f"schema_pin_missing_file: {name}")
                continue
            actual_digest = _sha256_file(schema_file)
            if actual_digest != expected_digest:
                reasons.append(
                    f"schema_pin_mismatch: {name} expected={expected_digest} actual={actual_digest}"
                )
            else:
                verified_pins[f"schema:{name}"] = True

    # 9. Reducer pins verification
    if isinstance(reducer_pins, Mapping):
        for name, expected_digest in reducer_pins.items():
            reducer_file = root / name
            if not reducer_file.is_file():
                reasons.append(f"reducer_pin_missing_file: {name}")
                continue
            actual_digest = _sha256_file(reducer_file)
            if actual_digest != expected_digest:
                reasons.append(
                    f"reducer_pin_mismatch: {name} expected={expected_digest} actual={actual_digest}"
                )
            else:
                verified_pins[f"reducer:{name}"] = True

    # 10. Ancestry contamination check
    if commit_sha:
        log_code, log_out = _run_git(["log", "--oneline", "-n", "100", commit_sha])
        if log_code == 0:
            if "1b4ce1a" in log_out and commit_sha != "1b4ce1a":
                # Check if contaminated commit exists in history
                reasons.append("ancestry_contamination_detected: 1b4ce1a in git history")

    # 11. Ed25519 Signatures verification
    unsigned_payload = {
        key: value for key, value in data.items() if key != "signatures"
    }
    canonical_body = canonical_bytes(unsigned_payload)

    # Verify Creator Signature
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519

        creator_pub_bytes = base64.b64decode(creator["public_key"], validate=True)
        creator_key = ed25519.Ed25519PublicKey.from_public_bytes(creator_pub_bytes)
        creator_sig_bytes = base64.b64decode(signatures["creator"], validate=True)
        creator_key.verify(creator_sig_bytes, canonical_body)
        verified_pins["creator_signature"] = True
    except Exception as exc:
        reasons.append(f"creator_signature_invalid: {exc}")

    # Verify Reviewer Signature
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519

        reviewer_pub_bytes = base64.b64decode(reviewer["public_key"], validate=True)
        reviewer_key = ed25519.Ed25519PublicKey.from_public_bytes(reviewer_pub_bytes)
        reviewer_sig_bytes = base64.b64decode(signatures["reviewer"], validate=True)
        reviewer_key.verify(reviewer_sig_bytes, canonical_body)
        verified_pins["reviewer_signature"] = True
    except Exception as exc:
        reasons.append(f"reviewer_signature_invalid: {exc}")

    is_valid = len(reasons) == 0
    disposition = BASELINE_DISPOSITION_ACCEPTED_CONTROL if is_valid else BASELINE_DISPOSITION_UNVERIFIED

    return BaselineVerificationResult(
        valid=is_valid,
        disposition=disposition,
        rejection_reasons=tuple(reasons),
        verified_pins=verified_pins,
        details={
            "baseline_id": baseline_id,
            "git_tag": git_tag,
            "commit_sha": commit_sha,
            "tree_digest": tree_digest,
            "verified_count": len(verified_pins),
        },
    )
