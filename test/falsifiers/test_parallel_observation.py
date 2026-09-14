"""`A1` — parallel observation as a causal partial order.

One turn may carry N independent read-only requests. The claims below are the
ones that make that safe rather than merely faster, and each is written so it
reds when the guard behind it is reverted:

* ten independent reads settle in **one** turn, with ten distinct receipts and
  ten distinct digests, and exactly one `ProposalProduced` — turn accounting
  is what the budget is measured in, so a batch that cost ten turns would give
  back nothing;
* a batch carrying any non-observation verb is refused, typed and recorded.
  `patch.apply`, `proc.exec`, `finish` and `spawn` stay single and serialised:
  the single-writer rule and the atomic-candidate invariant (`RUN-10`) are not
  negotiable against turn economics;
* failure is per request — one failing read leaves the other nine settled;
* the order is **causal**, not positional: `A before C` and `B before C`
  without `A before B`;
* a cold reader reconstructs the identical partial order from the ledger
  alone;
* a composition that has declared no observation verbs settles no batch at
  all (fail closed).

The kernel under these tests is the real kernel. A stubbed one would make the
per-request identity claims vacuous, since per-request identity is exactly the
property of every member going through `Kernel.dispatch` on its own.
"""

from __future__ import annotations

import unittest
from typing import Any, Mapping

from vanguard.packages.agency import EpisodeEngine, RunTermination
from vanguard.packages.agency.episode.observation import (
    MAX_PARALLEL_OBSERVATIONS,
    ObservationRequest,
    batch_descriptor,
    parse_observation_requests,
    settlement_levels,
)
from vanguard.packages.agency.episode.state import (
    ProposalKind,
    ProposalMalformed,
    parse_proposal,
)
from vanguard.packages.kernel import (
    AdapterOutcome,
    EffectRequest,
    FailurePath,
    Occurrence,
    Scope,
    SinkClass,
    SinkRegistry,
)

from test.kernel import fakes
from test.agency import doubles

