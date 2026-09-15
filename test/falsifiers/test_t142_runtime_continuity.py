"""T-142: bounded long-session continuity, qualified on the real runtime.

`RUN-10` requires "compaction preserving objective, constraints, unresolved
failures, plan state, changed-file identity and the resource ledger; fresh-
process resume that neither duplicates effects nor resets ceilings." T-131.7
qualified the durable fold that produces that state. This module qualifies
what happens to it when a session runs long enough for the context compiler to
start reclaiming room.

The subject is the EXISTING compiler, composed exactly as `HarnessSession`
composes it -- `system_core`, `tool_schemas` and `skill_cards` from a real
installed manifest, `token_ceiling` from that pack's declared
`contextWindowTokens` (`session.py`, the `ContextCompiler(...)` call). There is
no second compiler here and no second task-state authority: sigma is whatever
`fold_task_state` produced from a real product run's WAL.

`RUN-12`: no provider is contacted, nothing is paid for. The model is a
scripted double, the store is a local disposable WAL, and the only processes
spawned are the sandbox's own allowlisted ones.

T-131.7 closes the two ingress gaps that initially limited this packet.  The
public resume entrypoint folds the durable run before composing the next
session, and recovery appends its adjudication at the durable project tip while
retaining the interrupted effect as causation.  The fresh-interpreter product
route is exercised in T-131.7 row 7; the controls below keep the T-142 runtime
side of that boundary explicit, including a non-tail open intent.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping, Sequence

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.agency.context import compaction as compaction_module
from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Fragment, PINNED_L4_SOURCES
from vanguard.packages.ports.event_store import EventRange, Result
from vanguard.packages.runtime import entrypoint
from vanguard.packages.runtime.root import Runtime
from vanguard.packages.runtime.task_state import fold_task_state

ROOT = Path(__file__).resolve().parents[2]
OBJECTIVE = "T142 OBJECTIVE: make app.f return 1 without touching the oracle"

#: Settled writes the fixture session accumulates. Enough that the folded
#: task state is larger than the dialogue the compiler can reclaim, which
#: is the condition under which the compaction floor is actually tested.
LONG_SESSION_WRITES = 15

#: The smallest context window `HarnessSession` will compose -- it floors
#: the pack's declared `contextWindowTokens` at this value (`session.py`).
#: Pressure tests run here because it is the tightest real configuration.
SESSION_WINDOW_FLOOR = 4096


class ScriptedModel:
    """A `ModelPort` double serving recorded proposals in tape order."""

    def __init__(self, tape: Sequence[Mapping[str, Any]]) -> None:
        self._tape = list(tape)
        self._cursor = 0
        self.contexts: list[Mapping[str, Any]] = []

    def propose(self, context: Mapping[str, Any], tools: Any, sampling: Any) -> Any:
        self.contexts.append(context)
        if self._cursor >= len(self._tape):
            return Result.success({"kind": "abstain", "note": "tape exhausted"})
        item = self._tape[self._cursor]
        self._cursor += 1
        return Result.success(dict(item))


def _effect(action: str, args: Mapping[str, Any], resource: Mapping[str, Any],
            note: str) -> dict[str, Any]:
    return {"kind": "effect", "action": action, "resource": dict(resource),
            "args": dict(args), "note": note}


_FS = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
_PROC = {"kind": "generic", "uriPattern": "proc://exec/allow/git,pytest,ruff,python3"}
_TASK = {"kind": "generic", "uriPattern": "task://revise/*"}


def _make_workspace(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text("[project]\nname='t142'\n", encoding="utf-8")
    (root / "app.py").write_text("def f():\n    pass\n", encoding="utf-8")
    for command in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"],
                    ["git", "config", "user.name", "t"], ["git", "add", "-A"],
                    ["git", "commit", "-qm", "init"]):
        subprocess.run(command, cwd=root, check=True, capture_output=True)
    (root / ".vanguard").mkdir(exist_ok=True)


class _RealRun:
    """One real product run through `entrypoint.execute`, compiled once.

    The tape is chosen so the WAL ends up carrying every kind of durable
    obligation a continuation has to preserve: one effect that never settles
    (unresolved work), two that do (settled identity), the grants and leases
    they consumed (authority and resources), and a change surface.
    """

    run_id = "run-t142-continuity"

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "workspace"
        self.store = self.root / ".vanguard" / "events.sqlite3"
        _make_workspace(self.root)
        os.environ["AETHER_WORKSPACE_ROOT"] = str(self.root)
        model = ScriptedModel([
            # `task.revise` is dispatched but does not settle on this route, so
            # the WAL keeps a genuinely open intent -- real unresolved work,
            # not an injected one.
            _effect("task.revise", {
                "plan": ["read the failure", "patch app.py", "verify"],
                "backlog": ["verify app.py", "re-run the suite"],
                "next_action": "patch.apply",
                "mutated_fields": ["plan", "backlog", "next_action"],
                "rationale": "T142 unresolved work",
            }, _TASK, "revise"),
            _effect("patch.apply", {"path": "app.py", "content": "def f():\n    return 1\n"},
                    _FS, "implement"),
            # A long session, not a two-turn one. Each settled write adds a
            # descriptor and a surface path, so sigma grows monotonically --
            # which is the whole reason long-session compaction is a distinct
            # problem from ordinary compaction.
            *[_effect("patch.apply",
                      {"path": f"mod_{i}.py", "content": f"VALUE_{i} = {i}\n"},
                      _FS, f"extend {i}")
              for i in range(LONG_SESSION_WRITES)],
            _effect("proc.exec", {"argv": ["python3", "-c", "print('ok')"]}, _PROC, "verify"),
            {"kind": "abstain", "note": "pause the session here"},
        ])
        self.frame = entrypoint.execute({
            "command": "code", "brief": OBJECTIVE, "workspace": str(self.root),
            "storePath": str(self.store), "injectedModel": model,
            "profile": "product", "interactive": False,
            "maxTurnsPerEpisode": 20, "runId": self.run_id,
        })

    def close(self) -> None:
        self._tmp.cleanup()

    def events(self) -> list[Any]:
        store = SqliteEventStore(str(self.store))
        try:
            return list(store.read(EventRange(run_id=self.run_id)).value or ())
        finally:
            store.close()

    def sigma(self) -> dict[str, Any]:
        return fold_task_state(self.events(), objective="").to_canonical_dict()


_RUN: _RealRun | None = None


def setUpModule() -> None:  # noqa: N802 - unittest protocol
    global _RUN
    _RUN = _RealRun()


def tearDownModule() -> None:  # noqa: N802 - unittest protocol
    if _RUN is not None:
        _RUN.close()


class RealRunCase(unittest.TestCase):
    """Shared access to the single real run, plus the real composed compiler."""

    maxDiff = None

    @property
    def real_run(self) -> _RealRun:
        assert _RUN is not None
        return _RUN

    def sigma(self) -> dict[str, Any]:
        return self.real_run.sigma()

    @staticmethod
    def compiler(*, ceiling: int | None = None) -> tuple[ContextCompiler, int]:
        """The compiler as `HarnessSession` composes it, from a real manifest."""
        harness = Runtime.compose("vg-code-balanced", episode_id="ep-t142")
        declared = max(
            harness.budget.get("context_window_tokens")
            or harness.budget.get("tokens", 0) or 64_000,
            4_096,
        )
        return ContextCompiler(
            system_core=harness.system_core,
            tool_schemas=harness.tool_schemas,
            environment="harness=vg-code-balanced environment=workspace",
            skill_cards=harness.skill_cards,
            token_ceiling=ceiling or declared,
        ), (ceiling or declared)

    @staticmethod
    def sigma_note(sigma: Mapping[str, Any]) -> Fragment:
        """Exactly the L4 note `PromptAssembler.assemble` builds for sigma."""
        return Fragment(
            source="task-state", label="sigma",
            text=json.dumps(sigma, sort_keys=True, default=str),
            evictable=False,
        )

    @staticmethod
    def observations(count: int, *, size: int = 900) -> tuple[Fragment, ...]:
        return tuple(
            Fragment(source="observation", label=f"obs-{i}",
                     text=f"observation {i}\n" + "X " * size, evictable=True)
            for i in range(count)
        )

    @staticmethod
    def compiled_sigma(compiled: Any) -> dict[str, Any] | None:
        for block in compiled.blocks:
            if block.label == "sigma":
                return json.loads(block.text)
        return None


class TheFixtureIsARealProductRun(RealRunCase):
    """The premise. Every assertion below is vacuous if this is not true."""

    def test_the_run_went_through_the_product_ingress(self) -> None:
        self.assertEqual(self.real_run.frame["type"], "result")
        self.assertEqual(self.real_run.frame["result"]["runId"], _RealRun.run_id)
        self.assertGreaterEqual(self.real_run.frame["result"]["turns"], 3)

    def test_the_wal_carries_real_settled_and_unresolved_work(self) -> None:
        sigma = self.sigma()
        continuity = sigma["recoveryState"]["continuity"]
        self.assertGreaterEqual(
            len(sigma["settledEffects"]), LONG_SESSION_WRITES,
            "the fixture session is not long enough to pressure the compiler")
        self.assertTrue(continuity["pendingEffects"], "no unresolved work")
        self.assertTrue(continuity["liveGrants"], "no grant identity")
        self.assertTrue(continuity["consumedBudgets"], "nothing was charged")
        self.assertEqual(sigma["objective"], OBJECTIVE)


class RepeatedCompactionPreservesObligations(RealRunCase):
    """T-142's central property, on the real compiler at the real ceiling."""

    def _obligations(self, sigma: Mapping[str, Any]) -> dict[str, Any]:
        continuity = sigma["recoveryState"]["continuity"]
        return {
            "objective": sigma["objective"],
            "settled": set(sigma["settledEffects"]),
            "pending": {entry["descriptorDigest"] for entry in continuity["pendingEffects"]},
            "grants": {grant["grantId"] for grant in continuity["liveGrants"]},
            "consumed": dict(continuity["consumedBudgets"]),
            "ceiling": dict(continuity["budgetCeiling"]),
        }

    def _compactions(self) -> list[tuple[int, Any]]:
        """Successive compilations under growing pressure. Real compactions only."""
        compiler, _ = self.compiler(ceiling=SESSION_WINDOW_FLOOR)
        note = self.sigma_note(self.sigma())
        observed: list[tuple[int, Any]] = []
        for count in (8, 20, 40, 80):
            compiled = compiler.compile(
                brief=OBJECTIVE, notes=(note,), dialogue=self.observations(count))
            if compiled.dropped or compiled.elided:
                observed.append((count, compiled))
        return observed

    def test_at_least_two_actual_compactions_are_observed(self) -> None:
        """A property proved under no pressure is not proved."""
        observed = self._compactions()
        self.assertGreaterEqual(
            len(observed), 2,
            "fewer than two real compactions; the pressure fixture is not loaded")

    def test_every_obligation_survives_every_compaction(self) -> None:
        expected = self._obligations(self.sigma())
        for count, compiled in self._compactions():
            with self.subTest(dialogue=count):
                surviving = self.compiled_sigma(compiled)
                self.assertIsNotNone(
                    surviving, "compaction dropped the durable task state entirely")
                observed = self._obligations(surviving)

                self.assertEqual(observed["objective"], expected["objective"])
                self.assertEqual(observed["pending"], expected["pending"],
                                 "compaction lost unresolved work")
                self.assertEqual(observed["grants"], expected["grants"],
                                 "compaction lost grant identity")
                self.assertEqual(observed["consumed"], expected["consumed"],
                                 "compaction lost aggregate consumption")
                self.assertEqual(observed["ceiling"], expected["ceiling"],
                                 "compaction lost the resource ceiling")

    def test_anything_compaction_did_bound_away_is_stated_in_place(self) -> None:
        """A bounded list that did not say so reads as a complete one."""
        for count, compiled in self._compactions():
            with self.subTest(dialogue=count):
                surviving = self.compiled_sigma(compiled) or {}
                omitted = surviving.get("boundedByCompaction")
                if omitted is None:
                    continue  # nothing of sigma was bounded at this rung
                self.assertIsInstance(omitted, dict)
                for key, amount in omitted.items():
                    self.assertIsInstance(amount, int)
                    self.assertGreater(amount, 0)
                    self.assertIn(key, surviving,
                                  f"{key} was counted as bounded but is absent entirely")

    def test_the_compaction_floor_is_load_bearing(self) -> None:
        """ADVERSARIAL: restore the pre-T-142 drop policy and the obligations go.

        Before T-142 `_drop_flexible_notes` exempted only `PINNED_L4_SOURCES`,
        so the durable task-state note was an ordinary droppable L4 note. This
        reinstates exactly that set and requires the loss to reappear -- if it
        does not, the repair above is not what is keeping sigma in the prompt
        and this module is measuring nothing.
        """
        compiler, _ = self.compiler(ceiling=SESSION_WINDOW_FLOOR)
        note = self.sigma_note(self.sigma())
        original = compaction_module._MANDATORY_L4_SOURCES
        try:
            compaction_module._MANDATORY_L4_SOURCES = PINNED_L4_SOURCES
            compiled = compiler.compile(
                brief=OBJECTIVE, notes=(note,), dialogue=self.observations(80))
        finally:
            compaction_module._MANDATORY_L4_SOURCES = original

        self.assertIn("sigma", compiled.dropped,
                      "the old policy no longer drops sigma; the control is vacuous")
        self.assertIsNone(self.compiled_sigma(compiled))

    def test_the_repaired_policy_keeps_sigma_under_the_same_pressure(self) -> None:
        compiler, _ = self.compiler(ceiling=SESSION_WINDOW_FLOOR)
        compiled = compiler.compile(
            brief=OBJECTIVE, notes=(self.sigma_note(self.sigma()),),
            dialogue=self.observations(80))
        self.assertNotIn("sigma", compiled.dropped)
        self.assertIsNotNone(self.compiled_sigma(compiled))


