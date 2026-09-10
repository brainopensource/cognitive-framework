"""Unit tests for ProtocolRecoveryPolicy and AdmissionGate."""

from __future__ import annotations

import time
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from vanguard.packages.agency.episode.admission_gate import AdmissionGate, VerificationReceipt
from vanguard.packages.agency.episode.engine import EpisodeEngine
from vanguard.packages.agency.episode.protocol_recovery import (
    Attempt,
    FailureClass,
    ProtocolRecoveryPolicy,
    ProtocolRecoveryState,
    RecoveryState,
    decide_recovery,
    recover,
    semantic_attempt_fingerprint,
    semantic_progress_key,
)
from vanguard.packages.agency.episode.state import RunTermination
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.kernel.dispatch import DispatchResult
from vanguard.packages.kernel.model import FailurePath

from test.agency import doubles
from test.kernel import fakes


class TestProtocolRecoveryAndAdmissionGate(unittest.TestCase):

    def test_protocol_recovery_patch_required(self) -> None:
        policy = ProtocolRecoveryPolicy()
        state = RecoveryState()

        # Proposal with only conversational text when patch is required
        proposal = {"text": "I analyzed the issue.", "toolCalls": ()}
        decision = policy.evaluate(proposal, state, patch_required=True)

        self.assertEqual(decision.action, "retry_model")
        self.assertEqual(decision.reason, "PATCH_REQUIRED_BUT_TEXT_EMITTED")
        self.assertIn("patch.apply", decision.feedback_message or "")

    def test_permission_denial_has_zero_automatic_retries(self) -> None:
        policy = ProtocolRecoveryPolicy()
        decision, state = policy.decide_failure("permission denied", RecoveryState(), action="fs.write")
        self.assertEqual(policy.classify("permission denied"), FailureClass.PERMISSION)
        self.assertEqual(decision.status, "fail_instrument")
        self.assertEqual(state.spent_decisions, ("permission",))
        self.assertIsNotNone(state.last_decision)
        self.assertEqual(state.last_decision.action, "stop")
        self.assertEqual(state.last_decision.delay_ms, 0)
        self.assertNotEqual(state.last_decision.action, "wait")

    def test_unchanged_semantic_attempt_is_not_repeated_after_resume(self) -> None:
        policy = ProtocolRecoveryPolicy()
        fp = semantic_attempt_fingerprint("patch.apply", {"path": "a.py"}, "sha256:ws")
        resumed = RecoveryState().record_attempt(fp, "retry")
        decision, _ = policy.decide_failure(
            "hunk does not apply", resumed, action="patch.apply",
            arguments={"path": "a.py"}, workspace_digest="sha256:ws")
        self.assertEqual(decision.status, "fail_instrument")

    def test_admission_gate_write_preset(self) -> None:
        gate = AdmissionGate()

        # Proposal attempting exit without changed files on write preset
        verdict = gate.evaluate("vg-code-v090-react-control", changed_files=(), proposal={"text": "done"})
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "MISSING_SOURCE_PATCH")

        # Proposal with changed files
        verdict_ok = gate.evaluate(
            "vg-code-v090-react-control",
            changed_files=("lru/entry.py",),
            inspected_files=("lru/entry.py",),
            proposal={"text": "done"},
            verification=VerificationReceipt(
                0, 1, "sha256:workspace", task_digest="sha256:task",
                composition_digest="sha256:composition", receipt_digest="sha256:receipt",
                verification_command="python -m unittest",
                verification_subject_digest="sha256:subject",
            ),
            current_workspace_digest="sha256:workspace",
            current_task_digest="sha256:task",
            current_composition_digest="sha256:composition",
            current_verification_command="python -m unittest",
            current_verification_subject_digest="sha256:subject",
        )
        self.assertTrue(verdict_ok.admissible)

        foreign = gate.evaluate(
            "vg-code-v090-react-control", changed_files=("lru/entry.py",),
            inspected_files=("lru/entry.py",), proposal={"text": "done"},
            verification=VerificationReceipt(
                0, 1, "sha256:workspace", task_digest="sha256:other",
                composition_digest="sha256:composition", receipt_digest="sha256:receipt",
                verification_command="python -m unittest",
                verification_subject_digest="sha256:subject",
            ),
            current_workspace_digest="sha256:workspace", current_task_digest="sha256:task",
            current_composition_digest="sha256:composition",
            current_verification_command="python -m unittest",
            current_verification_subject_digest="sha256:subject",
        )
        self.assertEqual(foreign.reason, "VERIFICATION_FOREIGN_TASK")

    def test_admission_gate_read_only_preset(self) -> None:
        gate = AdmissionGate()
        verdict = gate.evaluate("vg-tutor-v090-v1-read-search", changed_files=(), proposal={"text": "summary"})
        self.assertTrue(verdict.admissible)


