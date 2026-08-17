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
        for tool_name, action, args in [
            ("fs.read", "fs.read", {"path": "src/a.py"}),
            ("fs.search", "fs.search", {"pattern": "TODO", "path": "."}),
            ("patch.apply", "patch.apply", {"path": ".", "patch": "diff"}),
            ("proc.test", "proc.test", {"argv": ["pytest", "-q"]}),
        ]:
            proposal = {
                "text": "",
                "toolCalls": [{"name": tool_name, "arguments": args}]
            }
            res = ProposalTranslator.translate(proposal)
            self.assertTrue(res.ok)
            self.assertEqual(res.value["kind"], "effect")
            self.assertEqual(res.value["action"], action)
            self.assertEqual(res.value["args"], args)
            self.assertIsNone(res.value["reservation"])

    def test_translate_unknown_tool_fails(self):
        proposal = {
            "text": "",
            "toolCalls": [{"name": "fs.unknown", "arguments": {}}]
        }
        res = ProposalTranslator.translate(
            proposal,
            tool_schemas=({"name": "read", "verb": "fs.read"},),
        )
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
        self.assertFalse(res.ok)

    def test_validate_proposal_schema_rejects_wrong_types_and_authority(self):
        self.assertFalse(validate_proposal_schema({"text": 42}).ok)
        self.assertFalse(validate_proposal_schema({"text": "ok", "toolCalls": {}}).ok)
        self.assertFalse(validate_proposal_schema({
            "text": "",
            "toolCalls": [{"name": "fs.read", "arguments": {}, "reservation": "grant"}],
        }).ok)

    def test_translate_always_leaves_authority_for_runtime_binding(self):
        result = ProposalTranslator.translate({
            "text": "",
            "toolCalls": [{"name": "fs.read", "arguments": {"path": "x.py"}}],
        })
        self.assertTrue(result.ok)
        self.assertIsNone(result.value["reservation"])

    def test_manifest_binds_declared_tool_and_rejects_escape(self):
        result = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "read", "arguments": {"path": "x.py"}}]},
            tool_schemas=({"name": "read", "verb": "fs.read"},),
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.value["resource"]["root"], "/workspace")
        self.assertFalse(ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "read", "arguments": {"path": "../x"}}]},
            tool_schemas=({"name": "read", "verb": "fs.read"},),
        ).ok)

    def test_search_root_aliases_stay_inside_workspace(self):
        schemas = ({"name": "search", "verb": "fs.search"},)
        for path in ("", "/", "/workspace"):
            result = ProposalTranslator.translate(
                {"text": "", "toolCalls": [{"name": "search", "arguments": {"path": path, "pattern": "def "}}]},
                tool_schemas=schemas,
            )
            self.assertTrue(result.ok, path)
            self.assertEqual(result.value["args"]["path"], ".")

    def test_workspace_absolute_paths_are_bound_inside_the_root(self):
        result = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "read", "arguments": {"path": "/workspace/pkg/parser.py"}}]},
            tool_schemas=({"name": "read", "verb": "fs.read"},),
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.value["args"]["path"], "pkg/parser.py")
        self.assertEqual(result.value["resource"]["path"], "pkg/parser.py")

        result = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "read", "arguments": {"path": "/workspace/pkg/parser.py"}}]},
            tool_schemas=({"name": "read", "verb": "fs.read"},),
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.value["args"]["path"], "pkg/parser.py")
        self.assertEqual(result.value["resource"]["path"], "pkg/parser.py")

    def test_aliases_mapping_resolves_and_normalizes_arguments(self):
        aliases = {
            "to_canonical": {
                "Read": "fs.read",
                "Edit": "patch.apply",
                "Bash": "proc.exec",
                "Glob": "fs.search",
            }
        }
        # Read with file_path argument alias
        res = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "Read", "arguments": {"file_path": "foo.py"}}]},
            aliases=aliases,
        )
        self.assertTrue(res.ok)
        self.assertEqual(res.value["action"], "fs.read")
        self.assertEqual(res.value["args"]["path"], "foo.py")

        # Bash with command string argument
        res = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "Bash", "arguments": {"command": "pytest -v"}}]},
            aliases=aliases,
        )
        self.assertTrue(res.ok)
        self.assertEqual(res.value["action"], "proc.exec")
        self.assertEqual(res.value["args"]["argv"], ["pytest", "-v"])

        # Undeclared tool with aliases present fails
        res = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "NonExistent", "arguments": {}}]},
            aliases=aliases,
        )
        self.assertFalse(res.ok)
        self.assertEqual(res.error.kind, "instrument_error")

    def test_undeclared_competitor_name_fails_without_schema_or_aliases(self):
        # Without schemas/aliases, hardcoded competitor name fails because KNOWN_TOOLS shrunk
        res = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "read", "arguments": {"path": "x.py"}}]},
        )
        self.assertFalse(res.ok)
        self.assertEqual(res.error.kind, "instrument_error")

