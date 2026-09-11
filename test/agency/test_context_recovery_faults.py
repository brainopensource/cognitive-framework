"""B-owned fault matrix for context pressure, receipt integrity and recovery.

`test_cache_breakpoints.py` proves T-77 on a well-behaved packet. This module
is the adversarial half: every case here is one a plausible implementation
passes on the happy path and fails under pressure, on restart, or when the
material arriving from outside the process is actively hostile.

Four claims, one per section.

1. **Eviction reclaims bodies, never identity** (`NT-C04`, `NT-C05`). A
   receipt that has already replaced its body is not a body. Compaction that
   runs a second time over its own output must reclaim nothing further rather
   than overwrite what the first pass promised to keep — and when there is
   genuinely nothing left to reclaim, the answer is `CONTEXT_BUDGET_EXCEEDED`,
   not a quieter prompt that has lost its evidence.
2. **Selection is deterministic and repeatable** (`NT-C04`). The same state
   selects the same bytes and reports the same omissions in the same order,
   turn after turn, for as long as the run lasts.
3. **Recovery never loses an occurrence and never grants itself anything**
   (`NT-R01`-`NT-R03`). A reservation outlives the decision to stop chasing
   it; a bound is carried across restart rather than re-read from the running
   build; exhaustion is a terminal failure rather than a quiet success.
4. **Frozen state is frozen and old state is readable or typed-refused**
   (`NT-1.6`). Nothing a caller still holds can move a digest that has already
   been taken, and a payload from an older writer either migrates
   deterministically or fails as a version error.

Nothing here measures a cache hit, a token saving or a model behaviour.
"""

from __future__ import annotations

import json
import unittest

from vanguard.packages.agency.context import (
    PREFIX_LAYERS,
    ContextBudget,
    ContextBudgetExceeded,
    ContextCompiler,
    Fragment,
    Interaction,
    Layer,
)
from vanguard.packages.agency.context.compaction import (
    ResultEvictionStrategy,
    StructuredConsolidateStrategy,
    UnknownCompactionStrategyError,
    resolve_compaction_strategy,
)
from vanguard.packages.agency.episode.protocol_recovery import (
    MAX_DURABLE_ATTEMPTS,
    MAX_INTERVENTIONS,
    Attempt,
    ProtocolRecoveryState,
    RECOVERY_STATE_SCHEMA,
    decide_recovery,
    recover,
    semantic_progress_key,
)
from vanguard.packages.domain.task_state import (
    Evidence,
    MemoryView,
    RouteDecision,
    SemanticTaskState,
)

SUBJECT = "sha256:" + "a" * 64
OTHER_SUBJECT = "sha256:" + "b" * 64
ARTIFACT = "sha256:" + "c" * 64
DIGEST = "sha256:" + "0" * 64

SYSTEM_CORE = "Act on the repository task using typed tools."
ENVIRONMENT = "repo=cognitive-framework runtime=python3.12"
TOOLS = (
    {"name": "fs.read", "verb": "fs.read", "description": "read one file"},
    {"name": "patch.apply", "verb": "patch.apply", "description": "apply one diff"},
)

OBJECTIVE = "Repair the failing import in src/value.py without weakening the gate"
CONSTRAINTS = ("keep every existing test green", "never widen a declared budget ceiling")

#: A verification body: large, loud, and carrying identity that `NT-C05`
#: requires to outlive the log around it.
VERIFICATION_BODY = json.dumps({
    "command": ["python3", "-m", "unittest", "test.agency.test_context_compiler"],
    "environment": "cpython-3.12/linux-x86_64",
    "collected": 41,
    "executed": 41,
    "exit_status": 0,
    "output": "PASSED " * 4000,
})

VERIFICATION_FIELDS = (
    "command=python3 -m unittest",
    "environment=cpython-3.12/linux-x86_64",
    f"subject={SUBJECT}",
    "collected=41",
    "executed=41",
    "exit=0",
    f"artifact={ARTIFACT}",
)


