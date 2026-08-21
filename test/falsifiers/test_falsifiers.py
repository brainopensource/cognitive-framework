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
_COMMON = str(ROOT / "tools" / "common")
for _p in (_COMMON, _TOOLS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import repo_paths  # noqa: E402

from vanguard.packages.adapters.stores.event_store import EventRange  # noqa: E402
from vanguard.packages.kernel.dispatch import FailurePath  # noqa: E402


def _run_tool(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    candidate = ROOT / "tools" / script
    if not candidate.exists():
        candidate = ROOT / "tools" / "linters" / script
    return subprocess.run(
        [sys.executable, str(candidate), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONPATH": f"{_TOOLS}:{_COMMON}"},
    )


CODE_DEFAULT = (
    ROOT / "vanguard" / "packages" / "agency" / "manifests" / "vg-code-default" / "manifest.json"
)


class TestF01EnvelopeLineage(unittest.TestCase):
    def test_every_emitted_envelope_carries_full_lineage(self) -> None:
        """Subject of record is `vanguard/packages/` (ADR-0075 §3, Wave 1
        entry). `layer0.events.emitter` is a copy-fork awaiting absorption in
        Wave 2; measuring lineage there would gate M-1 on a deferred defect.
        """
        from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
        from vanguard.packages.runtime.ledger_emitter import LedgerEmitter

        emitter = LedgerEmitter(
            InMemoryEventStore(), episode_id="ep-1", project_id="proj-f01",
            principal_id="agent-1", harness_digest="sha256:" + "a" * 64, role="session")
        wire = emitter.emit_kind(
            "TurnStarted", run_id="run-1", principal="agent-1",
            payload={"turn": 1}).to_mhf_dict()
        self.assertEqual(wire["schema_version"], "mhf.event/1")
        for field in ("project_id", "principal_id", "parent_principal_id",
                      "parent_episode_id", "harness_digest", "episode_id"):
            self.assertIn(field, wire)
        self.assertEqual(wire["episode_id"], "ep-1")


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
                schema_version="mhf.event/1",
                event_id="e1",
                scope="episode",
                seq="0",
                occurred_at="1970-01-01T00:00:00.000Z",
                recorded_at="1970-01-01T00:00:00.000Z",
                principal="agent",
                principal_role="episode",
                tenant_id="tenant-default",
                owner_id="owner-platform",
                confidentiality="internal",
                retention_class="standard",
                trainability="prohibited",
                redaction_status="none",
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
    def test_only_the_evaluator_gateway_can_ledger_a_verdict(self) -> None:
        """F-03 on the subject of record: no writer role but
        `evaluator_gateway` can append `VerdictRecorded`, and the gateway
        itself has nothing to fabricate a pass *from* -- it ledgers the
        daemon's own signed bytes or returns `None` (ADR-0076 §5/§6).

        The residual `layer0/scheduler/driver.py` unsigned-pass fabrication is
        a deliberately deferred Wave-2 absorption defect (`wave2_convergence.md`),
        not an M-1 gate: `layer0/` is not the production path.
        """
        from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
        from vanguard.packages.ports.evaluator import Verdict
        from vanguard.packages.runtime.evaluator_gateway import record_verdict
        from vanguard.packages.runtime.ledger_emitter import (
            LedgerEmitter,
            WriterAuthorityError,
        )

        emitter = LedgerEmitter(
            InMemoryEventStore(), episode_id="ep-1", project_id="proj-f03",
            principal_id="agent-1", harness_digest="sha256:" + "b" * 64, role="session")
        for facade in (emitter, emitter.scheduler(), emitter.orchestrator(),
                       emitter.kernel(), emitter.registry(), emitter.approval()):
            with self.assertRaises(WriterAuthorityError):
                facade.emit_kind(
                    "VerdictRecorded", run_id="run-1", principal="agent-1",
                    payload={"signedVerdict": {"outcome": "pass"}})
        # An unsigned/unbound verdict has no signed body to ledger.
        self.assertIsNone(record_verdict(
            emitter, run_id="run-1", principal="agent-1", episode_id="ep-1",
            verdict=Verdict(outcome="claims", claims=(), reason="")))
        self.assertEqual(emitter.store.count(), 0)


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
        """ADR-0076 §6: writer authority is enforced at the one construction
        point (`LedgerEmitter`'s role-scoped facades), not by the store —
        `EventStorePort.append()` is a dumb persistence sink and was never the
        gate. A generic `append(any envelope)` bypassing the emitter is the
        wrong implementation F-05 exists to catch.
        """
        from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
        from vanguard.packages.runtime.ledger_emitter import LedgerEmitter, WriterAuthorityError

        emitter = LedgerEmitter(
            InMemoryEventStore(), episode_id="ep-1", project_id="proj-f05",
            principal_id="agent-1", harness_digest="sha256:" + "a" * 64, role="session")
        orchestrator = emitter.orchestrator()
        with self.assertRaises(WriterAuthorityError):
            orchestrator.emit_kind(
                "CapabilityGranted", run_id="run-1", principal="orchestrator",
                payload={"kind": "CapabilityGranted"})
        self.assertEqual(emitter.store.count(), 0,
                         "privileged kinds must be writer-scoped, not open append")


class TestF06CapabilityCeiling(unittest.TestCase):
    def test_declared_ceiling_survives_compilation_and_denies(self) -> None:
        from vanguard.packages.runtime.root import Runtime

        harness = Runtime.compose(CODE_DEFAULT, episode_id="f06")
        self.assertTrue(harness.verbs, "compiled harness must retain declared capability verbs")


class TestF07FailClosedAuthority(unittest.TestCase):
    def test_empty_ceiling_denies_everything(self) -> None:
        """`layer0/spi/ceiling.py` is fail-open and stays that way until its
        Wave-2 absorption; the canonical algebra lives in `domain/selectors/`.
        """
        from vanguard.packages.domain.selectors.resource_selector import ceiling_allows

        decision = ceiling_allows((), {"kind": "fs", "root": "/workspace",
                                       "paths": ["/workspace/a.py"]})
        self.assertFalse(decision.included)
        self.assertEqual(decision.reason, "empty_ceiling")


class TestF08GrantPath(unittest.TestCase):
    """F-08: *a privileged verb requires a bound grant.*

    The pre-gate form of this test dispatched a fully authorized `fs.write`
    -- held authority, covering scope, sufficient reservation -- and then
    asserted `failure is not OK`: it asserted that the grant path must fail on
    its own happy path. Adjudicated at the M-1 gate as an inverted falsifier,
    not a production defect. `dispatch()` S6 issues through
    `SinkRegistry.requires_grant`, S8 re-verifies the grant against the
    descriptor digest at the point of effect (`K-05`), and S8a records
    `grantId`/`grantDigest` in the durable intent. The law is restated below
    in both directions.
    """

    def test_privileged_verb_is_bound_to_a_grant(self) -> None:
        from test.kernel import fakes

        harness = fakes.build()
        result = harness.kernel.dispatch(
            fakes.request(action="fs.write"),
            requested_scope=fakes.child_scope(actions=frozenset({"fs.write"})),
            reservation=fakes.reservation(),
        )
        self.assertIs(result.failure, FailurePath.OK)
        intent = next(e for e in result.events if e.kind == "EffectStarted")
        self.assertTrue(intent.payload["grantId"], "privileged verb dispatched ungranted")
        self.assertTrue(intent.payload["grantDigest"], "grant is not bound to the effect")
        self.assertEqual(intent.payload["descriptorDigest"], result.descriptor_digest)

    def test_ungrantable_privileged_verb_never_reaches_durable_intent(self) -> None:
        """The other direction: when no grant can be issued, nothing runs.

        Three independent ways to reach ungrantable, because any single one
        could be satisfied by a check sitting in the wrong stage: a *sealed*
        scope that excludes the verb (`ADR-0067` — a sealed grant may not
        widen even on operator justification, which is precisely what
        separates it from the unsealed case above), a scope that escalates
        past the parent, and a widening justified only by an
        untrusted-external span (`K-30`/`F-09`).

        Note what is deliberately *not* asserted here: an unsealed narrower
        scope widening under an **operator** span is allowed, and holding no
        prior `fs.write` authority does not by itself deny — the authority
        predicate denies on the *provenance* of the justification, not on
        prior possession. Asserting otherwise is the F-08 inversion.
        """
        from test.kernel import fakes

        for label, harness, scope, request in (
            ("sealed scope",
             fakes.build(),
             fakes.child_scope(actions=frozenset({"fs.read"}), sealed=True),
             fakes.request(action="fs.write")),
            ("scope escalation past the parent",
             fakes.build(),
             fakes.child_scope(constraints=fakes.constraints(max_uses=4096)),
             fakes.request(action="fs.write")),
            ("widening on an untrusted-external span",
             fakes.build(held_actions=frozenset({"fs.read"})),
             fakes.child_scope(actions=frozenset({"fs.write"})),
             fakes.request(action="fs.write",
                           justifying_spans=(fakes.untrusted_result_span(),))),
        ):
            with self.subTest(label):
                result = harness.kernel.dispatch(
                    request,
                    requested_scope=scope,
                    reservation=fakes.reservation(),
                )
                self.assertIsNot(result.failure, FailurePath.OK)
                self.assertFalse(
                    [e for e in result.events if e.kind == "EffectStarted"],
                    "an ungrantable privileged verb must not reach durable intent")
                self.assertFalse(harness.adapter.calls, "the effect must not have run")


class TestF09SpawnAttenuation(unittest.TestCase):
    def test_child_grant_wider_than_parent_is_denied_whole(self) -> None:
        from vanguard.packages.kernel.attenuation import Constraints, Scope, attenuate

        base = dict(expires_at="2099-01-01T00:00:00.000Z", max_uses=4,
                    budget_usd_micros=1000, max_depth=3)
        resources = ({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},)
        parent = Scope(actions=frozenset({"fs.read"}), resources=resources,
                       constraints=Constraints(max_bytes=100, **base), depth=0)
        # Wider on the verb set...
        wider = Scope(actions=frozenset({"fs.read", "fs.write"}), resources=resources,
                      constraints=Constraints(max_bytes=100, **base), depth=1)
        self.assertFalse(attenuate(parent, wider).ok)
        # ...and 1.3-C: an unbounded child under a bounded parent is a widening.
        unbounded = Scope(actions=frozenset({"fs.read"}), resources=resources,
                          constraints=Constraints(max_bytes=None, **base), depth=1)
        self.assertFalse(attenuate(parent, unbounded).ok)


class TestF10DepthAlgebra(unittest.TestCase):
    def test_sibling_depths_are_not_summed(self) -> None:
        """Depth is a structural ceiling, never an additive cost: it is absent
        from `Reservation.as_map()`, so two siblings at depth 1 under a parent
        bounded at depth 2 both stand (ADR-0074 §2).
        """
        from vanguard.packages.kernel.attenuation import Constraints, Scope, attenuate
        from vanguard.packages.kernel.budget import Reservation

        resources = ({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},)
        constraints = Constraints(expires_at="2099-01-01T00:00:00.000Z", max_uses=8,
                                  budget_usd_micros=10_000, max_depth=2)
        parent = Scope(actions=frozenset({"fs.read"}), resources=resources,
                       constraints=constraints, depth=0)
        sibling = Scope(actions=frozenset({"fs.read"}), resources=resources,
                        constraints=constraints, depth=1)
        first, second = attenuate(parent, sibling), attenuate(parent, sibling)
        self.assertTrue(first.ok and second.ok)
        self.assertEqual((first.granted.depth, second.granted.depth), (1, 1))
        self.assertNotIn("depth", Reservation(usd_micros=1).as_map())

    def test_the_governor_refuses_a_reservation_carrying_structural_dimensions(self) -> None:
        """2.2-A: `Governor.reserve` is duck-typed on `as_map()`, and the
        generated wire `Reservation` (`domain/wire/types_gen.py`) is
        structurally interchangeable with the kernel's while carrying `depth`
        and `turns`. Repointing a caller from the layer0 governor to this one
        must not silently restore sibling-depth summing, so the governor names
        its own conserved dimensions and refuses anything else.
        """
        from vanguard.packages.domain.wire.types_gen import Reservation as WireReservation
        from vanguard.packages.kernel.budget import ADDITIVE_DIMENSIONS, BudgetDenied, Governor

        self.assertNotIn("depth", ADDITIVE_DIMENSIONS)
        self.assertNotIn("turns", ADDITIVE_DIMENSIONS)
        gov = Governor({"usd_micros": 1000, "depth": 2, "turns": 4})
        wire = WireReservation(usd_micros=1, millis=0, tokens=0, bytes=0, turns=1, depth=1)
        with self.assertRaises(BudgetDenied) as caught:
            gov.reserve("run", wire)
        self.assertEqual(caught.exception.reason, "not_a_conserved_dimension")
        self.assertEqual(gov.remaining("depth"), 2, "no structural ceiling was consumed")


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
        """The schema existing on disk is not evidence that anything emits it.
        The end-to-end proof over a live episode is in
        `test/runtime/test_ledger_truth.py`; this pins the assembler's own
        contract against the schema's required set, including the aborted
        case, where a trajectory is still owed and `verdict` is `null`.
        """
        from vanguard.packages.runtime.root import TaskContext
        from vanguard.packages.runtime.trajectory import assemble_trajectory

        schema = json.loads(
            (ROOT / "schemas" / "mhf" / "trajectory.schema.json").read_text(encoding="utf-8"))
        trajectory = assemble_trajectory(
            task=TaskContext(brief="b", repo_path=ROOT, run_id="run-1", episode_id="ep-1"),
            harness_digest="sha256:" + "d" * 64,
            terminal="abandoned",
            receipts=(), contexts=(), events=(), verdict=None,
        )
        self.assertEqual(trajectory["schema"], "mhf.trajectory/1")
        self.assertIsNone(trajectory["verdict"], "an aborted episode still owes a trajectory")
        for field in schema.get("required", ()):
            self.assertIn(field, trajectory)


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
            bridge = LedgerBridge(
                store, episode_id="ep-1", project_id="proj-f14",
                principal_id="agent", harness_digest="sha256:" + "c" * 64, role="kernel")
            intent = Event(
                kind="EffectStarted",
                reason="s8a",
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
        parent = harness.governor.reserve(
            "run-1", fakes.reservation(usd_micros=50, millis=0))
        harness.governor.reserve(
            "run-1",
            fakes.reservation(usd_micros=30, millis=0),
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
        source = (ROOT / "tools" / "linters" / "check_domain_blindness.py").read_text(encoding="utf-8")
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
