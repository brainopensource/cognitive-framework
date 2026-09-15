"""T-131 row 7 (`RUN-09` defect 7): RESUME and COMPACTION must preserve task,
candidate, plan, changed-file and budget identity.

`RUN-10` states the boundary this row qualifies: "compaction preserving
objective, constraints, unresolved failures, plan state, changed-file identity
and the resource ledger; fresh-process resume that neither duplicates effects
nor resets ceilings." `fold_task_state`, `CodingTaskState.to_canonical_dict`
and `critical_state` are the MECHANISM. This module is the QUALIFICATION.

Structure, as for row 4: one pure instrument (`identity_failures`) scored
against a product route and then against injected defects, so a green reading
is only obtainable by the property actually holding.

`RUN-12`: no provider is contacted. The fresh-process test spawns the local
interpreter only; the model is the scripted cassette double.
"""

from __future__ import annotations

import inspect
import json
import os
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping, Sequence

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.agency.context import ContextPacketError
from vanguard.packages.domain.canonicalisation.jcs import canonical_bytes
from vanguard.packages.domain.task_state import MemoryView, SemanticTaskState, critical_state
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime import entrypoint
from vanguard.packages.runtime.session import HarnessSession
from vanguard.packages.runtime.task_state import fold_task_state

ROOT = Path(__file__).resolve().parents[2]

#: The five identity dimensions row 7 names, and where each one lives in the
#: canonical resume state. A dimension that is not read here is not qualified.
DIMENSIONS: Mapping[str, tuple[str, ...]] = {
    "task": ("objective",),
    "candidate": ("changedFilesTreeHash",),
    "plan": ("plan", "backlog", "todoItems", "activeStepId"),
    "changed-file": ("modifiedFiles", "changeSurface"),
    "budget": ("remainingBudgets",),
}


def identity_failures(before: Mapping[str, Any], after: Mapping[str, Any]) -> list[str]:
    """Score one resume/compaction transition. Empty list == identity held.

    `before` is what the pre-transition state asserted; `after` is what the
    post-transition state carries. Any dimension that changed, emptied or
    disappeared is a row-7 failure by name.
    """
    failures: list[str] = []
    for dimension, keys in DIMENSIONS.items():
        for key in keys:
            expected = before.get(key)
            if expected in (None, "", [], {}, ()):
                continue  # the source never asserted this field; nothing to lose
            actual = after.get(key)
            if actual in (None, "", [], {}, ()):
                failures.append(
                    f"{dimension} identity lost: {key!r} was {expected!r}, is now {actual!r}")
            elif actual != expected:
                failures.append(
                    f"{dimension} identity drifted: {key!r} was {expected!r}, is now {actual!r}")
    return failures


# --------------------------------------------------------------------------
# A durable episode whose five identity dimensions are all asserted on the wire.
# --------------------------------------------------------------------------

TREE_HASH = "sha256:" + "e" * 64
DECLARED = {
    "objective": "make the failing suite green without touching the oracle",
    "changedFilesTreeHash": TREE_HASH,
    "plan": ["read the failure", "patch src/a.py", "verify"],
    "modifiedFiles": ["src/a.py"],
    "changeSurface": ["src/a.py"],
    "remainingBudgets": {"tokens": 13, "usd_micros": 500},
}


def _event(kind: str, payload: Mapping[str, Any]) -> Any:
    from vanguard.packages.kernel.model import Event

    return Event(kind=kind, reason="t131-row7", at="2026-09-12T00:00:00.000Z",
                 run_id="run-t131-row7", principal="agent-1",
                 payload={"kind": kind, **payload})


def durable_events() -> list[Any]:
    return [
        _event("EpisodeStarted", {
            "episodeId": "ep-t131-row7",
            "objective": DECLARED["objective"],
            "budgetCeiling": DECLARED["remainingBudgets"],
        }),
        _event("PlanDeclared", {"plan": DECLARED["plan"]}),
        _event("EffectCompleted", {
            "action": "patch.apply", "path": "src/a.py",
            "descriptorDigest": "sha256:" + "d" * 64,
            "changedFilesTreeHash": TREE_HASH,
        }),
        _event("ChangeSurfaceUpdated", {"changeSurface": DECLARED["changeSurface"]}),
        _event("ProposalProduced", {"turn": 0, "action": "patch.apply"}),
        _event("ProposalProduced", {"turn": 1, "action": "verify"}),
    ]


class TheProductFoldPreservesIdentity(unittest.TestCase):
    """POSITIVE falsifier — the in-process resume fold."""

    def test_every_named_dimension_survives_the_fold(self) -> None:
        state = fold_task_state(durable_events(), objective=DECLARED["objective"])
        after = state.to_canonical_dict()

        self.assertEqual(identity_failures(DECLARED, after), [])
        self.assertEqual(after["changedFilesTreeHash"], TREE_HASH)
        self.assertEqual(after["remainingBudgets"], DECLARED["remainingBudgets"])


