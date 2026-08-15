"""`TEST-CTX-001` / `REQ-CTX-001` — the L1–L5 prefix-stable context compiler.

Three claims, and none of them is "the compiler runs":

1. **The prefix does not move.** `L1`–`L3` are byte-for-byte identical across a
   replay of ten turns whose brief and dialogue both change underneath them
   (`VG-03 §10.2`). A cache economics claim without a replay to run over is an
   intention, so the replay is the test.
2. **The budget never eats the floor.** Over-ceiling assembly evicts `L5`
   result bodies oldest-first, then drops `L5` entries, then drops `L4` notes —
   and never `L1`, `L2`, `L3`, or the brief (`VG-03 §10.3`, `§10.5`).
3. **The prior is on the wire before turn 1.** `CompetencePriorRecorded`
   reaches the event sink with a digest binding it to the exact prompt it was
   a prior *for* (`S5-SA-002`), or offline Brier calibration is scoring against
   a context nobody can reconstruct.

The sink under these tests is the same `RecordingSink` the kernel emits
through, because a prior recorded to a private list is not recorded.
"""

from __future__ import annotations

import json
import unittest

from vanguard.packages.agency.context import (
    BREAKPOINT_LAYERS,
    PREFIX_LAYERS,
    Block,
    CacheBreakpointCeilingExceeded,
    CompetencePriorRecorder,
    CompiledContext,
    ContextBudgetExceeded,
    ContextCompiler,
    Fragment,
    Layer,
    estimate_tokens,
)

from test.kernel import fakes

SYSTEM_CORE = "Act on the repository task using typed tools."
ENVIRONMENT = "repo=vanguard branch=sprint5-6/integration runtime=python3.12"
TOOLS = (
    {"name": "read", "verb": "fs.read", "description": "Read file content."},
    {"name": "patch", "verb": "patch.apply", "description": "Apply a diff."},
)


def build(**overrides) -> ContextCompiler:
    kwargs = {
        "system_core": SYSTEM_CORE,
        "tool_schemas": TOOLS,
        "environment": ENVIRONMENT,
        "token_ceiling": 4096,
    }
    kwargs.update(overrides)
    return ContextCompiler(**kwargs)


def dialogue(count: int, *, size: int = 40, evictable: bool = True) -> tuple[Fragment, ...]:
    return tuple(
        Fragment(source="fs.read", label=f"result-{index}",
                 text="x" * size, evictable=evictable)
        for index in range(count)
    )


class LayerOrder(unittest.TestCase):
    def test_layers_render_in_order_and_only_when_non_empty(self) -> None:
        """`VG-03 §10.1`: one message per non-empty layer, rendered in order."""
        compiled = build().compile(brief="fix the parser")

        self.assertEqual([block.layer for block in compiled.blocks],
                         [Layer.SYSTEM, Layer.TOOLS, Layer.ENVIRONMENT, Layer.TASK])
        self.assertEqual([message["layer"] for message in compiled.messages()],
                         ["L1", "L2", "L3", "L4"])

    def test_dialogue_appends_as_the_last_layer(self) -> None:
        compiled = build().compile(brief="fix the parser", dialogue=dialogue(2))

        self.assertEqual(compiled.blocks[-1].layer, Layer.DIALOGUE)
        self.assertEqual([message["layer"] for message in compiled.messages()],
                         ["L1", "L2", "L3", "L4", "L5"])

    def test_an_empty_environment_emits_no_layer_three_message(self) -> None:
        """An empty layer that still renders is a byte of prefix nobody asked
        for, and it is in the cached region."""
        compiled = build(environment="").compile(brief="fix the parser")

        self.assertNotIn("L3", [message["layer"] for message in compiled.messages()])

    def test_every_block_carries_its_source_and_byte_length(self) -> None:
        """`REQ-CTX-001` provenance tagging: a block with no producing source
        cannot be attributed when it turns out to be the poisoned one."""
        compiled = build().compile(brief="fix the parser", dialogue=dialogue(1))

        for block in compiled.blocks:
            self.assertTrue(block.source)
            self.assertTrue(block.label)
            self.assertEqual(block.byte_length, len(block.text.encode("utf-8")))
            self.assertEqual(block.token_estimate, estimate_tokens(block.text))
        for message in compiled.messages():
            self.assertTrue(message["provenance"])


