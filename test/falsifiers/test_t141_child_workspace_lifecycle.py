"""T-141: a child mutates its own view, and shared mutation is fenced.

The defect this guards
----------------------
`RuntimeChildRunner._lower` handed every child `repo_path=parent_task.repo_path`
-- the *parent's own workspace*, unmodified. Recursion was real (the child
re-enters `run_composed`), authority was attenuated, and spend landed in one
ledger, but the filesystem was shared by every node in the tree with nothing
serialising it. Two causally-ready siblings mutating the same tree interleave
their edits; a child can write over its parent's working state; and a child
that dies mid-edit leaves the shared tree in a state nobody declared.

`DIR-C5`: git worktrees alone are not containment. A worktree gives a child a
separate *directory*; it does not say who may mutate the shared tree, for how
long, or what happens when that owner dies. The fence is the missing half.

What is proven here
-------------------
* a child cannot reach its parent's tree or a sibling's, by any spelling;
* shared mutation is serialised -- two children cannot both own the fence;
* ownership expires, and the writer whose lease expired is refused *by token*,
  not merely by clock, so a writer that slept through a takeover fails closed;
* a crash during mutation, during handoff, or during cleanup leaves no partial
  acceptance, loses no retained candidate, and settles no effect twice.

Every assertion below is mutation-proven against `runtime/workspace.py`; the
proof runs on the existing execution path (`derive_child_id`, the identity
`SpawnAdapter` actually mints), not on a private fixture identity scheme.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vanguard.packages.runtime.delegation import derive_child_id
from vanguard.packages.runtime.workspace import (
    ChildWorkspaceSupervisor,
    OwnershipConflict,
    StaleWriterError,
    WorkspaceEscapeError,
)


class _Clock:
    """A hand-wound clock. Expiry must be provable without sleeping."""

    def __init__(self, start: float = 1_000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class _Fixture(unittest.TestCase):
    """One shared tree, two children named the way the product names them."""

    LEASE = 60.0

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.shared = Path(self._tmp.name).resolve()
        (self.shared / "parent_secret.txt").write_text("parent state", encoding="utf-8")
        self.clock = _Clock()
        self.supervisor = self._supervisor()
        self.alice = derive_child_id("ep-parent", "intent-alice", "project-a")
        self.bob = derive_child_id("ep-parent", "intent-bob", "project-a")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _retained(self, child_id: str) -> str:
        """A real retained candidate, so an ownership refusal is unambiguous.

        A fence assertion made against a child with nothing retained passes for
        the wrong reason: `integrate` refuses the missing candidate before it
        ever consults ownership.
        """
        view = self.supervisor.workspace_for(child_id)
        view.write("out/a.py", "a = 1\n")
        view.write("out/b.py", "b = 2\n")
        return self.supervisor.retain_candidate(child_id)

    def _supervisor(self) -> ChildWorkspaceSupervisor:
        """A fresh supervisor over the same tree. Used to simulate a restart:
        a crash loses every in-memory fact and nothing on disk."""
        return ChildWorkspaceSupervisor(
            self.shared, now=self.clock, lease_seconds=self.LEASE)


class IsolationHoldsUnderEscape(_Fixture):
    """A view is a containment boundary, not a starting directory."""

    def test_a_child_view_is_not_the_parent_tree(self) -> None:
        view = self.supervisor.workspace_for(self.alice)
        self.assertNotEqual(view.root, self.shared)
        self.assertFalse(
            self.shared.samefile(view.root),
            "a child handed the parent's own tree has no isolation at all")

    def test_the_view_is_content_addressed_so_a_retry_finds_its_own_work(self) -> None:
        """Restart-stable identity is what makes retention recoverable."""
        self.supervisor.workspace_for(self.alice).write("draft.py", "x = 1\n")

        # A retry of the *same* intent derives the same child id, so the
        # restarted supervisor must land on the same view.
        again = derive_child_id("ep-parent", "intent-alice", "project-a")
        recovered = self._supervisor().workspace_for(again)
        self.assertEqual(recovered.read("draft.py"), "x = 1\n")

    def test_a_child_cannot_escape_upward_into_its_parent(self) -> None:
        view = self.supervisor.workspace_for(self.alice)
        for spelling in (
            "../parent_secret.txt",
            "../../parent_secret.txt",
            "a/../../parent_secret.txt",
            "./../parent_secret.txt",
        ):
            with self.subTest(spelling=spelling):
                with self.assertRaises(WorkspaceEscapeError):
                    view.write(spelling, "owned")
        self.assertEqual(
            (self.shared / "parent_secret.txt").read_text(encoding="utf-8"),
            "parent state", "a child reached its parent's tree")

    def test_a_child_cannot_reach_a_sibling(self) -> None:
        alice = self.supervisor.workspace_for(self.alice)
        bob = self.supervisor.workspace_for(self.bob)
        bob.write("bob_only.py", "bob = 1\n")

        relative = f"../{self.bob}/view/bob_only.py"
        with self.assertRaises(WorkspaceEscapeError):
            alice.write(relative, "alice was here")
        self.assertEqual(bob.read("bob_only.py"), "bob = 1\n")

    def test_an_absolute_path_is_refused_rather_than_silently_rebased(self) -> None:
        view = self.supervisor.workspace_for(self.alice)
        with self.assertRaises(WorkspaceEscapeError):
            view.write(str(self.shared / "parent_secret.txt"), "owned")

    def test_an_absolute_path_is_refused_even_when_it_points_inside(self) -> None:
        """The view API is relative-only, and says so rather than coping.

        Containment already rejects an absolute path aimed *outside*. This is
        the other half: a caller that builds paths by joining strings onto a
        root it should not have is refused while it is still harmless, instead
        of being quietly accommodated until the day it computes the root wrong.
        """
        view = self.supervisor.workspace_for(self.alice)
        with self.assertRaises(WorkspaceEscapeError):
            view.write(str(view.root / "legit.py"), "x = 1\n")

    def test_a_symlink_cannot_be_used_as_a_tunnel(self) -> None:
        view = self.supervisor.workspace_for(self.alice)
        try:
            (view.root / "tunnel").symlink_to(self.shared)
        except (OSError, NotImplementedError):  # pragma: no cover
            self.skipTest("platform does not permit symlink creation")
        with self.assertRaises(WorkspaceEscapeError):
            view.write("tunnel/parent_secret.txt", "owned")
        self.assertEqual(
            (self.shared / "parent_secret.txt").read_text(encoding="utf-8"),
            "parent state")


class TheFenceSerialisesSharedMutation(_Fixture):
    """Ownership of the shared tree is exclusive, expiring, and token-checked."""

    def test_two_children_cannot_both_own_the_fence(self) -> None:
        self.supervisor.acquire(self.alice)
        with self.assertRaises(OwnershipConflict):
            self.supervisor.acquire(self.bob)

    def test_the_loser_is_refused_rather_than_queued_behind_a_shared_tree(self) -> None:
        """Serialised means one owner at a time, not two writers taking turns."""
        ticket = self.supervisor.acquire(self.alice)
        with self.assertRaises(OwnershipConflict):
            self.supervisor.acquire(self.bob)
        self.supervisor.release(ticket)
        # Only once the owner releases may the sibling proceed.
        self.assertIsNotNone(self.supervisor.acquire(self.bob))

    def test_ownership_survives_a_restart_so_a_crash_does_not_free_the_tree(self) -> None:
        self.supervisor.acquire(self.alice)
        with self.assertRaises(OwnershipConflict):
            self._supervisor().acquire(self.bob)

    def test_an_expired_lease_is_reclaimable(self) -> None:
        self.supervisor.acquire(self.alice)
        self.clock.advance(self.LEASE + 1)
        self.assertIsNotNone(self.supervisor.acquire(self.bob))

    def test_a_stale_writer_is_refused_by_token_after_a_takeover(self) -> None:
        """Expiry alone is not containment; the fencing token is.

        The dangerous writer is not the one that checks the clock -- it is the
        one that was descheduled mid-call, woke after its lease was reclaimed,
        and still holds a ticket it believes is good. A takeover must invalidate
        that ticket by *token*, so the stale write fails closed even if the
        stale writer never looks at a clock again.
        """
        digest = self._retained(self.alice)
        stale = self.supervisor.acquire(self.alice)
        self.clock.advance(self.LEASE + 1)
        fresh = self.supervisor.acquire(self.bob)
        self.assertGreater(fresh.token, stale.token,
                           "a fencing token must be monotonic across takeover")

        # Rewind the clock so the stale ticket's own deadline looks valid: only
        # the token can still tell the truth.
        self.clock.now = stale.expires_at - 1
        with self.assertRaises(StaleWriterError):
            self.supervisor.integrate(stale, candidate_digest=digest)

    def test_a_childs_own_earlier_ticket_is_refused_after_it_reacquires(self) -> None:
        """The holder's *name* is not enough: a zombie writer is the same child.

        A child that hung, was presumed dead, and whose retry re-acquired the
        lease leaves two live tickets under one holder. Checking only the
        holder would accept both and let the zombie write through the retry's
        lease. Only the token separates them.
        """
        digest = self._retained(self.alice)
        first = self.supervisor.acquire(self.alice)
        second = self.supervisor.acquire(self.alice)  # the retry, same child
        self.assertGreater(second.token, first.token,
                           "re-acquiring must mint a new token, not reuse one")

        with self.assertRaises(StaleWriterError):
            self.supervisor.integrate(first, candidate_digest=digest)
        self.assertFalse(
            (self.shared / "out" / "a.py").exists(),
            "the zombie writer's candidate was applied through the retry's lease")

    def test_an_owner_whose_lease_expired_may_not_write_even_unopposed(self) -> None:
        """Nobody took over, so the token still matches. The deadline refuses.

        An owner presumed dead is one a competitor is entitled to displace at
        any moment. Letting it keep writing merely because no competitor has
        arrived yet makes the lease advisory, and the takeover a race.
        """
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        self.clock.advance(self.LEASE + 1)

        with self.assertRaises(StaleWriterError):
            self.supervisor.integrate(ticket, candidate_digest=digest)
        self.assertFalse((self.shared / "out" / "a.py").exists())

    def test_a_released_ticket_cannot_be_replayed(self) -> None:
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        self.supervisor.release(ticket)
        with self.assertRaises(StaleWriterError):
            self.supervisor.integrate(ticket, candidate_digest=digest)

    def test_releasing_a_ticket_that_no_longer_owns_the_fence_is_not_a_takeover(self) -> None:
        """A late cleanup must not free the *new* owner's lease."""
        stale = self.supervisor.acquire(self.alice)
        self.clock.advance(self.LEASE + 1)
        fresh = self.supervisor.acquire(self.bob)

        self.supervisor.release(stale)  # late cleanup from the dead writer
        with self.assertRaises(OwnershipConflict):
            self.supervisor.acquire(self.alice)
        self.supervisor.release(fresh)
        self.assertIsNotNone(self.supervisor.acquire(self.alice))