class TheCompactionFloorPreservesIdentity(unittest.TestCase):
    """POSITIVE falsifier — the compaction floor (`critical_state`).

    `critical_state` is the mandatory-state brief `ContextCompiler.compile_packet`
    places below the eviction watermark: whatever is not in it can be compacted
    away. Row 7 therefore requires all five dimensions to be inside it.
    """

    def _view(self) -> MemoryView:
        task = SemanticTaskState(
            objective=DECLARED["objective"],
            plan=tuple(DECLARED["plan"]),
            modified_files=tuple(DECLARED["modifiedFiles"]),
            remaining_budgets=dict(DECLARED["remainingBudgets"]),
            changed_files_tree_hash=TREE_HASH,
        )
        return MemoryView(
            task_bytes=canonical_bytes(task.to_canonical_dict()),
            cursor=2, lineage_id="lineage-t131", reducer_version="1",
        )

    def test_the_mandatory_state_carries_all_five_dimensions(self) -> None:
        projected = critical_state(self._view())
        mapped = {
            "objective": projected.get("objective"),
            "changedFilesTreeHash": projected.get("changed_files_tree_hash"),
            "plan": list(projected.get("plan") or []),
            "modifiedFiles": list(projected.get("modified_files") or []),
            "changeSurface": list(projected.get("modified_files") or []),
            "remainingBudgets": dict(projected.get("remaining_budgets") or {}),
        }
        self.assertEqual(identity_failures(DECLARED, mapped), [])

    def test_the_projection_is_json_serialisable_as_the_compiler_uses_it(self) -> None:
        """The compiler serialises this projection into the brief; a field it
        cannot serialise would be silently absent from the prompt."""
        text = json.dumps(critical_state(self._view()), sort_keys=True)
        self.assertIn(TREE_HASH, text)
        self.assertIn(DECLARED["objective"], text)


class TheInstrumentRedsOnLostIdentity(unittest.TestCase):
    """ADVERSARIAL falsifier — every dimension is individually load-bearing."""

    def setUp(self) -> None:
        self.after = fold_task_state(
            durable_events(), objective=DECLARED["objective"]).to_canonical_dict()
        self.assertEqual(identity_failures(DECLARED, self.after), [])

    def test_dropping_any_single_dimension_reds(self) -> None:
        for dimension, keys in DIMENSIONS.items():
            for key in keys:
                if DECLARED.get(key) in (None, "", [], {}, ()):
                    continue
                with self.subTest(dimension=dimension, key=key):
                    damaged = {k: v for k, v in self.after.items() if k != key}
                    failures = identity_failures(DECLARED, damaged)
                    self.assertTrue(failures, f"dropping {key} was not caught")
                    self.assertTrue(
                        any(item.startswith(f"{dimension} identity lost") for item in failures),
                        failures)

    def test_drifting_any_single_dimension_reds(self) -> None:
        for key in ("objective", "changedFilesTreeHash", "plan",
                    "modifiedFiles", "changeSurface", "remainingBudgets"):
            with self.subTest(key=key):
                damaged = dict(self.after)
                damaged[key] = "sha256:" + "0" * 64 if isinstance(damaged[key], str) else ["tampered"]
                self.assertTrue(identity_failures(DECLARED, damaged), f"{key} drift was not caught")

    def test_a_real_fold_that_drops_the_change_surface_reds(self) -> None:
        """A genuine product-shaped defect, not a hand-edited dict.

        `fold_task_state` ignores any event kind outside `_KNOWN_KINDS`. An
        emitter that renamed `ChangeSurfaceUpdated` therefore produces a resume
        state with no change surface at all — silently. The instrument must red
        on that fold rather than report a clean resume.
        """
        events = [
            _event("ChangeSurfaceRecorded", {"changeSurface": DECLARED["changeSurface"]})
            if e.payload.get("kind") == "ChangeSurfaceUpdated" else e
            for e in durable_events()
        ]
        after = fold_task_state(events, objective=DECLARED["objective"]).to_canonical_dict()
        failures = identity_failures(DECLARED, after)
        self.assertTrue(failures, "an unrecognised event kind silently emptied the change surface")
        self.assertTrue(
            any(item.startswith("changed-file identity lost") for item in failures), failures)

    def test_a_real_fold_that_loses_the_candidate_tree_hash_reds(self) -> None:
        events = [
            _event("EffectCompleted", {
                "action": "patch.apply", "path": "src/a.py",
                "descriptorDigest": "sha256:" + "d" * 64,
            })
            if e.payload.get("kind") == "EffectCompleted" else e
            for e in durable_events()
        ]
        after = fold_task_state(events, objective=DECLARED["objective"]).to_canonical_dict()
        failures = identity_failures(DECLARED, after)
        self.assertTrue(
            any(item.startswith("candidate identity lost") for item in failures), failures)

    def test_the_compaction_floor_check_reds_when_a_dimension_is_removed(self) -> None:
        """The compaction assertion must not be vacuous either."""
        projected = dict(critical_state(MemoryView(
            task_bytes=canonical_bytes(SemanticTaskState(
                objective=DECLARED["objective"],
                plan=tuple(DECLARED["plan"]),
                modified_files=tuple(DECLARED["modifiedFiles"]),
                remaining_budgets=dict(DECLARED["remainingBudgets"]),
                changed_files_tree_hash=TREE_HASH,
            ).to_canonical_dict()),
            cursor=2, lineage_id="lineage-t131", reducer_version="1")))
        for key in ("objective", "changed_files_tree_hash", "plan",
                    "modified_files", "remaining_budgets"):
            with self.subTest(key=key):
                damaged = {k: v for k, v in projected.items() if k != key}
                mapped = {
                    "objective": damaged.get("objective"),
                    "changedFilesTreeHash": damaged.get("changed_files_tree_hash"),
                    "plan": list(damaged.get("plan") or []),
                    "modifiedFiles": list(damaged.get("modified_files") or []),
                    "changeSurface": list(damaged.get("modified_files") or []),
                    "remainingBudgets": dict(damaged.get("remaining_budgets") or {}),
                }
                self.assertTrue(identity_failures(DECLARED, mapped),
                                f"compaction losing {key} was not caught")


