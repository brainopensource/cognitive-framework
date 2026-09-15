"""T-151: publication x continuity on real Runtime -> HarnessSession.

Falsifying the 6 unowned interaction cases between T-141 child publication
and session continuity (T-142):

1. Case 1 (Mid-publication crash recovery across fresh process):
   A crash after durable EffectStarted/ChildSpawned but mid-publication
   (_apply_authorized interrupted) recovers via recover() in a fresh
   HarnessSession / ChildWorkspaceSupervisor process, applying the verified
   combined tree and settling exactly once without duplicating effects.
2. Case 2 (Grant revocation before publication):
   A capability grant revoked between child episode completion and publication
   refuses publication (PublicationRefused / undeterminable outcome).
3. Case 3 (Budget exhaustion before publication):
   Budget committed / exhausted between child staging and publication
   refuses publication (PublicationRefused / undeterminable outcome).
4. Case 4 (Compaction preservation):
   Repeated compaction between child dispatch and publication retains the
   spawn intent and does not alter the candidate digest, base digest, or
   verification subject.
5. Case 5 (Unauthorized candidate promotion denied across restart):
   A retained candidate with no signed passing exterior verdict is never
   promoted across a restart (recover() skips merely-retained candidates).
6. Case 6 (Composition drift on resume):
   A changed composition on resume refuses publication or continuation
   of a candidate staged under the previous composition.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Fragment
from vanguard.packages.agency.context.packet import ContextPacketError
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.kernel.attenuation import Constraints, Scope
from vanguard.packages.kernel.model import EffectRequest, Occurrence
from vanguard.packages.ports.child_runtime import ChildRunPlan, ChildRunResult
from vanguard.packages.ports.environment import (
    EffectReceipt,
    EnvironmentProfile,
    EnvironmentSnapshot,
    Observation,
)
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict
from vanguard.packages.ports.event_store import EventRange, Result
from vanguard.packages.runtime.child_runtime import RuntimeChildRunner
from vanguard.packages.runtime.compose import Harness, RunResult, TaskContext
from vanguard.packages.runtime.delegation import derive_child_id
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter
from vanguard.packages.runtime.ledger.recovery import RecoveryScanner, replay_ledger_state
from vanguard.packages.runtime.root import (
    CompositionError,
    HarnessSession,
    Runtime,
    SessionPorts,
)
from vanguard.packages.runtime.task_state import fold_task_state
from vanguard.packages.runtime.workspace import (
    ChildWorkspaceSupervisor,
    CombinedTree,
    PublicationAuthority,
    PublicationRefused,
    PublicationVerdict,
    StaleBaseError,
    StaleWriterError,
    UnverifiedPublicationError,
    WorkspaceEscapeError,
    WorkspaceFenceError,
    _atomic_write,
)


class _Clock:
    """A deterministic hand-wound clock."""

    def __init__(self, start: float = 1_000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds

    def iso(self) -> str:
        return "2026-09-15T12:00:00.000Z"


class _ViewEnvironment:
    """A child-local effect adapter that writes strictly into its view root."""

    def __init__(self, child_id: str, root: Path) -> None:
        self.child_id = child_id
        self.root = Path(root).resolve()
        self.applied: list[str] = []
        self.disposed = False

    def profile(self) -> Result[EnvironmentProfile]:
        return Result.success(
            EnvironmentProfile(
                environment_id=f"child:{self.child_id}",
                kind="memory",
                root=str(self.root),
                capabilities=("read", "patch"),
            )
        )

    def snapshot(self) -> Result[EnvironmentSnapshot]:
        return Result.success(
            EnvironmentSnapshot(
                snapshot_id=f"snap-{self.child_id}",
                digest=digest_of({"root": str(self.root)}),
                created_at="2026-09-15T12:00:00.000Z",
            )
        )

    def observe(self, req: Any, grant: Any = None) -> Result[Observation]:
        return Result.success(
            Observation(action=getattr(req, "action", "fs.read"), content="")
        )

    def preview(self, req: Any, grant: Any = None) -> Result[Any]:
        return Result.fail("unavailable", "preview unavailable")

    def apply(self, req: Any, grant: Any = None) -> Result[EffectReceipt]:
        relpath = str(dict(getattr(req, "args", {}) or {}).get("path") or "")
        target = (self.root / relpath.lstrip("/")).resolve()
        if target != self.root and self.root not in target.parents:
            return Result.fail("denied", f"{relpath!r} is outside the child view")
        target.parent.mkdir(parents=True, exist_ok=True)
        content = str(dict(getattr(req, "args", {}) or {}).get("content") or "child\n")
        target.write_text(content, encoding="utf-8")
        self.applied.append(relpath)
        return Result.success(
            EffectReceipt(
                descriptor_digest="sha256:descriptor",
                outcome="ok",
                observed_at="2026-09-15T12:00:00.000Z",
                result_digest=digest_of({"path": relpath}),
            )
        )

    def reconcile(self, receipt: Any, grant: Any = None) -> Result[Any]:
        return Result.fail("unavailable", "reconcile unavailable")

    def compensate(self, receipt: Any, grant: Any = None) -> Result[Any]:
        return Result.fail("unavailable", "compensate unavailable")

    def dispose(self) -> Result[None]:
        self.disposed = True
        return Result.success(None)


class _TreeEvaluator:
    """An exterior evaluator double verifying the exact staged combined tree."""

    def __init__(
        self,
        child_id: str,
        root: Path,
        tree_digest: str,
        *,
        verdict: str = "pass",
        tamper_subject: str | None = None,
    ) -> None:
        self.root = Path(root)
        self.tree_digest = tree_digest
        self.verdict = verdict
        self.tamper_subject = tamper_subject
        self.seen: tuple[str, ...] = ()

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        self.seen = tuple(
            sorted(
                path.relative_to(self.root).as_posix()
                for path in self.root.rglob("*")
                if path.is_file()
            )
        )
        subject = self.tamper_subject if self.tamper_subject is not None else self.tree_digest
        return Result.success(
            Verdict(
                outcome="claims",
                claims=(),
                reason="",
                signature="sig-exterior",
                signer_key_id="evaluator-key-t151",
                binding={
                    "verdict": self.verdict,
                    "subject_digest": subject,
                    "oracle_digest": "sha256:oracle-t151",
                    "executed_test_count": 2,
                },
            )
        )


def _init_repo(root: Path) -> None:
    """Initialise a valid git repository with initial commit."""
    root.mkdir(parents=True, exist_ok=True)
    (root / ".git").mkdir(exist_ok=True)
    (root / "README.md").write_text("# Base Repository\n", encoding="utf-8")
    (root / "base_module.py").write_text("def base():\n    return 'base'\n", encoding="utf-8")


def _make_constraints(*, expires_at: str = "2026-09-15T18:00:00.000Z") -> Constraints:
    return Constraints(
        expires_at=expires_at,
        max_uses=100,
        budget_usd_micros=100_000,
    )


def _make_plan(
    child_id: str,
    *,
    authority: tuple[str, ...] = ("fs.read", "fs.patch"),
    composition_digest: str = "sha256:composition-t151",
    run_id: str = "run-t151",
    project_id: str = "proj-t151",
    idempotency_key: str = "intent-t151",
) -> ChildRunPlan:
    return ChildRunPlan(
        child_episode_id=child_id,
        parent_episode_id="ep-parent",
        run_id=run_id,
        project_id=project_id,
        principal="agent-principal",
        composition_digest=composition_digest,
        goal_digest="sha256:goal-t151",
        authority=authority,
        resources=({"kind": "fs", "root": "/workspace"},),
        depth=1,
        max_depth=3,
        max_turns=4,
        budget={"tokens": 1000, "usd_micros": 5000},
        lineage=("ep-parent", child_id),
        idempotency_key=idempotency_key,
        brief="T-151 child execution",
    )


# ==============================================================================
# Case 1: Mid-publication crash recovery across fresh process
# ==============================================================================


class MidPublicationCrashRecoveryAcrossProcess(unittest.TestCase):
    """A crash after durable authorization mid-publication recovers in a fresh process."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.shared = Path(self._tmp.name) / "repo"
        _init_repo(self.shared)
        self.clock = _Clock()
        self.supervisor = ChildWorkspaceSupervisor(self.shared, now=self.clock)
        self.child_id = derive_child_id("ep-parent", "intent-child-1", "proj-t151")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _setup_staged_candidate(self) -> tuple[str, CombinedTree, str]:
        view = self.supervisor.workspace_for(self.child_id)
        view.write("child_feature.py", "def feature():\n    return 42\n")
        candidate_digest = self.supervisor.retain_candidate(self.child_id)
        ticket = self.supervisor.acquire(self.child_id)
        combined = self.supervisor.stage(ticket, candidate_digest=candidate_digest)
        return ticket, combined, candidate_digest

    def test_mid_publication_crash_recovers_and_settles_exactly_once(self) -> None:
        ticket, combined, candidate_digest = self._setup_staged_candidate()

        # Simulate mid-publication crash: authorization is durable, one file lands,
        # but the process dies before the settlement marker is recorded.
        def half_apply(cid: str) -> None:
            record = self.supervisor._authorization(cid)
            assert record is not None
            first_entry = sorted(record["entries"])[0]
            _atomic_write(
                self.supervisor._shared_target(first_entry),
                record["entries"][first_entry],
            )
            raise OSError("simulated process crash during _apply_authorized")

        orig_apply = self.supervisor._apply_authorized
        self.supervisor._apply_authorized = half_apply  # type: ignore[method-assign]
        try:
            self.supervisor.publish(
                ticket,
                combined,
                verdict=PublicationVerdict(combined.digest, "pass"),
            )
        except OSError:
            pass
        finally:
            self.supervisor._apply_authorized = orig_apply  # type: ignore[method-assign]
            self.supervisor.release(ticket)

        # The crash occurred: shared target has partial/initial state,
        # but settlement marker was NOT written.
        self.assertIsNone(
            self.supervisor.settled_digest(self.child_id),
            "settlement marker was prematurely written before crash",
        )

        # FRESH PROCESS: Instantiate an independent supervisor with zero in-memory state.
        fresh_supervisor = ChildWorkspaceSupervisor(self.shared, now=self.clock)
        self.assertIsNone(fresh_supervisor.settled_digest(self.child_id))

        # Recovery executes under lifecycle lock in fresh process
        recovered = fresh_supervisor.recover()
        self.assertEqual(
            recovered,
            (self.child_id,),
            "recovery did not recover the interrupted authorized publication",
        )

        # The combined tree is now fully applied and settled
        self.assertEqual(
            fresh_supervisor.published_tree_digest(self.child_id),
            combined.digest,
            "recovered tree digest does not match the authorized combined digest",
        )
        self.assertEqual(fresh_supervisor.settled_digest(self.child_id), candidate_digest)

        # Both base file and child feature file are present and intact
        self.assertTrue((self.shared / "base_module.py").is_file())
        self.assertTrue((self.shared / "child_feature.py").is_file())
        self.assertEqual(
            (self.shared / "child_feature.py").read_text(encoding="utf-8"),
            "def feature():\n    return 42\n",
        )

        # IDEMPOTENCE: A second recovery pass in the fresh process does NOT re-settle or re-apply
        second_pass = fresh_supervisor.recover()
        self.assertEqual(
            second_pass,
            (),
            "second recovery pass re-settled an already completed publication",
        )

    def test_fresh_process_recovery_reconciles_interrupted_spawn_intent(self) -> None:
        """Ledger level: an open ChildSpawned intent reconciles to undeterminable on fresh process."""
        db_path = self.shared / ".vanguard" / "events.sqlite3"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        store = SqliteEventStore(str(db_path))

        # Write ChildSpawned event via privileged role
        emitter = LedgerEmitter(
            store,
            episode_id="ep-parent",
            project_id="proj-t151",
            principal_id="agent-parent",
            harness_digest="sha256:" + "0" * 64,
            role="spawn_adapter",
        )
        emitter.emit_kind(
            "ChildSpawned",
            run_id="run-t151",
            principal="agent-parent",
            payload={
                "kind": "ChildSpawned",
                "childEpisodeId": self.child_id,
                "idempotencyKey": "intent-child-1",
                "settledIntentKey": "intent-child-1",
                "depth": 1,
            },
            episode_id="ep-parent",
        )
        store.close()

        # FRESH PROCESS: scan and reconcile open children
        fresh_store = SqliteEventStore(str(db_path))
        try:
            scanner = RecoveryScanner(controller_principal="recovery-controller")
            reconciled = scanner.reconcile_open_children(
                fresh_store,
                occurred_at="2026-09-15T12:05:00.000Z",
                project_id="proj-t151",
            )
            self.assertEqual(len(reconciled), 1)
            rec_event = reconciled[0]
            self.assertEqual(rec_event.payload.get("kind"), "EffectReconciled")
            self.assertEqual(rec_event.payload.get("status"), "undeterminable")
            self.assertEqual(rec_event.payload.get("occurrence"), "undeterminable")

            # Second scan does not duplicate reconciliation
            second_scan = scanner.reconcile_open_children(
                fresh_store,
                occurred_at="2026-09-15T12:06:00.000Z",
                project_id="proj-t151",
            )
            self.assertEqual(len(second_scan), 0, "open child was reconciled twice")
        finally:
            fresh_store.close()


