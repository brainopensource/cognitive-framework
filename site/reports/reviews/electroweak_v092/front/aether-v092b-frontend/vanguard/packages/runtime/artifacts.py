"""Runtime-owned artifact capture (`ADR-0096 §14.2/§14.5`, `EVIDENCE.md`).

`EVIDENCE.md` splits truth three ways: the **ledger** holds small durable
causal facts and digests, the **artifact store** holds the large content, and
**projections** are rebuildable and never canonical. Until now the middle
layer had a port (`ports/blob_store.py`) and two adapters, and no production
writer -- so every prompt, model output and compacted context the system
reasoned about was unrecoverable the moment the process exited.

This module is that writer. It is deliberately small and deliberately
paranoid, because the four ways artifact capture goes wrong are all silent:

* **A caller-supplied digest.** The port already refuses one (*"a store that
  trusts a caller's digest is a store whose addresses can lie"*), and so does
  `capture()` -- there is no parameter here to pass one through.
* **Inline content.** An event carrying the prompt puts unwithdrawable bytes
  in an append-only store. `_assert_no_inline_content` fails the write rather
  than the review.
* **An orphan blob.** Bytes stored and the referencing fact lost is garbage
  nothing will ever collect, and a claim nobody can find. Fatal.
* **A dangling reference.** A required fact pointing at absent bytes is worse
  than no fact: it reads as evidence. Forbidden.

**Retention is not authorization** (`ADR-0096 §14.5`). `full` says how long
authorized bytes may live, never that these bytes may be taken. Capture,
redaction and sensitivity resolve *before* `BlobStorePort.put`, and the
resolved policy identity/version enters provenance so a reader can tell a run
that captured nothing from a run that was not allowed to.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, replace
from typing import Any, Iterable, Mapping, Sequence

from ..agency.provenance import (
    CAPTURE_INCOMPLETE,
    EvidenceCaptureRequiredError,
    ProvenanceRecord,
)
from ..ports.blob_store import BlobStorePort

__all__ = [
    "ARTIFACT_ROLES",
    "RETENTION_LEVELS",
    "ArtifactRef",
    "ArtifactWriter",
    "CapturePolicy",
    "EvidenceCaptureRequiredError",
    "EvidenceLedgerAppendError",
    "OrphanArtifactError",
    "SecretRedactor",
    "resolve_capture_policy",
]

#: Exactly the three values `ADR-0096 §14.5` names. Not an open vocabulary:
#: a fourth level would be a retention semantics nobody ratified.
RETENTION_LEVELS = ("digests_only", "standard", "full")

#: The roles a run may capture, spelled exactly as the frozen cross-lane
#: fixture spells them (`test/fixtures/artifact_provenance_fixtures.py`,
#: B-M4-01). `checkpoint_state` is present so a checkpoint reference is an
#: ordinary artifact reference rather than a second mechanism (M-5a consumes
#: it; M-4 only has to not preclude it).
ARTIFACT_ROLES = frozenset({
    "prompt",
    "model_output",
    "context_bundle",
    "compaction_input",
    "compaction_output",
    "workspace_snapshot",
    "patch",
    "verification_report",
    "checkpoint_state",
})

#: `schemaId` for the trajectory `/2` artifact index. Exact model I/O carries
#: its own contract; everything else is opaque bytes and says so.
_SCHEMA_FOR_ROLE: Mapping[str, str] = {
    "prompt": "mhf.prompt/1",
    "model_output": "mhf.model-output/1",
}

#: Roles `standard` retention keeps. `digests_only` keeps none; `full` keeps
#: everything authorized. The split is by *evidentiary density*: exact model
#: I/O is the thing RF-95 exists to prove, and a workspace snapshot is the
#: thing that makes an interactive run cost gigabytes.
_STANDARD_ROLES = frozenset({
    "prompt",
    "model_output",
    "context_bundle",
    "compaction_output",
    "patch",
    "verification_report",
    "checkpoint_state",
})


class EvidenceLedgerAppendError(RuntimeError):
    """An evidence fact could not be durably appended.

    `ADR-0096 §14.2`: evidence-ledger append failure is fatal, and so is
    failure to record a degradation. This is raised in both cases -- there is
    no path on which a lost fact becomes a warning.
    """


class OrphanArtifactError(EvidenceLedgerAppendError):
    """Bytes were stored and the referencing fact was not.

    Distinguished from a plain append failure because the operational
    remedy differs: the blob store now holds content no ledger names, which
    is garbage *and* an un-referenced copy of possibly sensitive material.
    """


# Conservative, high-signal secret shapes. This is a last line of defence in
# front of a store from which nothing can be withdrawn -- not a replacement
# for `tools/linters/scan_secrets.py`, which fails a change before it runs.
_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"sk-or-v1-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:authorization|bearer)\b[\s:=]+[A-Za-z0-9._\-]{16,}"),
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*[\"']?[A-Za-z0-9._\-]{12,}"),
)

_REDACTED = "[redacted]"


class SecretRedactor:
    """Replaces credential-shaped substrings before anything is persisted.

    Applied to the bytes, not to the event: the event never carries content
    at all, so redaction that ran only on the fact would protect nothing.
    """

    __slots__ = ()

    #: Enters provenance so a reader knows which redactor saw these bytes.
    identity = "runtime.secret-redactor/1"

    def redact(self, text: str) -> tuple[str, int]:
        """Returns the scrubbed text and how many substitutions were made."""
        total = 0
        for pattern in _SECRET_PATTERNS:
            text, count = pattern.subn(_REDACTED, text)
            total += count
        return text, total


@dataclass(frozen=True, slots=True)
class CapturePolicy:
    """What this run may take, scrub and keep -- resolved before any write.

    Three independent axes that older designs collapsed into one:

    * `authorized_roles` -- *may* these bytes be taken at all;
    * `retention` -- how much of what was authorized is kept;
    * `required` -- whether failing to keep it fails the run.

    Collapsing them is how a system ends up believing a `full`-retention
    profile granted it permission to persist a prompt containing a secret.
    """

    policy_id: str = "runtime.capture-policy/default"
    policy_version: str = "1"
    retention: str = "standard"
    required: bool = False
    authorized_roles: frozenset[str] = field(default_factory=lambda: frozenset(ARTIFACT_ROLES))
    redact: bool = True
    sensitivity: str = "internal"

    def __post_init__(self) -> None:
        if self.retention not in RETENTION_LEVELS:
            raise ValueError(
                f"retention must be one of {RETENTION_LEVELS}; got {self.retention!r}")
        unknown = set(self.authorized_roles) - ARTIFACT_ROLES
        if unknown:
            raise ValueError(f"unknown artifact roles: {sorted(unknown)}")

    def authorizes(self, role: str) -> bool:
        """Whether raw bytes for `role` may be taken. Retention is not consulted:
        an unauthorized role is unauthorized under every retention level."""
        return role in self.authorized_roles

    def retains(self, role: str) -> bool:
        """Whether authorized bytes for `role` are actually stored."""
        if self.retention == "digests_only":
            return False
        if self.retention == "full":
            return True
        return role in _STANDARD_ROLES

    def identity(self) -> Mapping[str, Any]:
        """The provenance form. `ADR-0096 §14.5`: policy identity and version
        enter provenance, so absence of an artifact is attributable."""
        return {
            "policyId": self.policy_id,
            "policyVersion": self.policy_version,
            "retention": self.retention,
            "required": bool(self.required),
            "redact": bool(self.redact),
            "sensitivity": self.sensitivity,
        }


def resolve_capture_policy(profile: Any = None, *, required: bool | None = None,
                           retention: str | None = None) -> CapturePolicy:
    """Derive the effective policy from an execution profile, structurally.

    Read duck-typed rather than by importing `runtime/profiles.py` types: the
    profile contract is Dev B-owned and gains its `/2` retention and
    `capture.required` fields in the same milestone this writer lands
    (`sprint_active §2`). Reading `getattr` off whatever arrives means the
    `/2` fields light this up the moment they exist, without this file having
    an opinion about a schema it does not own.

    `capture_content` on `/1` is `"redacted" | "full"`; it is a *redaction*
    switch, not a retention one, and is not silently promoted into one.
    """
    requested = getattr(profile, "requested", profile)
    if requested is None:
        return CapturePolicy()

    resolved_retention = retention
    if resolved_retention is None:
        candidate = getattr(requested, "retention", None)
        resolved_retention = candidate if candidate in RETENTION_LEVELS else "standard"

    resolved_required = required
    if resolved_required is None:
        declared = getattr(requested, "capture_required", None)
        resolved_required = bool(declared) if declared is not None else False

    capture_content = getattr(requested, "capture_content", "redacted")
    profile_id = str(getattr(requested, "id", "") or "unresolved")

    return CapturePolicy(
        policy_id=f"runtime.capture-policy/{profile_id}",
        policy_version="1",
        retention=str(resolved_retention),
        required=bool(resolved_required),
        redact=capture_content != "full",
    )


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    """A durable pointer, or an honest record that there is nothing to point at.

    `stored=False` with a digest is the `digests_only`/unauthorized outcome:
    the identity is known, the bytes are not held, and a reader can tell that
    apart from a capture that failed (`captured=False` with no digest).
    """

    artifact_id: str
    role: str
    digest: str
    byte_length: int
    stored: bool
    captured: bool
    retention: str
    policy_id: str
    policy_version: str
    redactions: int = 0
    reason: str = ""
    turn: int | None = None

    def to_index_entry(self) -> Mapping[str, Any]:
        """The frozen `ArtifactIndexEntry` shape Dev B's trajectory `/2` writer
        consumes (B-M4-01). Dev A does not write the trajectory; it publishes
        the index in the shape the published fixture froze, so neither lane
        has to translate the other's field names at merge time."""
        return {
            "artifactId": self.artifact_id,
            "digest": self.digest,
            "role": self.role,
            "schemaId": _SCHEMA_FOR_ROLE.get(self.role, "application/octet-stream;v=1"),
            "sizeBytes": int(self.byte_length),
            "retentionClass": self.retention,
            "stored": bool(self.stored),
            "producedBy": {
                "component": "runtime.artifact-writer",
                "policy_id": self.policy_id,
                "policy_version": self.policy_version,
            },
            "refs": ({"turn": str(self.turn)} if self.turn is not None else {}),
        }

    def to_claim(self) -> Mapping[str, Any]:
        """The small wire form. Never content -- see `_assert_no_inline_content`."""
        return {
            "artifactId": self.artifact_id,
            "role": self.role,
            "contentDigest": self.digest,
            "byteLength": int(self.byte_length),
            "stored": bool(self.stored),
            "captured": bool(self.captured),
            "retention": self.retention,
            "policyId": self.policy_id,
            "policyVersion": self.policy_version,
            "redactions": int(self.redactions),
            **({"reason": self.reason} if self.reason else {}),
        }