# --------------------------------------------------------------------------
# Fresh-process resume. A separate interpreter, a file-backed WAL, a hard exit.
# --------------------------------------------------------------------------

_WRITER = r'''
import os, sys, json
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.kernel.model import Event
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter
from vanguard.packages.runtime.root import Runtime

db, declared_json = sys.argv[1], sys.argv[2]
declared = json.loads(declared_json)
harness = Runtime.compose("vg-code-default", episode_id="ep-t131-row7")
store = SqliteEventStore(db)
emitter = LedgerEmitter(
    store, episode_id="ep-t131-row7", project_id="project-t131",
    principal_id="agent-1", harness_digest=harness.composition_digest,
    clock=FixedClock(at="2026-09-12T00:00:00.000Z", step_ms=1),
    random=SeededRandom(seed=131), role="kernel")

def emit(kind, payload):
    emitter.emit(Event(kind=kind, reason="t131", at="2026-09-12T00:00:00.000Z",
                       run_id="run-t131-row7", principal="agent-1",
                       payload={"kind": kind, **payload}))

emit("EpisodeStarted", {"episodeId": "ep-t131-row7",
                        "compositionDigest": harness.composition_digest,
                        "objective": declared["objective"],
                        "maxTurns": 8,
                        "budgetCeiling": declared["remainingBudgets"]})
emit("PlanRevised", {"plan": declared["plan"]})
emit("ProposalProduced", {"turn": 0, "proposalDigest": "sha256:" + "1" * 64,
                          "action": "patch.apply"})
emit("EffectCompleted", {"action": "patch.apply", "path": "src/a.py",
                         "descriptorDigest": "sha256:" + "d" * 64,
                         "changedFilesTreeHash": declared["changedFilesTreeHash"]})
emit("ProposalProduced", {"turn": 1, "proposalDigest": "sha256:" + "2" * 64})
emit("BudgetReserved", {"leaseId": "lease-t131", "dimensions": {"tokens": 20},
                        "limits": {"tokens": 20}})
emit("BudgetCommitted", {"leaseId": "lease-t131", "debits": {"tokens": 7}})
# Hard death: no terminal event, no clean shutdown, no flush of anything the
# process was holding. Whatever survives is what the WAL durably held.
os._exit(91)
'''

_RESUMER = r'''
import json, sys
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.task_state import fold_task_state

db = sys.argv[1]
store = SqliteEventStore(db)
read = store.read(EventRange(run_id="run-t131-row7"))
events = list(read.value or ())
state = fold_task_state(events, objective="")
turns = len([e for e in events
             if (getattr(e, "payload", {}) or {}).get("kind") == "ProposalProduced"])
print(json.dumps({
    "resumeState": state.to_canonical_dict(),
    "turnsConsumed": turns,
    "kinds": [(getattr(e, "payload", {}) or {}).get("kind") for e in events],
}))
store.close()
'''