class CrashLeavesNoPartialAcceptance(_Fixture):
    """No partial accepted candidate, no lost artifact, no duplicate effect."""

    def test_a_retained_candidate_survives_a_crash_before_integration(self) -> None:
        digest = self._retained(self.alice)
        restarted = self._supervisor()
        self.assertEqual(restarted.candidate_digest(self.alice), digest,
                         "an accepted child's work was lost on restart")

    def test_integration_is_all_or_nothing(self) -> None:
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        self.supervisor.integrate(ticket, candidate_digest=digest)

        self.assertEqual((self.shared / "out" / "a.py").read_text(encoding="utf-8"), "a = 1\n")
        self.assertEqual((self.shared / "out" / "b.py").read_text(encoding="utf-8"), "b = 2\n")

    def test_a_crash_mid_integration_is_completed_by_recovery_not_left_partial(self) -> None:
        """Acceptance is the marker, written last. Until then nothing is accepted."""
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)

        # Crash after the first file lands and before acceptance is recorded.
        self.supervisor._apply_one(self.alice, "out/a.py")
        self.assertIsNone(self.supervisor.settled_digest(self.alice),
                          "a half-applied candidate must not read as accepted")

        restarted = self._supervisor()
        recovered = restarted.recover()
        self.assertIn(self.alice, recovered)
        self.assertEqual(restarted.settled_digest(self.alice), digest)
        self.assertEqual((self.shared / "out" / "b.py").read_text(encoding="utf-8"),
                         "b = 2\n", "recovery left the accepted candidate partial")

    def test_integrating_twice_settles_once(self) -> None:
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)

        first = self.supervisor.integrate(ticket, candidate_digest=digest)
        second = self.supervisor.integrate(ticket, candidate_digest=digest)
        self.assertEqual(first, "integrated")
        self.assertEqual(second, "already_integrated",
                         "a replayed integration settled the same effect twice")

    def test_a_crash_during_handoff_does_not_settle_twice_on_replay(self) -> None:
        """The retry cannot tell whether the first attempt landed. It must not
        matter: the settled marker is keyed by candidate, so replay converges."""
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        self.supervisor.integrate(ticket, candidate_digest=digest)

        restarted = self._supervisor()
        replay = restarted.acquire(self.alice)
        self.assertEqual(
            restarted.integrate(replay, candidate_digest=digest), "already_integrated")
        self.assertEqual(restarted.recover(), (),
                         "an already-settled child was re-integrated by recovery")

    def test_a_crash_during_cleanup_leaves_the_effect_settled_exactly_once(self) -> None:
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        self.supervisor.integrate(ticket, candidate_digest=digest)
        # Crash before `release`/cleanup ever runs: the lease is simply left
        # held, and expires. What must not happen is a second settlement.
        restarted = self._supervisor()
        self.clock.advance(self.LEASE + 1)
        self.assertEqual(restarted.settled_digest(self.alice), digest)
        self.assertEqual(restarted.recover(), ())

    def test_a_tampered_candidate_is_refused_rather_than_integrated(self) -> None:
        """Retention is content-addressed; acceptance checks what it applies."""
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        with self.assertRaises(StaleWriterError):
            self.supervisor.integrate(ticket, candidate_digest=digest[:-4] + "0000")
        self.assertFalse((self.shared / "out" / "a.py").exists(),
                         "a candidate that failed its digest check was applied anyway")

    def test_a_child_with_no_retained_candidate_integrates_nothing(self) -> None:
        ticket = self.supervisor.acquire(self.alice)
        with self.assertRaises(StaleWriterError):
            self.supervisor.integrate(ticket, candidate_digest="sha256:absent")