#: Payload keys that would mean content had been inlined into a fact. The
#: check is on the emitted payload, not on the caller's intent, because the
#: caller that inlines content is never the one that meant to.
_CONTENT_KEYS = frozenset({
    "content", "text", "body", "prompt", "output", "messages", "bundle",
    "response", "raw", "data", "patch", "snapshot", "report",
})


def _assert_no_inline_content(payload: Mapping[str, Any]) -> None:
    """Refuse an evidence fact that carries content rather than a digest."""
    for key, value in payload.items():
        if key in _CONTENT_KEYS:
            raise ValueError(
                f"artifact fact would inline content under {key!r}; events carry "
                "digests and identities only (EVIDENCE.md truth model)")
        if isinstance(value, Mapping):
            _assert_no_inline_content(value)
        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, Mapping):
                    _assert_no_inline_content(item)


def _jsonable(value: Any) -> Any:
    """Coerce a captured value into something JCS can canonicalise.

    A provider response is whatever the adapter returned -- a `Mapping` that
    is not a `dict`, a dataclass, an enum. Refusing to encode it would turn a
    provider's choice of container into a capture failure, and *guessing* at
    its fields would fabricate content. Coercing containers structurally and
    falling back to `repr` for opaque leaves keeps the bytes faithful to what
    was actually returned.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        items = sorted(value, key=repr) if isinstance(value, (set, frozenset)) else value
        return [_jsonable(item) for item in items]
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode("utf-8", errors="replace")
    fields = getattr(value, "__dict__", None)
    if isinstance(fields, dict) and fields:
        return {str(key): _jsonable(item) for key, item in fields.items()}
    slots = getattr(type(value), "__slots__", None)
    if slots:
        return {str(name): _jsonable(getattr(value, name, None)) for name in slots}
    return repr(value)


def _encode(payload: Any) -> bytes:
    """Bytes for anything a capture site hands over.

    Structures go through the canonical JSON form so two runs that produced
    the same value produce the same digest -- a digest that depended on dict
    ordering would report drift that never happened.
    """
    if isinstance(payload, (bytes, bytearray)):
        return bytes(payload)
    if isinstance(payload, str):
        return payload.encode("utf-8")
    from ..domain.canonicalisation.jcs import canonicalise

    return canonicalise(_jsonable(payload)).encode("utf-8")


def _local_digest(data: bytes) -> str:
    """The identity of bytes that are deliberately **not** stored.

    This is not a caller-supplied digest reaching a store: nothing is stored.
    Whenever bytes do reach the store, `BlobStorePort.put` computes the
    address and its answer is the one that is recorded.
    """
    return "sha256:" + hashlib.sha256(data).hexdigest()


class ArtifactWriter:
    """Blob first, event second, and never the other way round.

    The ordering is the whole durability argument. A fact appended before its
    bytes are durable can name a blob that never arrives -- a reference to
    nothing that reads as evidence. Bytes durable before the fact can at worst
    leave garbage, which is why the reverse failure is *fatal* rather than
    ignored: an orphan is detectable and a dangling reference is not.

    The writer owns no event kind of its own. It emits `ArtifactCreated` and
    `EvidenceClaimProduced`, both already in the roster and both already
    reduced (`domain/ledger/reducer.py`), because M-4 authorizes no roster
    change (`sprint_active §8`).
    """

    def __init__(
        self,
        blobs: BlobStorePort,
        emitter: Any,
        *,
        policy: CapturePolicy | None = None,
        run_id: str,
        principal: str,
        episode_id: str | None = None,
        redactor: Any | None = None,
    ) -> None:
        self._blobs = blobs
        self._emitter = emitter
        self.policy = policy or CapturePolicy()
        self._run_id = run_id
        self._principal = principal
        self._episode_id = episode_id
        self._redactor = redactor if redactor is not None else SecretRedactor()
        self._index: list[ArtifactRef] = []
        self._sequence = 0
        #: Set once optional capture has degraded. `EVIDENCE.md`: the run is
        #: then non-evidentiary and cannot satisfy RF-95 or promotion.
        self.degraded = False
        self._degradation_reason = ""

    # -- the session artifact index (consumed by trajectory `/2`) ---------

    @property
    def index(self) -> tuple[ArtifactRef, ...]:
        """Every reference this run produced, in production order."""
        return tuple(self._index)

    def index_claims(self) -> tuple[Mapping[str, Any], ...]:
        """The wire form of the index, for a trajectory writer to embed."""
        return tuple(ref.to_claim() for ref in self._index)

    def index_entries(self) -> tuple[Mapping[str, Any], ...]:
        """The artifact index in the frozen cross-lane shape (B-M4-01)."""
        return tuple(ref.to_index_entry() for ref in self._index)

    def capture_state(self) -> Mapping[str, Any]:
        """The frozen `CaptureState` shape.

        `incomplete` is not a severity label: `EVIDENCE.md` makes a degraded
        run non-evidentiary, so this is the field a promotion or RF-95 check
        reads to refuse the run outright.
        """
        state: dict[str, Any] = {
            "status": "incomplete" if self.degraded else "complete",
            "required": bool(self.policy.required),
            "policy_id": self.policy.policy_id,
            "policy_version": self.policy.policy_version,
        }
        if self.degraded and self._degradation_reason:
            state["degradation_reason"] = self._degradation_reason
        return state

    def digests_for(self, role: str) -> tuple[str, ...]:
        return tuple(ref.digest for ref in self._index if ref.role == role and ref.digest)

    # -- capture ----------------------------------------------------------

    def capture(
        self,
        role: str,
        payload: Any,
        *,
        required: bool | None = None,
        turn: int | None = None,
        labels: Mapping[str, Any] | None = None,
    ) -> ArtifactRef:
        """Resolve policy, persist bytes, then record the fact. In that order.

        `required` overrides the policy default for one call -- exact model
        I/O is required on an RF-95 run even where a workspace snapshot is
        not. There is no `digest=` parameter and there will not be one.
        """
        if role not in ARTIFACT_ROLES:
            raise ValueError(f"unknown artifact role {role!r}")
        is_required = self.policy.required if required is None else bool(required)

        data = _encode(payload)
        redactions = 0
        if self.policy.redact and self._redactor is not None:
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = None
            if text is not None:
                scrubbed, redactions = self._redactor.redact(text)
                data = scrubbed.encode("utf-8")

        # Authorization and retention, both before `put`. An unauthorized
        # role never reaches the store even under `full` retention.
        if not self.policy.authorizes(role):
            if is_required:
                raise EvidenceCaptureRequiredError(
                    f"capture of required role {role!r} is not authorized by "
                    f"{self.policy.policy_id}@{self.policy.policy_version}")
            return self._record_digest_only(
                role, data, redactions=redactions, turn=turn, labels=labels,
                reason="unauthorized")
        if not self.policy.retains(role):
            return self._record_digest_only(
                role, data, redactions=redactions, turn=turn, labels=labels,
                reason=f"retention:{self.policy.retention}")

        # Blob first. The store computes the address.
        stored = self._blobs.put(data)
        if not stored.ok or not stored.value:
            message = stored.error.message if stored.error else "blob write rejected"
            if is_required:
                raise EvidenceCaptureRequiredError(
                    f"required artifact capture failed for role {role!r}: {message}")
            self.degrade(role=role, reason=f"blob_write_failed: {message}", turn=turn)
            return self._absent_ref(role, len(data), reason="blob_write_failed", turn=turn)

        ref = ArtifactRef(
            artifact_id=self._next_id(role),
            role=role,
            digest=str(stored.value),
            byte_length=len(data),
            stored=True,
            captured=True,
            retention=self.policy.retention,
            policy_id=self.policy.policy_id,
            policy_version=self.policy.policy_version,
            redactions=redactions,
            turn=turn,
        )

        # Event second. A blob without its fact is orphan garbage, and that is
        # fatal whether or not this particular capture was required.
        try:
            self._emit_artifact(ref, turn=turn, labels=labels)
        except Exception as exc:  # noqa: BLE001 -- re-raised as fatal below
            raise OrphanArtifactError(
                f"artifact blob {stored.value} was stored but its ledger fact "
                f"could not be appended: {exc}") from exc

        self._index.append(ref)
        return ref

    def write(
        self,
        role: str,
        payload: Any,
        *,
        digest: bytes | str | None = None,
        required: bool = True,
        turn: int | None = None,
        labels: Mapping[str, Any] | None = None,
    ) -> ArtifactRef:
        """Alias for capture with optional caller-supplied digest verification (C-06)."""
        if digest is not None:
            raw_data = _encode(payload)
            if self.policy.redact and self._redactor is not None:
                try:
                    text = raw_data.decode("utf-8")
                except UnicodeDecodeError:
                    text = None
                if text is not None:
                    scrubbed, _ = self._redactor.redact(text)
                    raw_data = scrubbed.encode("utf-8")
            actual_bytes_digest = hashlib.sha256(raw_data).digest()
            actual_str_digest = "sha256:" + hashlib.sha256(raw_data).hexdigest()
            if isinstance(digest, bytes) and digest != actual_bytes_digest:
                raise EvidenceCaptureRequiredError("digest mismatch")
            elif isinstance(digest, str) and digest != actual_str_digest and digest != actual_str_digest[7:]:
                raise EvidenceCaptureRequiredError("digest mismatch")

        return self.capture(role, payload, required=required, turn=turn, labels=labels)

    def reference(self, digest: str) -> bool:
        """Whether a required blob a fact is about to name actually exists.

        `has()` never raises by contract, so this is a cheap guard callers use
        before emitting a reference they did not themselves produce.
        """
        return bool(digest) and self._blobs.has(digest)

    # -- degradation ------------------------------------------------------

    def degrade(self, *, role: str, reason: str, turn: int | None = None) -> None:
        """Record a durable `capture_incomplete` fact, or die trying.

        `ADR-0096 §14.2`: optional capture may degrade **only after** the
        degradation is durable, and failure to record it is fatal. A run that
        quietly lost an artifact and said nothing is a run whose evidence is
        indistinguishable from a run that captured everything -- which is the
        precise failure the whole evidence contract exists to prevent.
        """
        record = ProvenanceRecord(
            kind=CAPTURE_INCOMPLETE,
            subject=role,
            policy_id=self.policy.policy_id,
            policy_version=self.policy.policy_version,
            parameters={"reason": reason, **self.policy.identity()},
            turn=turn,
        )
        claim = dict(record.to_claim())
        claim["evidentiary"] = False
        _assert_no_inline_content(claim)
        try:
            self._emitter.emit_kind(
                "EvidenceClaimProduced",
                run_id=self._run_id,
                principal=self._principal,
                episode_id=self._episode_id,
                payload={
                    "claimId": self._next_id("capture-incomplete"),
                    "subject": f"run:{self._run_id}",
                    "predicate": CAPTURE_INCOMPLETE,
                    "value": claim,
                    "reason": CAPTURE_INCOMPLETE,
                },
            )
        except Exception as exc:  # noqa: BLE001 -- fatal by contract
            raise EvidenceLedgerAppendError(
                f"capture degraded for role {role!r} ({reason}) and the "
                f"capture_incomplete fact could not be recorded: {exc}") from exc
        # Only now. The run is non-evidentiary from this point.
        self.degraded = True
        if not self._degradation_reason:
            self._degradation_reason = reason

    # -- internals --------------------------------------------------------

    def _next_id(self, role: str) -> str:
        self._sequence += 1
        return f"{self._run_id}:{role}:{self._sequence}"

    def _absent_ref(self, role: str, byte_length: int, *, reason: str,
                    turn: int | None = None) -> ArtifactRef:
        ref = ArtifactRef(
            artifact_id=self._next_id(role), role=role, digest="",
            byte_length=byte_length, stored=False, captured=False,
            retention=self.policy.retention, policy_id=self.policy.policy_id,
            policy_version=self.policy.policy_version, reason=reason, turn=turn)
        self._index.append(ref)
        return ref

    def _record_digest_only(self, role: str, data: bytes, *, redactions: int,
                            turn: int | None, labels: Mapping[str, Any] | None,
                            reason: str) -> ArtifactRef:
        """The allowed non-capture outcome (`ADR-0096 §14.5`).

        The identity survives even though the bytes do not, so a later reader
        can still say *which* prompt this was if the same bytes are ever
        legitimately captured elsewhere.
        """
        ref = ArtifactRef(
            artifact_id=self._next_id(role), role=role, digest=_local_digest(data),
            byte_length=len(data), stored=False, captured=False,
            retention=self.policy.retention, policy_id=self.policy.policy_id,
            policy_version=self.policy.policy_version, redactions=redactions,
            reason=reason, turn=turn)
        self._emit_artifact(ref, turn=turn, labels=labels)
        self._index.append(ref)
        return ref

    def _emit_artifact(self, ref: ArtifactRef, *, turn: int | None,
                       labels: Mapping[str, Any] | None) -> None:
        payload: dict[str, Any] = {
            "artifact": {
                "artifactId": ref.artifact_id,
                "artifactKind": "M",
                "version": "1.0.0",
                "contentDigest": ref.digest,
            },
            "reason": f"artifact_captured:{ref.role}",
            **ref.to_claim(),
        }
        if turn is not None:
            payload["turn"] = int(turn)
        if labels:
            payload["labels"] = {str(k): v for k, v in labels.items()}
        _assert_no_inline_content(payload)
        self._emitter.emit_kind(
            "ArtifactCreated",
            run_id=self._run_id,
            principal=self._principal,
            episode_id=self._episode_id,
            payload=payload,
        )