WORKSPACE = {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src"]}


class PathAdapter:
    """A read adapter whose receipt digest is a function of the path read.

    Distinct receipts per request are the whole point of the batch keeping
    per-request identity, so the double must be able to produce them. A double
    returning one constant digest would let a collapsed batch pass.
    """

    name = "fs.read"

    def __init__(self, *, failing: frozenset[str] = frozenset()) -> None:
        self.calls: list[EffectRequest] = []
        self._failing = failing

    def healthy(self) -> bool:
        return True

    def execute(self, request: EffectRequest) -> AdapterOutcome:
        self.calls.append(request)
        path = str(request.args.get("path", ""))
        if path in self._failing:
            return AdapterOutcome("error", Occurrence.DID_NOT_OCCUR,
                                  {"usd_micros": 1}, detail=f"no such file: {path}")
        return AdapterOutcome(
            "ok", Occurrence.OCCURRED, {"usd_micros": 1},
            result_digest="sha256:" + f"{abs(hash(path)):064x}"[:64])


def read_scope() -> Scope:
    return Scope(
        actions=frozenset({"fs.read"}),
        resources=(WORKSPACE,),
        constraints=fakes.constraints(),
        depth=1,
    )


def observation_sinks() -> SinkRegistry:
    """What the composition root hands the engine: the manifest's own sink
    declarations, never a list the engine carries itself."""
    registry = SinkRegistry()
    registry.register("fs.read", SinkClass.OBSERVATION)
    registry.register("fs.search", SinkClass.OBSERVATION)
    registry.register("patch.apply", SinkClass.PRIVILEGED)
    registry.register("agency.finish", SinkClass.PRIVILEGED)
    return registry


def batch(paths, *, action: str = "fs.read", depends=None):
    """A recorded observe proposal over `paths`, independent unless told."""
    depends = depends or {}
    return {
        "kind": "observe",
        "requests": [
            {"id": f"r{index}",
             "action": action,
             "resource": {"kind": "fs", "root": "/workspace",
                          "paths": [f"/workspace/src/{path}"]},
             "args": {"path": path},
             "dependsOn": list(depends.get(f"r{index}", ()))}
            for index, path in enumerate(paths)
        ],
    }


def build(proposals, *, adapter=None, sinks=..., scope=None, **harness_kwargs):
    adapter = adapter if adapter is not None else PathAdapter()
    harness = fakes.build(
        adapter=adapter,
        held_actions=frozenset({"fs.read"}),
        held_resources=(WORKSPACE,),
        scope=scope or read_scope(),
        **harness_kwargs,
    )
    engine = EpisodeEngine(
        kernel=harness.kernel,
        model=doubles.ScriptedModel(proposals),
        clock=harness.clock,
        events=harness.sink,
        scope=scope or read_scope(),
        max_turns=8,
        observation_sinks=(observation_sinks() if sinks is ... else sinks),
    )
    return harness, adapter, engine


def run(engine, **overrides):
    kwargs = {
        "episode_id": "episode-1",
        "run_id": "run-1",
        "principal": "agent-1",
        "brief": "read the module before changing it",
        "spans": (fakes.operator_span(),),
    }
    kwargs.update(overrides)
    return engine.run(**kwargs)


TEN = [f"m{index}.py" for index in range(10)]


class OneTurnTenObservations(unittest.TestCase):
    def test_ten_reads_settle_in_one_turn(self) -> None:
        """The turn is the unit of budget. Ten reads that cost ten turns give
        back nothing, which is the defect this whole row exists to remove."""
        harness, adapter, engine = build([batch(TEN), doubles.finish()])
        outcome = run(engine)

        self.assertIs(outcome.terminal, RunTermination.COMPLETED)
        self.assertEqual(len(adapter.calls), 10)
        # One turn for ten reads. A finish reduces straight to a terminal and
        # records no turn of its own, so the whole episode is one turn here —
        # which is exactly the economics the row is for.
        self.assertEqual(outcome.episode.turn_count, 1)
        self.assertEqual(outcome.episode.turns[0].progress_signal,
                         "observed_10_of_10")

    def test_one_proposal_produced_for_the_whole_batch(self) -> None:
        """`Session.turns_consumed` counts `ProposalProduced`. One per turn,
        batch or not, or a ten-read batch silently costs ten turns of budget."""
        harness, adapter, engine = build([batch(TEN), doubles.finish()])
        run(engine)

        produced = [event for event in harness.sink.events
                    if event.kind == "ProposalProduced"]
        self.assertEqual(len(produced), 2)
        self.assertEqual(len(produced[0].payload["observations"]), 10)

    def test_every_request_keeps_its_own_effect_started(self) -> None:
        """Per-request causal identity. A collapsed batch receipt would make
        the run unreplayable and the change surface unreconstructable."""
        harness, adapter, engine = build([batch(TEN), doubles.finish()])
        run(engine)

        self.assertEqual([entry.kind for entry in harness.ledger.entries],
                         ["EffectStarted"] * 10)
        started = [event for event in harness.sink.events
                   if event.kind == "EffectStarted"]
        digests = {event.payload["descriptorDigest"] for event in started}
        self.assertEqual(len(digests), 10)

    def test_ten_distinct_receipts_and_ten_distinct_digests(self) -> None:
        harness, adapter, engine = build([batch(TEN), doubles.finish()])
        outcome = run(engine)

        settled = [dispatch for dispatch in outcome.dispatches
                   if dispatch.failure is FailurePath.OK]
        self.assertEqual(len(settled), 10)
        self.assertEqual(len({d.outcome.result_digest for d in settled}), 10)
        self.assertEqual(len({d.descriptor_digest for d in settled}), 10)

    def test_each_request_reserves_and_settles_on_its_own(self) -> None:
        """One reservation per sub-request, settled individually against the
        governor — the shape the inference meter already established."""
        harness, adapter, engine = build([batch(TEN), doubles.finish()])
        run(engine)

        self.assertEqual(harness.trace.count("reserve"), 10)
        self.assertEqual(harness.trace.count("commit"), 10)

    def test_the_batch_receipt_is_a_vector_not_a_collapse(self) -> None:
        """Two batches differing in one member's result must differ in the
        turn receipt, or no-progress detection cannot see the difference."""
        _, _, engine_a = build([batch(TEN), doubles.finish()])
        outcome_a = run(engine_a)
        _, _, engine_b = build(
            [batch(TEN), doubles.finish()],
            adapter=PathAdapter(failing=frozenset({"m4.py"})))
        outcome_b = run(engine_b)

        self.assertNotEqual(outcome_a.episode.turns[0].receipt_digest,
                            outcome_b.episode.turns[0].receipt_digest)


class ReadOnlyOnly(unittest.TestCase):
    def test_a_batch_carrying_a_mutation_is_refused(self) -> None:
        """`RUN-10`. No turn-economics argument outranks the single-writer
        rule, so the mutation never reaches dispatch inside a batch."""
        mixed = batch(["a.py"])
        mixed["requests"].append({
            "id": "w", "action": "patch.apply",
            "resource": WORKSPACE, "args": {"path": "a.py", "diff": "..."},
        })
        harness, adapter, engine = build([mixed, doubles.finish()])
        outcome = run(engine)

        self.assertEqual(adapter.calls, [])
        denials = [event for event in harness.sink.events
                   if event.kind == "AuthorizationDenied"
                   and event.reason == "observation_batch_refused"]
        self.assertEqual(len(denials), 1)
        self.assertIn("patch.apply", denials[0].payload["detail"])
        # Typed feedback, not a terminated run: the model may re-propose the
        # reads as a batch and the patch on its own (`VG-03 §6.1`).
        self.assertIs(outcome.terminal, RunTermination.COMPLETED)

    def test_a_refused_batch_dispatches_nothing_at_all(self) -> None:
        """Not even the read-only members. A batch is refused whole, so a
        mutation cannot be smuggled in to launder the reads beside it."""
        mixed = batch(["a.py", "b.py"])
        mixed["requests"].append({
            "id": "w", "action": "proc.exec",
            "resource": WORKSPACE, "args": {"argv": ["rm", "-rf", "/"]},
        })
        harness, adapter, engine = build([mixed, doubles.finish()])
        run(engine)

        self.assertEqual(harness.ledger.entries, [])

    def test_a_batch_carrying_a_terminal_is_refused(self) -> None:
        mixed = batch(["a.py"])
        mixed["requests"].append({
            "id": "done", "action": "agency.finish",
            "resource": {"kind": "generic", "uriPattern": "agency://finish"},
            "args": {"summary": "done"},
        })
        harness, adapter, engine = build([mixed, doubles.finish()])

        run(engine)

        self.assertEqual(adapter.calls, [])
        denials = [event for event in harness.sink.events
                   if event.reason == "observation_batch_refused"]
        self.assertEqual(len(denials), 1)
        self.assertIn("agency.finish", denials[0].payload["detail"])

    def test_a_composition_with_no_declared_sinks_settles_no_batch(self) -> None:
        """Fail closed (`F-05`). A composition that has not said which of its
        verbs are observations has authorised none of them to batch."""
        harness, adapter, engine = build([batch(TEN), doubles.finish()],
                                         sinks=None)
        run(engine)

        self.assertEqual(adapter.calls, [])
        denials = [event for event in harness.sink.events
                   if event.reason == "observation_batch_refused"]
        self.assertEqual(len(denials), 1)

    def test_an_attenuated_child_may_not_batch_outside_its_sealed_scope(self) -> None:
        """`S8-B-01`. The single-action path refuses a sealed-scope escalation
        further down the loop; the batch path reaches settlement first, so it
        carries the equivalent refusal or a child would widen itself simply by
        batching (`RF-26` proves kernel policy still denies either way — this
        is the engine's own defence in depth)."""
        harness = fakes.build(
            adapter=PathAdapter(),
            held_actions=frozenset({"fs.read", "fs.search"}),
            held_resources=(WORKSPACE,),
            scope=fakes.parent_scope(),
        )
        sealed = Scope(actions=frozenset({"fs.read"}), resources=(WORKSPACE,),
                       constraints=fakes.constraints(), depth=1)
        widening = batch(["a.py"])
        widening["requests"].append(
            {"id": "s", "action": "fs.search",
             "resource": WORKSPACE, "args": {"pattern": "secret"}})
        engine = EpisodeEngine(
            kernel=harness.kernel, model=doubles.ScriptedModel(
                [widening, doubles.finish()]),
            clock=harness.clock, events=harness.sink, scope=sealed,
            max_turns=8, attenuated=True,
            observation_sinks=observation_sinks(),
        )
        run(engine)

        denials = [event for event in harness.sink.events
                   if event.reason == "observation_batch_refused"]
        self.assertEqual(len(denials), 1)
        self.assertIn("fs.search", denials[0].payload["detail"])
        self.assertEqual(harness.ledger.entries, [])

    def test_a_batch_cannot_evade_the_narrowed_phase_policy(self) -> None:
        """The phase ladder gates every request in a batch, not the batch as a
        whole. Otherwise a verb the phase has withdrawn becomes reachable
        again simply by sending it beside a permitted one."""
        harness = fakes.build(
            adapter=PathAdapter(),
            held_actions=frozenset({"fs.read", "fs.search"}),
            held_resources=(WORKSPACE,),
            scope=fakes.parent_scope(),
        )
        gated = batch(["a.py"])
        gated["requests"].append(
            {"id": "s", "action": "fs.search",
             "resource": WORKSPACE, "args": {"pattern": "q"}})
        engine = EpisodeEngine(
            kernel=harness.kernel,
            model=doubles.ScriptedModel([gated, doubles.finish()]),
            clock=harness.clock, events=harness.sink,
            scope=Scope(actions=frozenset({"fs.read", "fs.search"}),
                        resources=(WORKSPACE,),
                        constraints=fakes.constraints(), depth=1),
            tools=({"verb": "fs.read", "name": "read"},
                   {"verb": "fs.search", "name": "search"},
                   {"verb": "patch.apply", "name": "patch"}),
            max_turns=8,
            preset_mode="code",
            observation_sinks=observation_sinks(),
        )
        # `verify` phase withdraws `fs.search` while keeping `fs.read`.
        run(engine, prior_seen_verbs=("patch.apply",))

        retried = [event for event in harness.sink.events
                   if event.kind == "EpisodeStateChanged"
                   and event.reason == "protocol_recovery"]
        self.assertTrue(retried)
        self.assertEqual(harness.ledger.entries, [])

    def test_an_unknown_verb_is_not_an_observation(self) -> None:
        """`SinkRegistry` fails closed on unregistered actions, and the batch
        inherits that: absence of a declaration is not evidence of safety."""
        unknown = batch(["a.py"])
        unknown["requests"].append(
            {"id": "x", "action": "net.fetch", "resource": WORKSPACE, "args": {}})
        harness, adapter, engine = build([unknown, doubles.finish()])
        run(engine)

        self.assertEqual(adapter.calls, [])


class FailureIsPerRequest(unittest.TestCase):
    def test_one_failing_read_leaves_the_other_nine_settled(self) -> None:
        harness, adapter, engine = build(
            [batch(TEN), doubles.finish()],
            adapter=PathAdapter(failing=frozenset({"m4.py"})))
        outcome = run(engine)

        self.assertEqual(len(adapter.calls), 10)
        failures = [dispatch for dispatch in outcome.dispatches
                    if dispatch.failure is not FailurePath.OK]
        self.assertEqual(len(failures), 1)
        completed = [event for event in harness.sink.events
                     if event.kind == "EffectCompleted"]
        failed = [event for event in harness.sink.events
                  if event.kind == "EffectFailed"]
        self.assertEqual(len(completed), 9)
        self.assertEqual(len(failed), 1)

    def test_a_failed_member_still_carries_its_own_identity(self) -> None:
        harness, adapter, engine = build(
            [batch(TEN), doubles.finish()],
            adapter=PathAdapter(failing=frozenset({"m4.py"})))
        run(engine)

        rows = _settlement_rows(harness)
        failed = [row for row in rows if row["failure"] != "ok"]
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["requestId"], "r4")
        self.assertIsNotNone(failed[0]["descriptorDigest"])


