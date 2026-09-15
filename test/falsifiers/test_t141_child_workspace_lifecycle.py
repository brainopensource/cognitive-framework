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

from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.delegation import derive_child_id
from vanguard.packages.runtime.workspace import (
    ChildWorkspaceSupervisor,
    CombinedTree,
    OwnershipConflict,
    PublicationAuthority,
    PublicationVerdict,
    StaleBaseError,
    StaleWriterError,
    UnverifiedPublicationError,
    WorkspaceEscapeError,
    _atomic_write,
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

    def _crash_mid_publication(self, child_id: str, digest: str) -> str:
        """Authorize a publication, land one file, then die before the marker.

        The crash is injected at the one instant that can leave the shared tree
        in a state nobody declared: after the authorization is durable and
        after the first byte lands, before acceptance is recorded.
        """
        ticket = self.supervisor.acquire(child_id)
        combined = self.supervisor.stage(ticket, candidate_digest=digest)

        def half(cid: str) -> None:
            record = self.supervisor._authorization(cid)
            first = sorted(record["entries"])[0]
            _atomic_write(
                self.supervisor._shared_target(first), record["entries"][first])

        original = self.supervisor._apply_authorized
        self.supervisor._apply_authorized = half  # type: ignore[method-assign]
        try:
            self.supervisor.publish(ticket, combined, verdict=_passing(combined))
        finally:
            self.supervisor._apply_authorized = original  # type: ignore[method-assign]
        return combined.digest

    def _publish(
        self,
        ticket,
        digest: str,
        *,
        supervisor: ChildWorkspaceSupervisor | None = None,
        verdict: PublicationVerdict | None = None,
    ) -> str:
        """Stage, verify and publish -- the whole authorized path, once.

        Written as one helper because the three steps are not independently
        meaningful: a staged tree nobody verified may not be published, and a
        verdict about anything other than the staged tree is not a verdict
        about what lands. Tests that want to break one of those links do it
        explicitly below rather than by leaving a step out here.
        """
        supervisor = supervisor or self.supervisor
        combined = supervisor.stage(ticket, candidate_digest=digest)
        return supervisor.publish(
            ticket, combined, verdict=verdict or _passing(combined))


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
            self._publish(stale, digest)

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
            self._publish(first, digest)
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
            self._publish(ticket, digest)
        self.assertFalse((self.shared / "out" / "a.py").exists())

    def test_a_released_ticket_cannot_be_replayed(self) -> None:
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        self.supervisor.release(ticket)
        with self.assertRaises(StaleWriterError):
            self._publish(ticket, digest)

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


class TheBaseIsTheWorkingTreeNotTheRepository(_Fixture):
    """What a candidate is computed against is content, not VCS metadata."""

    def test_repository_metadata_is_not_part_of_the_base(self) -> None:
        """Otherwise any `git` command makes every candidate stale."""
        (self.shared / ".git").mkdir()
        (self.shared / ".git" / "HEAD").write_text("ref: main\n", encoding="utf-8")
        digest = self._retained(self.alice)

        (self.shared / ".git" / "HEAD").write_text("ref: other\n", encoding="utf-8")
        ticket = self.supervisor.acquire(self.alice)
        self.assertEqual(self._publish(ticket, digest), "published",
                         "a git operation was mistaken for a concurrent mutation")

    def test_a_candidate_cannot_publish_into_repository_metadata(self) -> None:
        """The exclusion cuts both ways, or it is an escape hatch.

        `.git` is excluded from the base, so nothing compares it. A candidate
        allowed to write there would be writing the one directory no staleness
        check can see -- and a published `.git/config` carrying
        `core.hooksPath` executes on the parent's next git command.
        """
        view = self.supervisor.workspace_for(self.alice)
        view.write(".git/config", "[core]\n\thooksPath = /tmp/evil\n")
        digest = self.supervisor.retain_candidate(self.alice)
        ticket = self.supervisor.acquire(self.alice)

        with self.assertRaises(WorkspaceEscapeError):
            self._publish(ticket, digest)
        self.assertFalse((self.shared / ".git" / "config").exists(),
                         "a child rewrote the repository's own configuration")
        self.assertIsNone(self.supervisor.settled_digest(self.alice))

    def test_the_control_directory_is_still_refused(self) -> None:
        """A candidate that could forge acceptance would settle itself."""
        view = self.supervisor.workspace_for(self.alice)
        view.write(".vanguard/children/fence.json", "forged")
        digest = self.supervisor.retain_candidate(self.alice)
        ticket = self.supervisor.acquire(self.alice)

        with self.assertRaises(WorkspaceEscapeError):
            self._publish(ticket, digest)
        self.assertIsNone(self.supervisor.settled_digest(self.alice))


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
        self._publish(ticket, digest)

        self.assertEqual((self.shared / "out" / "a.py").read_text(encoding="utf-8"), "a = 1\n")
        self.assertEqual((self.shared / "out" / "b.py").read_text(encoding="utf-8"), "b = 2\n")

    def test_a_crash_mid_publication_is_completed_by_recovery_not_left_partial(self) -> None:
        """Acceptance is the marker, written last. Until then nothing is accepted."""
        digest = self._retained(self.alice)
        tree = self._crash_mid_publication(self.alice, digest)
        self.assertIsNone(self.supervisor.settled_digest(self.alice),
                          "a half-applied candidate must not read as accepted")

        restarted = self._supervisor()
        recovered = restarted.recover()
        self.assertIn(self.alice, recovered)
        self.assertEqual(restarted.settled_digest(self.alice), digest)
        self.assertEqual(restarted.published_tree_digest(self.alice), tree)
        self.assertEqual((self.shared / "out" / "b.py").read_text(encoding="utf-8"),
                         "b = 2\n", "recovery left the accepted candidate partial")

    def test_integrating_twice_settles_once(self) -> None:
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)

        first = self._publish(ticket, digest)
        second = self._publish(ticket, digest)
        self.assertEqual(first, "published")
        self.assertEqual(second, "already_published",
                         "a replayed publication settled the same effect twice")

    def test_a_crash_during_handoff_does_not_settle_twice_on_replay(self) -> None:
        """The retry cannot tell whether the first attempt landed. It must not
        matter: the settled marker is keyed by candidate, so replay converges."""
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        self._publish(ticket, digest)

        restarted = self._supervisor()
        replay = restarted.acquire(self.alice)
        self.assertEqual(
            self._publish(replay, digest, supervisor=restarted), "already_published")
        self.assertEqual(restarted.recover(), (),
                         "an already-settled child was re-integrated by recovery")

    def test_a_crash_during_cleanup_leaves_the_effect_settled_exactly_once(self) -> None:
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        self._publish(ticket, digest)
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
            self._publish(ticket, digest[:-4] + "0000")
        self.assertFalse((self.shared / "out" / "a.py").exists(),
                         "a candidate that failed its digest check was applied anyway")

    def test_a_child_with_no_retained_candidate_integrates_nothing(self) -> None:
        ticket = self.supervisor.acquire(self.alice)
        with self.assertRaises(StaleWriterError):
            self._publish(ticket, "sha256:absent")


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
    """`run_child_authorized` retains, then publishes only what earns it."""

    def _run(self, terminal: str, child_id: str, **kwargs):
        runner, plan = _child_runner(
            self.shared, self.supervisor, child_id, terminal=terminal, **kwargs)
        self.runner = runner
        return runner.run_child_authorized(plan, _authority())

    def test_a_completed_child_lands_in_the_shared_tree(self) -> None:
        result = self._run("completed", self.alice)

        self.assertTrue(result.ok)
        self.assertEqual(
            (self.shared / "work.py").read_text(encoding="utf-8"), "done\n",
            "a completed child's work never reached the shared tree")
        self.assertEqual(self.supervisor.settled_digest(self.alice),
                         self.supervisor.candidate_digest(self.alice))

    def test_the_child_ran_against_its_own_adapter_not_the_parents(self) -> None:
        """`DIR-C5`. A view the child does not actually write through is a lie."""
        self._run("completed", self.alice)
        adapters = self.runner.environments

        self.assertEqual(len(adapters), 1, "no child-local adapter was built")
        self.assertEqual(
            adapters[0].root,
            self.supervisor.workspace_for(self.alice).root,
            "the child's effects were bound to a root it does not own")
        self.assertTrue(adapters[0].disposed,
                        "the child's own adapter outlived the child episode")

    def test_what_was_verified_is_exactly_what_was_published(self) -> None:
        """`DIR-C7`. Verifying the view and publishing the tree verifies nothing."""
        self._run("completed", self.alice)
        evaluator = self.runner.evaluators[0]

        published = self.supervisor.published_tree_digest(self.alice)
        self.assertEqual(evaluator.tree_digest, published,
                         "the evaluator saw a tree other than the one published")
        self.assertIn("work.py", evaluator.seen)
        self.assertIn("parent_secret.txt", evaluator.seen,
                      "the verified tree was the child's view, not the "
                      "combined tree the parent ends up with")

    def test_an_unverified_child_is_not_published_on_completion_alone(self) -> None:
        """Completion produces a candidate. It does not produce permission."""
        runner, plan = _child_runner(
            self.shared, self.supervisor, self.alice, terminal="completed")
        result = runner.run_child(plan)  # no authority accompanies it

        self.assertFalse(result.ok)
        self.assertEqual(result.outcome, "undeterminable")
        self.assertIn("not published", result.detail)
        self.assertIsNone(self.supervisor.settled_digest(self.alice))
        self.assertFalse((self.shared / "work.py").exists())

    def test_a_failing_exterior_verdict_refuses_the_publication(self) -> None:
        """A `fail` about the *right* tree. Binding alone must not admit it.

        The evaluator is built through the factory so it is bound to the exact
        staged tree: a control that rejected on a mismatched subject would
        prove the subject check twice and the verdict check never.
        """
        runner, plan = _child_runner(
            self.shared, self.supervisor, self.alice, terminal="completed")
        runner._tree_verifier = lambda cid, root, digest: _ScriptedEvaluator(
            Path(root), digest, verdict="fail")
        result = runner.run_child_authorized(plan, _authority())

        self.assertFalse(result.ok)
        self.assertIsNone(self.supervisor.settled_digest(self.alice))
        self.assertFalse((self.shared / "work.py").exists(),
                         "a rejected candidate reached the shared tree")

    def test_a_rejected_verdict_is_refused_at_the_publication_boundary(self) -> None:
        """The same refusal one layer down, where the tree actually changes.

        `_verify_tree` can refuse a verdict before `publish` ever sees it, so
        the supervisor is exercised directly here: a caller holding the fence,
        a live base and a correctly bound verdict that simply did not pass must
        still be refused, or the gate lives only in the caller.
        """
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        combined = self.supervisor.stage(ticket, candidate_digest=digest)

        with self.assertRaises(UnverifiedPublicationError):
            self.supervisor.publish(ticket, combined, verdict=PublicationVerdict(
                subject_digest=combined.digest, disposition="failed",
                envelope_digest="sha256:envelope"))
        self.assertFalse((self.shared / "out" / "a.py").exists())
        self.assertIsNone(self.supervisor.settled_digest(self.alice))

    def test_an_undeterminable_verdict_is_not_a_pass(self) -> None:
        digest = self._retained(self.alice)
        ticket = self.supervisor.acquire(self.alice)
        combined = self.supervisor.stage(ticket, candidate_digest=digest)

        with self.assertRaises(UnverifiedPublicationError):
            self.supervisor.publish(ticket, combined, verdict=PublicationVerdict(
                subject_digest=combined.digest, disposition="undeterminable"))
        self.assertFalse((self.shared / "out" / "a.py").exists())

    def test_a_verdict_about_another_tree_refuses_the_publication(self) -> None:
        """Candidate substitution: a real pass, bound to something else."""
        runner, plan = _child_runner(
            self.shared, self.supervisor, self.alice, terminal="completed",
            evaluator=_ScriptedEvaluator(
                self.shared, "sha256:other", subject="sha256:other"))
        result = runner.run_child_authorized(plan, _authority())

        self.assertFalse(result.ok)
        self.assertFalse((self.shared / "work.py").exists())

    def test_a_signed_pass_with_no_executed_tests_is_not_a_publication(self) -> None:
        """Vacuous verification is missingness, not a pass (`ADR-0076 §5`)."""
        runner, plan = _child_runner(
            self.shared, self.supervisor, self.alice, terminal="completed",
            evaluator=None)
        runner._tree_verifier = lambda cid, root, digest: _ScriptedEvaluator(
            Path(root), digest, executed=0)
        result = runner.run_child_authorized(plan, _authority())

        self.assertFalse(result.ok)
        self.assertFalse((self.shared / "work.py").exists())

    def test_an_expired_grant_refuses_the_publication(self) -> None:
        """A long child does not extend the authority that admitted it."""
        runner, plan = _child_runner(
            self.shared, self.supervisor, self.alice, terminal="completed")
        result = runner.run_child_authorized(
            plan, _authority(expires_at="2026-09-15T11:00:00.000Z"))

        self.assertFalse(result.ok)
        self.assertIn("grant expired", result.detail)
        self.assertFalse((self.shared / "work.py").exists())

    def test_authority_the_current_grant_no_longer_carries_refuses(self) -> None:
        runner, plan = _child_runner(
            self.shared, self.supervisor, self.alice, terminal="completed")
        result = runner.run_child_authorized(plan, _authority(actions=("fs.stat",)))

        self.assertFalse(result.ok)
        self.assertFalse((self.shared / "work.py").exists())

    def test_a_sibling_that_moved_the_tree_makes_the_base_stale(self) -> None:
        """Stale base: the candidate describes a tree that no longer exists."""
        runner, plan = _child_runner(
            self.shared, self.supervisor, self.alice, terminal="completed")
        self.supervisor.workspace_for(self.alice, seed=True)  # bind the base
        (self.shared / "parent_secret.txt").write_text("moved", encoding="utf-8")

        result = runner.run_child_authorized(plan, _authority())
        self.assertFalse(result.ok)
        self.assertFalse((self.shared / "work.py").exists(),
                         "a candidate computed against a stale base was published")
        self.assertEqual(
            (self.shared / "parent_secret.txt").read_text(encoding="utf-8"), "moved",
            "publication overwrote the change that made the base stale")

    def test_an_uncontained_runner_never_reaches_a_child_episode(self) -> None:
        """No child-local adapter means the child does not run at all."""
        runner, plan = _child_runner(
            self.shared, self.supervisor, self.alice, terminal="completed",
            contained=False)
        self.assertFalse(runner.is_contained())
        with self.assertRaises(Exception):
            runner.run_child_authorized(plan, _authority())
        self.assertIsNone(self.supervisor.candidate_digest(self.alice),
                          "an uncontained child ran far enough to produce work")

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
        """A completed child whose publication was refused must not read `ok`."""
        self.supervisor.acquire(self.bob)  # a sibling owns the tree
        result = self._run("completed", self.alice)

        self.assertFalse(result.ok, "a refused publication was reported as success")
        self.assertEqual(result.outcome, "undeterminable")
        self.assertIsNone(self.supervisor.settled_digest(self.alice))
        self.assertFalse((self.shared / "work.py").exists())