class RestartCannotWidenGrantsOrReplenishConsumption(RealRunCase):
    """T-142: a restart is a continuation, not a fresh allocation."""

    def _event(self, kind: str, payload: Mapping[str, Any]) -> Any:
        from vanguard.packages.kernel.model import Event

        return Event(kind=kind, reason="t142", at="2026-09-15T00:00:00.000Z",
                     run_id=_RealRun.run_id, principal="agent-1",
                     payload={"kind": kind, **payload})

    def test_a_restart_that_re_declares_a_larger_ceiling_does_not_widen_it(self) -> None:
        sigma = self.sigma()
        ceiling = sigma["recoveryState"]["continuity"]["budgetCeiling"]
        restarted = self.real_run.events() + [self._event("EpisodeStarted", {
            "episodeId": f"episode-{_RealRun.run_id}",
            "budgetCeiling": {k: v * 100 for k, v in ceiling.items()},
        })]
        after = fold_task_state(restarted, objective="").to_canonical_dict()
        for dimension, amount in sigma["remainingBudgets"].items():
            with self.subTest(dimension=dimension):
                self.assertLessEqual(after["remainingBudgets"][dimension], amount)

    def test_a_restart_cannot_replenish_what_was_consumed(self) -> None:
        sigma = self.sigma()
        consumed = sigma["recoveryState"]["continuity"]["consumedBudgets"]
        self.assertTrue(consumed)
        restarted = self.real_run.events() + [self._event("EpisodeStarted", {
            "episodeId": f"episode-{_RealRun.run_id}",
            "budgetCeiling": sigma["recoveryState"]["continuity"]["budgetCeiling"],
        })]
        after = fold_task_state(restarted, objective="").to_canonical_dict()
        for dimension, spent in consumed.items():
            with self.subTest(dimension=dimension):
                self.assertEqual(after["remainingBudgets"][dimension],
                                 sigma["remainingBudgets"][dimension])
                self.assertEqual(
                    after["remainingBudgets"][dimension],
                    max(sigma["recoveryState"]["continuity"]["budgetCeiling"][dimension]
                        - spent, 0))

    def test_revocation_denies_the_grant_a_restart_would_otherwise_restore(self) -> None:
        sigma = self.sigma()
        grant_id = sigma["recoveryState"]["continuity"]["liveGrants"][0]["grantId"]
        revoked = self.real_run.events() + [
            self._event("CapabilityRevoked", {"grantId": grant_id}),
            self._event("EpisodeStarted", {
                "episodeId": f"episode-{_RealRun.run_id}",
                "budgetCeiling": sigma["recoveryState"]["continuity"]["budgetCeiling"],
            }),
        ]
        after = fold_task_state(revoked, objective="").to_canonical_dict()
        continuity = after["recoveryState"]["continuity"]
        self.assertNotIn(grant_id, {g["grantId"] for g in continuity["liveGrants"]})
        self.assertIn(grant_id, continuity["revokedGrants"])

    def test_revocation_survives_compaction(self) -> None:
        """Authority a restart may not restore must also survive pressure."""
        sigma = self.sigma()
        grant_id = sigma["recoveryState"]["continuity"]["liveGrants"][0]["grantId"]
        revoked = fold_task_state(
            self.real_run.events() + [self._event("CapabilityRevoked", {"grantId": grant_id})],
            objective="").to_canonical_dict()
        compiler, _ = self.compiler(ceiling=SESSION_WINDOW_FLOOR)
        compiled = compiler.compile(
            brief=OBJECTIVE, notes=(self.sigma_note(revoked),),
            dialogue=self.observations(80))
        surviving = self.compiled_sigma(compiled) or {}
        continuity = surviving.get("recoveryState", {}).get("continuity", {})
        self.assertIn(grant_id, continuity.get("revokedGrants", []))
        self.assertNotIn(grant_id,
                         {g["grantId"] for g in continuity.get("liveGrants", [])})


