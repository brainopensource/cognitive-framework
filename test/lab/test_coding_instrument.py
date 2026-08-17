"""Coding instrument, LAM denominator, LAR offline, anti-cheat (GAMMA / REQ-TRUST-001)."""

from __future__ import annotations

import ast
import io
import tempfile
import unittest
from pathlib import Path

from tools.telemetry.aa_runner import AARunner
from tools.telemetry.coding_instrument import (
    CODING_FAMILY,
    PREREGISTERED_TASKS,
    WORKER_HIDDEN_NAMES,
    instrument_tuple,
    is_hidden_from_worker,
    mock_must_not_wear_live_label,
)
from tools.telemetry.coding_lam import default_workspace_map, run_coding_lam
from tools.telemetry.coding_lar import hypotheses_from_sessions, write_review_artifact

ROOT = Path(__file__).resolve().parents[2]
LAM_SRC = (ROOT / "tools" / "telemetry" / "coding_lam.py").read_text(encoding="utf-8")
LAR_SRC = (ROOT / "tools" / "telemetry" / "coding_lar.py").read_text(encoding="utf-8")
LAB_RUN = (ROOT / "lab" / "run.py").read_text(encoding="utf-8")


class TestCodingInstrumentTuple(unittest.TestCase):
    def test_family_and_split_are_preregistered(self) -> None:
        tup = instrument_tuple(arm="mock")
        self.assertEqual(tup["family"], CODING_FAMILY)
        self.assertEqual(tup["split"], list(PREREGISTERED_TASKS))
        self.assertIsNone(tup["contaminationLedger"])
        self.assertEqual(len(PREREGISTERED_TASKS), 4)

    def test_unknown_arm_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            instrument_tuple(arm="anthropic-paid")


class TestLamDenominator(unittest.TestCase):
    def test_all_missing_stay_in_denominator(self) -> None:
        report = run_coding_lam({task: None for task in PREREGISTERED_TASKS}, arm="mock")
        self.assertEqual(report["passRateDenominator"], 4)
        self.assertEqual(report["workspaceMissingCount"], 4)
        self.assertEqual(report["oracleGreenCount"], 0)
        self.assertFalse(report["q2"])
        self.assertIsNone(report["publishedLift"])
        self.assertTrue(all(row["inDenominator"] for row in report["tasks"]))
        self.assertTrue(all(
            row["termination"] == "inconclusive:workspace_missing" for row in report["tasks"]
        ))

    def test_present_dir_without_session_is_not_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            workspaces = {task: None for task in PREREGISTERED_TASKS}
            workspaces["DOGFOOD-01"] = path
            report = run_coding_lam(workspaces, arm="mock")
        self.assertEqual(report["passRateDenominator"], 4)
        by_id = {row["taskId"]: row for row in report["tasks"]}
        self.assertEqual(by_id["DOGFOOD-01"]["termination"], "inconclusive:driver_not_bound")
        self.assertTrue(by_id["DOGFOOD-01"]["inDenominator"])
        self.assertFalse(by_id["DOGFOOD-01"]["oracle_green"])
        self.assertEqual(by_id["DOGFOOD-02"]["termination"], "inconclusive:workspace_missing")

    def test_session_can_mark_oracle_green_without_shrinking_denominator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            sessions = {
                "DOGFOOD-01": {
                    "schema": "vg.coding-session.v1",
                    "termination": "oracle_green",
                    "turnCount": 3,
                    "verbs": ["fs.read", "patch.apply"],
                    "denialCount": 0,
                    "compactCount": 1,
                    "deadEnds": [],
                    "oracle_green": True,
                    "cacheMissAttribution": "turn:2",
                }
            }
            workspaces = {task: (path if task == "DOGFOOD-01" else None) for task in PREREGISTERED_TASKS}
            report = run_coding_lam(workspaces, sessions=sessions, arm="mock")
        self.assertEqual(report["passRateDenominator"], 4)
        self.assertEqual(report["passRateNumerator"], 1)

    def test_default_map_resolves_beta_kebab_dirs(self) -> None:
        mapping = default_workspace_map(ROOT)
        self.assertEqual(set(mapping), set(PREREGISTERED_TASKS))
        missing = [task_id for task_id, path in mapping.items() if path is None]
        self.assertEqual(missing, [], f"declared dirs missing: {missing}")

    def test_lab_run_shim_computes_nothing(self) -> None:
        self.assertIn("vanguard.packages.runtime.lab_driver", LAB_RUN)
        self.assertNotIn("HarnessSession", LAB_RUN)
        self.assertIn("cannot claim an outcome", LAB_RUN)
        self.assertIn("subprocess.run", LAB_RUN)

    def test_mock_cannot_wear_live_label(self) -> None:
        with self.assertRaises(ValueError):
            run_coding_lam({}, arm="ollama:deepseek-r1", model_port="mock")
        self.assertTrue(mock_must_not_wear_live_label("mock", "mock"))
        self.assertFalse(mock_must_not_wear_live_label("mock", "openrouter-free"))


