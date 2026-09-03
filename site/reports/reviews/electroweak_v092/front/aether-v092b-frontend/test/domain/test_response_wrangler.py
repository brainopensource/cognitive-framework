"""Unit tests for ResponseWrangler and Protocol Decoders."""

import json
import unittest

from vanguard.packages.domain.transforms.protocol.response_wrangler import (
    DSMLDecoderPlugin,
    JSONArgumentNormalizerPlugin,
    MarkdownPatchDecoderPlugin,
    ResponseWrangler,
)


class TestResponseWrangler(unittest.TestCase):

    def test_dsml_decoder_plugin(self) -> None:
        plugin = DSMLDecoderPlugin()
        text = 'Analyzing code... <｜DSML｜tool_calls>[{"name": "fs.read", "arguments": {"path": "main.py"}}]</｜DSML｜tool_calls>'
        res = plugin.decode(text, ())
        self.assertIsNotNone(res)
        assert res is not None
        self.assertEqual(res.classification, "dsml_decoded")
        self.assertEqual(len(res.tool_calls), 1)
        self.assertIn("fs.read", str(res.tool_calls[0]))

    def test_markdown_patch_decoder_plugin(self) -> None:
        plugin = MarkdownPatchDecoderPlugin()
        text = (
            "Here is the fix:\n"
            "```diff\n"
            "--- a/lru/entry.py\n"
            "+++ b/lru/entry.py\n"
            "@@ -10,3 +10,3 @@\n"
            "-    return self.val\n"
            "+    return self.val or None\n"
            "```"
        )
        res = plugin.decode(text, ())
        self.assertIsNotNone(res)
        assert res is not None
        self.assertEqual(res.classification, "markdown_patch_extracted")
        self.assertEqual(len(res.tool_calls), 1)
        self.assertEqual(res.tool_calls[0]["function"]["name"], "patch.apply")

    def test_json_argument_normalizer(self) -> None:
        raw_args = '{"path": "file.py",\n"content": "line1\nline2"}'
        normalized = JSONArgumentNormalizerPlugin.normalize_arguments(raw_args)
        self.assertIsInstance(normalized, dict)
        self.assertEqual(normalized.get("path"), "file.py")

    def test_full_response_wrangler(self) -> None:
        wrangler = ResponseWrangler()
        text = "```diff\n--- a/main.py\n+++ b/main.py\n@@ -1 +1 @@\n-old\n+new\n```"
        res = wrangler.wrangle(text, ())
        self.assertEqual(res.classification, "markdown_patch_extracted")
        self.assertEqual(len(res.tool_calls), 1)


if __name__ == "__main__":
    unittest.main()