def _passing(combined: CombinedTree, *, subject: str | None = None) -> PublicationVerdict:
    """The verdict shape publication accepts: a pass bound to one exact tree."""
    return PublicationVerdict(
        subject_digest=subject if subject is not None else combined.digest,
        disposition="passed",
        envelope_digest="sha256:envelope",
    )


class _ScriptedEvaluator:
    """An exterior evaluator over one staged tree.

    It signs and binds like the daemon does, because that is what publication
    revalidates: an unsigned or unbound result has nothing to publish on, and
    `evaluator_gateway.settlement_payload` is the same code that decides what
    may be ledgered. It reads the staged tree it was handed, so a test that
    verifies one tree and publishes another is caught rather than arranged.
    """

    def __init__(self, root: Path, tree_digest: str, *, verdict: str = "pass",
                 subject: str | None = None, executed: int = 3) -> None:
        self.root = root
        self.tree_digest = tree_digest
        self._verdict = verdict
        self._subject = subject
        self._executed = executed
        self.seen: list[str] = []

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol):
        self.seen = sorted(
            path.relative_to(self.root).as_posix()
            for path in self.root.rglob("*") if path.is_file())
        binding = {
            "verdict": self._verdict,
            "subject_digest": self._subject or self.tree_digest,
            "oracle_digest": "sha256:oracle",
            "executed_test_count": self._executed,
        }
        return Result.success(Verdict(
            outcome="claims", claims=(), reason="",
            signature="sig", signer_key_id="key-1", binding=binding))