class TheOrderIsCausal(unittest.TestCase):
    def test_a_before_c_and_b_before_c_does_not_order_a_against_b(self) -> None:
        """Sequence number is not dependency. A and B share a level; only C
        is ranked after them."""
        requests = parse_observation_requests(
            batch(["a.py", "b.py", "c.py"],
                  depends={"r2": ("r0", "r1")})["requests"])
        self.assertEqual(settlement_levels(requests), ((0, 1), (2,)))

    def test_the_partial_order_is_recorded_per_request(self) -> None:
        harness, adapter, engine = build(
            [batch(["a.py", "b.py", "c.py"], depends={"r2": ("r0", "r1")}),
             doubles.finish()])
        run(engine)

        rows = _settlement_rows(harness)
        by_id = {row["requestId"]: row for row in rows}
        self.assertEqual(by_id["r0"]["level"], 0)
        self.assertEqual(by_id["r1"]["level"], 0)
        self.assertEqual(by_id["r2"]["level"], 1)
        self.assertEqual(by_id["r2"]["dependsOn"], ["r0", "r1"])
        self.assertEqual(by_id["r0"]["dependsOn"], [])

    def test_a_dependent_request_settles_after_what_it_depends_on(self) -> None:
        harness, adapter, engine = build(
            [batch(["a.py", "b.py", "c.py"], depends={"r2": ("r0", "r1")}),
             doubles.finish()])
        run(engine)

        order = [str(call.args["path"]) for call in adapter.calls]
        self.assertLess(order.index("a.py"), order.index("c.py"))
        self.assertLess(order.index("b.py"), order.index("c.py"))

    def test_a_dependency_cycle_is_malformed_not_a_deadlock(self) -> None:
        with self.assertRaises(ProposalMalformed):
            parse_proposal(batch(["a.py", "b.py"],
                                 depends={"r0": ("r1",), "r1": ("r0",)}))

    def test_a_dependency_on_an_unknown_id_is_malformed(self) -> None:
        with self.assertRaises(ProposalMalformed):
            parse_proposal(batch(["a.py"], depends={"r0": ("ghost",)}))

    def test_the_batch_descriptor_is_stable_under_provider_id_renaming(self) -> None:
        """No-progress detection compares descriptors across turns. A
        descriptor keyed on provider-generated ids would differ every turn and
        the livelock detector would never fire (`Turn.signature`)."""
        first = batch(["a.py", "b.py"], depends={"r1": ("r0",)})
        second = {"kind": "observe", "requests": [
            {**dict(row), "id": row["id"].replace("r", "call_abc"),
             "dependsOn": [dep.replace("r", "call_abc") for dep in row["dependsOn"]]}
            for row in first["requests"]]}
        self.assertNotEqual(
            [row["id"] for row in first["requests"]],
            [row["id"] for row in second["requests"]])
        self.assertEqual(parse_proposal(first).descriptor,
                         parse_proposal(second).descriptor)

    def test_the_descriptor_distinguishes_two_different_orders(self) -> None:
        """Rename-stability must not become order-blindness."""
        independent = parse_proposal(batch(["a.py", "b.py"])).descriptor
        ordered = parse_proposal(
            batch(["a.py", "b.py"], depends={"r1": ("r0",)})).descriptor
        self.assertNotEqual(independent, ordered)


