"""The concrete provenance sink (`ADR-0096 §14.1`, `EVIDENCE.md`).

`agency/provenance.py` declares the protocol, the record and the error.
Nothing there can write. This is the half that can: it turns a
`ProvenanceRecord` into a durable `EvidenceClaimProduced` fact through the
one canonical writer (`LedgerEmitter`, `ADR-0076 §6`), and it lives in
`runtime/` because `runtime/` is the only package permitted to know both the
ledger and the turn engine.

**Failures are not swallowed here.** `CompetencePriorRecorder` may lose its
prior to `F-25` because a missing prior is a measurement gap in a calibration
set. A lost provenance fact is different in kind: `ADR-0096 §14.2` makes
evidence-ledger append failure fatal, because the run continues to *look*
evidentiary afterwards. So `record()` raises.

**Absence is a claim too.** `record_cache` emits nothing when the provider
reported no cache participation. A live invocation that never touched a cache
has no cache identity, no key digest and no validation status, and inventing
`{"hit": false}` for it would make "we asked and it missed" indistinguishable
from "there was no cache in this composition".
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..agency.provenance import (
    CACHE,
    COMPACTION,
    CONTEXT_SELECTION,
    MODEL_IO,
    NullProvenanceSink,
    ProvenanceRecord,
    ProvenanceSink,
)
from .artifacts import ArtifactRef, EvidenceLedgerAppendError, _assert_no_inline_content

__all__ = [
    "NullProvenanceSink",
    "ProvenanceRecord",
    "ProvenanceSink",
    "RuntimeProvenanceSink",
    "cache_participation",
]

#: Keys a provider response may use to report cache/cassette participation.
#: Only what a provider *actually says*; nothing here infers participation
#: from latency, cost or a cassette-shaped adapter name.
_CACHE_KEYS = ("cache", "cassette", "prompt_cache", "cache_read")


def cache_participation(value: Any) -> Mapping[str, Any] | None:
    """The provider's own cache report, or `None` when it made none.

    Returning `None` is the common and correct answer for a live call. A
    caller that treated `None` as a miss would emit a cache claim for a
    composition that has no cache.
    """
    if not isinstance(value, Mapping):
        return None
    for key in _CACHE_KEYS:
        reported = value.get(key)
        if isinstance(reported, Mapping) and reported:
            return reported
        if isinstance(reported, bool) and reported:
            return {"participated": True, "source": key}
    return None


class RuntimeProvenanceSink:
    """Writes provenance records as `EvidenceClaimProduced` facts.

    No new event kind: M-4 authorizes none (`sprint_active §8`), and
    `EvidenceClaimProduced` is already in the roster and already reduced into
    `LedgerState.evidence_claims`. The record kind rides in `predicate`, which
    is what a claim's predicate is for.
    """

    def __init__(self, emitter: Any, *, run_id: str, principal: str,
                 episode_id: str | None = None) -> None:
        self._emitter = emitter
        self._run_id = run_id
        self._principal = principal
        self._episode_id = episode_id
        self._records: list[ProvenanceRecord] = []
        self._sequence = 0

    # -- the session provenance index (consumed by trajectory `/2`) -------

    @property
    def records(self) -> tuple[ProvenanceRecord, ...]:
        return tuple(self._records)

    def claims(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(record.to_claim() for record in self._records)

    # -- ProvenanceSink ---------------------------------------------------

    def record(self, record: ProvenanceRecord) -> None:
        claim = record.to_claim()
        _assert_no_inline_content(claim)
        self._sequence += 1
        try:
            self._emitter.emit_kind(
                "EvidenceClaimProduced",
                run_id=self._run_id,
                principal=self._principal,
                episode_id=self._episode_id,
                payload={
                    "claimId": f"{self._run_id}:{record.kind}:{self._sequence}",
                    "subject": record.subject,
                    "predicate": record.kind,
                    "value": claim,
                    "reason": record.kind,
                },
            )
        except Exception as exc:  # noqa: BLE001 -- fatal by ADR-0096 §14.2
            raise EvidenceLedgerAppendError(
                f"provenance record {record.kind!r} for {record.subject!r} could "
                f"not be appended: {exc}") from exc
        self._records.append(record)

    def trajectory_provenance(self) -> Mapping[str, Any]:
        """The `provenance` block of `mhf.trajectory/2`, in the frozen shapes.

        Dev B owns the trajectory writer; Dev A owns what actually happened.
        This is the handover, and it is deliberately a projection of
        `self._records` rather than a second accumulator -- a block that could
        disagree with the ledger facts would be a third truth.
        """
        context: list[Mapping[str, Any]] = []
        compaction: list[Mapping[str, Any]] = []
        cache: list[Mapping[str, Any]] = []
        for record in self._records:
            if record.kind == CONTEXT_SELECTION:
                context.append({
                    "claimKind": CONTEXT_SELECTION,
                    "policy": {
                        "id": record.policy_id,
                        "version": record.policy_version,
                        "paramsDigest": str(record.parameters.get("paramsDigest") or ""),
                    },
                    "inputDigest": record.input_digest,
                    "outputDigest": record.output_digest,
                    "metrics": {
                        "tokenCount": int(record.counts.get("tokenCount") or 0),
                        "layerCounts": dict(record.counts.get("layerCounts") or {}),
                    },
                    "turnIndex": int(record.turn or 0),
                    "selectedLabels": list(record.labels.get("selected") or ()),
                    "droppedLabels": list(record.labels.get("dropped") or ()),
                    "elidedLabels": list(record.labels.get("elided") or ()),
                    "inputArtifacts": list(record.labels.get("inputArtifacts") or ()),
                    "outputArtifacts": list(record.labels.get("outputArtifacts") or ()),
                })
            elif record.kind == COMPACTION:
                compaction.append({
                    "claimKind": COMPACTION,
                    "policy": {
                        "id": record.policy_id,
                        "version": record.policy_version,
                        "paramsDigest": str(record.parameters.get("paramsDigest") or ""),
                    },
                    "inputDigest": record.input_digest,
                    "outputDigest": record.output_digest,
                    "metrics": {
                        "tokensBefore": int(record.counts.get("tokensBefore") or 0),
                        "tokensAfter": int(record.counts.get("tokensAfter") or 0),
                        "removedTokens": int(record.counts.get("removedTokens") or 0),
                    },
                    "turnIndex": int(record.turn or 0),
                    "inputArtifacts": list(record.artifacts),
                    "outputArtifacts": [],
                })
            elif record.kind == CACHE:
                cache.append({
                    "claimKind": "cache_interaction",
                    "cacheId": str(record.parameters.get("cacheId") or ""),
                    "keyDigest": record.input_digest,
                    "sourceDigest": record.output_digest,
                    "hit": bool(record.parameters.get("hit")),
                    "sourceStatus": str(record.parameters.get("sourceStatus") or ""),
                    "turnIndex": int(record.turn or 0),
                })
        # Absence stays absence: an empty list is "this run had none", which
        # is what a live no-cache run must report.
        return {"context": context, "compaction": compaction, "cache": cache}

    # -- typed capture sites ----------------------------------------------

    def record_context_selection(
        self,
        *,
        identity: Mapping[str, Any],
        candidate_digest: str,
        selected_digest: str,
        prefix_digest: str,
        selected: Sequence[str],
        dropped: Sequence[str],
        elided: Sequence[str],
        tokens: int,
        layer_counts: Mapping[str, int],
        turn: int | None = None,
        input_artifacts: Sequence[str] = (),
        output_artifacts: Sequence[str] = (),
    ) -> ProvenanceRecord:
        """Which context this turn ran on, and what the budget removed.

        Labels, not text. A dropped label tells a reviewer *what* left the
        window; the body of what left is either in a captured artifact or
        deliberately not retained.
        """
        record = ProvenanceRecord(
            kind=CONTEXT_SELECTION,
            subject=f"run:{self._run_id}",
            policy_id=str(identity.get("policyId") or ""),
            policy_version=str(identity.get("policyVersion") or ""),
            parameters={
                **dict(identity.get("parameters") or {}),
                # The frozen fixture identifies resolved parameters by digest,
                # so two runs under the same policy are comparable without a
                # reader having to diff free-form option maps.
                "paramsDigest": digest_of(dict(identity.get("parameters") or {})),
            },
            input_digest=candidate_digest,
            output_digest=selected_digest,
            labels={
                "selected": list(selected),
                "dropped": list(dropped),
                "elided": list(elided),
                "inputArtifacts": list(input_artifacts),
                "outputArtifacts": list(output_artifacts),
            },
            counts={
                "tokenCount": int(tokens),
                "layerCounts": dict(layer_counts),
                "prefixDigest": prefix_digest,
            },
            artifacts=tuple(input_artifacts) + tuple(output_artifacts),
            turn=turn,
        )
        self.record(record)
        return record

    def record_compaction(
        self,
        *,
        identity: Mapping[str, Any],
        input_digest: str,
        output_digest: str,
        dropped: Sequence[str],
        elided: Sequence[str],
        tokens_before: int,
        tokens_after: int,
        turn: int | None = None,
        artifacts: Sequence[str] = (),
    ) -> ProvenanceRecord | None:
        """Emitted only when compaction actually removed something.

        A turn that fit inside the ceiling was not compacted, and a
        `compaction` record for it would report an operation that never ran.
        """
        if not dropped and not elided:
            return None
        record = ProvenanceRecord(
            kind=COMPACTION,
            subject=f"run:{self._run_id}",
            policy_id=str(identity.get("policyId") or ""),
            policy_version=str(identity.get("policyVersion") or ""),
            parameters={
                **dict(identity.get("parameters") or {}),
                "paramsDigest": digest_of(dict(identity.get("parameters") or {})),
            },
            input_digest=input_digest,
            output_digest=output_digest,
            labels={"dropped": list(dropped), "elided": list(elided)},
            counts={
                "tokensBefore": int(tokens_before),
                "tokensAfter": int(tokens_after),
                # Never negative: compaction removes, it does not add.
                "removedTokens": max(0, int(tokens_before) - int(tokens_after)),
                "dropped": len(dropped),
                "elided": len(elided),
            },
            artifacts=tuple(artifacts),
            turn=turn,
        )
        self.record(record)
        return record

    def record_model_io(
        self,
        *,
        route: Mapping[str, Any],
        input_ref: ArtifactRef | None,
        output_ref: ArtifactRef | None,
        capture_policy: Mapping[str, Any],
        turn: int | None = None,
    ) -> ProvenanceRecord:
        """The RF-95 claim: this run, this turn, this route, these exact bytes.

        Recorded from the refs the writer produced, so a claim can never name
        a digest the artifact writer did not itself obtain from the store.
        """
        artifacts = tuple(
            ref.artifact_id for ref in (input_ref, output_ref) if ref is not None)
        record = ProvenanceRecord(
            kind=MODEL_IO,
            subject=f"run:{self._run_id}",
            policy_id=str(capture_policy.get("policyId") or ""),
            policy_version=str(capture_policy.get("policyVersion") or ""),
            parameters=dict(route),
            input_digest=input_ref.digest if input_ref else "",
            output_digest=output_ref.digest if output_ref else "",
            labels={
                "inputCaptured": bool(input_ref and input_ref.stored),
                "outputCaptured": bool(output_ref and output_ref.stored),
                "retention": str(capture_policy.get("retention") or ""),
            },
            counts={
                "inputBytes": int(input_ref.byte_length) if input_ref else 0,
                "outputBytes": int(output_ref.byte_length) if output_ref else 0,
            },
            artifacts=artifacts,
            turn=turn,
        )
        self.record(record)
        return record

    def record_cache(
        self,
        *,
        reported: Mapping[str, Any] | None,
        source_digest: str = "",
        key_digest: str = "",
        turn: int | None = None,
    ) -> ProvenanceRecord | None:
        """Emit a cache claim only when the provider reported one.

        `None` in, `None` out, no event. This is the *correct* outcome for a
        live invocation, and `test_no_cache_claim_on_live_invocation` exists
        to keep it that way.
        """
        if not reported:
            return None
        record = ProvenanceRecord(
            kind=CACHE,
            subject=f"run:{self._run_id}",
            parameters={
                "cacheId": str(reported.get("id") or reported.get("cacheId") or ""),
                "source": str(reported.get("source") or ""),
                # `hit` stays whatever the provider said. It is only ever read
                # on a record that exists at all, and a record only exists
                # when the provider reported participation -- so `False` here
                # means "asked and missed", never "there was no cache".
                "hit": bool(reported.get("hit", str(reported.get("status") or "") == "hit")),
                "sourceStatus": str(reported.get("status")
                                    or reported.get("sourceStatus") or ""),
                "validation": str(reported.get("validation")
                                  or reported.get("validated") or ""),
            },
            input_digest=key_digest or str(reported.get("keyDigest") or ""),
            output_digest=source_digest or str(reported.get("sourceDigest") or ""),
            counts={"reportedKeys": len(reported)},
            turn=turn,
        )
        self.record(record)
        return record