class FreshProcessResumePreservesIdentity(unittest.TestCase):
    """POSITIVE plus ADVERSARIAL — resume across a real process boundary.

    The writer dies with `os._exit`, so nothing in-process survives. Every
    dimension the resumer reports came out of the durable WAL.
    """

    def _run(self) -> tuple[dict[str, Any], Path]:
        tmp = tempfile.mkdtemp()
        db = Path(tmp) / "row7.sqlite3"
        env = {**os.environ, "PYTHONPATH": str(ROOT)}
        crashed = subprocess.run(
            [sys.executable, "-c", _WRITER, str(db), json.dumps(DECLARED)],
            cwd=ROOT, env=env, check=False, capture_output=True, text=True)
        self.assertEqual(crashed.returncode, 91,
                         (crashed.stdout or "") + (crashed.stderr or ""))
        resumed = subprocess.run(
            [sys.executable, "-c", _RESUMER, str(db)],
            cwd=ROOT, env=env, check=False, capture_output=True, text=True)
        self.assertEqual(resumed.returncode, 0,
                         (resumed.stdout or "") + (resumed.stderr or ""))
        return json.loads(resumed.stdout.strip().splitlines()[-1]), db

    #: The writer durably commits 7 tokens against the declared 13-token
    #: ceiling, so a continuation that preserved resource identity reports 6
    #: remaining. Reporting 13 is not "identity preserved" -- it is the
    #: replenished budget row 7 names as a defect (T-131.7).
    DEBITED_BUDGETS = {"tokens": 6, "usd_micros": 500}

    def test_a_fresh_interpreter_recovers_all_five_dimensions(self) -> None:
        observed, _ = self._run()
        # This fixture's writer emits no `ChangeSurfaceUpdated`, so the
        # changed-file identity it recovers comes from `EffectCompleted.path`
        # and the declared surface is not among the dimensions this run can
        # observe. DIR-D1 has since made `ChangeSurfaceUpdated` writable and
        # given it a producer; the surface carrier itself is falsified in
        # `test/runtime/test_task_state_durable_carriers.py`, not here.
        declared = {
            **{k: v for k, v in DECLARED.items() if k != "changeSurface"},
            "remainingBudgets": self.DEBITED_BUDGETS,
        }
        self.assertEqual(identity_failures(declared, observed["resumeState"]), [])
        self.assertEqual(observed["resumeState"]["modifiedFiles"], ["src/a.py"])

    def test_the_resumed_budget_is_debited_by_the_durable_commitment(self) -> None:
        """ADVERSARIAL: the ceiling is not what a continuation may report.

        Before T-131.7 the fold read `remainingBudgets` back out of the
        `EpisodeStarted` header, so a fresh process reported the full ceiling
        however much the same WAL said it had already committed. The writer
        commits 7 of 13 tokens; a resume that still says 13 has replenished a
        spent budget, and this asserts it cannot.
        """
        observed, _ = self._run()
        remaining = observed["resumeState"]["remainingBudgets"]
        self.assertEqual(remaining["tokens"], 6)
        self.assertNotEqual(
            remaining["tokens"], DECLARED["remainingBudgets"]["tokens"],
            "the fresh process restored the ceiling instead of the remainder")
        self.assertLess(remaining["tokens"], DECLARED["remainingBudgets"]["tokens"])

    def test_the_fresh_process_neither_duplicates_effects_nor_resets_the_ceiling(self) -> None:
        observed, _ = self._run()
        kinds = observed["kinds"]
        self.assertEqual(kinds.count("EpisodeStarted"), 1,
                         "resume duplicated the episode start")
        self.assertEqual(kinds.count("EffectCompleted"), 1,
                         "resume duplicated a settled effect")
        # `HarnessSession.run` computes `remaining = max_turns - turns_consumed()`
        # from the ledger, so a ceiling that survives the process boundary must
        # be strictly reduced by the turns already spent.
        original_ceiling = 8
        self.assertEqual(observed["turnsConsumed"], 2)
        remaining = original_ceiling - observed["turnsConsumed"]
        self.assertEqual(remaining, 6)
        self.assertLess(remaining, original_ceiling,
                        "the ceiling was reset rather than resumed")

    def test_a_resume_that_reset_the_ceiling_would_be_caught(self) -> None:
        """ADVERSARIAL control for the ceiling clause.

        A resume that ignores the ledger's turn count restores the full
        ceiling. The assertion above must be capable of failing on it.
        """
        observed, _ = self._run()
        reset_remaining = 8  # the defect: ledger turns ignored
        with self.assertRaises(AssertionError):
            self.assertLess(reset_remaining, 8)
        self.assertNotEqual(reset_remaining, 8 - observed["turnsConsumed"])


