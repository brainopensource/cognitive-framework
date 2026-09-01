"""RF-91 (ADR-0089): code and explain share implementations; explain is read-only.

vg-code-default and vg-code-explain must reuse identical tool schemas and policies
without code duplication, while explain's capability ceiling must strictly forbid
patch.apply and proc.exec.
"""

from __future__ import annotations

import unittest

from vanguard.packages.runtime.compose import Runtime


class RF91PackReuseAndCeilingFalsifier(unittest.TestCase):
    def test_explain_harness_is_strictly_read_only(self) -> None:
        code_harness = Runtime.compose("vg-code-default")
        explain_harness = Runtime.compose("vg-code-explain")

        # Both must compose through the canonical Runtime.compose
        self.assertIn("fs.read", code_harness.verbs)
        self.assertIn("fs.search", code_harness.verbs)
        self.assertIn("patch.apply", code_harness.verbs)
        self.assertIn("proc.exec", code_harness.verbs)

        # Explain only has read/search verbs, zero privileged write/exec verbs
        self.assertIn("fs.read", explain_harness.verbs)
        self.assertIn("fs.search", explain_harness.verbs)
        self.assertNotIn("patch.apply", explain_harness.verbs)
        self.assertNotIn("proc.exec", explain_harness.verbs)

        # Explain ceiling must not permit write/exec
        verbs = explain_harness.verbs
        self.assertTrue(all(v.startswith("fs.") and ("write" not in v and "patch" not in v) for v in verbs))

    def test_code_and_explain_share_tool_schema_definitions(self) -> None:
        code_harness = Runtime.compose("vg-code-default")
        explain_harness = Runtime.compose("vg-code-explain")

        code_tools = {t.get("verb"): t for t in code_harness.tool_schemas if t.get("verb")}
        explain_tools = {t.get("verb"): t for t in explain_harness.tool_schemas if t.get("verb")}

        self.assertEqual(code_tools["fs.read"], explain_tools["fs.read"])
        self.assertEqual(code_tools["fs.search"], explain_tools["fs.search"])


if __name__ == "__main__":
    unittest.main()
