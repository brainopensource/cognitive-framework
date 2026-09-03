"""Canonical vg.4 RuntimeService wire-contract vocabulary and frame validation.

Mirrors ``schemas/v4/runtime-service.schema.json`` in hand-written Python so
``RuntimeService`` can reject malformed frames, unknown commands, and unknown
fields *before* they touch the command inbox or ledger, without depending on
cross-file JSON-Schema ``$ref`` resolution (the ``referencing`` package that
``jsonschema`` needs for that is not present in every environment this runs
in). ``ERROR_CODES`` is the single vocabulary shared, byte-for-byte, with
``@vanguard/client-core``'s ``ClientFailure.code`` (TypeScript) and the
``ErrorCode`` enum in the schema file. The tables below are the
Python half of a single frozen contract: they are checked field-for-field
against ``schemas/v4/runtime-service.schema.json`` by
``test/contracts/test_runtime_service_contract_parity.py``, so the mirror
cannot drift from the schema. A shared corpus of golden/negative vectors under
``schemas/v4/vectors/runtime-service/`` proves the Python and TypeScript
readers agree (see ``test/contracts/test_runtime_service_vectors.py`` and
``client-core/test/runtime-service-vectors.test.ts``).

Owning contract: ADR-0101, ADR-0103, docs/_archive/reviews/frontend/integration_plan.md §4.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

# -- Canonical error vocabulary (integration_plan.md §4.5) -------------------

ERROR_CODES: frozenset[str] = frozenset(
    {
        "invalid_request",
        "unauthenticated",
        "permission_denied",
        "not_found",
        "conflict",
        "incompatible_version",
        "frame_too_large",
        "rate_limited",
        "not_available",
        "internal",
    }
)

#: Codes the service may retry-hint by default when a handler does not say otherwise.
_DEFAULT_RETRYABLE = frozenset({"conflict", "rate_limited", "not_available"})


class ContractError(ValueError):
    """A command/frame failed contract validation or a handler-level rule.

    Carries a canonical ``code`` so ``RuntimeService`` never has to guess one
    from free-text exception messages.
    """

    def __init__(self, code: str, message: str, *, retryable: bool | None = None) -> None:
        if code not in ERROR_CODES:
            raise ValueError(f"unknown canonical error code {code!r}")
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable if retryable is not None else (code in _DEFAULT_RETRYABLE)


class NotFoundError(ContractError):
    def __init__(self, message: str) -> None:
        super().__init__("not_found", message, retryable=False)


class ConflictError(ContractError):
    def __init__(self, message: str) -> None:
        super().__init__("conflict", message, retryable=True)


class UnauthenticatedError(ContractError):
    """The caller's identity or key could not be established."""

    def __init__(self, message: str) -> None:
        super().__init__("unauthenticated", message, retryable=False)


class PermissionDeniedError(ContractError):
    """Identity established, but this request is not authorised.

    Distinct from ``UnauthenticatedError`` on purpose: a failed signature over a
    *registered* key is an authorisation failure and must not read as "log in
    again", while an unknown key ID never reached authorisation at all.
    """

    def __init__(self, message: str) -> None:
        super().__init__("permission_denied", message, retryable=False)


class NotAvailableError(ContractError):
    """A required capability or verifier is not available.

    Never a pass. A verifier that cannot run leaves the request undecided, and
    an undecided privileged request fails closed.
    """

    def __init__(self, message: str) -> None:
        super().__init__("not_available", message, retryable=True)


def service_error(
    code: str, message: str, *, retryable: bool | None = None, detail: str | None = None
) -> dict[str, Any]:
    """Build a canonical ``ServiceError`` body (schema: ``$defs/ServiceError``)."""
    if code not in ERROR_CODES:
        code = "internal"
    body: dict[str, Any] = {
        "code": code,
        "message": message,
        "retryable": retryable if retryable is not None else (code in _DEFAULT_RETRYABLE),
    }
    if detail:
        body["detail"] = detail
    return body


def error_code_for_exception(exc: Exception) -> str:
    """Map an internal exception to a canonical wire error code."""
    if isinstance(exc, ContractError):
        return exc.code
    if isinstance(exc, ValueError):
        return "invalid_request"
    return "internal"


# -- Command run-scoping and payload rules (integration_plan.md §4.3) ---------

RUN_SCOPE_REQUIRED = "required"
RUN_SCOPE_FORBIDDEN = "forbidden"
RUN_SCOPE_OPTIONAL = "optional"