class TheChildRunnerUsesTheIsolatedView(_Fixture):
    """The wiring proof: isolation on the existing execution path, not beside it."""

    def test_the_lowered_task_points_at_the_childs_view_not_the_parent_tree(self) -> None:
        from vanguard.packages.runtime.child_runtime import RuntimeChildRunner

        runner, plan = _child_runner(self.shared, self.supervisor, self.alice)
        lowered = runner._lower(plan)

        self.assertNotEqual(lowered.repo_path, self.shared)
        self.assertEqual(
            lowered.repo_path,
            self.supervisor.workspace_for(self.alice).root,
            "the child ran in its parent's tree; DIR-C5 containment is absent")

    def test_without_a_supervisor_the_existing_behaviour_is_unchanged(self) -> None:
        """The seam is additive: an unsupervised composition still runs."""
        runner, plan = _child_runner(self.shared, None, self.alice)
        self.assertEqual(runner._lower(plan).repo_path, self.shared)


class TheLifecycleRunsOnTheExistingSpawnPath(_Fixture):
    """`run_child` retains, then integrates only what completed."""

    def _run(self, terminal: str, child_id: str):
        runner, plan = _child_runner(
            self.shared, self.supervisor, child_id, terminal=terminal)
        return runner.run_child(plan)

    def test_a_completed_child_lands_in_the_shared_tree(self) -> None:
        result = self._run("completed", self.alice)

        self.assertTrue(result.ok)
        self.assertEqual(
            (self.shared / "work.py").read_text(encoding="utf-8"), "done\n",
            "a completed child's work never reached the shared tree")
        self.assertEqual(self.supervisor.settled_digest(self.alice),
                         self.supervisor.candidate_digest(self.alice))

    def test_the_child_wrote_into_its_view_not_the_tree_it_integrated_into(self) -> None:
        """Integration is a separate, fenced step -- not a shared-tree write."""
        self._run("completed", self.alice)
        view = self.supervisor.workspace_for(self.alice)
        self.assertEqual(view.read("work.py"), "done\n")

    def test_an_incomplete_child_is_retained_but_never_integrated(self) -> None:
        result = self._run("abandoned", self.alice)

        self.assertFalse(result.ok)
        self.assertIsNotNone(self.supervisor.candidate_digest(self.alice),
                             "an abandoned child's work was discarded, not retained")
        self.assertIsNone(self.supervisor.settled_digest(self.alice))
        self.assertFalse((self.shared / "work.py").exists(),
                         "an incomplete child was partially accepted")

    def test_an_undeterminable_child_is_not_accepted(self) -> None:
        self._run("instrument_error", self.alice)
        self.assertIsNone(self.supervisor.settled_digest(self.alice))
        self.assertFalse((self.shared / "work.py").exists())

    def test_a_retried_spawn_settles_the_same_effect_once(self) -> None:
        """The retry derives the same child id, so it must converge, not double."""
        self._run("completed", self.alice)
        first = self.supervisor.settled_digest(self.alice)

        self._run("completed", self.alice)
        self.assertEqual(self.supervisor.settled_digest(self.alice), first)
        self.assertEqual(self.supervisor.recover(), (),
                         "a retried spawn left a second unsettled candidate")

    def test_the_fence_is_released_so_a_sibling_can_follow(self) -> None:
        self._run("completed", self.alice)
        self.assertIsNotNone(
            self.supervisor.acquire(self.bob),
            "the fence was left held after integration; siblings are blocked")

    def test_a_fence_refusal_is_not_reported_as_an_ordinary_success(self) -> None:
        """A completed child whose integration was refused must not read `ok`."""
        self.supervisor.acquire(self.bob)  # a sibling owns the tree
        with self.assertRaises(OwnershipConflict):
            self._run("completed", self.alice)
        self.assertIsNone(self.supervisor.settled_digest(self.alice))


