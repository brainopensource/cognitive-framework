"""CMX-06 falsifiers for bounded model orchestration and specialist role gating."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.repository.multi_file_completeness import CodeDefaultCompletionPolicy
from vanguard.packages.agency.episode.admission_gate import VerificationReceipt
from vanguard.packages.kernel.attenuation import Constraints, Scope, attenuate
from vanguard.packages.runtime.model_selection import ModelUnavailable, select_model
from vanguard.packages.runtime.repair import StopReason
from vanguard.packages.runtime.tier_escalation import (
    EscalationOutcome,
    ModelRole,
    RoleAwareRouter,
    TierLadder,
    run_with_escalation,
)
from vanguard.packages.runtime.topology import Topology, TopologyRole, TopologyEdge, lower_topology, TopologyError


class TestCMX06ModelOrchestration(unittest.TestCase):
    def test_missing_openrouter_api_key_yields_typed_unavailability_without_escalation(self) -> None:
        with self.assertRaises(ModelUnavailable) as ctx:
            select_model("openrouter", env={})
        self.assertEqual(ctx.exception.port, "openrouter")
        self.assertEqual(ctx.exception.instrument_error, "instrument_error:openrouter_unavailable")
        self.assertIn("OPENROUTER_API_KEY is not set", ctx.exception.reason)

    def test_unknown_model_port_fails_closed(self) -> None:
        with self.assertRaises(ModelUnavailable) as ctx:
            select_model("unknown_port", env={})
        self.assertIn("unknown model port", ctx.exception.reason)

    def test_paid_model_refused_without_explicit_paid_authorization(self) -> None:
        router = RoleAwareRouter(
            bands={
                "free": ("openrouter/free",),
                "medium": ("deepseek/deepseek-v4-flash-0731",),
            },
            planner_model="deepseek/deepseek-v4-flash-0731",
        )
        with self.assertRaises(ValueError) as ctx:
            router.choose(
                ModelRole.ARCHITECT,
                episode_id="ep-1",
                reason="plan",
                allow_paid=False,
            )
        self.assertIn("not authorized", str(ctx.exception))

        with self.assertRaises(ModelUnavailable) as ctx2:
            select_model(
                "openrouter",
                model_name="deepseek/deepseek-v4-flash-0731",
                allow_paid=False,
                env={"OPENROUTER_API_KEY": "sk-dummy-key"},
                free_models=lambda: ["openrouter/free"],
            )
        self.assertIn("not in the free band; refusing to spend", ctx2.exception.reason)

    def test_free_model_failure_does_not_erase_discoveries_before_escalation(self) -> None:
        ladder = TierLadder(
            rungs=(
                ("free", "openrouter/free"),
                ("medium", "deepseek/deepseek-v4-flash-0731"),
            )
        )
        discoveries_collected = []

        def run_one(band: str, model_name: str) -> dict:
            if band == "free":
                discoveries_collected.append("discovered:src/calc.py")
                return {
                    "outcome": StopReason.NO_PROGRESS,
                    "discoveries": tuple(discoveries_collected),
                    "session": (),
                }
            discoveries_collected.append("discovered:src/formula.py")
            return {
                "outcome": StopReason.ORACLE_GREEN,
                "discoveries": tuple(discoveries_collected),
                "session": ({"verb": "patch.apply"},),
            }

        outcome = run_with_escalation(ladder, run_one)
        self.assertEqual(len(outcome.attempts), 2)
        self.assertEqual(outcome.attempts[0].band, "free")
        self.assertEqual(outcome.attempts[1].band, "medium")
        self.assertEqual(outcome.settled_band, "medium")
        self.assertEqual(outcome.settled_model, "deepseek/deepseek-v4-flash-0731")
        self.assertIn("discovered:src/calc.py", outcome.final["discoveries"])
        self.assertIn("discovered:src/formula.py", outcome.final["discoveries"])

    def test_escalation_cannot_add_capability_monotonically(self) -> None:
        parent_scope = Scope(
            actions=frozenset(["fs.read", "fs.search"]),
            resources=(),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=10,
                budget_usd_micros=100_000,
                risk_ceiling="low",
                max_depth=2,
                network_policy="deny",
            ),
            depth=1,
            sealed=True,
        )
        requested_scope = Scope(
            actions=frozenset(["fs.read", "fs.search", "fs.write", "proc.exec"]),
            resources=(),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=5,
                budget_usd_micros=50_000,
                risk_ceiling="low",
                max_depth=2,
                network_policy="deny",
            ),
            depth=1,
            sealed=True,
        )
        result = attenuate(parent_scope, requested_scope)
        self.assertFalse(result.ok)
        self.assertIsNotNone(result.denial)
        self.assertEqual(result.denial.dimension, "actions")
        self.assertEqual(sorted(result.denial.requested), ["fs.write", "proc.exec"])

    def test_child_budget_is_no_greater_than_parent_remaining_budget(self) -> None:
        role_entry = TopologyRole(
            role_id="lead",
            policy_ref="policy.yaml",
            budget_template={"usd_micros": 500_000},
        )
        topology = Topology(
            topology_id="topo-1",
            version="1.0",
            roles=(role_entry,),
            edge_records=(),
            artifact_flows=(),
            entry_role="lead",
        )
        comp = MagicMock()
        comp.verbs = ("agent.spawn",)
        comp.budget = {"usd_micros": 200_000}
        with self.assertRaises(TopologyError) as ctx:
            lower_topology(topology, composition=comp)
        self.assertIn("above composition ceiling", str(ctx.exception))

    def test_reviewer_artifacts_bound_to_current_patch_digest(self) -> None:
        policy = CodeDefaultCompletionPolicy()
        verdict = policy.evaluate(
            preset_name="vg-code-max",
            changed_files=["src/app.py"],
            proposal={"kind": "finish"},
            inspected_files=["src/app.py"],
            implicated_files=["src/app.py"],
            verification=VerificationReceipt(0, 1, "sha256:workspace"),
            current_workspace_digest="sha256:workspace",
            current_patch_digest="sha256:current_patch",
            review_required=True,
            review_evidence={"passed": True, "patch_digest": "sha256:current_patch"},
        )
        self.assertTrue(verdict["admissible"])

    def test_stale_review_cannot_admit_completion(self) -> None:
        policy = CodeDefaultCompletionPolicy()
        verdict = policy.evaluate(
            preset_name="vg-code-max",
            changed_files=["src/app.py"],
            proposal={"kind": "finish"},
            inspected_files=["src/app.py"],
            implicated_files=["src/app.py"],
            verification=VerificationReceipt(0, 1, "sha256:workspace"),
            current_workspace_digest="sha256:workspace",
            current_patch_digest="sha256:new_patch",
            review_required=True,
            review_evidence={"passed": True, "patch_digest": "sha256:old_patch"},
        )
        self.assertFalse(verdict["admissible"])
        self.assertEqual(verdict["reason"], "REVIEW_STALE")

    def test_reviewer_pass_cannot_override_verifier_failure(self) -> None:
        policy = CodeDefaultCompletionPolicy()
        verdict = policy.evaluate(
            preset_name="vg-code-max",
            changed_files=["src/app.py"],
            proposal={"kind": "finish"},
            inspected_files=["src/app.py"],
            implicated_files=["src/app.py"],
            verification=VerificationReceipt(1, 1, "sha256:workspace"),
            current_workspace_digest="sha256:workspace",
            current_patch_digest="sha256:patch",
            review_required=True,
            review_evidence={"passed": True, "patch_digest": "sha256:patch"},
        )
        self.assertFalse(verdict["admissible"])
        self.assertEqual(verdict["reason"], "VERIFICATION_FAILED")

    def test_no_progress_triggers_one_bounded_escalation(self) -> None:
        ladder = TierLadder(
            rungs=(
                ("free", "openrouter/free"),
                ("medium", "deepseek/deepseek-v4-flash-0731"),
            )
        )
        attempt_count = 0

        def run_one(band: str, model_name: str) -> dict:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                return {"outcome": StopReason.NO_PROGRESS, "session": ()}
            return {"outcome": StopReason.ORACLE_GREEN, "session": ({"verb": "test"},)}

        outcome = run_with_escalation(ladder, run_one)
        self.assertEqual(len(outcome.attempts), 2)
        self.assertEqual(outcome.settled_band, "medium")

    def test_configuration_error_does_not_trigger_expensive_escalation(self) -> None:
        ladder = TierLadder(
            rungs=(
                ("free", "openrouter/free"),
                ("medium", "deepseek/deepseek-v4-flash-0731"),
            )
        )
        attempt_count = 0

        def run_one(band: str, model_name: str) -> dict:
            nonlocal attempt_count
            attempt_count += 1
            return {"outcome": "workspace_missing", "session": ()}

        outcome = run_with_escalation(ladder, run_one)
        self.assertEqual(len(outcome.attempts), 1)
        self.assertEqual(attempt_count, 1)
        self.assertIsNone(outcome.settled_band)


if __name__ == "__main__":
    unittest.main()
