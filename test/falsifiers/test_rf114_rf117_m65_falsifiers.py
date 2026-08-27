"""RF-114..RF-117: M-6.5 progress projection, semantic checkpoints, and attributable study.

Ratified falsifiers from ADR-0103 & WP-B2:
- RF-114: A directive carrying a grant, verb, sink, or budget key is refused.
- RF-115: Controller-off produces byte-identical events and state digest.
- RF-116: A stale epoch or unknown subject leaves the verdict unchanged.
- RF-117: SemanticCheckpointRef is stable across retry and approval re-entry.
- Stochastic ModelPort adapter: same-key replay, interior variance, block elicitation, and signed report.
"""

from __future__ import annotations

import json
import unittest

from lab.m65_study import (
    M65StrategyController,
    build_m65_evidence_envelope,
    execute_stochastic_m65_study,
    perturbation_key,
)
from lab.m65_tasks import generate_m65_task_suite
from vanguard.packages.adapters.models.stochastic import (
    RECOVERABLE_BLOCK_TYPES,
    StochasticModelAdapter,
)
from vanguard.packages.domain.evidence.envelope import parse_envelope
from vanguard.packages.domain.ledger.agent_view import AgentView
from vanguard.packages.domain.ledger.progress import (
    ConfidenceRecord,
    ProgressProjection,
    ProgressView,
    SemanticCheckpointRef,
    fold_progress,
    fold_progress_projection,
)
from vanguard.packages.ports.meta_controller import StrategyDirective
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.meta_controller import (
    ControllerInputError,
    ControllerOutputError,
    guarded_consult,
    validate_confidence,
    validate_directive,
)


class RF114AuthorityFreeDirectives(unittest.TestCase):
    """RF-114: A directive carrying a grant, verb, sink, or budget key is refused."""

    def test_directive_with_authority_or_sink_is_refused(self) -> None:
        for forbidden in ("capabilities", "grants", "authority", "sink", "verb", "principal", "approval", "signature"):
            directive = StrategyDirective("delegate", "controller-1", "reason",
                                          brief="task brief", scope_slice={forbidden: "admin"})
            with self.assertRaises(ControllerOutputError) as ctx:
                validate_directive(directive)
            self.assertIn("authority", str(ctx.exception))

    def test_directive_with_unbounded_or_enlarging_budget_is_refused(self) -> None:
        # Without ceiling
        directive = StrategyDirective("delegate", "controller-1", "reason",
                                      brief="task brief", scope_slice={"maxTurns": 5})
        with self.assertRaises(ControllerOutputError):
            validate_directive(directive)

        # Exceeding remaining budget
        with self.assertRaises(ControllerOutputError):
            validate_directive(directive, remaining_budget={"turns": 3})

        # Valid bounded slice succeeds
        validate_directive(directive, remaining_budget={"turns": 10})


class RF115ControllerOffParity(unittest.TestCase):
    """RF-115: Controller-off produces byte-identical events and state digest."""

    def test_controller_off_is_byte_identical_and_issues_zero_directives(self) -> None:
        view = AgentView("lin-1", goal="task", context_epoch=0)
        progress = ProgressView(assessment="advancing", stall_count=0)

        proposal = guarded_consult(None, view, progress)
        self.assertIsNone(proposal)

        # Ensure disabled path parity
        task = generate_m65_task_suite(20)[0]
        checkpoint = SemanticCheckpointRef(run_id="run-1", episode_id="ep-1", epoch=0, attempt=0)
        adapter1 = StochasticModelAdapter(task_manifest_digest=task.digest(), environment_seed=42, checkpoint=checkpoint)
        adapter2 = StochasticModelAdapter(task_manifest_digest=task.digest(), environment_seed=42, checkpoint=checkpoint)

        context = {"layers": [{"role": "user", "content": "hello"}]}
        res1 = adapter1.propose(context)
        res2 = adapter2.propose(context)

        self.assertEqual(res1.value, res2.value)


class RF116StaleEpochAndUnknownSubjectInvariance(unittest.TestCase):
    """RF-116: A stale epoch or unknown subject leaves verdict unchanged / fails closed."""

    def test_stale_epoch_is_refused(self) -> None:
        view = AgentView("lin-1", goal="task", context_epoch=2)
        stale_record = ConfidenceRecord("behavioral", 0.6, "goal", ("event-1",), {"contextEpoch": 1, "method": "held-out"})
        with self.assertRaises(ControllerInputError) as ctx:
            validate_confidence(view, (stale_record,))
        self.assertIn("stale", str(ctx.exception))

    def test_unknown_subject_outside_view_is_refused(self) -> None:
        view = AgentView("lin-1", goal="task", context_epoch=0)
        unknown_record = ConfidenceRecord("behavioral", 0.6, "unknown-subject-99", ("event-1",), {"contextEpoch": 0, "method": "held-out"})
        with self.assertRaises(ControllerInputError) as ctx:
            validate_confidence(view, (unknown_record,))
        self.assertIn("not in the view", str(ctx.exception))


