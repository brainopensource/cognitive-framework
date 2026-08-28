"""M-8: a skill may propose evidence; it may never declare itself better (`B-M8`).

Every test here is an attempt to get an unearned promotion through, because
that is the only failure mode that matters: a rejected good skill costs a
cycle, a promoted bad one silently degrades every later run and is invisible
in exactly the metric that promoted it.

The attacks are grouped by which separation they try to collapse:

* generator/evaluator/promoter identity -- self-promotion;
* candidate/composition -- scoring one thing and shipping another;
* present/invoked/grounded/verified -- a presence-only effect read as a lift;
* dev/held-out -- optimising against the split that decides;
* promotion/rollback -- a rollback that is documented rather than executable.

The last group ends with an injected regression: the only honest way to show a
rollback works is to break something on purpose and watch it come back.
"""

from __future__ import annotations

import unittest

from vanguard.packages.runtime.reproducibility import (
    assess_reproducibility,
    reassess_current_reproducibility,
)
from vanguard.packages.runtime.skill_evaluation import (
    AuthoritySeparationError,
    EvaluationWorkload,
    HeldOutEvaluator,
    PromoterSigner,
    PromotionRefused,
    RollbackRefused,
    SignedSkillPromoter,
    TrajectorySkillGenerator,
    promote_and_register,
    rollback_and_register,
    verify_promotion_evidence,
)
from vanguard.packages.runtime.skill_lifecycle import CompositionRegistry

BASE, NEXT = "composition-v1", "composition-v2"
KEY = b"m8-promoter-private-key-32bytes!"[:32]

# Forty held-out instances, not ten. `MEASUREMENT.md §5.4` is blunt about it:
# detecting a five-point effect against a realistic floor takes low hundreds of
# paired instances, and a ten-task split cannot express a lift smaller than
# 0.1 at all -- so a threshold test on it would only ever be testing rounding.
HELD_OUT = tuple(f"H{index}" for index in range(1, 41))
WORKLOAD = EvaluationWorkload(dev=("D1", "D2"), held_out=HELD_OUT,
                              adversarial=("A1",), transfer=("T1",))


def _runner(
    *,
    gains: tuple[str, ...] = ("H1", "H2", "H3", "H4"),
    breaks: tuple[str, ...] = (),
    invoked: tuple[str, ...] | None = None,
    grounded: tuple[str, ...] | None = None,
    verified: tuple[str, ...] | None = None,
    adversarial_invoked: bool = False,
):
    """A stubbed workload: the baseline fails `gains`, the candidate fixes them."""
    invoked = gains if invoked is None else invoked
    grounded = gains if grounded is None else grounded
    verified = gains if verified is None else verified

    def run(task: str, version: str) -> dict[str, bool]:
        if task == "A1":
            return {"passed": False, "invoked": adversarial_invoked}
        if task == "T1":
            return {"passed": version == NEXT}
        if version == BASE:
            return {"passed": task not in gains}
        return {"passed": task not in breaks,
                "invoked": task in invoked,
                "grounded": task in grounded,
                "verified": task in verified}
    return run


def _pipeline(**kw):
    generator = TrajectorySkillGenerator("gen-1")
    candidate = generator.generate("sha256:traj", ("sha256:fail",),
                                   composition_version=BASE)
    evaluator = HeldOutEvaluator("eval-1", WORKLOAD, _runner(**kw))
    report, detail = evaluator.evaluate(candidate, baseline_version=BASE,
                                        candidate_version=NEXT)
    promoter = SignedSkillPromoter("promoter-1", PromoterSigner(KEY, "promoter-key"),
                                   generator_id="gen-1", evaluator_id="eval-1")
    return candidate, report, detail, promoter


