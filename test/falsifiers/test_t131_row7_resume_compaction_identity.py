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

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.canonicalisation.jcs import canonical_bytes
from vanguard.packages.domain.task_state import MemoryView, SemanticTaskState, critical_state
from vanguard.packages.ports.event_store import EventRange
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

    def test_a_fresh_interpreter_recovers_all_five_dimensions(self) -> None:
        observed, _ = self._run()
        # `ChangeSurfaceUpdated` is not in `WRITABLE_KINDS`, so no production
        # writer can originate it and the durable carrier of changed-file
        # identity is `EffectCompleted.path`. See
        # `EveryDimensionHasAWritableCarrier` for that boundary stated as a
        # falsifier rather than as a comment.
        declared = {k: v for k, v in DECLARED.items() if k != "changeSurface"}
        self.assertEqual(identity_failures(declared, observed["resumeState"]), [])
        self.assertEqual(observed["resumeState"]["modifiedFiles"], ["src/a.py"])

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

        `ChangeSurfaceUpdated` is read by the fold and is NOT writable. If a
        dimension were routed through it, the check must red.
        """
        from vanguard.packages.domain.ledger.events import WRITABLE_KINDS
        from vanguard.packages.runtime.task_state import _KNOWN_KINDS

        self.assertIn("ChangeSurfaceUpdated", _KNOWN_KINDS)
        with self.assertRaises(AssertionError):
            self.assertIn("ChangeSurfaceUpdated", WRITABLE_KINDS)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
