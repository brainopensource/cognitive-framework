"""Test doubles for the episode suite.

The **kernel is the real thing** here: an episode test that stubs the kernel
proves nothing about `REQ-EXEC-001`, whose whole claim is that every effect
goes through `Kernel.dispatch`. Only the seams outside the loop are doubled,
and they are the same seams `test/kernel/fakes.py` already injects at.

`ScriptedModel` is a **local cassette double**, not a port. It exists until
`S3-DC-001` lands `ports.model.ModelPort` with its shared fake; the engine
consumes the provider structurally, so the double is deleted and the fake
substituted without touching `agency/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from vanguard.packages.kernel import Event


@dataclass(frozen=True, slots=True)
class _Failure:
    kind: str
    message: str
    retryable: bool = False


@dataclass(frozen=True, slots=True)
class _Result:
    """Structurally identical to `ports.event_store.Result` (`ICD §4`)."""

    ok: bool
    value: Any = None
    error: _Failure | None = None


class ScriptedModel:
    """Serves recorded proposals in tape order; exhaustion is `instrument_error`.

    `CT-33`: exhaustion returns a typed instrument error and never raises, so
    the loop reduces it to `instrument_error` rather than to a task verdict.
    """

    def __init__(self, proposals: Sequence[Any]) -> None:
        self._proposals = list(proposals)
        self._cursor = 0
        self.calls: list[Mapping[str, Any]] = []

    def propose(self, context: Mapping[str, Any],
                tools: Sequence[Mapping[str, Any]],
                sampling: Mapping[str, Any]) -> _Result:
        self.calls.append(dict(context))
        if self._cursor >= len(self._proposals):
            return _Result(False, error=_Failure(
                "instrument_error", "cassette exhausted: no more recorded proposals"))
        proposal = self._proposals[self._cursor]
        self._cursor += 1
        return _Result(True, value=proposal)


class RaisingModel:
    """A provider that violates `ICD §4` by raising. Still an instrument error."""

    def propose(self, context: Any, tools: Any, sampling: Any) -> Any:
        raise ConnectionError("provider socket closed")


class RecordingEvaluator:
    """An evaluator the episode must never reach (`ICD §3`, `VG-03 §6.1`).

    It is injected nowhere. The suite asserts it stays uncalled *and* that no
    evaluator symbol is reachable from `agency/` at all — the second assertion
    is the one that cannot be satisfied by an unreachable defence.
    """

    def __init__(self) -> None:
        self.calls: list[Any] = []

    def evaluate(self, run_ref: Any, protocol: Any) -> Any:
        self.calls.append(run_ref)
        raise AssertionError("an episode must not request its own evaluation")


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def emit(self, event: Event) -> None:
        self.events.append(event)


def effect(action: str = "fs.write", *, path: str = "/workspace/src/a.ts",
           **reservation: int) -> Mapping[str, Any]:
    """A recorded effect proposal."""
    return {
        "kind": "effect",
        "action": action,
        "resource": {"kind": "fs", "root": "/workspace", "paths": [path]},
        "args": {"path": path, "bytes": "12"},
        "reservation": dict(reservation) or {"usd_micros": 500, "millis": 1000},
    }


def finish(note: str = "done") -> Mapping[str, Any]:
    return {"kind": "finish", "note": note}


def abstain(note: str = "insufficient grounds") -> Mapping[str, Any]:
    return {"kind": "abstain", "note": note}


def escalate(note: str = "needs a human") -> Mapping[str, Any]:
    return {"kind": "escalate", "note": note}
