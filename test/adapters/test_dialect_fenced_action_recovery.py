"""T-82 fenced-action recovery and premature-finish falsifiers."""

from __future__ import annotations

import unittest

from vanguard.packages.adapters.models.dialect import normalize_response
from vanguard.packages.adapters.models.invocation import ProposalTranslator
from vanguard.packages.agency.admission import admit_finish_candidate


READ_SCHEMA = ({
    "name": "read",
    "verb": "fs.read",
    "schema": {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
    "selector": {
        "kind": "fs",
        "root": "/workspace",
        "paths": ["/workspace"],
    },
},)
FINISH_SCHEMA = {
    "name": "finish",
    "verb": "agency.finish",
    "schema": {
        "type": "object",
        "properties": {"summary": {"type": "string"}},
        "required": ["summary"],
        "additionalProperties": False,
    },
}


class TestDialectFencedActionRecovery(unittest.TestCase):
    def test_action_spelling_in_fenced_note_recovers_through_manifest_validation(self) -> None:
        response = {
            "text": 'I will inspect the input.\n```json\n{"action":"read","path":"data/orders.csv"}\n```',
            "toolCalls": [],
        }

        result = ProposalTranslator.translate(response, tool_schemas=READ_SCHEMA)

        self.assertTrue(result.ok, result.error)
        self.assertEqual(result.value["kind"], "effect")
        self.assertEqual(result.value["action"], "fs.read")
        self.assertEqual(result.value["args"], {"path": "data/orders.csv"})
        self.assertEqual(result.value["resource"]["paths"], ["/workspace/data/orders.csv"])

    def test_outer_null_action_recovers_fenced_note_candidate(self) -> None:
        result = normalize_response({
            "kind": "finish",
            "action": None,
            "note": '```json\n{"kind":"effect","action":"read","args":{"path":"test_report.py"}}\n```',
        })

        self.assertTrue(result.ok, result.failure)
        self.assertEqual(result.proposal["kind"], "effect")
        self.assertEqual(result.proposal["action"], "read")
        self.assertEqual(result.proposal["args"], {"path": "test_report.py"})

    def test_non_null_outer_action_is_never_replaced_by_note(self) -> None:
        result = normalize_response({
            "kind": "effect",
            "action": "fs.search",
            "args": {"pattern": "class "},
            "note": '```json\n{"kind":"effect","action":"read","args":{"path":"x.py"}}\n```',
        })

        self.assertTrue(result.ok, result.failure)
        self.assertEqual(result.proposal["action"], "fs.search")

    def test_multiple_fenced_note_actions_are_rejected_as_ambiguous(self) -> None:
        result = normalize_response({
            "kind": "finish",
            "action": None,
            "note": (
                '```json\n{"action":"read","path":"a.py"}\n```\n'
                '```json\n{"action":"read","path":"b.py"}\n```'
            ),
        })

        self.assertFalse(result.ok)
        self.assertEqual(result.failure, "PREMATURE_FINISH_REJECTED")

    def test_unparsed_invocation_does_not_decay_into_finish(self) -> None:
        result = ProposalTranslator.translate(
            {
                "text": '```json\n{"action":"read","path":}\n```',
                "toolCalls": [],
            },
            tool_schemas=READ_SCHEMA,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "PREMATURE_FINISH_REJECTED")

    def test_unparsed_invocation_remaining_after_valid_one_rejects_candidate(self) -> None:
        result = ProposalTranslator.translate(
            {
                "text": (
                    '```json\n{"action":"read","path":"safe.py"}\n```\n'
                    '```json\n{"action":"read","path":}\n```'
                ),
                "toolCalls": [],
            },
            tool_schemas=READ_SCHEMA,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "PREMATURE_FINISH_REJECTED")

    def test_declared_finish_makes_text_only_completion_fail_closed(self) -> None:
        result = ProposalTranslator.translate(
            {"text": "Everything looks done.", "toolCalls": []},
            tool_schemas=READ_SCHEMA + (FINISH_SCHEMA,),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "PREMATURE_FINISH_REJECTED")

    def test_explicit_finish_before_mutation_and_verification_is_rejected(self) -> None:
        verdict = admit_finish_candidate(
            {"kind": "finish", "note": "done"},
            mutation_observed=False,
            verification_observed=False,
        )

        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "PREMATURE_FINISH_REJECTED")

    def test_explicit_finish_is_manifest_declared_and_typed(self) -> None:
        undeclared = ProposalTranslator.translate({
            "text": "",
            "toolCalls": [{"name": "finish", "arguments": {"summary": "done"}}],
        })
        missing = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "finish", "arguments": {}}]},
            tool_schemas=(FINISH_SCHEMA,),
        )
        wrong_type = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "finish", "arguments": {"summary": 7}}]},
            tool_schemas=(FINISH_SCHEMA,),
        )
        extra = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{
                "name": "finish",
                "arguments": {"summary": "done", "approval": True},
            }]},
            tool_schemas=(FINISH_SCHEMA,),
        )
        valid = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{
                "name": "finish",
                "arguments": {"summary": "verified change"},
            }]},
            tool_schemas=(FINISH_SCHEMA,),
        )

        for result in (undeclared, missing, wrong_type, extra):
            self.assertFalse(result.ok)
            self.assertEqual(result.error.kind, "instrument_error")
        self.assertTrue(valid.ok, valid.error)
        self.assertEqual(valid.value, {"kind": "finish", "note": "verified change"})

    def test_recovered_action_still_rejects_invalid_typed_resource(self) -> None:
        result = ProposalTranslator.translate(
            {
                "text": '```json\n{"action":"read","path":"../secrets"}\n```',
                "toolCalls": [],
            },
            tool_schemas=READ_SCHEMA,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")


if __name__ == "__main__":
    unittest.main()
