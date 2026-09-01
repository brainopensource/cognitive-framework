"""Tests for protocol middleware decoders, normalizers, and validators."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.protocol.dsml_decoder import decode_dsml_markup
from middleware.protocol.json_argument_normalizer import normalize_json_arguments
from middleware.protocol.markdown_patch_detector import detect_markdown_patch
from middleware.protocol.native_tool_call_decoder import decode_native_tool_call
from middleware.protocol.role_history_validator import validate_role_history
from middleware.protocol.tool_schema_validator import validate_tool_arguments
from middleware.protocol.truncation_detector import detect_truncation


class TestProtocolMiddleware(unittest.TestCase):
    def test_decode_native_tool_call(self) -> None:
        openai_call = {
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "fs.read",
                        "arguments": '{"path": "src/main.py"}',
                    },
                }
            ]
        }
        res = decode_native_tool_call(openai_call)
        self.assertIsNotNone(res)
        self.assertEqual(res["kind"], "effect")
        self.assertEqual(res["action"], "fs.read")
        self.assertEqual(res["args"], {"path": "src/main.py"})

    def test_decode_dsml_markup(self) -> None:
        dsml_text = '<invoke name="fs.read"><parameter name="path">"src/main.py"</parameter></invoke>'
        res = decode_dsml_markup(dsml_text)
        self.assertIsNotNone(res)
        self.assertEqual(res["action"], "fs.read")
        self.assertEqual(res["args"]["path"], "src/main.py")

    def test_normalize_json_arguments(self) -> None:
        raw_trailing_comma = '{"path": "foo.py", "lines": [1, 2, ], }'
        parsed, repaired = normalize_json_arguments(raw_trailing_comma)
        self.assertTrue(repaired)
        self.assertEqual(parsed["path"], "foo.py")

    def test_detect_markdown_patch(self) -> None:
        diff_text = """Here is the fix:
```diff
--- a/calculator.py
+++ b/calculator.py
@@ -1,2 +1,2 @@
-def multiply(a, b): return a + b
+def multiply(a, b): return a * b
```
"""
        detection = detect_markdown_patch(diff_text)
        self.assertTrue(detection.has_patch)
        self.assertIn("--- a/calculator.py", detection.patch_content)
        self.assertEqual(detection.target_file, "calculator.py")

    def test_detect_truncation(self) -> None:
        self.assertTrue(detect_truncation({"finish_reason": "length"}))
        self.assertTrue(detect_truncation('{"action": "fs.read", "args": {"path": "test.'))
        self.assertFalse(detect_truncation({"finish_reason": "stop", "content": '{"complete": true}'}))

    def test_validate_tool_arguments(self) -> None:
        errors = validate_tool_arguments("fs.read", {})
        self.assertIn("missing required argument 'path'", errors)

        valid_errors = validate_tool_arguments("fs.read", {"path": "main.py"})
        self.assertEqual(len(valid_errors), 0)

    def test_validate_role_history(self) -> None:
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "tool_calls": [{"id": "c1", "type": "function", "function": {"name": "f"}}]},
            {"role": "tool", "tool_call_id": "c1", "content": "result"},
        ]
        errors = validate_role_history(messages)
        self.assertEqual(len(errors), 0)

        unpaired = [
            {"role": "assistant", "tool_calls": [{"id": "c2", "type": "function", "function": {"name": "f"}}]},
        ]
        self.assertTrue(len(validate_role_history(unpaired)) > 0)


if __name__ == "__main__":
    unittest.main()
