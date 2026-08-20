"""Wave-2 2.1-C: the five SPI Protocols live at `ports/spi.py`, not `layer0`.

Each first-party adapter that used to implement `layer0.spi.interfaces`
implicitly now conforms to the canonical, `ports`-owned Protocol -- checked
here with `isinstance` (the Protocols are `@runtime_checkable`), against the
real adapters, not fakes. ADR-M0-03: exactly five: no sixth SPI.
"""

from __future__ import annotations

import tempfile
import unittest

from vanguard.packages.adapters.context.window import DefaultContextAdapter
from vanguard.packages.adapters.evaluators.gate import ExteriorJudgeAdapter
from vanguard.packages.adapters.models.planner import DefaultPlannerAdapter
from vanguard.packages.adapters.sandbox.toolkit import SubprocessToolkitAdapter
from vanguard.packages.adapters.stores.memory_engine import LocalFileMemoryAdapter
from vanguard.packages.ports import spi
from vanguard.packages.ports.event_store import Result as PortResult


class _StubModel:
    def propose(self, context, tools, sampling) -> PortResult:
        _ = context, tools, sampling
        return PortResult.success({"text": "done", "toolCalls": []})


class SpiProtocolIdentityTests(unittest.TestCase):
    def test_exactly_five_protocols_no_sixth_spi(self) -> None:
        self.assertEqual(
            set(spi.__all__),
            {"IPlanner", "IContextManager", "IToolkit", "IMemoryEngine", "IEvaluationGate"},
        )

    def test_layer0_result_is_the_same_object_not_a_second_result(self) -> None:
        """2.1-A: `layer0/spi/result.py` is a re-export, so an `Ok` a real
        adapter returns and an `Ok` checked against via the old import path
        are one class -- not two structurally-identical strangers.
        """
        from layer0.spi.result import Ok as LegacyOk
        from vanguard.packages.domain.wire.result import Ok as CanonicalOk

        self.assertIs(LegacyOk, CanonicalOk)


class RealAdapterConformanceTests(unittest.TestCase):
    """Real first-party adapters (not fakes) satisfy their Protocol by structure."""

    def test_default_planner_adapter_is_an_iplanner(self) -> None:
        planner: spi.IPlanner = DefaultPlannerAdapter(_StubModel())
        self.assertIsInstance(planner, spi.IPlanner)

    def test_default_context_adapter_is_an_icontext_manager(self) -> None:
        context: spi.IContextManager = DefaultContextAdapter()
        self.assertIsInstance(context, spi.IContextManager)

    def test_local_file_memory_adapter_is_an_imemory_engine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine: spi.IMemoryEngine = LocalFileMemoryAdapter(tmp)
            self.assertIsInstance(engine, spi.IMemoryEngine)

    def test_exterior_judge_adapter_is_an_ievaluation_gate(self) -> None:
        gate: spi.IEvaluationGate = ExteriorJudgeAdapter(
            "/tmp/does-not-need-to-exist.sock", public_key=b"k" * 32, key_id="k")
        self.assertIsInstance(gate, spi.IEvaluationGate)

    def test_subprocess_toolkit_adapter_is_an_itoolkit(self) -> None:
        # Structural check only -- no live UDS peer needed to satisfy the
        # Protocol shape. The behavioural conformance (a real plugin cell)
        # is exercised in
        # `test/adapters/test_mhf_spi_adapters.py::SubprocessToolkitAdapterTests`
        # against this same `ports.spi.IToolkit`.
        toolkit: spi.IToolkit = SubprocessToolkitAdapter("/tmp/does-not-need-to-exist.sock")
        self.assertIsInstance(toolkit, spi.IToolkit)


if __name__ == "__main__":
    unittest.main()
