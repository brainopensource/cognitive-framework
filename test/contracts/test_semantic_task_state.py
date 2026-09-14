"""T-09 / T-100: SemanticTaskState plus versioned memory-view and recovery values."""

from __future__ import annotations

import importlib
import unittest

from vanguard.packages.agency.episode.protocol_recovery import (
    Attempt,
    FailureClass,
    ProtocolRecoveryState,
    RecoveryDecision,
    RecoveryState,
    SemanticRecoveryDecision,
)
from vanguard.packages.domain.canonicalisation.digest import digest_bytes, digest_of
from vanguard.packages.domain.canonicalisation.jcs import canonical_bytes, canonicalise, parse_json_text
from vanguard.packages.domain.task_state import (
    CodingTaskState,
    Evidence,
    MemoryView,
    SemanticTaskState,
    StepState,
    TaskStep,
    TaskRevision,
    TASK_MUTABLE_FIELDS,
    TASK_REVISION_CONFLICTING,
    TASK_REVISION_MALFORMED,
    TASK_REVISION_STALE,
    TASK_REVISION_WIDENING,
    validate_revision_invariants,
)

_DIGEST_A = "sha256:" + "a" * 64
_DIGEST_B = "sha256:" + "b" * 64
_DIGEST_C = "sha256:" + "c" * 64
_MEMORY_SCHEMA = "aether.memory-view/1"
_RECOVERY_SCHEMA = "aether.recovery-state/1"


def _task(**overrides: object) -> SemanticTaskState:
    values: dict[str, object] = {
        "objective": "repair parser",
        "run_id": "run-1",
        "revision": 2,
        "task_class": "bugfix",
        "last_verification": {"nested": {"count": 1}, "ok": True},
        "remaining_budgets": {"turns": 4},
        "recovery_state": {"inner": {"spent": 1}},
    }
    values.update(overrides)
    return SemanticTaskState(**values)  # type: ignore[arg-type]


class TestSemanticTaskState(unittest.TestCase):
    def test_module_is_stdlib_plus_jcs(self) -> None:
        module = importlib.import_module("vanguard.packages.domain.task_state")
        forbidden = {
            name
            for name, value in vars(module).items()
            if getattr(value, "__module__", "").startswith(
                ("vanguard.packages.runtime", "vanguard.packages.adapters",
                 "vanguard.packages.agency", "vanguard.packages.kernel")
            )
        }
        self.assertEqual(forbidden, set())

    def test_coding_task_state_is_the_same_schema(self) -> None:
        self.assertIs(CodingTaskState, SemanticTaskState)

    def test_jcs_round_trip_and_digest_are_stable(self) -> None:
        state = SemanticTaskState(
            objective="repair parser",
            run_id="run-1",
            revision=2,
            backlog=(TaskStep("step-001", "inspect parser", ("src/parser.py",)),),
            falsified_hypotheses=("regex-only repair",),
            settled_invariants=("parser is hand-written",),
            changed_files_tree_hash="sha256:" + "a" * 64,
            task_class="bugfix",
        )
        restored = SemanticTaskState.from_mapping(state.to_canonical_dict())
        self.assertEqual(restored, state)
        self.assertEqual(canonicalise(state.to_canonical_dict()),
                         canonicalise(restored.to_canonical_dict()))
        self.assertEqual(state.digest(), restored.digest())
        self.assertEqual(state.overarching_goal, "repair parser")

    def test_task_step_and_step_state_are_immutable_values(self) -> None:
        step = TaskStep("step-001", "inspect", ("a.py",), state=StepState.READY)
        self.assertEqual(step.state, StepState.READY)
        with self.assertRaises(AttributeError):
            step.title = "mutated"  # type: ignore[misc]

    def test_empty_objective_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            SemanticTaskState("")