def _child_runner(shared: Path, supervisor, child_id: str, terminal: str | None = None):
    """A `RuntimeChildRunner` and one plan, built the way the runtime builds them."""
    from vanguard.packages.runtime.child_runtime import RuntimeChildRunner
    from vanguard.packages.runtime.compose import TaskContext
    from vanguard.packages.ports.child_runtime import ChildRunPlan

    parent_task = TaskContext(
        brief="parent", repo_path=shared, run_id="run-1",
        episode_id="ep-parent", project_id="project-a", max_turns=4,
    )
    plan = ChildRunPlan(
        run_id="run-1",
        parent_episode_id="ep-parent",
        child_episode_id=child_id,
        project_id="project-a",
        brief="child",
        principal="child-principal",
        composition_digest="sha256:composition",
        goal_digest="sha256:goal",
        budget={},
        idempotency_key="intent-alice",
        authority=("fs.read",),
        resources=(),
        constraints={},
        depth=1,
        max_depth=4,
        max_turns=2,
        lineage=("ep-parent",),
        artifact_refs=(),
    )
    def run_composed(_harness, _ports, task, **_kwargs):
        """Stand in for one child episode: it writes where it was told to."""
        (Path(task.repo_path) / "work.py").write_text("done\n", encoding="utf-8")
        return _RunResult(terminal or "completed")

    runner = RuntimeChildRunner(
        run_composed=run_composed,
        parent_ports=_Ports(),
        harness=None,
        parent_task=parent_task,
        workspaces=supervisor,
    )
    return runner, plan