class TheThreeAuthoritiesStayDistinct(unittest.TestCase):
    def test_a_promoter_that_is_also_the_generator_is_refused(self) -> None:
        with self.assertRaises(AuthoritySeparationError) as ctx:
            SignedSkillPromoter("gen-1", PromoterSigner(KEY, "k"),
                                generator_id="gen-1", evaluator_id="eval-1")
        self.assertIn("self-promote", str(ctx.exception))

    def test_a_promoter_that_is_also_the_evaluator_is_refused(self) -> None:
        with self.assertRaises(AuthoritySeparationError):
            SignedSkillPromoter("eval-1", PromoterSigner(KEY, "k"),
                                generator_id="gen-1", evaluator_id="eval-1")

    def test_a_generator_that_is_also_the_evaluator_is_refused(self) -> None:
        with self.assertRaises(AuthoritySeparationError):
            SignedSkillPromoter("promoter-1", PromoterSigner(KEY, "k"),
                                generator_id="same", evaluator_id="same")

    def test_the_generator_exposes_no_evaluation_or_promotion_method(self) -> None:
        # Structural, not procedural: an agent driving the generator cannot
        # reach a promotion path even by mistake.
        generator = TrajectorySkillGenerator("gen-1")
        for forbidden in ("evaluate", "promote", "sign", "signer"):
            self.assertFalse(hasattr(generator, forbidden), forbidden)

    def test_the_evaluator_holds_no_signing_key(self) -> None:
        evaluator = HeldOutEvaluator("eval-1", WORKLOAD, _runner())
        for forbidden in ("promote", "sign", "signer", "public_bytes"):
            self.assertFalse(hasattr(evaluator, forbidden), forbidden)