class TestMemoryViewContract(unittest.TestCase):
    def test_capture_encode_decode_bytes_are_deterministic(self) -> None:
        task = _task()
        evidence = (
            Evidence("ev-1", _DIGEST_A, _DIGEST_B, "parser is hand-written", "body"),
        )
        view = MemoryView.capture(
            task, 3, lineage_id="lin-1", reducer_version="task-fold/1", evidence=evidence,
        )
        payload = view.encode()
        digest = digest_bytes(payload)
        restored = MemoryView.decode(payload, digest)
        self.assertEqual(payload, restored.encode())
        self.assertEqual(digest, digest_bytes(restored.encode()))
        self.assertEqual(canonical_bytes(view.task.to_canonical_dict()), view.task_bytes)
        self.assertEqual(restored.cursor, 3)
        self.assertEqual(restored.lineage_id, "lin-1")
        self.assertEqual(restored.reducer_version, "task-fold/1")
        self.assertEqual(restored.task, task)
        self.assertEqual(restored.evidence, evidence)
        raw = parse_json_text(payload.decode("utf-8"))
        self.assertEqual(raw["schema"], _MEMORY_SCHEMA)
        self.assertEqual(MemoryView.decode(payload, digest).encode(), payload)

    def test_nested_map_mutation_cannot_alter_captured_bytes(self) -> None:
        last_verification = {"nested": {"count": 1}, "ok": True}
        remaining = {"turns": 4}
        recovery = {"inner": {"spent": 1}}
        task = _task(
            last_verification=last_verification,
            remaining_budgets=remaining,
            recovery_state=recovery,
        )
        view = MemoryView.capture(
            task, 0, lineage_id="lin-1", reducer_version="task-fold/1",
        )
        before = view.encode()
        identity = digest_bytes(before)
        last_verification["nested"]["count"] = 99
        last_verification["ok"] = False
        remaining["turns"] = 0
        recovery["inner"]["spent"] = 8
        # The captured bytes are stable, and so is the state that produced
        # them: the constructor detached every nested container, so none of
        # the edits above reaches the value the digest was taken over.
        self.assertEqual(task.last_verification["nested"]["count"], 1)
        self.assertTrue(task.last_verification["ok"])
        self.assertEqual(task.remaining_budgets["turns"], 4)
        self.assertEqual(task.recovery_state["inner"]["spent"], 1)
        # And the top level refuses the write outright rather than accepting
        # one that silently diverges from the captured identity.
        with self.assertRaises(TypeError):
            task.last_verification["extra"] = "live"  # type: ignore[index]
        self.assertEqual(view.encode(), before)
        self.assertEqual(digest_bytes(view.encode()), identity)
        reconstructed = view.task
        reconstructed.last_verification["nested"]["count"] = 7  # type: ignore[index]
        self.assertEqual(view.encode(), before)
        self.assertEqual(view.task.last_verification["nested"]["count"], 1)

    def test_unknown_schema_version_fails_closed(self) -> None:
        view = MemoryView.capture(
            _task(), 1, lineage_id="lin-1", reducer_version="task-fold/1",
        )
        raw = parse_json_text(view.encode().decode("utf-8"))
        raw["schema"] = "aether.memory-view/2"
        payload = canonical_bytes(raw)
        with self.assertRaises(ValueError):
            MemoryView.decode(payload, digest_bytes(payload))

    def test_malformed_digests_fail_closed(self) -> None:
        for bad in ("sha256:not-hex", "sha256:" + "A" * 64, "sha256:" + "a" * 63, "md5:" + "a" * 32, "a" * 64):
            with self.subTest(digest=bad):
                with self.assertRaises(ValueError):
                    Evidence("ev-1", bad, _DIGEST_B, "finding")
                with self.assertRaises(ValueError):
                    Evidence("ev-1", _DIGEST_A, bad, "finding")

    def test_duplicate_evidence_keys_fail_closed(self) -> None:
        evidence = (
            Evidence("dup", _DIGEST_A, _DIGEST_B, "one"),
            Evidence("dup", _DIGEST_B, _DIGEST_C, "two"),
        )
        with self.assertRaises(ValueError):
            MemoryView.capture(
                _task(), 0, lineage_id="lin-1", reducer_version="task-fold/1",
                evidence=evidence,
            )

    def test_negative_and_bool_cursor_fail_closed(self) -> None:
        task = _task()
        with self.assertRaises(ValueError):
            MemoryView.capture(task, -1, lineage_id="lin-1", reducer_version="task-fold/1")
        with self.assertRaises(ValueError):
            MemoryView.capture(task, True, lineage_id="lin-1", reducer_version="task-fold/1")  # type: ignore[arg-type]

    def test_direct_bytearray_and_list_inputs_are_snapshotted(self) -> None:
        task = _task()
        raw_bytes = bytearray(canonical_bytes(task.to_canonical_dict()))
        evidence = [Evidence("ev-1", _DIGEST_A, _DIGEST_B, "finding")]
        view = MemoryView(
            task_bytes=raw_bytes,
            cursor=2,
            lineage_id="lin-1",
            reducer_version="task-fold/1",
            evidence=evidence,
        )
        before = view.encode()
        identity = digest_bytes(before)
        raw_bytes[0] ^= 0x01
        evidence.append(Evidence("ev-2", _DIGEST_B, _DIGEST_C, "other"))
        self.assertEqual(view.encode(), before)
        self.assertEqual(digest_bytes(view.encode()), identity)
        self.assertEqual(len(view.evidence), 1)
        self.assertIsInstance(view.task_bytes, bytes)
        payload = bytearray(before)
        restored = MemoryView.decode(payload, identity)
        payload[0] ^= 0x01
        self.assertEqual(restored.encode(), before)


