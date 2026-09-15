"""T-141: unsafe automatic delegation fails before the public run activates."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test.agency.doubles import ScriptedModel, finish
from test.falsifiers.canonical_fixtures import code_pack
from vanguard.packages.runtime.child_runtime import RuntimeChildRunner
from test.falsifiers.test_rf55_rf59_delegation_e2e import (
    FakeEnvironment, _delegation_pack,
)
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.kernel.model import EffectRequest, Occurrence
from vanguard.packages.ports.environment import (
    EffectReceipt, EnvironmentProfile, EnvironmentSnapshot, Observation,
)
from vanguard.packages.ports.evaluator import Verdict
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.delegation import derive_child_id
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.root import (
    CompositionError, HarnessSession, Runtime, SessionPorts, TaskContext,
)
from vanguard.packages.runtime.workspace import ChildWorkspaceSupervisor


class ProductionActivation(unittest.TestCase):
    def test_unsafe_automatic_spawn_binding_refuses_before_session_activation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            harness = Runtime.compose(_delegation_pack(root / "pack"), episode_id="parent")
            environment = FakeEnvironment()
            ports = SessionPorts(
                model=ScriptedModel([finish()]), environment=environment,
                store=SqliteEventStore(":memory:"),
                clock=FixedClock(at="2026-08-26T12:00:00.000Z", step_ms=1),
                random=SeededRandom(seed=42), interactive=False,
            )
            task = TaskContext(
                brief="delegate safely", repo_path=root, run_id="t141-run",
                episode_id="parent", principal="agent-parent", max_turns=6,
            )
            self.assertIn("agent.spawn", harness.verbs)
            runner = RuntimeChildRunner(
                run_composed=Runtime.run_composed, harness=harness,
                parent_ports=ports, parent_task=task,
            )
            for child_runtime in (None, runner):
                with self.subTest(explicit_runner=child_runtime is not None):
                    with patch("vanguard.packages.runtime.root.HarnessSession") as session:
                        with self.assertRaisesRegex(CompositionError, "child-local effect"):
                            Runtime.run_composed(
                                harness, replace(ports, child_runtime=child_runtime), task)
                        session.assert_not_called()
            self.assertEqual(environment.applied, [])

            # Positive control: the same public path remains usable when the
            # composition cannot spawn. No session or run result is mocked.
            ordinary = Runtime.compose(code_pack(root), episode_id="ordinary")
            ordinary_task = replace(task, run_id="ordinary-run", episode_id="ordinary")
            result = Runtime.run_composed(ordinary, ports, ordinary_task)
            self.assertTrue(result.events)
            self.assertTrue(any(event.kind == "EpisodeStarted" for event in result.events))


class _ViewEnvironment:
    """A child-local effect adapter that really writes, and only in its view.

    Not a recorder. The point of the positive control is that the child's
    effects *land*, and land in a tree the parent does not share, so this
    performs the write against the root it was constructed with and refuses any
    path that resolves outside it. That refusal is the same `DIR-C5` boundary
    `ChildWorkspace.resolve` enforces, checked again at the adapter because an
    adapter is where a real escape would happen.
    """

    def __init__(self, child_id: str, root: Path) -> None:
        self.child_id = child_id
        self.root = Path(root).resolve()
        self.applied: list[str] = []
        self.disposed = False

    def profile(self):
        return Result.success(EnvironmentProfile(
            environment_id=f"child:{self.child_id}", kind="memory",
            root=str(self.root), capabilities=("read", "patch")))

    def snapshot(self):
        return Result.success(EnvironmentSnapshot(
            snapshot_id=f"snap-{self.child_id}", digest=digest_of(
                {"root": str(self.root)}), created_at="2026-09-15T12:00:00.000Z"))

    def observe(self, req, grant=None):
        return Result.success(Observation(
            action=getattr(req, "action", "fs.read"), content=""))

    def preview(self, req, grant=None):
        return Result.fail("unavailable", "preview unavailable")

    def apply(self, req, grant=None):
        relpath = str(dict(getattr(req, "args", {}) or {}).get("path") or "")
        target = (self.root / relpath.lstrip("/")).resolve()
        if target != self.root and self.root not in target.parents:
            return Result.fail("denied", f"{relpath!r} is outside the child view")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            str(dict(getattr(req, "args", {}) or {}).get("content") or "child\n"),
            encoding="utf-8")
        self.applied.append(relpath)
        return Result.success(EffectReceipt(
            descriptor_digest="sha256:descriptor", outcome="ok",
            observed_at="2026-09-15T12:00:00.000Z",
            result_digest=digest_of({"path": relpath})))

    def reconcile(self, receipt, grant=None):
        return Result.fail("unavailable", "reconcile unavailable")

    def compensate(self, receipt, grant=None):
        return Result.fail("unavailable", "compensate unavailable")

    def dispose(self):
        self.disposed = True
        return Result.success(None)


class _TreeEvaluator:
    """An exterior evaluator that reads the staged combined tree it is given.

    It signs and binds the way the daemon does, because publication revalidates
    the bound body rather than the adapter's say-so. It reports the tree it
    actually read, so a control that verified one tree and published another
    would fail here rather than be arranged away.
    """

    def __init__(self, child_id: str, root: Path, tree_digest: str) -> None:
        self.root = Path(root)
        self.tree_digest = tree_digest
        self.seen: tuple[str, ...] = ()

    def evaluate(self, run_ref, protocol):
        self.seen = tuple(sorted(
            path.relative_to(self.root).as_posix()
            for path in self.root.rglob("*") if path.is_file()))
        return Result.success(Verdict(
            outcome="claims", claims=(), reason="",
            signature="sig", signer_key_id="evaluator-key-1",
            binding={
                "verdict": "pass",
                "subject_digest": self.tree_digest,
                "oracle_digest": "sha256:oracle",
                "executed_test_count": 4,
            }))


class ContainedSpawnReallyRuns(unittest.TestCase):
    """The positive control. A permanent refusal is not T-141 completion.

    Everything below is the production path: `Runtime.compose` over an authored
    pack that declares `agent.spawn`, the session's own `SpawnAdapter`, the real
    `RuntimeChildRunner` bound to `Runtime.run_composed`, a child episode that
    re-enters that same public boundary, and publication through the fence.
    Nothing about the child's execution or its acceptance is mocked.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.shared = self.root / "repo"
        self.shared.mkdir()
        (self.shared / "README.md").write_text("base tree\n", encoding="utf-8")
        self.environments: list[_ViewEnvironment] = []
        self.evaluators: list[_TreeEvaluator] = []

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _child_environment(self, child_id: str, root) -> _ViewEnvironment:
        adapter = _ViewEnvironment(child_id, root)
        self.environments.append(adapter)
        return adapter

    def _tree_verifier(self, child_id: str, root, tree_digest: str) -> _TreeEvaluator:
        evaluator = _TreeEvaluator(child_id, root, tree_digest)
        self.evaluators.append(evaluator)
        return evaluator

    def _spawn(self, *, contained: bool = True):
        """Run one real spawn through the session's own adapter."""
        harness = Runtime.compose(
            _delegation_pack(self.root / "pack"), episode_id="ep-parent")
        ports = SessionPorts(
            model=ScriptedModel([finish()]),
            environment=FakeEnvironment(),
            store=SqliteEventStore(":memory:"),
            clock=FixedClock(at="2026-09-15T12:00:00.000Z", step_ms=1),
            random=SeededRandom(seed=42),
            interactive=False,
            child_environment=self._child_environment if contained else None,
            child_tree_verifier=self._tree_verifier if contained else None,
        )
        task = TaskContext(
            brief="delegate a real child", repo_path=self.shared,
            run_id="t141-positive", episode_id="ep-parent",
            principal="agent-parent", max_turns=6,
        )
        self.supervisor = ChildWorkspaceSupervisor(self.shared)
        runner = RuntimeChildRunner(
            run_composed=Runtime.run_composed,
            harness=harness,
            parent_ports=ports,
            parent_task=task,
            workspaces=self.supervisor,
            child_environment=ports.child_environment,
            tree_verifier=ports.child_tree_verifier,
        )
        self.assertEqual(runner.is_contained(), contained)
        ports = replace(ports, child_runtime=runner)
        session = HarnessSession(harness, ports, task)
        adapter = session.adapters["agent.spawn"]
        self.child_id = derive_child_id(
            "ep-parent", "intent-real-child", task.project_id)
        return adapter.execute(EffectRequest(
            action="agent.spawn",
            resource={"kind": "generic", "uriPattern": "agent://spawn/*"},
            args={
                "brief": "write the child's file",
                "authority": ["fs.read"],
                "budget": {"tokens": 100, "usd_micros": 400},
                "maxTurns": 2,
            },
            principal="agent-parent",
            run_id="t141-positive",
            depth=0,
            idempotency_key="intent-real-child",
        ))

    def test_a_contained_child_runs_through_the_public_boundary(self) -> None:
        outcome = self._spawn()

        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.occurrence, Occurrence.OCCURRED)
        self.assertEqual(len(self.environments), 1,
                         "the child did not get its own effect adapter")
        self.assertEqual(
            self.environments[0].root,
            self.supervisor.workspace_for(self.child_id).root.resolve(),
            "the child's adapter was rooted somewhere it does not own")
        self.assertTrue(self.environments[0].disposed,
                        "the child's adapter outlived its episode")

    def test_the_childs_work_is_published_after_exterior_verification(self) -> None:
        self._spawn()

        published = self.supervisor.published_tree_digest(self.child_id)
        self.assertIsNotNone(published, "a completed contained child published nothing")
        self.assertEqual(len(self.evaluators), 1)
        self.assertEqual(self.evaluators[0].tree_digest, published,
                         "the published tree is not the tree that was verified")
        self.assertIn("README.md", self.evaluators[0].seen,
                      "the evaluator saw the child's view, not the combined tree")
        self.assertEqual(
            (self.shared / "README.md").read_text(encoding="utf-8"), "base tree\n",
            "publication damaged the base it was computed against")

    def test_the_same_composition_is_still_refused_without_containment(self) -> None:
        """The negative control survives activation, which is the point of it.

        The refusal surfaces as `UNDETERMINABLE` rather than an exception: the
        adapter has already written `ChildSpawned`, so whether anything ran is
        a question the parent must not answer with a guess (`F-22`). What must
        not happen -- and does not -- is the child running against the parent's
        adapter, or a `completed` result standing in for work that never
        reached a tree.
        """
        outcome = self._spawn(contained=False)

        self.assertEqual(outcome.occurrence, Occurrence.UNDETERMINABLE)
        self.assertEqual(self.environments, [],
                         "an uncontained child built an effect adapter anyway")
        self.assertIsNone(self.supervisor.settled_digest(self.child_id))
        self.assertEqual(
            (self.shared / "README.md").read_text(encoding="utf-8"), "base tree\n")
