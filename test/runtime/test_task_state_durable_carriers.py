"""T-134 / DIR-D1: the two durable carriers, qualified end to end.

DIR-D1's claim is narrow and checkable: `VerificationRecorded` and
`ChangeSurfaceUpdated` are *emitted, validated, qualified* durable carriers,
so a fresh process can reconstruct an observed verification and a multi-file
create/modify/delete surface from persisted production facts alone.

Every event in this module is constructed by production code
(`HarnessSession._append_verification_record` /
`HarnessSession._append_change_surface`) and admitted by the production writer
(`LedgerEmitter`), through its real writer-authority and deprecation checks.
Nothing here injects an otherwise-unwritable event, and nothing hand-writes an
envelope: a carrier that production cannot originate cannot make this file
green.

`RUN-12`: no provider is contacted. The fresh-process case spawns the local
interpreter only.
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
from vanguard.packages.domain.ledger.events import DEPRECATED_KINDS, WRITABLE_KINDS
from vanguard.packages.kernel.model import Event
from vanguard.packages.ports.event_store import EventRange, Result
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.ledger_emitter import (
    DeprecatedKindError,
    LedgerEmitter,
    PRIVILEGED_KIND_OWNERS,
    WriterAuthorityError,
)
from vanguard.packages.runtime.session import HarnessSession, VerificationSubject
from vanguard.packages.runtime.task_state import fold_task_state

ROOT = Path(__file__).resolve().parents[2]
HARNESS_DIGEST = "sha256:" + "a" * 64
TASK_DIGEST = "sha256:" + "1" * 64
COMPOSITION_DIGEST = "sha256:" + "2" * 64
PREIMAGE_DIGEST = "sha256:" + "3" * 64
POSTIMAGE_DIGEST = "sha256:" + "4" * 64

#: A real multi-file candidate: one created file, one modified file, one
#: deleted file. The deletion is the case a surface that only listed surviving
#: paths would silently lose.
CREATED = "src/created.py"
MODIFIED = "src/modified.py"
DELETED = "src/removed.py"
SURFACE = sorted((CREATED, MODIFIED, DELETED))
ARGV = ("python3", "-m", "unittest", "test.smoke", "-v")
OBJECTIVE = "make the failing suite green without touching the oracle"


def _emitter(store: Any, *, role: str = "session", seed: int = 134) -> LedgerEmitter:
    return LedgerEmitter(
        store, episode_id="ep-t134", project_id="project-t134",
        principal_id="agent-1", harness_digest=HARNESS_DIGEST,
        clock=FixedClock(at="2026-09-12T00:00:00.000Z", step_ms=1),
        random=SeededRandom(seed=seed), role=role)


class _SessionUnderTest:
    """The production carrier methods, bound to the minimum they read.

    `HarnessSession.__init__` composes a whole runtime; these two methods read
    only a ledger, a task identity, a repo root and the in-memory receipt
    fields. Binding the real functions here exercises the shipped code without
    standing up a provider, and keeps the emitted bytes production bytes.
    """

    _append_change_surface = HarnessSession._append_change_surface
    _append_verification_record = HarnessSession._append_verification_record
    _carrier_bindings_or_latch = HarnessSession._carrier_bindings_or_latch
    _latch_carrier_failure = HarnessSession._latch_carrier_failure

    def __init__(self, ledger: LedgerEmitter, repo: Path, *,
                 workspace_digest: str = POSTIMAGE_DIGEST) -> None:
        self.ledger = ledger
        self.repo = repo
        self._workspace = workspace_digest
        self._completion_changed_files: set[str] = set()
        self._completion_verification = None
        self._completion_verification_subject = None
        self._durable_carrier_append_error: str | None = None
        self._completion_observed_test_count: int | None = 5
        self.task = type("Task", (), {
            "run_id": "run-t134", "principal": "agent-1",
            "episode_id": "ep-t134", "project_id": "project-t134"})()

    def _current_task_digest(self) -> str:
        return TASK_DIGEST

    def _workspace_digest(self) -> str:
        return self._workspace


def _receipt(*, exit_code: int = 0, count: int = 5,
             workspace: str = POSTIMAGE_DIGEST) -> Any:
    from vanguard.packages.agency.episode.admission_gate import VerificationReceipt

    subject = VerificationSubject(
        argv=ARGV, workspace_digest=workspace, task_digest=TASK_DIGEST)
    return VerificationReceipt(
        exit_code=exit_code, executed_test_count=count,
        workspace_digest=workspace, task_digest=TASK_DIGEST,
        receipt_digest="sha256:" + "5" * 64,
        composition_digest=COMPOSITION_DIGEST,
        verification_command=" ".join(ARGV),
        verification_subject_digest=subject.digest(),
    ), subject


def _request(action: str = "fs.patch") -> Any:
    from vanguard.packages.kernel import EffectRequest

    return EffectRequest(
        action=action, resource={"path": MODIFIED},
        args={"path": MODIFIED, "diff": "@@"},
        principal="agent-1", run_id="run-t134")


def _write_surface(session: _SessionUnderTest, repo: Path) -> None:
    """Land a create, a modify and a delete, then publish the surface."""
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / CREATED).write_text("created\n")
    (repo / MODIFIED).write_text("modified\n")
    # `DELETED` is deliberately never created: the carrier must still carry it.
    session._completion_changed_files.update(SURFACE)
    session._append_change_surface(_request())


def _kinds(events: Any) -> list[str]:
    return [(getattr(e, "payload", {}) or {}).get("kind") for e in events]


def _payload(events: Any, kind: str) -> Mapping[str, Any]:
    for event in events:
        if (getattr(event, "payload", {}) or {}).get("kind") == kind:
            return event.payload
    raise AssertionError(f"no {kind} in {_kinds(events)}")


class TheAllocationIsExactlyTwo(unittest.TestCase):
    """DIR-D1 scope. A third activation is an escalation, not a lease call."""

    def test_both_authorised_kinds_are_writable(self) -> None:
        for kind in ("VerificationRecorded", "ChangeSurfaceUpdated"):
            self.assertIn(kind, WRITABLE_KINDS)

    def test_no_other_fold_kind_was_activated(self) -> None:
        from vanguard.packages.runtime.task_state import _KNOWN_KINDS

        self.assertEqual(sorted(_KNOWN_KINDS - WRITABLE_KINDS), [
            "AmbiguityRecorded", "ConstraintDiscovered", "DeadEndRecorded",
            "HypothesisOpened", "HypothesisRejected", "HypothesisSupported",
            "NextActionSelected", "ObligationOpened", "ObligationSatisfied",
            "OperatorDirectiveReceived", "PlanDeclared", "RecoveryStateUpdated",
            "TaskClassified", "VerificationCompleted", "VerificationFailed",
            "VerificationPassed",
        ])

    def test_no_deprecated_kind_was_revived(self) -> None:
        self.assertEqual(
            DEPRECATED_KINDS & {"VerificationRecorded", "ChangeSurfaceUpdated"},
            frozenset())
        # `WRITABLE_KINDS` must stay the derivation, never a literal set.
        from vanguard.packages.domain.ledger.events import READABLE_KINDS

        self.assertEqual(WRITABLE_KINDS, READABLE_KINDS - DEPRECATED_KINDS)

    def test_verdict_ownership_is_unchanged(self) -> None:
        """The new fact is observed verification, not an evaluator verdict."""
        self.assertEqual(
            PRIVILEGED_KIND_OWNERS["VerdictRecorded"], frozenset({"evaluator_gateway"}))
        self.assertNotIn(
            "evaluator_gateway", PRIVILEGED_KIND_OWNERS["VerificationRecorded"])


class OnlyTheSessionMayOriginateACarrier(unittest.TestCase):
    """Sole session writer, and deprecated writes still denied."""

    def setUp(self) -> None:
        self.store = SqliteEventStore(":memory:")

    def tearDown(self) -> None:
        self.store.close()

    def _emit_as(self, role: str, kind: str) -> Any:
        # A fresh seed per append: the deterministic event-id source would
        # otherwise mint the same id twice and the store's UNIQUE constraint,
        # not the writer-authority check, would be what failed.
        self._seed = getattr(self, "_seed", 134) + 1
        emitter = _emitter(self.store, role=role, seed=self._seed)
        return emitter.emit_kind(
            kind, run_id="run-t134", principal="agent-1",
            episode_id="ep-t134", payload={"taskDigest": TASK_DIGEST})

    def test_the_session_role_may_originate_both_carriers(self) -> None:
        for kind in ("VerificationRecorded", "ChangeSurfaceUpdated"):
            envelope = self._emit_as("session", kind)
            self.assertEqual(envelope.payload["kind"], kind)

    def test_an_unauthorised_writer_is_refused(self) -> None:
        for role in ("orchestrator", "evaluator_gateway", "registry",
                     "recovery", "approval", "spawn_adapter", "kernel",
                     "scheduler"):
            for kind in ("VerificationRecorded", "ChangeSurfaceUpdated"):
                with self.subTest(role=role, kind=kind):
                    with self.assertRaises(WriterAuthorityError):
                        self._emit_as(role, kind)

    def test_the_refusal_is_not_a_blanket_refusal(self) -> None:
        """ADVERSARIAL: the check above would pass on a writer that refused
        everything. The same roles must still write what they do own."""
        self.assertEqual(
            self._emit_as("registry", "PluginActivated").payload["kind"],
            "PluginActivated")
        self.assertEqual(
            self._emit_as("kernel", "EffectCompleted").payload["kind"],
            "EffectCompleted")

    def test_deprecated_kinds_remain_denied(self) -> None:
        for kind in sorted(DEPRECATED_KINDS):
            with self.subTest(kind=kind):
                with self.assertRaises(DeprecatedKindError):
                    self._emit_as("session", kind)


class _RefusingStore:
    """An event store whose append durably fails."""

    def __init__(self, inner: Any, *, fail_on: str) -> None:
        self._inner = inner
        self._fail_on = fail_on
        self.appended: list[str] = []

    def append(self, envelopes: Any) -> Any:
        kinds = [e.payload.get("kind") for e in envelopes]
        if self._fail_on in kinds:
            return Result.fail("EIO", "disk full")
        self.appended.extend(kinds)
        return self._inner.append(envelopes)

    def read(self, selector: Any) -> Any:
        return self._inner.read(selector)


class AnAppendFailureStopsProgress(unittest.TestCase):
    """NT-1.6: the fact authorising the next boundary lands first, or nothing."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.inner = SqliteEventStore(":memory:")

    def tearDown(self) -> None:
        self.inner.close()
        self.tmp.cleanup()

    def _session(self, *, fail_on: str) -> _SessionUnderTest:
        store = _RefusingStore(self.inner, fail_on=fail_on)
        return _SessionUnderTest(_emitter(store), self.repo)

    def test_a_failed_surface_append_raises_and_latches(self) -> None:
        session = self._session(fail_on="ChangeSurfaceUpdated")
        with self.assertRaises(Exception):
            _write_surface(session, self.repo)
        self.assertIsNotNone(session._durable_carrier_append_error)
        self.assertIn("ChangeSurfaceUpdated", session._durable_carrier_append_error)

    def test_a_failed_verification_append_raises_and_latches(self) -> None:
        session = self._session(fail_on="VerificationRecorded")
        session._completion_verification, session._completion_verification_subject = _receipt()
        with self.assertRaises(Exception):
            session._append_verification_record()
        self.assertIn("VerificationRecorded", session._durable_carrier_append_error)

    def test_the_latch_refuses_the_next_inference_and_the_next_dispatch(self) -> None:
        """The gate is on `HarnessSession` itself, not on this stand-in."""
        session = self._session(fail_on="VerificationRecorded")
        session._completion_verification, session._completion_verification_subject = _receipt()
        with self.assertRaises(Exception):
            session._append_verification_record()

        session._recovery_guard = None
        session.context_packet = None
        with self.assertRaises(RuntimeError) as inference:
            HarnessSession._record_context_selection(
                session, {}, object(), 0, (), {})
        self.assertIn("durable carrier append failed", str(inference.exception))

        with self.assertRaises(RuntimeError) as dispatch:
            HarnessSession.dispatch(session, _request())
        self.assertIn("durable carrier append failed", str(dispatch.exception))

    def test_the_gate_is_not_always_closed(self) -> None:
        """ADVERSARIAL: a gate that refused unconditionally would also pass
        the test above. With no latch set, neither boundary refuses for this
        reason."""
        session = self._session(fail_on="nothing")
        session._recovery_guard = None
        session.context_packet = None
        self.assertIsNone(session._durable_carrier_append_error)
        try:
            HarnessSession._record_context_selection(session, {}, object(), 0, (), {})
        except RuntimeError as exc:  # pragma: no cover - defensive
            self.assertNotIn("durable carrier append failed", str(exc))
        except Exception:
            pass

    def test_an_unbound_identity_binding_is_refused_before_the_append(self) -> None:
        session = self._session(fail_on="nothing")
        session._workspace = ""  # environment snapshot unbound
        with self.assertRaises(RuntimeError):
            _write_surface(session, self.repo)
        self.assertIn("unbound identity bindings",
                      session._durable_carrier_append_error)
        read = self.inner.read(EventRange(run_id="run-t134"))
        self.assertNotIn("ChangeSurfaceUpdated", _kinds(read.value or ()))