class TestRecoveryStateContract(unittest.TestCase):
    def test_versioned_round_trip_is_byte_stable_and_preserves_ceilings(self) -> None:
        fingerprint = digest_of({"action": "patch.apply"})
        progress = digest_of({"progress": "new-fact"})
        policy = digest_of({"maxTransportRetries": 3})
        state = ProtocolRecoveryState(
            transport_retries=1,
            protocol_retries=2,
            truncation_retries=1,
            effect_retries=0,
            max_transport_retries=3,
            max_protocol_retries=4,
            max_truncation_retries=2,
            max_effect_retries=5,
            attempted_fingerprints=(fingerprint,),
            spent_decisions=("retry",),
            policy_digest=policy,
            history=(Attempt(fingerprint, "retry", progress, FailureClass.PATCH.value),),
            errors={FailureClass.PATCH.value: 1, FailureClass.TRANSPORT.value: 0},
            interventions=1,
            decisions=2,
        )
        payload = state.encode()
        restored = ProtocolRecoveryState.decode(payload)
        self.assertEqual(restored.encode(), payload)
        self.assertEqual(restored, state)
        raw = parse_json_text(payload.decode("utf-8"))
        self.assertEqual(raw["schema"], _RECOVERY_SCHEMA)
        self.assertEqual(restored.max_transport_retries, 3)
        self.assertEqual(restored.max_protocol_retries, 4)
        self.assertEqual(restored.max_truncation_retries, 2)
        self.assertEqual(restored.max_effect_retries, 5)
        self.assertEqual(restored.attempted_fingerprints, (fingerprint,))
        self.assertEqual(restored.spent_decisions, ("retry",))

    def test_legacy_dictionary_migrates_without_resetting_or_replaying(self) -> None:
        fingerprint = digest_of({"action": "fs.write"})
        legacy = {
            "transportRetries": 1,
            "protocolRetries": 2,
            "truncationRetries": 0,
            "effectRetries": 1,
            "attemptedFingerprints": [fingerprint],
            "spentDecisions": ["no_retry"],
        }
        migrated = ProtocolRecoveryState.from_dict(legacy)
        self.assertEqual(migrated.transport_retries, 1)
        self.assertEqual(migrated.protocol_retries, 2)
        self.assertEqual(migrated.truncation_retries, 0)
        self.assertEqual(migrated.effect_retries, 1)
        self.assertEqual(migrated.max_transport_retries, 2)
        self.assertEqual(migrated.max_protocol_retries, 2)
        self.assertEqual(migrated.max_truncation_retries, 1)
        self.assertEqual(migrated.max_effect_retries, 2)
        self.assertEqual(migrated.attempted_fingerprints, (fingerprint,))
        self.assertEqual(migrated.spent_decisions, ("no_retry",))
        again = ProtocolRecoveryState.from_dict(migrated.to_dict())
        self.assertEqual(again.spent_decisions, ("no_retry",))
        self.assertEqual(again.attempted_fingerprints, (fingerprint,))
        self.assertEqual(again.transport_retries, 1)
        self.assertNotIn("consult", again.spent_decisions)
        self.assertEqual(RecoveryState, ProtocolRecoveryState)
        decision = RecoveryDecision(status="accept")
        self.assertEqual(decision.action, "accept")
        self.assertEqual(decision.reason, "ok")

    def test_legacy_explicit_nondefault_ceilings_are_preserved(self) -> None:
        fingerprint = digest_of({"action": "patch.apply"})
        legacy = {
            "transportRetries": 1,
            "protocolRetries": 0,
            "truncationRetries": 0,
            "effectRetries": 0,
            "maxTransportRetries": 7,
            "maxProtocolRetries": 9,
            "maxTruncationRetries": 4,
            "maxEffectRetries": 6,
            "attemptedFingerprints": [fingerprint],
            "spentDecisions": ["retry"],
        }
        migrated = ProtocolRecoveryState.from_dict(legacy)
        self.assertEqual(migrated.max_transport_retries, 7)
        self.assertEqual(migrated.max_protocol_retries, 9)
        self.assertEqual(migrated.max_truncation_retries, 4)
        self.assertEqual(migrated.max_effect_retries, 6)
        self.assertEqual(migrated.transport_retries, 1)
        self.assertEqual(migrated.attempted_fingerprints, (fingerprint,))
        self.assertEqual(migrated.spent_decisions, ("retry",))

    def test_direct_list_inputs_are_snapshotted(self) -> None:
        fingerprint = digest_of({"action": "fs.read"})
        fingerprints = [fingerprint]
        spent = ["retry"]
        history = [Attempt(fingerprint, "retry", fingerprint, None)]
        errors = {FailureClass.TOOL.value: 1}
        state = ProtocolRecoveryState(
            attempted_fingerprints=fingerprints,
            spent_decisions=spent,
            history=history,
            errors=errors,
        )
        fingerprints.append(digest_of({"action": "other"}))
        spent.append("stop")
        history.append(Attempt(digest_of({"action": "other"}), "stop", fingerprint, None))
        errors[FailureClass.TOOL.value] = 9
        self.assertEqual(state.attempted_fingerprints, (fingerprint,))
        self.assertEqual(state.spent_decisions, ("retry",))
        self.assertEqual(len(state.history), 1)
        self.assertEqual(state.errors[FailureClass.TOOL.value], 1)

    def test_unknown_recovery_schema_fails_closed(self) -> None:
        raw = ProtocolRecoveryState().to_dict()
        raw["schema"] = "aether.recovery-state/2"
        with self.assertRaises(ValueError):
            ProtocolRecoveryState.from_dict(raw)

    def test_malformed_recovery_digests_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            ProtocolRecoveryState(policy_digest="sha256:nope")
        with self.assertRaises(ValueError):
            Attempt("sha256:short", "retry", _DIGEST_A)
        with self.assertRaises(ValueError):
            Attempt(_DIGEST_A, "retry", "sha256:" + "A" * 64)

    def test_negative_and_bool_counters_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            ProtocolRecoveryState(transport_retries=-1)
        with self.assertRaises(ValueError):
            ProtocolRecoveryState(protocol_retries=True)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            ProtocolRecoveryState(errors={FailureClass.TOOL.value: -1})
        with self.assertRaises(ValueError):
            ProtocolRecoveryState(errors={FailureClass.TOOL.value: True})  # type: ignore[dict-item]
        with self.assertRaises(ValueError):
            ProtocolRecoveryState.from_dict({"transportRetries": True})
        with self.assertRaises(ValueError):
            ProtocolRecoveryState.from_dict({"effectRetries": -2})

    def test_oversized_history_fails_closed(self) -> None:
        fingerprints = tuple(digest_of({"i": i}) for i in range(13))
        with self.assertRaises(ValueError):
            ProtocolRecoveryState(attempted_fingerprints=fingerprints)
        history = tuple(
            Attempt(digest_of({"i": i}), "retry", digest_of({"p": i}))
            for i in range(13)
        )
        with self.assertRaises(ValueError):
            ProtocolRecoveryState(history=history)
        state = ProtocolRecoveryState()
        for i in range(12):
            state = state.record_attempt(digest_of({"bound": i}), "retry")
        with self.assertRaises(ValueError):
            state.record_attempt(digest_of({"bound": 12}), "retry")

    def test_pending_operation_requires_deadline(self) -> None:
        with self.assertRaises(ValueError):
            ProtocolRecoveryState(pending_operation="call-1")
        with self.assertRaises(ValueError):
            ProtocolRecoveryState(deadline="2026-09-10T00:00:00.000Z")
        held = ProtocolRecoveryState(
            pending_operation="call-1", deadline="2026-09-10T00:00:00.000Z",
        )
        self.assertEqual(held.pending_operation, "call-1")

    def test_incomplete_versioned_payload_fails_closed(self) -> None:
        raw = ProtocolRecoveryState().to_dict()
        for key in ("policyDigest", "history", "errors", "interventions", "decisions",
                    "pendingOperation", "deadline"):
            incomplete = dict(raw)
            incomplete.pop(key)
            with self.subTest(missing=key):
                with self.assertRaises(ValueError):
                    ProtocolRecoveryState.from_dict(incomplete)

    def test_inconsistent_history_and_legacy_fields_fail_closed(self) -> None:
        fingerprint = digest_of({"action": "patch.apply"})
        other = digest_of({"action": "other"})
        state = ProtocolRecoveryState(
            attempted_fingerprints=(fingerprint,),
            spent_decisions=("retry",),
            history=(Attempt(fingerprint, "retry", fingerprint, None),),
        )
        raw = state.to_dict()
        mismatched = dict(raw)
        mismatched["attemptedFingerprints"] = [other]
        with self.assertRaises(ValueError):
            ProtocolRecoveryState.from_dict(mismatched)
        mismatched_spent = dict(raw)
        mismatched_spent["spentDecisions"] = ["stop"]
        with self.assertRaises(ValueError):
            ProtocolRecoveryState.from_dict(mismatched_spent)

    def test_semantic_recovery_decision_round_trips_without_consult(self) -> None:
        decision = SemanticRecoveryDecision(
            action="reground",
            reason="no_progress",
            delay_ms=250,
            state_digest=_DIGEST_A,
            remaining_budget_ref=_DIGEST_B,
        )
        restored = SemanticRecoveryDecision.decode(decision.encode())
        self.assertEqual(restored, decision)
        self.assertEqual(restored.action, "reground")
        self.assertEqual(restored.delay_ms, 250)
        protocol = RecoveryDecision(status="retry_model", retry_reason="OUTPUT_TRUNCATED")
        self.assertEqual(protocol.action, "retry_model")
        self.assertNotEqual(protocol.action, restored.action)
        with self.assertRaises(ValueError):
            SemanticRecoveryDecision(
                action="consult",
                reason="ask-specialist",
                delay_ms=0,
                state_digest=_DIGEST_A,
                remaining_budget_ref=_DIGEST_B,
            )
        with self.assertRaises(ValueError):
            SemanticRecoveryDecision(
                action="stop",
                reason="budget",
                delay_ms=True,  # type: ignore[arg-type]
                state_digest=_DIGEST_A,
                remaining_budget_ref=_DIGEST_B,
            )


