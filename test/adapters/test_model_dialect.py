"""BEP-02 provider dialect and normalization falsifiers."""

import unittest

from vanguard.packages.adapters.models.dialect import (
    ModelIntent,
    NormalizedResponse,
    compile_intent,
    normalize_response,
)
from vanguard.packages.domain.models.profile import ModelCapabilityProfile, ToolCallStyle


class TestModelDialect(unittest.TestCase):
    def test_native_projection_keeps_tools_structured(self) -> None:
        profile = ModelCapabilityProfile("native", tool_call_style=ToolCallStyle.NATIVE)
        request = compile_intent(ModelIntent("system", tools=({"name": "read", "schema": {"type": "object"}},)), profile)
        self.assertEqual(request.tools[0]["type"], "function")
        self.assertEqual(request.profile_id, "native")
        self.assertTrue(request.capability_profile_digest)

    def test_unknown_model_uses_conservative_fenced_projection(self) -> None:
        request = compile_intent(ModelIntent("system"), "unregistered/model")
        self.assertEqual(request.tools, ())
        self.assertIn("```json", request.messages[0]["content"])

    def test_native_response_normalizes_tool_call(self) -> None:
        result = normalize_response({"choices": [{"message": {"tool_calls": [
            {"function": {"name": "read", "arguments": '{"path":"a.py"}'}}
        ]}}]})
        self.assertTrue(result.ok)
        self.assertEqual(result.proposal["kind"], "effect")
        self.assertEqual(result.proposal["args"]["path"], "a.py")

    def test_malformed_and_truncated_responses_are_typed(self) -> None:
        malformed = normalize_response("not json")
        truncated = normalize_response('{"kind":"effect"')
        self.assertIsInstance(malformed, NormalizedResponse)
        self.assertEqual(malformed.failure, "not_json")
        self.assertEqual(truncated.failure, "truncated")

    def test_text_grammar_normalizes_without_json(self) -> None:
        profile = ModelCapabilityProfile("weak", tool_call_style=ToolCallStyle.TEXT_GRAMMAR)
        result = normalize_response("KIND: finish\nACTION: -\nARGS: {}", profile)
        self.assertTrue(result.ok)
        self.assertEqual(result.proposal["kind"], "finish")


if __name__ == "__main__":
    unittest.main()
