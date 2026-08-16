"""EpisodeCoordinator: one recursive coordinator, emergent depth in lam.sqlite."""

from __future__ import annotations

import ast
import sqlite3
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.coordination import (
    DEPTH_LABELS,
    BudgetExceeded,
    EpisodeCoordinator,
)


RUNTIME = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "runtime"


class NoClassBloat(unittest.TestCase):
    def test_coordination_defines_no_cell_or_organism_classes(self) -> None:
        source = (RUNTIME / "coordination.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
        self.assertNotIn("Cell", names)
        self.assertNotIn("Organism", names)
        self.assertNotIn("Molecule", names)
        self.assertNotIn("Polymer", names)
        self.assertNotIn("Body", names)
        self.assertIn("EpisodeCoordinator", names)


class DepthAndBudget(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "lam.sqlite"
        self.coord = EpisodeCoordinator(self.db)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_root_episode_is_atom_at_depth_zero(self) -> None:
        ep = self.coord.open_episode(task_id="fix-parser", budget_tokens=1000)
        self.assertEqual(ep["depth"], 0)
        self.assertEqual(ep["depth_label"], "Atom")
        self.assertEqual(ep["budget_tokens"], 1000)
        self.assertIsNone(ep["parent_id"])

    def test_spawned_depths_carry_emergent_labels(self) -> None:
        root = self.coord.open_episode(task_id="root", budget_tokens=800)
        molecule = self.coord.spawn(root["episode_id"], task_id="file-fix", requested_tokens=400)
        polymer = self.coord.spawn(molecule["episode_id"], task_id="refactor", requested_tokens=200)
        cell = self.coord.spawn(polymer["episode_id"], task_id="repair", requested_tokens=100)
        body = self.coord.spawn(cell["episode_id"], task_id="swarm", requested_tokens=50)
        self.assertEqual(molecule["depth_label"], "Molecule")
        self.assertEqual(polymer["depth_label"], "Polymer")
        self.assertEqual(cell["depth_label"], "Cell")
        self.assertEqual(body["depth_label"], "Body")
        self.assertEqual(body["depth"], 4)
        self.assertEqual(DEPTH_LABELS[0], "Atom")

    def test_child_budget_cannot_exceed_parent_remaining(self) -> None:
        root = self.coord.open_episode(task_id="root", budget_tokens=100)
        child = self.coord.spawn(root["episode_id"], task_id="child", requested_tokens=999)
        self.assertEqual(child["budget_tokens"], 100)
        parent = self.coord.get_episode(root["episode_id"])
        self.assertEqual(parent["remaining_tokens"], 0)

    def test_spawn_after_consume_uses_remaining_not_original(self) -> None:
        root = self.coord.open_episode(task_id="root", budget_tokens=100)
        self.coord.consume(root["episode_id"], 40)
        child = self.coord.spawn(root["episode_id"], task_id="child", requested_tokens=80)
        self.assertEqual(child["budget_tokens"], 60)
        parent = self.coord.get_episode(root["episode_id"])
        self.assertEqual(parent["remaining_tokens"], 0)
        self.assertEqual(parent["tokens_used"], 40)

    def test_consume_beyond_remaining_raises(self) -> None:
        root = self.coord.open_episode(task_id="root", budget_tokens=10)
        with self.assertRaises(BudgetExceeded):
            self.coord.consume(root["episode_id"], 11)

    def test_episode_row_is_written_to_lam_sqlite(self) -> None:
        ep = self.coord.open_episode(task_id="task-9", budget_tokens=50)
        self.coord.consume(ep["episode_id"], 12)
        with sqlite3.connect(self.db) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT task_id, parent_id, depth, depth_label, tokens_used FROM episodes WHERE episode_id = ?",
                (ep["episode_id"],),
            ).fetchone()
        self.assertEqual(row["task_id"], "task-9")
        self.assertIsNone(row["parent_id"])
        self.assertEqual(row["depth"], 0)
        self.assertEqual(row["depth_label"], "Atom")
        self.assertEqual(row["tokens_used"], 12)

    def test_execute_harness_writes_episode_depth_row(self) -> None:
        import os
        import subprocess
        from vanguard.packages.runtime.root import Runtime, TaskContext
        from test.integration.test_reconstruction_packs import (
            build_repo,
            unified_diff,
            SuiteVerifier,
            PackScriptedOperator,
            sign_challenge,
            OPERATOR_KEY,
        )

        repo = build_repo()
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(repo)], check=False))
        diff = unified_diff(repo)
        verifier = SuiteVerifier(repo)
        resource = {"kind": "fs", "root": str(repo), "paths": [str(repo)]}
        script = [
            {"kind": "effect", "action": "fs.read", "resource": resource, "args": {"path": "calc.py"}},
            {"kind": "effect", "action": "patch.apply", "resource": resource, "args": {"diff": diff}},
            {"kind": "finish", "note": "done"},
        ]
        operator = PackScriptedOperator(script)
        task = TaskContext(
            brief="Fix bug",
            repo_path=repo,
            run_id="run-coord-1",
            episode_id="ep-coord-1",
            principal="agent-1",
            competence_prior=0.5,
        )

        old_db = os.environ.get("VANGUARD_LAM_DB")
        try:
            os.environ["VANGUARD_LAM_DB"] = str(self.db)
            res = Runtime.execute_harness(
                manifest_path="vg-code-default",
                task_context=task,
                model=operator,
                approver=sign_challenge,
                approval_key=OPERATOR_KEY,
                verifier=verifier,
            )
            ep = self.coord.get_episode("ep-coord-1")
            self.assertEqual(ep["depth"], 0)
            self.assertEqual(ep["depth_label"], "Atom")
            self.assertGreater(ep["tokens_used"], 0)
        finally:
            if old_db is not None:
                os.environ["VANGUARD_LAM_DB"] = old_db
            else:
                os.environ.pop("VANGUARD_LAM_DB", None)


if __name__ == "__main__":
    unittest.main()