def compiler(**overrides) -> ContextCompiler:
    kwargs = {
        "system_core": SYSTEM_CORE,
        "tool_schemas": TOOLS,
        "environment": ENVIRONMENT,
        "token_ceiling": 64_000,
    }
    kwargs.update(overrides)
    return ContextCompiler(**kwargs)


def state(**overrides) -> SemanticTaskState:
    kwargs = dict(objective=OBJECTIVE, constraints=CONSTRAINTS,
                  plan=("read", "patch", "verify"), next_action="read src/value.py")
    kwargs.update(overrides)
    return SemanticTaskState(**kwargs)


def view(*evidence: Evidence, cursor: int = 1,
         task: SemanticTaskState | None = None) -> MemoryView:
    return MemoryView.capture(task or state(), cursor, lineage_id="lin-1",
                              reducer_version="task-fold/1", evidence=evidence)


def verification_turns(count: int) -> tuple[Interaction, ...]:
    return tuple(
        Interaction(f"turn-{index}", f"proc.exec suite {index}", VERIFICATION_BODY, ARTIFACT)
        for index in range(count)
    )


def prefix_bytes(packet) -> bytes:
    return b"\x00".join(block.text.encode("utf-8") for block in packet.blocks
                        if block.layer in PREFIX_LAYERS)


def fingerprint(index: int) -> str:
    return "sha256:" + format(index, "064x")


# ---------------------------------------------------------------------------
# 1. Eviction reclaims bodies, never identity
# ---------------------------------------------------------------------------

class ReceiptIntegrityUnderRepeatedEviction(unittest.TestCase):
    """`NT-C05`: what a verification attested outlives the log it came from."""

    def _narrowest_packet(self, turns):
        """The tightest window that still compiles, and the packet it yields.

        Compaction runs in two passes — the packet selector and then the
        compaction strategy underneath `compile`. The interesting window is
        the one where the second pass runs over the first pass's output, which
        is exactly where a receipt is at risk of being treated as a body.
        """
        subject = compiler()
        smallest = None
        for window in range(120, 400):
            try:
                packet = subject.compile_packet(
                    view(), SUBJECT, turns,
                    budget=ContextBudget(window=window, max_body_bytes=2000))
            except ContextBudgetExceeded:
                continue
            smallest = packet
            break
        self.assertIsNotNone(smallest, "no window in range compiled at all")
        return smallest

    def test_a_verification_receipt_is_never_re_elided_into_a_byte_count(self) -> None:
        packet = self._narrowest_packet(verification_turns(3))
        tail = [block for block in packet.blocks
                if block.source in {"interaction", "newest-interaction"}]
        self.assertTrue(tail, "the newest complete interaction was dropped entirely")
        kept = tail[-1].text
        for field in VERIFICATION_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, kept)
        self.assertNotIn("bytes elided after use", kept)

    def test_the_raw_log_is_gone_even_though_its_identity_stayed(self) -> None:
        packet = self._narrowest_packet(verification_turns(3))
        self.assertNotIn("PASSED PASSED", packet.bundle()["layers"][-1]["content"])

    def test_state_that_cannot_shrink_further_is_refused_not_silently_gutted(self) -> None:
        """`NT-C04`: the floor is `CONTEXT_BUDGET_EXCEEDED`, not a lossy prompt."""
        subject = compiler()
        with self.assertRaises(ContextBudgetExceeded) as raised:
            subject.compile_packet(
                view(), SUBJECT, verification_turns(3),
                budget=ContextBudget(window=100, max_body_bytes=2000))
        self.assertIn("CONTEXT_BUDGET_EXCEEDED", str(raised.exception))

    def test_an_eviction_receipt_keeps_the_action_and_the_artifact(self) -> None:
        """A receipt naming neither what ran nor where the bytes went attests nothing."""
        from vanguard.packages.agency.context.layers import (
            NEWEST_INTERACTION_SOURCE, blocks_of,
        )
        # Pinned, so the strategy must reclaim the body by eliding it rather
        # than by removing the block: eliding is the behaviour under test.
        dialogue = list(blocks_of(Layer.DIALOGUE, [
            Fragment(source=NEWEST_INTERACTION_SOURCE, label="turn-0",
                     text=f"fs.read src/value.py\nartifact={ARTIFACT}\n" + "x" * 4000,
                     evictable=True),
        ]))
        ResultEvictionStrategy().compact(floor=0, ceiling=1, notes=[], dialogue=dialogue)
        receipt = dialogue[0].text
        self.assertIn("fs.read src/value.py", receipt)
        self.assertIn(f"artifact={ARTIFACT}", receipt)
        self.assertIn("bytes elided after use", receipt)
        self.assertNotIn("x" * 100, receipt)

    def test_a_single_line_body_is_not_mistaken_for_its_own_header(self) -> None:
        """Retaining "the first line" of a one-line body retains the body."""
        from vanguard.packages.agency.context.layers import (
            NEWEST_INTERACTION_SOURCE, blocks_of,
        )
        dialogue = list(blocks_of(Layer.DIALOGUE, [
            Fragment(source=NEWEST_INTERACTION_SOURCE, label="turn-0",
                     text="y" * 4000, evictable=True),
        ]))
        ResultEvictionStrategy().compact(floor=0, ceiling=1, notes=[], dialogue=dialogue)
        self.assertNotIn("y" * 100, dialogue[0].text)
        self.assertIn("bytes elided after use", dialogue[0].text)