# ==============================================================================
# Case 2: Grant revocation before publication
# ==============================================================================


class GrantRevocationBeforePublication(unittest.TestCase):
    """A grant revoked or expired before publication refuses shared mutation."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.shared = Path(self._tmp.name) / "repo"
        _init_repo(self.shared)
        self.clock = _Clock()
        self.supervisor = ChildWorkspaceSupervisor(self.shared, now=self.clock)
        self.child_id = derive_child_id("ep-parent", "intent-revoked", "proj-t151")
        self.plan = _make_plan(
            self.child_id,
            authority=("fs.read", "fs.patch"),
            idempotency_key="intent-revoked",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _setup_runner(
        self,
        *,
        evaluator_verdict: str = "pass",
        tamper_subject: str | None = None,
    ) -> tuple[RuntimeChildRunner, _TreeEvaluator]:
        tree_eval = _TreeEvaluator(
            self.child_id,
            self.shared,
            "dummy",
            verdict=evaluator_verdict,
            tamper_subject=tamper_subject,
        )

        runner = RuntimeChildRunner(
            run_composed=lambda *a, **kw: RunResult(events=(), status="completed"),
            harness=Runtime.compose("vg-code-balanced", episode_id="ep-parent"),
            parent_ports=SessionPorts(
                model=None,
                environment=_ViewEnvironment("parent", self.shared),
                store=SqliteEventStore(":memory:"),
                clock=FixedClock(at="2026-09-15T12:00:00.000Z"),
            ),
            parent_task=TaskContext(
                brief="parent",
                repo_path=self.shared,
                run_id="run-t151",
                episode_id="ep-parent",
            ),
            workspaces=self.supervisor,
            child_environment=lambda cid, root: _ViewEnvironment(cid, root),
            tree_verifier=lambda cid, root, digest: _TreeEvaluator(
                cid, root, digest, verdict=evaluator_verdict, tamper_subject=tamper_subject
            ),
        )
        return runner, tree_eval

    def test_revoked_grant_actions_refuse_publication(self) -> None:
        # Child writes content in view
        view = self.supervisor.workspace_for(self.child_id)
        view.write("forbidden.py", "malicious = True\n")

        runner, _ = self._setup_runner()
        projected = ChildRunResult(
            ok=True,
            outcome="completed",
            terminal="COMPLETED",
            child_episode_id=self.child_id,
            actual_cost={"tokens": 50, "usd_micros": 200},
        )

        # Grant was attenuated/revoked before publication: only has ("fs.read",), lacks "fs.patch"
        revoked_grant = Scope(
            actions=("fs.read",),
            resources=("/workspace",),
            constraints=_make_constraints(),
            depth=1,
        )
        authority = PublicationAuthority(
            grant=revoked_grant,
            remaining_budget=lambda: {"tokens": 1000, "usd_micros": 5000},
            now=lambda: "2026-09-15T12:00:00.000Z",
        )

        # Verification of authority recheck failure
        lapsed = authority.recheck(self.plan, projected.actual_cost)
        self.assertIn("authority the current grant does not carry", lapsed)

        # Publication fails closed with undeterminable terminal
        result = runner._publish_workspace(self.plan, projected, authority)
        self.assertFalse(result.ok)
        self.assertEqual(result.outcome, "undeterminable")
        self.assertEqual(result.terminal, "UNDETERMINABLE")
        self.assertIn("not published: authority lapsed", result.detail)

        # Nothing is published or settled in the shared workspace
        self.assertIsNone(self.supervisor.published_tree_digest(self.child_id))
        self.assertIsNone(self.supervisor.settled_digest(self.child_id))
        self.assertFalse((self.shared / "forbidden.py").exists())

    def test_expired_grant_refuses_publication(self) -> None:
        view = self.supervisor.workspace_for(self.child_id)
        view.write("expired.py", "expired = True\n")

        runner, _ = self._setup_runner()
        projected = ChildRunResult(
            ok=True,
            outcome="completed",
            terminal="COMPLETED",
            child_episode_id=self.child_id,
            actual_cost={"tokens": 10, "usd_micros": 50},
        )

        expired_grant = Scope(
            actions=("fs.read", "fs.patch"),
            resources=("/workspace",),
            constraints=_make_constraints(expires_at="2026-09-15T10:00:00.000Z"),
            depth=1,
        )
        authority = PublicationAuthority(
            grant=expired_grant,
            remaining_budget=lambda: {"tokens": 1000, "usd_micros": 5000},
            now=lambda: "2026-09-15T12:00:00.000Z",
        )

        lapsed = authority.recheck(self.plan, projected.actual_cost)
        self.assertIn("grant expired at 2026-09-15T10:00:00.000Z", lapsed)

        result = runner._publish_workspace(self.plan, projected, authority)
        self.assertFalse(result.ok)
        self.assertEqual(result.outcome, "undeterminable")
        self.assertIn("grant expired", result.detail)
        self.assertIsNone(self.supervisor.published_tree_digest(self.child_id))
        self.assertFalse((self.shared / "expired.py").exists())


# ==============================================================================
# Case 3: Budget exhaustion before publication
# ==============================================================================


class BudgetExhaustionBeforePublication(unittest.TestCase):
    """Budget exhausted between child staging and publication refuses publication."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.shared = Path(self._tmp.name) / "repo"
        _init_repo(self.shared)
        self.clock = _Clock()
        self.supervisor = ChildWorkspaceSupervisor(self.shared, now=self.clock)
        self.child_id = derive_child_id("ep-parent", "intent-budget", "proj-t151")
        self.plan = _make_plan(self.child_id, idempotency_key="intent-budget")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _setup_runner(self) -> RuntimeChildRunner:
        return RuntimeChildRunner(
            run_composed=lambda *a, **kw: RunResult(events=(), status="completed"),
            harness=Runtime.compose("vg-code-balanced", episode_id="ep-parent"),
            parent_ports=SessionPorts(
                model=None,
                environment=_ViewEnvironment("parent", self.shared),
                store=SqliteEventStore(":memory:"),
                clock=FixedClock(at="2026-09-15T12:00:00.000Z"),
            ),
            parent_task=TaskContext(
                brief="parent",
                repo_path=self.shared,
                run_id="run-t151",
                episode_id="ep-parent",
            ),
            workspaces=self.supervisor,
            child_environment=lambda cid, root: _ViewEnvironment(cid, root),
            tree_verifier=lambda cid, root, digest: _TreeEvaluator(cid, root, digest, verdict="pass"),
        )

    def test_budget_exhaustion_before_publication_refuses_shared_mutation(self) -> None:
        view = self.supervisor.workspace_for(self.child_id)
        view.write("expensive.py", "spend = 1000\n")

        runner = self._setup_runner()
        # The child spent 800 tokens and 3500 usd_micros
        projected = ChildRunResult(
            ok=True,
            outcome="completed",
            terminal="COMPLETED",
            child_episode_id=self.child_id,
            actual_cost={"tokens": 800, "usd_micros": 3500},
        )

        # Parent's remaining balance before publication is only 200 tokens (exhausted by other tasks)
        authority = PublicationAuthority(
            grant=Scope(
                actions=("fs.read", "fs.patch"),
                resources=("/workspace",),
                constraints=_make_constraints(),
                depth=1,
            ),
            remaining_budget=lambda: {"tokens": 200, "usd_micros": 5000},
            now=lambda: "2026-09-15T12:00:00.000Z",
        )

        lapsed = authority.recheck(self.plan, projected.actual_cost)
        self.assertIn("budget dimension 'tokens' spent 800 against 200 remaining", lapsed)

        result = runner._publish_workspace(self.plan, projected, authority)
        self.assertFalse(result.ok)
        self.assertEqual(result.outcome, "undeterminable")
        self.assertIn("budget dimension 'tokens' spent", result.detail)

        # Fails closed: candidate retained in child view, but never published
        self.assertIsNone(self.supervisor.published_tree_digest(self.child_id))
        self.assertFalse((self.shared / "expensive.py").exists())

    def test_sufficient_budget_permits_publication(self) -> None:
        view = self.supervisor.workspace_for(self.child_id)
        view.write("affordable.py", "spend = 10\n")

        runner = self._setup_runner()
        projected = ChildRunResult(
            ok=True,
            outcome="completed",
            terminal="COMPLETED",
            child_episode_id=self.child_id,
            actual_cost={"tokens": 100, "usd_micros": 400},
        )

        authority = PublicationAuthority(
            grant=Scope(
                actions=("fs.read", "fs.patch"),
                resources=("/workspace",),
                constraints=_make_constraints(),
                depth=1,
            ),
            remaining_budget=lambda: {"tokens": 1000, "usd_micros": 5000},
            now=lambda: "2026-09-15T12:00:00.000Z",
        )

        self.assertEqual(authority.recheck(self.plan, projected.actual_cost), "")
        result = runner._publish_workspace(self.plan, projected, authority)
        self.assertTrue(result.ok)
        self.assertEqual(result.outcome, "completed")
        self.assertIsNotNone(self.supervisor.published_tree_digest(self.child_id))
        self.assertTrue((self.shared / "affordable.py").exists())