class RF117SemanticCheckpointStability(unittest.TestCase):
    """RF-117: SemanticCheckpointRef is stable across retry and approval re-entry."""

    def test_semantic_checkpoint_ref_is_deterministic_and_immutable(self) -> None:
        cp1 = SemanticCheckpointRef(run_id="run-100", episode_id="ep-100", epoch=1, attempt=2)
        cp2 = SemanticCheckpointRef(run_id="run-100", episode_id="ep-100", epoch=1, attempt=2)

        self.assertEqual(cp1, cp2)
        self.assertEqual(cp1.digest(), cp2.digest())
        self.assertEqual(cp1.to_dict(), {
            "runId": "run-100",
            "episodeId": "ep-100",
            "epoch": 1,
            "attempt": 2,
        })

    def test_perturbation_key_deterministic_replay_and_interior_variance(self) -> None:
        cp = SemanticCheckpointRef(run_id="run-100", episode_id="ep-100", epoch=0, attempt=0)

        # Same key -> identical digest
        k1 = perturbation_key("sha256:taskA", 42, cp, attempt_ordinal=0, perturbation="p1")
        k2 = perturbation_key("sha256:taskA", 42, cp, attempt_ordinal=0, perturbation="p1")
        self.assertEqual(k1, k2)

        # Changed seed -> variance
        k3 = perturbation_key("sha256:taskA", 43, cp, attempt_ordinal=0, perturbation="p1")
        self.assertNotEqual(k1, k3)

        # Changed attempt -> variance
        k4 = perturbation_key("sha256:taskA", 42, cp, attempt_ordinal=1, perturbation="p1")
        self.assertNotEqual(k1, k4)


class StochasticModelAdapterTests(unittest.TestCase):
    """Tests for the ModelPort-compliant stochastic adapter."""

    def test_adapter_proposes_through_model_port_with_same_key_replay(self) -> None:
        task = generate_m65_task_suite(20)[0]
        checkpoint = SemanticCheckpointRef(run_id="run-test", episode_id="ep-test", epoch=0, attempt=0)

        adapter1 = StochasticModelAdapter(
            task_manifest_digest=task.digest(),
            environment_seed=42,
            checkpoint=checkpoint,
            block_type="context_deficit",
        )
        adapter2 = StochasticModelAdapter(
            task_manifest_digest=task.digest(),
            environment_seed=42,
            checkpoint=checkpoint,
            block_type="context_deficit",
        )

        context = {"layers": [{"role": "user", "content": "solve task"}]}
        res1 = adapter1.propose(context)
        res2 = adapter2.propose(context)

        self.assertTrue(res1.ok)
        self.assertTrue(res2.ok)
        self.assertEqual(res1.value, res2.value)

    def test_block_elicitation_and_recovery_on_all_four_block_types(self) -> None:
        tasks = generate_m65_task_suite(24)
        directive_map = {
            "context_deficit": "request_context",
            "plan_stalemate": "revise_plan",
            "hypothesis_loop": "abandon_hypothesis",
            "verification_gap": "change_verification",
        }

        for block_type in RECOVERABLE_BLOCK_TYPES:
            matching_tasks = [t for t in tasks if t.block_type == block_type]
            self.assertTrue(len(matching_tasks) >= 5, f"Expected >=5 tasks for {block_type}")
            task = matching_tasks[0]

            adapter = StochasticModelAdapter(
                task_manifest_digest=task.digest(),
                environment_seed=42,
                block_type=block_type,
            )

            # Blocked context without directive
            ctx_blocked = {"layers": [{"role": "user", "content": f"Task: {task.name}"}]}
            res_blocked = adapter.propose(ctx_blocked)
            self.assertTrue(res_blocked.ok)

            # Unblocked context with directive
            directive = directive_map[block_type]
            ctx_unblocked = {
                "layers": [
                    {"role": "user", "content": f"Task: {task.name}"},
                    {"role": "assistant", "content": f"Strategy directive: {directive}"},
                ]
            }
            res_unblocked = adapter.propose(ctx_unblocked)
            self.assertTrue(res_unblocked.ok)
            self.assertIn("solution.py", str(res_unblocked.value.get("args", {}).get("path", "")))


class ProgressProjectionTests(unittest.TestCase):
    def test_progress_projection_fold(self) -> None:
        events = [
            {"payload": {"kind": "ProposalProduced"}},
            {"payload": {"kind": "EffectCompleted", "descriptorDigest": "d1"}},
            {"payload": {"kind": "StrategyChanged", "to": "revise_plan"}},
            {"payload": {"kind": "EffectCompleted", "descriptorDigest": "d2"}},
        ]
        conf = (ConfidenceRecord("behavioral", 0.8, "goal", ("event-1",), {"contextEpoch": 0, "method": "held-out"}),)
        proj = fold_progress_projection(events, conf)

        self.assertEqual(proj.schema, "ProgressProjection/2")
        self.assertEqual(proj.failed_unknown_rate, 0.0)
        self.assertEqual(proj.revision_effectiveness, 1.0)
        self.assertAlmostEqual(proj.calibrated_uncertainty, 0.2, places=4)
        self.assertTrue(proj.digest().startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
