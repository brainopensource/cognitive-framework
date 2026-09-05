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

from ..domain.canonicalisation.digest import digest_of
from ..domain.evidence.disposition import SettlementReceipt, TaskDisposition
from ..domain.ledger.events import EventEnvelope
from ..ports.evaluator import Verdict
from .ledger_emitter import LedgerEmitter

__all__ = ["record_verdict", "settlement_payload", "signed_verdict_payload"]


def signed_verdict_payload(verdict: Verdict) -> Mapping[str, Any] | None:
    """The `SignedVerdict` object exactly as the daemon signed it, or `None`.

    `None` means the daemon never produced a bound, signed body -- no
    evaluator was reachable, or a legacy/unsigned response came back. Nothing
    here repairs that into a pass; the caller gets nothing to ledger.
    """
    if verdict.binding is None or not verdict.signature:
        return None
    return {**dict(verdict.binding), "signature": verdict.signature}


def settlement_payload(
    verdict: Verdict,
    *,
    task_id: str,
    terminal_status: str = "",
    executed_test_count: int = 0,
    oracle_digest: str = "",
    verification_subject_digest: str = "",
) -> Mapping[str, Any] | None:
    """Build the honest task-disposition axis from a signed verdict.

    A signed exterior ``pass`` is not published as ``passed`` unless runtime
    can also bind the executed tests, oracle, and verification subject. Missing
    evidence becomes typed missingness; terminal state never supplies it.
    """
    signed = signed_verdict_payload(verdict)
    if signed is None:
        return None
    raw = str(signed.get("verdict", "")).strip().lower()
    bound_oracle = str(signed.get("oracle_digest") or oracle_digest or "")
    bound_subject = str(
        verification_subject_digest or signed.get("subject_digest") or ""
    )
    if raw in {"pass", "passed"} and (
        executed_test_count <= 0 or not bound_oracle or not bound_subject
    ):
        disposition = TaskDisposition.UNDETERMINABLE
        reason = "signed_pass_missing_execution_binding"
    elif raw in {"pass", "passed"}:
        disposition = TaskDisposition.PASSED
        reason = ""
    elif raw in {"fail", "failed"}:
        disposition = TaskDisposition.FAILED
        reason = ""
    else:
        disposition = TaskDisposition.UNDETERMINABLE
        reason = verdict.reason.strip() or "evaluator_inconclusive"
    receipt = SettlementReceipt(
        task_id=task_id,
        disposition=disposition,
        terminal_status=terminal_status,
        oracle_digest=bound_oracle,
        verification_subject_digest=bound_subject,
        executed_test_count=max(0, executed_test_count),
        envelope_digest=digest_of(dict(signed)),
        undeterminable_reason=reason,
    )
    return {**receipt.to_wire(), "signedVerdict": dict(signed)}


def record_verdict(
    emitter: LedgerEmitter,
    *,
    run_id: str,
    principal: str,
    episode_id: str,
    verdict: Verdict,
    task_id: str | None = None,
    terminal_status: str = "",
    executed_test_count: int = 0,
    oracle_digest: str = "",
    verification_subject_digest: str = "",
) -> EventEnvelope | None:
    """Ledger `VerdictRecorded{SignedVerdict}` for a bound, signed verdict.

    Returns the appended envelope, or `None` when `verdict` carries no bound
    signature -- F1 (a fabricated pass) cannot reach the ledger through this
    call because there is nothing here to fabricate: the payload is always
    the daemon's own signed bytes, never reconstructed from `outcome`/`claims`.
    """
    payload = settlement_payload(
        verdict,
        task_id=task_id or run_id,
        terminal_status=terminal_status,
        executed_test_count=executed_test_count,
        oracle_digest=oracle_digest,
        verification_subject_digest=verification_subject_digest,
    )
    if payload is None:
        return None
    return emitter.evaluator_gateway().emit_kind(
        "VerdictRecorded",
        run_id=run_id,
        principal=principal,
        episode_id=episode_id,
        payload=payload,
    )