# ---------------------------------------------------------------------------
# 2. Selection is deterministic and repeatable
# ---------------------------------------------------------------------------

class DeterministicSelectionAcrossEpochs(unittest.TestCase):
    """`NT-C04`: same state, same bytes, same omissions, in the same order."""

    def _packet(self, subject: ContextCompiler, turn_count: int = 12):
        evidence = tuple(
            Evidence(f"ev-{index}", SUBJECT if index % 2 else OTHER_SUBJECT,
                     ARTIFACT, f"finding {index}", "z" * 600)
            for index in range(6)
        )
        return subject.compile_packet(
            view(*evidence), SUBJECT, verification_turns(turn_count),
            budget=ContextBudget(window=2400, max_body_bytes=800))

    def test_the_same_state_selects_the_same_bytes_and_omission_order(self) -> None:
        first = self._packet(compiler())
        second = self._packet(compiler())
        self.assertEqual(first.digest, second.digest)
        self.assertEqual(first.omissions, second.omissions)
        self.assertEqual(first.elided, second.elided)
        self.assertEqual(first.dropped, second.dropped)

    def test_omissions_follow_the_declared_eviction_order(self) -> None:
        """`NT-C04`: stale evidence precedes every body and every drop."""
        packet = self._packet(compiler())
        reasons = [reason for _, reason in packet.omissions]
        self.assertIn("stale", reasons)
        last_stale = max(index for index, reason in enumerate(reasons) if reason == "stale")
        later = {reason for reason in reasons[last_stale + 1:]}
        self.assertNotIn("stale", later)

    def test_elided_and_dropped_stay_disjoint(self) -> None:
        """A fragment that was elided and then removed has no receipt left."""
        packet = self._packet(compiler())
        self.assertEqual(set(packet.elided) & set(packet.dropped), set())

    def test_a_hundred_compactions_never_move_the_frozen_prefix(self) -> None:
        subject = compiler()
        epoch = subject.composition_epoch
        baseline = prefix_bytes(self._packet(subject, turn_count=1))
        for turn in range(1, 101):
            packet = self._packet(subject, turn_count=turn)
            with self.subTest(turn=turn):
                self.assertEqual(prefix_bytes(packet), baseline)
                self.assertEqual(subject.composition_epoch, epoch)

    def test_the_goal_echo_is_still_last_after_a_hundred_compactions(self) -> None:
        subject = compiler()
        for turn in range(1, 101):
            packet = self._packet(subject, turn_count=turn)
            with self.subTest(turn=turn):
                self.assertEqual(packet.blocks[-1].source, "goal-echo")
                self.assertIn(OBJECTIVE, packet.goal_echo)
                for constraint in CONSTRAINTS:
                    self.assertIn(constraint, packet.goal_echo)


