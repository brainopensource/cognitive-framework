"""BaaC Zero-State Materialization and Cryptographic Manifest Engine.

Guarantees:
1. Cryptographic zero-state verification against committed sha256 digests.
2. Ephemeral scratch workspace materialization with strict zero-leakage of oracle tests.
3. Clean reset with zero drift from pristine challenge sources.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
from typing import Dict, List, Sequence, Tuple


EXCLUDED_FROM_WORKSPACE = {
    "challenge.yaml",
    "manifest.sha256",
    "oracle",
    "__pycache__",
    ".git",
    ".DS_Store",
    ".pytest_cache",
}


def compute_file_sha256(file_path: Path) -> str:
    """Compute sha256 hex digest of a single file."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_directory_manifest(dir_path: Path) -> Dict[str, str]:
    """Compute relative_path -> sha256 mapping for all files in a directory."""
    manifest: Dict[str, str] = {}
    if not dir_path.exists():
        return manifest

    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", ".venv", ".pytest_cache")]
        for f in sorted(files):
            if f.endswith(".pyc") or f == "manifest.sha256":
                continue
            full_path = Path(root, f)
            rel_path = str(full_path.relative_to(dir_path)).replace("\\", "/")
            manifest[rel_path] = compute_file_sha256(full_path)

    return dict(sorted(manifest.items()))


def parse_manifest_file(manifest_path: Path) -> Dict[str, str]:
    """Parse a committed manifest.sha256 file format: '<sha256>  <relative_path>'."""
    manifest: Dict[str, str] = {}
    if not manifest_path.is_file():
        return manifest

    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            digest, rel_path = parts
            manifest[rel_path.strip().replace("\\", "/")] = digest.strip()

    return manifest


def write_manifest_file(manifest_path: Path, manifest: Dict[str, str]) -> None:
    """Write sorted manifest entries to manifest.sha256."""
    lines = [f"{digest}  {rel_path}" for rel_path, digest in sorted(manifest.items())]
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_challenge_manifest(challenge_dir: Path) -> Path:
    """Generate and write manifest.sha256 for a challenge directory."""
    manifest = compute_directory_manifest(challenge_dir)
    manifest_path = challenge_dir / "manifest.sha256"
    write_manifest_file(manifest_path, manifest)
    return manifest_path


def verify_challenge_zero_state(challenge_dir: Path) -> Tuple[bool, List[str]]:
    """Verify that current challenge files match committed manifest.sha256 exactly."""
    manifest_path = challenge_dir / "manifest.sha256"
    if not manifest_path.is_file():
        return False, [f"Missing manifest.sha256 in {challenge_dir}"]

    expected = parse_manifest_file(manifest_path)
    actual = compute_directory_manifest(challenge_dir)

    drifts: List[str] = []

    # Check for missing or modified files
    for rel_path, expected_digest in expected.items():
        if rel_path not in actual:
            drifts.append(f"Missing file: {rel_path}")
        elif actual[rel_path] != expected_digest:
            drifts.append(f"Content drift in {rel_path} (expected {expected_digest[:8]}, got {actual[rel_path][:8]})")

    # Check for unexpected new files
    for rel_path in actual:
        if rel_path not in expected:
            drifts.append(f"Untracked file in challenge: {rel_path}")

    return len(drifts) == 0, drifts


def materialize_scratch_workspace(challenge_dir: Path, target_scratch_dir: Path) -> Path:
    """Materialize a clean workspace for the agent.
    
    CRITICAL: Never copies oracle/ or internal verification scripts to the agent workspace.
    """
    target_scratch_dir.mkdir(parents=True, exist_ok=True)

    for item in challenge_dir.iterdir():
        if item.name in EXCLUDED_FROM_WORKSPACE:
            continue

        dest = target_scratch_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
        else:
            shutil.copy2(item, dest)

    return target_scratch_dir


def clean_scratch_workspace(scratch_dir: Path) -> None:
    """Safely wipe an ephemeral scratch workspace."""
    if scratch_dir.exists():
        shutil.rmtree(scratch_dir, ignore_errors=True)
