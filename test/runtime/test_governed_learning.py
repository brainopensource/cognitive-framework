"""Comprehensive test suite for M-8 Governed Learning and CAS Promotion Registry."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.governance import (
    ApprovalAuthority,
    CompositionCandidate,
    DurableCompositionRegistry,
    EvaluationReport,
    NotAvailableError,
    OperatorSigner,
    PromotionEvidence,
    WorkloadSuite,
)


class TestGovernedLearning(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tempdir.name) / "registry.db"
        self.signer = OperatorSigner(key_id="promoter-key-1")
        self.authority = ApprovalAuthority({"promoter-key-1": self.signer.public_bytes})
        self.registry = DurableCompositionRegistry(
            db_path=self.db_path,
            initial_version="v1.0.0",
            initial_manifest={"version": "v1.0.0", "plugins": ["core"]},
            authority=self.authority,
        )

    def tearDown(self) -> None:
        self.registry.close()
        self._tempdir.cleanup()

    def test_candidate_creation_and_digest(self) -> None:
        cand = CompositionCandidate.create(
            base_version="v1.0.0",
            manifest={"version": "v1.1.0", "plugins": ["core", "optimizer"]},
            source_trajectories=["traj-001", "traj-002"],
            generator_id="gen-agent-alpha",
        )
        self.assertTrue(cand.candidate_id.startswith("cand-"))
        self.assertEqual(cand.base_version, "v1.0.0")
        self.assertTrue(cand.manifest_digest.startswith("sha256:"))
        self.assertEqual(cand.generator_id, "gen-agent-alpha")

    def test_promotion_without_a_verifier_fails_closed(self) -> None:
        registry = DurableCompositionRegistry(
            db_path=self.db_path.parent / "unverified.db",
            initial_version="v1.0.0",
            initial_manifest={"version": "v1.0.0"},
            authority=ApprovalAuthority({}),
        )
        try:
            cand = CompositionCandidate.create("v1.0.0", {"version": "v1.1.0"})
            report = EvaluationReport.create(
                cand,
                development_pass_rate=0.90,
                held_out_pass_rate=0.80,
                baseline_held_out_pass_rate=0.65,
                adversarial_pass_rate=0.85,
                baseline_adversarial_pass_rate=0.85,
                transfer_pass_rate=0.80,
                baseline_transfer_pass_rate=0.80,
            )
            evidence = PromotionEvidence(
                candidate_id=cand.candidate_id,
                base_version="v1.0.0",
                promoted_version="v1.1.0",
                expected_generation=0,
                report_digest=report.report_digest,
                promoter_id="promoter-1",
                key_id="missing-key",
                signature="",
                created_at="",
            )
            with self.assertRaises(NotAvailableError):
                registry.promote(cand, report, evidence)
        finally:
            registry.close()

    def test_evaluation_report_promotable_with_held_out_lift(self) -> None:
        cand = CompositionCandidate.create("v1.0.0", {"version": "v1.1.0"})
        report = EvaluationReport.create(
            cand,
            development_pass_rate=0.95,
            held_out_pass_rate=0.85,
            baseline_held_out_pass_rate=0.70,
            adversarial_pass_rate=0.80,
            baseline_adversarial_pass_rate=0.82,
            transfer_pass_rate=0.75,
            baseline_transfer_pass_rate=0.75,
            regression_budget=0.05,
            grounded=True,
            verified=True,
            evaluator_id="eval-daemon-1",
        )
        self.assertAlmostEqual(report.held_out_lift, 0.15, places=2)
        self.assertTrue(report.regression_pass)
        self.assertTrue(report.promotable)

    def test_evaluation_report_rejects_presence_only_gains(self) -> None:
        """Presence-only gains (high dev score without held-out lift) must not be promotable."""
        cand = CompositionCandidate.create("v1.0.0", {"version": "v1.1.0"})
        report = EvaluationReport.create(
            cand,
            development_pass_rate=0.99,
            held_out_pass_rate=0.70,
            baseline_held_out_pass_rate=0.70,  # Lift is 0.0
            adversarial_pass_rate=0.80,
            baseline_adversarial_pass_rate=0.80,
            transfer_pass_rate=0.75,
            baseline_transfer_pass_rate=0.75,
            evaluator_id="eval-daemon-1",
        )
        self.assertEqual(report.held_out_lift, 0.0)
        self.assertFalse(report.promotable)

    def test_evaluation_report_rejects_regression_exceeding_budget(self) -> None:
        cand = CompositionCandidate.create("v1.0.0", {"version": "v1.1.0"})
        report = EvaluationReport.create(
            cand,
            development_pass_rate=0.95,
            held_out_pass_rate=0.85,
            baseline_held_out_pass_rate=0.70,  # +0.15 lift
            adversarial_pass_rate=0.60,
            baseline_adversarial_pass_rate=0.80,  # -0.20 drop > 0.05 budget
            transfer_pass_rate=0.75,
            baseline_transfer_pass_rate=0.75,
            regression_budget=0.05,
            evaluator_id="eval-daemon-1",
        )
        self.assertFalse(report.regression_pass)
        self.assertFalse(report.promotable)

    def test_durable_cas_promotion_and_history(self) -> None:
        cand = CompositionCandidate.create("v1.0.0", {"version": "v1.1.0", "feature": "fast_search"})
        report = EvaluationReport.create(
            cand,
            development_pass_rate=0.90,
            held_out_pass_rate=0.80,
            baseline_held_out_pass_rate=0.65,
            adversarial_pass_rate=0.85,
            baseline_adversarial_pass_rate=0.85,
            transfer_pass_rate=0.80,
            baseline_transfer_pass_rate=0.80,
        )
        self.assertTrue(report.promotable)

        current_ver, current_gen = self.registry.get_current()
        self.assertEqual(current_ver, "v1.0.0")
        self.assertEqual(current_gen, 0)

        # Build signed promotion evidence
        evidence_draft = PromotionEvidence(
            candidate_id=cand.candidate_id,
            base_version=cand.base_version,
            promoted_version="v1.1.0",
            expected_generation=current_gen,
            report_digest=report.report_digest,
            promoter_id="promoter-operator-1",
            key_id=self.signer.key_id,
            signature="",
            created_at="",
        )
        sig = self.signer.sign_bytes(evidence_draft.canonical_bytes())
        evidence = PromotionEvidence(
            candidate_id=evidence_draft.candidate_id,
            base_version=evidence_draft.base_version,
            promoted_version=evidence_draft.promoted_version,
            expected_generation=evidence_draft.expected_generation,
            report_digest=evidence_draft.report_digest,
            promoter_id=evidence_draft.promoter_id,
            key_id=evidence_draft.key_id,
            signature=sig,
            created_at="2026-08-27T00:00:00.000Z",
        )

        promoted_ver = self.registry.promote(cand, report, evidence)
        self.assertEqual(promoted_ver, "v1.1.0")
        self.assertEqual(self.registry.current_version, "v1.1.0")
        self.assertEqual(self.registry.generation, 1)

        comp = self.registry.get_composition("v1.1.0")
        self.assertIsNotNone(comp)
        self.assertEqual(comp["manifest"]["feature"], "fast_search")
        self.assertEqual(comp["parent_version"], "v1.0.0")

    def test_cas_conflict_handling_on_concurrent_promotion(self) -> None:
        cand1 = CompositionCandidate.create("v1.0.0", {"version": "v1.1.0-A"})
        report1 = EvaluationReport.create(
            cand1,
            development_pass_rate=0.90,
            held_out_pass_rate=0.80,
            baseline_held_out_pass_rate=0.65,
            adversarial_pass_rate=0.85,
            baseline_adversarial_pass_rate=0.85,
            transfer_pass_rate=0.80,
            baseline_transfer_pass_rate=0.80,
        )
        evidence1 = PromotionEvidence(
            candidate_id=cand1.candidate_id,
            base_version="v1.0.0",
            promoted_version="v1.1.0-A",
            expected_generation=0,
            report_digest=report1.report_digest,
            promoter_id="promoter-1",
            key_id=self.signer.key_id,
            signature="",
            created_at="",
        )
        sig1 = self.signer.sign_bytes(evidence1.canonical_bytes())
        evidence1 = PromotionEvidence(
            candidate_id=evidence1.candidate_id,
            base_version=evidence1.base_version,
            promoted_version=evidence1.promoted_version,
            expected_generation=0,
            report_digest=evidence1.report_digest,
            promoter_id=evidence1.promoter_id,
            key_id=evidence1.key_id,
            signature=sig1,
            created_at="",
        )

        cand2 = CompositionCandidate.create("v1.0.0", {"version": "v1.1.0-B"})
        report2 = EvaluationReport.create(
            cand2,
            development_pass_rate=0.90,
            held_out_pass_rate=0.82,
            baseline_held_out_pass_rate=0.65,
            adversarial_pass_rate=0.85,
            baseline_adversarial_pass_rate=0.85,
            transfer_pass_rate=0.80,
            baseline_transfer_pass_rate=0.80,
        )
        evidence2 = PromotionEvidence(
            candidate_id=cand2.candidate_id,
            base_version="v1.0.0",
            promoted_version="v1.1.0-B",
            expected_generation=0,
            report_digest=report2.report_digest,
            promoter_id="promoter-2",
            key_id=self.signer.key_id,
            signature="",
            created_at="",
        )
        sig2 = self.signer.sign_bytes(evidence2.canonical_bytes())
        evidence2 = PromotionEvidence(
            candidate_id=evidence2.candidate_id,
            base_version=evidence2.base_version,
            promoted_version=evidence2.promoted_version,
            expected_generation=0,
            report_digest=evidence2.report_digest,
            promoter_id=evidence2.promoter_id,
            key_id=evidence2.key_id,
            signature=sig2,
            created_at="",
        )

        # First promoter wins
        self.registry.promote(cand1, report1, evidence1)
        self.assertEqual(self.registry.current_version, "v1.1.0-A")

        # Second promoter racing with same base generation must fail with CAS conflict
        with self.assertRaises(ValueError) as ctx:
            self.registry.promote(cand2, report2, evidence2)
        self.assertIn("conflict", str(ctx.exception).lower())

    def test_rollback_restores_previous_known_good(self) -> None:
        cand = CompositionCandidate.create("v1.0.0", {"version": "v1.1.0", "injected": "regression"})
        report = EvaluationReport.create(
            cand,
            development_pass_rate=0.90,
            held_out_pass_rate=0.80,
            baseline_held_out_pass_rate=0.65,
            adversarial_pass_rate=0.85,
            baseline_adversarial_pass_rate=0.85,
            transfer_pass_rate=0.80,
            baseline_transfer_pass_rate=0.80,
        )
        evidence = PromotionEvidence(
            candidate_id=cand.candidate_id,
            base_version="v1.0.0",
            promoted_version="v1.1.0",
            expected_generation=0,
            report_digest=report.report_digest,
            promoter_id="promoter-1",
            key_id=self.signer.key_id,
            signature="",
            created_at="",
        )
        sig = self.signer.sign_bytes(evidence.canonical_bytes())
        evidence = PromotionEvidence(
            candidate_id=evidence.candidate_id,
            base_version=evidence.base_version,
            promoted_version=evidence.promoted_version,
            expected_generation=0,
            report_digest=evidence.report_digest,
            promoter_id=evidence.promoter_id,
            key_id=evidence.key_id,
            signature=sig,
            created_at="",
        )

        self.registry.promote(cand, report, evidence)
        self.assertEqual(self.registry.current_version, "v1.1.0")

        # Injected regression detected in production -> rollback
        restored = self.registry.rollback()
        self.assertEqual(restored, "v1.0.0")
        self.assertEqual(self.registry.current_version, "v1.0.0")

    def test_restart_recovery_from_sqlite_wal(self) -> None:
        cand = CompositionCandidate.create("v1.0.0", {"version": "v1.2.0"})
        report = EvaluationReport.create(
            cand,
            development_pass_rate=0.90,
            held_out_pass_rate=0.80,
            baseline_held_out_pass_rate=0.65,
            adversarial_pass_rate=0.85,
            baseline_adversarial_pass_rate=0.85,
            transfer_pass_rate=0.80,
            baseline_transfer_pass_rate=0.80,
        )
        evidence = PromotionEvidence(
            candidate_id=cand.candidate_id,
            base_version="v1.0.0",
            promoted_version="v1.2.0",
            expected_generation=0,
            report_digest=report.report_digest,
            promoter_id="promoter-1",
            key_id=self.signer.key_id,
            signature="",
            created_at="",
        )
        sig = self.signer.sign_bytes(evidence.canonical_bytes())
        evidence = PromotionEvidence(
            candidate_id=evidence.candidate_id,
            base_version=evidence.base_version,
            promoted_version=evidence.promoted_version,
            expected_generation=0,
            report_digest=evidence.report_digest,
            promoter_id=evidence.promoter_id,
            key_id=evidence.key_id,
            signature=sig,
            created_at="",
        )
        self.registry.promote(cand, report, evidence)
        self.registry.close()

        # Reopen from disk in fresh registry instance
        fresh_registry = DurableCompositionRegistry(
            db_path=self.db_path,
            authority=self.authority,
        )
        try:
            self.assertEqual(fresh_registry.current_version, "v1.2.0")
            self.assertEqual(fresh_registry.generation, 1)
            comp = fresh_registry.get_composition("v1.2.0")
            self.assertIsNotNone(comp)
            self.assertEqual(comp["version"], "v1.2.0")
        finally:
            fresh_registry.close()


if __name__ == "__main__":
    unittest.main()