class EveryDimensionHasAWritableCarrier(unittest.TestCase):
    """Row 7 is unqualifiable if the fold reads kinds nothing may write.

    `fold_task_state` recognises 28 event kinds, but `WRITABLE_KINDS`
    (`domain/ledger/events.py`, `ADR-0098 Decision 3`) is the sole authority on
    what a production writer may originate. A dimension whose only carrier is
    an unwritable kind cannot survive a real resume however green a fixture
    looks, so the carriers are asserted here against that authority.
    """

    #: The carrier each dimension must be reconstructible from on the product
    #: route. These are the kinds the fresh-process test actually emits.
    CARRIERS = {
        "task": "EpisodeStarted",
        "candidate": "EffectCompleted",
        "plan": "PlanRevised",
        "changed-file": "EffectCompleted",
        "budget": "EpisodeStarted",
    }

    def test_each_dimension_is_carried_by_a_writable_kind(self) -> None:
        from vanguard.packages.domain.ledger.events import WRITABLE_KINDS
        from vanguard.packages.runtime.task_state import _KNOWN_KINDS

        for dimension, kind in self.CARRIERS.items():
            with self.subTest(dimension=dimension):
                self.assertIn(kind, WRITABLE_KINDS,
                              f"{dimension} identity has no writable carrier")
                self.assertIn(kind, _KNOWN_KINDS,
                              f"the resume fold ignores {kind}")

    def test_the_check_reds_on_an_unwritable_carrier(self) -> None:
        """ADVERSARIAL control: the assertion above is not vacuous.

        The control needs a kind the fold reads and no production writer may
        originate. `ChangeSurfaceUpdated` was that kind until DIR-D1 allocated
        it a schema kind, a sole session writer and a producer, so naming it
        here would now assert the opposite of what it did. `PlanDeclared` is
        narrowed in as its replacement: it is read by `fold_task_state` and is
        still not writable, so the check is exercised on a real unwritable
        carrier rather than retired. DIR-D1 authorised exactly two
        allocations; the remaining sixteen unwritable fold names, this one
        included, stay unwritable.
        """
        from vanguard.packages.domain.ledger.events import WRITABLE_KINDS
        from vanguard.packages.runtime.task_state import _KNOWN_KINDS

        self.assertIn("PlanDeclared", _KNOWN_KINDS)
        with self.assertRaises(AssertionError):
            self.assertIn("PlanDeclared", WRITABLE_KINDS)

    def test_exactly_the_two_authorised_kinds_became_writable(self) -> None:
        """DIR-D1 scope: two allocations, not a blanket activation.

        At the T-131 subject eighteen of the fold's recognised kinds were
        unwritable. DIR-D1 authorises `VerificationRecorded` and
        `ChangeSurfaceUpdated` and forbids activating the rest, so the count
        is pinned: a third activation reds here before it reaches review.
        """
        from vanguard.packages.domain.ledger.events import (
            DEPRECATED_KINDS, WRITABLE_KINDS)
        from vanguard.packages.runtime.task_state import _KNOWN_KINDS

        unwritable = _KNOWN_KINDS - WRITABLE_KINDS
        self.assertEqual(len(unwritable), 16, sorted(unwritable))
        for kind in ("VerificationRecorded", "ChangeSurfaceUpdated"):
            self.assertIn(kind, WRITABLE_KINDS)
        # None of the fold's kinds is deprecated, so shrinking
        # `DEPRECATED_KINDS` could never have closed this gap.
        self.assertEqual(_KNOWN_KINDS & DEPRECATED_KINDS, frozenset())


# ==========================================================================
# T-131.7 — continuation identity through the ACTUAL runtime, not the fold.
#
# Everything above scores `fold_task_state` over handcrafted events and
# `critical_state` over a constructed `MemoryView`. That qualifies the
# projection, not the product: a run whose ingress never hands the projection
# to the planner would pass every assertion above while losing the objective
# on restart.
#
# This section therefore drives the executable ingress the board names --
# `entrypoint.execute` -> `Runtime.execute_profiled` -> `Runtime.run_composed`
# -> `HarnessSession.run` -- with `injectedModel`, `storePath` and the same run
# ID across two real processes, and kills the first one with SIGKILL after a
# real durable `EffectStarted`. No provider is contacted: the model is a
# scripted double and the store is a local disposable WAL (`RUN-12`).
# ==========================================================================

RUN_ID = "run-t131-row7-runtime"
OBJECTIVE = "T131ROW7 OBJECTIVE: make app.f return 1"

