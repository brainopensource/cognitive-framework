#!/usr/bin/env python3
"""Fail closed unless every evidence bundle has valid independent acceptance."""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from vanguard.packages.domain.canonicalisation.jcs import canonical_bytes
from vanguard.packages.domain.evidence.envelope import acceptance_defects, parse_envelope


def verify_acceptance(produced_path: Path, acceptance_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        produced = parse_envelope(json.loads(produced_path.read_text(encoding="utf-8")))
        acceptance = parse_envelope(json.loads(acceptance_path.read_text(encoding="utf-8")))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"{produced_path.name}: malformed evidence or acceptance: {exc}"]
    if not produced.signature:
        errors.append("producer envelope is unsigned")
    if not acceptance.signature:
        errors.append("acceptance envelope is unsigned")
    errors.extend(acceptance_defects(acceptance, produced))
    if acceptance.protocol != "aether.evidence.acceptance/1":
        errors.append("wrong acceptance protocol")
    encoded_key = acceptance.environment.get("reviewerPublicKey")
    if not isinstance(encoded_key, str):
        errors.append("reviewer public key is missing")
    elif not acceptance.signature.startswith("ed25519:"):
        errors.append("unsupported acceptance signature format")
    else:
        try:
            public = ed25519.Ed25519PublicKey.from_public_bytes(base64.b64decode(encoded_key, validate=True))
            public.verify(base64.b64decode(acceptance.signature.removeprefix("ed25519:"), validate=True), canonical_bytes(acceptance.body()))
        except (ValueError, InvalidSignature) as exc:
            errors.append(f"reviewer signature invalid: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, default=Path("docs/03_execution/evidence"))
    args = parser.parse_args()
    failures: list[str] = []
    for produced in sorted(args.evidence_dir.glob("*.json")):
        if produced.name.endswith(".acceptance.json"):
            continue
        acceptance = produced.with_name(produced.name + ".acceptance.json")
        if not acceptance.is_file():
            failures.append(f"{produced.name}: independent acceptance is absent")
            continue
        failures.extend(f"{produced.name}: {error}" for error in verify_acceptance(produced, acceptance))
    if failures:
        for failure in failures:
            print(f"EVIDENCE ACCEPTANCE FAIL: {failure}")
        return 1
    print(f"EVIDENCE ACCEPTANCE PASS: {len(list(args.evidence_dir.glob('*.json')))} bundles independently accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
