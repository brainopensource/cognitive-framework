"""Tests for trajectory log importer."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from importer import import_trajectory


class TestLamImporter(unittest.TestCase):
    def test_import_trajectory_maps_claude_code_verbs(self) -> None:
        tmp_dir = tempfile.mkdtemp()
        jsonl_path = Path(tmp_dir) / "claude_session.jsonl"

        lines = [
            json.dumps({"tool_calls": [{"function": {"name": "read_file", "arguments": '{"path": "foo.py"}'}}]}),
            json.dumps({"tool_calls": [{"function": {"name": "bash", "arguments": '{"command": "pytest"}'}}]}),
            json.dumps({"tool_calls": []}),
        ]
        jsonl_path.write_text("\n".join(lines), encoding="utf-8")

        workspace = {"foo.py": "print(1)"}
        sc = import_trajectory(jsonl_path, "t1-calculator", 1, "Imported Calculator", workspace)

        self.assertEqual(sc["id"], "t1-calculator")
        self.assertEqual(sc["title"], "Imported Calculator")
        self.assertEqual(len(sc["turns"]), 3)
        self.assertEqual(sc["turns"][0]["tool_calls"][0]["function"]["name"], "view_file")
        self.assertEqual(sc["turns"][1]["tool_calls"][0]["function"]["name"], "run_command")


if __name__ == "__main__":
    unittest.main()
