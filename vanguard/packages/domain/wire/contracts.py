"""Reader-profile implementation for the T1.4–T1.12 wire contracts.

Readers validate every known field and preserve unknown fields recursively.
Writer strictness remains normative in ``schemas/v4/*.schema.json``.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping

from ..canonicalisation.digest import digest_of
from ..primitives.primitives import ParseError, parse
from ..selectors.resource_selector import SELECTOR_KINDS, SelectorError, parse_selector

JsonObject = dict[str, Any]


class WireError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(f"{path}: {message} ({code})")
        self.code = code
        self.path = path


def _object(value: Any, path: str) -> JsonObject:
    if not isinstance(value, dict):
        raise WireError("type", path, "expected object")
    return value


def _array(value: Any, path: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list):
        raise WireError("type", path, "expected array")
    if nonempty and not value:
        raise WireError("minItems", path, "must not be empty")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise WireError("type", path, "expected string")
    if not value:
        raise WireError("minLength", path, "must not be empty")
    return value


def _integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise WireError("type", path, "expected integer")
    return value


def _required(value: Mapping[str, Any], fields: tuple[str, ...], path: str) -> None:
    for field in fields:
        if field not in value:
            raise WireError("required", path, f"missing {field}")


def _enum(value: Any, options: tuple[str, ...], path: str) -> str:
    result = _string(value, path)
    if result not in options:
        raise WireError("enum", path, f"unsupported value {result!r}")
    return result


def _primitive(kind: str, value: Any, path: str) -> None:
    try:
        parse(kind, value)
    except ParseError as exc:
        raise WireError(exc.code, path, str(exc)) from exc


def _strings(value: Any, path: str, *, nonempty: bool = False) -> list[str]:
    items = _array(value, path, nonempty=nonempty)
    result = [_string(item, f"{path}/{index}") for index, item in enumerate(items)]
    if len(result) != len(set(result)):
        raise WireError("uniqueItems", path, "items must be unique")
    return result


def _selector(value: Any, path: str) -> None:
    source = _object(value, path)
    kind = source.get("kind")
    if kind not in SELECTOR_KINDS:
        raise WireError("enum", f"{path}/kind", "unknown selector kind")
    known_fields = {
        "fs": ("kind", "root", "paths"),
        "network": ("kind", "hosts", "ports"),
        "secret": ("kind", "refs", "discloseToModel"),
        "git": ("kind", "repo", "refs"),
        "table": ("kind", "table", "ranges"),
        "browser": ("kind", "origin", "accountRef"),
        "generic": ("kind", "uriPattern"),
    }[kind]
    candidate = {field: source[field] for field in known_fields if field in source}
    try:
        parse_selector(candidate)
    except SelectorError as exc:
        raise WireError(exc.code, path, str(exc)) from exc


def _provenance(value: Any, path: str) -> None:
    source = _object(value, path)
    _required(source, ("origin", "instructionAuthority", "integrity", "confidentiality", "epistemic"), path)
    _enum(source["origin"], ("operator", "system", "environment", "model", "external", "memory"), f"{path}/origin")
    _enum(source["instructionAuthority"], ("directive", "advisory", "inert"), f"{path}/instructionAuthority")
    _enum(source["integrity"], ("attested", "verified", "unverified", "tampered"), f"{path}/integrity")
    _primitive("ConfidentialityLabel", source["confidentiality"], f"{path}/confidentiality")
    _primitive("EpistemicState", source["epistemic"], f"{path}/epistemic")


def _invalidation(value: Any, path: str) -> None:
    for index, item in enumerate(_array(value, path, nonempty=True)):
        item_path = f"{path}/{index}"
        source = _object(item, item_path)
        _required(source, ("condition", "checkKind"), item_path)
        _string(source["condition"], f"{item_path}/condition")
        check_kind = _enum(source["checkKind"], ("automatic", "scheduled", "manual"), f"{item_path}/checkKind")
        if check_kind == "automatic":
            if "checkRef" not in source:
                raise WireError("required", item_path, "automatic condition requires checkRef")
            _primitive("EvaluatorId", source["checkRef"], f"{item_path}/checkRef")


def _parse_effect(value: Any) -> None:
    source = _object(value, "EffectDescriptor")
    _required(source, ("verb", "sinkClass", "selector", "args", "argsDigest", "idempotencyKey", "riskTier", "provenance"), "EffectDescriptor")
    _string(source["verb"], "EffectDescriptor/verb")
    _enum(source["sinkClass"], ("pure", "observation", "privileged"), "EffectDescriptor/sinkClass")
    _selector(source["selector"], "EffectDescriptor/selector")
    args = _object(source["args"], "EffectDescriptor/args")
    _primitive("Digest", source["argsDigest"], "EffectDescriptor/argsDigest")
    if digest_of(args) != source["argsDigest"]:
        raise WireError("digest", "EffectDescriptor/argsDigest", "does not bind canonical args")
    if "workingDirectory" in source:
        _string(source["workingDirectory"], "EffectDescriptor/workingDirectory")
    for field in ("readSet", "writeSet"):
        if field in source:
            for index, selector in enumerate(_array(source[field], f"EffectDescriptor/{field}")):
                _selector(selector, f"EffectDescriptor/{field}/{index}")
    _string(source["idempotencyKey"], "EffectDescriptor/idempotencyKey")
    _primitive("RiskTier", source["riskTier"], "EffectDescriptor/riskTier")
    _provenance(source["provenance"], "EffectDescriptor/provenance")


def _parse_grant(value: Any) -> None:
    source = _object(value, "CapabilityGrant")
    _required(source, ("grantId", "principal", "descriptorDigest", "actions", "selector", "constraints", "expiry", "maxUses", "purposeDigest"), "CapabilityGrant")
    for field, kind in (("grantId", "GrantId"), ("principal", "PrincipalId"), ("descriptorDigest", "Digest"), ("expiry", "Timestamp"), ("maxUses", "IntString"), ("purposeDigest", "Digest")):
        _primitive(kind, source[field], f"CapabilityGrant/{field}")
    _strings(source["actions"], "CapabilityGrant/actions", nonempty=True)
    _selector(source["selector"], "CapabilityGrant/selector")
    constraints = _object(source["constraints"], "CapabilityGrant/constraints")
    _required(constraints, ("budgetLeaseId",), "CapabilityGrant/constraints")
    _primitive("LeaseId", constraints["budgetLeaseId"], "CapabilityGrant/constraints/budgetLeaseId")
    for field in ("maxBytes", "maxEffects"):
        if field in constraints:
            _primitive("IntString", constraints[field], f"CapabilityGrant/constraints/{field}")
    if "environmentSnapshot" in constraints:
        _primitive("Digest", constraints["environmentSnapshot"], "CapabilityGrant/constraints/environmentSnapshot")
    if "networkPolicy" in constraints:
        _enum(constraints["networkPolicy"], ("deny", "allowlist"), "CapabilityGrant/constraints/networkPolicy")
    if "requirePreview" in constraints and not isinstance(constraints["requirePreview"], bool):
        raise WireError("type", "CapabilityGrant/constraints/requirePreview", "expected boolean")
    if "requireApprovalAboveRisk" in constraints:
        _primitive("RiskTier", constraints["requireApprovalAboveRisk"], "CapabilityGrant/constraints/requireApprovalAboveRisk")
    if "parentGrantId" in source:
        _primitive("GrantId", source["parentGrantId"], "CapabilityGrant/parentGrantId")
    if "approvalRef" in source:
        _primitive("ApprovalId", source["approvalRef"], "CapabilityGrant/approvalRef")
    if "authenticator" in source:
        _string(source["authenticator"], "CapabilityGrant/authenticator")


def _parse_receipt(value: Any) -> None:
    source = _object(value, "Receipt")
    _required(source, ("descriptorDigest", "outcome", "observedAt", "resultDigest", "affectedResources"), "Receipt")
    for field, kind in (("descriptorDigest", "Digest"), ("observedAt", "Timestamp"), ("resultDigest", "Digest")):
        _primitive(kind, source[field], f"Receipt/{field}")
    outcome = _enum(source["outcome"], ("ok", "failed", "undeterminable"), "Receipt/outcome")
    if "grantId" in source:
        _primitive("GrantId", source["grantId"], "Receipt/grantId")
    for index, item in enumerate(_array(source["affectedResources"], "Receipt/affectedResources")):
        item_path = f"Receipt/affectedResources/{index}"
        record = _object(item, item_path)
        _required(record, ("resource", "change"), item_path)
        _string(record["resource"], f"{item_path}/resource")
        change = _enum(record["change"], ("created", "modified", "deleted", "observed"), f"{item_path}/change")
        if change != "created" and "preDigest" not in record:
            raise WireError("required", item_path, "preDigest required")
        if change != "deleted" and "postDigest" not in record:
            raise WireError("required", item_path, "postDigest required")
        for field in ("preDigest", "postDigest", "patchRef"):
            if field in record:
                _primitive("Digest", record[field], f"{item_path}/{field}")
    if outcome == "undeterminable":
        if "uncertainty" not in source:
            raise WireError("required", "Receipt", "undeterminable requires uncertainty")
        uncertainty = _object(source["uncertainty"], "Receipt/uncertainty")
        _required(uncertainty, ("scope", "reason"), "Receipt/uncertainty")
        _enum(uncertainty["scope"], ("effect_occurrence", "evidence_completeness", "result"), "Receipt/uncertainty/scope")
        _string(uncertainty["reason"], "Receipt/uncertainty/reason")


def _parse_event(value: Any) -> None:
    source = _object(value, "EventEnvelope")
    required = ("schemaVersion", "eventId", "scope", "traceId", "spanId", "seq", "occurredAt", "recordedAt", "principal", "principalRole", "tenantId", "ownerId", "confidentiality", "retentionClass", "trainability", "redactionStatus", "payload")
    _required(source, required, "EventEnvelope")
    if source["schemaVersion"] != "vg.4":
        raise WireError("const", "EventEnvelope/schemaVersion", "unsupported schema version")
    scope = _enum(source["scope"], ("episode", "governance", "evolution", "recovery"), "EventEnvelope/scope")
    for field, kind in (("eventId", "Uuidv7"), ("seq", "IntString"), ("occurredAt", "Timestamp"), ("recordedAt", "Timestamp"), ("principal", "PrincipalId"), ("tenantId", "TenantId"), ("ownerId", "OwnerId"), ("confidentiality", "ConfidentialityLabel"), ("retentionClass", "RetentionClass"), ("trainability", "TrainabilityLabel"), ("redactionStatus", "RedactionStatus")):
        _primitive(kind, source[field], f"EventEnvelope/{field}")
    _enum(source["principalRole"], ("user", "operator", "episode", "process", "evaluator", "release"), "EventEnvelope/principalRole")
    _string(source["traceId"], "EventEnvelope/traceId")
    _string(source["spanId"], "EventEnvelope/spanId")
    if scope in ("episode", "recovery") and "runId" not in source:
        raise WireError("required", "EventEnvelope", f"{scope} requires runId")
    if scope == "episode" and "episodeId" not in source:
        raise WireError("required", "EventEnvelope", "episode requires episodeId")
    if scope in ("governance", "evolution") and "runId" in source:
        raise WireError("scope", "EventEnvelope/runId", f"{scope} cannot carry runId")
    if scope != "episode" and "episodeId" in source:
        raise WireError("scope", "EventEnvelope/episodeId", f"{scope} cannot carry episodeId")
    payload = _object(source["payload"], "EventEnvelope/payload")
    _required(payload, ("kind",), "EventEnvelope/payload")
    _string(payload["kind"], "EventEnvelope/payload/kind")


def _parse_artifact(value: Any) -> None:
    source = _object(value, "Artifact")
    _required(source, ("artifactId", "kind", "class", "hypothesis", "evidenceRefs", "invalidationConditions", "riskDelta", "contentDigest"), "Artifact")
    _primitive("ArtifactId", source["artifactId"], "Artifact/artifactId")
    _string(source["kind"], "Artifact/kind")
    artifact_class = _enum(source["class"], ("enforcement", "compensation"), "Artifact/class")
    if artifact_class == "compensation" and "compensatesFor" not in source:
        raise WireError("required", "Artifact", "compensation requires compensatesFor")
    if artifact_class == "enforcement" and "compensatesFor" in source:
        raise WireError("not", "Artifact/compensatesFor", "enforcement cannot compensate")
    _string(source["hypothesis"], "Artifact/hypothesis")
    for index, digest in enumerate(_array(source["evidenceRefs"], "Artifact/evidenceRefs")):
        _primitive("Digest", digest, f"Artifact/evidenceRefs/{index}")
    _invalidation(source["invalidationConditions"], "Artifact/invalidationConditions")
    _integer(source["riskDelta"], "Artifact/riskDelta")
    _primitive("Digest", source["contentDigest"], "Artifact/contentDigest")
    content = {key: val for key, val in source.items() if key != "contentDigest" and key in {"artifactId", "kind", "class", "compensatesFor", "hypothesis", "evidenceRefs", "invalidationConditions", "riskDelta"}}
    if digest_of(content) != source["contentDigest"]:
        raise WireError("digest", "Artifact/contentDigest", "does not bind immutable content")


def _parse_claim(value: Any) -> None:
    source = _object(value, "EvidenceClaim")
    _required(source, ("id", "subject", "predicate", "value", "protocol", "evaluator", "environmentProfile", "substrateProfile", "taskDistribution", "uncertainty", "validity", "invalidationConditions"), "EvidenceClaim")
    for field, kind in (("id", "ClaimId"), ("protocol", "Digest"), ("environmentProfile", "Digest"), ("substrateProfile", "Digest"), ("taskDistribution", "Digest")):
        _primitive(kind, source[field], f"EvidenceClaim/{field}")
    _string(source["subject"], "EvidenceClaim/subject")
    _string(source["predicate"], "EvidenceClaim/predicate")
    evaluator = _object(source["evaluator"], "EvidenceClaim/evaluator")
    _required(evaluator, ("evaluatorId", "class", "imageDigest"), "EvidenceClaim/evaluator")
    _primitive("EvaluatorId", evaluator["evaluatorId"], "EvidenceClaim/evaluator/evaluatorId")
    _primitive("Digest", evaluator["imageDigest"], "EvidenceClaim/evaluator/imageDigest")
    validity = _object(source["validity"], "EvidenceClaim/validity")
    _required(validity, ("domains",), "EvidenceClaim/validity")
    _strings(validity["domains"], "EvidenceClaim/validity/domains", nonempty=True)
    _invalidation(source["invalidationConditions"], "EvidenceClaim/invalidationConditions")


def _parse_correction(value: Any) -> None:
    source = _object(value, "CorrectionRecord")
    _required(source, ("episodeId", "proposedPatchDigest", "acceptedPatchDigest", "reasonCodes", "magnitude", "scope", "correctingPrincipalRole"), "CorrectionRecord")
    for field, kind in (("episodeId", "EpisodeId"), ("proposedPatchDigest", "Digest"), ("acceptedPatchDigest", "Digest")):
        _primitive(kind, source[field], f"CorrectionRecord/{field}")
    reasons = _strings(source["reasonCodes"], "CorrectionRecord/reasonCodes", nonempty=True)
    allowed = {"functional_defect", "missing_requirement", "security_policy", "test_inadequacy", "maintainability", "architecture_preference", "style", "product_change", "environment_change", "reviewer_disagreement"}
    if not set(reasons) <= allowed:
        raise WireError("enum", "CorrectionRecord/reasonCodes", "unknown reason code")
    _enum(source["magnitude"], ("minor", "moderate", "major"), "CorrectionRecord/magnitude")
    scope = _enum(source["scope"], ("user", "team", "repo", "domain", "general"), "CorrectionRecord/scope")
    if set(reasons) & {"style", "architecture_preference"} and scope not in {"user", "team", "repo"}:
        raise WireError("scope", "CorrectionRecord/scope", "style and preference corrections must remain local")
    _enum(source["correctingPrincipalRole"], ("user", "operator", "episode", "process", "evaluator", "release"), "CorrectionRecord/correctingPrincipalRole")


def _parse_recording(value: Any) -> None:
    source = _object(value, "Recording")
    _required(source, ("modelCassetteDigest", "imageDigest", "envSnapshotDigest", "seed", "clockPolicy"), "Recording")
    for field in ("modelCassetteDigest", "imageDigest", "envSnapshotDigest"):
        _primitive("Digest", source[field], f"Recording/{field}")
    _primitive("IntString", source["seed"], "Recording/seed")
    _enum(source["clockPolicy"], ("recorded", "fixed", "logical"), "Recording/clockPolicy")


def _parse_process_definition(value: Any) -> None:
    source = _object(value, "ProcessDefinition")
    _required(source, ("definitionDigest", "states", "initialState", "transitions", "approvalPoints", "boundEffectVerbs"), "ProcessDefinition")
    _primitive("Digest", source["definitionDigest"], "ProcessDefinition/definitionDigest")
    states = set(_strings(source["states"], "ProcessDefinition/states", nonempty=True))
    initial = _string(source["initialState"], "ProcessDefinition/initialState")
    if initial not in states:
        raise WireError("state", "ProcessDefinition/initialState", "initial state is undeclared")
    transitions = _array(source["transitions"], "ProcessDefinition/transitions")
    seen: set[tuple[str, str]] = set()
    for index, value in enumerate(transitions):
        path = f"ProcessDefinition/transitions/{index}"
        transition = _object(value, path)
        _required(transition, ("from", "eventKind", "to"), path)
        start, event, end = (_string(transition[key], f"{path}/{key}") for key in ("from", "eventKind", "to"))
        if start not in states or end not in states:
            raise WireError("state", path, "transition references undeclared state")
        if (start, event) in seen:
            raise WireError("conflict", path, "transition is nondeterministic")
        seen.add((start, event))
    _strings(source["approvalPoints"], "ProcessDefinition/approvalPoints")
    _strings(source["boundEffectVerbs"], "ProcessDefinition/boundEffectVerbs")
    content = {key: source[key] for key in ("states", "initialState", "transitions", "approvalPoints", "boundEffectVerbs")}
    if digest_of(content) != source["definitionDigest"]:
        raise WireError("digest", "ProcessDefinition/definitionDigest", "does not bind definition")


def _parse_process_instance(value: Any) -> None:
    source = _object(value, "ProcessInstance")
    _required(source, ("processId", "definitionDigest", "currentState", "allowedTransitions", "pendingApprovals", "boundEffectVerbs", "history"), "ProcessInstance")
    _primitive("ProcessId", source["processId"], "ProcessInstance/processId")
    _primitive("Digest", source["definitionDigest"], "ProcessInstance/definitionDigest")
    _string(source["currentState"], "ProcessInstance/currentState")
    _strings(source["allowedTransitions"], "ProcessInstance/allowedTransitions")
    for index, approval in enumerate(_array(source["pendingApprovals"], "ProcessInstance/pendingApprovals")):
        _primitive("ApprovalId", approval, f"ProcessInstance/pendingApprovals/{index}")
    _strings(source["boundEffectVerbs"], "ProcessInstance/boundEffectVerbs")
    for index, value in enumerate(_array(source["history"], "ProcessInstance/history")):
        path = f"ProcessInstance/history/{index}"
        record = _object(value, path)
        _required(record, ("from", "eventKind", "to", "eventId"), path)
        for field in ("from", "eventKind", "to"):
            _string(record[field], f"{path}/{field}")
        _primitive("Uuidv7", record["eventId"], f"{path}/eventId")


_PARSERS: dict[str, Callable[[Any], None]] = {
    "EffectDescriptor": _parse_effect,
    "CapabilityGrant": _parse_grant,
    "Receipt": _parse_receipt,
    "EventEnvelope": _parse_event,
    "Artifact": _parse_artifact,
    "EvidenceClaim": _parse_claim,
    "CorrectionRecord": _parse_correction,
    "Recording": _parse_recording,
    "ProcessDefinition": _parse_process_definition,
    "ProcessInstance": _parse_process_instance,
}
WIRE_KINDS = tuple(_PARSERS)


def parse_wire(kind: str, value: Any) -> JsonObject:
    """Validate one reader-profile value and return a lossless deep copy."""

    parser = _PARSERS.get(kind)
    if parser is None:
        raise WireError("kind", kind, "unknown wire contract")
    parser(value)
    return deepcopy(_object(value, kind))