COMMAND_RUN_SCOPE: Mapping[str, str] = {
    "StartRun": RUN_SCOPE_REQUIRED,
    "GetRun": RUN_SCOPE_REQUIRED,
    "ListRuns": RUN_SCOPE_FORBIDDEN,
    "StreamEvents": RUN_SCOPE_REQUIRED,
    "Cancel": RUN_SCOPE_REQUIRED,
    "Checkpoint": RUN_SCOPE_REQUIRED,
    "Resume": RUN_SCOPE_REQUIRED,
    "ResolveApproval": RUN_SCOPE_REQUIRED,
    "RecordCorrection": RUN_SCOPE_REQUIRED,
    "ExplainArtifact": RUN_SCOPE_OPTIONAL,
    "GetCapabilities": RUN_SCOPE_FORBIDDEN,
}

#: Required payload fields per command, checked shallowly.
COMMAND_REQUIRED_PAYLOAD_FIELDS: Mapping[str, Sequence[str]] = {
    "StartRun": ("manifestPath", "repoPath", "brief"),
    "GetRun": (),
    "ListRuns": (),
    "StreamEvents": (),
    "Cancel": (),
    "Checkpoint": (),
    "Resume": (),
    "ResolveApproval": ("decision",),
    "RecordCorrection": ("correction",),
    "ExplainArtifact": ("artifactId",),
    "GetCapabilities": (),
}

#: Allowed payload fields per command.
COMMAND_ALLOWED_PAYLOAD_FIELDS: Mapping[str, frozenset[str]] = {
    "StartRun": frozenset({"manifestPath", "repoPath", "brief", "profileId", "model", "episodeId", "expectedSeq"}),
    "GetRun": frozenset({"expectedSeq"}),
    "ListRuns": frozenset({"limit", "offset"}),
    "StreamEvents": frozenset({"afterSeq"}),
    "Cancel": frozenset({"reason", "expectedSeq"}),
    "Checkpoint": frozenset({"reason", "expectedSeq"}),
    "Resume": frozenset({"checkpointId", "expectedSeq"}),
    "ResolveApproval": frozenset({"decision", "expectedSeq"}),
    "RecordCorrection": frozenset({"correction", "expectedSeq"}),
    "ExplainArtifact": frozenset({"artifactId", "substrateProfile", "expectedSeq"}),
    "GetCapabilities": frozenset(),
}

#: Payload fields whose *value* shape ingress must check, not merely their name.
#: Both are sequence guards (``$defs/SeqGuard``): a JSON integer, or the CT-06
#: decimal-string form, because a run sequence may exceed 2^53-1. Validating the
#: name alone let a malformed guard through to ``int()`` deep in the service,
#: where it surfaced as ``internal`` -- an operator-supplied value must never
#: report as a substrate fault.
_SEQ_GUARD_FIELDS: frozenset[str] = frozenset({"expectedSeq", "afterSeq"})


def _check_seq_guard(command: str, field: str, value: Any) -> None:
    """Reject anything that is not a non-negative sequence number."""
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ContractError(
            "invalid_request",
            f"{command} payload {field} must be a non-negative integer or decimal string",
        )
    if isinstance(value, str):
        if not value.isdigit() or (len(value) > 1 and value.startswith("0")):
            raise ContractError(
                "invalid_request",
                f"{command} payload {field} must be a canonical decimal string",
            )
    elif value < 0:
        raise ContractError(
            "invalid_request", f"{command} payload {field} must not be negative"
        )


APPROVAL_DECISION_REQUIRED_FIELDS: Sequence[str] = (
    "approvalId",
    "resolution",
    "reviewer",
    "argsDigest",
    "descriptorDigest",
    "expiresAt",
    "keyId",
    "signature",
)

#: Ed25519 signatures are 64 bytes rendered as lowercase-or-uppercase hex by
#: both signers (``governance/approvals.py`` ``.hex()`` and client-core's
#: ``signer.ts`` ``toString("hex")``), and ``approval-decision.schema.json``
#: has always required that shape. Accepting any non-empty string here let a
#: structurally impossible signature reach the verifier.
_SIGNATURE_RE = re.compile(r"^[0-9a-fA-F]{128}$")


APPROVAL_DECISION_ALLOWED_FIELDS: frozenset[str] = frozenset(
    {
        "approvalId",
        "resolution",
        "reviewer",
        "argsDigest",
        "descriptorDigest",
        "expiresAt",
        "keyId",
        "signature",
    }
)

_COMMAND_TOP_LEVEL_FIELDS = frozenset({"name", "commandId", "idempotencyKey", "actor", "runId", "payload"})
#: Inbound command frames carry no ``inReplyTo``: it is an outbound-only
#: correlation field on receipt/event/error frames, and ``CommandFrame`` in
#: the schema forbids it. Accepting it here widened ingress for no reader.
_FRAME_TOP_LEVEL_FIELDS = frozenset({"version", "frameType", "frameId", "command"})


@dataclass(frozen=True, slots=True)
class ValidatedCommand:
    name: str
    command_id: str
    idempotency_key: str
    run_id: str
    actor: str
    payload: Mapping[str, Any]