class PrefixStability(unittest.TestCase):
    def test_layers_one_to_three_are_byte_identical_across_ten_turns(self) -> None:
        """`VG-03 §10.2`. The replay the cache metric is measured over."""
        compiler = build()
        prefixes: set[tuple[str, ...]] = set()
        digests: set[str] = set()

        for turn in range(10):
            compiled = compiler.compile(
                brief=f"fix the parser, attempt {turn}",
                notes=(Fragment(source="operator", label=f"note-{turn}", text="n" * turn),),
                dialogue=dialogue(turn),
            )
            prefixes.add(tuple(block.text for block in compiled.blocks
                               if block.layer in PREFIX_LAYERS))
            digests.add(compiled.prefix_digest)

        self.assertEqual(len(prefixes), 1)
        self.assertEqual(len(digests), 1)

    def test_the_prefix_digest_moves_when_the_prefix_actually_changes(self) -> None:
        """`M6`: a stability metric that cannot register instability is not a
        metric. A *different composition* is the only thing that may move it."""
        first = build().compile(brief="fix the parser")
        second = build(environment=ENVIRONMENT + " dirty=true").compile(brief="fix the parser")

        self.assertNotEqual(first.prefix_digest, second.prefix_digest)

    def test_tool_schemas_render_canonically_not_in_argument_order(self) -> None:
        """Two composition roots that name the same tools in the same order
        must produce the same bytes, whatever their key order was."""
        reordered = tuple({key: tool[key] for key in reversed(list(tool))} for tool in TOOLS)
        self.assertNotEqual([list(tool) for tool in reordered], [list(tool) for tool in TOOLS])

        self.assertEqual(build().compile(brief="b").prefix_digest,
                         build(tool_schemas=reordered).compile(brief="b").prefix_digest)


class CacheBreakpoints(unittest.TestCase):
    def test_breakpoints_sit_only_at_layer_one_three_and_four(self) -> None:
        """`VG-03 §10.2`."""
        compiled = build().compile(brief="fix the parser", dialogue=dialogue(1))

        self.assertEqual(compiled.breakpoints, BREAKPOINT_LAYERS)
        self.assertEqual([message["layer"] for message in compiled.messages()
                          if message["cacheBreakpoint"]], ["L1", "L3", "L4"])

    def test_layer_five_never_carries_a_breakpoint(self) -> None:
        """It is the only layer permitted to mutate; marking it stable is a lie
        to the provider about what is stable."""
        compiled = build().compile(brief="fix the parser", dialogue=dialogue(4))

        self.assertNotIn(Layer.DIALOGUE, compiled.breakpoints)

    def test_exceeding_the_breakpoint_ceiling_raises_at_assembly(self) -> None:
        """Never discovered afterwards from cache-hit telemetry."""
        with self.assertRaises(CacheBreakpointCeilingExceeded):
            build(breakpoint_ceiling=2).compile(brief="fix the parser")


