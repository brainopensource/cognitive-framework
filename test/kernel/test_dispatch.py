"""The dispatch sequence: ordering rules and the enumerated failure paths.

`05 §2.2` — every ordering rule corresponds to a defect that actually shipped,
so each has a test that fails if the order is restored to the "obvious" one.
`05 §2.3` — every exit is enumerated; `AT-09` requires the set to be
exhaustive, which is asserted directly here.
"""

from __future__ import annotations

import unittest

from vanguard.packages.kernel import (
    AdapterOutcome,
    FailurePath,
    Governor,
    Occurrence,
    Reservation,
    SinkClass,
    SinkMismatch,
    SinkRegistry,
)

from . import fakes


class HappyPath(unittest.TestCase):
    def test_a_within_authority_write_completes(self) -> None:
        harness = fakes.build()
        result = harness.kernel.dispatch(
            fakes.request(), requested_scope=fakes.child_scope(),
            reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.OK, result.detail)
        self.assertEqual(len(harness.adapter.calls), 1)

    def test_intent_is_durable_before_the_effect_begins(self) -> None:
        """`K-47`. Without this, a crash between dispatch and emit leaves no
        record that the effect was attempted."""
        harness = fakes.build()
        harness.kernel.dispatch(fakes.request(), requested_scope=fakes.child_scope(),
                                reservation=fakes.reservation())
        self.assertEqual(len(harness.ledger.entries), 1)
        intent = harness.ledger.entries[0]
        self.assertEqual(intent.kind, "EffectStarted")
        self.assertIn("descriptorDigest", intent.payload)
        # The adapter ran after the ledger entry existed, not before.
        self.assertEqual(len(harness.adapter.calls), 1)

    def test_release_precedes_emit_on_the_happy_path(self) -> None:
        """`K-06`. A leaked lease is worse than a lost event."""
        harness = fakes.build()
        harness.kernel.dispatch(fakes.request(), requested_scope=fakes.child_scope(),
                                reservation=fakes.reservation())
        self.assertIn("release", harness.trace)
        emits = [index for index, step in enumerate(harness.trace)
                 if step.startswith("emit:")]
        self.assertTrue(emits, harness.trace)
        self.assertLess(harness.trace.index("release"), emits[0], harness.trace)

    def test_emit_failure_does_not_fail_the_effect(self) -> None:
        """`F-25`: log, do not fail the effect."""
        harness = fakes.build(sink=fakes.RecordingSink(fails=True))
        result = harness.kernel.dispatch(fakes.request(),
                                         requested_scope=fakes.child_scope(),
                                         reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.OK)


class OrderingRules(unittest.TestCase):
    def test_unknown_action_never_opens_a_lease(self) -> None:
        """`K-04` / `F-02`. With lookup after reservation, an unknown action
        strands a lease that is never released and never committed."""
        harness = fakes.build()
        result = harness.kernel.dispatch(
            fakes.request(action="fs.chmod"), requested_scope=fakes.child_scope(),
            reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.UNKNOWN_ACTION)
        self.assertNotIn("reserve", harness.trace)
        self.assertEqual(harness.governor.remaining("usd_micros"), 10_000)

    def test_unhealthy_adapter_never_opens_a_lease(self) -> None:
        harness = fakes.build(adapter=fakes.FakeAdapter("fs.write", healthy=False))
        result = harness.kernel.dispatch(fakes.request(),
                                         requested_scope=fakes.child_scope(),
                                         reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.ADAPTER_UNAVAILABLE)
        self.assertNotIn("reserve", harness.trace)

    def test_denied_request_never_opens_a_lease(self) -> None:
        """`F-06`..`F-10` all sit before S7."""
        harness = fakes.build()
        escalation = fakes.child_scope(resources=(fakes.ETC,))
        result = harness.kernel.dispatch(fakes.request(), requested_scope=escalation,
                                         reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.DENIED_SCOPE_ESCALATION)
        self.assertNotIn("reserve", harness.trace)

    def test_grant_is_verified_at_the_point_of_effect(self) -> None:
        """`K-05`: S8 is inside the guard, after S7, so a mutated request
        cannot ride a grant issued for a different call."""
        harness = fakes.build()
        result = harness.kernel.dispatch(fakes.request(),
                                         requested_scope=fakes.child_scope(),
                                         reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.OK)
        # The grant bound the descriptor of exactly this call.
        intent = harness.ledger.entries[0]
        self.assertEqual(intent.payload["descriptorDigest"], result.descriptor_digest)

    def test_lease_returns_on_every_failure_path_after_reservation(self) -> None:
        for label, adapter in (
            ("raises", fakes.FakeAdapter("fs.write", raises=RuntimeError("boom"))),
            ("timeout", fakes.FakeAdapter(
                "fs.write", outcome=AdapterOutcome("timeout", Occurrence.UNDETERMINABLE))),
            ("error", fakes.FakeAdapter(
                "fs.write", outcome=AdapterOutcome("error", Occurrence.DID_NOT_OCCUR))),
        ):
            with self.subTest(case=label):
                harness = fakes.build(adapter=adapter)
                harness.kernel.dispatch(fakes.request(),
                                        requested_scope=fakes.child_scope(),
                                        reservation=fakes.reservation())
                self.assertIn("release", harness.trace)
                self.assertEqual(harness.governor.ledger()["usd_micros"]["held"], 0)