class HeldOutEvidenceMustBeReal(unittest.TestCase):
    def test_a_held_out_task_contaminated_by_the_dev_split_is_refused(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            EvaluationWorkload(dev=("H1",), held_out=HELD_OUT)
        self.assertIn("contaminated", str(ctx.exception))

    def test_a_workload_with_no_held_out_split_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            EvaluationWorkload(dev=("D1",), held_out=())

    def test_duplicate_or_cross_split_tasks_are_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate"):
            EvaluationWorkload(dev=("D1",), held_out=("H1", "H1"))
        with self.assertRaisesRegex(ValueError, "contaminate"):
            EvaluationWorkload(dev=("D1",), held_out=("H1",), transfer=("H1",))

    def test_measurement_thresholds_cannot_be_disabled(self) -> None:
        with self.assertRaises(ValueError):
            HeldOutEvaluator("eval", WORKLOAD, _runner(), min_held_out_lift=0.0)
        with self.assertRaises(ValueError):
            HeldOutEvaluator("eval", WORKLOAD, _runner(), regression_budget=1.1)

    def test_non_boolean_runner_outcomes_are_refused(self) -> None:
        evaluator = HeldOutEvaluator(
            "eval", WORKLOAD, lambda _task, _version: {"passed": "false"})
        candidate = TrajectorySkillGenerator("gen").generate(
            "sha256:traj", composition_version=BASE)
        with self.assertRaises(TypeError):
            evaluator.evaluate(candidate, baseline_version=BASE, candidate_version=NEXT)

    def test_a_lift_below_the_threshold_does_not_promote(self) -> None:
        # One task in forty is 0.025 -- inside the range a fixed set moves on
        # its own, and below the 0.05 the promoter will not lower.
        candidate, report, detail, promoter = _pipeline(gains=("H1",))
        self.assertFalse(report.held_out_pass)
        with self.assertRaises(PromotionRefused):
            promoter.promote(candidate, report, detail,
                             previous_version=BASE, promoted_version=NEXT)

    def test_a_regression_beyond_budget_does_not_promote(self) -> None:
        candidate, report, detail, promoter = _pipeline(
            gains=("H1", "H2", "H3", "H4"), breaks=("H5", "H6"))
        self.assertFalse(report.affected_context_pass)
        self.assertEqual(detail.regressions, ("H5", "H6"))
        with self.assertRaises(PromotionRefused):
            promoter.promote(candidate, report, detail,
                             previous_version=BASE, promoted_version=NEXT)

    def test_residual_failures_are_recorded_not_dropped(self) -> None:
        _, _, detail, _ = _pipeline(breaks=("H9",))
        self.assertIn("H9", detail.regressions + detail.residual_failures)
        self.assertEqual(detail.baseline_passes, len(HELD_OUT) - 4)

    def test_the_promotion_unit_is_the_composition_not_the_skill(self) -> None:
        candidate, report, detail, promoter = _pipeline()
        with self.assertRaises(PromotionRefused) as ctx:
            promoter.promote(candidate, report, detail,
                             previous_version=BASE, promoted_version=BASE)
        self.assertIn("change the composition version", str(ctx.exception))


class PresenceIsNotUseAndUseIsNotGrounding(unittest.TestCase):
    def test_a_skill_that_gained_without_ever_being_invoked_is_refused(self) -> None:
        # The score moved and the skill was merely in context. Those two facts
        # are unrelated until something connects them.
        candidate, report, detail, promoter = _pipeline(invoked=())
        self.assertTrue(detail.presence_only)
        self.assertFalse(report.adversarial_pass)
        with self.assertRaises(PromotionRefused):
            promoter.promote(candidate, report, detail,
                             previous_version=BASE, promoted_version=NEXT)

    def test_every_reported_gain_must_have_an_invocation(self) -> None:
        _, report, detail, _ = _pipeline(invoked=("H1",))
        self.assertTrue(detail.presence_only)
        self.assertFalse(report.adversarial_pass)

    def test_an_ungrounded_gain_is_refused(self) -> None:
        _, report, _, _ = _pipeline(grounded=("H1",))
        self.assertFalse(report.grounded)
        self.assertFalse(report.promotable)

    def test_an_unverified_gain_is_refused(self) -> None:
        _, report, _, _ = _pipeline(verified=())
        self.assertFalse(report.verified)
        self.assertFalse(report.promotable)

    def test_an_adversarial_task_the_skill_reaches_into_is_refused(self) -> None:
        # Presence-only check: A1 must be untouched by this candidate.
        _, report, detail, _ = _pipeline(adversarial_invoked=True)
        self.assertEqual(detail.adversarial_present_only, ("A1",))
        self.assertFalse(report.adversarial_pass)

    def test_transfer_is_recorded_alongside_the_held_out_result(self) -> None:
        _, _, detail, _ = _pipeline()
        self.assertEqual(detail.transfer_passes, 1)


class PromotionEvidenceBindsWhatWasDecided(unittest.TestCase):
    def test_a_clean_candidate_promotes_with_a_verifiable_signature(self) -> None:
        candidate, report, detail, promoter = _pipeline()
        self.assertTrue(report.promotable)
        evidence = promoter.promote(candidate, report, detail,
                                    previous_version=BASE, promoted_version=NEXT)
        self.assertTrue(verify_promotion_evidence(
            evidence, candidate, report, detail, promoter.signer.public_bytes))

    def test_another_key_does_not_verify_the_promotion(self) -> None:
        candidate, report, detail, promoter = _pipeline()
        evidence = promoter.promote(candidate, report, detail,
                                    previous_version=BASE, promoted_version=NEXT)
        other = PromoterSigner(b"a-different-promoter-key-32byte!"[:32], "other")
        self.assertFalse(verify_promotion_evidence(
            evidence, candidate, report, detail, other.public_bytes))

    def test_a_report_describing_another_candidate_is_refused(self) -> None:
        candidate, report, detail, promoter = _pipeline()
        other = TrajectorySkillGenerator("gen-1").generate(
            "sha256:other", composition_version=BASE)
        with self.assertRaises(PromotionRefused) as ctx:
            promoter.promote(other, report, detail,
                             previous_version=BASE, promoted_version=NEXT)
        self.assertIn("does not describe this candidate", str(ctx.exception))

    def test_a_summary_that_disagrees_with_its_own_decomposition_is_refused(self) -> None:
        import dataclasses

        candidate, report, detail, promoter = _pipeline()
        # The classic swap: keep the passing summary, replace the numbers.
        forged = dataclasses.replace(detail, regressions=("H9", "H8", "H7"))
        with self.assertRaises(PromotionRefused) as ctx:
            promoter.promote(candidate, report, forged,
                             previous_version=BASE, promoted_version=NEXT)
        self.assertIn("disagree", str(ctx.exception))

    def test_the_signature_covers_the_workload_it_was_scored_on(self) -> None:
        import dataclasses

        candidate, report, detail, promoter = _pipeline()
        evidence = promoter.promote(candidate, report, detail,
                                    previous_version=BASE, promoted_version=NEXT)
        moved = dataclasses.replace(detail, workload_digest="sha256:" + "0" * 64)
        self.assertFalse(verify_promotion_evidence(
            evidence, candidate, report, moved, promoter.signer.public_bytes))


def _signed_rollback(promoter, base: str, target: str):
    """Rollback evidence signed by the promotion authority.

    `registry.rollback()` takes no evidence and is refused: moving the served
    version is the same authority promotion exercises, so it carries the same
    proof (guidelines.md 9.2).
    """
    from vanguard.packages.runtime.skill_evaluation import sign_rollback

    return sign_rollback(
        promoter.signer,
        promoter_id="promoter-under-test",
        base_version=base,
        target_version=target,
        reason="injected regression observed on held-out tasks",
    )


class RollbackIsExecutableNotDocumented(unittest.TestCase):
    def test_a_promotion_can_be_rolled_back_to_the_prior_composition(self) -> None:
        candidate, report, detail, promoter = _pipeline()
        registry = CompositionRegistry(BASE)
        evidence = promoter.promote(candidate, report, detail,
                                    previous_version=BASE, promoted_version=NEXT)
        self.assertEqual(promote_and_register(
            registry, evidence, report, candidate, detail,
            promoter.signer.public_bytes), NEXT)
        self.assertEqual(
            rollback_and_register(
                registry, _signed_rollback(promoter, NEXT, BASE),
                promoter.signer.public_bytes),
            BASE)

    def test_fabricated_nonempty_signature_cannot_reach_the_registry(self) -> None:
        import dataclasses

        candidate, report, detail, promoter = _pipeline()
        evidence = promoter.promote(candidate, report, detail,
                                    previous_version=BASE, promoted_version=NEXT)
        forged = dataclasses.replace(evidence, signature="not-a-signature")
        registry = CompositionRegistry(BASE)
        with self.assertRaises(PromotionRefused):
            promote_and_register(
                registry, forged, report, candidate, detail,
                promoter.signer.public_bytes)
        self.assertEqual(registry.current, BASE)
        with self.assertRaises(PermissionError):
            registry.promote(forged, report)

    def test_an_injected_regression_is_caught_and_the_rollback_restores_behaviour(self) -> None:
        # The only honest rollback test: promote a composition, break a task
        # on purpose, observe the break, roll back, observe it gone.
        candidate, report, detail, promoter = _pipeline()
        registry = CompositionRegistry(BASE)
        evidence = promoter.promote(candidate, report, detail,
                                    previous_version=BASE, promoted_version=NEXT)
        promote_and_register(
            registry, evidence, report, candidate, detail,
            promoter.signer.public_bytes)

        injected = _runner(breaks=("H7", "H8", "H9"))
        broken = [task for task in HELD_OUT
                  if injected(task, registry.current).get("passed") is False
                  and injected(task, BASE).get("passed") is True]
        self.assertEqual(broken, ["H7", "H8", "H9"])

        self.assertEqual(
            rollback_and_register(
                registry, _signed_rollback(promoter, NEXT, BASE),
                promoter.signer.public_bytes),
            BASE)
        still_broken = [task for task in broken
                        if not injected(task, registry.current).get("passed")]
        self.assertEqual(still_broken, [])

    def test_a_registry_with_nothing_promoted_cannot_roll_back(self) -> None:
        _, _, _, promoter = _pipeline()
        with self.assertRaises(ValueError):
            rollback_and_register(
                CompositionRegistry(BASE), _signed_rollback(promoter, BASE, NEXT),
                promoter.signer.public_bytes)

    def test_an_unsigned_rollback_is_refused_outright(self) -> None:
        """The pointer move that used to work."""
        with self.assertRaises(PermissionError):
            CompositionRegistry(BASE).rollback()

    def test_a_forged_rollback_signature_cannot_move_the_served_version(self) -> None:
        candidate, report, detail, promoter = _pipeline()
        registry = CompositionRegistry(BASE)
        promote_and_register(
            registry,
            promoter.promote(candidate, report, detail,
                             previous_version=BASE, promoted_version=NEXT),
            report, candidate, detail, promoter.signer.public_bytes)

        forged = {**_signed_rollback(promoter, NEXT, BASE), "signature": "not-a-signature"}
        with self.assertRaises(RollbackRefused):
            rollback_and_register(registry, forged, promoter.signer.public_bytes)
        self.assertEqual(registry.current, NEXT)

    def test_rollback_evidence_cannot_be_replayed_against_a_moved_head(self) -> None:
        """Evidence binds the version it was signed against, not only the target."""
        candidate, report, detail, promoter = _pipeline()
        registry = CompositionRegistry(BASE)
        promote_and_register(
            registry,
            promoter.promote(candidate, report, detail,
                             previous_version=BASE, promoted_version=NEXT),
            report, candidate, detail, promoter.signer.public_bytes)

        # Signed while NEXT was served, but replayed after rolling back to BASE.
        captured = _signed_rollback(promoter, NEXT, BASE)
        rollback_and_register(registry, captured, promoter.signer.public_bytes)
        self.assertEqual(registry.current, BASE)
        with self.assertRaises(RollbackRefused):
            rollback_and_register(registry, captured, promoter.signer.public_bytes)

    def test_promotion_on_a_stale_base_version_is_refused(self) -> None:
        candidate, report, detail, promoter = _pipeline()
        registry = CompositionRegistry("composition-v0")
        evidence = promoter.promote(candidate, report, detail,
                                    previous_version=BASE, promoted_version=NEXT)
        with self.assertRaises(ValueError):
            promote_and_register(
                registry, evidence, report, candidate, detail,
                promoter.signer.public_bytes)


class ReproducibilityIsRecomputedAfterPromotion(unittest.TestCase):
    """A promotion changes what a later reader can reproduce, so the current
    claim is recomputed while the run-close claim stays immutable."""

    def _run_close(self):
        return assess_reproducibility(
            profile=type("P", (), {"profile_id": "product", "name": "product"})(),
            wal_durable=True, pins={"reducer": "v1.1.0"}, run_id="run-1")

    def test_the_run_close_vector_is_not_mutated_by_reassessment(self) -> None:
        run_close = self._run_close()
        before = run_close.to_dict()
        current = reassess_current_reproducibility(
            run_close, {"composition_version": NEXT})
        self.assertEqual(run_close.to_dict(), before)
        self.assertIn("reassessed_current", current.basis)

    def test_a_retired_provider_downgrades_the_current_claim_only(self) -> None:
        run_close = self._run_close()
        current = reassess_current_reproducibility(run_close, {"provider_retired": True})
        self.assertEqual(current.external_reexecution, "unavailable")
        self.assertNotEqual(run_close.to_dict(), current.to_dict())


class NoLifecycleEventKindIsIntroducedBeforeADR0100(unittest.TestCase):
    def test_the_module_declares_no_new_event_kind(self) -> None:
        from pathlib import Path

        from vanguard.packages.domain.ledger.events import READABLE_KINDS

        source = (Path(__file__).resolve().parents[2]
                  / "vanguard/packages/runtime/skill_evaluation.py").read_text(encoding="utf-8")
        for candidate in ("SkillProposed", "SkillEvaluated", "SkillPromoted",
                          "SkillRolledBack", "CompositionPromoted"):
            if candidate in source:
                self.assertIn(candidate, READABLE_KINDS, candidate)


if __name__ == "__main__":
    unittest.main()