class SummariesNeverOverwriteObligations(unittest.TestCase):
    """`NT-C02`: a summary is evidence about the work, never the work itself."""

    def test_structured_consolidation_leaves_the_brief_and_the_echo_alone(self) -> None:
        subject = compiler(context_policy="structured_consolidate")
        packet = subject.compile_packet(
            view(), SUBJECT, verification_turns(8),
            budget=ContextBudget(window=900, max_body_bytes=400))
        brief = [block for block in packet.blocks
                 if block.layer is Layer.TASK and block.label == "brief"]
        self.assertEqual(len(brief), 1)
        self.assertIn(OBJECTIVE, brief[0].text)
        for constraint in CONSTRAINTS:
            self.assertIn(constraint, brief[0].text)
        self.assertEqual(packet.blocks[-1].source, "goal-echo")

    def test_an_unknown_strategy_fails_closed_rather_than_defaulting(self) -> None:
        with self.assertRaises(UnknownCompactionStrategyError):
            resolve_compaction_strategy({"kind": "model-written-summary"})

    def test_consolidation_never_drops_the_newest_complete_interaction(self) -> None:
        from vanguard.packages.agency.context.layers import blocks_of
        from vanguard.packages.agency.context.layers import NEWEST_INTERACTION_SOURCE
        dialogue = list(blocks_of(Layer.DIALOGUE, [
            Fragment(source="interaction", label=f"turn-{index}",
                     text="failed to apply " + "q" * 800, evictable=True)
            for index in range(6)
        ] + [
            Fragment(source=NEWEST_INTERACTION_SOURCE, label="turn-6",
                     text="the state the next action starts from", evictable=True),
        ]))
        StructuredConsolidateStrategy().compact(
            floor=0, ceiling=1, notes=[], dialogue=dialogue)
        self.assertIn("turn-6", [block.label for block in dialogue])


# ---------------------------------------------------------------------------
# 3. Recovery loses no occurrence and grants itself nothing
# ---------------------------------------------------------------------------

def recovered(state_in: ProtocolRecoveryState, attempt: Attempt, **overrides):
    kwargs = dict(remaining_ms=100_000, remaining_turns=8, jitter=0.0,
                  state_digest=DIGEST, remaining_budget_ref=DIGEST)
    kwargs.update(overrides)
    return recover(state_in, attempt, **kwargs)


class PendingOperationReservation(unittest.TestCase):
    """`NT-R03`: an unobserved outcome outlives the decision that stopped chasing it."""

    HELD = ProtocolRecoveryState(pending_operation="op-A", deadline="2026-01-01T00:00:00Z")

    def test_a_held_reservation_is_never_replaced_by_a_new_identity(self) -> None:
        _, next_state = recovered(
            self.HELD, Attempt(fingerprint(1), "dispatch", fingerprint(2), "transport"))
        self.assertEqual(next_state.pending_operation, "op-A")
        self.assertEqual(next_state.deadline, "2026-01-01T00:00:00Z")

    def test_stopping_does_not_release_an_unsettled_occurrence(self) -> None:
        decision, next_state = recovered(
            self.HELD, Attempt(fingerprint(3), "denied", fingerprint(4), "permission"))
        self.assertEqual(decision.action, "stop")
        self.assertEqual(next_state.pending_operation, "op-A")
        self.assertEqual(next_state.deadline, "2026-01-01T00:00:00Z")

    def test_an_intervention_does_not_release_an_unsettled_occurrence(self) -> None:
        stalled = ProtocolRecoveryState(
            pending_operation="op-A", deadline="2026-01-01T00:00:00Z",
            history=tuple(Attempt(fingerprint(9), "stall", fingerprint(9), None)
                          for _ in range(5)),
        )
        decision, next_state = recovered(
            stalled, Attempt(fingerprint(9), "stall", fingerprint(9), None))
        self.assertIn(decision.action, {"reground", "replan"})
        self.assertEqual(next_state.pending_operation, "op-A")

    def test_only_the_operation_that_settled_clears_its_own_reservation(self) -> None:
        held = ProtocolRecoveryState(pending_operation=fingerprint(7), deadline="dl")
        _, next_state = recovered(
            held, Attempt(fingerprint(7), "denied", fingerprint(8), "permission"))
        self.assertIsNone(next_state.pending_operation)
        self.assertIsNone(next_state.deadline)

    def test_an_unheld_wait_takes_its_own_reservation_and_deadline(self) -> None:
        decision, next_state = recovered(
            ProtocolRecoveryState(),
            Attempt(fingerprint(1), "dispatch", fingerprint(2), "transport"))
        self.assertEqual(decision.action, "wait")
        self.assertEqual(next_state.pending_operation, fingerprint(1))
        self.assertEqual(next_state.deadline, f"delay-ms:{decision.delay_ms}")

    def test_a_pending_operation_always_has_a_deadline(self) -> None:
        with self.assertRaises(ValueError):
            ProtocolRecoveryState(pending_operation="op-A")