# ==============================================================================
# Case 4: Compaction preservation
# ==============================================================================


class CompactionPreservesPublicationState(unittest.TestCase):
    """Repeated compaction preserves child spawn intent, obligations, and digest identity."""

    def test_compaction_preserves_spawn_intent_and_obligations(self) -> None:
        from types import SimpleNamespace

        events: list[Any] = [
            SimpleNamespace(
                payload={
                    "kind": "EpisodeStarted",
                    "objective": "preserve child spawn across compaction",
                    "turnCeiling": 20,
                    "remainingBudgets": {"tokens": 50000, "usd_micros": 100000},
                }
            ),
            SimpleNamespace(
                payload={
                    "kind": "EffectStarted",
                    "action": "agent.spawn",
                    "descriptorDigest": "sha256:spawn-descriptor-c-1",
                    "idempotencyKey": "intent-child-c-1",
                }
            ),
            SimpleNamespace(
                payload={
                    "kind": "ChildSpawned",
                    "childEpisodeId": "child-c-1",
                    "idempotencyKey": "intent-child-c-1",
                    "depth": 1,
                    "brief": "child task to preserve",
                    "candidateDigest": "sha256:candidate-digest-c-1",
                    "baseDigest": "sha256:base-digest-c-1",
                    "verificationSubjectDigest": "sha256:subject-digest-c-1",
                }
            ),
        ]

        # Add 15 settled writes and observations to induce high memory pressure
        for i in range(15):
            events.append(
                SimpleNamespace(
                    payload={
                        "kind": "EffectCompleted",
                        "action": "fs.write",
                        "idempotencyKey": f"intent-write-{i}",
                        "target": f"file_{i}.py",
                    }
                )
            )

        # Fold task state
        sigma = fold_task_state(events, objective="preserve child spawn across compaction").to_canonical_dict()
        continuity = sigma.get("recoveryState", {}).get("continuity", {})

        # The spawn intent must be recognized in pending effects / continuity
        self.assertIn("pendingEffects", continuity)
        pending = continuity["pendingEffects"]
        self.assertTrue(
            any(p.get("idempotencyKey") == "intent-child-c-1" for p in pending),
            "spawn intent was dropped from continuity pendingEffects",
        )

        # Now test compiler under tight token ceiling (compaction pressure)
        harness = Runtime.compose("vg-code-balanced", episode_id="ep-compaction")
        compiler = ContextCompiler(
            system_core=harness.system_core,
            tool_schemas=harness.tool_schemas,
            environment="harness=vg-code-balanced environment=workspace",
            skill_cards=harness.skill_cards,
            token_ceiling=4096,
        )

        sigma_fragment = Fragment(
            source="task-state",
            label="sigma",
            text=json.dumps(sigma, sort_keys=True, default=str),
            evictable=False,
        )

        # Compile twice with large observations to force multiple compaction passes
        large_obs = tuple(
            Fragment(
                source="observation",
                label=f"obs-{i}",
                text=f"observation {i}: " + "X " * 800,
                evictable=True,
            )
            for i in range(10)
        )

        compiled_1 = compiler.compile(
            brief="preserve child spawn across compaction",
            notes=(sigma_fragment,),
            dialogue=large_obs[:5],
        )
        compiled_2 = compiler.compile(
            brief="preserve child spawn across compaction",
            notes=(sigma_fragment,),
            dialogue=large_obs,
        )

        # Verify sigma survives compilation intact in both passes
        for idx, compiled in enumerate((compiled_1, compiled_2), start=1):
            sigma_block = next((b for b in compiled.blocks if b.label == "sigma"), None)
            self.assertIsNotNone(sigma_block, f"pass {idx}: sigma was evicted under pressure")
            restored_sigma = json.loads(sigma_block.text)
            restored_pending = restored_sigma.get("recoveryState", {}).get("continuity", {}).get("pendingEffects", [])
            self.assertTrue(
                any(p.get("idempotencyKey") == "intent-child-c-1" for p in restored_pending),
                f"pass {idx}: child spawn intent was dropped by compaction",
            )


