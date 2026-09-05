"""T-36: ResultDistiller caps tool bodies and echoes the goal at L5 tail."""

from __future__ import annotations

import unittest

from vanguard.packages.agency.context import ContextCompiler, Fragment, Layer, estimate_tokens
from vanguard.packages.agency.context.distiller import TOOL_BODY_CHAR_CAP, distill_tool_output
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.runtime.session import _admit_turn_result

from test.agency.test_context_compiler import build, dialogue


class ResultDistillerTests(unittest.TestCase):
    def test_short_output_is_unchanged_and_digest_bound(self) -> None:
        distilled = distill_tool_output("ok\n")
        self.assertFalse(distilled.truncated)
        self.assertEqual(distilled.compact_text, "ok\n")
        self.assertEqual(distilled.full_artifact_digest, digest_of({"toolOutput": "ok\n"}))
        self.assertEqual(distilled.tokens_saved, 0)

    def test_oversized_stdout_is_truncated_and_digest_bound(self) -> None:
        payload = "x" * 8000
        distilled = distill_tool_output(payload)
        self.assertTrue(distilled.truncated)
        self.assertLessEqual(len(distilled.compact_text), TOOL_BODY_CHAR_CAP + 80)
        self.assertIn(distilled.full_artifact_digest, distilled.compact_text)
        self.assertEqual(distilled.full_artifact_digest, digest_of({"toolOutput": payload}))
        self.assertGreater(distilled.tokens_saved, 0)
        self.assertTrue(distilled.compact_text.startswith("x" * 16))
        self.assertTrue(distilled.compact_text.endswith("x" * 16))


class GoalEchoTests(unittest.TestCase):
    def test_goal_echo_is_present_after_compaction(self) -> None:
        brief = "implement the store and keep checksums monotonic"
        floor = build().compile(brief=brief).total_tokens
        compiled = build(token_ceiling=floor + 16).compile(
            brief=brief,
            dialogue=dialogue(30, size=400),
        )
        l5 = compiled.layer_blocks(Layer.DIALOGUE)
        self.assertTrue(l5)
        self.assertEqual(l5[-1].source, "goal-echo")
        self.assertIn(brief, l5[-1].text)
        self.assertNotIn("goal-echo", compiled.dropped)


class EffectBoundaryDistillTests(unittest.TestCase):
    def test_admit_turn_result_caps_oversized_tool_stdout(self) -> None:
        notes: list[dict[str, object]] = []

        class Operator:
            def note(self, **note: object) -> None:
                notes.append(note)

        payload = "line\n" * 2000
        outcome = type("Outcome", (), {"result_digest": "sha256:" + "a" * 64, "detail": payload})()
        result = type("R", (), {"outcome": outcome, "detail": payload})()
        span = _admit_turn_result(Operator(), 4, result)
        self.assertIsNotNone(span)
        self.assertEqual(len(notes), 1)
        text = str(notes[0]["text"])
        self.assertLessEqual(len(text), TOOL_BODY_CHAR_CAP + 250)
        self.assertIn(digest_of({"toolOutput": payload}), text)


if __name__ == "__main__":
    unittest.main()
