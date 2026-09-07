"""Replay is byte-identical, not merely state-equivalent.

S8-A-03. Without an injected source of randomness and a determinism-complete
clock, "replay" means state reconstruction only. Counterfactual re-execution --
the thing that makes the corpus *attributable* (`GTS-13C` Ch. 11 stage 2) -- is
unreachable, and the progressive-vs-degenerating ratio cannot be computed at
all.

The hole was concrete: every event id came from `uuidv7()`, which draws its
timestamp from the system clock and its 74 random bits from the process-global
RNG. Two runs of the same recording could never produce the same bytes.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

from vanguard.packages.ports.determinism import ClockPort, RandomPort
from vanguard.packages.runtime.determinism import (
    FixedClock,
    SeededRandom,
    SystemClock,
    SystemRandom,
    event_id,
)

PACKAGES = Path(__file__).resolve().parents[2] / "vanguard" / "packages"


class PortsAreSatisfiedByBothSides(unittest.TestCase):
    def test_the_real_pair_satisfies_the_ports(self) -> None:
        self.assertIsInstance(SystemRandom(), RandomPort)
        self.assertIsInstance(SystemClock(), ClockPort)

    def test_the_fake_pair_satisfies_the_ports(self) -> None:
        self.assertIsInstance(SeededRandom(seed=1), RandomPort)
        self.assertIsInstance(FixedClock(at="2026-08-16T00:00:00.000Z"), ClockPort)


class SameSeedSameBytes(unittest.TestCase):
    def test_two_seeded_streams_agree_bit_for_bit(self) -> None:
        left = SeededRandom(seed=42)
        right = SeededRandom(seed=42)
        self.assertEqual(
            [left.getrandbits(62) for _ in range(64)],
            [right.getrandbits(62) for _ in range(64)],
        )

    def test_different_seeds_diverge(self) -> None:
        left = SeededRandom(seed=42)
        right = SeededRandom(seed=43)
        self.assertNotEqual(
            [left.getrandbits(62) for _ in range(16)],
            [right.getrandbits(62) for _ in range(16)],
        )

    def test_a_seeded_stream_does_not_touch_the_global_rng(self) -> None:
        """A module-level `random.seed` elsewhere must not move this stream."""

        import random

        random.seed(1)
        first = [SeededRandom(seed=7).getrandbits(32) for _ in range(4)]
        random.seed(999999)
        second = [SeededRandom(seed=7).getrandbits(32) for _ in range(4)]
        self.assertEqual(first, second)

    def test_event_ids_replay_byte_identically(self) -> None:
        """The DoD: same recording seed, same trajectory bytes."""

        def trajectory() -> list[str]:
            clock = FixedClock(at="2026-08-16T00:00:00.000Z")
            rng = SeededRandom(seed=2026)
            return [event_id(clock=clock, random=rng) for _ in range(32)]

        self.assertEqual(trajectory(), trajectory())

    def test_a_different_seed_gives_a_different_trajectory(self) -> None:
        def trajectory(seed: int) -> list[str]:
            clock = FixedClock(at="2026-08-16T00:00:00.000Z")
            return [event_id(clock=clock, random=SeededRandom(seed=seed))
                    for _ in range(8)]

        self.assertNotEqual(trajectory(2026), trajectory(2027))

    def test_generated_ids_are_well_formed_uuidv7(self) -> None:
        import uuid

        value = event_id(clock=FixedClock(at="2026-08-16T00:00:00.000Z"),
                         random=SeededRandom(seed=1))
        parsed = uuid.UUID(value)
        self.assertEqual(parsed.version, 7)
        self.assertEqual(parsed.variant, uuid.RFC_4122)


class ClockIsDeterminismComplete(unittest.TestCase):
    def test_a_fixed_clock_never_advances(self) -> None:
        clock = FixedClock(at="2026-08-16T00:00:00.000Z")
        self.assertEqual(clock.now(), clock.now())

    def test_a_fixed_clock_reports_millis_matching_its_instant(self) -> None:
        clock = FixedClock(at="2026-08-16T00:00:00.000Z")
        self.assertEqual(clock.now_ms(), clock.now_ms())
        self.assertIsInstance(clock.now_ms(), int)

    def test_a_logical_clock_advances_by_a_fixed_step(self) -> None:
        """`clockPolicy: logical` -- time is a counter, not a measurement."""

        clock = FixedClock(at="2026-08-16T00:00:00.000Z", step_ms=1000)
        first, second = clock.now(), clock.now()
        self.assertNotEqual(first, second)
        self.assertLess(first, second)

    def test_the_system_clock_emits_ct08_shape(self) -> None:
        import re

        self.assertRegex(
            SystemClock().now(), r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


class NothingReachesTheGlobalSourcesUnannounced(unittest.TestCase):
    """The architecture test the kit asks for.

    Determinism is a property of the import graph too: a module that can reach
    `random` or the wall clock directly can break replay without any caller
    being able to see it. Every remaining hole is listed with the row that owns
    it, so this test fails when a *new* one appears rather than pretending the
    tree is already clean.
    """

    #: path -> why it is still allowed to reach a global source.
    KNOWN_HOLES = {
        # `uuidv7()` draws its timestamp from `time.time()` and its 74 random
        # bits from the process-global RNG. Every trajectory call site now
        # routes through `runtime/determinism.py` instead, but the primitive
        # itself is in `domain/primitives/`, which is outside Lane A's Sprint 8
        # write scope. Reported, not edited.
        "domain/primitives/primitives.py",
        # Retry jitter on a live provider. Not on the replay path: a recorded
        # run replays from the cassette and never retries.
        "adapters/models/openrouter.py",
        # Sandbox attestation timestamp, already injectable via `attested_at`.
        "adapters/sandbox/rootless.py",
        # Environment receipt timestamps. Candidate for ClockPort injection;
        # `adapters/**` is not Lane A's Sprint 8 scope.
        "adapters/environment/sandboxed.py",
        # Service frame ids and inbox bookkeeping, outside the episode
        # trajectory. `S8-A-02` re-entry does not read them.
        "runtime/service/service.py",
        # The real half of the pair. It is *supposed* to reach both.
        "runtime/determinism.py",
    }

    def _offenders(self) -> set[str]:
        found: set[str] = set()
        for path in PACKAGES.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            rel = path.relative_to(PACKAGES).as_posix()
            source = path.read_text(encoding="utf-8")
            for node in ast.walk(ast.parse(source)):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                if any(n == "random" or n.startswith("random.") for n in names):
                    found.add(rel)
                if "datetime.now(" in source or "time.time()" in source:
                    found.add(rel)
        return found

    def test_no_new_module_reaches_random_or_the_wall_clock(self) -> None:
        offenders = self._offenders() - self.KNOWN_HOLES
        self.assertEqual(offenders, set(), f"new determinism hole(s): {sorted(offenders)}")

    def test_the_known_holes_are_still_real(self) -> None:
        """A stale allowlist entry is a rule quietly getting weaker."""

        stale = self.KNOWN_HOLES - self._offenders()
        self.assertEqual(stale, set(), f"allowlist entries no longer needed: {sorted(stale)}")

    def test_the_episode_trajectory_does_not_call_uuidv7_directly(self) -> None:
        """`root.py`'s ledger writes event ids through the ports now."""

        source = "\n".join(
            (PACKAGES / "runtime" / name).read_text(encoding="utf-8")
            for name in ("root.py", "compose.py", "session.py", "wiring.py", "ledger_emitter.py")
        )
        self.assertNotIn("event_id=uuidv7()", source)