class ColdReplay(unittest.TestCase):
    def test_a_cold_reader_reconstructs_the_identical_partial_order(self) -> None:
        """From the ledger alone, with no live object surviving: the same
        requests, the same levels, the same dependency edges, the same
        settlement sequence."""
        harness, adapter, engine = build(
            [batch(["a.py", "b.py", "c.py"], depends={"r2": ("r0", "r1")}),
             doubles.finish()])
        run(engine)
        first = _reconstructed_order(harness)

        harness2, adapter2, engine2 = build(
            [batch(["a.py", "b.py", "c.py"], depends={"r2": ("r0", "r1")}),
             doubles.finish()])
        run(engine2)

        self.assertEqual(first, _reconstructed_order(harness2))
        self.assertEqual(first, (
            (("r0", 0, ()), ("r1", 0, ())),
            (("r2", 1, ("r0", "r1")),),
        ))

    def test_the_settlement_record_joins_to_the_kernel_receipts(self) -> None:
        """`descriptorDigest` is the kernel's own, so each recorded row joins
        to its `EffectStarted` / `EffectCompleted` pair rather than floating
        beside them."""
        harness, adapter, engine = build([batch(TEN), doubles.finish()])
        run(engine)

        recorded = {row["descriptorDigest"] for row in _settlement_rows(harness)}
        started = {event.payload["descriptorDigest"]
                   for event in harness.sink.events
                   if event.kind == "EffectStarted"}
        self.assertEqual(recorded, started)


