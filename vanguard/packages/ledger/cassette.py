"""Deterministic cassette recorder and player for the model provider port.

Owning contract: VG-01 §4.1, VG-04 §8 / `CT-33`, GTS-13C T3.8.

Invariants:
- Record writes live provider responses to cassette; replay serves them deterministically.
- Byte-identical reproduction: replaying a cassette reproduces the exact recorded model proposals.
- Zero I/O and zero network access during cassette replay.
- CT-33 compliant: cassette exhaustion or unknown requests return typed instrument errors, never throw.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence, TextIO, Union

from ..domain.canonicalisation.digest import digest_of
from ..domain.canonicalisation.jcs import canonicalise
from ..ports.event_store import PortFailure, Result

__all__ = [
    "CassetteRecord",
    "Cassette",
    "CassetteRecorder",
    "CassettePlayer",
]


@dataclass(frozen=True, slots=True)
class CassetteRecord:
    """A single recorded model interaction."""

    request_digest: str
    context: Mapping[str, Any]
    tools: Sequence[Mapping[str, Any]]
    sampling: Mapping[str, Any]
    proposal: Mapping[str, Any]
    recorded_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "requestDigest": self.request_digest,
            "context": dict(self.context),
            "tools": [dict(t) for t in self.tools],
            "sampling": dict(self.sampling),
            "proposal": dict(self.proposal),
            "recordedAt": self.recorded_at,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CassetteRecord:
        return cls(
            request_digest=data["requestDigest"],
            context=data["context"],
            tools=data.get("tools", []),
            sampling=data.get("sampling", {}),
            proposal=data["proposal"],
            recorded_at=data.get("recordedAt", "2026-08-15T00:00:00.000Z"),
        )


class Cassette:
    """An ordered cassette container holding recorded model interactions."""

    def __init__(self, records: Optional[Sequence[CassetteRecord]] = None) -> None:
        self.records: list[CassetteRecord] = list(records or [])

    def add_record(
        self,
        context: Mapping[str, Any],
        tools: Sequence[Mapping[str, Any]],
        sampling: Mapping[str, Any],
        proposal: Mapping[str, Any],
        recorded_at: str = "2026-08-15T00:00:00.000Z",
    ) -> CassetteRecord:
        req_dict = {
            "context": dict(context),
            "tools": [dict(t) for t in tools],
            "sampling": dict(sampling),
        }
        req_digest = digest_of(req_dict)
        record = CassetteRecord(
            request_digest=req_digest,
            context=context,
            tools=tools,
            sampling=sampling,
            proposal=proposal,
            recorded_at=recorded_at,
        )
        self.records.append(record)
        return record

    def to_json(self) -> str:
        data = [r.to_dict() for r in self.records]
        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> Cassette:
        data = json.loads(json_str)
        records = [CassetteRecord.from_dict(d) for d in data]
        return cls(records)

    def digest(self) -> str:
        """Cumulative sha256 digest of the entire cassette."""
        return digest_of([r.to_dict() for r in self.records])


class CassetteRecorder:
    """Records interactions with a live ModelProvider to a Cassette."""

    def __init__(self, cassette: Optional[Cassette] = None) -> None:
        self.cassette = cassette or Cassette()

    def record_interaction(
        self,
        context: Mapping[str, Any],
        tools: Sequence[Mapping[str, Any]],
        sampling: Mapping[str, Any],
        proposal: Mapping[str, Any],
        recorded_at: str = "2026-08-15T00:00:00.000Z",
    ) -> CassetteRecord:
        return self.cassette.add_record(context, tools, sampling, proposal, recorded_at)


class CassettePlayer:
    """Deterministic, zero-I/O model provider player serving recorded proposals from a cassette."""

    def __init__(self, cassette: Cassette, match_mode: str = "tape") -> None:
        """
        match_mode:
            'tape': serves interactions in sequential tape order (default)
            'digest': matches by canonical request digest
        """
        self.cassette = cassette
        self.match_mode = match_mode
        self._cursor = 0
        self._by_digest: dict[str, list[CassetteRecord]] = {}
        for r in cassette.records:
            if r.request_digest not in self._by_digest:
                self._by_digest[r.request_digest] = []
            self._by_digest[r.request_digest].append(r)
        self._digest_cursors: dict[str, int] = {k: 0 for k in self._by_digest}

    def propose(
        self,
        context: Mapping[str, Any],
        tools: Sequence[Mapping[str, Any]],
        sampling: Mapping[str, Any],
    ) -> Result[Mapping[str, Any]]:
        """Serve proposal deterministically from cassette."""
        if self.match_mode == "tape":
            if self._cursor >= len(self.cassette.records):
                return Result.fail(
                    kind="instrument_error",
                    message="Cassette exhausted: no more recorded interactions on tape",
                )
            record = self.cassette.records[self._cursor]
            self._cursor += 1
            return Result.success(dict(record.proposal))

        # digest matching mode
        req_dict = {
            "context": dict(context),
            "tools": [dict(t) for t in tools],
            "sampling": dict(sampling),
        }
        req_digest = digest_of(req_dict)
        matching = self._by_digest.get(req_digest)
        if not matching:
            return Result.fail(
                kind="instrument_error",
                message=f"No recorded cassette interaction matching request digest {req_digest}",
            )

        cur_pos = self._digest_cursors.get(req_digest, 0)
        if cur_pos >= len(matching):
            return Result.fail(
                kind="instrument_error",
                message=f"Cassette exhausted for request digest {req_digest}",
            )

        record = matching[cur_pos]
        self._digest_cursors[req_digest] = cur_pos + 1
        return Result.success(dict(record.proposal))

    def reset(self) -> None:
        """Reset player playback cursor to the beginning."""
        self._cursor = 0
        self._digest_cursors = {k: 0 for k in self._by_digest}