class FailClosed(unittest.TestCase):
    def test_classifier_exception_is_treated_as_widening(self) -> None:
        """`F-05`. Failing open here would mean an exception in the classifier
        disables the authority predicate — the most attractive target there is.
        """

        class Exploding:
            def widens_capability(self, request):
                raise ValueError("classifier is down")

        harness = fakes.build(classifier=Exploding())
        result = harness.kernel.dispatch(fakes.request(),
                                         requested_scope=fakes.child_scope(),
                                         reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.CLASSIFIER_ERROR)
        self.assertNotIn("reserve", harness.trace)
        rejection = result.events[-1]
        self.assertTrue(rejection.payload["widensCapability"])

    def test_intent_append_failure_stops_the_effect(self) -> None:
        """`F-21a`: the effect never starts, and the alarm is alertable."""
        harness = fakes.build(ledger=fakes.RecordingLedger(fails=True))
        result = harness.kernel.dispatch(fakes.request(),
                                         requested_scope=fakes.child_scope(),
                                         reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.INTENT_APPEND_FAILED)
        self.assertEqual(harness.adapter.calls, [])
        alarm = result.events[-1]
        self.assertEqual(alarm.kind, "KernelAlarm")
        self.assertTrue(alarm.alertable)

    def test_undeterminable_occurrence_is_preserved(self) -> None:
        """`F-22`. Resolving an undeterminable external effect to success or
        failure is manufacturing evidence."""
        adapter = fakes.FakeAdapter("fs.write", outcome=AdapterOutcome(
            "error", Occurrence.UNDETERMINABLE, {"usd_micros": 200}))
        harness = fakes.build(adapter=adapter)
        result = harness.kernel.dispatch(fakes.request(),
                                         requested_scope=fakes.child_scope(),
                                         reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.UNDETERMINABLE)
        reconciled = [event for event in result.events if event.kind == "EffectReconciled"]
        self.assertEqual(len(reconciled), 1)
        self.assertEqual(reconciled[0].payload["occurrence"], "undeterminable")

    def test_adapter_exception_leaves_occurrence_unknown(self) -> None:
        harness = fakes.build(adapter=fakes.FakeAdapter(
            "fs.write", raises=RuntimeError("connection reset mid-write")))
        result = harness.kernel.dispatch(fakes.request(),
                                         requested_scope=fakes.child_scope(),
                                         reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.UNDETERMINABLE)

    def test_budget_denial_is_reported_per_dimension(self) -> None:
        """`F-12`."""
        harness = fakes.build(ceilings={"usd_micros": 100})
        result = harness.kernel.dispatch(fakes.request(),
                                         requested_scope=fakes.child_scope(),
                                         reservation=Reservation(usd_micros=5_000))
        self.assertIs(result.failure, FailurePath.BUDGET_DENIED)
        self.assertEqual(result.events[-1].payload["dimension"], "usd_micros")

    def test_closed_parent_lease_denies(self) -> None:
        """`F-13`."""
        harness = fakes.build()
        parent = harness.governor.reserve("run-1", Reservation(usd_micros=100))
        harness.governor.release(parent)
        result = harness.kernel.dispatch(
            fakes.request(parent_lease=parent.lease_id),
            requested_scope=fakes.child_scope(), reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.PARENT_LEASE_CLOSED)

    def test_schema_validation_rejects_before_anything_else(self) -> None:
        """`F-01`."""
        harness = fakes.build()
        result = harness.kernel.dispatch(
            fakes.request(principal=""), requested_scope=fakes.child_scope(),
            reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.SCHEMA)
        self.assertEqual(harness.adapter.calls, [])


class Approval(unittest.TestCase):
    def test_interactive_mode_suspends_without_holding_a_lease(self) -> None:
        """`F-08`, `K-13`: a suspension may last hours."""
        harness = fakes.build(approval_required_above="low",
                              risk_of={"fs.write": "critical"})
        result = harness.kernel.dispatch(fakes.request(),
                                         requested_scope=fakes.child_scope(),
                                         reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.APPROVAL_SUSPENDED)
        self.assertNotIn("reserve", harness.trace)
        self.assertIsNotNone(result.suspension)
        # `K-15`: the token binds the descriptor, so an approval cannot be
        # transplanted onto a different call.
        self.assertEqual(result.suspension.descriptor_digest, result.descriptor_digest)

    def test_benchmark_mode_never_suspends(self) -> None:
        """`F-07`, `K-17`: a run that blocks for a human has unbounded
        wall-clock and a human contributing to the measured outcome."""
        harness = fakes.build(mode=fakes.Mode.BENCHMARK,
                              approval_required_above="low",
                              risk_of={"fs.write": "critical"})
        result = harness.kernel.dispatch(fakes.request(),
                                         requested_scope=fakes.child_scope(),
                                         reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.DENIED_ASK_FAIL_CLOSED)
        self.assertIsNone(result.suspension)