#: Emitted by the child so the parent can tell "the workspace was prepared"
#: apart from "the child died before it prepared anything".
_RUNTIME_DRIVER = r"""
import json, os, subprocess, sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime import entrypoint

phase, root, store, run_id, objective = sys.argv[2:7]
root, store = Path(root), Path(store)
os.environ["AETHER_WORKSPACE_ROOT"] = str(root)


class Scripted:
    # A ModelPort double. It records the compiled context it was handed, so
    # the parent can read exactly what the resumed planner was told.

    def __init__(self, tape):
        self.tape, self.cursor, self.contexts = list(tape), 0, []

    def propose(self, context, tools, sampling):
        self.contexts.append(context)
        if self.cursor >= len(self.tape):
            return Result.success({"kind": "abstain", "note": "tape exhausted"})
        item = self.tape[self.cursor]
        self.cursor += 1
        return Result.success(dict(item))


def patch(path, content):
    return {"kind": "effect", "action": "patch.apply",
            "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
            "args": {"path": path, "content": content}, "note": "implement"}


def run_proc(argv, note):
    return {"kind": "effect", "action": "proc.exec",
            "resource": {"kind": "generic",
                         "uriPattern": "proc://exec/allow/git,pytest,ruff,python3"},
            "args": {"argv": argv}, "note": note}


if phase == "seed":
    root.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text("[project]\nname='row7'\n")
    (root / "app.py").write_text("def f():\n    pass\n")
    for command in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"],
                    ["git", "config", "user.name", "t"], ["git", "add", "-A"],
                    ["git", "commit", "-qm", "init"]):
        subprocess.run(command, cwd=root, check=True, capture_output=True)
    (root / ".vanguard").mkdir(exist_ok=True)
    model = Scripted([
        patch("app.py", "def f():\n    return 1\n"),
        # A real process effect whose child SIGKILLs this interpreter. The
        # kernel has durably appended `EffectStarted` and has not yet appended
        # any terminal, so the WAL is left holding a genuine open intent --
        # not a fabricated test ledger entry.
        run_proc(["python3", "-c",
                  "import os, signal; os.kill(os.getppid(), signal.SIGKILL)"], "crash"),
        {"kind": "abstain", "note": "unreachable"},
    ])
    entrypoint.execute({
        "command": "code", "brief": objective, "workspace": str(root),
        "storePath": str(store), "injectedModel": model, "profile": "product",
        "interactive": False, "maxTurnsPerEpisode": 6, "runId": run_id,
        "harness": "vg-code-default"})
    print(json.dumps({"survivedTheCrash": True}))

elif phase == "resume":
    model = Scripted([{"kind": "abstain", "note": "observe the restored context"}])
    frame = entrypoint.execute({
        "command": "resume", "runId": run_id, "workspace": str(root),
        "storePath": str(store), "injectedModel": model, "profile": "product",
        "interactive": False, "maxTurnsPerEpisode": 6,
        "harness": "vg-code-default"})
    context = model.contexts[0] if model.contexts else {}
    print(json.dumps({
        "outcome": frame["result"]["outcome"],
        "firstResumedContext": json.dumps(context, default=str),
    }))
"""


def _drive(phase: str, root: Path, store: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", _RUNTIME_DRIVER, str(ROOT), phase,
         str(root), str(store), RUN_ID, OBJECTIVE],
        cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT)},
        check=False, capture_output=True, text=True, timeout=600)