class Budget(unittest.TestCase):
    def test_a_context_within_ceiling_is_untouched(self) -> None:
        compiled = build().compile(brief="fix the parser", dialogue=dialogue(3))

        self.assertEqual(compiled.elided, ())
        self.assertEqual(compiled.dropped, ())
        self.assertEqual(len(compiled.layer_blocks(Layer.DIALOGUE)), 3)

    def test_result_eviction_takes_the_oldest_body_first(self) -> None:
        """`VG-03 §10.3` `result_eviction`: keep *that* a file was read, drop
        the body. The oldest is the one most likely already superseded."""
        floor = build().compile(brief="fix the parser").total_tokens
        entries = dialogue(4, size=400)
        ceiling = floor + estimate_tokens("x" * 400) * 3

        compiled = build(token_ceiling=ceiling).compile(
            brief="fix the parser", dialogue=entries)

        self.assertEqual(compiled.elided[0], "result-0")
        self.assertLessEqual(compiled.total_tokens, ceiling)
        self.assertEqual(len(compiled.layer_blocks(Layer.DIALOGUE)), 4)
        self.assertIn("result-0", compiled.layer_blocks(Layer.DIALOGUE)[0].text)
        self.assertNotIn("x" * 400, compiled.layer_blocks(Layer.DIALOGUE)[0].text)

    def test_truncation_never_touches_the_system_core_or_the_schemas(self) -> None:
        """`REQ-CTX-001` margin: never truncate `L1` or `L2`."""
        floor = build().compile(brief="fix the parser").total_tokens
        compiled = build(token_ceiling=floor + 4).compile(
            brief="fix the parser", dialogue=dialogue(30, size=400))

        self.assertEqual(compiled.layer_blocks(Layer.SYSTEM)[0].text, SYSTEM_CORE)
        self.assertEqual(json.loads(compiled.layer_blocks(Layer.TOOLS)[0].text),
                         [dict(tool) for tool in TOOLS])
        self.assertLessEqual(compiled.total_tokens, floor + 4)

    def test_dialogue_is_exhausted_before_a_task_note_is_dropped(self) -> None:
        """`L5` truncates before `L4` compacts (`REQ-CTX-001`)."""
        note = Fragment(source="operator", label="note-0", text="n" * 400)
        floor = build().compile(brief="fix the parser").total_tokens
        ceiling = floor + estimate_tokens("n" * 400)

        compiled = build(token_ceiling=ceiling).compile(
            brief="fix the parser", notes=(note,), dialogue=dialogue(2, size=400))

        self.assertEqual(compiled.layer_blocks(Layer.DIALOGUE), ())
        self.assertIn("note-0", [block.label for block in compiled.layer_blocks(Layer.TASK)])
        self.assertIn("result-0", compiled.dropped)

    def test_the_brief_is_exempt_from_compaction(self) -> None:
        """`VG-03 §10.5`: work is checked against the brief, never against the
        last summary of it, so the brief cannot be the thing that is summarised."""
        brief = "fix the parser " * 20
        note = Fragment(source="operator", label="note-0", text="n" * 400)
        floor = build().compile(brief=brief).total_tokens

        compiled = build(token_ceiling=floor).compile(
            brief=brief, notes=(note,), dialogue=dialogue(4, size=400))

        self.assertIn(brief, [block.text for block in compiled.layer_blocks(Layer.TASK)])
        self.assertIn("note-0", compiled.dropped)

    def test_a_floor_that_cannot_fit_raises_at_assembly(self) -> None:
        """`M6`'s twin: a requirement that cannot be satisfied is not a
        requirement. Silently shipping an over-budget prompt is worse than a
        loud failure at the seam that owns the budget."""
        with self.assertRaises(ContextBudgetExceeded):
            build(token_ceiling=4).compile(brief="fix the parser")