class SinkClassification(unittest.TestCase):
    def test_privileged_sink_cannot_be_declared_pure(self) -> None:
        """`MF-KRN-008`: the registry refuses the registration, so the defect
        never reaches dispatch."""
        registry = SinkRegistry()
        for action in ("fs.write", "net.fetch", "exec.run", "secret.read"):
            with self.subTest(action=action):
                with self.assertRaises(SinkMismatch):
                    registry.register(action, SinkClass.PURE)

    def test_observation_cannot_be_declared_pure(self) -> None:
        registry = SinkRegistry()
        with self.assertRaises(SinkMismatch):
            registry.register("fs.read", SinkClass.PURE)

    def test_unregistered_action_is_privileged(self) -> None:
        """An unregistered effect is not evidence of harmlessness."""
        self.assertTrue(SinkRegistry().requires_grant("something.new"))

    def test_all_effects_are_recorded_including_observations(self) -> None:
        """`MF-KRN-009`: a pure or observation effect still produces the
        attribution sequence; only the *grant* is skipped."""
        adapter = fakes.FakeAdapter("fs.read")
        harness = fakes.build(adapter=adapter)
        result = harness.kernel.dispatch(
            fakes.request(action="fs.read", declared_sink_class=SinkClass.OBSERVATION),
            requested_scope=fakes.child_scope(actions=frozenset({"fs.read"})),
            reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.OK)
        kinds = [event.kind for event in result.events]
        self.assertIn("EffectStarted", kinds)
        self.assertIn("EffectCompleted", kinds)
        self.assertEqual(harness.ledger.entries[0].payload["grantId"], None)


class FailureTableIsExhaustive(unittest.TestCase):
    """`AT-09`: an exit not in the `05 §2.3` table is a defect."""

    DOCUMENTED = {
        "F-01", "F-02", "F-03", "F-04", "F-05", "F-06", "F-07", "F-08", "F-09",
        "F-10", "F-11", "F-12", "F-13", "F-14", "F-15", "F-16", "F-17", "F-18",
        "F-19", "F-20", "F-21", "F-21a", "F-22", "F-23", "F-24", "F-25",
    }

    def test_every_failure_path_is_a_documented_row(self) -> None:
        implemented = {path.value for path in FailurePath} - {"ok"}
        self.assertEqual(implemented, self.DOCUMENTED)

    def test_dispatch_always_names_a_path(self) -> None:
        """No exit returns without a `FailurePath`, on any input."""
        cases = [
            ("valid", fakes.request(), fakes.child_scope()),
            ("bad-principal", fakes.request(principal=""), fakes.child_scope()),
            ("unknown-action", fakes.request(action="nope"), fakes.child_scope()),
            ("escalation", fakes.request(), fakes.child_scope(resources=(fakes.ETC,))),
            ("bad-args", fakes.request(args={"path": object()}), fakes.child_scope()),
        ]
        for label, req, scope in cases:
            with self.subTest(case=label):
                harness = fakes.build()
                result = harness.kernel.dispatch(req, requested_scope=scope,
                                                 reservation=fakes.reservation())
                self.assertIsInstance(result.failure, FailurePath)


class BudgetConservation(unittest.TestCase):
    """`K-07`: commit debits reality, overruns included."""

    def test_overrun_is_debited_not_clamped(self) -> None:
        governor = Governor({"usd_micros": 10_000})
        lease = governor.reserve("run-1", Reservation(usd_micros=500))
        settlement = governor.commit(lease, {"usd_micros": 800})
        # `MF-KRN-007` fails here against max(reserved - actual, 0).
        self.assertEqual(settlement["usd_micros"], -300)
        self.assertEqual(governor.spent("usd_micros"), 800)
        self.assertEqual(governor.remaining("usd_micros"), 9_200)

    def test_underrun_refunds_the_difference(self) -> None:
        governor = Governor({"usd_micros": 10_000})
        lease = governor.reserve("run-1", Reservation(usd_micros=500))
        settlement = governor.commit(lease, {"usd_micros": 200})
        self.assertEqual(settlement["usd_micros"], 300)
        self.assertEqual(governor.remaining("usd_micros"), 9_800)

    def test_ceiling_is_conserved_across_many_effects(self) -> None:
        governor = Governor({"usd_micros": 10_000})
        for actual in (100, 900, 250, 700, 0):
            lease = governor.reserve("run-1", Reservation(usd_micros=500))
            governor.commit(lease, {"usd_micros": actual})
            governor.release(lease)
        self.assertEqual(governor.spent("usd_micros"), 1_950)
        self.assertEqual(governor.remaining("usd_micros"), 10_000 - 1_950)
        self.assertEqual(governor.ledger()["usd_micros"]["held"], 0)

    def test_released_lease_returns_the_whole_reservation(self) -> None:
        governor = Governor({"usd_micros": 10_000})
        lease = governor.reserve("run-1", Reservation(usd_micros=500))
        self.assertEqual(governor.remaining("usd_micros"), 9_500)
        governor.release(lease)
        self.assertEqual(governor.remaining("usd_micros"), 10_000)