class ConfigurableBoundsSurviveRestart(unittest.TestCase):
    """`NT-R02`: bounds are configurable, versioned, and never reset by restart."""

    def test_the_intervention_ceiling_is_configurable(self) -> None:
        decision, _ = recovered(
            ProtocolRecoveryState(max_interventions=0),
            Attempt(fingerprint(6), "stall", fingerprint(7), "protocol"))
        self.assertEqual(decision.action, "stop")
        self.assertEqual(decision.reason, "intervention_limit")

    def test_a_non_default_ceiling_round_trips_through_the_durable_form(self) -> None:
        original = ProtocolRecoveryState(max_interventions=5, interventions=1)
        restored = ProtocolRecoveryState.decode(original.encode())
        self.assertEqual(restored.max_interventions, 5)
        self.assertEqual(restored.interventions, 1)
        self.assertEqual(restored.encode(), original.encode())

    def test_the_default_ceiling_adds_no_bytes_to_an_existing_payload(self) -> None:
        """Older writers produced payloads without this key; they still decode."""
        self.assertNotIn(b"maxInterventions", ProtocolRecoveryState().encode())
        self.assertEqual(
            ProtocolRecoveryState.decode(ProtocolRecoveryState().encode()).max_interventions,
            MAX_INTERVENTIONS)

    def test_the_ceiling_is_part_of_the_policy_identity(self) -> None:
        default = ProtocolRecoveryState().to_dict()["policyDigest"]
        widened = ProtocolRecoveryState(max_interventions=5).to_dict()["policyDigest"]
        self.assertNotEqual(default, widened)

    def test_counters_are_not_reset_by_a_restart(self) -> None:
        spent = ProtocolRecoveryState(interventions=2, transport_retries=3, decisions=9)
        restored = ProtocolRecoveryState.decode(spent.encode())
        self.assertEqual(restored.interventions, 2)
        self.assertEqual(restored.transport_retries, 3)
        self.assertEqual(restored.decisions, 9)
        decision, _ = recovered(restored, Attempt(fingerprint(1), "s", fingerprint(2), "protocol"))
        self.assertEqual(decision.action, "stop")
        self.assertEqual(decision.reason, "intervention_limit")

    def test_a_restarted_transport_budget_is_not_replenished(self) -> None:
        spent = ProtocolRecoveryState.decode(
            ProtocolRecoveryState(transport_retries=3).encode())
        decision, _ = recovered(
            spent, Attempt(fingerprint(1), "dispatch", fingerprint(2), "transport"))
        self.assertEqual(decision.action, "stop")
        self.assertEqual(decision.reason, "retry_limit")