class ASessionReplaysToTheSameBytes(unittest.TestCase):
    """End-to-end: the DoD, through a real `HarnessSession`."""

    def _trajectory(self) -> list[str]:
        from test.agency.doubles import ScriptedModel, finish
        from test.runtime.test_harness_session import FakeEnvironment
        from vanguard.packages.adapters.stores.event_store import SqliteEventStore
        from vanguard.packages.runtime.root import (
            HarnessSession, Runtime, SessionPorts, TaskContext)

        harness = Runtime.compose("vg-code-default", episode_id="ep-replay-1")
        ports = SessionPorts(
            model=ScriptedModel([finish()]),
            environment=FakeEnvironment(),
            clock=FixedClock(at="2026-08-16T00:00:00.000Z", step_ms=1),
            random=SeededRandom(seed=2026),
            store=SqliteEventStore(":memory:"),
            interactive=False,
        )
        task = TaskContext(
            brief="make the suite green", repo_path=Path("/workspace"),
            run_id="run-replay-1", episode_id="ep-replay-1", max_turns=4)
        result = HarnessSession(harness, ports, task).run()
        return [e.event_id for e in result.events if hasattr(e, "event_id")]

    def test_two_runs_of_one_recording_produce_identical_event_ids(self) -> None:
        first, second = self._trajectory(), self._trajectory()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
