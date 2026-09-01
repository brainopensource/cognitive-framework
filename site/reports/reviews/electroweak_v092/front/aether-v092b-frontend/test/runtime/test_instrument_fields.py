"""What a benchmarked run must carry to be measurable (`S9-A-01`…`S9-A-04`).

Sprint 9 is the instrument. It reports turns, tokens and cost per arm, and it
attributes differences to components. Neither is possible against a `RunResult`
that does not say which components were active or what the run cost.

Two disciplines are asserted here rather than assumed:

  - **Integers are the truth** (`S6B-MD-009`). Cost is USD micros, time is
    integer milliseconds, tokens are counts. A float that has been through a
    division is a number that no longer sums, and a corpus of them cannot be
    re-added to check itself.
  - **An absent measurement is absent, not zero.** A run whose provider never
    answered has `None` tokens and an `instrument_error` reason. Reporting `0`
    would make a failed instrument look like a free run, which is exactly the
    degenerate-row problem Sprint 7 spent itself removing.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeEnvironment
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.root import (
    HarnessSession,
    RunResult,
    Runtime,
    SessionPorts,
    TaskContext,
)
from vanguard.packages.runtime.telemetry import RunTelemetry


def _session(script, *, episode_id: str = "ep-instr-1", **overrides):
    ports = SessionPorts(
        model=ScriptedModel(script),
        environment=FakeEnvironment(),
        clock=FixedClock(at="2026-08-17T00:00:00.000Z", step_ms=1),
        random=SeededRandom(seed=9),
        store=SqliteEventStore(":memory:"),
        interactive=False,
        **overrides,
    )
    task = TaskContext(
        brief="instrument probe", repo_path=Path("/workspace"),
        run_id="run-instr-1", episode_id=episode_id, max_turns=4)
    return HarnessSession(
        Runtime.compose("vg-code-default", episode_id=episode_id), ports, task)


class RunResultCarriesTheComposition(unittest.TestCase):
    """`S9-A-01`. Attribution needs to know which components were active."""

    def test_gene_digests_reach_the_result(self) -> None:
        result = _session([finish()]).run()
        self.assertTrue(result.gene_digests)

    def test_gene_digests_match_the_harness_they_ran(self) -> None:
        session = _session([finish()])
        result = session.run()
        self.assertEqual(dict(result.gene_digests),
                         dict(session.harness.gene_digests))

    def test_the_composition_digest_is_dh_not_episode_bound(self) -> None:
        """ADR-0076 §4: D_H is composition identity; episode_id is not in it."""

        first = _session([finish()], episode_id="ep-a").run()
        again = _session([finish()], episode_id="ep-a").run()
        other = _session([finish()], episode_id="ep-b").run()
        self.assertTrue(first.composition_digest)
        self.assertEqual(first.composition_digest, again.composition_digest)
        self.assertEqual(first.composition_digest, other.composition_digest)

    def test_gene_digests_are_the_cross_run_pack_identity(self) -> None:
        """What attribution actually groups on."""

        first = _session([finish()], episode_id="ep-a").run()
        other = _session([finish()], episode_id="ep-b").run()
        self.assertEqual(dict(first.gene_digests), dict(other.gene_digests))

    def test_two_packs_give_two_composition_digests(self) -> None:
        """A digest that does not move between packs cannot attribute anything."""

        default = Runtime.compose("vg-code-default", episode_id="e")
        shell = Runtime.compose("vg-shell-only", episode_id="e")
        self.assertNotEqual(default.composition_digest, shell.composition_digest)


class TelemetryIsIntegral(unittest.TestCase):
    """`S9-A-02` / `S6B-MD-009`. No float is ever the truth."""

    def test_every_reported_quantity_is_an_int_or_absent(self) -> None:
        result = _session([finish()]).run()
        telemetry = result.telemetry
        for name in ("turns", "prompt_tokens", "completion_tokens",
                     "usd_micros", "wall_millis"):
            value = getattr(telemetry, name)
            with self.subTest(field=name):
                self.assertTrue(value is None or isinstance(value, int),
                                f"{name}={value!r} is neither int nor None")
                self.assertNotIsInstance(value, float)

    def test_total_tokens_is_the_sum_and_not_a_rounded_float(self) -> None:
        telemetry = RunTelemetry(turns=2, prompt_tokens=101,
                                 completion_tokens=57, usd_micros=13,
                                 wall_millis=9)
        self.assertEqual(telemetry.total_tokens, 158)
        self.assertIsInstance(telemetry.total_tokens, int)

    def test_absent_token_counts_do_not_become_zero(self) -> None:
        """A provider that never answered did not answer cheaply."""

        telemetry = RunTelemetry(turns=1)
        self.assertIsNone(telemetry.prompt_tokens)
        self.assertIsNone(telemetry.total_tokens)

    def test_turns_are_counted_from_the_ledger(self) -> None:
        session = _session([finish()])
        result = session.run()
        self.assertEqual(result.telemetry.turns, session.turns_consumed())


class InstrumentErrorIsNamedPerArm(unittest.TestCase):
    """`S9-A-01`. A run that failed to be measured is not a measured failure."""

    def test_a_clean_run_reports_no_instrument_error(self) -> None:
        result = _session([finish()]).run()
        self.assertIsNone(result.instrument_error)

    def test_a_provider_failure_is_recorded_as_an_instrument_error(self) -> None:
        from test.agency.doubles import RaisingModel

        session = _session([finish()])
        session.operator._model = RaisingModel()
        result = session.run()
        self.assertEqual(result.instrument_error, "model_not_invoked")

    def test_an_instrument_error_run_reports_no_fabricated_cost(self) -> None:
        from test.agency.doubles import RaisingModel

        session = _session([finish()])
        session.operator._model = RaisingModel()
        result = session.run()
        self.assertIsNone(result.telemetry.prompt_tokens)


class RecordingSufficiencyIsAudited(unittest.TestCase):
    """`S9-A-03`. Replay needs the digests, and the audit is executable."""

    def test_the_result_names_every_digest_replay_requires(self) -> None:
        result = _session([finish()]).run()
        missing = result.replay_gaps()
        self.assertEqual(missing, (), f"Recording cannot replay this run: {missing}")

    def test_the_audit_reports_a_gap_rather_than_hiding_it(self) -> None:
        """The check must be able to fail, or it is not a check (`A-10`)."""

        import dataclasses

        result = _session([finish()]).run()
        stripped = dataclasses.replace(result, gene_digests={})
        self.assertIn("gene_digests", stripped.replay_gaps())
        self.assertNotIn("gene_digests", result.replay_gaps())


class LedgerQueriesForThePairedRunner(unittest.TestCase):
    """`S9-A-04`. Lane C's paired runner reads the ledger, not the objects."""

    def test_a_run_exposes_its_episode_reduction(self) -> None:
        session = _session([finish()])
        session.run()
        self.assertIsNotNone(session.ledger_state().episode_id)

    def test_the_state_digest_is_available_for_pairing(self) -> None:
        """The paired runner needs a digest it can *recompute*, not one that
        merely round-trips through a live object.

        This used to assert `result.state_digest == session.state_digest()`.
        Both were then re-reads of the ledger *after* the terminal event, and
        that event carries the trajectory, which carries the digest -- so the
        value summarised a state containing itself and no fresh process could
        reproduce it (D9). The run-close digest now folds exactly the events
        the trajectory declares, so the property worth pinning is that a cold
        fold of that range returns it.
        """
        from vanguard.packages.domain.ledger.reducer import (
            compute_state_digest, reconstruct_state,
        )
        from vanguard.packages.ports.event_store import EventRange

        session = _session([finish()])
        result = session.run()
        last = (result.trajectory or {})["event_range"]["last_seq"]
        events = list(session.ports.store.read(
            EventRange(episode_id=session.task.episode_id)).value or [])
        named = [event for event in events if int(event.seq) <= int(last)]

        self.assertEqual(compute_state_digest(reconstruct_state(named)),
                         result.state_digest)