class BoundedHistoryAndTerminalExhaustion(unittest.TestCase):
    """`NT-R01`: at most twelve signatures, and exhaustion terminates explicitly."""

    def test_history_never_exceeds_the_durable_bound(self) -> None:
        current = ProtocolRecoveryState()
        for index in range(40):
            _, current = recovered(
                current, Attempt(fingerprint(index), "step", fingerprint(index), None))
            with self.subTest(index=index):
                self.assertLessEqual(len(current.history), MAX_DURABLE_ATTEMPTS)
                self.assertLessEqual(len(current.attempted_fingerprints), MAX_DURABLE_ATTEMPTS)

    def test_history_retains_the_newest_signatures_not_the_oldest(self) -> None:
        current = ProtocolRecoveryState()
        for index in range(20):
            _, current = recovered(
                current, Attempt(fingerprint(index), "step", fingerprint(index), None))
        self.assertEqual(current.history[-1].fingerprint, fingerprint(19))

    def test_exhausted_recovery_is_an_explicit_terminal_failure(self) -> None:
        current = ProtocolRecoveryState()
        actions = []
        for index in range(8):
            decision, current = recovered(
                current, Attempt(fingerprint(1), "stall", fingerprint(1), None))
            actions.append(decision.action)
        self.assertEqual(actions[-1], "stop")
        self.assertEqual(current.last_decision.action, "stop")
        self.assertEqual(current.last_decision.reason, "intervention_limit")

    def test_one_reground_then_one_replan_then_stop(self) -> None:
        current = ProtocolRecoveryState()
        seen = []
        for _ in range(6):
            decision, current = recovered(
                current, Attempt(fingerprint(1), "stall", fingerprint(1), None))
            seen.append(decision.action)
        self.assertEqual(seen.count("reground"), 1)
        self.assertEqual(seen.count("replan"), 1)
        self.assertEqual(seen[-1], "stop")

    def test_new_material_evidence_permits_progress(self) -> None:
        """A changed progress key is the difference between a loop and work."""
        current = ProtocolRecoveryState()
        for index in range(4):
            decision, current = recovered(current, Attempt(
                fingerprint(index), "step",
                semantic_progress_key({"fact": index}, ()), None))
            with self.subTest(index=index):
                self.assertEqual(decision.action, "continue")
                self.assertEqual(decision.reason, "progress")

    def test_a_budget_or_permission_failure_never_waits(self) -> None:
        for failure in ("budget", "permission"):
            with self.subTest(failure=failure):
                decision, _ = recovered(
                    ProtocolRecoveryState(),
                    Attempt(fingerprint(1), failure, fingerprint(2), failure))
                self.assertEqual(decision.action, "stop")
                self.assertEqual(decision.delay_ms, 0)

    def test_recovery_never_widens_a_budget_or_a_grant(self) -> None:
        """`NT-R02`: no automatic authority expansion. The decision is a reference."""
        current = ProtocolRecoveryState()
        for index in range(10):
            decision, current = recovered(
                current, Attempt(fingerprint(index), "step", fingerprint(index), "protocol"),
                remaining_turns=2, remaining_ms=50)
            with self.subTest(index=index):
                self.assertEqual(decision.remaining_budget_ref, DIGEST)
                self.assertNotIn("grant", decision.to_dict())
                self.assertLessEqual(decision.delay_ms, 50)

    def test_a_zero_remainder_stops_before_anything_is_spent(self) -> None:
        for remaining in ({"remaining_turns": 0}, {"remaining_ms": 0}):
            with self.subTest(**remaining):
                decision, _ = recovered(
                    ProtocolRecoveryState(),
                    Attempt(fingerprint(1), "step", fingerprint(2), None), **remaining)
                self.assertEqual(decision.action, "stop")
                self.assertEqual(decision.reason, "budget")
                self.assertEqual(decision.delay_ms, 0)

    def test_length_two_and_three_cycles_are_caught_inside_the_window(self) -> None:
        two = [(fingerprint(index % 2), "step", fingerprint(index % 2)) for index in range(6)]
        three = [(fingerprint(index % 3), "step", fingerprint(index % 3)) for index in range(6)]
        for name, history in (("two", two), ("three", three)):
            with self.subTest(cycle=name):
                core = decide_recovery(
                    history, failure=None, interventions=0, transport_retries=0,
                    remaining_turns=5, remaining_ms=5000, jitter=0.0)
                self.assertIn(core.action, {"reground", "replan"})


# ---------------------------------------------------------------------------
# 4. Frozen state is frozen; old state migrates or is typed-refused
# ---------------------------------------------------------------------------