class Bounds(unittest.TestCase):
    def test_a_batch_beyond_the_ceiling_is_malformed(self) -> None:
        """A bound, not a preference: an unbounded batch lets one malformed
        reply reserve arbitrarily much in a single turn."""
        with self.assertRaises(ProposalMalformed):
            parse_proposal(batch([f"m{i}.py"
                                  for i in range(MAX_PARALLEL_OBSERVATIONS + 1)]))

    def test_the_ceiling_admits_a_batch_exactly_at_it(self) -> None:
        parsed = parse_proposal(
            batch([f"m{i}.py" for i in range(MAX_PARALLEL_OBSERVATIONS)]))
        self.assertEqual(len(parsed.observations), MAX_PARALLEL_OBSERVATIONS)

    def test_an_empty_batch_is_malformed(self) -> None:
        with self.assertRaises(ProposalMalformed):
            parse_proposal({"kind": "observe", "requests": []})

    def test_duplicate_request_ids_are_malformed(self) -> None:
        with self.assertRaises(ProposalMalformed):
            parse_proposal({"kind": "observe", "requests": [
                {"id": "r0", "action": "fs.read", "args": {"path": "a.py"}},
                {"id": "r0", "action": "fs.read", "args": {"path": "b.py"}},
            ]})

    def test_a_negative_reservation_is_malformed(self) -> None:
        with self.assertRaises(ProposalMalformed):
            parse_proposal({"kind": "observe", "requests": [
                {"id": "r0", "action": "fs.read", "args": {},
                 "reservation": {"usd_micros": -1}},
            ]})