def validate_command(cmd: Mapping[str, Any]) -> ValidatedCommand:
    """Validate one ``command`` object against the frozen vg.4 contract.

    Raises :class:`ContractError` (always ``invalid_request`` here — malformed
    input is a client error, never ``internal``) on the first violation found.
    Unknown commands and unknown fields fail closed rather than being coerced
    or ignored.
    """
    if not isinstance(cmd, Mapping):
        raise ContractError("invalid_request", "command must be an object")

    unknown_fields = set(cmd.keys()) - _COMMAND_TOP_LEVEL_FIELDS
    if unknown_fields:
        raise ContractError("invalid_request", f"unknown command field(s): {sorted(unknown_fields)}")

    name = cmd.get("name")
    if not isinstance(name, str) or name not in COMMAND_RUN_SCOPE:
        raise ContractError("invalid_request", f"unknown command {name!r}")

    command_id = cmd.get("commandId")
    if not isinstance(command_id, str) or not command_id:
        raise ContractError("invalid_request", "command requires non-empty commandId")

    idempotency_key = cmd.get("idempotencyKey")
    if not isinstance(idempotency_key, str) or not idempotency_key:
        raise ContractError("invalid_request", "command requires non-empty idempotencyKey")

    run_id_raw = cmd.get("runId")
    scope = COMMAND_RUN_SCOPE[name]
    if scope == RUN_SCOPE_FORBIDDEN and run_id_raw not in (None, ""):
        raise ContractError("invalid_request", f"{name} must not carry a non-empty runId")
    if scope == RUN_SCOPE_REQUIRED and not run_id_raw:
        raise ContractError("invalid_request", f"{name} requires runId")
    run_id = str(run_id_raw) if run_id_raw is not None else ""

    actor = cmd.get("actor", "operator")
    if not isinstance(actor, str):
        raise ContractError("invalid_request", "actor must be a string")

    payload = cmd.get("payload", {})
    if not isinstance(payload, Mapping):
        raise ContractError("invalid_request", "payload must be an object")

    allowed_payload = COMMAND_ALLOWED_PAYLOAD_FIELDS.get(name, frozenset())
    unknown_payload = set(payload.keys()) - allowed_payload
    if unknown_payload:
        raise ContractError(
            "invalid_request", f"unknown payload field(s) for {name}: {sorted(unknown_payload)}"
        )

    for field in _SEQ_GUARD_FIELDS & set(payload):
        _check_seq_guard(name, field, payload[field])

    missing = [f for f in COMMAND_REQUIRED_PAYLOAD_FIELDS[name] if f not in payload]
    if missing:
        raise ContractError("invalid_request", f"{name} payload missing required field(s): {missing}")

    if name == "ResolveApproval":
        decision = payload.get("decision")
        if not isinstance(decision, Mapping):
            raise ContractError("invalid_request", "ResolveApproval requires a decision object")
        unknown_decision = set(decision.keys()) - APPROVAL_DECISION_ALLOWED_FIELDS
        if unknown_decision:
            raise ContractError(
                "invalid_request", f"unknown decision field(s): {sorted(unknown_decision)}"
            )
        missing_decision = [f for f in APPROVAL_DECISION_REQUIRED_FIELDS if not decision.get(f)]
        if missing_decision:
            raise ContractError(
                "invalid_request", f"decision missing required field(s): {missing_decision}"
            )
        if decision.get("resolution") not in ("approved", "rejected"):
            raise ContractError("invalid_request", "decision.resolution must be approved|rejected")
        sig = decision.get("signature")
        if not isinstance(sig, str) or not _SIGNATURE_RE.match(sig):
            raise ContractError(
                "invalid_request",
                "decision signature must be a 128-character hex Ed25519 signature",
            )

    return ValidatedCommand(
        name=name,
        command_id=command_id,
        idempotency_key=idempotency_key,
        run_id=run_id,
        actor=actor,
        payload=payload,
    )


def validate_frame_envelope(frame: Any) -> None:
    """Validate the outer ``RuntimeServiceFrame`` shell before touching its payload."""
    if not isinstance(frame, Mapping):
        raise ContractError("invalid_request", "frame must be a JSON object")
    
    unknown_frame_fields = set(frame.keys()) - _FRAME_TOP_LEVEL_FIELDS
    if unknown_frame_fields:
        raise ContractError("invalid_request", f"unknown frame field(s): {sorted(unknown_frame_fields)}")

    if frame.get("version") != "vg.4":
        raise ContractError("incompatible_version", "frame version must be vg.4")
    
    frame_type = frame.get("frameType")
    if frame_type not in ("command", "receipt", "event", "error"):
        raise ContractError("invalid_request", f"unknown frameType {frame_type!r}")
    if frame_type != "command":
        raise ContractError("invalid_request", "frame frameType must be command")
    
    frame_id = frame.get("frameId")
    if not isinstance(frame_id, str) or not frame_id:
        raise ContractError("invalid_request", "frame requires non-empty frameId")