if __name__ == "__main__":
    unittest.main()


class NoVerbLacksABinding(unittest.TestCase):
    """`S10-A-02`. The translator and the binding table must agree.

    `proc.test` sat in the translator's verb table with no entry in
    `DEFAULT_BINDINGS` and no adapter behind it — reachable in principle,
    unwireable in practice. It is deleted rather than bound: tests run as
    allowlisted `proc.exec` (`pytest` is already on that selector), so there is
    one privileged process path with one allowlist instead of two that have to
    be kept in agreement (`D-04`).
    """

    def test_every_bound_verb_has_a_worker_operation_or_an_environment_one(self) -> None:
        from vanguard.packages.adapters.sandbox.worker import WorkerProtocol
        from vanguard.packages.runtime.root import DEFAULT_BINDINGS

        # Sandbox worker operations plus in-process mediated delegation (M-6 agent.spawn)
        supported = set(WorkerProtocol.SUPPORTED_OPERATIONS) | {"agent.spawn"}
        self.assertTrue(set(DEFAULT_BINDINGS) <= supported,
                        f"bound but unsupported: {sorted(set(DEFAULT_BINDINGS) - supported)}")

    def test_the_worker_supports_no_operation_nothing_can_bind(self) -> None:
        """The other direction: an operation with no binding is an orphan."""

        from vanguard.packages.adapters.sandbox.worker import WorkerProtocol
        from vanguard.packages.runtime.root import DEFAULT_BINDINGS

        orphans = set(WorkerProtocol.SUPPORTED_OPERATIONS) - set(DEFAULT_BINDINGS)
        self.assertEqual(orphans, set(), f"unbindable worker operations: {sorted(orphans)}")

    def test_the_deleted_verb_is_gone_from_the_runtime_and_the_sandbox(self) -> None:
        from pathlib import Path

        packages = Path(__file__).resolve().parents[2] / "vanguard" / "packages"
        for module in ("runtime/root.py", "runtime/compose.py", "runtime/session.py",
                       "runtime/wiring.py", "adapters/sandbox/worker.py",
                       "adapters/environment/sandboxed.py",
                       "adapters/models/invocation.py"):
            source = (packages / module).read_text(encoding="utf-8")
            code = "\n".join(line for line in source.splitlines()
                             if not line.lstrip().startswith("#"))
            with self.subTest(module=module):
                self.assertNotIn("proc.test", code)
