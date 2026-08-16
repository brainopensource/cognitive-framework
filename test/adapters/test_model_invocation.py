import unittest
import json
from vanguard.packages.adapters.models.invocation import ProposalTranslator, validate_proposal_schema

class TestModelInvocation(unittest.TestCase):
    def test_translate_text_only(self):
        proposal = {"text": "Hello world", "toolCalls": []}
        res = ProposalTranslator.translate(proposal)
        self.assertTrue(res.ok)
        self.assertEqual(res.value["kind"], "finish")
        self.assertEqual(res.value["note"], "Hello world")

    def test_translate_empty_proposal_fails(self):
        proposal = {"text": "", "toolCalls": []}
        res = ProposalTranslator.translate(proposal)
        self.assertFalse(res.ok)
        self.assertEqual(res.error.kind, "instrument_error")

    def test_translate_valid_tool_call(self):
        for tool_name, action in [
            ("fs.read", "read"),
            ("fs.search", "search"),
            ("patch.apply", "patch"),
            ("proc.test", "test"),
        ]:
            proposal = {
                "text": "",
                "toolCalls": [{"name": tool_name, "arguments": {"foo": "bar"}}]
            }
            res = ProposalTranslator.translate(proposal)
            self.assertTrue(res.ok)
            self.assertEqual(res.value["kind"], "effect")
            self.assertEqual(res.value["action"], action)
            self.assertEqual(res.value["args"], {"foo": "bar"})

    def test_translate_unknown_tool_fails(self):
        proposal = {
            "text": "",
            "toolCalls": [{"name": "fs.unknown", "arguments": {}}]
        }
        res = ProposalTranslator.translate(proposal)
        self.assertFalse(res.ok)

    def test_translate_malformed_args_fails(self):
        proposal = {
            "text": "",
            "toolCalls": [{"name": "fs.read", "arguments": "not-a-dict"}]
        }
        res = ProposalTranslator.translate(proposal)
        self.assertFalse(res.ok)

    def test_translate_multiple_actions_fails(self):
        proposal = {
            "text": "",
            "toolCalls": [
                {"name": "fs.read", "arguments": {}},
                {"name": "fs.search", "arguments": {}}
            ]
        }
        res = ProposalTranslator.translate(proposal)
        self.assertFalse(res.ok)

    def test_translate_oversized_args_fails(self):
        large_str = "a" * 1048577
        proposal = {
            "text": "",
            "toolCalls": [{"name": "fs.read", "arguments": {"data": large_str}}]
        }
        res = ProposalTranslator.translate(proposal)
        self.assertFalse(res.ok)

    def test_translate_deep_args_fails(self):
        # 21 levels deep
        deep_args = {}
        curr = deep_args
        for _ in range(21):
            curr["nested"] = {}
            curr = curr["nested"]
            
        proposal = {
            "text": "",
            "toolCalls": [{"name": "fs.read", "arguments": deep_args}]
        }
        res = ProposalTranslator.translate(proposal)
        self.assertFalse(res.ok)

    def test_validate_proposal_schema(self):
        res = validate_proposal_schema({})
        self.assertTrue(res.ok)
