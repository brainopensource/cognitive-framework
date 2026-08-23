"""First-party SPI adapters (M2). Do not import sibling adapter families."""

from __future__ import annotations

import dataclasses
import json
import os
import socket
import tempfile
import threading
import unittest
from typing import Any, Mapping, Sequence

from cryptography.hazmat.primitives.asymmetric import ed25519

from vanguard.packages.domain.wire.result import Err, Ok
from vanguard.packages.domain.wire.types_gen import (
    ClaimRef,
    EffectContext,
    EffectFailure,
    EffectRequest,
    EpisodeOutcome,
    EpisodeView,
    EvaluationSubject,
    GateDecision,
    MemoryQuery,
    MemoryRecord,
    OracleSpec,
    Proposal,
    Receipt,
    Reservation,
    SignedVerdict,
    SinkClass,
    TrajectoryRef,
)
from vanguard.packages.adapters.evaluators.gate import ExteriorJudgeAdapter
from vanguard.packages.adapters.evaluators.signing import VerdictSigner
from vanguard.packages.adapters.models.planner import DefaultPlannerAdapter
from vanguard.packages.adapters.sandbox.toolkit import SubprocessToolkitAdapter
from vanguard.packages.adapters.stores.memory_engine import LocalFileMemoryAdapter
from vanguard.packages.ports.event_store import Result as PortResult
from vanguard.packages.ports.model import ModelPort

from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter
from vanguard.packages.runtime.registry.broker import PluginIsolationBroker
from vanguard.packages.runtime.registry.sandbox import SandboxLimits
from vanguard.packages.adapters.context.window import DefaultContextAdapter

_BUDGET = Reservation(usd_micros=1, millis=1000, tokens=128, bytes=1024, turns=4, depth=1)
_LIMITS = SandboxLimits(
    cpu_seconds=2,
    address_space_bytes=256 * 1024 * 1024,
    max_open_files=32,
    max_processes=64,
)


class _ScriptedModel:
    """Local ModelPort double — not adapters.models, to respect family isolation."""

    def __init__(self, proposal: Mapping[str, Any]) -> None:
        self._proposal = proposal

    def propose(self, context, tools, sampling) -> PortResult[Mapping[str, Any]]:
        _ = context, tools, sampling
        return PortResult.success(dict(self._proposal))


class DefaultPlannerAdapterTests(unittest.TestCase):
    def test_single_turn_wraps_model_tool_call(self) -> None:
        model: ModelPort = _ScriptedModel(
            {
                "text": "do it",
                "toolCalls": [{"name": "echo", "arguments": {"text": "hi"}}],
            }
        )
        planner = DefaultPlannerAdapter(
            model,
            tools=({"verb": "echo", "schema": {"type": "object"}},),
        )
        view = EpisodeView(run_id="r", episode_id="e", turn=0, goal="say hi")
        result = planner.plan(view, _BUDGET)
        self.assertIsInstance(result, Ok)
        assert isinstance(result, Ok)
        self.assertEqual(len(result.value.requests), 1)
        self.assertEqual(result.value.requests[0].verb, "echo")
        planner.observe((), view)
        reflected = planner.reflect(EpisodeOutcome(status="ok"), TrajectoryRef(digest="sha256:" + "0" * 64))
        self.assertIsInstance(reflected, Ok)

    def test_instrument_error_on_empty_model(self) -> None:
        class Boom:
            def propose(self, context, tools, sampling) -> PortResult[Mapping[str, Any]]:
                _ = context, tools, sampling
                return PortResult.fail("instrument_error", "down")

        planner = DefaultPlannerAdapter(Boom())
        result = planner.plan(
            EpisodeView(run_id="r", episode_id="e", turn=0, goal="x"),
            _BUDGET,
        )
        self.assertIsInstance(result, Err)
        assert isinstance(result, Err)
        self.assertTrue(result.instrument_error)


class LocalFileMemoryAdapterTests(unittest.TestCase):
    def test_transactional_write_recall_invalidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine = LocalFileMemoryAdapter(tmp)
            written = engine.write(MemoryRecord(kind="note", text="alpha token"))
            self.assertIsInstance(written, Ok)
            hits = engine.recall(MemoryQuery(text="alpha"), budget_tokens=32)
            self.assertIsInstance(hits, Ok)
            assert isinstance(hits, Ok)
            self.assertEqual(len(hits.value), 1)
            report = engine.consolidate(0)
            self.assertIsInstance(report, Ok)
            engine.invalidate(ClaimRef(claim_id="c1"), "stale")
            self.assertIn("kv", engine.capabilities())


