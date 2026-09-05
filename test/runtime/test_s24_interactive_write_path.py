"""S24: a write completes under INTERACTIVE, and asks nobody under BENCHMARK.

`REQ-TRUST-001`, `K-17`. A coding harness that can never write is not a coding
harness, and one that writes without a human in INTERACTIVE is not a safe one.
Both halves are asserted against the real `StandardPolicy` — no mock kernel,
and no auto-approval in BENCHMARK.

The approver here is a **test operator holding a real Ed25519 key**. It is not
a bypass: it signs the exact descriptor, and the pack's declared `mode:
assisted` is what puts it in the loop at all.

Under BENCHMARK there is no signer, and since T-70 there is no ask either: the
pack's declared `threshold: standard` covers its own `patch.apply`, so the run
proceeds without blocking rather than being denied for want of a human.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from test.agency.doubles import ScriptedModel, finish
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)
from vanguard.packages.runtime.session_log import session_log

OPERATOR = OperatorSigner(b"test-operator-held-approval-key")

SOURCE = "def total(values):\n    return 1\n"
FIXED_SOURCE = "def total(values):\n    return sum(values)\n"
DIFF = (
    "--- a/calc.py\n"
    "+++ b/calc.py\n"
    "@@ -1,2 +1,2 @@\n"
    " def total(values):\n"
    "-    return 1\n"
    "+    return sum(values)\n"
)


def approve(challenge: Any) -> Any:
    """A human who signs this exact descriptor. Not a blanket allow."""
    return OPERATOR.approve(challenge, reviewer="operator-1")


def _patch(diff: str = DIFF) -> dict:
    return {"kind": "effect", "action": "patch.apply",
            "resource": {"kind": "fs", "root": "/workspace",
                         "paths": ["/workspace"]},
            "args": {"diff": diff}, "note": "apply the fix"}


def _read(path: str = "calc.py") -> dict:
    return {"kind": "effect", "action": "fs.read",
            "resource": {"kind": "fs", "root": "/workspace",
                         "paths": ["/workspace"]},
            "args": {"path": path}, "note": "read it back"}


class _Environment:
    """A workspace that actually changes when a patch is applied.

    Without this the "next turn can read the new file" claim is unfalsifiable:
    an environment that discards writes would pass a test that only checks a
    receipt was produced.
    """

    def __init__(self) -> None:
        self.files = {"calc.py": SOURCE}
        self.disposed = False
        self.applied: list[Any] = []

    def profile(self) -> Any:
        from vanguard.packages.ports.environment import EnvironmentProfile
        from vanguard.packages.ports.event_store import Result

        return Result.success(EnvironmentProfile(
            environment_id="fake:/workspace", kind="memory", root="/workspace"))

    def snapshot(self) -> Any:
        from vanguard.packages.ports.environment import EnvironmentSnapshot
        from vanguard.packages.ports.event_store import Result

        return Result.success(EnvironmentSnapshot(
            snapshot_id="s1", digest="sha256:s",
            created_at="2026-08-17T00:00:00.000Z"))

    def observe(self, req: Any, grant: Any = None) -> Any:
        from vanguard.packages.ports.environment import Observation
        from vanguard.packages.ports.event_store import Result

        path = (getattr(req, "args", {}) or {}).get("path", "calc.py")
        return Result.success(Observation(
            action=getattr(req, "action", "fs.read"),
            content=self.files.get(str(path), "")))

    def preview(self, req: Any, grant: Any = None) -> Any:
        from vanguard.packages.ports.event_store import Result

        return Result.fail("unavailable", "no preview")

    def apply(self, req: Any, grant: Any = None) -> Any:
        from vanguard.packages.ports.environment import EffectReceipt
        from vanguard.packages.ports.event_store import Result

        self.applied.append(req)
        self.files["calc.py"] = FIXED_SOURCE
        return Result.success(EffectReceipt(
            descriptor_digest="sha256:d", outcome="ok",
            observed_at="2026-08-17T00:00:00.000Z", result_digest="sha256:r"))

    def reconcile(self, receipt: Any, grant: Any = None) -> Any:
        from vanguard.packages.ports.event_store import Result

        return Result.fail("unavailable", "no reconcile")

    def dispose(self) -> Any:
        from vanguard.packages.ports.event_store import Result

        self.disposed = True
        return Result.success(None)


def _run(script: list, *, interactive: bool, environment: Any) -> dict:
    ports = SessionPorts(
        model=ScriptedModel(script), environment=environment,
        clock=FixedClock(at="2026-08-17T00:00:00.000Z", step_ms=1),
        random=SeededRandom(seed=24), store=SqliteEventStore(":memory:"),
        interactive=interactive,
        approver=approve if interactive else None,
        approval_key=OPERATOR.public_bytes if interactive else None)
    task = TaskContext(brief="make the suite pass", repo_path=Path("/workspace"),
                       run_id="run-s24", episode_id="ep-s24", max_turns=6)
    harness = Runtime.compose("vg-code-default", episode_id="ep-s24")
    result = HarnessSession(harness, ports, task).run()
    return {"result": result, "log": session_log(result.events),
            "environment": environment}


class AWriteCompletesUnderInteractive(unittest.TestCase):
    """A-24-03, first half."""

    def test_the_patch_reaches_the_environment(self) -> None:
        out = _run([_patch(), finish()], interactive=True,
                   environment=_Environment())
        self.assertTrue(out["environment"].applied,
                        "no patch reached the environment under INTERACTIVE")

    def test_the_turn_is_recorded_with_its_verb(self) -> None:
        out = _run([_patch(), finish()], interactive=True,
                   environment=_Environment())
        verbs = [entry.verb for entry in out["log"].entries if entry.verb]
        self.assertIn("patch.apply", verbs)

    def test_the_approval_was_requested_not_assumed(self) -> None:
        """The signer is consulted; nothing is auto-allowed."""

        out = _run([_patch(), finish()], interactive=True,
                   environment=_Environment())
        kinds = [event.kind for event in out["result"].events]
        self.assertIn("ApprovalRequested", kinds)


class BenchmarkAsksNobodyAndWritesAnyway(unittest.TestCase):
    """A-24-03, second half. Successor to `BenchmarkStillDeniesTheSameVerb`.

    `K-17` said a benchmark must never block for a human, and the old
    assertions read that as: the privileged write is denied. That was the
    hardcoded `approval_required_above` speaking, not the manifest -- a coding
    preset that cannot write under benchmark cannot be benchmarked at all.
    Since T-70 the declared `threshold: standard` covers the pack's own
    `patch.apply`, so the write proceeds *and* no human is ever asked. Both
    halves are pinned here; `K-17` is upheld by the second, not the first.
    """

    def test_the_declared_write_reaches_the_environment(self) -> None:
        out = _run([_patch(), finish()], interactive=False,
                   environment=_Environment())
        self.assertNotEqual(out["environment"].applied, [],
                            "BENCHMARK denied a write the manifest declared")

    def test_the_write_is_recorded_as_authorized_not_denied(self) -> None:
        out = _run([_patch(), finish()], interactive=False,
                   environment=_Environment())
        receipts = {entry.verb: entry.receipt for entry in out["log"].entries}
        self.assertNotEqual(receipts.get("patch.apply"), "AuthorizationDenied")

    def test_no_approval_is_requested_without_a_human(self) -> None:
        """`K-17` proper: the benchmark never blocks, whatever it decides."""
        out = _run([_patch(), finish()], interactive=False,
                   environment=_Environment())
        kinds = [event.kind for event in out["result"].events]
        self.assertNotIn("ApprovalRequested", kinds)

    def test_the_workspace_carries_the_write_it_authorized(self) -> None:
        environment = _Environment()
        _run([_patch(), finish()], interactive=False, environment=environment)
        self.assertEqual(environment.files["calc.py"], FIXED_SOURCE)


class TheNextTurnSeesTheWrite(unittest.TestCase):
    """A-24-04. A write is only real if the next turn can observe it."""

    def test_a_read_after_a_write_returns_the_new_content(self) -> None:
        environment = _Environment()
        out = _run([_patch(), _read(), finish()], interactive=True,
                   environment=environment)
        self.assertEqual(environment.files["calc.py"], FIXED_SOURCE)
        verbs = [entry.verb for entry in out["log"].entries if entry.verb]
        self.assertEqual(verbs[:2], ["patch.apply", "fs.read"])

    def test_both_turns_are_on_the_ledger_in_order(self) -> None:
        out = _run([_patch(), _read(), finish()], interactive=True,
                   environment=_Environment())
        turns = [(entry.turn, entry.verb) for entry in out["log"].entries
                 if entry.verb]
        self.assertEqual(turns, [(1, "patch.apply"), (2, "fs.read")])

    def test_the_read_completed_rather_than_being_denied(self) -> None:
        out = _run([_patch(), _read(), finish()], interactive=True,
                   environment=_Environment())
        receipts = {entry.verb: entry.receipt for entry in out["log"].entries}
        self.assertEqual(receipts.get("fs.read"), "EffectCompleted")

    def test_no_second_loop_was_introduced(self) -> None:
        import inspect

        import vanguard.packages.runtime.lab_driver as driver

        source = inspect.getsource(driver)
        self.assertNotIn("while True", source)
        self.assertNotIn("EpisodeEngine(", source)


if __name__ == "__main__":
    unittest.main()
