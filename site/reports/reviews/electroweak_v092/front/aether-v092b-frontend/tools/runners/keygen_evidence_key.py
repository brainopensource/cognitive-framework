#!/usr/bin/env python3
"""Generate an Ed25519 signing key for evidence producers and reviewers.

Keys live on disk, outside the repository, because a key committed beside the
artifacts it signs is not an authority: anyone who can read the tree can forge
the signature. The private key is written with owner-only permissions; the
public key is printed for registration in
``tools/linters/evidence_trust_root.json``.

Registration is deliberately a separate, manual act by the verifying lane. A
key that arrives together with the evidence it authenticates proves nothing.

Usage:
    python3 tools/runners/keygen_evidence_key.py --key-id dev-b-evidence-1
    python3 tools/runners/keygen_evidence_key.py --key-id r-1 --out /path/to.key
    python3 tools/runners/keygen_evidence_key.py --key-id r-1 --public-only
"""
from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

DEFAULT_KEY_DIR = Path.home() / ".aether" / "keys"


def public_b64(private: ed25519.Ed25519PrivateKey) -> str:
    return base64.b64encode(
        private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
    ).decode("ascii")


def load_key(path: Path) -> ed25519.Ed25519PrivateKey:
    """Read a raw 32-byte Ed25519 private key, hex or base64 also accepted."""
    raw = path.read_bytes()
    if len(raw) == 32:
        return ed25519.Ed25519PrivateKey.from_private_bytes(raw)
    text = raw.decode("ascii").strip()
    try:
        decoded = bytes.fromhex(text)
    except ValueError:
        decoded = base64.b64decode(text, validate=True)
    if len(decoded) != 32:
        raise ValueError(f"{path} does not contain 32 Ed25519 private-key bytes")
    return ed25519.Ed25519PrivateKey.from_private_bytes(decoded)


def generate(key_id: str, out: Path | None, *, force: bool = False) -> tuple[Path, str]:
    path = out or (DEFAULT_KEY_DIR / f"{key_id}.key")
    if path.exists() and not force:
        # Overwriting a signing key silently invalidates every signature it
        # ever made, so it is never a side effect of running this command.
        return path, public_b64(load_key(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    private = ed25519.Ed25519PrivateKey.generate()
    raw = private.private_bytes(
        serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(raw)
    return path, public_b64(private)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key-id", required=True,
                        help="identifier this key is registered under")
    parser.add_argument("--out", type=Path, default=None,
                        help=f"key path (default {DEFAULT_KEY_DIR}/<key-id>.key)")
    parser.add_argument("--force", action="store_true",
                        help="replace an existing key; invalidates its signatures")
    parser.add_argument("--public-only", action="store_true",
                        help="print the public key of an existing key and exit")
    args = parser.parse_args()

    path = args.out or (DEFAULT_KEY_DIR / f"{args.key_id}.key")
    if args.public_only:
        if not path.is_file():
            print(f"no key at {path}", file=sys.stderr)
            return 1
        print(public_b64(load_key(path)))
        return 0

    path, public = generate(args.key_id, args.out, force=args.force)
    print(f"key-id:    {args.key_id}")
    print(f"key:       {path}")
    print(f"publicKey: {public}")
    print("\nRegister the public key in tools/linters/evidence_trust_root.json "
          "before evidence signed with it can verify.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
