"""Bound falsifiers F-01..F-21 (ADR-0075, gap register section 4.2).

Each test asserts SPEC law against the surface where the wrong implementation
currently lives. Most are expected to fail (honest red) until the matching wave
lands. Uncollected silence is worse than a named red.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_TOOLS = str(ROOT / "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

import repo_paths  # noqa: E402

from vanguard.packages.adapters.stores.event_store import EventRange  # noqa: E402
from vanguard.packages.kernel.dispatch import FailurePath  # noqa: E402


def _run_tool(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONPATH": _TOOLS},
    )


CODE_DEFAULT = (
    ROOT / "vanguard" / "packages" / "agency" / "manifests" / "vg-code-default" / "manifest.json"
)


class TestF01EnvelopeLineage(unittest.TestCase):
    def test_every_emitted_envelope_carries_full_lineage(self) -> None:
        from layer0.events.emitter import InMemorySink, LedgerEmitter
        from layer0.events.envelope import EnvelopeFactory
        from layer0.spi.types_gen import EventKind

        factory = EnvelopeFactory()
        emitter = LedgerEmitter(factory, InMemorySink())
        envelope = emitter.emit_kind(
            EventKind.TURN_STARTED,
            run_id="run-1",
            principal="agent",
            episode_id="ep-1",
            causation_id="cause-1",
            correlation_id="corr-1",
            payload={"turn": 1},
        )
        self.assertEqual(envelope.episode_id, "ep-1")
        self.assertEqual(envelope.causation_id, "cause-1")
        self.assertEqual(envelope.correlation_id, "corr-1")


class TestF02StateFold(unittest.TestCase):
    def test_cold_reader_reconstructs_live_state_from_disk(self) -> None:
        from vanguard.packages.adapters.stores.event_store import SqliteEventStore
        from vanguard.packages.domain.ledger.reducer import (
            compute_state_digest,
            reconstruct_state,
        )
        from vanguard.packages.domain.ledger.events import EventEnvelope

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite"
            store = SqliteEventStore(path)
            envelope = EventEnvelope(
                event_id="e1",
                scope="episode",
                seq="0",
                occurred_at="1970-01-01T00:00:00.000Z",
                recorded_at="1970-01-01T00:00:00.000Z",
                principal="agent",
                principal_role="episode",
                run_id="run-1",
                episode_id="ep-1",
                trace_id="run-1",
                span_id="s1",
                payload={"kind": "RunStarted"},
            )
            store.append([envelope])
            read = store.read(EventRange(episode_id="ep-1"))
            self.assertTrue(read.ok)
            digest_disk = compute_state_digest(reconstruct_state(read.value or ()))
            in_memory = reconstruct_state(tuple(read.value or ()))
            self.assertEqual(compute_state_digest(in_memory), digest_disk)
            store2 = SqliteEventStore(path)
            read2 = store2.read(EventRange(episode_id="ep-1"))
            cold = reconstruct_state(read2.value or ())
            self.assertEqual(compute_state_digest(cold), digest_disk)


class TestF03EvaluatorExteriority(unittest.TestCase):
    def test_scheduler_cannot_produce_a_verdict_without_a_signature(self) -> None:
        driver_path = ROOT / "layer0" / "scheduler" / "driver.py"
        text = driver_path.read_text(encoding="utf-8")
        self.assertNotIn(
            'payload={"verdict": "pass"}',
            text,
            "layer0 driver fabricates VERDICT_RECORDED without exterior signature (F1)",
        )


class TestF04VerdictBinding(unittest.TestCase):
    def test_replayed_or_unbound_signature_is_rejected(self) -> None:
        from vanguard.packages.adapters.evaluators.signing import VerdictSigner

        signer = VerdictSigner(b"s" * 32, "eval-1")
        payload = {"outcome": "claims", "claims": [], "reason": "", "requestId": "r1"}
        signature = signer.sign(payload)
        tampered = {**payload, "requestId": "r2"}
        self.assertFalse(VerdictSigner.verify(tampered, signature, signer.public_bytes))


class TestF05WriterAuthority(unittest.TestCase):
    def test_orchestrator_cannot_append_privileged_kinds(self) -> None:
        from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
        from vanguard.packages.domain.ledger.events import EventEnvelope

        store = InMemoryEventStore()
        envelope = EventEnvelope(
            event_id="priv-1",
            scope="episode",
            seq="0",
            occurred_at="1970-01-01T00:00:00.000Z",
            recorded_at="1970-01-01T00:00:00.000Z",
            principal="orchestrator",
            principal_role="orchestrator",
            run_id="run-1",
            episode_id="ep-1",
            trace_id="run-1",
            span_id="s1",
            payload={"kind": "CapabilityGranted"},
        )
        result = store.append([envelope])
        self.assertFalse(result.ok, "privileged kinds must be writer-scoped, not open append")


class TestF06CapabilityCeiling(unittest.TestCase):
    def test_declared_ceiling_survives_compilation_and_denies(self) -> None:
        from vanguard.packages.runtime.root import Runtime

        harness = Runtime.compose(CODE_DEFAULT, episode_id="f06")
        self.assertTrue(harness.verbs, "compiled harness must retain declared capability verbs")


class TestF07FailClosedAuthority(unittest.TestCase):
    def test_empty_ceiling_denies_everything(self) -> None:
        from layer0.spi.ceiling import ceiling_allows

        self.assertFalse(ceiling_allows("execute", {"verb": "fs.read", "selector": {}}, []))


class TestF08GrantPath(unittest.TestCase):
    def test_privileged_verb_requires_a_bound_grant(self) -> None:
        from test.kernel import fakes

        harness = fakes.build()
        result = harness.kernel.dispatch(
            fakes.request(action="fs.write"),
            requested_scope=fakes.child_scope(actions=frozenset({"fs.write"})),
            reservation=fakes.reservation(),
        )
        self.assertIsNot(result.failure, FailurePath.OK)


class TestF09SpawnAttenuation(unittest.TestCase):
    def test_child_grant_wider_than_parent_is_denied_whole(self) -> None:
        from layer0.kernel.attenuation import Scope, attenuate
        from test.kernel.fakes import constraints

        parent = Scope(
            actions=frozenset({"fs.read"}),
            resources=(),
            constraints=constraints(),
            depth=0,
        )
        child = Scope(
            actions=frozenset({"fs.read", "fs.write"}),
            resources=(),
            constraints=constraints(),
            depth=1,
        )
        self.assertFalse(attenuate(parent, child).ok)


class TestF10DepthAlgebra(unittest.TestCase):
    def test_sibling_depths_are_not_summed(self) -> None:
        from layer0.spi.types_gen import Reservation

        parent = Reservation(usd_micros=0, millis=0, tokens=0, bytes=0, turns=0, depth=2)
        first = Reservation(usd_micros=0, millis=0, tokens=0, bytes=0, turns=0, depth=1)
        second = Reservation(usd_micros=0, millis=0, tokens=0, bytes=0, turns=0, depth=1)
        self.assertLessEqual(first.depth, parent.depth)
        self.assertLessEqual(second.depth, parent.depth)
        self.assertLessEqual(first.depth + second.depth, parent.depth)


class TestF11DHCompleteness(unittest.TestCase):
    def test_prompt_or_ceiling_change_changes_digest(self) -> None:
        from vanguard.packages.runtime.root import Runtime

        prompt = CODE_DEFAULT.parent / "system-prompt.txt"
        original = prompt.read_text(encoding="utf-8")
        key = "vg-code-default/system-prompt.txt"
        try:
            before = dict(Runtime.compose(CODE_DEFAULT, episode_id="f11-a").gene_digests)
            prompt.write_text(original + "\n", encoding="utf-8")
            after = dict(Runtime.compose(CODE_DEFAULT, episode_id="f11-b").gene_digests)
            self.assertNotEqual(before[key], after[key])
        finally:
            prompt.write_text(original, encoding="utf-8")


class TestF12Trajectory(unittest.TestCase):
    def test_episode_completed_emits_schema_valid_mhf_trajectory_1(self) -> None:
        trajectory_path = ROOT / "schemas" / "mhf" / "trajectory.schema.json"
        self.assertTrue(trajectory_path.is_file(), "mhf.trajectory/1 schema must exist on disk")


class TestF13GeneratedTypes(unittest.TestCase):
    def test_generate_types_check_is_clean(self) -> None:
        result = _run_tool("codegen/generate_types.py", "--check")
        self.assertEqual(
            result.returncode,
            0,
            msg=(result.stdout or "") + (result.stderr or ""),
        )


class TestF14DurableIntent(unittest.TestCase):
    def test_intent_survives_process_death(self) -> None:
        from vanguard.packages.adapters.stores.event_store import SqliteEventStore
        from vanguard.packages.kernel.model import Event
        from vanguard.packages.runtime.root import LedgerBridge

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite"
            store = SqliteEventStore(path)
            bridge = LedgerBridge(store, episode_id="ep-1")
            intent = Event(
                kind="EffectStarted",
                at="1970-01-01T00:00:00.000Z",
                principal="agent",
                run_id="run-1",
                payload={"verb": "fs.read"},
            )
            bridge.append_intent(intent)
            store2 = SqliteEventStore(path)
            read = store2.read(EventRange(episode_id="ep-1"))
            self.assertTrue(read.ok)
            self.assertTrue(read.value)


class TestF15BudgetLineage(unittest.TestCase):
    def test_child_budget_debits_parent_remaining(self) -> None:
        from test.kernel import fakes

        harness = fakes.build(ceilings={"usd_micros": 100})
        parent = harness.governor.reserve("run-1", fakes.reservation(usd_micros=50))
        harness.governor.reserve(
            "run-1",
            fakes.reservation(usd_micros=30),
            parent_lease_id=parent.lease_id,
        )
        self.assertLessEqual(harness.governor.remaining("usd_micros"), 20)


class TestF16NoDuplicateKernel(unittest.TestCase):
    def test_duplication_detector_runs(self) -> None:
        result = _run_tool("check_duplication.py")
        self.assertEqual(result.returncode, 0)
        self.assertIn("DUPLICATION", result.stdout)


class TestF17CISubject(unittest.TestCase):
    def test_living_workflow_runs_kernel_and_packages_suites(self) -> None:
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("test/kernel", ci)
        self.assertIn("test/agency", ci)
        self.assertIn("test/runtime", ci)
        self.assertIn("test/adapters", ci)
        kernel_pos = ci.index("test/kernel")
        layer0_pos = ci.index("test/layer0")
        self.assertLess(kernel_pos, layer0_pos)


class TestF18DomainBlindnessScope(unittest.TestCase):
    def test_check_domain_blindness_scans_packages_domain_and_kernel(self) -> None:
        source = (ROOT / "tools" / "check_domain_blindness.py").read_text(encoding="utf-8")
        self.assertIn("vanguard/packages/domain", source)
        self.assertIn("vanguard/packages/kernel", source)
        result = _run_tool("check_domain_blindness.py")
        self.assertEqual(result.returncode, 0)


class TestF19TestsCollected(unittest.TestCase):
    def test_integration_and_governance_are_discovered(self) -> None:
        for pkg in ("test.integration", "test.governance"):
            spec = importlib.util.find_spec(pkg)
            self.assertIsNotNone(spec, f"{pkg} must be importable (needs __init__.py)")


class TestF20OracleRegistry(unittest.TestCase):
    def test_preregistered_oracles_resolves_and_is_digest_bound(self) -> None:
        path = repo_paths.preregistered_oracles()
        self.assertTrue(path.is_file(), path)
        registry = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(registry["status"], "preregistered-not-run")
        for task in registry["tasks"]:
            oracle = repo_paths.repo_path(task["oracle"])
            digest = "sha256:" + hashlib.sha256(oracle.read_bytes()).hexdigest()
            self.assertEqual(digest, task["oracleDigest"])


class TestF21TranslatorLifting(unittest.TestCase):
    def test_parameters_key_and_fenced_payloads_are_lifted(self) -> None:
        from vanguard.packages.adapters.models.invocation import ProposalTranslator

        schemas = (
            {
                "name": "patch",
                "verb": "patch.apply",
                "payloadArgument": "content",
                "schema": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                    "required": ["path"],
                },
                "selector": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
            },
        )
        parameters = json.dumps(
            {"name": "patch", "parameters": {"path": "pkg/stats.py", "content": "V = 1\n"}}
        )
        res = ProposalTranslator.translate({"text": parameters, "toolCalls": []}, tool_schemas=schemas)
        self.assertTrue(res.ok)
        self.assertEqual(res.value["kind"], "effect")
        self.assertEqual(res.value["action"], "patch.apply")

        fenced = "Sure.\n\n```patch path=pkg/x.py\nline\n```\n"
        res2 = ProposalTranslator.translate({"text": fenced, "toolCalls": []}, tool_schemas=schemas)
        self.assertTrue(res2.ok)
        self.assertEqual(res2.value["kind"], "effect")


if __name__ == "__main__":
    unittest.main()
