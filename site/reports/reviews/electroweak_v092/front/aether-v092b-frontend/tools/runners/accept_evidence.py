#!/usr/bin/env python3
"""Create a signed, independent acceptance envelope for an evidence bundle.

The command never changes the produced bundle.  It writes a sibling
``<bundle>.acceptance.json`` and requires an explicit reviewer key.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from vanguard.packages.domain.canonicalisation.jcs import canonical_bytes
from vanguard.packages.domain.evidence.envelope import EvidenceEnvelope, Producer, parse_envelope


def _key_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if len(raw) == 32:
        return raw
    text = raw.decode("ascii").strip()
    try:
        decoded = bytes.fromhex(text)
    except ValueError:
        decoded = base64.b64decode(text, validate=True)
    if len(decoded) != 32:
        raise ValueError("reviewer key must contain exactly 32 Ed25519 private-key bytes")
    return decoded


def create_acceptance(bundle_path: Path, reviewer: str, key_path: Path, key_id: str) -> Path:
    wire = json.loads(bundle_path.read_text(encoding="utf-8"))
    produced = parse_envelope(wire)
    if produced.producer.identity == reviewer:
        raise ValueError("reviewer identity must differ from evidence producer")
    private = ed25519.Ed25519PrivateKey.from_private_bytes(_key_bytes(key_path))
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    acceptance = EvidenceEnvelope(
        claim=f"acceptance:{produced.claim}",
        protocol="aether.evidence.acceptance/1",
        subjects=(produced.digest(),),
        materials=tuple(produced.materials),
        run={"acceptedEvidenceDigest": produced.digest()},
        pins=dict(produced.pins),
        environment={
            "reviewerPublicKey": base64.b64encode(public).decode("ascii"),
        },
        outcome="passed",
        producer=Producer(identity=reviewer, key_id=key_id, role="reviewer"),
    )
    signature = base64.b64encode(private.sign(canonical_bytes(acceptance.body()))).decode("ascii")
    signed = EvidenceEnvelope(
        claim=acceptance.claim,
        protocol=acceptance.protocol,
        subjects=acceptance.subjects,
        materials=acceptance.materials,
        run=acceptance.run,
        pins=acceptance.pins,
        environment=acceptance.environment,
        outcome=acceptance.outcome,
        producer=acceptance.producer,
        artifact_refs=acceptance.artifact_refs,
        detail=acceptance.detail,
        signature=f"ed25519:{signature}",
    )
    output = bundle_path.with_name(bundle_path.name + ".acceptance.json")
    output.write_text(json.dumps(signed.to_wire(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--key", type=Path)
    parser.add_argument("--key-id", default=None)
    args = parser.parse_args()
    key = args.key or Path(os.environ.get("VANGUARD_REVIEWER_KEY", "~/.vanguard/keys")) / f"{args.reviewer}.ed25519"
    try:
        output = create_acceptance(args.bundle.resolve(), args.reviewer, key.expanduser().resolve(), args.key_id or f"{args.reviewer}-key")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