def _digest(label: str) -> str:
    return digest_of({"id": label})


def _attempt(label: str, *, progress: str, outcome: str = "ok", failure: str | None = None) -> Attempt:
    return Attempt(_digest(f"fp:{label}"), outcome, _digest(f"pk:{progress}"), failure)


def _recover(state: ProtocolRecoveryState, attempt: Attempt, **overrides: Any):
    kwargs = {
        "remaining_ms": 8_000,
        "remaining_turns": 8,
        "jitter": 0.0,
        "state_digest": _digest("state"),
        "remaining_budget_ref": _digest("budget"),
        "deadline": "2026-09-10T00:00:00.000Z",
    }
    kwargs.update(overrides)
    return recover(state, attempt, **kwargs)


class TestBoundedStallRecovery(unittest.TestCase):
    def test_six_action_window_detects_three_unchanged_signatures(self) -> None:
        prefix = tuple((_digest(str(i)), "ok", _digest(f"p{i}")) for i in range(3))
        repeated = (_digest("same-action"), "ok", _digest("same-progress"))
        decision = decide_recovery(
            prefix + (repeated, repeated, repeated),
            failure=None, interventions=0, transport_retries=0,
            remaining_turns=4, remaining_ms=4_000, jitter=0.0,
        )
        self.assertEqual(decision.action, "reground")
        self.assertEqual(decision.reason, "no_progress")

    def test_length_two_and_three_cycles_are_detected(self) -> None:
        ab = ((_digest("a"), "ok", _digest("p")), (_digest("b"), "ok", _digest("q")))
        two_cycle = ab + ab
        two = decide_recovery(
            two_cycle, failure=None, interventions=0, transport_retries=0,
            remaining_turns=4, remaining_ms=4_000, jitter=0.0,
        )
        self.assertEqual(two.action, "reground")
        abc = (
            (_digest("a"), "ok", _digest("p")),
            (_digest("b"), "ok", _digest("q")),
            (_digest("c"), "ok", _digest("r")),
        )
        three = decide_recovery(
            abc + abc, failure=None, interventions=0, transport_retries=0,
            remaining_turns=4, remaining_ms=4_000, jitter=0.0,
        )
        self.assertEqual(three.action, "reground")

    def test_new_evidence_permits_progress(self) -> None:
        state = ProtocolRecoveryState()
        for index in range(4):
            _, state = _recover(state, _attempt(f"read-{index}", progress=f"fact-{index}"))
        decision, state = _recover(state, _attempt("read-5", progress="new-hypothesis"))
        self.assertEqual(decision.action, "continue")
        self.assertEqual(decision.reason, "progress")
        self.assertEqual(state.last_decision.action, "continue")

    def test_one_reground_one_replan_then_stop(self) -> None:
        state = ProtocolRecoveryState()
        stalled = _attempt("patch.apply", progress="stuck", outcome="failed", failure="patch")
        first, state = _recover(state, stalled)
        self.assertEqual(first.action, "reground")
        self.assertEqual(state.interventions, 1)
        second, state = _recover(state, _attempt("patch.apply", progress="stuck", outcome="failed", failure="patch"))
        self.assertEqual(second.action, "replan")
        self.assertEqual(state.interventions, 2)
        third, state = _recover(state, _attempt("patch.apply", progress="stuck", outcome="failed", failure="patch"))
        self.assertEqual(third.action, "stop")
        self.assertEqual(third.reason, "intervention_limit")
        self.assertNotIn(third.action, {"consult", "retry_model"})

    def test_transient_wait_persists_delay_then_stops_at_three(self) -> None:
        state = ProtocolRecoveryState(max_transport_retries=3)
        transient = _attempt("model.complete", progress="none", outcome="timeout", failure="transport")
        wait, state = _recover(state, transient, jitter=1.0)
        self.assertEqual(wait.action, "wait")
        self.assertGreater(wait.delay_ms, 0)
        self.assertEqual(state.transport_retries, 1)
        self.assertEqual(state.pending_operation, transient.fingerprint)
        self.assertEqual(state.deadline, "2026-09-10T00:00:00.000Z")
        restored = ProtocolRecoveryState.decode(state.encode())
        self.assertEqual(restored.transport_retries, 1)
        self.assertEqual(restored.deadline, state.deadline)
        self.assertEqual(restored.last_decision.delay_ms, wait.delay_ms)
        _, state = _recover(restored, transient, jitter=1.0)
        _, state = _recover(state, transient, jitter=1.0)
        self.assertEqual(state.transport_retries, 3)
        stop, state = _recover(state, transient, jitter=1.0)
        self.assertEqual(stop.action, "stop")
        self.assertEqual(state.transport_retries, 3)

    def test_counters_decisions_deadlines_fingerprints_and_budget_survive_restart(self) -> None:
        first = _attempt("fs.read", progress="fact-1")
        decision, state = _recover(
            ProtocolRecoveryState(),
            first,
            remaining_ms=1_500,
            remaining_turns=5,
        )
        self.assertEqual(decision.action, "continue")
        payload = state.encode()
        restored = ProtocolRecoveryState.decode(payload)
        self.assertEqual(restored.encode(), payload)
        self.assertEqual(restored.transport_retries, state.transport_retries)
        self.assertEqual(restored.decisions, 1)
        self.assertEqual(restored.attempted_fingerprints, (first.fingerprint,))
        self.assertEqual(restored.history[0].progress_key, first.progress_key)
        self.assertEqual(restored.last_decision.remaining_budget_ref, _digest("budget"))
        self.assertEqual(restored.last_decision.state_digest, _digest("state"))
        mutated = bytearray(payload)
        mutated[-4] ^= 0x01
        with self.assertRaises(ValueError):
            ProtocolRecoveryState.decode(bytes(mutated))

    def test_permission_never_waits_or_sleeps_into_authorization(self) -> None:
        denied = _attempt("fs.write", progress="none", outcome="denied", failure="permission")
        decision, state = _recover(ProtocolRecoveryState(), denied, remaining_ms=8_000, jitter=1.0)
        self.assertEqual(decision.action, "stop")
        self.assertEqual(decision.delay_ms, 0)
        self.assertEqual(decision.reason, "permission")
        self.assertIsNone(state.pending_operation)
        with self.assertRaises(ValueError):
            decide_recovery(
                ((denied.fingerprint, denied.outcome, denied.progress_key),),
                failure="consult", interventions=0, transport_retries=0,
                remaining_turns=3, remaining_ms=3_000, jitter=0.0,
            )

    def test_budget_and_zero_remainder_stop_without_consult(self) -> None:
        attempt = _attempt("proc.exec", progress="none", failure="budget")
        decision, _ = _recover(ProtocolRecoveryState(), attempt)
        self.assertEqual(decision.action, "stop")
        exhausted = decide_recovery(
            ((attempt.fingerprint, "ok", attempt.progress_key),),
            failure=None, interventions=0, transport_retries=0,
            remaining_turns=0, remaining_ms=5_000, jitter=0.0,
        )
        self.assertEqual(exhausted.action, "stop")
        self.assertEqual(exhausted.reason, "budget")


