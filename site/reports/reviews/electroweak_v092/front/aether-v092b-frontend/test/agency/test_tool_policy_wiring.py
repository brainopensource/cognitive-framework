"""Wiring tests for bounded protocol recovery and tool policy (`ADR-0106`).

The engine consumes an *injected* decoder pipeline (agency never imports pack
middleware) and applies the phase ladder only for presets that declared one.
These tests hold both properties shut against the real kernel fakes.
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from vanguard.packages.agency import EpisodeEngine, RunTermination
from vanguard.packages.agency.episode.tool_policy import derive_phase

from test.kernel import fakes
from vanguard.packages.runtime.protocol_pipeline import default_protocol_pipeline

_DECODERS, _PATCH_DETECTOR, _TRUNCATION_DETECTOR = default_protocol_pipeline()


@dataclass(frozen=True, slots=True)
class _Failure:
    kind: str
    message: str


@dataclass(frozen=True, slots=True)
class _Result:
    ok: bool
    value: Any = None
    error: _Failure | None = None


class CaptureModel:
    """Serves a tape of raw proposal values, recording every request seam."""

    def __init__(self, proposals: Sequence[Any]) -> None:
        self._proposals = list(proposals)
        self._cursor = 0
        self.calls: list[dict[str, Any]] = []

    def propose(self, context: Mapping[str, Any],
                tools: Sequence[Mapping[str, Any]],
                sampling: Mapping[str, Any]) -> _Result:
        self.calls.append({
            "context": dict(context),
            "tools": tuple(dict(tool) for tool in tools),
            "sampling": dict(sampling),
        })
        if self._cursor >= len(self._proposals):
            return _Result(False, error=_Failure(
                "instrument_error", "tape exhausted"))
        value = self._proposals[self._cursor]
        self._cursor += 1
        return _Result(True, value=value)


def _engine(model: CaptureModel, *, tools: Sequence[Mapping[str, Any]] = (),
            preset_mode: str | None = None, **harness_kwargs: Any):
    harness = fakes.build(**harness_kwargs)
    engine = EpisodeEngine(
        kernel=harness.kernel,
        model=model,
        clock=harness.clock,
        events=harness.sink,
        scope=fakes.child_scope(
            actions=frozenset({"fs.read", "patch.apply"})),
        tools=tools,
        preset_mode=preset_mode,
        protocol_decoders=_DECODERS,
        patch_detector=_PATCH_DETECTOR,
        truncation_detector=_TRUNCATION_DETECTOR,
        max_turns=8,
    )
    return harness, engine


class TestDerivePhase(unittest.TestCase):
    def test_phase_ladder(self) -> None:
        self.assertEqual(derive_phase(set()), "inspect")
        self.assertEqual(derive_phase({"fs.read"}), "edit")
        self.assertEqual(derive_phase({"fs.read", "patch.apply"}), "verify")


class TestTruncationContinuationWiring(unittest.TestCase):
    def test_retry_feeds_back_and_bumps_max_tokens(self) -> None:
        """Fix 1: the model observes recovery feedback and a raised token cap."""
        model = CaptureModel([
            # Turn 0: truncated generation (finish_reason length, mid-JSON).
            {"finish_reason": "length", "content": '{"kind": "effect", "ac'},
            # Turn 1 (after continuation retry): a complete proposal.
            {"kind": "finish", "note": "done"},
        ])
        harness, engine = _engine(model, preset_mode=None)

        outcome = engine.run(
            episode_id="ep-trunc", run_id="run-1",
            principal="agent-1", brief="truncation probe")

        self.assertEqual(outcome.terminal, RunTermination.COMPLETED)
        self.assertEqual(len(model.calls), 2)
        # The retry request carries the structured feedback.
        feedback = model.calls[1]["context"].get("recoveryFeedback")
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback["reason"], "OUTPUT_TRUNCATED")
        # ...and the continuation doubled the bounded output cap.
        self.assertEqual(model.calls[1]["sampling"].get("maxTokens"), 8192)
        self.assertNotIn("maxTokens", model.calls[0]["sampling"])


class TestToolPolicyWiring(unittest.TestCase):
    def test_phase_gate_blocks_then_advances(self) -> None:
        """Fix 3: a declared verb outside the phase is retried, not dispatched."""
        model = CaptureModel([
            # Turn 0 (inspect): patch attempt must be gated, not dispatched.
            {"kind": "effect", "action": "patch.apply",
             "args": {"diff": "x"}, "note": "eager patch"},
            # Turn 1 (edit after gated retry): an inspection lands.
            {"kind": "effect", "action": "fs.read",
             "args": {"path": "src/a.py"}, "note": "look first"},
            # Turn 2 (edit phase): the patch is now admissible at the gate.
            {"kind": "finish", "note": "done"},
        ])
        harness, engine = _engine(
            model,
            tools=({"verb": "fs.read"}, {"verb": "patch.apply"}),
            preset_mode="code",
            held_actions=frozenset({"fs.read", "patch.apply"}),
            adapter=fakes.FakeAdapter("fs.read"))

        outcome = engine.run(
            episode_id="ep-gate", run_id="run-1",
            principal="agent-1", brief="phase probe")

        self.assertEqual(outcome.terminal, RunTermination.COMPLETED)
        self.assertEqual(len(model.calls), 3)
        gated = model.calls[1]["context"].get("recoveryFeedback")
        self.assertIsNotNone(gated)
        self.assertEqual(gated["reason"], "DISALLOWED_TOOL_PHASE")
        self.assertEqual(gated["phase"], "inspect")
        self.assertNotIn("patch.apply", gated["allowed_tools"])
        # The gate offered only the phase tools on the retry request.
        offered = {tool.get("verb") for tool in model.calls[1]["tools"]}
        self.assertEqual(offered, {"fs.read"})
        # After the gated turn the feedback is cleared for clean requests.
        self.assertNotIn("recoveryFeedback", model.calls[2]["context"])

    def test_generic_engine_without_preset_is_ungated(self) -> None:
        """No preset declared -> no phase gating (ADR-0060 generic loop)."""
        model = CaptureModel([
            {"kind": "effect", "action": "patch.apply",
             "args": {"diff": "x"}, "note": "eager patch"},
            {"kind": "finish", "note": "done"},
        ])
        harness, engine = _engine(
            model,
            tools=({"verb": "fs.read"}, {"verb": "patch.apply"}),
            preset_mode=None,
            held_actions=frozenset({"fs.read", "patch.apply"}),
            adapter=fakes.FakeAdapter("fs.read"))

        outcome = engine.run(
            episode_id="ep-generic", run_id="run-1",
            principal="agent-1", brief="generic probe")

        self.assertEqual(outcome.terminal, RunTermination.COMPLETED)
        # The eager patch went straight to the kernel (never intercepted by
        # a phase gate); no recovery feedback was injected.
        self.assertEqual(len(model.calls), 2)
        self.assertNotIn("recoveryFeedback", model.calls[1]["context"])

    def test_research_preset_declares_auto(self) -> None:
        from vanguard.packages.agency.episode.tool_policy import resolve_tool_policy

        policy = resolve_tool_policy("inspect", preset_mode="research")
        self.assertEqual(policy.mode, "auto")


if __name__ == "__main__":
    unittest.main()

