"""Offline Ed25519 sealing and verification for M-8 evidence bundles."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from vanguard.packages.runtime.root import canonical_bytes

__all__ = ["CredentialLeakError", "bundle_digest", "canonical_bundle_bytes", "sign_bundle", "seal_bundle", "verify_bundle"]

MANDATORY_FIELDS = frozenset({"schema", "run_id", "subject_sha", "canary_manifest_digest", "records", "aggregate_lift", "timestamp", "signer_id"})
_CREDENTIAL = re.compile(r"(?:OPENROUTER_API_KEY|sk-or-v1-[A-Za-z0-9]{16,}|-----BEGIN .*PRIVATE KEY-----)")


class CredentialLeakError(ValueError):
    """Bundle data contains a provider credential or private-key material."""


def _scan(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    if _CREDENTIAL.search(text):
        raise CredentialLeakError("credential-like material is not admissible in an evidence bundle")


def _body(bundle: dict[str, Any]) -> dict[str, Any]:
    body = dict(bundle)
    body.pop("bundle_digest", None)
    body.pop("bundleDigest", None)
    return body


def _validate(bundle: dict[str, Any]) -> None:
    missing = sorted(MANDATORY_FIELDS - bundle.keys())
    if missing:
        raise ValueError("bundle missing mandatory fields: " + ", ".join(missing))
    if not isinstance(bundle["records"], list):
        raise ValueError("bundle records must be a list")
    _scan(bundle)


def canonical_bundle_bytes(bundle: dict[str, Any]) -> bytes:
    """Return RFC 8785 bytes from the single runtime/domain authority."""
    _validate(bundle)
    return canonical_bytes(_body(bundle))


def bundle_digest(bundle: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_bundle_bytes(bundle)).hexdigest()


def _load_private(path: str | Path) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(Path(path).read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError("key path must contain an Ed25519 private key")
    return key


def sign_bundle(bundle: dict[str, Any], key_path: str | Path, output_dir: str | Path) -> tuple[Path, Path]:
    """Write bundle.json and a raw detached bundle.sig; never creates key material."""
    _validate(bundle)
    sealed = _body(bundle)
    sealed["bundle_digest"] = bundle_digest(bundle)
    signature = _load_private(key_path).sign(bytes.fromhex(sealed["bundle_digest"].split(":", 1)[1]))
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    bundle_path = destination / "bundle.json"
    signature_path = destination / "bundle.sig"
    bundle_path.write_text(json.dumps(sealed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    signature_path.write_bytes(signature)
    return bundle_path, signature_path


seal_bundle = sign_bundle


def verify_bundle(bundle: dict[str, Any], signature: bytes | str | Path, public_key: Ed25519PublicKey | bytes) -> bool:
    """Verify the detached signature without network access or a private key."""
    try:
        _validate(bundle)
        expected = bundle_digest(bundle)
        claimed = bundle.get("bundle_digest", bundle.get("bundleDigest"))
        if claimed is not None and claimed != expected:
            return False
        sig = Path(signature).read_bytes() if isinstance(signature, Path) else (base64.b64decode(signature) if isinstance(signature, str) else signature)
        key = public_key if isinstance(public_key, Ed25519PublicKey) else Ed25519PublicKey.from_public_bytes(public_key)
        key.verify(sig, bytes.fromhex(expected.split(":", 1)[1]))
        return True
    except (InvalidSignature, OSError, ValueError, TypeError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--key-path", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sign_bundle(json.loads(args.bundle.read_text(encoding="utf-8")), args.key_path, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