class TestEpisodeEngineStallRecovery(unittest.TestCase):
    def test_permission_denial_fails_closed_without_sleeping(self) -> None:
        kernel = MagicMock()
        kernel.dispatch.return_value = DispatchResult(
            failure=FailurePath.DENIED_REJECT, detail="permission denied",
        )
        slept: list[Any] = []

        def _sleep(seconds: float) -> None:
            slept.append(seconds)
            raise AssertionError("permission denial must not sleep into authorization")

        engine = EpisodeEngine(
            kernel=kernel,
            model=doubles.ScriptedModel([doubles.effect(), doubles.finish()]),
            clock=fakes.FakeClock(),
            events=doubles.RecordingSink(),
            scope=fakes.child_scope(),
            max_turns=8,
        )
        with patch.object(time, "sleep", _sleep):
            outcome = engine.run(
                episode_id="episode-1", run_id="run-1", principal="agent-1",
                brief="write one file", spans=(fakes.operator_span(),),
            )
        self.assertIs(outcome.terminal, RunTermination.ABANDONED)
        self.assertEqual(outcome.recovery_state.last_decision.action, "stop")
        self.assertEqual(outcome.recovery_state.last_decision.delay_ms, 0)
        self.assertEqual(slept, [])
        self.assertEqual(kernel.dispatch.call_count, 1)
        restored = ProtocolRecoveryState.decode(outcome.recovery_state.encode())
        self.assertEqual(restored.last_decision.action, "stop")
        self.assertIn("permission", restored.last_decision.reason)

    def test_resumed_intervention_budget_is_not_reset(self) -> None:
        stalled = _attempt("patch.apply", progress="stuck", outcome="failed", failure="patch")
        _, state = _recover(ProtocolRecoveryState(), stalled)
        _, state = _recover(state, stalled)
        resumed = ProtocolRecoveryState.decode(state.encode())
        self.assertEqual(resumed.interventions, 2)
        stop, resumed = _recover(resumed, stalled)
        self.assertEqual(stop.action, "stop")
        self.assertNotEqual(stop.action, "consult")


if __name__ == "__main__":
    unittest.main()
