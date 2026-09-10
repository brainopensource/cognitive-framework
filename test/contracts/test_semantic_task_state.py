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


if __name__ == "__main__":
    unittest.main()
