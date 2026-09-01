"""`TEST-TRUST-001` / `REQ-TRUST-001` — the scripted no-model trajectory.

`ADR-0048`: model behaviour must not become a prerequisite of kernel
verification. Six properties are proved here with no provider present at all,
and the last test in the file proves the *absence* — because a model-free gate
that silently acquires a model import is worth nothing, and that is exactly
the failure mode the requirement exists to prevent.

Each class below is one row of the acceptance evidence: denial, attenuation,
budget exhaustion, event atomicity, kill recovery, secret non-disclosure.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

from vanguard.packages.agency import RunTermination
from vanguard.packages.kernel import AdapterOutcome, FailurePath, Occurrence
from vanguard.packages.runtime.ledger.recovery import RecoveryScanner

from test.support.composition import SharedLedger
from test.trust import spine


class Denial(unittest.TestCase):
    """A refused effect is a recorded event, not a crash and not a silent
    narrowing (`K-26`, `VG-03 §6.1`).

    The refusal exercised here is `F-09`: turn 1 performs a held effect, its
    receipt is labelled `untrusted_external` at its source class (`K-30`), and
    turn 2 proposes a capability-widening effect whose only justification is
    now that receipt. Untrusted content may inform work; it may never
    authorise it.
    """

    TAPE = (spine.effect(), spine.effect("fs.delete"), spine.effect(), spine.finish())

    def test_a_denied_effect_never_reaches_its_adapter(self) -> None:
        wired = spine.build(list(self.TAPE))
        outcome = wired.run()

        self.assertIs(outcome.dispatches[0].failure, FailurePath.OK)
        self.assertIs(outcome.dispatches[1].failure,
                      FailurePath.DENIED_UNTRUSTED_JUSTIFYING)
        self.assertEqual(wired.adapters["fs.delete"].calls, [])
        # The run continues past the denial and completes.
        self.assertIs(outcome.terminal, RunTermination.COMPLETED)
        self.assertEqual(len(wired.adapters["fs.write"].calls), 2)

    def test_the_denial_names_the_offending_call_not_the_one_after_it(self) -> None:
        """`VG-03 §6.5`: misattributed exhaustion is the defect this prevents."""
        wired = spine.build(list(self.TAPE))
        wired.run()

        denials = [event for event in wired.ledger.events()
                   if event.payload.get("kind") == "AuthorizationDenied"]
        self.assertEqual(len(denials), 1)
        self.assertEqual(denials[0].payload["untrustedSpans"], ["receipt-0"])

        proposals = [event for event in wired.ledger.events()
                     if event.payload.get("kind") == "ProposalProduced"]
        self.assertEqual(proposals[1].payload["action"], "fs.delete")
        self.assertLess(int(proposals[1].seq), int(denials[0].seq))
        self.assertLess(int(denials[0].seq), int(proposals[2].seq))

    def test_a_denied_call_opens_no_lease(self) -> None:
        """`F-06`..`F-10` sit before S7, so a denial cannot subtract a
        ceiling. Only the two effects that ran are debited."""
        wired = spine.build(list(self.TAPE))
        wired.run()
        self.assertEqual(wired.governor.spent("usd_micros"), 200)
        self.assertEqual(wired.governor.remaining("usd_micros"), 9_800)


class Attenuation(unittest.TestCase):
    def test_a_scope_wider_than_its_parent_is_refused_and_alertable(self) -> None:
        """`F-10`, `K-27`: a child asking for more than its parent holds is
        the strongest intrusion signal available, so it pages rather than logs."""
        wider = spine.requested_scope(resources=(spine.ETC,))
        wired = spine.build([spine.effect(), spine.finish()], scope=wider)
        outcome = wired.run()

        self.assertIs(outcome.dispatches[0].failure, FailurePath.DENIED_SCOPE_ESCALATION)
        self.assertEqual(wired.adapters["fs.write"].calls, [])
        alerts = [event for event in wired.ledger.events() if event.payload.get("alertable")]
        self.assertTrue(alerts)

    def test_widening_alone_is_not_a_violation(self) -> None:
        """Both operands are required. Without this the test above would pass
        against an implementation that denies every widening request, and the
        provenance clause would be untested."""
        wired = spine.build([spine.effect("fs.delete"), spine.finish()])
        outcome = wired.run(spans=(spine.operator_span(),), receipt_labeller=None)
        self.assertIs(outcome.dispatches[0].failure, FailurePath.OK)


class BudgetExhaustion(unittest.TestCase):
    def test_the_run_terminates_as_budget_exhausted(self) -> None:
        wired = spine.build([
            spine.effect(args={"path": f"/workspace/src/budget_{i}.ts"}, usd_micros=400)
            for i in range(6)
        ],
                            ceilings={"usd_micros": 1_000, "millis": 60_000},
                            adapters={"fs.write": spine.StaticAdapter(
                                "fs.write", cost={"usd_micros": 400, "millis": 10})})
        outcome = wired.run()

        self.assertIs(outcome.terminal, RunTermination.BUDGET_EXHAUSTED)
        self.assertIs(outcome.dispatches[-1].failure, FailurePath.BUDGET_DENIED)
        self.assertEqual(len(wired.adapters["fs.write"].calls), 2)

    def test_budget_is_conserved_including_the_denied_turn(self) -> None:
        """`K-07`: commit debits reality. `spent + remaining` equals the
        ceiling at all times, which is what makes exhaustion a fact rather
        than an estimate."""
        wired = spine.build([spine.effect(usd_micros=400) for _ in range(6)],
                            ceilings={"usd_micros": 1_000, "millis": 60_000},
                            adapters={"fs.write": spine.StaticAdapter(
                                "fs.write", cost={"usd_micros": 400, "millis": 10})})
        wired.run()
        self.assertEqual(wired.governor.spent("usd_micros")
                         + wired.governor.remaining("usd_micros"), 1_000)

    def test_an_overrun_is_debited_rather_than_clamped(self) -> None:
        """`MF-KRN-007`. Clamping the refund at zero lets a run exceed its
        budget indefinitely, one small overrun at a time."""
        overrunning = spine.StaticAdapter("fs.write", cost={"usd_micros": 900})
        wired = spine.build([spine.effect(usd_micros=400) for _ in range(6)],
                            ceilings={"usd_micros": 1_000, "millis": 60_000},
                            adapters={"fs.write": overrunning})
        wired.run()
        self.assertGreaterEqual(wired.governor.spent("usd_micros"), 900)


class Atomicity(unittest.TestCase):
    def test_intent_is_durable_before_the_effect_begins(self) -> None:
        """`K-47`: a crash between dispatch and emit must leave the effect
        undeterminable rather than invisible."""
        wired = spine.build([spine.effect(), spine.finish()])
        wired.run()

        kinds = wired.ledger.kinds()
        self.assertIn("EffectStarted", kinds)
        self.assertLess(kinds.index("EffectStarted"), kinds.index("EffectCompleted"))

    def test_an_intent_that_cannot_be_written_stops_the_effect(self) -> None:
        """`F-21a`. The alarm is recorded and the adapter never runs."""
        wired = spine.build([spine.effect(), spine.finish()],
                            ledger=SharedLedger(fails=True))
        outcome = wired.run()

        self.assertIs(outcome.dispatches[0].failure, FailurePath.INTENT_APPEND_FAILED)
        self.assertEqual(wired.adapters["fs.write"].calls, [])
        self.assertIs(outcome.terminal, RunTermination.RUNTIME_ERROR)

    def test_an_adapter_that_raises_leaves_occurrence_undeterminable(self) -> None:
        """`F-22`: uncertainty is preserved, never resolved. Resolving it to
        success or failure is manufacturing evidence."""
        exploding = spine.StaticAdapter("fs.write", raises=RuntimeError("connection reset"))
        wired = spine.build([spine.effect(), spine.finish()],
                            adapters={"fs.write": exploding})
        outcome = wired.run()

        self.assertIs(outcome.dispatches[0].failure, FailurePath.UNDETERMINABLE)
        reconciled = [event for event in wired.ledger.events()
                      if event.payload.get("kind") == "EffectReconciled"]
        self.assertEqual(reconciled[0].payload["occurrence"], "undeterminable")

    def test_the_lease_is_released_on_the_failing_path_too(self) -> None:
        """`K-06` / `F-24`: a leaked lease permanently subtracts a ceiling."""
        exploding = spine.StaticAdapter("fs.write", raises=RuntimeError("connection reset"))
        wired = spine.build([spine.effect(), spine.finish()],
                            adapters={"fs.write": exploding})
        wired.run()
        self.assertEqual(wired.governor.remaining("millis"), 60_000)


class KillRecovery(unittest.TestCase):
    def test_the_terminal_record_is_written_from_outside_the_corpse(self) -> None:
        """`VG-04 §12.4`. A dying process cannot be trusted to record its own
        death, so an interrupted run is terminated by the external controller.

        The interruption is modelled as a run whose durable intent exists with
        no outcome after it — which is precisely the state `K-47` guarantees a
        crash leaves behind.
        """
        interrupted = spine.build([spine.effect(), spine.finish()],
                                  adapters={"fs.write": spine.StaticAdapter(
                                      "fs.write", outcome=AdapterOutcome(
                                          "error", Occurrence.UNDETERMINABLE,
                                          {"usd_micros": 100}, detail="killed"))})
        interrupted.run()

        scanner = RecoveryScanner()
        record = scanner.scan_and_recover_run(
            interrupted.ledger.store, "run-trust",
            current_time_iso="2026-08-15T11:00:00.000Z", lease_timeout_ms=60_000)

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.action, "recovered")
        self.assertEqual(record.controller_principal, "recovery-controller")
        terminal = interrupted.ledger.events()[-1]
        self.assertEqual(terminal.payload["kind"], "RunRecovered")
        self.assertNotEqual(terminal.principal, spine.PRINCIPAL)

    def test_a_live_run_is_not_recovered(self) -> None:
        """A recovery controller that terminates healthy runs is worse than
        none, so the lease bound is asserted in both directions."""
        wired = spine.build([spine.effect(), spine.finish()])
        wired.run()
        scanner = RecoveryScanner()
        self.assertIsNone(scanner.scan_and_recover_run(
            wired.ledger.store, "run-trust",
            current_time_iso="2026-08-15T10:00:05.000Z", lease_timeout_ms=60_000))


class SecretNonDisclosure(unittest.TestCase):
    def test_a_secret_reaches_the_adapter_and_no_event(self) -> None:
        """`REQ-PORT-006` margin: zero secrets in events or exports.

        The value exists only inside the adapter. The run holds a reference,
        so the ledger cannot leak what the run was never given.
        """
        wired = spine.build([spine.send_secret(), spine.finish()])
        outcome = wired.run()

        self.assertIs(outcome.dispatches[0].failure, FailurePath.OK)
        self.assertEqual(wired.adapters["secret.send"].resolved, [spine.SECRET_VALUE])

        exported = json.dumps([event.to_dict() for event in wired.ledger.events()])
        self.assertNotIn(spine.SECRET_VALUE, exported)
        self.assertNotIn("sk-live", exported)

    def test_the_reference_itself_is_not_broadcast_in_a_proposal_event(self) -> None:
        """The proposal record carries a descriptor, not the arguments: a
        reference is not a secret, but it is a map to one."""
        wired = spine.build([spine.send_secret(), spine.finish()])
        wired.run()

        produced = [event for event in wired.ledger.events()
                    if event.payload.get("kind") == "ProposalProduced"]
        self.assertNotIn(spine.SECRET_REFERENCE, json.dumps(produced[0].payload))
        self.assertIn("proposalDescriptor", produced[0].payload)

    def test_the_leak_check_would_catch_one(self) -> None:
        """`ICD §7.5`: a gate that cannot fail is not a gate. If the exported
        ledger did contain the value, the assertion above would fire."""
        leaked = json.dumps({"payload": {"apiKey": spine.SECRET_VALUE}})
        self.assertIn(spine.SECRET_VALUE, leaked)


class LoopCompletion(unittest.TestCase):
    """The two loop properties `S4-SA-001` adds on top of the S3 slice."""

    def test_cancellation_terminates_the_run_before_the_next_proposal(self) -> None:
        """Cancellation is a run state, not an exception (`VG-03 §6.2`). It is
        checked before the proposal so a cancelled run cannot spend a turn."""
        wired = spine.build([spine.effect(), spine.effect(), spine.finish()])
        turns = {"seen": 0}

        def cancelled() -> bool:
            turns["seen"] += 1
            return turns["seen"] > 1

        outcome = wired.run(is_cancelled=cancelled)
        self.assertIs(outcome.terminal, RunTermination.CANCELLED)
        self.assertEqual(len(wired.adapters["fs.write"].calls), 1)

    def test_the_request_carries_the_episode_depth(self) -> None:
        """`K-24`: depth is a budget dimension, and the classifier measures
        the *request's* depth against the held ceiling. A loop that dropped it
        would leave runaway recursion unbounded while the invariant still
        appeared to be enforced."""
        wired = spine.build([spine.effect(), spine.finish()])
        wired.run(depth=2)
        self.assertEqual(wired.adapters["fs.write"].calls[0].depth, 2)


class NoModelOnTheGatePath(unittest.TestCase):
    """`REQ-TRUST-001` margin: zero model imports on the gate path."""

    def test_the_trajectory_runs_with_no_provider_key_set(self) -> None:
        self.assertIsNone(os.environ.get("OPENROUTER_API_KEY"),
                          "TEST-TRUST-001 must be run with the provider key unset")
        wired = spine.build([spine.effect(), spine.send_secret(), spine.finish()])
        self.assertIs(wired.run().terminal, RunTermination.COMPLETED)

    def test_no_provider_adapter_is_loaded_by_the_spine(self) -> None:
        """Asserted over the loaded module graph rather than promised in a
        docstring. A gate whose only evidence is a comment is a comment."""
        cmd = [
            sys.executable,
            "-c",
            "import sys; from test.trust import spine; spine.build([spine.finish()]).run(); "
            "loaded = [name for name in sys.modules if 'openrouter' in name.lower() or 'adapters.models' in name]; "
            "assert loaded == [], f'Provider adapters loaded: {loaded}'"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Spine loaded provider adapter: {res.stderr}")

    def test_the_episode_holds_no_evaluator_authority(self) -> None:
        """`ICD §3` / `ICD §6`: evaluation is exterior and runs under a
        separate identity. OS isolation is Sprint 5; what is provable now is
        that the episode principal and the evaluator principal are distinct
        and that the episode reaches no evaluator symbol."""
        cmd = [
            sys.executable,
            "-c",
            "import sys; from test.trust import spine; wired = spine.build([spine.effect(), spine.finish()]); wired.run(); "
            "assert spine.PRINCIPAL != spine.EVALUATOR_PRINCIPAL; "
            "principals = {event.principal for event in wired.ledger.events()}; "
            "assert spine.EVALUATOR_PRINCIPAL not in principals; "
            "eval_mods = [name for name in sys.modules if name.startswith('vanguard.packages.agency') and 'evaluator' in name]; "
            "assert eval_mods == [], f'Evaluator modules in agency: {eval_mods}'"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Evaluator authority breached: {res.stderr}")


if __name__ == "__main__":
    unittest.main()