@dataclass(frozen=True)
class _Ports:
    """The fields `_rebind` narrows. A real `replace()` target, not a stub."""

    model: Any = None
    interactive: bool = True
    meta_controller: Any = None
    controller_confidence: tuple = ()
    child_runtime: Any = None
    environment_owner: bool = True


class _RunResult:
    """The historical `RunResult` fields `_project` reads from a double."""

    def __init__(self, terminal: str) -> None:
        self.terminal = terminal
        self.receipts = ()
        self.events = ()
        self.store = None
        self.run_digest = ""
        self.activation_digest = ""
        self.state_digest = ""
        self.detail = ""


if __name__ == "__main__":
    unittest.main()


class RetainedCandidateIntegrity(_Fixture):
    def test_retention_cannot_replace_an_existing_candidate(self) -> None:
        original = self._retained(self.alice)
        self.supervisor.workspace_for(self.alice).write("out/a.py", "replacement")
        with self.assertRaises(StaleWriterError):
            self.supervisor.retain_candidate(self.alice)
        self.assertEqual(self.supervisor.candidate_digest(self.alice), original)

    def test_modified_retained_bytes_cannot_keep_the_old_digest(self) -> None:
        digest = self._retained(self.alice)
        path = self.supervisor._child_dir(self.alice) / "candidate.json"
        record = json.loads(path.read_text())
        record["entries"]["out/a.py"] = "forged"
        path.write_text(json.dumps(record))
        ticket = self.supervisor.acquire(self.alice)
        with self.assertRaises(StaleWriterError):
            self.supervisor.integrate(ticket, candidate_digest=digest)
        self.assertFalse((self.shared / "out/a.py").exists())

    def test_unreadable_candidate_content_is_not_silently_omitted(self) -> None:
        view = self.supervisor.workspace_for(self.alice)
        (view.root / "binary.dat").write_bytes(b"\xff")
        with self.assertRaises(WorkspaceEscapeError):
            self.supervisor.retain_candidate(self.alice)

    def test_corrupt_fence_cannot_reset_ownership(self) -> None:
        self.supervisor.acquire(self.alice)
        self.supervisor._fence_path().write_text("{")
        with self.assertRaises(StaleWriterError):
            self.supervisor.acquire(self.bob)

    def test_recovery_rechecks_retained_content_identity(self) -> None:
        self._retained(self.alice)
        path = self.supervisor._child_dir(self.alice) / "candidate.json"
        record = json.loads(path.read_text())
        record["entries"]["out/a.py"] = "forged"
        path.write_text(json.dumps(record))
        with self.assertRaises(StaleWriterError):
            self._supervisor().recover()
        self.assertIsNone(self.supervisor.settled_digest(self.alice))

    def test_identical_retention_is_idempotent(self) -> None:
        original = self._retained(self.alice)
        self.assertEqual(self.supervisor.retain_candidate(self.alice), original)

    def test_competing_threads_cannot_both_acquire(self) -> None:
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        barrier = Barrier(2)
        def acquire(child):
            barrier.wait(timeout=5)
            try:
                self._supervisor().acquire(child)
                return True
            except OwnershipConflict:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(acquire, (self.alice, self.bob)))
        self.assertEqual(sum(results), 1)
