"""Tests for Sprint 9 MetaLoopEngine."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.coordination import EpisodeCoordinator
from vanguard.packages.runtime.loops.meta_loop import MetaLoopEngine


class TestMetaLoopEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.tmp_dir) / "test_episodes.sqlite"
        self.coordinator = EpisodeCoordinator(self.db_path)
        self.engine = MetaLoopEngine(self.coordinator, max_turns=3)

    def test_context_compaction(self) -> None:
        files = {
            "main.py": "print('hello')",
            "cache.pyc": "binary data",
            "large.py": "x = 1\n" * 2000,
        }
        compacted = self.engine.compact_context(files, max_bytes=500)
        self.assertIn("main.py", compacted)
        self.assertNotIn("cache.pyc", compacted)
        self.assertIn("truncated", compacted["large.py"])

    def test_meta_loop_execution_with_mock_model(self) -> None:
        ws = Path(self.tmp_dir) / "ws"
        ws.mkdir(parents=True, exist_ok=True)
        (ws / "test_simple.py").write_text("def test_ok(): assert True\n", encoding="utf-8")

        def fake_complete(messages: list[dict]) -> dict:
            return {
                "choices": [{"message": {"role": "assistant", "content": "Tests pass."}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            }

        res = self.engine.run_loop(
            task_id="simple-task",
            workspace_dir=ws,
            complete_fn=fake_complete,
            test_runner=lambda p: (0, "all passed"),
        )
        self.assertTrue(res.passed)
        self.assertEqual(res.turns_executed, 1)
        self.assertEqual(res.prompt_tokens, 100)
        self.assertEqual(res.completion_tokens, 20)
        self.assertGreater(res.telemetry["cei"], 0.0)


if __name__ == "__main__":
    unittest.main()
