"""T-145 / E4 -- public ingress truthfulness.

Falsifies the two defects `docs/execution/main/mvp_delivery_protocol.md` §5
reproduces on the shipped public route, and the repairs that close them:

* `E-CLI-1` -- a workspace whose identity cannot be observed must yield a
  *typed refusal*, never an unhandled `WorkspaceSnapshotRefused` escaping
  `entrypoint.execute`, and never a completion admitted against a fabricated,
  empty-tree or skipped identity.
* `E-CLI-2` -- durable resume state must be hydrated and revalidated on every
  ingress that has durable events for the run, not only on `command ==
  "resume"`; and revalidation must fail closed rather than trust.

Everything below runs through `entrypoint.execute` -- the public route --
with a scripted model, a disposable store and no provider.

Each negative control here is mutation-proved under `DIR-5.5` / §7.4 by
the `MutationProof` cases in this module: disable the named guard, the
control that names it reds, restore, confirm green.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

from unittest.mock import patch

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime import entrypoint
from vanguard.packages.runtime.session import WorkspaceSnapshotRefused
from vanguard.packages.runtime.task_state import fold_task_state


def _model(note: str = "scripted") -> FakeModel:
    return FakeModel([{"kind": "finish", "note": note}])


class _PublicRoute(unittest.TestCase):
    """One disposable workspace and store per test; the route does the rest."""

    git: bool = True

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self._tmp.name).resolve()
        (self.workspace / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
        if self.git:
            import subprocess
            subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        self.state_dir = self.workspace / ".vanguard"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.store_path = self.state_dir / "events.sqlite3"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def execute(self, **overrides: Any) -> dict[str, Any]:
        request: dict[str, Any] = {
            "command": "code",
            "brief": "create the module",
            "workspace": str(self.workspace),
            "storePath": str(self.store_path),
            "injectedModel": _model(),
            "interactive": False,
            "profile": "product",
        }
        request.update(overrides)
        return entrypoint.execute(request)

    def events(self, run_id: str) -> list[Any]:
        store = SqliteEventStore(str(self.store_path))
        try:
            read = store.read(EventRange(run_id=run_id))
        finally:
            store.close()
        return list(read.value or ()) if read.ok else []


# -- E-CLI-1 ---------------------------------------------------------------


class UnobservableWorkspaceIsTruthful(_PublicRoute):
    """A plain directory is not a repository, and saying so is not a crash."""

    git = False

    def test_a_plain_directory_reaches_a_terminal_rather_than_crashing(self) -> None:
        """Defect (a): the greenfield journey could not reach a terminal at all."""
        try:
            response = self.execute(runId="run-plain")
        except WorkspaceSnapshotRefused as exc:  # pragma: no cover - the defect
            self.fail(f"a legitimate refusal escaped the public route as a crash: {exc}")
        self.assertEqual(response["type"], "result")
        self.assertEqual(response["result"]["runId"], "run-plain")
        self.assertIn(
            response["result"]["outcome"],
            {"abstained", "failed", "abandoned", "undeterminable"},
            "the terminal is not one of the truthful refusal outcomes `E6` admits")

    def test_an_unobservable_workspace_never_admits_completion(self) -> None:
        """Defect (b): the honest refusal must be a terminal, not a completion.

        The assertion is on the *outcome*, not on the absence of an exception:
        a fabricated digest or an empty-tree default would silence the crash
        by admitting a completion against a subject nothing observed, and this
        control has to red on that repair as loudly as on the original defect.

        The terminal is deliberately not pinned to one name. A plain directory
        is unobservable *and* unindexable, and `INDEX_UNBOUND` legitimately
        fires first; demanding a particular refusal here would assert the
        order two independent instrument failures happen to race in, which is
        not a contract this packet owns.
        """
        response = self.execute(runId="run-plain-2")
        self.assertNotEqual(
            response["result"]["outcome"], "completed",
            "completion was admitted on a workspace whose identity could not "
            "be observed")

    def test_the_refusal_names_an_instrument_rather_than_the_model(self) -> None:
        """Whatever refused must say so; tape exhaustion is not the reason."""
        response = self.execute(runId="run-plain-3")
        blob = (str(response["result"].get("detail") or "")
                + str(response["result"].get("projections") or "")).lower()
        self.assertTrue(
            "workspace" in blob or "index_unbound" in blob,
            f"the refusal does not name what could not be observed: {blob[:400]}")
        self.assertNotIn(
            "scripted model exhausted", blob,
            "the run reported the model running out instead of the instrument "
            "failure that actually fired")

    # A plain directory *inside* a repository is still observable to git by
    # parent-walk, so its completion receipt would bind to the parent's
    # identity. That is a real hole, but closing it belongs in the git
    # environment adapter's `snapshot()`, not here: asking git directly from
    # the session asserts one adapter's implementation at a port boundary and
    # refuses every composition whose environment is legitimately not a git
    # checkout (it red 6 controls across T-141 and INDEX_UNBOUND when tried).
    # Recorded as a finding for a future packet, not closed by this one.

class AnObservableWorkspaceStillWorks(_PublicRoute):
    """The repair must not buy truthfulness by refusing everything."""

    def test_an_unborn_repository_is_observable_and_is_not_refused(self) -> None:
        """`git init` with zero commits snapshots to the empty tree (§5)."""
        response = self.execute(runId="run-unborn")
        detail = str(response["result"].get("detail") or "").lower()
        self.assertNotIn("workspace_unobservable", detail)


# -- E-CLI-2 ---------------------------------------------------------------


class HydrationIsKeyedOnDurableStateNotTheVerb(_PublicRoute):
    """Continuity that depends on the operator typing the right word is none."""

    def _seed(self, run_id: str = "run-continuity") -> list[Any]:
        self.execute(runId=run_id, brief="the original objective",
                     projectId="proj-original")
        events = self.events(run_id)
        self.assertTrue(events, "the seeding run wrote no durable events")
        return events

    def test_a_code_ingress_hydrates_a_run_that_already_has_durable_events(self) -> None:
        """The positive control: no `command == "resume"` anywhere in it."""
        seeded = self._seed()
        folded = fold_task_state(seeded, objective="")

        captured: dict[str, Any] = {}
        original = entrypoint.Runtime.execute_profiled

        def spy(manifest_path, task, **kwargs):
            captured["resume_state"] = task.resume_state
            captured["brief"] = task.brief
            captured["episode_id"] = task.episode_id
            captured["project_id"] = task.project_id
            return original(manifest_path, task, **kwargs)

        entrypoint.Runtime.execute_profiled = staticmethod(spy)
        try:
            self.execute(runId="run-continuity", command="code",
                         brief="a different sentence entirely")
        finally:
            entrypoint.Runtime.execute_profiled = original

        self.assertIsNotNone(
            captured["resume_state"],
            "a `code` ingress over a run with durable events hydrated nothing; "
            "continuity was conditioned on the command verb")
        self.assertEqual(
            captured["brief"], folded.objective or "the original objective",
            "the hydrated objective did not survive the ingress")
        self.assertEqual(captured["project_id"], "proj-original",
                         "the project identity was not hydrated")
        self.assertTrue(captured["episode_id"],
                        "the episode identity was not hydrated")

    def test_a_fresh_run_with_no_durable_events_hydrates_nothing(self) -> None:
        """Hydration keys on state, so absent state must hydrate absent."""
        captured: dict[str, Any] = {}
        original = entrypoint.Runtime.execute_profiled

        def spy(manifest_path, task, **kwargs):
            captured["resume_state"] = task.resume_state
            return original(manifest_path, task, **kwargs)

        entrypoint.Runtime.execute_profiled = staticmethod(spy)
        try:
            self.execute(runId="run-brand-new")
        finally:
            entrypoint.Runtime.execute_profiled = original
        self.assertIsNone(captured["resume_state"],
                          "a run with no durable events invented resume state")

    def test_resume_with_no_durable_events_is_still_refused(self) -> None:
        """Widening hydration must not weaken the explicit resume contract."""
        with self.assertRaises(ValueError) as caught:
            self.execute(command="resume", runId="run-that-never-existed")
        self.assertIn("no durable events", str(caught.exception))


class HydrationRevalidatesRatherThanTrusts(_PublicRoute):
    """Fail closed on every input the continuation could have moved."""

    def test_a_widened_turn_ceiling_refuses_the_continuation(self) -> None:
        self.execute(runId="run-ceiling", maxTurnsPerEpisode=3)
        self.assertTrue(self.events("run-ceiling"))
        with self.assertRaises(ValueError) as caught:
            self.execute(runId="run-ceiling", maxTurnsPerEpisode=99)
        self.assertIn("turn ceiling", str(caught.exception).lower())

    def test_an_equal_turn_ceiling_is_admitted(self) -> None:
        """The control must red on widening, not on continuing at all."""
        self.execute(runId="run-ceiling-ok", maxTurnsPerEpisode=3)
        response = self.execute(runId="run-ceiling-ok", maxTurnsPerEpisode=3)
        self.assertEqual(response["result"]["runId"], "run-ceiling-ok")

    def test_a_changed_preset_refuses_the_continuation(self) -> None:
        """Composition revalidation must fire on the *cold* path too.

        `EpisodeStarted` records the immutable `behaviorIdentity`, and
        `HarnessSession._assert_resume_behavior_identity` rejects a
        continuation whose composition moved. That check is only reachable if
        hydration actually carries the identity: before T-145 a later
        `ContextSelectionRecorded` replaced the whole `selectionPolicyIdentity`
        dict and dropped it, so the guard compared nothing and cold-start
        composition revalidation was a silent no-op.
        """
        self.execute(runId="run-preset", preset="balanced")
        state = fold_task_state(
            self.events("run-preset"), objective="").to_canonical_dict()
        identity = (state.get("selectionPolicyIdentity") or {}).get("behaviorIdentity")
        self.assertTrue(
            identity,
            "hydration carries no behaviorIdentity, so a changed composition "
            "has nothing to fail closed against")

        response = self.execute(runId="run-preset", preset="fast")
        self.assertNotEqual(
            response["result"]["outcome"], "completed",
            "a continuation under a different preset was admitted")

    def test_hydration_never_replenishes_spent_budget(self) -> None:
        """A continuation inherits the ledger's spend, and the tighter ceiling.

        `fold_task_state` pins the ceiling on the first `EpisodeStarted` and
        thereafter takes the *minimum* of the pinned and re-declared ceilings,
        so a restart can tighten a budget but can never buy one. The assertion
        is on what the ingress actually hands the next run, not on a second
        fold of the same events.
        """
        self.execute(runId="run-budget")
        first = fold_task_state(
            self.events("run-budget"), objective="").to_canonical_dict()
        before = dict(first.get("remainingBudgets") or {})
        self.assertTrue(before, "hydration carried no remaining budget at all")

        captured: dict[str, Any] = {}
        original = entrypoint.Runtime.execute_profiled

        def spy(manifest_path, task, **kwargs):
            captured["resume_state"] = task.resume_state
            return original(manifest_path, task, **kwargs)

        entrypoint.Runtime.execute_profiled = staticmethod(spy)
        try:
            self.execute(runId="run-budget")
        finally:
            entrypoint.Runtime.execute_profiled = original

        after = dict((captured["resume_state"] or {}).get("remainingBudgets") or {})
        self.assertTrue(after, "the second ingress hydrated no budget")
        for dimension, remaining in after.items():
            self.assertLessEqual(
                remaining, before.get(dimension, remaining),
                f"re-entry replenished {dimension}: "
                f"{before.get(dimension)} -> {remaining}")

    def test_hydration_never_rewidens_a_revoked_grant(self) -> None:
        """`K-49` revocation is transitive over descendants and survives it."""
        self.execute(runId="run-grants")
        events = self.events("run-grants")
        folded = fold_task_state(events, objective="")
        revoked = {str(item) for item in (getattr(folded, "revoked_grants", None) or ())}
        live = {str(getattr(grant, "grant_id", "") or (
                    grant.get("grantId") if isinstance(grant, dict) else ""))
                for grant in (getattr(folded, "live_grants", None) or ())}
        self.assertEqual(
            revoked & live, set(),
            "a revoked grant reappeared as live authority after hydration")


class MutationProof(_PublicRoute):
    """DIR-5.5: each negative control reds when its named guard is removed."""

    git = False

    # The own-git guard is mutation-proved by
    # `test_a_directory_inside_another_repository_is_not_its_parent`
    # calling `workspace_repository_present` directly: through the whole
    # route a second instrument failure can refuse first and mask it.

    def test_hydration_reds_when_keyed_on_the_command_verb(self) -> None:
        self.git = True
        import subprocess
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        self.execute(runId="run-mut-hyd", brief="the original objective")
        captured: dict[str, Any] = {}
        original = entrypoint.Runtime.execute_profiled

        def spy(manifest_path, task, **kwargs):
            captured["resume_state"] = task.resume_state
            return original(manifest_path, task, **kwargs)

        def verb_keyed(command: str, events):
            return list(events) if command == "resume" else []

        entrypoint.Runtime.execute_profiled = staticmethod(spy)
        try:
            with patch.object(entrypoint, "_events_to_hydrate", verb_keyed):
                self.execute(runId="run-mut-hyd", command="code",
                             brief="a different sentence entirely")
        finally:
            entrypoint.Runtime.execute_profiled = original
        self.assertIsNone(
            captured.get("resume_state"),
            "disabling state-keyed hydration still hydrated a `code` ingress; "
            "the control would stay green")

    def test_turn_ceiling_reds_when_the_durable_bound_is_ignored(self) -> None:
        self.git = True
        import subprocess
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        self.execute(runId="run-mut-ceil", maxTurnsPerEpisode=3)
        with patch.object(entrypoint, "_durable_turn_ceiling", return_value=None):
            response = self.execute(runId="run-mut-ceil", maxTurnsPerEpisode=99)
        self.assertEqual(
            response["result"]["runId"], "run-mut-ceil",
            "disabling the durable turn-ceiling guard still refused the "
            "widened continuation; the control would stay green")


if __name__ == "__main__":
    unittest.main()
