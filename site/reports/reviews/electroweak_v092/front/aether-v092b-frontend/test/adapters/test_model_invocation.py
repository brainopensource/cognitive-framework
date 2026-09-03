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

    def test_translate_json_string_arguments(self):
        proposal = {
            "text": "",
            "toolCalls": [{"name": "fs.read", "arguments": json.dumps({"path": "pkg/parser.py"})}],
        }
        res = ProposalTranslator.translate(proposal)
        self.assertTrue(res.ok)
        self.assertEqual(res.value["args"]["path"], "pkg/parser.py")

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
        self.assertEqual(result.value["resource"]["paths"], ["/workspace/pkg/parser.py"])

        result = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "read", "arguments": {"path": "/workspace/pkg/parser.py"}}]},
            tool_schemas=({"name": "read", "verb": "fs.read"},),
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.value["args"]["path"], "pkg/parser.py")
        self.assertEqual(result.value["resource"]["paths"], ["/workspace/pkg/parser.py"])

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

    def test_text_json_tool_block_becomes_an_effect(self) -> None:
        schemas = ({"name": "read", "verb": "fs.read",
                    "schema": {"type": "object", "properties": {"path": {"type": "string"}},
                               "required": ["path"]}},)
        res = ProposalTranslator.translate(
            {"text": '```json\n{"verb": "fs.read", "path": "pkg/parser.py"}\n```',
             "toolCalls": []},
            tool_schemas=schemas,
        )
        self.assertTrue(res.ok)
        self.assertEqual(res.value["kind"], "effect")
        self.assertEqual(res.value["action"], "fs.read")
        self.assertEqual(res.value["args"]["path"], "pkg/parser.py")

    def test_text_named_json_objects_take_first_call_only(self) -> None:
        schemas = (
            {"name": "search", "verb": "fs.search",
             "schema": {"type": "object",
                        "properties": {"path": {"type": "string"}, "pattern": {"type": "string"}},
                        "required": ["path", "pattern"]}},
            {"name": "read", "verb": "fs.read",
             "schema": {"type": "object", "properties": {"path": {"type": "string"}},
                        "required": ["path"]}},
        )
        text = (
            '{"name": "search", "arguments": {"path": "pkg/parser.py", "pattern": "def "}}\n'
            '{"name": "read", "arguments": {"path": "pkg/totals.py"}}'
        )
        res = ProposalTranslator.translate({"text": text, "toolCalls": []}, tool_schemas=schemas)
        self.assertTrue(res.ok)
        self.assertEqual(res.value["action"], "fs.search")
        self.assertEqual(res.value["args"]["path"], "pkg/parser.py")

    def test_fs_resource_is_canonical_under_workspace(self) -> None:
        res = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "fs.read", "arguments": {"path": "pkg/parser.py"}}]},
        )
        self.assertTrue(res.ok)
        resource = res.value["resource"]
        self.assertEqual(resource["kind"], "fs")
        self.assertEqual(resource["root"], "/workspace")
        self.assertEqual(resource["paths"], ["/workspace/pkg/parser.py"])
        self.assertEqual(set(resource), {"kind", "root", "paths"})

        from vanguard.packages.domain.selectors.resource_selector import decide
        held = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
        self.assertTrue(decide(held, resource).included)

    #: The vg-code-default `proc.exec` selector, verbatim from its manifest.
    PROC_SELECTOR = {"kind": "generic",
                     "uriPattern": "proc://exec/allow/git,pytest,ruff,python3"}

    def _exec_schemas(self, selector):
        return ({
            "name": "bash",
            "verb": "proc.exec",
            "schema": {
                "type": "object",
                "properties": {"argv": {"type": "array", "items": {"type": "string"}}},
                "required": ["argv"],
            },
            "selector": selector,
        },)

    def test_declared_proc_selector_binds_in_grant_and_is_parseable(self) -> None:
        """The bound resource is the granted selector, so it is not widening.

        `kind: process` is not in `SELECTOR_KINDS`; binding it made every
        `proc.exec` unparsable, which the classifier reads as widening and
        `F-09` then denies after the first untrusted receipt.
        """
        from vanguard.packages.domain.selectors.resource_selector import decide, parse_selector

        res = ProposalTranslator.translate(
            {"text": "", "toolCalls": [
                {"name": "bash", "arguments": json.dumps({"argv": ["pytest", "-q"]})}]},
            tool_schemas=self._exec_schemas(self.PROC_SELECTOR),
        )
        self.assertTrue(res.ok)
        resource = res.value["resource"]
        self.assertEqual(resource, self.PROC_SELECTOR)
        # No `root`, no `executable`: `generic` admits kind/uriPattern only.
        self.assertEqual(set(resource), {"kind", "uriPattern"})
        parse_selector(resource)
        self.assertTrue(decide(self.PROC_SELECTOR, resource).included)
        # The executable stays an argument; a resource is authority, not argv.
        self.assertEqual(res.value["args"]["argv"], ["pytest", "-q"])

    def test_proc_selector_outside_the_grant_is_still_denied(self) -> None:
        """Task 1/2 widen nothing: a different uriPattern remains out of grant."""
        from vanguard.packages.domain.selectors.resource_selector import decide

        res = ProposalTranslator.translate(
            {"text": "", "toolCalls": [
                {"name": "bash", "arguments": json.dumps({"argv": ["curl", "http://x"]})}]},
            tool_schemas=self._exec_schemas(
                {"kind": "generic", "uriPattern": "proc://exec/allow/curl"}),
        )
        self.assertTrue(res.ok)
        self.assertFalse(decide(self.PROC_SELECTOR, res.value["resource"]).included)

    def test_inferred_argv_selector_is_generic_never_process(self) -> None:
        """With no declared selector the inference must still be parseable."""
        from vanguard.packages.domain.selectors.resource_selector import parse_selector

        res = ProposalTranslator.translate(
            {"text": "", "toolCalls": [
                {"name": "proc.exec", "arguments": json.dumps({"argv": ["pytest"]})}]},
        )
        self.assertTrue(res.ok)
        resource = res.value["resource"]
        self.assertEqual(resource["kind"], "generic")
        self.assertNotEqual(resource["kind"], "process")
        parse_selector(resource)

    def test_extra_fs_key_stays_out_of_grant(self) -> None:
        """Deny-closed: an unparsable fs selector is not repaired into a grant."""
        from vanguard.packages.domain.selectors.resource_selector import decide

        held = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
        self.assertFalse(decide(held, {**held, "path": "/workspace/a.py"}).included)


    def test_text_tool_call_using_parameters_key_is_lifted(self) -> None:
        """`parameters` is the third call spelling small models emit.

        It is the key OpenAI's tool *schema* uses for the argument object, and
        instruction-tuned models copy it into the call. Observed live from
        llama3.2:3b: a correct whole-file fix, dropped as prose.
        """
        schemas = ({"name": "patch", "verb": "patch.apply",
                    "schema": {"type": "object",
                               "properties": {"path": {"type": "string"},
                                              "content": {"type": "string"}},
                               "required": ["path"]},
                    "selector": {"kind": "fs", "root": "/workspace",
                                 "paths": ["/workspace"]}},)
        text = json.dumps({"name": "patch",
                           "parameters": {"path": "pkg/stats.py", "content": "V = 1\n"}})
        res = ProposalTranslator.translate(
            {"text": text, "toolCalls": []}, tool_schemas=schemas)
        self.assertTrue(res.ok)
        self.assertEqual(res.value["action"], "patch.apply")
        self.assertEqual(res.value["args"]["path"], "pkg/stats.py")
        self.assertEqual(res.value["args"]["content"], "V = 1\n")

    def test_plain_json_without_a_call_shape_is_still_prose(self) -> None:
        """The `parameters` synonym must not make every JSON object a tool."""
        res = ProposalTranslator.translate(
            {"text": json.dumps({"name": "some report", "summary": "done"}),
             "toolCalls": []})
        self.assertTrue(res.ok)
        self.assertEqual(res.value["kind"], "finish")

    FENCED_SCHEMAS = ({"name": "patch", "verb": "patch.apply",
                       "payloadArgument": "content",
                       "schema": {"type": "object",
                                  "properties": {"path": {"type": "string"},
                                                 "content": {"type": "string"}},
                                  "required": ["path"]},
                       "selector": {"kind": "fs", "root": "/workspace",
                                    "paths": ["/workspace"]}},)

    def test_fenced_payload_carries_code_without_any_escaping(self) -> None:
        """The payload rides outside the JSON, so nothing has to be escaped.

        Asking a model to embed a program in a JSON string is asking it to
        escape every quote and backslash while writing the program. Observed
        across three local models and two families: all three produced correct
        algorithms, none produced valid JSON.
        """
        body = 'def f():\n    return "a \\ b"  # quote and backslash\n'
        text = "Sure.\n\n```patch path=pkg/x.py\n" + body + "```\n"
        res = ProposalTranslator.translate({"text": text, "toolCalls": []},
                                           tool_schemas=self.FENCED_SCHEMAS)
        self.assertTrue(res.ok)
        self.assertEqual(res.value["action"], "patch.apply")
        self.assertEqual(res.value["args"]["path"], "pkg/x.py")
        self.assertEqual(res.value["args"]["content"], body.rstrip("\n"))
        self.assertEqual(res.value["resource"]["paths"], ["/workspace/pkg/x.py"])

    def test_a_plain_code_fence_is_not_an_action(self) -> None:
        """Only a fence whose info string opens with a declared tool name acts."""
        res = ProposalTranslator.translate(
            {"text": "My plan:\n```python\nprint(1)\n```\n", "toolCalls": []},
            tool_schemas=self.FENCED_SCHEMAS)
        self.assertTrue(res.ok)
        self.assertEqual(res.value["kind"], "finish")

    def test_fenced_lifting_is_off_unless_the_schema_declares_a_payload(self) -> None:
        """`C-01`: opting in is pack data, never a builtin verb list here."""
        plain = ({"name": "patch", "verb": "patch.apply",
                  "schema": {"type": "object",
                             "properties": {"path": {"type": "string"},
                                            "content": {"type": "string"}},
                             "required": ["path"]}},)
        res = ProposalTranslator.translate(
            {"text": "```patch path=a.py\nx = 1\n```\n", "toolCalls": []},
            tool_schemas=plain)
        self.assertTrue(res.ok)
        self.assertEqual(res.value["kind"], "finish")

    def test_fenced_info_string_accepts_quoted_values(self) -> None:
        res = ProposalTranslator.translate(
            {"text": '```patch path="dir with space/x.py"\nx = 1\n```\n', "toolCalls": []},
            tool_schemas=self.FENCED_SCHEMAS)
        self.assertTrue(res.ok)
        self.assertEqual(res.value["args"]["path"], "dir with space/x.py")

    def test_a_truncated_fence_is_reported_not_silently_dropped(self) -> None:
        """A reply cut off by the token ceiling must say so.

        Observed: gpt-5.6-luna opened ```patch and ran out of completion
        tokens mid-file. With no closing fence the action degraded to prose,
        the turn was spent, and the model was told nothing.
        """
        text = "```patch path=solution.py\ndef encode(text):\n    partial"
        res = ProposalTranslator.translate({"text": text, "toolCalls": []},
                                           tool_schemas=self.FENCED_SCHEMAS)
        self.assertFalse(res.ok)
        self.assertIn("never closed", res.error.message)

    def test_a_truncated_fence_never_writes_the_partial_payload(self) -> None:
        """Half a file on disk is worse than none."""
        text = "```patch path=solution.py\ndef encode(text):\n    partial"
        res = ProposalTranslator.translate({"text": text, "toolCalls": []},
                                           tool_schemas=self.FENCED_SCHEMAS)
        self.assertFalse(res.ok)
        self.assertNotIn("partial", str(getattr(res, "value", "")))

    def test_prose_mentioning_a_fence_word_is_still_prose(self) -> None:
        res = ProposalTranslator.translate(
            {"text": "I will patch the file next.", "toolCalls": []},
            tool_schemas=self.FENCED_SCHEMAS)
        self.assertTrue(res.ok)
        self.assertEqual(res.value["kind"], "finish")