class SettledEffectsNeverReplay(RealRunCase):
    """T-142: a settled effect is settled for the rest of the run's life."""

    def test_settled_identity_is_not_reopened_by_a_repeated_intent(self) -> None:
        from vanguard.packages.kernel.model import Event

        sigma = self.sigma()
        settled = sigma["settledEffects"][0]
        replayed = self.real_run.events() + [Event(
            kind="EffectStarted", reason="t142", at="2026-09-15T00:00:00.000Z",
            run_id=_RealRun.run_id, principal="agent-1",
            payload={"kind": "EffectStarted", "action": "patch.apply",
                     "descriptorDigest": settled})]
        after = fold_task_state(replayed, objective="").to_canonical_dict()
        pending = {entry["descriptorDigest"]
                   for entry in after["recoveryState"]["continuity"]["pendingEffects"]}
        self.assertIn(settled, after["settledEffects"])
        self.assertNotIn(settled, pending)

    def test_settled_identity_survives_compaction(self) -> None:
        compiler, _ = self.compiler(ceiling=SESSION_WINDOW_FLOOR)
        expected = set(self.sigma()["settledEffects"])
        compiled = compiler.compile(
            brief=OBJECTIVE, notes=(self.sigma_note(self.sigma()),),
            dialogue=self.observations(80))
        surviving = self.compiled_sigma(compiled) or {}
        # A settled effect may be bounded out of the list only if the omission
        # is stated; silently shortening it invites the planner to redo one.
        omitted = (surviving.get("boundedByCompaction") or {}).get("settledEffects", 0)
        self.assertEqual(len(surviving.get("settledEffects", [])) + omitted, len(expected))