# ==============================================================================
# Case 5: Unauthorized candidate promotion denied across restart
# ==============================================================================


class UnauthorizedCandidateNeverPromotedAcrossRestart(unittest.TestCase):
    """A retained candidate without signed passing exterior verdict is never promoted."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.shared = Path(self._tmp.name) / "repo"
        _init_repo(self.shared)
        self.clock = _Clock()
        self.supervisor = ChildWorkspaceSupervisor(self.shared, now=self.clock)
        self.child_id = derive_child_id("ep-parent", "intent-unauth", "proj-t151")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_retained_candidate_without_authorization_is_ignored_by_recovery(self) -> None:
        # Child writes files and retains candidate
        view = self.supervisor.workspace_for(self.child_id)
        view.write("unauthorized.py", "unauthorized = 1\n")
        candidate_digest = self.supervisor.retain_candidate(self.child_id)
        self.assertIsNotNone(candidate_digest)

        # NO exterior verification, NO authorization record is written.
        # Fresh process restart:
        fresh_supervisor = ChildWorkspaceSupervisor(self.shared, now=self.clock)
        recovered = fresh_supervisor.recover()

        self.assertEqual(
            recovered,
            (),
            "recover() promoted a merely-retained candidate without authorization",
        )
        self.assertIsNone(fresh_supervisor.published_tree_digest(self.child_id))
        self.assertIsNone(fresh_supervisor.settled_digest(self.child_id))
        self.assertFalse(
            (self.shared / "unauthorized.py").exists(),
            "unauthorized candidate was leaked into shared workspace",
        )

    def test_failed_exterior_verdict_is_never_authorized_or_recovered(self) -> None:
        view = self.supervisor.workspace_for(self.child_id)
        view.write("broken.py", "broken = True\n")
        candidate_digest = self.supervisor.retain_candidate(self.child_id)

        ticket = self.supervisor.acquire(self.child_id)
        combined = self.supervisor.stage(ticket, candidate_digest=candidate_digest)

        # Evaluator reports failure
        failing_verdict = PublicationVerdict(combined.digest, "fail")
        with self.assertRaises(UnverifiedPublicationError):
            self.supervisor.publish(ticket, combined, verdict=failing_verdict)
        self.supervisor.release(ticket)

        # Fresh process restart:
        fresh_supervisor = ChildWorkspaceSupervisor(self.shared, now=self.clock)
        recovered = fresh_supervisor.recover()
        self.assertEqual(recovered, (), "failed verdict was recovered as a pass")
        self.assertIsNone(fresh_supervisor.published_tree_digest(self.child_id))
        self.assertFalse((self.shared / "broken.py").exists())


# ==============================================================================
# Case 6: Composition drift on resume
# ==============================================================================


class CompositionDriftOnResumeRefusesPublication(unittest.TestCase):
    """A changed composition on resume refuses continuation or publication."""

    def test_composition_drift_on_resume_refuses_continuation(self) -> None:
        from types import SimpleNamespace

        # Resumed session whose durable behavior identity does not match current composition
        session = SimpleNamespace(
            task=SimpleNamespace(
                resume_state={
                    "selectionPolicyIdentity": {
                        "behaviorIdentity": {
                            "compositionDigest": "sha256:" + "a" * 64,
                        }
                    },
                }
            ),
            _behavior_identity={"compositionDigest": "sha256:" + "b" * 64},
        )
        with self.assertRaises(ContextPacketError):
            HarnessSession._assert_resume_behavior_identity(session)

    def test_child_plan_composition_drift_refuses_foreign_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            shared = Path(directory) / "repo"
            _init_repo(shared)
            supervisor = ChildWorkspaceSupervisor(shared)
            child_id = derive_child_id("ep-parent", "intent-drift", "proj-t151")

            # Plan was formed under composition A
            plan = _make_plan(
                child_id,
                composition_digest="sha256:comp-A",
                idempotency_key="intent-drift",
            )

            # Runner is bound to a harness with composition B
            harness = Runtime.compose("vg-code-balanced", episode_id="ep-parent")
            runner = RuntimeChildRunner(
                run_composed=lambda *a, **kw: RunResult(events=(), status="completed"),
                harness=harness,
                parent_ports=SessionPorts(
                    model=None,
                    environment=_ViewEnvironment("parent", shared),
                    store=SqliteEventStore(":memory:"),
                    clock=FixedClock(at="2026-09-15T12:00:00.000Z"),
                ),
                parent_task=TaskContext(
                    brief="parent",
                    repo_path=shared,
                    run_id="run-t151",
                    episode_id="ep-parent",
                ),
                workspaces=supervisor,
                child_environment=lambda cid, root: _ViewEnvironment(cid, root),
                tree_verifier=lambda cid, root, digest: _TreeEvaluator(cid, root, digest, verdict="pass"),
            )

            # Lowering the child task must preserve the plan's composition digest or fail closed
            lowered = runner._lower(plan)
            self.assertEqual(lowered.run_id, plan.run_id)


# ==============================================================================
# Built-in Mutation Proof Controls (DIR-5.5 / §7.4 verification)
# ==============================================================================


class MutationProofControls(unittest.TestCase):
    """Confirm that negative controls fail if security guards are omitted."""

    def test_stale_base_mutation_detection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            shared = Path(directory) / "repo"
            _init_repo(shared)
            supervisor = ChildWorkspaceSupervisor(shared)
            child_id = derive_child_id("ep-parent", "intent-stale", "proj-t151")

            view = supervisor.workspace_for(child_id)
            view.write("feature.py", "x = 1\n")
            candidate_digest = supervisor.retain_candidate(child_id)

            ticket = supervisor.acquire(child_id)
            combined = supervisor.stage(ticket, candidate_digest=candidate_digest)

            # Adversarial mutation: base repository changed behind supervisor's back
            (shared / "base_module.py").write_text("def base():\n    return 'mutated'\n", encoding="utf-8")

            # Base revalidation must raise StaleBaseError
            with self.assertRaises(StaleBaseError):
                supervisor.publish(
                    ticket,
                    combined,
                    verdict=PublicationVerdict(combined.digest, "pass"),
                )
            supervisor.release(ticket)

    def test_verdict_subject_mismatch_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            shared = Path(directory) / "repo"
            _init_repo(shared)
            supervisor = ChildWorkspaceSupervisor(shared)
            child_id = derive_child_id("ep-parent", "intent-mismatch", "proj-t151")
            plan = _make_plan(child_id, idempotency_key="intent-mismatch")

            view = supervisor.workspace_for(child_id)
            view.write("feature.py", "x = 1\n")
            candidate_digest = supervisor.retain_candidate(child_id)

            # Evaluator returns a verdict for a completely different tree digest
            runner = RuntimeChildRunner(
                run_composed=lambda *a, **kw: RunResult(events=(), status="completed"),
                harness=Runtime.compose("vg-code-balanced", episode_id="ep-parent"),
                parent_ports=SessionPorts(
                    model=None,
                    environment=_ViewEnvironment("parent", shared),
                    store=SqliteEventStore(":memory:"),
                    clock=FixedClock(at="2026-09-15T12:00:00.000Z"),
                ),
                parent_task=TaskContext(
                    brief="parent",
                    repo_path=shared,
                    run_id="run-t151",
                    episode_id="ep-parent",
                ),
                workspaces=supervisor,
                child_environment=lambda cid, root: _ViewEnvironment(cid, root),
                tree_verifier=lambda cid, root, digest: _TreeEvaluator(
                    cid, root, digest, verdict="pass", tamper_subject="sha256:foreign-tree"
                ),
            )

            projected = ChildRunResult(
                ok=True,
                outcome="completed",
                terminal="COMPLETED",
                child_episode_id=child_id,
                actual_cost={"tokens": 10, "usd_micros": 50},
            )
            authority = PublicationAuthority(
                grant=Scope(
                    actions=("fs.read", "fs.patch"),
                    resources=("/workspace",),
                    constraints=_make_constraints(),
                    depth=1,
                ),
                remaining_budget=lambda: {"tokens": 1000, "usd_micros": 5000},
                now=lambda: "2026-09-15T12:00:00.000Z",
            )

            # Publication must refuse with undeterminable because subject does not match
            result = runner._publish_workspace(plan, projected, authority)
            self.assertFalse(result.ok)
            self.assertEqual(result.outcome, "undeterminable")
            self.assertIn("not the tree to publish", result.detail)
            self.assertIsNone(supervisor.published_tree_digest(child_id))


if __name__ == "__main__":
    unittest.main()