class DefaultContextAdapterTests(unittest.TestCase):
    def test_prefix_stable_and_suffix_slides(self) -> None:
        ctx = DefaultContextAdapter(system_prefix="SYS")
        view = EpisodeView(run_id="r", episode_id="e", turn=0, goal="GOAL")
        first = ctx.compile(view, budget_tokens=64)
        second = ctx.compile(view, budget_tokens=64)
        self.assertIsInstance(first, Ok)
        assert isinstance(first, Ok) and isinstance(second, Ok)
        self.assertTrue(first.value.prefix.startswith("SYS"))
        self.assertEqual(first.value.prefix, second.value.prefix)
        receipt = Receipt(
            request_digest="sha256:" + "1" * 64,
            outcome="completed",
            cost=_BUDGET,
        )
        ctx.ingest((receipt,))
        after = ctx.compile(view, budget_tokens=64)
        assert isinstance(after, Ok)
        self.assertEqual(after.value.prefix, first.value.prefix)
        self.assertIn("completed", after.value.suffix)
        compacted = ctx.compact(1.0)
        self.assertIsInstance(compacted, Ok)
        reground = ctx.reground(EffectFailure(verb="echo", detail="boom"))
        self.assertIsInstance(reground, Ok)


class SubprocessToolkitAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryEventStore()
        self.emitter = LedgerEmitter(
            self.store,
            episode_id="ep-tk",
            project_id="proj-tk",
            principal_id="agent-1",
            harness_digest="sha256:" + "0" * 64,
        )
        self.broker = PluginIsolationBroker(
            emitter=self.emitter,
            run_id="run-tk",
            principal="agent-1",
        )
        self.cell = self.broker.bind(
            "mhf.toolkit.echo",
            limits=_LIMITS,
            capabilities=({"verb": "echo", "selector": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},),
        )
        self.broker.start(self.cell)
        self.toolkit = SubprocessToolkitAdapter(
            self.cell.socket_path,
            capabilities=({"verb": "echo", "selector": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},),
        )

    def tearDown(self) -> None:
        self.broker.shutdown()

    def test_execute_over_uds_with_attenuation(self) -> None:
        request = EffectRequest(
            verb="echo",
            args={"text": "via-adapter"},
            selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
            sink=SinkClass.OBSERVATION,
            reservation=_BUDGET,
        )
        result = self.toolkit.execute(request, EffectContext(principal="p", run_id="r"))
        self.assertIsInstance(result, Ok)
        denied = self.toolkit.execute(
            EffectRequest(
                verb="proc.exec",
                args={"command": ["id"]},
                selector={"kind": "generic", "uriPattern": "proc://exec/allow/id"},
                sink=SinkClass.PRIVILEGED,
                reservation=_BUDGET,
            ),
            EffectContext(principal="p", run_id="r"),
        )
        self.assertIsInstance(denied, Err)
        self.assertIn("echo", self.toolkit.verbs())
        self.assertTrue(self.toolkit.health().ok)
        compensated = self.toolkit.compensate(
            Receipt(request_digest="sha256:" + "2" * 64, outcome="completed", cost=_BUDGET)
        )
        self.assertIsInstance(compensated, Ok)


class ExteriorJudgeAdapterTests(unittest.TestCase):
    def test_uds_signed_verdict_and_gate(self) -> None:
        private = os.urandom(32)
        signer = VerdictSigner(private, "eval-test")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        socket_path = os.path.join(tmp.name, "eval.sock")

        def serve() -> None:
            if os.path.exists(socket_path):
                os.remove(socket_path)
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.bind(socket_path)
            server.listen(1)
            conn, _ = server.accept()
            with conn, server:
                line = conn.makefile("r", encoding="utf-8").readline()
                req = json.loads(line)
                verdict = {
                    "outcome": "pass",
                    "subject": req["params"]["subject"]["run_id"],
                }
                payload = {
                    "jsonrpc": "2.0",
                    "id": req["id"],
                    "result": {
                        "verdict": verdict,
                        "signature": signer.sign(verdict),
                        "keyId": signer.key_id,
                    },
                }
                conn.sendall((json.dumps(payload) + "\n").encode("utf-8"))

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        for _ in range(50):
            if os.path.exists(socket_path):
                break
            import time
            time.sleep(0.01)

        gate = ExteriorJudgeAdapter(
            socket_path,
            public_key=signer.public_bytes,
            key_id="eval-test",
        )
        requested = gate.request(EvaluationSubject(run_id="r1", episode_id="e1"))
        self.assertIsInstance(requested, Ok)

        # `gate()` re-verifies on read (ADR-0076 §5, F-03/F-08): a verdict
        # bearing a signature this evaluator's key did not produce is not
        # evidence, no matter what its `verdict` field claims.
        def signed(outcome: str) -> SignedVerdict:
            body = {"verdict": outcome, "subject_digest": "sha256:" + "0" * 64,
                    "evaluation_request_id": "eval-1", "oracle_id": "oracle-1",
                    "nonce": "n" * 16, "key_id": "eval-test", "signed_at": "2026-08-20T00:00:00Z"}
            return SignedVerdict(signature=signer.sign(body), **body)

        self.assertEqual(gate.gate((signed("pass"),)), GateDecision.PASS)
        self.assertEqual(gate.gate((signed("fail"),)), GateDecision.RETRY)
        tampered = dataclasses.replace(signed("pass"), signature="not-a-real-signature")
        self.assertEqual(
            gate.gate((tampered,)),
            GateDecision.ABANDON,
            "an unverifiable signature must not pass the gate",
        )

        prereg = gate.preregister(OracleSpec(id="oracle-1"))
        self.assertIsInstance(prereg, Ok)
        thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
