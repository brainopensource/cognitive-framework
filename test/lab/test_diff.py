"""Side-by-side tool-cascade diffs."""

from __future__ import annotations

import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_lab(name: str):
    path = ROOT / "lab" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lab_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CascadeDiff(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "lam.sqlite"
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                """
                CREATE TABLE traces (
                    trace_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id TEXT NOT NULL,
                    backend TEXT NOT NULL DEFAULT 'lam',
                    model TEXT NOT NULL DEFAULT 'lam/x',
                    passed INTEGER NOT NULL DEFAULT 1,
                    llm_calls INTEGER NOT NULL DEFAULT 2,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL DEFAULT 0,
                    usd REAL NOT NULL DEFAULT 0,
                    wall_s REAL NOT NULL DEFAULT 0.01,
                    recorded_at TEXT NOT NULL DEFAULT '2026-08-16T00:00:00Z',
                    harness TEXT,
                    cascade TEXT
                );
                """
            )
            conn.execute(
                "INSERT INTO traces (scenario_id, prompt_tokens, harness, cascade) VALUES (?,?,?,?)",
                ("s1", 120, "vg-code-default", json_cascade(["fs.read", "patch.apply", "proc.exec"])),
            )
            conn.execute(
                "INSERT INTO traces (scenario_id, prompt_tokens, harness, cascade) VALUES (?,?,?,?)",
                ("s1", 80, "vg-shell-only", json_cascade(["proc.exec", "proc.exec"])),
            )
            conn.commit()
        self.diff = load_lab("diff")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_side_by_side_marks_tool_disagreement(self) -> None:
        text = self.diff.render_diff(self.db, 1, 2)
        self.assertIn("fs.read", text)
        self.assertIn("proc.exec", text)
        self.assertIn("120", text)
        self.assertIn("80", text)
        self.assertIn("|", text)


def json_cascade(tools: list[str]) -> str:
    return "[" + ", ".join('"%s"' % t for t in tools) + "]"


if __name__ == "__main__":
    unittest.main()