class CompetencePrior(unittest.TestCase):
    """`S5-SA-002`. The prior is logged *before* turn 1 reaches the model."""

    def setUp(self) -> None:
        self.clock = fakes.FakeClock()
        self.sink = fakes.RecordingSink()
        self.recorder = CompetencePriorRecorder(clock=self.clock, events=self.sink)
        self.compiled = build().compile(brief="fix the parser")

    def record(self, prior: float = 0.42, **overrides) -> bool:
        kwargs = {
            "episode_id": "episode-1",
            "run_id": "run-1",
            "principal": "agent-1",
            "prior": prior,
            "context": self.compiled,
        }
        kwargs.update(overrides)
        return self.recorder.record(**kwargs)

    def test_the_prior_reaches_the_event_sink(self) -> None:
        self.assertTrue(self.record())

        event = self.sink.events[0]
        self.assertEqual(event.kind, "CompetencePriorRecorded")
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.payload["episodeId"], "episode-1")
        self.assertEqual(event.payload["beforeTurn"], 0)

    def test_the_prior_is_recorded_as_a_canonical_decimal_string(self) -> None:
        """`VG-04 §0.4`: a number that must survive a canonical digest crosses
        the wire as a string, not as a host float."""
        self.record(0.42)

        self.assertEqual(self.sink.events[0].payload["prior"], "0.4200")

    def test_the_prior_is_bound_to_the_prompt_it_was_a_prior_for(self) -> None:
        """Offline Brier scoring against a context nobody can reconstruct is
        not calibration."""
        self.record()

        payload = self.sink.events[0].payload
        self.assertEqual(payload["prefixDigest"], self.compiled.prefix_digest)
        self.assertEqual(payload["promptDigest"], self.compiled.digest)
        self.assertEqual(payload["tokens"], self.compiled.total_tokens)

    def test_the_payload_carries_no_prompt_text(self) -> None:
        """`REQ-TRUST-001`: digests on the wire, never the brief itself."""
        rendered = json.dumps(dict(self.sink.events[0].payload) if self.sink.events else {})
        self.record()
        rendered = json.dumps(dict(self.sink.events[0].payload))

        self.assertNotIn("fix the parser", rendered)
        self.assertNotIn(SYSTEM_CORE, rendered)

    def test_a_second_record_for_the_same_episode_is_refused(self) -> None:
        """A *pre-action* prior recorded twice is two priors, and the second one
        is conditioned on evidence the first never saw."""
        self.assertTrue(self.record())
        self.assertFalse(self.record(0.9))

        self.assertEqual(len(self.sink.events), 1)

    def test_a_second_episode_records_its_own_prior(self) -> None:
        self.record()
        self.assertTrue(self.record(episode_id="episode-2"))

        self.assertEqual(len(self.sink.events), 2)

    def test_a_value_outside_zero_to_one_is_not_a_probability(self) -> None:
        for prior in (-0.1, 1.1, float("nan")):
            with self.subTest(prior=prior), self.assertRaises(ValueError):
                self.record(prior)
        self.assertEqual(self.sink.events, [])

    def test_a_sink_failure_never_fails_the_turn_it_describes(self) -> None:
        """`F-25`: emission failure never fails the work it describes."""
        recorder = CompetencePriorRecorder(clock=self.clock,
                                           events=fakes.RecordingSink(fails=True))

        self.assertFalse(recorder.record(episode_id="episode-1", run_id="run-1",
                                         principal="agent-1", prior=0.42,
                                         context=self.compiled))


class Reach(unittest.TestCase):
    """`M11`: the compiler is domain-agnostic data, not a coding-shaped module."""

    def test_the_compiler_holds_no_authority_and_no_kernel(self) -> None:
        compiler = build()
        for forbidden in ("dispatch", "kernel", "evaluate", "grant"):
            self.assertFalse(hasattr(compiler, forbidden), forbidden)

    def test_compiled_context_is_immutable(self) -> None:
        compiled = build().compile(brief="fix the parser")
        with self.assertRaises(Exception):
            compiled.blocks = ()  # type: ignore[misc]

    def test_a_block_is_immutable(self) -> None:
        block = Block(layer=Layer.TASK, source="operator", label="brief", text="b")
        with self.assertRaises(Exception):
            block.text = "c"  # type: ignore[misc]

    def test_the_compiled_context_is_what_the_model_port_consumes(self) -> None:
        """`ICD §4`: `ModelPort.propose(context, tools, sampling)`. The bundle
        is a mapping, so no adapter needs to know this type exists."""
        compiled: CompiledContext = build().compile(brief="fix the parser")
        bundle = compiled.bundle()

        self.assertEqual([message["layer"] for message in bundle["messages"]],
                         ["L1", "L2", "L3", "L4"])
        self.assertEqual(bundle["promptDigest"], compiled.digest)


if __name__ == "__main__":
    unittest.main()