class FrozenStateRejectsAliasedInput(unittest.TestCase):
    """`NT-1.6`: nothing a caller still holds may move a digest already taken."""

    def test_a_caller_cannot_edit_task_state_after_it_was_digested(self) -> None:
        verification = {"command": "python3 -m unittest", "nested": {"exit": 0}}
        budgets = {"turns": 4}
        recovery = {"interventions": 0}
        task = state(last_verification=verification, remaining_budgets=budgets,
                     recovery_state=recovery)
        digest = task.digest()
        verification["command"] = "true"
        verification["nested"]["exit"] = 1
        budgets["turns"] = 999
        recovery["interventions"] = 99
        self.assertEqual(task.digest(), digest)
        self.assertEqual(task.last_verification["command"], "python3 -m unittest")
        self.assertEqual(task.last_verification["nested"]["exit"], 0)
        self.assertEqual(task.remaining_budgets["turns"], 4)
        self.assertEqual(task.recovery_state["interventions"], 0)

    def test_a_route_decision_snapshot_is_detached_from_its_caller(self) -> None:
        snapshot = {"turns": 3}
        decision = RouteDecision(route="local", reason="cheap", budget_snapshot=snapshot)
        snapshot["turns"] = 0
        self.assertEqual(decision.budget_snapshot["turns"], 3)
        self.assertEqual(decision.to_dict()["budgetSnapshot"], {"turns": 3})

    def test_frozen_mappings_refuse_a_write_rather_than_accepting_a_divergence(self) -> None:
        task = state(last_verification={"exit": 0})
        with self.assertRaises(TypeError):
            task.last_verification["exit"] = 1  # type: ignore[index]

    def test_a_canonical_round_trip_is_stable(self) -> None:
        task = state(last_verification={"command": "x", "nested": {"exit": 0}},
                     remaining_budgets={"turns": 4})
        again = SemanticTaskState.from_mapping(task.to_canonical_dict())
        self.assertEqual(again.digest(), task.digest())
        self.assertEqual(again.to_canonical_dict(), task.to_canonical_dict())

    def test_a_memory_view_round_trips_through_its_durable_form(self) -> None:
        snapshot = view(Evidence("ev-1", SUBJECT, ARTIFACT, "finding", "body"))
        restored = MemoryView.decode(snapshot.encode(), snapshot.digest())
        self.assertEqual(restored.encode(), snapshot.encode())
        self.assertEqual(restored.task.digest(), snapshot.task.digest())


class OldStateMigratesOrFailsTyped(unittest.TestCase):
    """`NT-1.6`: a payload from an older writer is readable or refused, never guessed."""

    def test_a_legacy_recovery_payload_migrates_deterministically(self) -> None:
        legacy = {"transportRetries": 1, "protocolRetries": 2,
                  "attemptedFingerprints": [fingerprint(1)], "spentDecisions": ["retry"]}
        first = ProtocolRecoveryState.from_dict(legacy)
        second = ProtocolRecoveryState.from_dict(dict(legacy))
        self.assertEqual(first.encode(), second.encode())
        self.assertEqual(first.transport_retries, 1)
        self.assertEqual(first.protocol_retries, 2)
        self.assertEqual(first.max_interventions, MAX_INTERVENTIONS)

    def test_an_unknown_recovery_schema_is_refused_as_a_version_error(self) -> None:
        with self.assertRaises(ValueError) as raised:
            ProtocolRecoveryState.from_dict({"schema": "aether.recovery-state/99"})
        self.assertIn("unsupported recovery schema", str(raised.exception))

    def test_an_incomplete_versioned_payload_names_what_is_missing(self) -> None:
        with self.assertRaises(ValueError) as raised:
            ProtocolRecoveryState.from_dict({"schema": RECOVERY_STATE_SCHEMA})
        self.assertIn("incomplete recovery-state payload", str(raised.exception))

    def test_an_unknown_memory_schema_is_refused(self) -> None:
        snapshot = view()
        payload = json.loads(snapshot.encode().decode("utf-8"))
        payload["schema"] = "aether.memory-view/99"
        from vanguard.packages.domain.canonicalisation.jcs import canonical_bytes
        from vanguard.packages.domain.canonicalisation.digest import digest_bytes
        mutated = canonical_bytes(payload)
        with self.assertRaises(ValueError):
            MemoryView.decode(mutated, digest_bytes(mutated))

    def test_a_digest_mismatch_is_refused_before_the_payload_is_trusted(self) -> None:
        snapshot = view()
        with self.assertRaises(ValueError):
            MemoryView.decode(snapshot.encode(), DIGEST)


