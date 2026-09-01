#!/usr/bin/env python3
"""Producer-side signing and portability repair for `aether.evidence/1` bundles.

Owning contract: ADR-0101, WP-C1 (Wave 3).

Two jobs, both strictly producer-side:

1. **Make artifacts portable.** `--relocate` copies every material whose `ref`
   points outside the repository into a durable, repository-supported directory
   and re-points the reference. A bundle citing `/tmp/.../events.sqlite3` cannot
   be reconstructed by a reviewer, and no countersignature cures that: the bytes
   are simply gone by the time anyone reads it. Digests are re-verified against
   the copy, so relocation cannot silently substitute different bytes.

2. **Sign as the producer.** The signature covers the canonical body minus the
   signature value itself, so a field edited after signing invalidates it.

What this tool deliberately does **not** do:

* It does not create acceptance envelopes. Independent acceptance is a separate
  envelope by a *different* identity, and `accepts()` refuses self-acceptance.
  A producer that could mint its own receipt would make the gate decorative.
* It does not change `outcome` to something better than the run earned. Use
  `--outcome` to record an honest downgrade (e.g. `undeterminable`) together
  with a `--detail` explaining why; there is no flag that upgrades a result.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from vanguard.packages.domain.evidence.envelope import (  # noqa: E402
    EvidenceEnvelope,
    Material,
    Producer,
    parse_envelope,
)
# The signing implementation and the key loader are shared with the builder;
# the signature rule is imported from the verifier itself, so this tool cannot
# self-verify under a laxer rule than the gate applies.
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(_REPO_ROOT / "tools" / "linters"))

from build_evidence_bundle import sign_envelope  # noqa: E402
from keygen_evidence_key import load_key  # noqa: E402
from verify_evidence import verify_signature_reason  # noqa: E402

#: Where relocated artifacts live. Inside the repository, so a reviewer who has
#: the tree has the bytes.
ARTIFACT_ROOT = _REPO_ROOT / "evidence" / "artifacts"


def _digest_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _is_portable(ref: str) -> bool:
    """Whether a reference resolves inside the repository."""
    if not ref:
        return True
    candidate = Path(ref)
    if not candidate.is_absolute():
        return True
    try:
        candidate.resolve().relative_to(_REPO_ROOT)
        return True
    except ValueError:
        return False


def relocate_materials(
    envelope: EvidenceEnvelope, bundle_name: str, *, dry_run: bool = False,
    mark_unresolvable: bool = False,
) -> tuple[EvidenceEnvelope, list[str]]:
    """Copy non-portable materials into the repository and re-point them."""
    target_dir = ARTIFACT_ROOT / bundle_name
    notes: list[str] = []
    new_materials: list[Material] = []
    ref_map: dict[str, str] = {}

    for material in envelope.materials:
        if _is_portable(material.ref):
            new_materials.append(material)
            continue

        source = Path(material.ref)
        if not source.is_file():
            # The bytes are gone. Say so in the envelope rather than leaving a
            # reference that looks resolvable and is not.
            notes.append(
                f"material {material.name!r}: source {material.ref} no longer exists; "
                "reference cleared and marked unresolvable"
            )
            new_materials.append(
                Material(name=material.name, digest=material.digest, ref="",
                         media_type=material.media_type))
            continue

        # Verify before copying. Bytes that no longer match the recorded digest
        # are not this bundle's artifact, whatever the path says.
        actual = _digest_file(source)
        if actual != material.digest:
            if not mark_unresolvable:
                raise SystemExit(
                    f"REFUSED: material {material.name!r} at {material.ref} digests to "
                    f"{actual}, but the bundle records {material.digest}. These are not "
                    "the bytes the claim was made about. Re-run --relocate with "
                    "--mark-unresolvable to record that honestly, or re-execute the run."
                )
            notes.append(
                f"material {material.name!r}: bytes at {material.ref} digest to {actual}, "
                f"not the recorded {material.digest}; reference cleared as unresolvable"
            )
            new_materials.append(
                Material(name=material.name, digest=material.digest, ref="",
                         media_type=material.media_type))
            continue

        dest = target_dir / f"{material.name}{source.suffix or ''}"
        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            if _digest_file(dest) != material.digest:
                dest.unlink(missing_ok=True)
                raise SystemExit(
                    f"REFUSED: material {material.name!r} digest changed during copy")
        rel = dest.relative_to(_REPO_ROOT).as_posix()
        ref_map[material.ref] = rel
        notes.append(f"material {material.name!r}: {material.ref} -> {rel}")
        new_materials.append(
            Material(name=material.name, digest=material.digest, ref=rel,
                     media_type=material.media_type))

    new_refs = tuple(ref_map.get(ref, ref) for ref in envelope.artifact_refs)
    unresolvable = [r for r in new_refs if not _is_portable(r)]
    if unresolvable:
        new_refs = tuple(r for r in new_refs if _is_portable(r))
        notes.extend(f"artifactRef dropped as unresolvable: {r}" for r in unresolvable)

    return (
        EvidenceEnvelope(
            claim=envelope.claim,
            protocol=envelope.protocol,
            subjects=envelope.subjects,
            materials=tuple(new_materials),
            run=envelope.run,
            pins=envelope.pins,
            environment=envelope.environment,
            outcome=envelope.outcome,
            producer=envelope.producer,
            artifact_refs=new_refs,
            detail=envelope.detail,
        ),
        notes,
    )


def rebuild(
    envelope: EvidenceEnvelope,
    *,
    identity: str,
    key_id: str,
    outcome: str | None,
    detail: str | None,
) -> EvidenceEnvelope:
    return EvidenceEnvelope(
        claim=envelope.claim,
        protocol=envelope.protocol,
        subjects=envelope.subjects,
        materials=envelope.materials,
        run=envelope.run,
        pins=envelope.pins,
        environment=envelope.environment,
        outcome=outcome or envelope.outcome,
        producer=Producer(identity=identity, key_id=key_id, role="producer"),
        artifact_refs=envelope.artifact_refs,
        detail=detail if detail is not None else envelope.detail,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sign and repair a producer evidence bundle (never accept one)")
    parser.add_argument("bundle", help="path to the evidence JSON")
    parser.add_argument("--identity", default="dev-a", help="producer identity")
    parser.add_argument("--key-id", default="", help="key id recorded in the envelope")
    parser.add_argument("--producer-key", required=True,
                        help="path to the Ed25519 producer key (outside the repo)")
    parser.add_argument("--relocate", action="store_true",
                        help="copy non-portable materials into the repository")
    parser.add_argument("--outcome", default=None,
                        help="record an honest outcome (passed|failed|undeterminable)")
    parser.add_argument("--detail", default=None, help="explanatory detail")
    parser.add_argument("--mark-unresolvable", action="store_true",
                        help="record materials whose bytes no longer match their digest")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    bundle_path = Path(args.bundle).resolve()
    envelope = parse_envelope(json.loads(bundle_path.read_text(encoding="utf-8")))

    notes: list[str] = []
    if args.relocate:
        envelope, notes = relocate_materials(
            envelope, bundle_path.stem, dry_run=args.dry_run,
            mark_unresolvable=args.mark_unresolvable)

    key_path = Path(args.producer_key).expanduser()
    try:
        private = load_key(key_path)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(f"       expected an Ed25519 key at {key_path}", file=sys.stderr)
        print("       generate one with tools/runners/keygen_evidence_key.py",
              file=sys.stderr)
        return 3

    key_id = args.key_id or f"{args.identity}-operator"
    unsigned = rebuild(
        envelope, identity=args.identity, key_id=key_id,
        outcome=args.outcome, detail=args.detail,
    )
    # One signing implementation, shared with the builder: `ed25519:<base64>`
    # over the canonical body. A hex signature names no algorithm, so the
    # verifier refuses it rather than guessing -- which is why every bundle
    # this tool signed before now reads as `failed`.
    signed = sign_envelope(unsigned, key_path, key_id)

    # Verify what we just wrote, against the same public key a reviewer would use.
    public_b64 = base64.b64encode(
        private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    ).decode("ascii")
    reason = verify_signature_reason(signed, public_b64)
    if reason:
        print(f"ERROR: self-verification of the new signature failed: {reason}",
              file=sys.stderr)
        return 1

    for note in notes:
        print(f"  {note}")
    print(f"  outcome  : {signed.outcome}")
    print(f"  digest   : {signed.digest()}")
    print(f"  producer : {signed.producer.identity} ({key_id})")
    print(f"  publicKey: {public_b64}")

    if args.dry_run:
        print("DRY RUN: nothing written")
        return 0

    bundle_path.write_text(
        json.dumps(signed.to_wire(), sort_keys=True, indent=2) + "\n", encoding="utf-8")
    try:
        shown = bundle_path.relative_to(_REPO_ROOT)
    except ValueError:
        shown = bundle_path  # a bundle staged outside the repo is still signable
    print(f"signed {shown}")
    print("NOTE: this is a PRODUCER signature. Independent acceptance is a "
          "separate envelope by a different identity and is not created here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
