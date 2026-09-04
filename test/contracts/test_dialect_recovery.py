"""T-21: dialect recovery classifies truncated JSON, DeepSeek fences, and XML tags.

A classified failure MUST NOT report ok. Valid recovered payloads may be ok.
"""

from __future__ import annotations

import unittest

from vanguard.packages.adapters.models.dialect import normalize_response


class TestDialectRecovery(unittest.TestCase):
    def test_truncated_json_is_classified_not_ok(self) -> None:
        result = normalize_response('{"kind":"effect","action":"read","args":{')
        self.assertFalse(result.ok)
        self.assertIsNone(result.proposal)
        self.assertIn(result.failure, {"truncated", "truncation"})

    def test_deepseek_fence_truncated_json_is_classified_not_ok(self) -> None:
        raw = (
            "<think>plan the edit</think>\n"
            "```json\n"
            '{"kind":"effect","action":"patch.apply","args":{"path":"a.py"'
            "\n"
        )
        result = normalize_response(raw)
        self.assertFalse(result.ok)
        self.assertIsNone(result.proposal)
        self.assertIsNotNone(result.failure)
        self.assertIn(result.failure, {"truncated", "truncation", "deepseek_fence"})

    def test_deepseek_dsml_without_payload_is_classified_not_ok(self) -> None:
        result = normalize_response('<|DSML|invoke name="read">incomplete')
        self.assertFalse(result.ok)
        self.assertIsNone(result.proposal)
        self.assertEqual(result.failure, "deepseek_fence")

    def test_xml_tool_tags_truncated_are_classified_not_ok(self) -> None:
        result = normalize_response(
            "<tool_call>\n"
            '{"name":"read","arguments":{"path":"a.py"'
            "\n"
        )
        self.assertFalse(result.ok)
        self.assertIsNone(result.proposal)
        self.assertIn(result.failure, {"truncated", "truncation", "xml_tool_tags"})

    def test_xml_tool_tags_non_json_are_classified_not_ok(self) -> None:
        result = normalize_response("<tool_call>please read a.py</tool_call>")
        self.assertFalse(result.ok)
        self.assertIsNone(result.proposal)
        self.assertEqual(result.failure, "xml_tool_tags")

    def test_valid_fenced_json_still_normalizes(self) -> None:
        result = normalize_response('```json\n{"kind":"finish"}\n```')
        self.assertTrue(result.ok)
        self.assertEqual(result.proposal["kind"], "finish")
        self.assertIsNone(result.failure)


if __name__ == "__main__":
    unittest.main()
