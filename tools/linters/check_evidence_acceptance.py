#!/usr/bin/env python3
"""Fail closed unless every milestone's evidence has valid independent acceptance.

Two rules keep this gate honest in both directions.

It never accepts a reviewer key that arrives inside the document it
authenticates -- keys come from ``evidence_trust_root.json``, the same registry
the independent verifier uses.

And it recognises *supersession*. When a milestone's evidence has been
re-executed and the successor verifies as ``passed``, the earlier bundle is not
a standing failure: it is history that records an `undeterminable` run, and its
own outcome is left saying exactly that. A successor only supersedes when it
verifies green under the independent verifier *and* pins a commit descended from
the bundle it replaces, so a stale or unrelated bundle cannot excuse anything.
Without this the gate could never go green even after the prescribed repair --
re-executing the evidence -- which would make it a gate nobody can pass rather
than a gate that means something.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_evidence import (  # noqa: E402
    PASSED,
    _registered_key,
    verify_bundle,
    verify_signature_reason,
)

from vanguard.packages.domain.evidence.envelope import acceptance_defects, parse_envelope


def _is_ancestor(older: str, newer: str) -> bool:
    """Whether `older` is an ancestor of `newer` in this repository's history."""
    if not older or not newer or older == newer:
        return False
    result = subprocess.run(
        ["git", "-C", str(_ROOT), "merge-base", "--is-ancestor", older, newer],
        capture_output=True, check=False,
    )
    return result.returncode == 0


def superseding_bundle(produced_path: Path, siblings: list[Path]) -> Path | None:
    """The green successor that replaces this bundle, if one exists."""
    try:
        produced = parse_envelope(json.loads(produced_path.read_text(encoding="utf-8")))
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    commit = str((produced.pins or {}).get("commit") or "")
    for candidate_path in siblings:
        if candidate_path == produced_path:
            continue
        try:
            candidate = parse_envelope(
                json.loads(candidate_path.read_text(encoding="utf-8")))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if candidate.claim != produced.claim:
            continue
        if not _is_ancestor(commit, str((candidate.pins or {}).get("commit") or "")):
            continue
        if verify_bundle(candidate_path).outcome == PASSED:
            return candidate_path
    return None


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
    registered, encoded_key = _registered_key("reviewers", acceptance.producer.key_id)
    if not registered or encoded_key is None:
        errors.append(
            f"reviewer key {acceptance.producer.key_id or '(none)'!r} is not registered "
            f"in the verifier trust root")
    else:
        # One implementation of the signature rule, shared with the verifier.
        # A second copy here could drift from the gate it is supposed to mirror,
        # and a signature format the two disagree about is exactly the gap a
        # forged bundle would be published through.
        reason = verify_signature_reason(acceptance, encoded_key)
        if reason:
            errors.append(f"reviewer signature invalid: {reason}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, default=Path("evidence"))
    args = parser.parse_args()
    bundles = [path for path in sorted(args.evidence_dir.glob("*.json"))
               if not path.name.endswith(".acceptance.json")]
    failures: list[str] = []
    superseded: list[str] = []
    for produced in bundles:
        successor = superseding_bundle(produced, bundles)
        if successor is not None:
            superseded.append(f"{produced.name} -> {successor.name}")
            continue
        acceptance = produced.with_name(produced.name + ".acceptance.json")
        if not acceptance.is_file():
            failures.append(f"{produced.name}: independent acceptance is absent")
            continue
        failures.extend(f"{produced.name}: {error}" for error in verify_acceptance(produced, acceptance))
    for line in superseded:
        print(f"EVIDENCE ACCEPTANCE SUPERSEDED: {line}")
    if failures:
        for failure in failures:
            print(f"EVIDENCE ACCEPTANCE FAIL: {failure}")
        return 1
    print(f"EVIDENCE ACCEPTANCE PASS: {len(bundles) - len(superseded)} bundles "
          f"independently accepted, {len(superseded)} superseded by re-executed evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