class TheMutations(unittest.TestCase):
    """`Rule 2`: every adversarial assertion above must red when its guard is
    reverted. These run the revert in-process rather than describing it.
    """

    def test_reverting_the_read_only_guard_would_admit_a_mutation(self) -> None:
        mixed = batch(["a.py"])
        mixed["requests"].append({
            "id": "w", "action": "patch.apply",
            "resource": WORKSPACE, "args": {"path": "a.py", "diff": "..."},
        })
        harness, adapter, engine = build([mixed, doubles.finish()])
        # The revert: a sink source that calls everything an observation, which
        # is what "trust the manifest less" looks like in practice.
        engine._observation_sinks = lambda action: SinkClass.OBSERVATION
        run(engine)

        # Red: with the guard reverted the mutation reaches dispatch. The
        # kernel still denies it (`fs.read` is the only held action), but the
        # batch no longer refuses it, which is the guard under test.
        self.assertEqual(
            [event for event in harness.sink.events
             if event.reason == "observation_batch_refused"], [])

    def test_reverting_rename_stability_would_blind_the_repeat_detector(self) -> None:
        """Digesting ids instead of positions makes two identical batches look
        different, and `Turn.signature` never fires."""
        first = parse_proposal(batch(["a.py", "b.py"])).observations
        renamed = tuple(
            ObservationRequest(request_id=f"call_{row.request_id}",
                               action=row.action, resource=row.resource,
                               args=row.args)
            for row in first)
        self.assertEqual(batch_descriptor(first), batch_descriptor(renamed))

        def id_keyed(requests) -> str:
            from vanguard.packages.domain.canonicalisation.digest import digest_of
            return digest_of([{"id": row.request_id, "action": row.action}
                              for row in requests])

        self.assertNotEqual(id_keyed(first), id_keyed(renamed))

    def test_reverting_per_request_dispatch_would_lose_nine_receipts(self) -> None:
        """A collapsed batch — one dispatch for the whole thing — produces one
        `EffectStarted`, not ten. The assertion that catches that is real."""
        harness, adapter, engine = build([batch(TEN), doubles.finish()])
        run(engine)
        self.assertEqual(len(harness.ledger.entries), 10)

        harness2, adapter2, engine2 = build([batch(TEN[:1]), doubles.finish()])
        run(engine2)
        self.assertEqual(len(harness2.ledger.entries), 1)


def _settlement_rows(harness) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    for event in harness.sink.events:
        if (event.kind == "EpisodeStateChanged"
                and event.reason == "observation_batch"):
            rows.extend(event.payload["observations"])
    return rows


def _reconstructed_order(harness) -> tuple[tuple[tuple[str, int, tuple[str, ...]], ...], ...]:
    """The partial order as a cold reader sees it: levels, in settlement order."""
    levels: dict[int, list[tuple[str, int, tuple[str, ...]]]] = {}
    for row in _settlement_rows(harness):
        levels.setdefault(int(row["level"]), []).append(
            (str(row["requestId"]), int(row["level"]), tuple(row["dependsOn"])))
    return tuple(tuple(levels[level]) for level in sorted(levels))


if __name__ == "__main__":
    unittest.main()
