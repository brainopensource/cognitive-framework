"""Unit tests for WorkspaceDiscovery engine (Task A.2)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.agency.context.layers import Layer
from vanguard.packages.agency.manifests.discovery import (
    WorkspaceDiscovery,
)


class TestWorkspaceDiscovery(unittest.TestCase):
    def test_discovery_empty_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = WorkspaceDiscovery(tmpdir)
            instructions = discovery.discover()
            self.assertEqual(instructions, ())
            self.assertEqual(discovery.render_environment_text(), "")
            self.assertIsNone(discovery.as_environment_block())
            self.assertEqual(discovery.as_fragments(), ())

    def test_discovery_agents_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            agents_md = tmp_path / "AGENTS.md"
            agents_md.write_text("# Project Rules\n\nUse TDD.", encoding="utf-8")

            discovery = WorkspaceDiscovery(tmpdir)
            instructions = discovery.discover()
            self.assertEqual(len(instructions), 1)
            self.assertEqual(instructions[0].filename, "AGENTS.md")
            self.assertEqual(instructions[0].content, "# Project Rules\n\nUse TDD.")

            # Check L3 environment block
            block = discovery.as_environment_block()
            self.assertIsNotNone(block)
            assert block is not None
            self.assertEqual(block.layer, Layer.ENVIRONMENT)
            self.assertIn("=== Workspace Instructions (AGENTS.md) ===", block.text)
            self.assertIn("# Project Rules\n\nUse TDD.", block.text)

            # Check L4 fragments
            fragments = discovery.as_fragments()
            self.assertEqual(len(fragments), 1)
            self.assertEqual(fragments[0].label, "instruction:agents_md")
            self.assertIn("[AGENTS.md]", fragments[0].text)

    def test_discovery_multiple_candidate_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "AGENTS.md").write_text("Agents guide", encoding="utf-8")
            (tmp_path / "CLAUDE.md").write_text("Claude guide", encoding="utf-8")

            discovery = WorkspaceDiscovery(tmpdir)
            instructions = discovery.discover()
            self.assertEqual(len(instructions), 2)
            filenames = [inst.filename for inst in instructions]
            self.assertEqual(filenames, ["AGENTS.md", "CLAUDE.md"])

            text = discovery.render_environment_text()
            self.assertIn("AGENTS.md", text)
            self.assertIn("CLAUDE.md", text)


if __name__ == "__main__":
    unittest.main()
