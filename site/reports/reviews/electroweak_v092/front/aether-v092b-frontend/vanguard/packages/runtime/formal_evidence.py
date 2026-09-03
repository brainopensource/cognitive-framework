"""M-5b signed verdict evidence (`B-M5B`).

The SAT pack already proves a *result*: an exterior oracle accepted a complete
assignment it did not search for.  That is not yet **evidence**.  Evidence is a
bundle a second reader can check without trusting this process:

* the pinned formula, witness and oracle bytes it was computed over;
* the exact JCS body the **evaluator daemon** signed, and its Ed25519
  signature -- the runtime never constructs a verdict, it only carries one;
* the run's own terminal truth, taken from the ledger rather than asserted.

The third item is the one most easily lost.  A run that abandoned and a run
that completed can both carry a passing witness verdict, because the two axes
are different: `RunTermination` is the run axis and the evaluator owns the
evaluation axis (`agency/episode/state.py`).  Folding them -- reporting
`COMPLETED` because the witness held -- would turn an interrupted M-5b run
into a generality claim.  So the bundle carries both, refuses to be built with
a terminal status the ledger does not show, and marks itself
non-promotable unless *both* axes are clean.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from ..domain.canonicalisation.digest import digest_of
from ..domain.canonicalisation.jcs import canonical_bytes
from ..ports.evaluator import Verdict

__all__ = [
    "TERMINAL_COMPLETED",
    "TERMINAL_ABANDONED",
    "FormalVerdictBundle",
    "build_bundle",
    "terminal_status_from_events",
    "verify_bundle",
]

#: The two terminal outcomes M-5b distinguishes.  `resolved` is the payload
#: spelling `session.py` writes for `RunTermination.COMPLETED`/`ABSTAINED`;
#: everything else -- abandoned, cancelled, budget exhausted, instrument or
#: runtime error -- is *not* a completed run and must never be recorded as one.
TERMINAL_COMPLETED = "completed"
TERMINAL_ABANDONED = "abandoned"

_TERMINAL_KINDS = ("EpisodeCompleted", "RunCompleted", "RunAborted", "RunFailed", "RunRecovered")
_RESOLVED_PAYLOADS = frozenset({"resolved", "completed", "abstained"})


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _payload(event: Any) -> Mapping[str, Any]:
    payload = getattr(event, "payload", None)
    if payload is None and isinstance(event, Mapping):
        payload = event.get("payload", event)
    return payload if isinstance(payload, Mapping) else {}


def _kind(event: Any) -> str:
    payload = _payload(event)
    kind = getattr(event, "kind", None) or payload.get("kind")
    if kind is None and isinstance(event, Mapping):
        kind = event.get("kind")
    return str(kind or "")


def terminal_status_from_events(events: Iterable[Any]) -> str:
    """Fold the run's terminal truth out of its own durable events.

    A run with no terminal event has not ended; that is `abandoned` here
    because M-5b evidence is only ever read after the run is over, so a
    missing terminal record means the run stopped without saying so.
    """
    status = TERMINAL_ABANDONED
    for event in events:
        kind = _kind(event)
        if kind not in _TERMINAL_KINDS:
            continue
        payload = _payload(event)
        outcome = payload.get("outcome") or payload.get("status") or getattr(event, "reason", "")
        status = (TERMINAL_COMPLETED if str(outcome) in _RESOLVED_PAYLOADS
                  else str(outcome or kind))
    return status


@dataclass(frozen=True, slots=True)
class FormalVerdictBundle:
    """One M-5b task's independently checkable evidence."""

    task_id: str
    formula_digest: str
    witness_digest: str
    oracle_digest: str
    registry_digest: str
    verdict: str            # "pass" | "fail" | "inconclusive" (daemon-reduced)
    signed_body: Mapping[str, Any]
    signature: str
    key_id: str
    terminal_status: str    # ledger truth, never the evaluator's opinion
    signature_verified: bool = False
    artifacts_bound: bool = False

    @property
    def signed(self) -> bool:
        return bool(self.signature and self.key_id and self.signed_body)

    @property
    def promotable(self) -> bool:
        """Both axes clean, and the pass actually carries a signature.

        An unsigned `pass` is an assertion by whoever is reporting it.
        """
        return (self.signed and self.signature_verified and self.artifacts_bound
                and self.verdict == "pass"
                and self.terminal_status == TERMINAL_COMPLETED)

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskId": self.task_id,
            "formulaDigest": self.formula_digest,
            "witnessDigest": self.witness_digest,
            "oracleDigest": self.oracle_digest,
            "registryDigest": self.registry_digest,
            "verdict": self.verdict,
            "signedBody": dict(self.signed_body),
            "signature": self.signature,
            "keyId": self.key_id,
            "terminalStatus": self.terminal_status,
            "signed": self.signed,
            "signatureVerified": self.signature_verified,
            "artifactsBound": self.artifacts_bound,
            "promotable": self.promotable,
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())


