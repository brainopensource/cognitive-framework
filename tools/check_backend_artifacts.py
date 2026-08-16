"""Validate the worker/evaluator artifact contract before a release build."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
PLACEHOLDERS = {
    "sha256:" + "0" * 64,
    "sha256:" + "0123456789abcdef" * 4,
    "sha256:" + "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}


def validate(*, release: bool) -> list[str]:
    errors: list[str] = []
    manifest_path = ROOT / "containers/manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest unreadable: {exc}"]

    for role in ("worker", "evaluator"):
        digest = manifest.get(role, {}).get("imageDigest")
        if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
            errors.append(f"{role}.imageDigest is not a sha256 digest")
        elif digest in PLACEHOLDERS:
            errors.append(f"{role}.imageDigest is a build placeholder")

    worker = (ROOT / "containers/worker.Dockerfile").read_text(encoding="utf-8")
    evaluator = (ROOT / "containers/evaluator.Dockerfile").read_text(encoding="utf-8")
    required_worker = ("adduser -u 10001", "USER 10001:10001", "py3-cryptography",
                       "bubblewrap", "ENV PATH=\"/usr/bin:/bin\"")
    required_evaluator = ("adduser -u 10002", "USER 10002:10002", "py3-cryptography",
                          "sealed-oracle", "ENTRYPOINT")
    for text, required, label in ((worker, required_worker, "worker"),
                                  (evaluator, required_evaluator, "evaluator")):
        for marker in required:
            if marker not in text:
                errors.append(f"{label} Dockerfile missing {marker}")

    if release and errors:
        return errors
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()
    errors = validate(release=args.release)
    if errors:
        print("BACKEND ARTIFACT CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1 if args.release else 0
    print("BACKEND ARTIFACT CHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