def _make_revision(
    *,
    revision_id: str = "rev-001",
    target_binding: tuple[str, str, str, str] = ("run-1", "ep-1", "turn-1", "prop-1"),
    expected_revision: int = 2,
    expected_state_digest: str = _DIGEST_A,
    mutated_fields: tuple[TaskMutableField, ...] = ("plan",),
    proposed_state: SemanticTaskState | None = None,
    authority_proof: str = "authenticated-dispatch",
) -> TaskRevision:
    if proposed_state is None:
        proposed_state = _task(revision=expected_revision + 1)
    return TaskRevision(
        revision_id=revision_id,
        target_binding=target_binding,
        expected_revision=expected_revision,
        expected_state_digest=expected_state_digest,
        mutated_fields=mutated_fields,
        proposed_state=proposed_state,
        authority_proof=authority_proof,
    )


class TestTaskRevisionContract(unittest.TestCase):
    def test_mutable_fields_specification(self) -> None:
        self.assertEqual(
            TASK_MUTABLE_FIELDS,
            frozenset({
                "plan",
                "strategy_steps",
                "hypotheses",
                "verification_plan",
                "next_action",
                "active_step_id",
                "backlog",
            }),
        )

    def test_task_revision_dataclass_and_canonical_round_trip(self) -> None:
        proposed = _task(
            revision=3,
            plan=("step 1: inspect", "step 2: test"),
            next_action="step 1: inspect",
        )
        revision = _make_revision(
            revision_id="rev-001",
            expected_revision=2,
            expected_state_digest=_DIGEST_A,
            mutated_fields=("plan", "next_action"),
            proposed_state=proposed,
        )
        canonical = revision.to_canonical_dict()
        self.assertEqual(canonical["revisionId"], "rev-001")
        self.assertEqual(canonical["expectedRevision"], 2)
        self.assertEqual(canonical["expectedStateDigest"], _DIGEST_A)
        self.assertEqual(canonical["mutatedFields"], ["plan", "next_action"])

        restored = TaskRevision.from_mapping(canonical)
        self.assertEqual(restored, revision)
        self.assertEqual(restored.digest(), revision.digest())
        self.assertTrue(revision.digest().startswith("sha256:"))

    def test_task_revision_is_frozen_value_object(self) -> None:
        revision = _make_revision()
        with self.assertRaises(AttributeError):
            revision.revision_id = "rev-002"  # type: ignore[misc]
        with self.assertRaises(AttributeError):
            revision.authority_proof = "tampered"  # type: ignore[misc]

    def test_validate_revision_invariants_valid(self) -> None:
        state = _task(revision=2)
        proposed = _task(
            revision=3,
            plan=("p1", "p2"),
            strategy_steps=("s1",),
        )
        revision = _make_revision(
            revision_id="rev-valid-1",
            expected_revision=2,
            expected_state_digest=state.digest(),
            mutated_fields=("plan", "strategy_steps"),
            proposed_state=proposed,
        )
        ok, err_kind, err_msg = validate_revision_invariants(state, revision)
        self.assertTrue(ok)
        self.assertIsNone(err_kind)
        self.assertIsNone(err_msg)

    def test_validate_revision_invariants_refuses_stale_revision(self) -> None:
        state = _task(revision=5)
        # Sequence mismatch
        stale_seq = _make_revision(
            expected_revision=4,
            expected_state_digest=state.digest(),
            proposed_state=_task(revision=5),
        )
        ok, err, msg = validate_revision_invariants(state, stale_seq)
        self.assertFalse(ok)
        self.assertEqual(err, TASK_REVISION_STALE)

        # Digest mismatch
        stale_digest = _make_revision(
            expected_revision=5,
            expected_state_digest=_DIGEST_B,
            proposed_state=_task(revision=6),
        )
        ok2, err2, msg2 = validate_revision_invariants(state, stale_digest)
        self.assertFalse(ok2)
        self.assertEqual(err2, TASK_REVISION_STALE)

    def test_validate_revision_invariants_refuses_widening(self) -> None:
        state = _task(revision=2)
        # Attempt to widen objective
        widening_obj = _make_revision(
            expected_revision=2,
            expected_state_digest=state.digest(),
            proposed_state=_task(revision=3, objective="new unconstrained objective"),
        )
        ok, err, msg = validate_revision_invariants(state, widening_obj)
        self.assertFalse(ok)
        self.assertEqual(err, TASK_REVISION_WIDENING)

        # Attempt to widen remaining budgets
        widening_budget = _make_revision(
            expected_revision=2,
            expected_state_digest=state.digest(),
            proposed_state=_task(revision=3, remaining_budgets={"turns": 100}),
        )
        ok2, err2, msg2 = validate_revision_invariants(state, widening_budget)
        self.assertFalse(ok2)
        self.assertEqual(err2, TASK_REVISION_WIDENING)

    def test_validate_revision_invariants_refuses_malformed(self) -> None:
        state = _task(revision=2)
        # Empty revision_id fails at construction
        with self.assertRaises(ValueError):
            _make_revision(revision_id="")

        # Non-whitelisted mutated field fails at construction
        with self.assertRaises(ValueError):
            _make_revision(mutated_fields=("arbitrary_field",))  # type: ignore[arg-type]



if __name__ == "__main__":
    unittest.main()