class _FakeChildEnvironment:
    """A child-local effect adapter. It owns one root and disposes itself."""

    def __init__(self, child_id: str, root: Path) -> None:
        self.child_id = child_id
        self.root = Path(root)
        self.disposed = False

    def dispose(self):
        self.disposed = True
        return None


def _child_runner(
    shared: Path,
    supervisor,
    child_id: str,
    terminal: str | None = None,
    *,
    contained: bool = True,
    evaluator: Any = None,
):
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

    environments: list[_FakeChildEnvironment] = []
    evaluators: list[Any] = []

    def child_environment(cid: str, root: Path) -> _FakeChildEnvironment:
        adapter = _FakeChildEnvironment(cid, root)
        environments.append(adapter)
        return adapter

    def tree_verifier(cid: str, root: Path, tree_digest: str) -> Any:
        bound = evaluator or _ScriptedEvaluator(Path(root), tree_digest)
        evaluators.append(bound)
        return bound

    runner = RuntimeChildRunner(
        run_composed=run_composed,
        parent_ports=_Ports(),
        harness=_Harness(),
        parent_task=parent_task,
        workspaces=supervisor,
        child_environment=child_environment if contained else None,
        tree_verifier=tree_verifier if contained else None,
    )
    runner.environments = environments  # type: ignore[attr-defined]
    runner.evaluators = evaluators  # type: ignore[attr-defined]
    return runner, plan


