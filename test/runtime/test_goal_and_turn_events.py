"""T-60 / A §23.4: the goal and each turn are facts on the ledger.

Both kinds were catalogued, reduced and rendered by clients while nothing
emitted them, so a real run produced no user bubble and no turn boundaries.
These assert the producers exist and that what they write is what the
existing readers already expect.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.ledger.events import WRITABLE_KINDS, parse_event_envelope
from vanguard.packages.domain.ledger.reducer import initial_state, reduce_event

ROOT = Path(__file__).resolve().parents[2]
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")

#: The brief `DogfoodGate.execute()` runs. Kept here rather than reaching into
#: the fixture so this module fails loudly if the two ever diverge, instead of
#: silently comparing a digest against itself.
BRIEF = "calc.total is off by one for every input; make the suite green."


class _RealRun(unittest.TestCase):
    """One real composed run, shared by every assertion below.

    `DogfoodGate` is driven rather than subclassed: inheriting it would
    re-execute its whole suite once per subclass here, and the run is the
    expensive part.
    """

    events: list = []

    @classmethod
    def setUpClass(cls) -> None:
        # Imported here, not at module scope: pytest collects every
        # `TestCase` subclass visible in a module, so a top-level import
        # would re-run the whole composition-root suite once per class here.
        from test.runtime.test_composition_root import DogfoodGate

        cls._gate = DogfoodGate("run")
        cls._gate.setUp()
        cls.events = list(cls._gate.execute().events)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._gate.doCleanups()

    def kinds(self) -> list[str]:
        return [e.kind for e in self.events]


class GoalDeclaredIsProduced(_RealRun):
    def test_the_goal_is_declared_exactly_once(self) -> None:
        goals = [e for e in self.events if e.kind == "GoalDeclared"]
        self.assertEqual(len(goals), 1, "one run declares one goal")

    def test_the_goal_follows_episode_started_and_nothing_precedes_it(self) -> None:
        # `TSK-LED-002`/`G-050-03`: `EpisodeStarted` is the durable beginning
        # of a run. The goal is the next fact, not an earlier one.
        kinds = self.kinds()
        self.assertEqual(kinds[0], "EpisodeStarted")
        self.assertEqual(kinds[1], "GoalDeclared")

    def test_the_goal_payload_carries_digests_and_no_goal_text(self) -> None:
        # ADR-0098 Decision 5. Goal text on an append-only store cannot be
        # withdrawn, so the ledger keeps identity only.
        goal = next(e for e in self.events if e.kind == "GoalDeclared")
        payload = dict(goal.payload)
        self.assertRegex(payload["goalDigest"], _SHA256)
        for absent in ("goal", "brief", "prompt", "text", "objective"):
            self.assertNotIn(absent, payload)

    def test_the_goal_payload_validates_against_its_schema(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "mhf" / "goal_declared.schema.json").read_text())
        payload = dict(next(e for e in self.events if e.kind == "GoalDeclared").payload)
        allowed = set(schema["properties"])
        # `additionalProperties: false` -- the envelope's own `kind`/`reason`/
        # `alertable` are added by the emitter and are not payload properties.
        extra = set(payload) - allowed - {"kind", "reason", "alertable"}
        self.assertEqual(extra, set(), f"payload carries fields the schema forbids: {extra}")
        for required in schema["required"]:
            self.assertIn(required, payload)
        for field in ("goalArtifact", "parentGoalDigest"):
            if field in payload and payload[field] is not None:
                self.assertRegex(payload[field], _SHA256)

    def test_the_goal_digest_is_derived_from_the_brief(self) -> None:
        goal = next(e for e in self.events if e.kind == "GoalDeclared")
        self.assertEqual(goal.payload["goalDigest"], digest_of({"brief": BRIEF}))


class TurnStartedIsProduced(_RealRun):
    def test_every_turn_is_recorded_from_zero(self) -> None:
        turns = [e.payload.get("turn") for e in self.events if e.kind == "TurnStarted"]
        self.assertTrue(turns, "a run that took turns must record them")
        self.assertEqual(turns, list(range(len(turns))), "0-based and contiguous")

    def test_a_turn_that_never_ran_is_never_recorded(self) -> None:
        # The emit sits below the cancellation and turn-bound guards, so the
        # ledger's turn count cannot exceed the episode's.
        started = [e for e in self.events if e.kind == "TurnStarted"]
        proposals = [e for e in self.events if e.kind == "ProposalProduced"]
        self.assertLessEqual(len(started), len(proposals) + 1)


class TurnZeroSurvivesTheFold(unittest.TestCase):
    """The reducer read `turn` through an `or` chain, so turn 0 -- a falsy but
    entirely ordinary value -- fell through to the envelope seq and the first
    turn of every episode was relabelled."""

    @staticmethod
    def _envelope(kind: str, seq: int, payload: dict) -> object:
        return parse_event_envelope({
            "schemaVersion": "vg.4",
            "eventId": f"018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a{seq:02x}",
            "scope": "episode", "runId": "run-1", "episodeId": "ep-1", "seq": str(seq),
            "occurredAt": "2026-09-03T00:00:00.000Z",
            "recordedAt": "2026-09-03T00:00:00.001Z",
            "principal": "agent-1", "principalRole": "episode",
            "tenantId": "t", "ownerId": "o", "confidentiality": "internal",
            "retentionClass": "standard", "trainability": "prohibited",
            "redactionStatus": "none", "traceId": "tr", "spanId": "sp",
            "payload": {"kind": kind, **payload},
        })

    def test_turn_zero_is_not_relabelled_with_the_envelope_seq(self) -> None:
        state = initial_state()
        # seq deliberately != turn, so a fallback to seq is visible.
        state = reduce_event(state, self._envelope("EpisodeStarted", 7, {}))
        state = reduce_event(state, self._envelope("TurnStarted", 8, {"turn": 0}))
        state = reduce_event(state, self._envelope("TurnStarted", 9, {"turn": 1}))
        labels = [t[2] for t in state.episode.state_transitions if t[2].startswith("TurnStarted")]
        self.assertEqual(labels, ["TurnStarted:0", "TurnStarted:1"])

    def test_a_turnless_payload_still_falls_back_to_the_seq(self) -> None:
        state = reduce_event(initial_state(), self._envelope("TurnStarted", 4, {}))
        labels = [t[2] for t in state.episode.state_transitions if t[2].startswith("TurnStarted")]
        self.assertEqual(labels, ["TurnStarted:4"])


class BothKindsAreWritable(unittest.TestCase):
    def test_the_catalog_admits_what_the_producers_write(self) -> None:
        for kind in ("GoalDeclared", "TurnStarted"):
            self.assertIn(kind, WRITABLE_KINDS)
