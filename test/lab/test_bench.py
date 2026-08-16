"""Paired McNemar bench and vg-shell-only control arm."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "vanguard" / "packages" / "agency" / "manifests"


def load_lab(name: str):
    path = ROOT / "lab" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lab_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def seed_pair(db: Path, rows: list[tuple[str, str, int, int, str]]) -> None:
    """rows: scenario_id, harness, passed, tokens, cascade_json."""
    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS traces (
                trace_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id TEXT NOT NULL,
                backend TEXT NOT NULL,
                model TEXT NOT NULL,
                passed INTEGER NOT NULL,
                llm_calls INTEGER NOT NULL DEFAULT 1,
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
        for scenario_id, harness, passed, tokens, cascade in rows:
            conn.execute(
                """
                INSERT INTO traces (
                    scenario_id, backend, model, passed, prompt_tokens, harness, cascade
                ) VALUES (?, 'lam', ?, ?, ?, ?, ?)
                """,
                (scenario_id, harness, passed, tokens, harness, cascade),
            )
        conn.commit()


class ShellOnlyControl(unittest.TestCase):
    def test_vg_shell_only_is_undeletable_single_proc_exec(self) -> None:
        manifest = json.loads((MANIFESTS / "vg-shell-only" / "manifest.json").read_text())
        aliases = json.loads((MANIFESTS / "vg-shell-only" / "aliases.json").read_text())
        self.assertTrue(manifest["undeletable"])
        verbs = {cap["verb"] for cap in manifest["capabilities"]}
        self.assertEqual(verbs, {"proc.exec"})
        self.assertEqual(set(aliases["aliases"].values()), {"proc.exec"})
        self.assertTrue(aliases["passthrough"])


class McNemarBench(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "lam.sqlite"
        self.bench = load_lab("bench")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_contingency_and_chi_square_on_discordant_pairs(self) -> None:
        # 2 both-pass, 8 A-pass-B-fail (b), 0 A-fail-B-pass (c) → exact p < 0.05
        rows: list[tuple[str, str, int, int, str]] = [
            ("s1", "vg-code-default", 1, 100, '["fs.read"]'),
            ("s1", "vg-code-claude-shaped", 1, 120, '["Read"]'),
            ("s2", "vg-code-default", 1, 100, "[]"),
            ("s2", "vg-code-claude-shaped", 1, 80, "[]"),
        ]
        for i in range(3, 11):
            sid = f"s{i}"
            rows.append((sid, "vg-code-default", 1, 50, "[]"))
            rows.append((sid, "vg-code-claude-shaped", 0, 50, "[]"))
        seed_pair(self.db, rows)
        result = self.bench.compare_packs(
            self.db, "vg-code-default", "vg-code-claude-shaped"
        )
        self.assertEqual(result["b"], 8)
        self.assertEqual(result["c"], 0)
        self.assertAlmostEqual(result["chi2"], (8 - 0) ** 2 / 8)
        self.assertLess(result["p_value"], 0.05)
        self.assertAlmostEqual(result["pass_rate_a"], 10 / 10)
        self.assertAlmostEqual(result["pass_rate_b"], 2 / 10)

    def test_degenerate_aa_floor_is_refused(self) -> None:
        seed_pair(
            self.db,
            [
                ("s1", "vg-shell-only", 1, 10, "[]"),
                ("s1", "vg-shell-only-copy", 1, 10, "[]"),
                ("s2", "vg-shell-only", 1, 10, "[]"),
                ("s2", "vg-shell-only-copy", 1, 10, "[]"),
            ],
        )
        result = self.bench.compare_packs(self.db, "vg-shell-only", "vg-shell-only-copy")
        self.assertTrue(result["refused"])
        self.assertEqual(result["b"], 0)
        self.assertEqual(result["c"], 0)


if __name__ == "__main__":
    unittest.main()