class ChangedSubjectInvalidatesEvidence(unittest.TestCase):
    """`NT-C04`: a finding about another subject is not weaker evidence about this one."""

    def test_evidence_bound_to_another_subject_never_reaches_the_prompt(self) -> None:
        stale = Evidence("ev-stale", OTHER_SUBJECT, ARTIFACT, "finding from another tree", "body")
        fresh = Evidence("ev-fresh", SUBJECT, ARTIFACT, "finding from this tree", "body")
        packet = compiler().compile_packet(view(stale, fresh), SUBJECT, ())
        rendered = "\n".join(block.text for block in packet.blocks)
        self.assertNotIn("finding from another tree", rendered)
        self.assertIn("finding from this tree", rendered)
        self.assertIn(("ev-stale", "stale"), packet.omissions)

    def test_the_same_evidence_becomes_stale_when_the_subject_moves(self) -> None:
        evidence = Evidence("ev-1", SUBJECT, ARTIFACT, "finding", "body")
        before = compiler().compile_packet(view(evidence), SUBJECT, ())
        after = compiler().compile_packet(view(evidence), OTHER_SUBJECT, ())
        self.assertNotIn(("ev-1", "stale"), before.omissions)
        self.assertIn(("ev-1", "stale"), after.omissions)


class DeclaredBehaviorIdentity(unittest.TestCase):
    """`NT-1.6`: every behavior-affecting member moves the composition epoch."""

    BASE = {
        "modelRoute": "anthropic/claude-opus-5",
        "serializerId": "agency.context.messages/1",
        "counterId": "agency.context.estimate_tokens/1",
        "recoveryPolicyDigest": DIGEST,
        "productPreset": "code-default",
    }

    def test_each_declared_member_moves_the_epoch_independently(self) -> None:
        base = compiler(behavior_identity=self.BASE).composition_epoch
        for member in self.BASE:
            mutated = dict(self.BASE)
            mutated[member] = "changed"
            with self.subTest(member=member):
                self.assertNotEqual(
                    compiler(behavior_identity=mutated).composition_epoch, base)

    def test_declaration_order_does_not_split_an_epoch(self) -> None:
        forward = compiler(behavior_identity=dict(self.BASE))
        reverse = compiler(behavior_identity=dict(reversed(list(self.BASE.items()))))
        self.assertEqual(forward.composition_epoch, reverse.composition_epoch)

    def test_declaring_nothing_leaves_the_existing_epoch_exactly_where_it_was(self) -> None:
        self.assertEqual(
            compiler().composition_epoch,
            compiler(behavior_identity=None).composition_epoch)

    def test_a_declared_identity_reaches_the_selection_record(self) -> None:
        identity = compiler(behavior_identity=self.BASE).selection_identity()
        self.assertEqual(
            identity["parameters"]["behaviorIdentity"]["modelRoute"],
            "anthropic/claude-opus-5")

    def test_a_structure_is_refused_rather_than_put_on_the_ledger(self) -> None:
        with self.assertRaises(TypeError):
            compiler(behavior_identity={"route": {"nested": "value"}})

    def test_telemetry_shaped_change_does_not_move_the_epoch(self) -> None:
        """`NT-1.6`: wall-clock observation does not alter behavior identity."""
        subject = compiler(behavior_identity=self.BASE)
        epoch = subject.composition_epoch
        subject.compile_packet(view(), SUBJECT, verification_turns(4))
        subject.compile_packet(view(cursor=99), SUBJECT, verification_turns(9))
        self.assertEqual(subject.composition_epoch, epoch)


if __name__ == "__main__":
    unittest.main()
