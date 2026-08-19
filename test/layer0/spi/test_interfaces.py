from __future__ import annotations

import unittest

from layer0.spi.fakes import (
    EchoToolkit,
    FixedGate,
    IdentityContext,
    InMemoryEngine,
    ScriptedPlanner,
)
from layer0.spi.interfaces import (
    IContextManager,
    IEvaluationGate,
    IMemoryEngine,
    IPlanner,
    IToolkit,
)
from layer0.spi.result import Ok
from layer0.spi.types_gen import (
    EffectContext,
    EffectRequest,
    EpisodeView,
    GateDecision,
    MemoryQuery,
    MemoryRecord,
    Proposal,
    Reservation,
    SinkClass,
)


def _budget() -> Reservation:
    return Reservation(0, 0, 16, 0, 4, 1)


def _request() -> EffectRequest:
    return EffectRequest(
        verb="echo",
        args={},
        selector={"kind": "generic", "uriPattern": "echo://x"},
        sink=SinkClass.ADVISORY,
        reservation=_budget(),
    )


class SpiContractTests(unittest.TestCase):
    def test_protocols_expose_spi_version(self) -> None:
        for cls in (ScriptedPlanner, EchoToolkit, InMemoryEngine, IdentityContext, FixedGate):
            self.assertEqual(cls.spi_version, "1.0")

    def test_scripted_planner_emits_then_exhausts(self) -> None:
        planner: IPlanner = ScriptedPlanner((Proposal(requests=(_request(),)),))
        view = EpisodeView("r", "e", 0, "goal")
        first = planner.plan(view, _budget())
        self.assertIsInstance(first, Ok)
        second = planner.plan(view, _budget())
        self.assertEqual(second.code, "empty_script")  # type: ignore[union-attr]

    def test_echo_toolkit_and_identity_context(self) -> None:
        toolkit: IToolkit = EchoToolkit()
        self.assertIn("echo", toolkit.verbs())
        receipt = toolkit.execute(_request(), EffectContext("p", "r"))
        self.assertIsInstance(receipt, Ok)
        context: IContextManager = IdentityContext()
        bundle = context.compile(EpisodeView("r", "e", 0, "goal"), 128)
        self.assertIsInstance(bundle, Ok)

    def test_memory_and_gate_fakes(self) -> None:
        memory: IMemoryEngine = InMemoryEngine()
        written = memory.write(MemoryRecord(kind="episodic", text="hello world"))
        self.assertIsInstance(written, Ok)
        hits = memory.recall(MemoryQuery(text="hello"), 32)
        self.assertIsInstance(hits, Ok)
        self.assertEqual(len(hits.value), 1)  # type: ignore[union-attr]
        gate: IEvaluationGate = FixedGate(GateDecision.PASS)
        self.assertEqual(gate.gate(()), GateDecision.PASS)
        self.assertIn("kv", memory.capabilities())
