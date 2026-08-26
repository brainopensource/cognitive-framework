"""The generic provenance seam (`ADR-0096 §14.1`, `ADR-0097 Decision 1`).

Agency produces the facts that make a turn attributable — which context was
selected, what compaction did to it, which bytes actually reached the
provider — but Agency may not know where those facts are durably written.
`domain <- ports <- kernel <- agency <- runtime` is the whole point: a
`ContextCompiler` that imported a ledger emitter would make the composition
root a dependency of the thing it composes.

So this module holds **only** protocol, records and errors. Every concrete
sink lives in `runtime/provenance.py`. Nothing here imports `runtime`,
`adapters` or `packs`, and nothing here writes anything.

`EvidenceCaptureRequiredError` is declared here for the same reason: when
`capture.required=true` and capture fails, the failure is fatal
(`ADR-0096 §14.2`) and it has to travel *up* through Agency call frames from
a Runtime-owned writer. A generic error type crosses the protocol; a Runtime
error type would drag Runtime across the boundary with it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, runtime_checkable

__all__ = [
    "CONTEXT_SELECTION",
    "COMPACTION",
    "MODEL_IO",
    "CACHE",
    "CAPTURE_INCOMPLETE",
    "EvidenceCaptureRequiredError",
    "NullProvenanceSink",
    "ProvenanceRecord",
    "ProvenanceSink",
]

#: Record kinds. These are *provenance* discriminators carried inside an
#: existing contract-authorized evidence fact -- they are not event kinds and
#: they do not enter the event roster (M-4 non-scope, `sprint_active §8`).
CONTEXT_SELECTION = "context_selection"
COMPACTION = "compaction"
MODEL_IO = "model_io"
CACHE = "cache"
CAPTURE_INCOMPLETE = "capture_incomplete"


class EvidenceCaptureRequiredError(RuntimeError):
    """Required evidence capture failed; the run must not continue.

    `ADR-0096 §14.2`. Raised by a Runtime-owned artifact writer when
    `capture.required=true` and the bytes could not be durably persisted, and
    allowed to propagate through Agency untouched. Agency must never catch
    this to keep a turn alive: a run that continued past it would be claiming
    evidence it does not hold.
    """


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    """One small, durable causal fact about how a turn was assembled.

    Digests and identities only. `EVIDENCE.md` splits truth three ways --
    ledger, artifact store, projections -- and this is the ledger half: the
    bytes live behind `input_digest`/`output_digest`/`artifacts`, never in
    the record. A record that inlined a prompt would put unwithdrawable
    content in an append-only store.
    """

    kind: str
    subject: str
    policy_id: str = ""
    policy_version: str = ""
    parameters: Mapping[str, Any] = field(default_factory=dict)
    input_digest: str = ""
    output_digest: str = ""
    labels: Mapping[str, Any] = field(default_factory=dict)
    counts: Mapping[str, Any] = field(default_factory=dict)
    artifacts: tuple[str, ...] = ()
    turn: int | None = None

    def to_claim(self) -> Mapping[str, Any]:
        """The small wire form. Empty fields are omitted, not nulled: an
        absent cache claim and a null one read differently, and only one of
        them is honest about a live call that never touched a cache."""
        body: dict[str, Any] = {"kind": self.kind, "subject": self.subject}
        if self.policy_id:
            body["policyId"] = self.policy_id
        if self.policy_version:
            body["policyVersion"] = self.policy_version
        if self.parameters:
            body["parameters"] = dict(self.parameters)
        if self.input_digest:
            body["inputDigest"] = self.input_digest
        if self.output_digest:
            body["outputDigest"] = self.output_digest
        if self.labels:
            body["labels"] = dict(self.labels)
        if self.counts:
            body["counts"] = dict(self.counts)
        if self.artifacts:
            body["artifacts"] = list(self.artifacts)
        if self.turn is not None:
            body["turn"] = int(self.turn)
        return body


@runtime_checkable
class ProvenanceSink(Protocol):
    """Where provenance records go. Implemented in `runtime/`, never here."""

    def record(self, record: ProvenanceRecord) -> None:
        """Durably record one fact, or raise. Never silently swallow.

        `ADR-0096 §14.2`: evidence-ledger append failure is fatal, so a sink
        that returned `False` on failure would let a caller mistake a lost
        fact for a recorded one.
        """


class NullProvenanceSink:
    """The no-capture composition. Records nothing and claims nothing.

    This is what `blobs=None` resolves to, and it is the reason the legacy
    path stays legal: a session with no blob store emits no provenance and
    therefore makes no evidence claim it cannot support.
    """

    __slots__ = ()

    def record(self, record: ProvenanceRecord) -> None:
        return None