@dataclass(frozen=True)
class _Harness:
    """The one field `_verify_tree` reads: the oracle the pack declared."""

    evaluators: tuple = ("oracle-1",)


def _authority(
    *,
    actions: tuple = ("fs.read",),
    expires_at: str = "2099-01-01T00:00:00.000Z",
    remaining: dict | None = None,
) -> PublicationAuthority:
    """The live grant/budget authority `SpawnAdapter` hands the runner."""
    from vanguard.packages.kernel.attenuation import Constraints, Scope

    return PublicationAuthority(
        grant=Scope(
            actions=frozenset(actions),
            resources=(),
            constraints=Constraints(
                expires_at=expires_at, max_uses=10, budget_usd_micros=1_000_000,
                max_bytes=None, max_effects=None, risk_ceiling="low",
                max_depth=4, network_policy="deny",
            ),
            depth=1,
        ),
        remaining_budget=lambda: dict(remaining or {"usd_micros": 1_000_000}),
        now=lambda: "2026-09-15T12:00:00.000Z",
    )


@dataclass(frozen=True)
class _Ports:
    """The fields `_rebind` narrows. A real `replace()` target, not a stub."""

    model: Any = None
    environment: Any = None
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
            self._publish(ticket, digest)
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

    def test_recovery_never_promotes_a_merely_retained_candidate(self) -> None:
        """Retention is work. Authorization is permission. They are not the same.

        This is the defect the T-141 delivery ruling named: a recovery pass
        that re-applies every retained candidate publishes work that no fence,
        no base check, no grant and no evaluator ever admitted -- and does it
        on a restart, where none of that authority can be re-derived.
        """
        self._retained(self.alice)  # retained, never staged, never authorized
        restarted = self._supervisor()

        self.assertEqual(restarted.recover(), (),
                         "recovery published a candidate nothing authorized")
        self.assertIsNone(restarted.settled_digest(self.alice))
        self.assertFalse((self.shared / "out" / "a.py").exists())
        self.assertFalse((self.shared / "out" / "b.py").exists())

    def test_recovery_refuses_a_candidate_whose_child_never_completed(self) -> None:
        """An abandoned child's work is retained and stays unpublished."""
        runner, plan = _child_runner(
            self.shared, self.supervisor, self.alice, terminal="abandoned")
        runner.run_child_authorized(plan, _authority())
        self.assertIsNotNone(self.supervisor.candidate_digest(self.alice))

        self.assertEqual(self._supervisor().recover(), ())
        self.assertFalse((self.shared / "work.py").exists(),
                         "recovery accepted a child that never completed")

    def test_recovery_rechecks_authorized_content_identity(self) -> None:
        """Recovery re-applies bytes; it must prove they are the verified bytes."""
        digest = self._retained(self.alice)
        self._crash_mid_publication(self.alice, digest)
        path = self.supervisor._child_dir(self.alice) / "authorized.json"
        record = json.loads(path.read_text())
        record["entries"]["out/b.py"] = "forged"
        path.write_text(json.dumps(record))

        with self.assertRaises(UnverifiedPublicationError):
            self._supervisor().recover()
        self.assertIsNone(self.supervisor.settled_digest(self.alice))
        self.assertFalse((self.shared / "out" / "b.py").exists(),
                         "recovery applied content no evaluator ever saw")

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