class ObservedZeroIsNotUnknown(unittest.TestCase):
    """DIR-D1: the carrier binds the observed count, and null means unknown.

    Reported by Dev C in independent review of T-134. The carrier derived its
    field from `VerificationReceipt.executed_test_count`, an `int` that reports
    0 both when the runner printed no count and when it genuinely ran zero
    tests. Collapsing both to null made "ran zero tests" unrepresentable, so a
    resumed process could not tell an uninstrumented runner from one that
    executed nothing. `parse_observed_test_counts` already distinguishes them;
    the carrier now binds its answer.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.store = SqliteEventStore(":memory:")

    def tearDown(self) -> None:
        self.store.close()
        self.tmp.cleanup()

    def _emit_with(self, observed: int | None) -> Mapping[str, Any]:
        # A fresh seed per append: the deterministic event-id source would
        # otherwise mint the same id twice within one test.
        self._seed = getattr(self, "_seed", 134) + 1
        session = _SessionUnderTest(
            _emitter(self.store, seed=self._seed), self.repo)
        session._completion_verification, session._completion_verification_subject = _receipt()
        session._completion_observed_test_count = observed
        session._append_verification_record()
        read = self.store.read(EventRange(run_id="run-t134"))
        return _payload(list(read.value or ()), "VerificationRecorded")

    def test_a_reported_count_is_bound_verbatim(self) -> None:
        self.assertEqual(self._emit_with(7)["observedTestCount"], 7)

    def test_an_observed_zero_is_recorded_as_zero_not_null(self) -> None:
        payload = self._emit_with(0)
        self.assertEqual(payload["observedTestCount"], 0)
        self.assertIsNotNone(
            payload["observedTestCount"],
            "a runner that reported running zero tests is a known fact, not unknown")

    def test_an_unreported_count_is_recorded_as_null(self) -> None:
        self.assertIsNone(self._emit_with(None)["observedTestCount"])

    def test_the_parser_is_what_separates_the_two(self) -> None:
        """The distinction is derived from the runner text, not invented."""
        from vanguard.packages.runtime.session import parse_observed_test_counts

        self.assertEqual(parse_observed_test_counts("Ran 0 tests in 0.000s\nOK").executed, 0)
        self.assertEqual(parse_observed_test_counts("Ran 7 tests in 0.1s\nOK").executed, 7)
        # No runner summary at all: unknown, and never invented as zero.
        self.assertIsNone(parse_observed_test_counts("some unrelated output").executed)
        self.assertIsNone(parse_observed_test_counts("").executed)

    def test_both_values_validate_against_the_typed_payload(self) -> None:
        """ADVERSARIAL: zero must be admissible under the schema, not just in
        Python. A payload def that required a positive integer, or forbade
        null, would make one of these two facts unrepresentable on the wire."""
        from jsonschema import Draft202012Validator

        allocation = json.loads(
            (ROOT / "schemas/mhf/event_envelope.schema.json").read_text())
        schema = allocation["$defs"]["VerificationRecordedPayload"]
        for observed in (0, None, 7):
            with self.subTest(observed=observed):
                payload = dict(self._emit_with(observed))
                errors = list(Draft202012Validator(schema).iter_errors(payload))
                self.assertEqual(errors, [], f"{observed!r}: {errors}")
        # And a negative count stays invalid.
        bad = dict(self._emit_with(7))
        bad["observedTestCount"] = -1
        self.assertNotEqual(
            list(Draft202012Validator(schema).iter_errors(bad)), [])


class TheEngineSeamDoesNotSwallowTheFailure(unittest.TestCase):
    """NT-1.6, the half a green suite cannot show: the raise must escape.

    The latch is the backstop, not the mechanism. `_observe_completion_dispatch`
    runs inside `_admit_turn_result`, which `EpisodeEngine` invokes as its
    `receipt_labeller` with no `try`/`except` around the call
    (`agency/episode/engine.py:690`, `:801`). If that seam swallowed the
    carrier append failure, the turn would report a receipt for evidence the
    ledger never accepted, and progress would stop only at the *following*
    boundary. This test pins the seam itself.
    """

    def test_admit_turn_result_propagates_an_on_dispatch_failure(self) -> None:
        from vanguard.packages.runtime.session import _admit_turn_result

        class _Operator:
            def __init__(self) -> None:
                self._completion_calls = [(_request(), object())]
                self._model = object()
                self.notes: list[str] = []

            def note(self, **kwargs: Any) -> None:
                self.notes.append(kwargs.get("label", ""))

        operator = _Operator()

        def _raising(request: Any, result: Any) -> None:
            raise RuntimeError("ChangeSurfaceUpdated: disk full")

        with self.assertRaises(RuntimeError) as raised:
            _admit_turn_result(operator, 0, object(), on_dispatch=_raising)
        self.assertIn("ChangeSurfaceUpdated", str(raised.exception))
        # The turn produced no receipt note: nothing downstream can read a
        # label for a fact that never landed.
        self.assertEqual(operator.notes, [])

    def test_the_seam_still_labels_a_turn_when_nothing_failed(self) -> None:
        """ADVERSARIAL: a seam that raised unconditionally would also pass."""
        from vanguard.packages.runtime.session import _admit_turn_result

        class _Operator:
            def __init__(self) -> None:
                self._completion_calls = [(_request(), object())]
                self._model = object()
                self.notes: list[str] = []

            def note(self, **kwargs: Any) -> None:
                self.notes.append(kwargs.get("label", ""))

        operator = _Operator()
        observed: list[Any] = []
        result = type("R", (), {
            "outcome": type("O", (), {"result_digest": "sha256:" + "7" * 64,
                                      "detail": "ok"})(),
            "detail": "ok"})()
        span = _admit_turn_result(
            operator, 3, result, on_dispatch=lambda req, res: observed.append(req))
        self.assertEqual(len(observed), 1)
        self.assertEqual(operator.notes, ["tool-result-3"])
        self.assertIsNotNone(span)


class TheCarriersSurviveACloseAndReopen(unittest.TestCase):
    """A real SQLite file, closed and reopened. Nothing in memory carries over."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.db = str(self.repo / "ledger.sqlite3")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_then_reopen(self, *, verification_workspace: str = POSTIMAGE_DIGEST,
                           verify_first: bool = False) -> Any:
        store = SqliteEventStore(self.db)
        session = _SessionUnderTest(_emitter(store), self.repo)
        receipt, subject = _receipt(workspace=verification_workspace)
        if verify_first:
            session._completion_verification = receipt
            session._completion_verification_subject = subject
            session._append_verification_record()
            _write_surface(session, self.repo)
        else:
            _write_surface(session, self.repo)
            session._completion_verification = receipt
            session._completion_verification_subject = subject
            session._append_verification_record()
        store.close()
        del store, session

        reopened = SqliteEventStore(self.db)
        try:
            read = reopened.read(EventRange(run_id="run-t134"))
            return list(read.value or ())
        finally:
            reopened.close()

    def test_the_multi_file_surface_survives_with_its_deletion(self) -> None:
        events = self._write_then_reopen()
        payload = _payload(events, "ChangeSurfaceUpdated")
        self.assertEqual(payload["changeSurface"], SURFACE)
        self.assertEqual(payload["deletedPaths"], [DELETED])
        self.assertEqual(payload["taskDigest"], TASK_DIGEST)
        self.assertEqual(payload["candidateDigest"], POSTIMAGE_DIGEST)

        folded = fold_task_state(events, objective=OBJECTIVE).to_canonical_dict()
        self.assertEqual(sorted(folded["changeSurface"]), SURFACE)
        # The deleted path is a changed path. A resumed planner that never saw
        # it would propose the delete again.
        self.assertIn(DELETED, folded["modifiedFiles"])

    def test_the_verification_survives_with_every_binding(self) -> None:
        events = self._write_then_reopen()
        payload = _payload(events, "VerificationRecorded")
        self.assertEqual(payload["argv"], list(ARGV))
        self.assertEqual(payload["exitCode"], 0)
        self.assertEqual(payload["observedTestCount"], 5)
        self.assertEqual(payload["taskDigest"], TASK_DIGEST)
        self.assertEqual(payload["compositionDigest"], COMPOSITION_DIGEST)
        self.assertEqual(payload["workspaceDigest"], POSTIMAGE_DIGEST)

        folded = fold_task_state(events, objective=OBJECTIVE).to_canonical_dict()
        self.assertEqual(folded["lastVerification"]["argv"], list(ARGV))
        self.assertEqual(folded["lastVerification"]["exitCode"], 0)

    def test_the_carriers_are_written_as_slash_two_envelopes(self) -> None:
        events = self._write_then_reopen()
        for kind in ("VerificationRecorded", "ChangeSurfaceUpdated"):
            envelope = next(e for e in events
                            if (e.payload or {}).get("kind") == kind)
            self.assertEqual(envelope.schema_version, "mhf.event/2")
            self.assertEqual(envelope.authority_source, "kernel-capability")

    def test_a_stale_receipt_does_not_survive_as_applicable_evidence(self) -> None:
        """No stale receipt admits completion.

        The verification ran over `PREIMAGE_DIGEST`; the surface then settled a
        candidate at `POSTIMAGE_DIGEST`. The receipt attests a postimage that
        no longer exists, so replay must not present it as the applicable
        verification.
        """
        events = self._write_then_reopen(
            verification_workspace=PREIMAGE_DIGEST, verify_first=True)
        self.assertIn("VerificationRecorded", _kinds(events))
        folded = fold_task_state(events, objective=OBJECTIVE).to_canonical_dict()
        self.assertEqual(folded["lastVerification"], {})

    def test_a_current_receipt_is_still_applicable(self) -> None:
        """ADVERSARIAL: the staleness rule must not discard every receipt.

        Same ordering, same code path -- only the postimage the receipt was
        bound to matches. A rule that dropped the receipt here would make the
        test above vacuous.
        """
        events = self._write_then_reopen(
            verification_workspace=POSTIMAGE_DIGEST, verify_first=True)
        folded = fold_task_state(events, objective=OBJECTIVE).to_canonical_dict()
        self.assertEqual(folded["lastVerification"]["workspaceDigest"],
                         POSTIMAGE_DIGEST)

    def test_no_duplicate_effect_or_carrier_after_reopen(self) -> None:
        events = self._write_then_reopen()
        kinds = _kinds(events)
        self.assertEqual(kinds.count("ChangeSurfaceUpdated"), 1)
        self.assertEqual(kinds.count("VerificationRecorded"), 1)

    def test_an_old_ledger_without_carriers_still_folds(self) -> None:
        """Retained old-ledger compatibility.

        A ledger written before DIR-D1 has neither carrier. It must fold into
        the same shape, with an empty surface rather than an error.
        """
        store = SqliteEventStore(self.db)
        emitter = _emitter(store)
        emitter.emit_kind(
            "EffectCompleted", run_id="run-t134", principal="agent-1",
            episode_id="ep-t134", writer="kernel",
            payload={"action": "patch.apply", "path": MODIFIED,
                     "descriptorDigest": "sha256:" + "d" * 64})
        store.close()

        reopened = SqliteEventStore(self.db)
        try:
            events = list(reopened.read(EventRange(run_id="run-t134")).value or ())
        finally:
            reopened.close()
        folded = fold_task_state(events, objective=OBJECTIVE).to_canonical_dict()
        self.assertEqual(folded["modifiedFiles"], [MODIFIED])
        self.assertEqual(folded["changeSurface"], [])
        self.assertEqual(folded["lastVerification"], {})