class ExhaustionDeniesTheNextDispatch(unittest.TestCase):
    """T-142: exhaustion denies the next action, and denies it safely."""

    def test_an_exhausted_run_stops_instead_of_dispatching_again(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "workspace"
        _make_workspace(root)
        os.environ["AETHER_WORKSPACE_ROOT"] = str(root)
        store = root / ".vanguard" / "events.sqlite3"
        # The `fast` pack declares eight turns. The tape offers more work than
        # that, so the run must stop on its own bound rather than take it.
        reads = [_effect("fs.read", {"path": "app.py"}, _FS, f"read {i}")
                 for i in range(20)]
        model = ScriptedModel(reads)
        frame = entrypoint.execute({
            "command": "code", "brief": OBJECTIVE, "workspace": str(root),
            "storePath": str(store), "injectedModel": model, "preset": "fast",
            "profile": "product", "interactive": False, "runId": "run-t142-exhaust",
        })

        self.assertNotEqual(frame["result"]["outcome"], "completed",
                            "an exhausted run reported completion")
        self.assertLessEqual(frame["result"]["turns"], 8,
                             "the declared turn bound was exceeded")
        self.assertLess(len(model.contexts), len(reads),
                        "every scripted turn was taken; nothing was denied")

        events = SqliteEventStore(str(store)).read(
            EventRange(run_id="run-t142-exhaust")).value or ()
        kinds = [(getattr(e, "payload", {}) or {}).get("kind") for e in events]
        # Safe denial: the run stops between turns, never mid-effect.
        started = kinds.count("EffectStarted")
        terminal = sum(kinds.count(k) for k in
                       ("EffectCompleted", "EffectFailed", "EffectRejected",
                        "EffectReconciled"))
        self.assertEqual(started, terminal,
                         "exhaustion left an effect open instead of denying the next one")


class FreshProcessIngressAndRecoveryAreBound(unittest.TestCase):
    """The resume seam preserves identity and reconciles without rewinding.

    The process-boundary positive control is T-131.7 row 7's public
    ``entrypoint.execute('resume')`` run.  This packet additionally proves the
    ingress binding and the recovery append rule at the exact two seams that
    formerly prevented that route from continuing.
    """

    def test_the_ingress_binds_durable_resume_state_to_task_context(self) -> None:
        import inspect

        source = inspect.getsource(entrypoint.execute)
        construction = source.split("task = TaskContext(", 1)[1].split(")", 1)[0]
        self.assertIn("resume_state=resume_state", construction)
        self.assertIn("fold_task_state(events", source)

    def test_non_tail_open_intent_reconciles_at_the_current_chain_tip(self) -> None:
        from vanguard.packages.kernel.model import Event
        from vanguard.packages.runtime.ledger.recovery import RecoveryScanner
        from vanguard.packages.runtime.ledger_emitter import LedgerEmitter

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = SqliteEventStore(str(Path(tmp.name) / "events.sqlite3"))
        self.addCleanup(store.close)
        emitter = LedgerEmitter(
            store, episode_id="ep-t142-recovery", project_id="project-t142-recovery",
            principal_id="agent-t142", harness_digest="sha256:" + "a" * 64,
            role="session",
        )
        emitter.emit(Event(
            kind="EpisodeStarted", reason="test", at="2026-09-15T00:00:00.000Z",
            run_id="run-t142-recovery", principal="agent-t142",
            payload={"kind": "EpisodeStarted"},
        ))
        emitter.append_intent(Event(
            kind="EffectStarted", reason="test", at="2026-09-15T00:00:01.000Z",
            run_id="run-t142-recovery", principal="agent-t142",
            payload={"kind": "EffectStarted", "idempotencyKey": "open-t142",
                     "descriptorDigest": "sha256:" + "b" * 64},
        ))
        tail = emitter.emit(Event(
            kind="Heartbeat", reason="test", at="2026-09-15T00:00:02.000Z",
            run_id="run-t142-recovery", principal="agent-t142",
            payload={"kind": "Heartbeat"},
        ))
        before = list(store.read(EventRange(project_id="project-t142-recovery")).value or ())
        intent = next(event for event in before if event.payload.get("kind") == "EffectStarted")

        reconciled = RecoveryScanner(controller_principal="agent-t142-recovery").reconcile_open_intents(
            store, occurred_at="2026-09-15T00:00:03.000Z", project_id="project-t142-recovery")
        self.assertEqual(len(reconciled), 1)
        self.assertEqual(reconciled[0].causation_id, intent.event_id)
        self.assertGreater(int(reconciled[0].seq), int(tail.seq))
        self.assertEqual(reconciled[0].payload["status"], "undeterminable")
        second = RecoveryScanner(controller_principal="agent-t142-recovery").reconcile_open_intents(
            store, occurred_at="2026-09-15T00:00:04.000Z", project_id="project-t142-recovery")
        self.assertEqual(second, [])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
