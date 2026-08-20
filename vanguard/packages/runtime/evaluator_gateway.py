"""Evaluator gateway: the sole legal writer of `VerdictRecorded` (ADR-0076 §5/§6).

`LedgerEmitter` already refuses `VerdictRecorded` from every writer role but
`evaluator_gateway` (`PRIVILEGED_KIND_OWNERS` in `ledger_emitter.py`); this
module is the one call site that holds that facade. It never constructs a
verdict -- the exterior evaluator daemon does that, under its own signature
(`adapters/evaluators/daemon.py`) -- it only ledgers the bound `SignedVerdict`
a `Verdict` already carries, or refuses when there is nothing bound to ledger.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..domain.ledger.events import EventEnvelope
from ..ports.evaluator import Verdict
from .ledger_emitter import LedgerEmitter

__all__ = ["record_verdict", "signed_verdict_payload"]


def signed_verdict_payload(verdict: Verdict) -> Mapping[str, Any] | None:
    """The `SignedVerdict` object exactly as the daemon signed it, or `None`.

    `None` means the daemon never produced a bound, signed body -- no
    evaluator was reachable, or a legacy/unsigned response came back. Nothing
    here repairs that into a pass; the caller gets nothing to ledger.
    """
    if verdict.binding is None or not verdict.signature:
        return None
    return {**dict(verdict.binding), "signature": verdict.signature}


def record_verdict(
    emitter: LedgerEmitter,
    *,
    run_id: str,
    principal: str,
    episode_id: str,
    verdict: Verdict,
) -> EventEnvelope | None:
    """Ledger `VerdictRecorded{SignedVerdict}` for a bound, signed verdict.

    Returns the appended envelope, or `None` when `verdict` carries no bound
    signature -- F1 (a fabricated pass) cannot reach the ledger through this
    call because there is nothing here to fabricate: the payload is always
    the daemon's own signed bytes, never reconstructed from `outcome`/`claims`.
    """
    payload = signed_verdict_payload(verdict)
    if payload is None:
        return None
    return emitter.evaluator_gateway().emit_kind(
        "VerdictRecorded",
        run_id=run_id,
        principal=principal,
        episode_id=episode_id,
        payload={"signedVerdict": dict(payload)},
    )
