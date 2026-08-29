"""Checkpointed projection reconstruction (`ADR-0098 Decision 6`, `RF-96`).

Cold folding a long ledger is correct and slow: every restart pays for the
whole history again. A checkpoint is the standard remedy -- and the standard
way it goes wrong is that it becomes a *second source of truth*. A checkpoint
that is trusted because it exists silently substitutes stale or corrupt state
for the events, and nothing downstream can tell.

So this module treats a checkpoint as a **cache with a proof obligation**, not
as state. Four things are re-established before a restored fold is used at all:

* the blob is present, and its bytes re-digest to the address they were stored
  under -- a store whose addresses can lie is caught here, not downstream;
* the decoded state re-digests to the `state_digest` the checkpoint pinned, so
  a decoder that lost a field is a failure rather than a quiet divergence;
* the reducer and event-schema **pins** match the ones running now, because a
  checkpoint written by a different reducer is a fold of different rules;
* the tail replayed on top starts exactly at `last_seq + 1`.

Any of those failing is **not** an error the caller has to handle: it falls
back to the full cold fold and says why. That is the fail-closed direction --
the slow answer is always available and always correct, so there is never a
reason to accept an unproven fast one. The reverse (raising, or returning
partial state) would turn a corrupt cache into an outage or, worse, into a
wrong answer.

`capability` and `verification` are kept apart exactly as `ADR-0096 §14 / C-04`
requires. Restoring from a checkpoint establishes `from_checkpoint`
*capability*; it never on its own establishes `verified`. Verification means
this run also cold-folded and the two digests agreed -- an executed receipt,
not a prerequisite.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..domain.ledger.events import EventEnvelope
from ..domain.ledger.reducer import (
    REDUCER_VERSION,
    ReducerError,
    initial_state,
    reduce_batch,
)
from ..domain.ledger.state import (
    ApprovalRecord,
    ArtifactRecord,
    BudgetLeaseState,
    ChildRecord,
    EffectRecord,
    EpisodeState,
    EvidenceRecord,
    LedgerState,
    PluginRecord,
    VerdictRecord,
)
from ..ports.blob_store import BlobStorePort
from .ledger_emitter import EVENT_SCHEMA_VERSION

__all__ = [
    "CHECKPOINT_SCHEMA_VERSION",
    "Checkpoint",
    "CheckpointManager",
    "CheckpointPins",
    "CheckpointValidationError",
    "Reconstruction",
    "decode_state",
    "encode_state",
]

#: The checkpoint envelope's own version. Bumping it invalidates every prior
#: checkpoint by pin mismatch, which is the intended effect: an old blob
#: decoded by new rules is the failure mode this pin exists to prevent.
CHECKPOINT_SCHEMA_VERSION = "mhf.checkpoint/1"

#: Nested record types by the field that holds them. Encoding is generic over
#: the dataclass, so a field added to `LedgerState` cannot be silently dropped
#: from a checkpoint -- `decode_state` reconstructs by field name and the
#: state-digest check fails loudly if anything went missing.
_RECORD_TYPES: Mapping[str, type] = {
    "leases": BudgetLeaseState,
    "effects": EffectRecord,
    "artifacts": ArtifactRecord,
    "evidence_claims": EvidenceRecord,
    "approvals": ApprovalRecord,
    "verdicts": VerdictRecord,
    "plugins": PluginRecord,
    "children": ChildRecord,
}

#: `LedgerState` fields that are ordered tuples of opaque mappings. They stay
#: tuples through a round trip: JSON has only arrays, and a list where the
#: reducer expects a tuple changes the canonical form and therefore the digest.
_TUPLE_FIELDS = frozenset({
    "revoked_grants",
    "denials",
    "observations",
    "proposals",
    "conflicts",
    "goals",
    "plan_revisions",
    "strategy_changes",
    "progress_assessments",
    "context_compactions",
    "unknown_events",
})


class CheckpointValidationError(ValueError):
    """A checkpoint failed a proof obligation and must not be trusted.

    Raised only by `CheckpointManager.load`, which callers use when they want
    the reason. `reconstruct` never propagates it: it falls back to the cold
    fold, because a bad cache is not an execution failure.
    """


@dataclass(frozen=True, slots=True)
class CheckpointPins:
    """What the fold that produced a checkpoint was computed *by*.

    Not metadata. A checkpoint is a memo of `reduce_batch` under a particular
    reducer over a particular event vocabulary; reusing it under different
    rules answers a question nobody asked.
    """

    reducer_version: str
    event_schema_version: str
    checkpoint_schema_version: str = CHECKPOINT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "reducerVersion": self.reducer_version,
            "eventSchemaVersion": self.event_schema_version,
            "checkpointSchemaVersion": self.checkpoint_schema_version,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "CheckpointPins":
        return cls(
            reducer_version=str(raw.get("reducerVersion", "")),
            event_schema_version=str(raw.get("eventSchemaVersion", "")),
            checkpoint_schema_version=str(
                raw.get("checkpointSchemaVersion", CHECKPOINT_SCHEMA_VERSION)),
        )


@dataclass(frozen=True, slots=True)
class Checkpoint:
    """A durable pointer to a folded state, plus everything needed to doubt it.

    Digests and identities only. The state itself lives in the blob store,
    which is the whole point: an append-only ledger is no place for a
    snapshot that will be superseded on the next turn.
    """

    blob_digest: str
    state_digest: str
    last_seq: int
    event_count: int
    pins: CheckpointPins
    run_id: Optional[str] = None
    episode_id: Optional[str] = None
    branch_id: str = "main"
    byte_length: int = 0

    def to_fact(self) -> dict[str, Any]:
        """The small wire form a ledger fact or trajectory may carry."""
        return {
            "blobDigest": self.blob_digest,
            "stateDigest": self.state_digest,
            "lastSeq": int(self.last_seq),
            "eventCount": int(self.event_count),
            "branchId": self.branch_id,
            "byteLength": int(self.byte_length),
            "runId": self.run_id,
            "episodeId": self.episode_id,
            "pins": self.pins.to_dict(),
        }

    @classmethod
    def from_fact(cls, raw: Mapping[str, Any]) -> "Checkpoint":
        return cls(
            blob_digest=str(raw.get("blobDigest", "")),
            state_digest=str(raw.get("stateDigest", "")),
            last_seq=int(raw.get("lastSeq", 0)),
            event_count=int(raw.get("eventCount", 0)),
            pins=CheckpointPins.from_dict(raw.get("pins") or {}),
            run_id=raw.get("runId"),
            episode_id=raw.get("episodeId"),
            branch_id=str(raw.get("branchId", "main")),
            byte_length=int(raw.get("byteLength", 0)),
        )


@dataclass(frozen=True, slots=True)
class Reconstruction:
    """The outcome of rebuilding state, and how much of it is actually proven.

    `capability` and `verification` never collapse into one field. `C-04`:
    "WAL presence is not proof of full cold reconstruction" -- and neither is
    a checkpoint that loaded cleanly.
    """

    state: Optional[LedgerState]
    #: "none" | "from_checkpoint" | "full_cold"
    capability: str
    #: "unverified" | "verified"
    verification: str = "unverified"
    events_replayed: int = 0
    checkpoint: Optional[Checkpoint] = None
    #: Why the checkpoint was not used. Empty when one was, or when none was
    #: offered -- a fallback that does not say why is indistinguishable from
    #: a cold fold that was always going to happen.
    fallback_reason: str = ""

    @property
    def state_digest(self) -> str:
        return self.state.digest() if self.state is not None else ""

    def to_claim(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "verification": self.verification,
            "eventsReplayed": int(self.events_replayed),
            "stateDigest": self.state_digest,
            **({"fallbackReason": self.fallback_reason} if self.fallback_reason else {}),
            **({"checkpoint": self.checkpoint.to_fact()} if self.checkpoint else {}),
        }


# -- state serialisation --------------------------------------------------


def _encode_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: _encode_value(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, Mapping):
        return {str(k): _encode_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_encode_value(item) for item in value]
    return value


def encode_state(state: LedgerState) -> dict[str, Any]:
    """A lossless, JSON-shaped view of `LedgerState`.

    Deliberately *not* `to_canonical_dict`: that form is built for the digest
    and drops what the digest does not need, so decoding it would silently
    return a smaller state. This walks the dataclass by field name instead, so
    the round trip is total by construction and provably so -- a lost field
    changes the digest and `load` refuses the checkpoint.
    """
    return {
        "schemaVersion": CHECKPOINT_SCHEMA_VERSION,
        "state": {f.name: _encode_value(getattr(state, f.name)) for f in fields(state)},
    }


def _decode_record(record_type: type, raw: Any) -> Any:
    if not isinstance(raw, Mapping):
        return raw
    names = {f.name for f in fields(record_type)}
    kwargs = {
        name: (tuple(value) if isinstance(value, list) else value)
        for name, value in raw.items()
        if name in names
    }
    if record_type is EpisodeState and isinstance(kwargs.get("state_transitions"), tuple):
        kwargs["state_transitions"] = tuple(
            tuple(item) if isinstance(item, list) else item
            for item in kwargs["state_transitions"]
        )
    return record_type(**kwargs)


def decode_state(raw: Mapping[str, Any]) -> LedgerState:
    """Rebuild `LedgerState` from `encode_state` output.

    Unknown keys are dropped rather than passed through: a checkpoint written
    by a newer build must not construct a `LedgerState` this build cannot
    describe. The pin check normally rejects that case first; this is the
    second line, and its failure surfaces as a digest mismatch.
    """
    body = raw.get("state")
    if not isinstance(body, Mapping):
        raise CheckpointValidationError("checkpoint blob has no 'state' object")
    known = {f.name for f in fields(LedgerState)}
    kwargs: dict[str, Any] = {}
    for name, value in body.items():
        if name not in known:
            continue
        if name == "episode":
            kwargs[name] = _decode_record(EpisodeState, value)
        elif name in _RECORD_TYPES and isinstance(value, Mapping):
            record_type = _RECORD_TYPES[name]
            kwargs[name] = {
                str(k): _decode_record(record_type, v) for k, v in value.items()
            }
        elif name in _TUPLE_FIELDS and isinstance(value, list):
            kwargs[name] = tuple(value)
        else:
            kwargs[name] = value
    try:
        return LedgerState(**kwargs)
    except TypeError as exc:  # pragma: no cover -- guarded by `known` filter
        raise CheckpointValidationError(f"checkpoint state is not decodable: {exc}") from exc


class CheckpointManager:
    """Writes checkpoints, and refuses to believe them without proof.

    The manager owns no event kind and no authority. It captures through the
    ordinary `ArtifactWriter` when one is supplied, so a checkpoint is an
    ordinary `checkpoint_state` artifact -- blob first, fact second, store
    computes the address -- rather than a second durability mechanism with its
    own failure modes.
    """

    def __init__(
        self,
        blobs: BlobStorePort,
        *,
        artifacts: Any | None = None,
        reducer_version: str = REDUCER_VERSION,
        event_schema_version: str = EVENT_SCHEMA_VERSION,
    ) -> None:
        self._blobs = blobs
        self._artifacts = artifacts
        self._pins = CheckpointPins(
            reducer_version=reducer_version,
            event_schema_version=event_schema_version,
        )

    @property
    def pins(self) -> CheckpointPins:
        return self._pins

    # -- write ------------------------------------------------------------

    def capture(
        self,
        state: LedgerState,
        *,
        turn: int | None = None,
        required: bool | None = False,
    ) -> Optional[Checkpoint]:
        """Persist `state` and return the pointer, or `None` if it was not stored.

        `None` is the honest answer under `digests_only` retention or an
        unauthorised capture policy: there is no blob to point at, and a
        pointer to bytes nobody kept is exactly the dangling reference
        `artifacts.py` refuses to emit. A run without a checkpoint cold-folds,
        which is correct and merely slower.

        Capture is optional by default (`required=False`) because a checkpoint
        is a cache: failing an evidentiary run over an unwritten cache would
        be the fail-closed direction pointed the wrong way.
        """
        payload = encode_state(state)
        if self._artifacts is not None:
            ref = self._artifacts.capture(
                "checkpoint_state", payload, required=required, turn=turn,
                labels={"lastSeq": str(state.last_seq or ""),
                        "stateDigest": state.digest()},
            )
            if not ref.stored:
                return None
            blob_digest, byte_length = ref.digest, ref.byte_length
        else:
            from ..domain.canonicalisation.jcs import canonicalise

            data = canonicalise(payload).encode("utf-8")
            stored = self._blobs.put(data)
            if not stored.ok or not stored.value:
                return None
            blob_digest, byte_length = str(stored.value), len(data)

        return Checkpoint(
            blob_digest=blob_digest,
            state_digest=state.digest(),
            last_seq=int(state.last_seq) if state.last_seq is not None else 0,
            event_count=int(state.event_count),
            pins=self._pins,
            run_id=state.run_id,
            episode_id=state.episode_id,
            branch_id=state.branch_id,
            byte_length=byte_length,
        )

    # -- read -------------------------------------------------------------

    def load(self, checkpoint: Checkpoint) -> LedgerState:
        """Return the folded state, having earned the right to return it.

        Raises `CheckpointValidationError` on every failure. Callers that want
        a fallback use `reconstruct`, which is the only supported production
        path.
        """
        pins = checkpoint.pins
        if pins.checkpoint_schema_version != self._pins.checkpoint_schema_version:
            raise CheckpointValidationError(
                f"checkpoint schema pin {pins.checkpoint_schema_version!r} != "
                f"{self._pins.checkpoint_schema_version!r}")
        if pins.reducer_version != self._pins.reducer_version:
            raise CheckpointValidationError(
                f"reducer pin {pins.reducer_version!r} != {self._pins.reducer_version!r}; "
                "a fold under different rules is not this fold")
        if pins.event_schema_version != self._pins.event_schema_version:
            raise CheckpointValidationError(
                f"event schema pin {pins.event_schema_version!r} != "
                f"{self._pins.event_schema_version!r}")

        if not checkpoint.blob_digest:
            raise CheckpointValidationError("checkpoint names no blob")
        if not self._blobs.has(checkpoint.blob_digest):
            raise CheckpointValidationError(
                f"checkpoint blob {checkpoint.blob_digest} is absent")
        fetched = self._blobs.get(checkpoint.blob_digest)
        if not fetched.ok or fetched.value is None:
            message = fetched.error.message if fetched.error else "blob read rejected"
            raise CheckpointValidationError(
                f"checkpoint blob {checkpoint.blob_digest} unreadable: {message}")

        data = bytes(fetched.value)
        actual = "sha256:" + hashlib.sha256(data).hexdigest()
        if actual != checkpoint.blob_digest:
            raise CheckpointValidationError(
                f"checkpoint blob digest mismatch: stored at {checkpoint.blob_digest}, "
                f"bytes hash to {actual}")

        import json

        try:
            raw = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise CheckpointValidationError(
                f"checkpoint blob is not decodable JSON: {exc}") from exc
        if not isinstance(raw, Mapping):
            raise CheckpointValidationError("checkpoint blob is not an object")

        state = decode_state(raw)
        recomputed = state.digest()
        if recomputed != checkpoint.state_digest:
            raise CheckpointValidationError(
                f"checkpoint state digest mismatch: pinned {checkpoint.state_digest}, "
                f"decoded state digests to {recomputed}")
        return state

    def reconstruct(
        self,
        envelopes: Sequence[EventEnvelope] | Iterable[EventEnvelope],
        *,
        checkpoint: Optional[Checkpoint] = None,
        verify: bool = False,
    ) -> Reconstruction:
        """Rebuild state, preferring a *proven* checkpoint and never an unproven one.

        With `verify=True` the cold fold runs as well and the two digests are
        compared. Only that comparison produces `verification="verified"`, and
        a mismatch discards the checkpoint result -- the events are the truth
        and the checkpoint is the cache, so the cache is what loses.
        """
        ordered = list(envelopes)

        if checkpoint is None:
            return self._cold(ordered)

        try:
            base = self.load(checkpoint)
        except CheckpointValidationError as exc:
            cold = self._cold(ordered)
            return _with_reason(cold, f"checkpoint_rejected: {exc}")

        tail = [ev for ev in ordered if _seq_of(ev) > checkpoint.last_seq]
        try:
            warm = reduce_batch(base, tail)
        except ReducerError as exc:
            # The checkpoint's fold is not a prefix of this history -- it is
            # ahead of the tail, or from a different chain entirely. Folding
            # the tail onto it is meaningless, and raising would let a bad
            # cache take down a run whose events are perfectly intact.
            cold = self._cold(ordered)
            return _with_reason(cold, f"checkpoint_not_a_prefix: {exc}")

        if not verify:
            return Reconstruction(
                state=warm,
                capability="from_checkpoint",
                verification="unverified",
                events_replayed=len(tail),
                checkpoint=checkpoint,
            )

        cold = self._cold(ordered)
        if cold.state is None or cold.state.digest() != warm.digest():
            return _with_reason(
                cold,
                "parity_mismatch: checkpoint fold "
                f"{warm.digest()} != cold fold {cold.state_digest}",
            )
        return Reconstruction(
            state=warm,
            capability="from_checkpoint",
            verification="verified",
            events_replayed=len(tail),
            checkpoint=checkpoint,
        )

    def _cold(self, envelopes: Sequence[EventEnvelope]) -> Reconstruction:
        """The always-available answer. `capability="none"` only when there is
        genuinely nothing to fold -- which is `UNDETERMINABLE`, never an empty
        state passed off as a complete one."""
        if not envelopes:
            return Reconstruction(state=None, capability="none", events_replayed=0)
        state = reduce_batch(initial_state(), envelopes)
        return Reconstruction(
            state=state, capability="full_cold", events_replayed=len(envelopes))

    def restore_latest(
        self,
        run_id: str,
        event_store: Any,
        checkpoint: Optional[Checkpoint] = None,
        verify: bool = False,
    ) -> tuple[Optional[LedgerState], int]:
        """Restore latest folded state using lazy delta suffix decoding (EVO-11).

        1. If checkpoint is passed, load and verify its digest and pins.
        2. If valid, query event_store strictly for delta events: EventRange(run_id=run_id, after_seq=str(checkpoint.last_seq)).
        3. Fold delta events onto the deserialized checkpoint base state.
        4. If verify=True, run cold-fold from seq=0 and assert parity.
        5. If checkpoint load, digest validation, or delta fold fails, fail closed to cold-fold from seq=0.

        Returns (state, events_replayed_count).
        """
        from ..ports.event_store import EventRange

        if checkpoint is not None:
            try:
                base = self.load(checkpoint)
                delta_res = event_store.read(EventRange(run_id=run_id, after_seq=str(checkpoint.last_seq)))
                if delta_res.ok and delta_res.value is not None:
                    delta_events = list(delta_res.value)
                    warm = reduce_batch(base, delta_events)
                    if not verify:
                        return warm, len(delta_events)

                    all_res = event_store.read(EventRange(run_id=run_id))
                    all_events = list(all_res.value or [])
                    cold_state = reduce_batch(initial_state(), all_events) if all_events else None
                    if cold_state is not None and cold_state.digest() == warm.digest():
                        return warm, len(delta_events)
            except Exception:
                pass

        all_res = event_store.read(EventRange(run_id=run_id))
        all_events = list(all_res.value or [])
        if not all_events:
            return None, 0
        cold_state = reduce_batch(initial_state(), all_events)
        return cold_state, len(all_events)


def _with_reason(outcome: Reconstruction, reason: str) -> Reconstruction:
    return Reconstruction(
        state=outcome.state,
        capability=outcome.capability,
        verification=outcome.verification,
        events_replayed=outcome.events_replayed,
        checkpoint=None,
        fallback_reason=reason,
    )


def _seq_of(envelope: EventEnvelope) -> int:
    try:
        return int(envelope.seq)
    except (TypeError, ValueError):
        return -1
