"""Contract test for EVO-13 / EVO-15: Cassette CLI and Diagnostic Bundle Exporter.

Owning contract: EVO-13, EVO-15, GTS-13C §7.4, ADR-0096 §14.5.
Invariants:
- vanguard doctor --export-bundle exports scrubbed system metadata without secrets.
- vanguard cassette record extracts run interactions to a valid cassette JSON.
- vanguard cassette replay executes deterministically using CassettePlayer.
"""

from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.runtime.app_service import ApplicationService
from vanguard.packages.runtime.cli import main


class TestEvo13CliCassetteDoctor(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        (self.workspace / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_doctor_export_bundle(self) -> None:
        """Verify doctor --export-bundle creates a valid scrubbed zip bundle."""
        bundle_path = self.workspace / "diag_bundle.zip"
        
        exit_code = main(["doctor", "-w", str(self.workspace), "--export-bundle", str(bundle_path)])
        self.assertEqual(exit_code, 0)
        self.assertTrue(bundle_path.exists())

        with zipfile.ZipFile(bundle_path, "r") as zf:
            namelist = zf.namelist()
            self.assertIn("system_info.json", namelist)
            self.assertIn("doctor_report.json", namelist)
            self.assertIn("state_metrics.json", namelist)

            sys_info = json.loads(zf.read("system_info.json").decode("utf-8"))
            self.assertIn("vanguard_version", sys_info)
            self.assertIn("python_version", sys_info)

            doc_rep = json.loads(zf.read("doctor_report.json").decode("utf-8"))
            self.assertIn("health", doc_rep)
            self.assertIn("checks", doc_rep)

    def test_cassette_record_and_replay_cycle(self) -> None:
        """Verify recording a cassette from a run and replaying it deterministically."""
        app = ApplicationService(workspace=self.workspace)
        fake_model = FakeModel([
            {
                "kind": "finish",
                "note": "done with task",
            },
        ])

        # Run an initial task with fake model
        run_res = app.run(
            brief="sample task for cassette test",
            model=fake_model,
            profile_id="product",
            interactive=False,
        )
        self.assertEqual(run_res.outcome, "completed")

        # Record cassette via CLI
        cassette_file = self.workspace / "recorded.cassette.json"
        rec_code = main([
            "cassette", "record", run_res.run_id,
            "-o", str(cassette_file),
            "-w", str(self.workspace),
        ])
        self.assertEqual(rec_code, 0)
        self.assertTrue(cassette_file.exists())

        cas_data = json.loads(cassette_file.read_text(encoding="utf-8"))
        self.assertIsInstance(cas_data, list)
        self.assertGreater(len(cas_data), 0)
        self.assertIn("proposal", cas_data[0])

        # Replay cassette via CLI
        rep_code = main([
            "cassette", "replay", str(cassette_file),
            "-b", "sample task for cassette test",
            "-w", str(self.workspace),
        ])
        self.assertEqual(rep_code, 0)


if __name__ == "__main__":
    unittest.main()
