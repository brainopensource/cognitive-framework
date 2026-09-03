#!/usr/bin/env python3
"""Independent milestone evidence verifier (Order 10).

Decides, mechanically and without a human in the loop, whether a milestone's
evidence supports its claim. It is deliberately separate from the producing
runners: it re-derives every judgement from the bundle bytes and refuses
anything it cannot check.

Three outcomes, and they are not interchangeable (ADR-0101 §4):

* ``passed``          -- the bundle claims a pass, the acceptance is valid, and
                         every material this verifier can resolve resolves.
* ``failed``          -- a check this verifier can decide came out negative.
* ``undeterminable``  -- the verifier could not decide: materials are missing,
                         the pins are unreproducible, or the tree was dirty.

``undeterminable`` never satisfies a milestone predicate. It is also not a
failure of the mechanism under test -- it is a failure to observe it, and the
repair is instrumentation, not a weaker threshold.

Usage:
    python3 tools/linters/verify_evidence.py
    python3 tools/linters/verify_evidence.py --milestone M-6.5
    python3 tools/linters/verify_evidence.py --json
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from vanguard.packages.domain.canonicalisation.jcs import canonical_bytes
from vanguard.packages.domain.evidence.envelope import (
    acceptance_defects,
    parse_envelope,
)

#: Where the accepted signing authorities live. A test or an operator may point
#: this elsewhere, but never at a path a producer writes: the whole value of the
#: registry is that adding an authority is a change to the verifying lane.
TRUST_ROOT_PATH = Path(__file__).resolve().with_name("evidence_trust_root.json")

PASSED = "passed"
FAILED = "failed"
UNDETERMINABLE = "undeterminable"


@dataclass
class Verdict:
    """One milestone's verified disposition, with the reasons behind it."""

    bundle: str
    claim: str
    claimed_outcome: str
    outcome: str
    failures: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "bundle": self.bundle,
            "claim": self.claim,
            "claimedOutcome": self.claimed_outcome,
            "verifiedOutcome": self.outcome,
            "failures": self.failures,
            "unresolved": self.unresolved,
            "notes": self.notes,
        }


#: Digest schemes this verifier knows how to re-derive. A bundle that declares
#: none of them records a digest nobody else can reproduce.
_SCHEMES: dict[str, object] = {}


def _digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _candidate_digests(data: bytes) -> dict[str, str]:
    """Every material digest this verifier can independently re-derive."""
    candidates = {"raw-sha256": _digest_bytes(data)}
    try:
        from vanguard.packages.domain.canonicalisation.digest import digest_of

        candidates["jcs-text"] = digest_of({"text": data.decode("utf-8")})
    except (UnicodeDecodeError, ImportError):
        pass
    return candidates