def _registry_task(registry: Mapping[str, Any], task_id: str) -> Mapping[str, Any]:
    for task in registry.get("tasks", ()):
        if isinstance(task, Mapping) and task.get("id") == task_id:
            return task
    raise ValueError(f"task {task_id!r} is not in the pinned registry")


def build_bundle(
    *,
    task_id: str,
    pack_root: Path | str,
    registry: Mapping[str, Any],
    verdict: Verdict,
    events: Iterable[Any],
    oracle_path: Path | str,
    witness_path: Path | str,
    witness_role: str,
    public_key: bytes,
) -> FormalVerdictBundle:
    """Assemble evidence from pinned bytes, a daemon verdict, and the ledger.

    Every digest is recomputed from the bytes on disk and checked against the
    registry pin.  A drifted formula, witness or oracle raises rather than
    producing a bundle: the alternative is evidence that records the digest of
    something other than what was graded.
    """
    root = Path(pack_root)
    task = _registry_task(registry, task_id)

    formula_digest = _sha256((root / str(task["formula"])).read_bytes())
    actual_witness = Path(witness_path)
    witness_digest = _sha256(actual_witness.read_bytes())
    oracle_digest = _sha256(Path(oracle_path).read_bytes())
    if formula_digest != task.get("formulaDigest"):
        raise ValueError("formula bytes drifted from the pinned registry digest")
    if witness_role == "positive":
        if witness_digest != task.get("positiveWitnessDigest"):
            raise ValueError("witness bytes drifted from the pinned registry digest")
    elif witness_role != "negative" or not task.get("negativeVector"):
        raise ValueError("witness role must name a registered positive or negative vector")
    if oracle_digest != registry.get("oracleDigest"):
        raise ValueError("oracle bytes drifted from the pinned registry digest")

    binding = verdict.binding if isinstance(verdict.binding, Mapping) else None
    signature = verdict.signature or ""
    key_id = verdict.signer_key_id or (str(binding.get("key_id")) if binding else "")
    signature_verified = False
    if binding and signature and key_id and key_id == str(binding.get("key_id", "")):
        try:
            import base64
            from cryptography.hazmat.primitives.asymmetric import ed25519

            key = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
            key.verify(base64.b64decode(signature, validate=True), canonical_bytes(dict(binding)))
            signature_verified = True
        except Exception:
            signature_verified = False
    artifacts = binding.get("artifact_digests") if binding else None
    artifacts_bound = bool(
        isinstance(artifacts, Mapping)
        and artifacts.get("formula") == formula_digest
        and artifacts.get("witness") == witness_digest
        and artifacts.get("oracle") == oracle_digest
    )
    reduced = str(binding.get("verdict")) if signature_verified and binding else "inconclusive"
    if reduced not in {"pass", "fail", "inconclusive"}:
        reduced = "inconclusive"
    return FormalVerdictBundle(
        task_id=task_id,
        formula_digest=formula_digest,
        witness_digest=witness_digest,
        oracle_digest=oracle_digest,
        registry_digest=digest_of(dict(registry)),
        verdict=reduced,
        signed_body=dict(binding) if binding else {},
        signature=signature,
        key_id=key_id,
        terminal_status=terminal_status_from_events(events),
        signature_verified=signature_verified,
        artifacts_bound=artifacts_bound,
    )


def verify_bundle(bundle: FormalVerdictBundle, public_key: bytes) -> bool:
    """Re-check the daemon's signature over the exact body it signed.

    This verifies; it cannot sign.  The evaluator's *private* key never
    reaches the runtime, so nothing here can manufacture the signature it is
    checking -- which is the whole point of an exterior judge (I-5).  The
    signed bytes come from the same domain JCS reader the daemon used, not
    from a second canonicaliser that could disagree with it.
    """
    if not bundle.signed:
        return False
    try:
        import base64

        from cryptography.hazmat.primitives.asymmetric import ed25519

        key = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
        key.verify(base64.b64decode(bundle.signature, validate=True),
                   canonical_bytes(dict(bundle.signed_body)))
        artifacts = bundle.signed_body.get("artifact_digests")
        return bool(
            bundle.key_id == bundle.signed_body.get("key_id")
            and isinstance(artifacts, Mapping)
            and artifacts.get("formula") == bundle.formula_digest
            and artifacts.get("witness") == bundle.witness_digest
            and artifacts.get("oracle") == bundle.oracle_digest
        )
    except Exception:
        return False
