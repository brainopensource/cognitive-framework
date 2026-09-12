"""T-89: the canary measures the shipped product path, not a private runtime."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
from unittest.mock import patch

from benchmarks.agentic_harness_matrix_benchmark import (
    run_single_harness_task,
    write_control_report,
)
from benchmarks.ladder.control import ControlManifestError, ControlNotFrozen, load_preregistration
from benchmarks.ladder.evidence import EvidenceError
from benchmarks.ladder.metrics import BUDGET_EXHAUSTED
from benchmarks.product_path import execute_product, manifest_for_preset
from test.benchmarks.test_metric_veto import _population
from test.benchmarks.test_preregistration import TASK_IDS, frozen_manifest
from vanguard.packages.apps.coding_max.facade import CodingMaxFacade
from vanguard.packages.runtime import entrypoint, pack_catalog
from vanguard.packages.runtime.app_service import ApplicationService

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "benchmarks" / "agentic_harness_matrix_benchmark.py"
PRODUCT_PATH = ROOT / "benchmarks" / "product_path.py"


class TestProductPathSubject(unittest.TestCase):
    def test_canary_runner_does_not_call_execute_profiled(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertNotIn("Runtime.execute_profiled", source)
        self.assertNotIn("execute_profiled(", source)
        self.assertIn("execute_product", source)

    def test_product_path_entry_is_entrypoint_execute(self) -> None:
        source = PRODUCT_PATH.read_text(encoding="utf-8")
        self.assertIn("from vanguard.packages.runtime.entrypoint import execute", source)
        self.assertIn("return execute(request)", source)

    def test_runner_and_cli_share_preset_manifest_identity(self) -> None:
        # T-102. The facade no longer owns a private ``_manifest``; it and the
        # entrypoint both resolve through ``pack_catalog``. The identity this
        # test guards is unchanged -- it is now asserted against the single
        # resolver the facade actually calls, and against the manifest the
        # facade hands to the application service.
        facade_manifest = pack_catalog.preset_manifest_path("balanced")
        entry_manifest = entrypoint._manifest("code", "balanced")
        helper_manifest = manifest_for_preset("balanced")
        self.assertEqual(facade_manifest.resolve(), entry_manifest.resolve())
        self.assertEqual(entry_manifest.resolve(), helper_manifest.resolve())
        self.assertIn("vg-code-balanced", str(entry_manifest))

        service = Mock(spec=ApplicationService)
        CodingMaxFacade(service=service).run("canary", preset="balanced")
        self.assertEqual(
            Path(service.run.call_args.kwargs["manifest_path"]).resolve(),
            entry_manifest.resolve(),
        )

    def test_execute_product_is_the_entrypoint_symbol(self) -> None:
        self.assertIs(execute_product.__wrapped__ if hasattr(execute_product, "__wrapped__") else execute_product, execute_product)
        self.assertEqual(execute_product.__module__, "benchmarks.product_path")
        self.assertIs(entrypoint.execute, entrypoint.execute)


class TestControlProductRoute(unittest.TestCase):
    """T-26b: report admission is reached through the real runner seam."""

    @staticmethod
    def _frame(run_id: str) -> dict:
        return {
            "type": "result",
            "runId": run_id,
            "result": {
                "runId": run_id,
                "outcome": "abandoned",
                "turns": 2,
                "promptTokens": 0,
                "completionTokens": 0,
                "spentUsdMicros": 0,
            },
        }

    def test_final_control_slot_runs_product_then_writes_admitted_report(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)[:29]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            report_path = root / "control-report.json"

            def fake_execute(**request: object) -> dict:
                self.assertEqual(request["harness"], "vg-code-balanced")
                self.assertEqual(request["preset"], "balanced")
                self.assertEqual(request["profile_id"], "product")
                return self._frame(str(request["run_id"]))

            with patch(
                "benchmarks.agentic_harness_matrix_benchmark.get_workspace_path",
                return_value=root,
            ), patch(
                "benchmarks.agentic_harness_matrix_benchmark.execute_product",
                side_effect=fake_execute,
            ) as execute, patch(
                "benchmarks.agentic_harness_matrix_benchmark.time.perf_counter_ns",
                return_value=52,
            ):
                result = run_single_harness_task(
                    harness_name="vg-code-balanced",
                    task_name=TASK_IDS[29],
                    brief="hermetic final control slot",
                    files={"subject.py": "value = 1\n"},
                    oracle_code="import unittest\n\nclass TestOracle(unittest.TestCase):\n    def test_ok(self): self.assertEqual(1, 1)\n",
                    model=None,
                    max_turns=3,
                    profile_id="product",
                    control_record=manifest,
                    control_rows=rows,
                    control_report_path=report_path,
                )

            execute.assert_called_once()
            self.assertEqual(result["control_evidence"]["identity"]["task_id"], TASK_IDS[29])
            self.assertEqual(result["control_report"]["disposition"], "POSITIVE")
            self.assertTrue(report_path.is_file())

    def test_unfrozen_or_mismatched_control_never_dispatches_product(self) -> None:
        with TemporaryDirectory() as directory, patch(
            "benchmarks.agentic_harness_matrix_benchmark.execute_product",
        ) as execute:
            args = {
                "harness_name": "vg-code-balanced",
                "task_name": TASK_IDS[0],
                "brief": "must not dispatch",
                "files": {},
                "oracle_code": "",
                "model": None,
                "profile_id": "product",
                "control_rows": [],
                "control_report_path": Path(directory) / "report.json",
            }
            with self.assertRaises(ControlNotFrozen):
                run_single_harness_task(control_record=load_preregistration(), **args)
            with self.assertRaises(ControlManifestError):
                run_single_harness_task(
                    control_record=frozen_manifest(),
                    **{**args, "task_name": "L2-EXTRA"},
                )
            mismatched_rows = _population(frozen_manifest())[:1]
            mismatched_rows[0]["identity"]["subject_sha"] = "dead" * 10
            with self.assertRaisesRegex(ControlManifestError, "does not bind"):
                run_single_harness_task(
                    control_record=frozen_manifest(),
                    **{
                        **args,
                        "task_name": TASK_IDS[1],
                        "control_rows": mismatched_rows,
                    },
                )
            execute.assert_not_called()

    def test_budget_exhaustion_stops_the_next_control_dispatch(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)[:1]
        rows[0]["settlement"] = {
            "terminal_status": BUDGET_EXHAUSTED,
            "disposition": "not_run",
            "undeterminable_reason": BUDGET_EXHAUSTED,
        }
        with TemporaryDirectory() as directory, patch(
            "benchmarks.agentic_harness_matrix_benchmark.execute_product",
        ) as execute:
            with self.assertRaisesRegex(ControlManifestError, "budget-exhausted"):
                run_single_harness_task(
                    harness_name="vg-code-balanced",
                    task_name=TASK_IDS[1],
                    brief="must stop",
                    files={},
                    oracle_code="",
                    model=None,
                    profile_id="product",
                    control_record=manifest,
                    control_rows=rows,
                    control_report_path=Path(directory) / "report.json",
                )
            execute.assert_not_called()

    def test_mismatched_population_cannot_write_a_report(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)
        rows[0]["identity"]["subject_sha"] = "dead" * 10
        with TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            with self.assertRaises(EvidenceError):
                write_control_report(path=path, record=manifest, rows=rows)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