class TestAntiCheat(unittest.TestCase):
    def test_reference_and_gold_hidden_from_worker(self) -> None:
        for name in WORKER_HIDDEN_NAMES:
            self.assertTrue(is_hidden_from_worker(name), name)
        self.assertFalse(is_hidden_from_worker("src/app.py"))

    def test_lam_source_has_no_host_pytest_oracle(self) -> None:
        tree = ast.parse(LAM_SRC)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if "pytest" in node.value and "proc.exec" not in node.value:
                    self.fail("coding_lam must not embed a host pytest oracle")
        self.assertNotIn("subprocess", LAM_SRC)
        self.assertNotIn("sqlite3", LAM_SRC)

    def test_no_llm_judge_in_lam_or_lar(self) -> None:
        blob = LAM_SRC + LAR_SRC
        for needle in ("llm_judge", "grade_self", "as_judge", "LLM-as-judge"):
            self.assertNotIn(needle, blob)

    def test_lar_refuses_to_write_pack_genes(self) -> None:
        dest = ROOT / "vanguard" / "packages" / "agency" / "manifests" / "vg-code-default" / "system-prompt.txt"
        with self.assertRaises(ValueError):
            write_review_artifact([], dest)

    def test_lar_writes_docs_review_only(self) -> None:
        hyps = hypotheses_from_sessions([
            {"termination": "inconclusive:workspace_missing", "turnCount": 0, "denialCount": 0}
        ])
        self.assertTrue(hyps)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "evidence" / "lar.md"
            write_review_artifact(hyps, dest)
            text = dest.read_text(encoding="utf-8")
        self.assertIn("Not applied", text)

    def test_sealed_spawn_still_green(self) -> None:
        from test.agency.test_episode_spawn import NarrowedChildCannotEscalate

        suite = unittest.defaultTestLoader.loadTestsFromTestCase(NarrowedChildCannotEscalate)
        result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        self.assertTrue(result.wasSuccessful(), result.failures + result.errors)


class TestCodingAAArm(unittest.TestCase):
    def test_coding_manifest_aa_refuses_degenerate_and_replay(self) -> None:
        replay = AARunner(manifest="vg-code-default", is_replay=True)
        res = replay.run_calibration(
            task_classes=["DOGFOOD-01", "DOGFOOD-02", "DOGFOOD-03"],
            arm1_evaluator=lambda t, i: {"passed": True},
            arm2_evaluator=lambda t, i: {"passed": True},
            n_repeats=4,
        )
        self.assertTrue(res.refused)
        zero = AARunner(manifest="vg-code-default", is_replay=False)
        res2 = zero.run_calibration(
            task_classes=["DOGFOOD-01", "DOGFOOD-02", "DOGFOOD-03"],
            arm1_evaluator=lambda t, i: {"passed": False},
            arm2_evaluator=lambda t, i: {"passed": False},
            n_repeats=4,
        )
        self.assertTrue(res2.refused)
        self.assertIn("degenerate", res2.reason.lower())


if __name__ == "__main__":
    unittest.main()
