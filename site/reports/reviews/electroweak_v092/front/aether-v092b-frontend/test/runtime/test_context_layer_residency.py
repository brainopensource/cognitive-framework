"""Step 8b — pin the premise that context interning would depend on.

The M-4..M-7 review bundle proposes a content-addressed `ContextStore` to strip
a claimed 11.0x memory redundancy from the live trajectory path (304,390 ->
27,609 bytes over 50 turns), on the grounds that every turn re-carries a
byte-identical prefix block -- specifically an L2 tool-schema block of 5,926
bytes "identical on every turn".

The block is real and its size is exactly right. The redundancy is not: on this
codebase every turn already carries *the same string object*, because
`CompiledContext.bundle()` renders a single-block layer with
`"\n\n".join([block.text])`, which returns `block.text` itself, and the prefix
fragments are stable across compiles. 304,390 is the logical byte total; the
resident total is one copy.

So interning was measured at 1.00x here and was not merged. What survives is
this file: the premise, pinned. If `bundle()` ever starts allocating a fresh
body per turn -- an innocuous-looking `+ ""`, an f-string, a per-turn
normalisation pass -- these tests fail, and *that* is the point at which the
bundle's `ContextStore` becomes worth landing. Without them the regression is
invisible until a long episode runs a host out of memory.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from test.agency.doubles import ScriptedModel, effect, finish
from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext

PREFIX_LAYERS = {"L1", "L2", "L3", "L4"}


def _episode(episode_id: str, turns: int = 10):
    """One real multi-turn episode through the canonical public path."""
    tape = [effect(path=f"/workspace/src/f{index}.ts") for index in range(turns)]
    tape.append(finish("done"))
    harness = Runtime.compose("vg-code-default", episode_id=episode_id)
    session = HarnessSession(
        harness,
        SessionPorts(model=ScriptedModel(tape), environment=FakeEnvironment(),
                     clock=FakeClock(), store=SqliteEventStore(":memory:"),
                     interactive=False),
        TaskContext(brief="residency", repo_path=Path("/workspace"),
                    run_id=f"run-{episode_id}", episode_id=episode_id,
                    principal="agent-1"),
    )
    session.run()
    return session


class PrefixLayerBodiesAreSharedAcrossTurns(unittest.TestCase):
    """The property that makes a context store unnecessary today."""

    def setUp(self) -> None:
        self.contexts = _episode("ep-residency").operator.contexts
        self.assertGreater(len(self.contexts), 1, "need multiple turns to compare")

    def test_a_prefix_layer_body_is_one_object_for_the_whole_episode(self) -> None:
        instances: dict[str, set[int]] = {}
        for bundle in self.contexts:
            for layer in bundle.get("layers", ()):
                if layer["layer"] in PREFIX_LAYERS:
                    instances.setdefault(layer["layer"], set()).add(id(layer["content"]))
        self.assertTrue(instances, "the episode carried no prefix layer")
        for layer, ids in sorted(instances.items()):
            self.assertEqual(
                len(ids), 1,
                f"{layer} was retained as {len(ids)} objects across "
                f"{len(self.contexts)} turns; the redundancy the review bundle's "
                f"ContextStore removes has appeared -- land it.",
            )

    def test_resident_bytes_do_not_grow_with_turn_count(self) -> None:
        short = _episode("ep-residency-short", turns=2).operator.contexts
        long = _episode("ep-residency-long", turns=20).operator.contexts
        self.assertGreater(len(long), len(short))

        def resident(contexts) -> int:
            unique: dict[int, int] = {}
            for bundle in contexts:
                for layer in bundle.get("layers", ()):
                    if layer["layer"] in PREFIX_LAYERS:
                        unique[id(layer["content"])] = len(layer["content"].encode())
            return sum(unique.values())

        self.assertEqual(resident(short), resident(long))

    def test_the_prefix_digest_confirms_the_bodies_really_are_identical(self) -> None:
        """Object identity would be vacuous if the bodies also differed."""
        digests = {bundle["prefixDigest"] for bundle in self.contexts}
        self.assertEqual(len(digests), 1,
                         "the cached prefix moved mid-episode (VG-03 10.2)")


if __name__ == "__main__":
    unittest.main()