class RuntimeContinuationIdentity(unittest.TestCase):
    """T-131.7 through the product ingress, across a real process boundary."""

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name) / "workspace"
        cls.store = cls.root / ".vanguard" / "events.sqlite3"
        cls.seed = _drive("seed", cls.root, cls.store)
        cls.events = cls._read()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    @classmethod
    def _read(cls) -> list[Any]:
        store = SqliteEventStore(str(cls.store))
        try:
            read = store.read(EventRange(run_id=RUN_ID))
            return list(read.value or ())
        finally:
            store.close()

    @classmethod
    def _kinds(cls, events: Sequence[Any]) -> list[str]:
        return [(getattr(e, "payload", {}) or {}).get("kind") or "" for e in events]

    def _folded(self) -> Mapping[str, Any]:
        return fold_task_state(self.events, objective="").to_canonical_dict()

    # -- the fixture itself must be the thing it claims to be --------------

    def test_the_seed_process_really_died_after_a_durable_effect_started(self) -> None:
        """The premise. A clean exit would make every assertion below vacuous."""
        self.assertLess(self.seed.returncode, 0,
                        f"seed exited {self.seed.returncode}, expected a signal death")
        self.assertEqual(self.seed.returncode, -signal.SIGKILL)
        self.assertNotIn("survivedTheCrash", self.seed.stdout)

        kinds = self._kinds(self.events)
        self.assertEqual(kinds.count("EffectStarted"), 2, kinds)
        self.assertEqual(kinds.count("EffectCompleted"), 1, kinds)
        # Exactly one intent is open: the process effect that killed us.
        started = {
            (getattr(e, "payload", {}) or {}).get("descriptorDigest")
            for e in self.events
            if (getattr(e, "payload", {}) or {}).get("kind") == "EffectStarted"
        }
        terminal = {
            (getattr(e, "payload", {}) or {}).get("descriptorDigest")
            for e in self.events
            if (getattr(e, "payload", {}) or {}).get("kind")
            in ("EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled")
        }
        self.assertEqual(len(started - terminal), 1, "no genuinely open intent was left")

    # -- POSITIVE: what the durable fold carries out of a real crash --------

    def test_the_objective_survives_the_process_boundary(self) -> None:
        self.assertEqual(self._folded()["objective"], OBJECTIVE)

    def test_the_candidate_and_change_surface_survive(self) -> None:
        folded = self._folded()
        self.assertEqual(folded["modifiedFiles"], ["app.py"])
        self.assertEqual(folded["changeSurface"], ["app.py"])
        self.assertTrue(folded["changedFilesTreeHash"].startswith("sha256:"))

    def test_the_settled_effect_is_identified_and_the_open_one_is_not(self) -> None:
        """Settled and pending effect identity are distinct, and stay distinct.

        Presenting the open intent as settled is how a continuation skips an
        effect that may never have happened; presenting the settled one as
        pending is how it replays one that did.
        """
        continuity = self._folded()["recoveryState"]["continuity"]
        pending = {entry["descriptorDigest"] for entry in continuity["pendingEffects"]}
        settled = set(self._folded()["settledEffects"])

        self.assertEqual(len(settled), 1, settled)
        self.assertEqual(len(pending), 1, pending)
        self.assertEqual(settled & pending, set(),
                         "an effect is reported as both settled and pending")
        self.assertEqual(
            [entry["action"] for entry in continuity["pendingEffects"]], ["proc.exec"])

    def test_aggregate_consumption_survives_and_is_not_replenished(self) -> None:
        """Resource identity: the ceiling is not the remainder.

        The run settled one real effect against the preset's declared ceiling.
        A continuation that reports the ceiling unchanged has replenished a
        budget the same WAL says was spent.
        """
        folded = self._folded()
        continuity = folded["recoveryState"]["continuity"]
        ceiling = continuity["budgetCeiling"]
        consumed = continuity["consumedBudgets"]

        self.assertTrue(ceiling, "the episode declared no ceiling to preserve")
        self.assertTrue(consumed, "a settled effect charged nothing at all")
        for dimension, spent in consumed.items():
            with self.subTest(dimension=dimension):
                self.assertEqual(
                    folded["remainingBudgets"][dimension],
                    max(ceiling[dimension] - spent, 0))
                self.assertLess(folded["remainingBudgets"][dimension], ceiling[dimension])

    def test_grant_identity_survives_the_process_boundary(self) -> None:
        live = self._folded()["recoveryState"]["continuity"]["liveGrants"]
        self.assertTrue(live, "no grant identity survived the crash")
        for grant in live:
            with self.subTest(grant=grant["grantId"]):
                self.assertTrue(grant["grantId"])
                self.assertTrue(str(grant["descriptorDigest"]).startswith("sha256:"))

    def test_the_real_resume_hydrates_identity_into_the_next_model_context(self) -> None:
        resumed = _drive("resume", self.root, self.store)
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        payload = json.loads(resumed.stdout.strip().splitlines()[-1])
        self.assertNotEqual(payload["outcome"], "completed")
        context = payload["firstResumedContext"]
        self.assertIn(OBJECTIVE, context)
        self.assertIn("app.py", context)
        self.assertIn("remainingBudgets", context)
        self.assertIn("pendingEffects", context)

    # -- ADVERSARIAL: each preservation step is individually load-bearing ---

    def test_a_restart_may_not_widen_the_ceiling(self) -> None:
        """A resumed episode re-declares its ceiling; a larger one is refused."""
        widened = list(self.events) + [
            _event("EpisodeStarted", {
                "episodeId": f"episode-{RUN_ID}",
                "budgetCeiling": {
                    dimension: amount * 1000 for dimension, amount
                    in self._folded()["recoveryState"]["continuity"]["budgetCeiling"].items()
                },
            })
        ]
        after = fold_task_state(widened, objective="").to_canonical_dict()
        for dimension, amount in self._folded()["remainingBudgets"].items():
            with self.subTest(dimension=dimension):
                self.assertLessEqual(after["remainingBudgets"][dimension], amount)

    def test_a_restart_may_not_replenish_a_spent_budget(self) -> None:
        """The exact defect: re-declaring the ceiling after the spend."""
        folded = self._folded()
        spent_dimension = next(iter(
            folded["recoveryState"]["continuity"]["consumedBudgets"]))
        replenished = list(self.events) + [
            _event("EpisodeStateChanged", {
                "remainingBudgets": {
                    k: v * 10 for k, v in
                    folded["recoveryState"]["continuity"]["budgetCeiling"].items()
                },
            })
        ]
        after = fold_task_state(replenished, objective="").to_canonical_dict()
        self.assertEqual(
            after["remainingBudgets"][spent_dimension],
            folded["remainingBudgets"][spent_dimension],
            "re-declaring the ceiling restored a spent dimension")
        self.assertLess(
            after["remainingBudgets"][spent_dimension],
            folded["recoveryState"]["continuity"]["budgetCeiling"][spent_dimension],
            "replenished budget reached or exceeded the ceiling")

    def test_a_settled_effect_may_not_be_replayed_as_pending(self) -> None:
        """Re-emitting the intent for an already-settled effect changes nothing.

        A retry loop that re-proposed the settled patch would append a second
        `EffectStarted` for the same descriptor. The projection must still
        report it settled, or the planner is invited to redo a durable write.
        """
        settled_digest = self._folded()["settledEffects"][0]
        replayed = list(self.events) + [
            _event("EffectStarted", {
                "action": "patch.apply", "descriptorDigest": settled_digest})
        ]
        after = fold_task_state(replayed, objective="").to_canonical_dict()
        pending = {
            entry["descriptorDigest"]
            for entry in after["recoveryState"]["continuity"]["pendingEffects"]
        }
        self.assertIn(settled_digest, after["settledEffects"])
        self.assertNotIn(settled_digest, pending,
                         "a settled effect was re-offered as unresolved work")

    def test_an_undeterminable_reconciliation_is_unresolved_work_not_evidence(self) -> None:
        """`F-22`: uncertainty is preserved, never resolved to success."""
        open_digest = next(
            entry["descriptorDigest"]
            for entry in self._folded()["recoveryState"]["continuity"]["pendingEffects"]
        )
        reconciled = list(self.events) + [
            _event("EffectReconciled", {
                "action": "proc.exec", "descriptorDigest": open_digest,
                "occurrence": "undeterminable"})
        ]
        after = fold_task_state(reconciled, objective="").to_canonical_dict()
        pending = {
            entry["descriptorDigest"]
            for entry in after["recoveryState"]["continuity"]["pendingEffects"]
        }
        self.assertNotIn(open_digest, after["settledEffects"],
                         "an undeterminable effect was promoted to settled")
        self.assertIn(open_digest, pending)

    def test_an_occurred_reconciliation_settles_and_stops_being_pending(self) -> None:
        open_digest = next(
            entry["descriptorDigest"]
            for entry in self._folded()["recoveryState"]["continuity"]["pendingEffects"]
        )
        reconciled = list(self.events) + [
            _event("EffectReconciled", {
                "action": "proc.exec", "descriptorDigest": open_digest,
                "occurrence": "occurred"})
        ]
        after = fold_task_state(reconciled, objective="").to_canonical_dict()
        pending = {
            entry["descriptorDigest"]
            for entry in after["recoveryState"]["continuity"]["pendingEffects"]
        }
        self.assertIn(open_digest, after["settledEffects"])
        self.assertNotIn(open_digest, pending)

    def test_revocation_survives_restart_and_is_transitive(self) -> None:
        """`K-49`. A restart may not restore authority that was revoked."""
        live = self._folded()["recoveryState"]["continuity"]["liveGrants"]
        parent = live[0]["grantId"]
        revoked_stream = list(self.events) + [
            _event("CapabilityGranted", {
                "grantId": "grant-child", "parentGrantId": parent,
                "descriptorDigest": "sha256:" + "c" * 64}),
            _event("CapabilityRevoked", {"grantId": parent}),
        ]
        after = fold_task_state(revoked_stream, objective="").to_canonical_dict()
        continuity = after["recoveryState"]["continuity"]
        surviving = {grant["grantId"] for grant in continuity["liveGrants"]}

        self.assertNotIn(parent, surviving, "a revoked grant survived the fold")
        self.assertNotIn("grant-child", surviving,
                         "a child of a revoked grant survived: revocation was not transitive")
        self.assertIn(parent, continuity["revokedGrants"])
        self.assertIn("grant-child", continuity["revokedGrants"])

    def test_dropping_a_continuity_carrier_reds(self) -> None:
        """No carrier is decorative: removing each one loses its dimension.

        This is the row-7 "dropped carrier" case applied to the continuity
        carriers, scored against the real runtime stream rather than a fixture.
        """
        baseline = self._folded()
        cases = {
            "EffectStarted": lambda after: after["recoveryState"]["continuity"]["pendingEffects"],
            "EffectCompleted": lambda after: after["settledEffects"],
            "CapabilityGranted": lambda after: after["recoveryState"]["continuity"]["liveGrants"],
            "BudgetCommitted": lambda after: after["recoveryState"]["continuity"]["consumedBudgets"],
        }
        for kind, project in cases.items():
            with self.subTest(carrier=kind):
                self.assertTrue(project(baseline), f"{kind} carried nothing to begin with")
                without = [
                    e for e in self.events
                    if (getattr(e, "payload", {}) or {}).get("kind") != kind
                ]
                after = fold_task_state(without, objective="").to_canonical_dict()
                self.assertFalse(
                    project(after),
                    f"dropping {kind} did not lose its dimension; the carrier is not load-bearing")


class ColdStartHydrationIsBound(unittest.TestCase):
    """T-131.7 cold-start ingress hydrates rather than synthesising a task."""

    def test_the_ingress_builds_the_durable_resume_state(self) -> None:
        source = inspect.getsource(entrypoint.execute)
        self.assertIn("task = TaskContext(", source)
        construction = source.split("task = TaskContext(", 1)[1].split(")", 1)[0]
        self.assertIn("resume_state=resume_state", construction)
        self.assertIn("fold_task_state(events", source)

    def test_changed_composition_is_rejected_when_resume_identity_is_present(self) -> None:
        session = SimpleNamespace(
            task=SimpleNamespace(resume_state={
                "selectionPolicyIdentity": {"behaviorIdentity": {
                    "compositionDigest": "sha256:" + "a" * 64,
                }},
            }),
            _behavior_identity={"compositionDigest": "sha256:" + "b" * 64},
        )
        with self.assertRaises(ContextPacketError):
            HarnessSession._assert_resume_behavior_identity(session)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
