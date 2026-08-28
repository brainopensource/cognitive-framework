#!/usr/bin/env python3
"""Prepare a *candidate* `aether.baseline/1` manifest for CONVERGENCE-BASE-v1.

Owning contract: ADR-0102, WP-C1 (Wave 4).

ADR-0102 records `M-5A-BASE-v2` as `CONTAMINATED_UNPUBLISHED`: a local
lightweight ref, absent from the configured remote, carrying successor treatment
code. It is retained as history and never moved, recreated, or validated by
prose. A reviewed, annotated, remotely resolvable `CONVERGENCE-BASE-v1` with a
signed baseline manifest is the only authorised successor control.

This tool prepares the manifest **inputs**. It deliberately does not:

* run any git command, create a tag, or push one;
* claim the baseline is valid;
* mint the reviewer's signature.

What it does is compute every pin that is derivable from the working tree --
package version, dependency lock digest, schema pins, reducer pins, prohibited
treatment paths, required gates -- and emit a candidate with the git-derived
fields left explicitly unresolved. Creating the annotated tag, filling those
fields, and obtaining an independent countersignature are separate, human,
post-clean-gates steps. `tools/linters/check_baseline_manifest.py` remains the
verifier and will refuse this candidate until those steps are done, which is
the intended behaviour: a candidate is not a baseline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from vanguard.packages.domain.evidence.baseline import (  # noqa: E402
    BASELINE_SCHEMA_VERSION,
    create_signed_baseline_manifest,
)
from cryptography.hazmat.primitives import serialization  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from keygen_evidence_key import load_key  # noqa: E402

#: Placeholder for a field only a git operation can supply. Chosen so it can
#: never be mistaken for a real object id and so the verifier rejects it.
UNRESOLVED = "UNRESOLVED-REQUIRES-ANNOTATED-TAG"

#: Substrate whose semantics must not move between a baseline and its treatment.
#: RF-86 compares against exactly these paths.
PROHIBITED_TREATMENT_PATHS = (
    "vanguard/packages/domain",
    "vanguard/packages/kernel",
    "vanguard/packages/ports",
)

#: Gates that must have receipts before the tag may be created (ADR-0102).
REQUIRED_GATES = ("RF-86", "RF-98", "python-suite", "linters", "uds-af-unix")

#: Reducers whose version determines whether a fold is *this* fold.
REDUCER_SOURCES = (
    "vanguard/packages/domain/ledger/reducer.py",
    "vanguard/packages/domain/ledger/state.py",
    "vanguard/packages/domain/ledger/events.py",
    "vanguard/packages/domain/ledger/agent_view.py",
)


def _digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _digest_file(path: Path) -> str:
    return _digest_bytes(path.read_bytes())


def package_version(root: Path) -> str:
    """Read the single source of package version truth."""
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("version") and "=" in stripped:
            return stripped.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("could not read [project].version from pyproject.toml")


def dependency_lock_digest(root: Path) -> tuple[str, str]:
    """Digest the dependency lock, naming which file was used."""
    for candidate in ("requirements.lock", "uv.lock", "pyproject.toml"):
        path = root / candidate
        if path.is_file():
            return candidate, _digest_file(path)
    raise SystemExit("no dependency lock file found")


def schema_pins(root: Path) -> dict[str, str]:
    """Digest every wire schema. A baseline that does not pin its schemas
    cannot tell a semantic change from a serialisation change."""
    schemas_dir = root / "schemas"
    return {
        path.relative_to(root).as_posix(): _digest_file(path)
        for path in sorted(schemas_dir.rglob("*.schema.json"))
    }


def reducer_pins(root: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for rel in REDUCER_SOURCES:
        path = root / rel
        if path.is_file():
            pins[rel] = _digest_file(path)
    return pins


def prohibited_path_digests(root: Path) -> dict[str, str]:
    """A digest per protected subtree, so contamination is detectable directly.

    RF-86 compares trees, but a reviewer holding only this manifest can still
    tell whether protected substrate moved, without re-running the falsifier.
    """
    digests: dict[str, str] = {}
    for rel in PROHIBITED_TREATMENT_PATHS:
        base = root / rel
        if not base.is_dir():
            continue
        accumulator = hashlib.sha256()
        for path in sorted(base.rglob("*.py")):
            accumulator.update(path.relative_to(root).as_posix().encode("utf-8"))
            accumulator.update(path.read_bytes())
        digests[rel] = "sha256:" + accumulator.hexdigest()
    return digests


def build_candidate(
    root: Path,
    *,
    baseline_id: str,
    tag_object_sha: str,
    commit_sha: str,
    tree_digest: str,
    creator_key_id: str,
    creator_private_key: bytes,
    reviewer_key_id: str,
    reviewer_public_key: str,
) -> dict[str, Any]:
    lock_name, lock_digest = dependency_lock_digest(root)
    manifest = create_signed_baseline_manifest(
        schema_version=BASELINE_SCHEMA_VERSION,
        baseline_id=baseline_id,
        git_tag=baseline_id,
        tag_object_sha=tag_object_sha,
        commit_sha=commit_sha,
        tree_digest=tree_digest,
        package_version=package_version(root),
        dependency_lock_digest=lock_digest,
        schema_pins=schema_pins(root),
        reducer_pins=reducer_pins(root),
        prohibited_treatment_paths=PROHIBITED_TREATMENT_PATHS,
        required_gates=REQUIRED_GATES,
        creator_key_id=creator_key_id,
        creator_private_key=creator_private_key,
        reviewer_key_id=reviewer_key_id,
        reviewer_public_key=reviewer_public_key,
    )

    wire = manifest.to_dict()
    unresolved = sorted(
        field for field in ("tag_object_sha", "commit_sha", "tree_digest")
        if wire.get(field) == UNRESOLVED
    )
    wire["candidate"] = {
        "status": "CANDIDATE_NOT_A_BASELINE",
        "dependencyLockFile": lock_name,
        "prohibitedPathDigests": prohibited_path_digests(root),
        "unresolvedFields": unresolved,
        "reviewerSignature": "ABSENT",
        "remainingSteps": [
            "Run the full declared-dependency Python, TypeScript, linter and "
            "qualified Linux AF_UNIX gates and retain their receipts.",
            "Obtain independent acceptance of the C1 evidence bundles.",
            "Create the ANNOTATED tag CONVERGENCE-BASE-v1 and push it to the "
            "configured remote (a lightweight or unpushed ref fails closed).",
            "Fill tag_object_sha, commit_sha and tree_digest from the pushed tag "
            "and re-sign as creator.",
            "Re-run RF-86 and RF-98 against the tag and attach the receipts.",
            "Have the named reviewer countersign via "
            "countersign_baseline_manifest; the creator cannot mint it.",
            "Verify with tools/linters/check_baseline_manifest.py.",
        ],
    }
    return wire


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a candidate CONVERGENCE-BASE-v1 manifest (never a valid one)")
    parser.add_argument("--baseline-id", default="CONVERGENCE-BASE-v1")
    parser.add_argument("--tag-object-sha", default=UNRESOLVED,
                        help="annotated tag object id, once the tag exists and is pushed")
    parser.add_argument("--commit-sha", default=UNRESOLVED)
    parser.add_argument("--tree-digest", default=UNRESOLVED)
    parser.add_argument("--creator-identity", default="dev-a")
    parser.add_argument("--reviewer-key-id", default="reviewer-pending",
                        help="key id of the independent reviewer who must countersign")
    parser.add_argument("--reviewer-public-key", default="",
                        help="base64 Ed25519 public key of that reviewer")
    parser.add_argument("--creator-key", default="",
                        help="path to the Ed25519 creator key (outside the repo)")
    parser.add_argument(
        "--out",
        default=str(_REPO_ROOT / "evidence" / "baselines" / "CONVERGENCE-BASE-v1.candidate.json"),
        help="output path; deliberately NOT the path the verifier reads",
    )
    args = parser.parse_args()

    try:
        creator_private_key = load_key(
            Path(args.creator_key).expanduser()).private_bytes(
                serialization.Encoding.Raw,
                serialization.PrivateFormat.Raw,
                serialization.NoEncryption())
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(f"       expected an Ed25519 key at {args.creator_key}",
              file=sys.stderr)
        print("       generate one with tools/runners/keygen_evidence_key.py",
              file=sys.stderr)
        return 3

    reviewer_public_key = args.reviewer_public_key
    if not reviewer_public_key:
        # A placeholder that cannot verify: the slot must be filled by a real
        # reviewer before the manifest can pass. Recording an empty slot is
        # more honest than recording the creator's own key.
        import base64

        reviewer_public_key = base64.b64encode(b"\x00" * 32).decode("ascii")
        print("NOTE: no reviewer public key supplied; the reviewer slot is a "
              "non-verifying placeholder and must be filled before review.")

    wire = build_candidate(
        _REPO_ROOT,
        baseline_id=args.baseline_id,
        tag_object_sha=args.tag_object_sha,
        commit_sha=args.commit_sha,
        tree_digest=args.tree_digest,
        creator_key_id=f"{args.creator_identity}-operator",
        creator_private_key=creator_private_key,
        reviewer_key_id=args.reviewer_key_id,
        reviewer_public_key=reviewer_public_key,
    )

    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(wire, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    candidate = wire["candidate"]
    try:
        shown = out_path.relative_to(_REPO_ROOT)
    except ValueError:
        shown = out_path  # a candidate staged outside the repo is still valid
    print(f"wrote {shown}")
    print(f"  status            : {candidate['status']}")
    print(f"  package version   : {wire['package_version']}")
    print(f"  dependency lock   : {candidate['dependencyLockFile']}")
    print(f"  schema pins       : {len(wire['schema_pins'])}")
    print(f"  reducer pins      : {len(wire['reducer_pins'])}")
    print(f"  protected subtrees: {len(candidate['prohibitedPathDigests'])}")
    print(f"  unresolved fields : {candidate['unresolvedFields'] or 'none'}")
    print(f"  reviewer signature: {candidate['reviewerSignature']}")
    print("This is a CANDIDATE. It is not a baseline, and no git operation was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
