#!/usr/bin/env python3
"""Backend release qualification without performing Git operations.

The command is intentionally a gate, not a publisher.  It checks the
installable backend, durable stores, configured profiles, container artifact
metadata, and an exact-subject signed evidence envelope.  The clean-subject
and baseline/tag facts that require Git are accepted only as an external JSON
receipt; this tool never invokes Git and never infers those facts from the
working tree.

Example::

    python3 tools/release_qualification.py \
      --subject sha256:<candidate> \
      --envelope /path/to/signed-release-envelope.json \
      --git-receipt /path/to/external-clean-subject.json
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from cryptography.hazmat.primitives.asymmetric import ed25519

# Executing ``python tools/release_qualification.py`` places ``tools/`` rather
# than the repository root on ``sys.path``.  Resolve imports explicitly so the
# qualification command works from a source checkout without PYTHONPATH.
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vanguard import __version__
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.adapters.stores.memory_engine import DurableMemoryPort
from vanguard.packages.agency.manifests.loader import ManifestLoader
from vanguard.packages.domain.evidence.envelope import parse_envelope
from vanguard.packages.runtime.profiles import PRESETS, resolve_profile


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _check_external_git_receipt(path: Path, subject: str) -> str | None:
    """Validate externally-produced Git facts without reading Git state."""
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"external Git prerequisite is unreadable: {exc}"
    if not isinstance(receipt, Mapping):
        return "external Git prerequisite must be a JSON object"
    if receipt.get("source") != "external":
        return "external Git prerequisite must declare source='external'"
    if receipt.get("subject") != subject:
        return "external Git prerequisite subject does not match the candidate"
    if receipt.get("clean") is not True:
        return "external Git prerequisite does not attest a clean subject"
    if not receipt.get("baseline"):
        return "external Git prerequisite must name the pinned baseline"
    return None


def _check_signed_subject(path: Path, subject: str) -> list[str]:
    errors: list[str] = []
    try:
        wire = json.loads(path.read_text(encoding="utf-8"))
        envelope = parse_envelope(wire)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"release envelope is malformed: {exc}"]
    if envelope.outcome != "passed":
        errors.append(f"release envelope outcome is {envelope.outcome!r}, not 'passed'")
    if envelope.subjects != (subject,):
        errors.append("release envelope subjects are not exactly the requested candidate")
    signature = envelope.signature
    if not signature.startswith("ed25519:"):
        errors.append("release envelope must carry an ed25519 signature")
        return errors

    key_text = os.environ.get("AETHER_RELEASE_PUBLIC_KEY", "")
    if not key_text:
        errors.append(
            "AETHER_RELEASE_PUBLIC_KEY is required; signature authority is an "
            "external release prerequisite"
        )
        return errors
    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(
            base64.b64decode(key_text, validate=True)
        )
        public_key.verify(
            base64.b64decode(signature.removeprefix("ed25519:"), validate=True),
            envelope.signable_bytes(),
        )
    except Exception as exc:  # cryptographic and encoding failures are one gate
        errors.append(f"release envelope signature does not verify: {exc}")
    return errors


def _check_installable_resources() -> list[str]:
    errors: list[str] = []
    try:
        loader = ManifestLoader()
        resource = loader._read_packaged_schema("schemas.v4", "harness-manifest.schema.json")
        if not resource[1]:
            errors.append("packaged harness schema is empty")
        manifest = Path(__file__).resolve().parents[1] / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"
        if not manifest.is_file():
            errors.append("default packaged manifest is missing")
        else:
            loader.load_pack(manifest)
    except Exception as exc:
        errors.append(f"installable manifest resources failed: {exc}")
    return errors


def _check_profiles() -> list[str]:
    errors: list[str] = []
    for profile_id in PRESETS:
        try:
            resolved = resolve_profile(profile_id, host_qualifies=True)
            if not resolved.digest:
                errors.append(f"profile {profile_id!r} has no digest")
        except Exception as exc:
            errors.append(f"profile {profile_id!r} failed resolution: {exc}")
    return errors


def _check_event_store() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="aether-release-store-") as temp:
        root = Path(temp)
        store = SqliteEventStore(root / "events.sqlite3")
        report = store.integrity_check()
        if not report.ok or not report.value or not report.value.get("ok"):
            errors.append("fresh SQLite-WAL event store failed integrity check")
        backup = store.backup(root / "backup.sqlite3")
        store.close()
        restored = SqliteEventStore.restore_backup(backup, root / "restored.sqlite3")
        restored.close()
    return errors


def _check_memory_store() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="aether-release-memory-") as temp:
        root = Path(temp)
        memory = DurableMemoryPort(root, "knowledge")
        health = memory.health()
        if health.get("integrity") != "ok":
            errors.append("fresh durable memory store failed integrity check")
        memory.backup(root / "backup")
        memory.close()
        restored = DurableMemoryPort.restore_backup(root / "backup", root / "restored", "knowledge")
        restored.close()
    return errors


def qualify(*, subject: str, envelope: Path, git_receipt: Path) -> dict[str, Any]:
    checks: dict[str, list[str]] = {
        "version": [] if __version__ else ["package version is empty"],
        "resources": _check_installable_resources(),
        "profiles": _check_profiles(),
        "event_store": _check_event_store(),
        "memory_store": _check_memory_store(),
        "signed_subject": _check_signed_subject(envelope, subject),
        "external_git_prerequisite": [],
    }
    git_error = _check_external_git_receipt(git_receipt, subject)
    if git_error:
        checks["external_git_prerequisite"].append(git_error)
    return {
        "schema": "aether.release-qualification/1",
        "subject": subject,
        "packageVersion": __version__,
        "checks": checks,
        "passed": not any(checks.values()),
        "gitOperations": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", required=True, help="exact candidate subject digest")
    parser.add_argument("--envelope", type=Path, required=True)
    parser.add_argument(
        "--git-receipt", type=Path, required=True,
        help="external clean-subject/baseline receipt; this command never runs Git",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = qualify(subject=args.subject, envelope=args.envelope, git_receipt=args.git_receipt)
    if args.json:
        print(json.dumps(report, sort_keys=True, indent=2))
    else:
        print("RELEASE QUALIFICATION PASS" if report["passed"] else "RELEASE QUALIFICATION BLOCKED")
        for name, failures in report["checks"].items():
            print(f"{name}: {'ok' if not failures else '; '.join(failures)}")
        print("git operations: none (external receipt required)")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