def _bytes_at_commit(commit: str, ref: str) -> bytes | None:
    """Read a material as it was at the pinned commit, not as it is now.

    Evidence pins the tree it was captured from. Hashing today's working copy
    would report a mismatch for every bundle the moment any pinned file is
    edited afterwards, which says nothing about whether the evidence was sound.
    A commit this checkout does not contain is unresolvable, not wrong.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(_ROOT), "show", f"{commit}:{ref}"],
            capture_output=True, check=False,
        )
    except OSError:
        return None
    return result.stdout if result.returncode == 0 else None


def _bytes_at_evidence(
    produced_path: Path, ref: str, artifact_root: str = "",
) -> bytes | None:
    """Resolve a run output that travels with the bundle, and nothing else.

    A producer may run in a temporary workspace, but an evidence envelope may
    only publish bytes that travel with it.  Absolute paths and paths escaping
    the bundle directory are deliberately unresolvable; looking at today's
    checkout would reintroduce the contamination bug this verifier exists to
    prevent.

    Resolution is confined to the bundle's declared ``pins.artifactRoot``.
    Without that fence a producer could satisfy any *source* material -- a
    runtime module, a schema, a falsifier suite -- by dropping a same-named
    file beside the bundle, which is precisely the substitution that resolving
    source refs at the pinned commit exists to prevent.  A bundle that declares
    no artifact root has no portable outputs, so nothing resolves this way.
    """
    if not artifact_root:
        return None
    candidate = Path(ref)
    if candidate.is_absolute():
        return None
    root = produced_path.parent.resolve()
    try:
        fence = (root / Path(artifact_root)).resolve()
        fence.relative_to(root)
        resolved = (root / candidate).resolve()
        resolved.relative_to(fence)
    except ValueError:
        return None
    return resolved.read_bytes() if resolved.is_file() else None


def _trust_root() -> dict:
    """Keys this verifier accepts as authorities, loaded from Lane B's registry.

    The registry lives beside the verifier, not inside the evidence directory a
    producer writes into, so adding an authority is a visible change to the
    verifying lane's own surface rather than a side effect of publishing a
    bundle.
    """
    try:
        return json.loads(TRUST_ROOT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _registered_key(kind: str, key_id: str) -> tuple[bool, str | None]:
    """Return ``(is_registered, public_key_b64)`` for a signing key.

    A registered key with no published public key is *known but uncheckable*;
    the caller must report that as undeterminable rather than as either a pass
    or a forgery.
    """
    entry = (_trust_root().get(kind) or {}).get(key_id)
    if entry is None:
        return False, None
    public = entry.get("publicKey")
    return True, public if isinstance(public, str) and public else None


def verify_signature_reason(envelope, public_key_b64: str | None) -> str | None:
    """Return a failure reason, or None when the signature verifies.

    Public because the acceptance gate must apply *this* rule rather than its
    own copy of it: two implementations of "what counts as a signature" can
    drift, and the gap between them is where an unverifiable bundle gets in.
    """
    signature = envelope.signature
    if not signature:
        return "envelope is unsigned"
    if not public_key_b64:
        return None  # Caller decides whether an unkeyed envelope is checkable.
    if not signature.startswith("ed25519:"):
        return f"unsupported signature format {signature.split(':', 1)[0]!r}"
    try:
        public = ed25519.Ed25519PublicKey.from_public_bytes(
            base64.b64decode(public_key_b64, validate=True)
        )
        public.verify(
            base64.b64decode(signature.removeprefix("ed25519:"), validate=True),
            canonical_bytes(envelope.body()),
        )
    except (ValueError, InvalidSignature) as exc:
        return f"signature does not verify: {exc}"
    return None


def verify_bundle(produced_path: Path) -> Verdict:
    """Verify one evidence bundle and its acceptance record."""
    try:
        produced = parse_envelope(
            json.loads(produced_path.read_text(encoding="utf-8"))
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return Verdict(produced_path.name, "?", "?", FAILED,
                       failures=[f"bundle is malformed: {exc}"])

    verdict = Verdict(
        bundle=produced_path.name,
        claim=produced.claim,
        claimed_outcome=produced.outcome,
        outcome=PASSED,
    )

    # -- the bundle's own claim ------------------------------------------
    if produced.outcome == FAILED:
        verdict.outcome = FAILED
        verdict.failures.append("bundle reports its own outcome as 'failed'")
    elif produced.outcome == UNDETERMINABLE:
        verdict.outcome = UNDETERMINABLE
        verdict.unresolved.append(
            "bundle reports its own outcome as 'undeterminable'; the run was "
            "not observable, so no predicate it feeds is satisfied"
        )

    if not produced.signature:
        verdict.outcome = FAILED
        verdict.failures.append("producer envelope is unsigned")
    else:
        # A signature nobody can re-derive is not a weaker signature; it is an
        # unavailable verifier, and an unavailable verifier never implies a
        # pass. The repair is publishing the producer key, not trusting the
        # bytes because they are present.
        producer_key_id = produced.producer.key_id
        registered, producer_public = _registered_key("producers", producer_key_id)
        if not registered:
            verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
            verdict.unresolved.append(
                f"producer key {producer_key_id or '(none)'!r} is not registered in "
                f"the verifier trust root; the envelope signature cannot be "
                f"attributed to a known producer"
            )
        elif producer_public is None:
            verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
            verdict.unresolved.append(
                f"producer key {producer_key_id!r} publishes no public key; the "
                f"envelope signature is present but cannot be re-derived"
            )
        else:
            reason = verify_signature_reason(produced, producer_public)
            if reason:
                verdict.outcome = FAILED
                verdict.failures.append(f"producer {reason}")

    # -- reproducibility pins --------------------------------------------
    pins = dict(produced.pins or {})
    if pins.get("dirty"):
        verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
        verdict.unresolved.append(
            f"pinned tree {pins.get('tree', '?')} was dirty at capture; the "
            f"recorded commit does not describe the code that ran"
        )
    for required in ("commit", "tree"):
        if not pins.get(required):
            verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
            verdict.unresolved.append(f"bundle does not pin {required}")

    # -- materials, resolved at the pinned commit -------------------------
    commit = str(pins.get("commit") or "")
    for material in produced.materials:
        ref = getattr(material, "ref", "") or ""
        if not ref:
            verdict.unresolved.append(
                f"material {material.name!r} carries a digest but no ref; its "
                f"bytes cannot be located to re-derive the digest"
            )
            verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
            continue
        if not commit:
            verdict.unresolved.append(
                f"material {material.name!r} cannot be resolved: no pinned commit"
            )
            verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
            continue
        # Source materials are resolved from the pinned commit.  Portable run
        # outputs use an evidence-local relative ref because they did not exist
        # when the runtime commit was created.  Never fall back to the current
        # checkout: that would let a later edit satisfy an old claim.
        data = _bytes_at_commit(commit, ref)
        if data is None:
            try:
                data = _bytes_at_evidence(
                    produced_path, ref, str(pins.get("artifactRoot") or "")
                )
            except OSError:
                data = None
        if data is None:
            verdict.unresolved.append(
                f"material {material.name!r} ref {ref!r} does not resolve at "
                f"pinned commit {commit[:12]}"
            )
            verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
            continue
        candidates = _candidate_digests(data)
        if material.digest in candidates.values():
            continue
        declared = str(getattr(material, "scheme", "") or "")
        if declared and declared in candidates:
            # The bundle said how it hashed, and the bytes do not match. That
            # is a decidable negative: the material has changed.
            verdict.outcome = FAILED
            verdict.failures.append(
                f"material {material.name!r} digest mismatch at pinned commit "
                f"{commit[:12]} under declared scheme {declared!r}: bundle "
                f"records {material.digest}, bytes hash to {candidates[declared]}"
            )
        else:
            # The bundle did not record how the digest was computed, so a
            # mismatch under a scheme this verifier guessed is not evidence of
            # anything. Undeterminable is the honest answer, and the repair is
            # a uniformly content-addressed material (Order 9), not a looser
            # comparison here.
            verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
            verdict.unresolved.append(
                f"material {material.name!r} records no digest scheme and "
                f"matches none this verifier can re-derive; its integrity "
                f"cannot be independently checked"
            )

    # Order 9 repeats key identity claims in both pins and materials.  The
    # material bytes are authoritative; the duplicate fields catch stale or
    # mis-bound runtime/pack/schema/config/workload claims.
    materials_by_name = {str(material.name): material for material in produced.materials}
    pin_bindings = {
        "runtimeDigest": "runtime",
        "packDigest": "pack",
        "configurationDigest": "configuration",
        "workloadDigest": "workload",
        "reportDigest": "falsifier_report",
    }
    schema_pins = pins.get("schemaDigests") or {}
    if isinstance(schema_pins, dict):
        pin_bindings.update({str(key): str(key) for key in schema_pins})
    for pin_name, material_name in pin_bindings.items():
        if pin_name not in pins:
            continue
        material = materials_by_name.get(material_name)
        if material is None:
            verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
            verdict.unresolved.append(
                f"pin {pin_name!r} has no matching material {material_name!r}")
        elif str(getattr(material, "digest", "")) != str(pins[pin_name]):
            verdict.outcome = FAILED
            verdict.failures.append(
                f"pin {pin_name!r} does not match material {material_name!r}")

    # A tree pin must describe the pinned commit whenever that commit is
    # available locally.  An unknown commit remains unresolvable; it cannot
    # silently pass as a clean subject.
    if commit:
        try:
            tree_proc = subprocess.run(
                ["git", "-C", str(_ROOT), "rev-parse", f"{commit}^{{tree}}"],
                capture_output=True, text=True, check=False,
            )
            if tree_proc.returncode == 0 and pins.get("tree") != tree_proc.stdout.strip():
                verdict.outcome = FAILED
                verdict.failures.append("tree pin does not match the pinned commit")
        except OSError:
            pass

    for ref in produced.artifact_refs:
        if Path(str(ref)).is_absolute():
            verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
            verdict.unresolved.append(f"artifactRef {ref!r} is an absolute, non-portable path")

    # -- independent acceptance -------------------------------------------
    acceptance_path = produced_path.with_name(produced_path.name + ".acceptance.json")
    if not acceptance_path.is_file():
        verdict.outcome = FAILED
        verdict.failures.append("no independent acceptance record is present")
        return verdict

    try:
        acceptance = parse_envelope(
            json.loads(acceptance_path.read_text(encoding="utf-8"))
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        verdict.outcome = FAILED
        verdict.failures.append(f"acceptance record is malformed: {exc}")
        return verdict

    if acceptance.protocol != "aether.evidence.acceptance/1":
        verdict.outcome = FAILED
        verdict.failures.append(
            f"acceptance protocol is {acceptance.protocol!r}, not "
            f"'aether.evidence.acceptance/1'"
        )

    for defect in acceptance_defects(acceptance, produced):
        verdict.outcome = FAILED
        verdict.failures.append(f"acceptance: {defect}")

    # The reviewer's key is taken from Lane B's registry, never from the
    # acceptance itself. A key that first appears inside the document it
    # authenticates establishes nothing: whoever can write the document can
    # mint the keypair, and two distinct identity strings signed by two
    # freshly minted keys are one authority wearing two names.
    claimed_key = acceptance.environment.get("reviewerPublicKey")
    reviewer_key_id = acceptance.producer.key_id
    registered, reviewer_key = _registered_key("reviewers", reviewer_key_id)
    if not registered:
        verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
        verdict.unresolved.append(
            f"reviewer key {reviewer_key_id or '(none)'!r} is not registered in the "
            f"verifier trust root; this acceptance is signed by an unvetted "
            f"authority and cannot be treated as independent"
        )
    elif reviewer_key is None:
        verdict.outcome = _weaken(verdict.outcome, UNDETERMINABLE)
        verdict.unresolved.append(
            f"reviewer key {reviewer_key_id!r} publishes no public key; the "
            f"acceptance signature cannot be re-derived"
        )
    else:
        if isinstance(claimed_key, str) and claimed_key and claimed_key != reviewer_key:
            verdict.outcome = FAILED
            verdict.failures.append(
                f"acceptance carries a reviewer public key that is not the one "
                f"registered for {reviewer_key_id!r}; the signer is not the "
                f"registered reviewer"
            )
        reason = verify_signature_reason(acceptance, reviewer_key)
        if reason:
            verdict.outcome = FAILED
            verdict.failures.append(f"acceptance {reason}")

    return verdict


def _weaken(current: str, proposed: str) -> str:
    """Move toward the weaker disposition; never upgrade toward `passed`."""
    order = {PASSED: 2, UNDETERMINABLE: 1, FAILED: 0}
    return current if order[current] <= order[proposed] else proposed


def verify_all(evidence_dir: Path) -> list[Verdict]:
    return [
        verify_bundle(path)
        for path in sorted(evidence_dir.glob("*.json"))
        if not path.name.endswith(".acceptance.json")
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path,
                        default=_ROOT / "evidence")
    parser.add_argument("--milestone", default="",
                        help="verify only bundles whose filename starts with this")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable verdicts")
    parser.add_argument("--trust-root", type=Path, default=None,
                        help="registry of accepted producer/reviewer keys")
    args = parser.parse_args()

    if args.trust_root is not None:
        global TRUST_ROOT_PATH
        TRUST_ROOT_PATH = args.trust_root.resolve()

    verdicts = [
        v for v in verify_all(args.evidence_dir)
        if not args.milestone or v.bundle.startswith(args.milestone)
    ]

    if args.json:
        print(json.dumps([v.to_dict() for v in verdicts], indent=2, sort_keys=True))
    else:
        for verdict in verdicts:
            print(f"{verdict.outcome.upper():16s} {verdict.bundle}  ({verdict.claim})")
            for failure in verdict.failures:
                print(f"    FAIL   {failure}")
            for unresolved in verdict.unresolved:
                print(f"    UNDET  {unresolved}")

    passed = sum(1 for v in verdicts if v.outcome == PASSED)
    summary = f"EVIDENCE VERIFIER: {passed}/{len(verdicts)} bundles verify as passed"
    if args.json:
        # stdout must stay parseable when --json is asked for; a human summary
        # appended after the array made the output invalid JSON, so the one
        # consumer the flag exists for could not read it.
        print(summary, file=sys.stderr)
    else:
        print(f"\n{summary}")
    return 0 if verdicts and all(v.outcome == PASSED for v in verdicts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