_WRITER = r'''
import os, sys, json
from pathlib import Path
sys.path.insert(0, sys.argv[3])
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter
from test.runtime.test_task_state_durable_carriers import (
    _SessionUnderTest, _receipt, _write_surface, _emitter)

db, repo = sys.argv[1], Path(sys.argv[2])
store = SqliteEventStore(db)
session = _SessionUnderTest(_emitter(store), repo)
_write_surface(session, repo)
session._completion_verification, session._completion_verification_subject = _receipt()
session._append_verification_record()
# Hard death. No close, no flush, no terminal event: whatever the resumer
# reads is what the WAL durably held.
os._exit(91)
'''

_RESUMER = r'''
import json, sys
sys.path.insert(0, sys.argv[2])
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.task_state import fold_task_state

store = SqliteEventStore(sys.argv[1])
events = list(store.read(EventRange(run_id="run-t134")).value or ())
print(json.dumps({
    "kinds": [(getattr(e, "payload", {}) or {}).get("kind") for e in events],
    "state": fold_task_state(events, objective=sys.argv[3]).to_canonical_dict(),
}))
store.close()
'''


class AFreshProcessReconstructsBothFacts(unittest.TestCase):
    """A separate interpreter, a file-backed WAL, and a hard exit."""

    def test_a_fresh_interpreter_recovers_the_surface_and_the_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            db = str(repo / "row.sqlite3")
            env = {**os.environ, "PYTHONPATH": str(ROOT)}
            crashed = subprocess.run(
                [sys.executable, "-c", _WRITER, db, str(repo), str(ROOT)],
                cwd=ROOT, env=env, check=False, capture_output=True, text=True)
            self.assertEqual(crashed.returncode, 91,
                             (crashed.stdout or "") + (crashed.stderr or ""))
            resumed = subprocess.run(
                [sys.executable, "-c", _RESUMER, db, str(ROOT), OBJECTIVE],
                cwd=ROOT, env=env, check=False, capture_output=True, text=True)
            self.assertEqual(resumed.returncode, 0,
                             (resumed.stdout or "") + (resumed.stderr or ""))
            observed = json.loads(resumed.stdout.strip().splitlines()[-1])

        self.assertIn("ChangeSurfaceUpdated", observed["kinds"])
        self.assertIn("VerificationRecorded", observed["kinds"])
        state = observed["state"]
        self.assertEqual(sorted(state["changeSurface"]), SURFACE)
        self.assertIn(DELETED, state["modifiedFiles"])
        self.assertEqual(state["lastVerification"]["argv"], list(ARGV))
        self.assertEqual(state["lastVerification"]["exitCode"], 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
