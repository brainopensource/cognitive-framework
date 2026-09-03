"""W3 falsifier: plan mode's read-only profile is enforced by grant attenuation,
not client-side politeness (`FRONTEND_TUI_DEVELOPMENT.md` W3).

`_scope_for(harness, workspace_access="read-only")` withholds `patch.apply` and
`proc.exec` from the granted `Scope.actions` at composition. `HarnessSession`
binds its adapter table only for held verbs (`session.py`, right after
`self.scope` is resolved), so a withheld verb has no adapter at all: a write
attempt is rejected at kernel dispatch stage S2 RESOLVE with `UNKNOWN_ACTION`
("no adapter for 'patch.apply'") before any lease, grant, or effect is
possible -- the session is never issued the authority, not merely asked not to
use it. (`Scope.actions` alone does not gate a top-level/unsealed session's own
dispatch -- `kernel/policy.py`'s S5 scope-escalation check compares a session's
own scope against itself and is a no-op there; it only bites a *sealed* child
scope, e.g. a delegated sub-agent. The adapter table is the real seam for an
unsealed session's own capability ceiling.)

The denial is recorded in the ledger as `EffectRejected`, and the fake
workspace is never touched. A second test proves the same profile still grants
`fs.read`, so "read-only" is distinguishable from "broken".
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

from test.agency.doubles import ScriptedModel, effect, finish
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.environment import (
    EffectReceipt,
    EnvironmentProfile,
    EnvironmentSnapshot,
    Observation,
)
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.profiles import PRESETS
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext
from vanguard.packages.runtime.wiring import _scope_for


class FakeClock:
    def now(self) -> str:
        return "2026-09-03T00:00:00.000Z"

    def now_ms(self) -> int:
        return 1_756_857_600_000


class FakeEnvironment:
    """Touches no real filesystem; `applied` records every effect that reached it."""

    def __init__(self) -> None:
        self.applied: list[Any] = []
        self.disposed = False

    def profile(self) -> Result[Any]:
        return Result.success(EnvironmentProfile(
            environment_id="fake:/workspace", kind="memory", root="/workspace"))

    def snapshot(self) -> Result[Any]:
        return Result.success(EnvironmentSnapshot(
            snapshot_id="snap-1", digest="sha256:snap",
            created_at="2026-09-03T00:00:00.000Z"))

    def observe(self, req: Any, grant: Any = None) -> Result[Any]:
        return Result.success(Observation(
            action=getattr(req, "action", "fs.read"),
            content="def total(values): pass"))

    def preview(self, req: Any, grant: Any = None) -> Result[Any]:
        return Result.fail("unavailable", "fake environment previews nothing")

    def apply(self, req: Any, grant: Any = None) -> Result[Any]:
        self.applied.append(req)
        return Result.success(EffectReceipt(
            descriptor_digest="sha256:descriptor", outcome="ok",
            observed_at="2026-09-03T00:00:00.000Z", result_digest="sha256:applied"))

    def reconcile(self, receipt: Any, grant: Any = None) -> Result[Any]:
        return Result.fail("unavailable", "fake environment reconciles nothing")

    def dispose(self) -> Result[None]:
        self.disposed = True
        return Result.success(None)


def _task() -> TaskContext:
    return TaskContext(
        brief="attempt a write under plan mode",
        repo_path=Path("/workspace"),
        run_id="run-plan-mode-1",
        episode_id="ep-plan-mode-1",
        principal="agent-1",
        max_turns=4,
    )


class PlanModeProfile(unittest.TestCase):
    def test_plan_preset_is_read_only_workspace_write_by_default(self) -> None:
        self.assertEqual(PRESETS["plan"].workspace_access, "read-only")
        self.assertEqual(PRESETS["local"].workspace_access, "workspace-write")

    def test_scope_for_withholds_patch_apply_and_proc_exec_under_read_only(self) -> None:
        harness = Runtime.compose("vg-code-max", episode_id="ep-scope-1")
        write_scope = _scope_for(harness, workspace_access="workspace-write")
        plan_scope = _scope_for(harness, workspace_access="read-only")

        self.assertIn("patch.apply", write_scope.actions)
        self.assertIn("proc.exec", write_scope.actions)

        self.assertNotIn("patch.apply", plan_scope.actions)
        self.assertNotIn("proc.exec", plan_scope.actions)
        self.assertIn("fs.read", plan_scope.actions)
        self.assertIn("fs.search", plan_scope.actions)
        # Attenuation only ever subtracts: every retained verb from the
        # write scope stays retained under plan mode, and nothing is added.
        withheld = {"patch.apply", "proc.exec"}
        self.assertEqual(plan_scope.actions, write_scope.actions - withheld)


class PlanModeDenialFalsifier(unittest.TestCase):
    """The Definition-of-Ready falsifier from W3 step 5."""

    def setUp(self) -> None:
        self.harness = Runtime.compose("vg-code-max", episode_id="ep-plan-mode-1")

    def _ports(self, model: Any, environment: Any, store: SqliteEventStore) -> SessionPorts:
        return SessionPorts(
            model=model,
            environment=environment,
            clock=FakeClock(),
            store=store,
            # Real interactive mode, not BENCHMARK (`interactive=False` denies
            # reads too and means something else -- W3 is explicit about this).
            interactive=True,
            workspace_access="read-only",
        )

    def test_patch_apply_is_denied_with_no_adapter_and_workspace_untouched(self) -> None:
        environment = FakeEnvironment()
        store = SqliteEventStore(":memory:")
        model = ScriptedModel([
            effect(action="patch.apply", path="/workspace/src/a.ts"),
            finish(),
        ])

        session = HarnessSession(self.harness, self._ports(model, environment, store), _task())
        # The attenuation happened at composition, before any request: the
        # session's own adapter table (what `Kernel` is built from) simply
        # has no entry for a withheld verb.
        self.assertNotIn("patch.apply", session.adapters)
        self.assertNotIn("proc.exec", session.adapters)

        session.run()

        events = tuple(store.read().value or ())
        rejections = [e for e in events if e.payload.get("kind") == "EffectRejected"]
        self.assertTrue(rejections, "expected an EffectRejected event in the ledger")
        self.assertTrue(
            any(e.payload.get("reason") == "unknown_action" for e in rejections),
            f"expected an unknown_action reason (no adapter bound for a withheld verb), "
            f"got: {[e.payload.get('reason') for e in rejections]}",
        )

        # The workspace is byte-identical afterward: the fake environment's
        # apply() -- the only path that could have mutated it -- was never called.
        self.assertEqual(environment.applied, [])

    def test_fs_read_still_succeeds_under_the_same_read_only_profile(self) -> None:
        """Read-only must be distinguishable from broken."""
        environment = FakeEnvironment()
        store = SqliteEventStore(":memory:")
        model = ScriptedModel([
            effect(action="fs.read", path="/workspace/src/a.ts"),
            finish(),
        ])

        session = HarnessSession(self.harness, self._ports(model, environment, store), _task())
        result = session.run()

        events = tuple(store.read().value or ())
        self.assertFalse(
            any(e.payload.get("kind") == "EffectRejected" for e in events),
            "fs.read must not be denied under plan mode",
        )
        self.assertTrue(any(
            e.payload.get("kind") == "EffectCompleted" and e.payload.get("action") == "fs.read"
            for e in events
        ))
        self.assertIsNotNone(result.terminal)


if __name__ == "__main__":
    unittest.main()
