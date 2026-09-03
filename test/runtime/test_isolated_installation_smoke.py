"""Hermetic smoke test for clean isolated package installation and CLI execution (Task 2).

Owning contract: BETA-06, BETA-04, BETA-05, REQ-PKG-001.

Invariants:
- Unpacked sdist contains all schemas, manifests, and package metadata.
- CLI executes cleanly out-of-the-box in an isolated environment decoupled from source checkout.
- Commands (version, init, doctor, run, status, events) function correctly from packaged resources.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

import setuptools.build_meta as build_meta

ROOT_DIR = Path(__file__).resolve().parents[2]


class TestIsolatedInstallationSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp_build = tempfile.mkdtemp(prefix="vg-sdist-build-")
        cls.tmp_install = tempfile.mkdtemp(prefix="vg-sdist-install-")

        # Build clean distribution source archive
        prev_cwd = os.getcwd()
        try:
            os.chdir(str(ROOT_DIR))
            cls.sdist_filename = build_meta.build_sdist(cls.tmp_build)
            cls.sdist_path = Path(cls.tmp_build) / cls.sdist_filename
        finally:
            os.chdir(prev_cwd)

        # Unpack archive into isolated location
        with tarfile.open(cls.sdist_path, "r:gz") as tar:
            tar.extractall(path=cls.tmp_install)

        dist_dirname = cls.sdist_filename.replace(".tar.gz", "")
        cls.extracted_pkg_root = Path(cls.tmp_install) / dist_dirname
        cls.env = {
            "PYTHONPATH": str(cls.extracted_pkg_root),
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": cls.tmp_install,
        }

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp_build, ignore_errors=True)
        shutil.rmtree(cls.tmp_install, ignore_errors=True)

    def setUp(self) -> None:
        self.tmp_ws = tempfile.mkdtemp(prefix="vg-isolated-ws-")
        self.workspace = Path(self.tmp_ws)
        # Create minimal target codebase inside workspace
        (self.workspace / "pyproject.toml").write_text(
            '[project]\nname = "user-project"\nversion = "0.1.0"\n', encoding="utf-8"
        )
        (self.workspace / "sample.py").write_text(
            "def calculate(x):\n    return x * 2\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_ws, ignore_errors=True)

    def _run_cli(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, "-m", "vanguard.packages.runtime.cli"] + args
        return subprocess.run(
            cmd,
            cwd=str(self.workspace),
            env=self.env,
            capture_output=True,
            text=True,
            check=check,
        )

    def test_package_archive_completeness(self) -> None:
        """Verify sdist tarball includes required packages, schemas, manifests, and metadata."""
        self.assertTrue(self.sdist_path.exists())
        self.assertIn(self.sdist_filename, ("vanguard-runtime-0.9.0b1.tar.gz", "vanguard_runtime-0.9.0b1.tar.gz"))

        pkg_root = self.extracted_pkg_root
        self.assertTrue((pkg_root / "pyproject.toml").is_file())
        self.assertTrue((pkg_root / "README.md").is_file())
        self.assertTrue((pkg_root / "vanguard").is_dir())
        self.assertTrue((pkg_root / "schemas").is_dir())

        # Check that agency manifests exist in packaged distribution
        manifests_dir = pkg_root / "vanguard" / "packages" / "agency" / "manifests"
        self.assertTrue(manifests_dir.is_dir())
        self.assertTrue((manifests_dir / "vg-code-default" / "manifest.json").is_file())
        self.assertTrue((manifests_dir / "vg-code-lex" / "manifest.json").is_file())
        self.assertTrue((manifests_dir / "vg-code-explain" / "manifest.json").is_file())

    def test_cli_version_reports_release_identity(self) -> None:
        """CLI --version reports authoritative 0.9.0b1 release identity."""
        proc = self._run_cli(["--version"])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("vanguard 0.9.0b1", proc.stdout)

    def test_cli_init_creates_state_contract_and_keys(self) -> None:
        """CLI init initializes workspace state directory and Ed25519 operator key."""
        proc = self._run_cli(["init"])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("workspace", proc.stdout)
        self.assertIn("operator key", proc.stdout)

        state_dir = self.workspace / ".vanguard"
        self.assertTrue(state_dir.is_dir())
        self.assertTrue((state_dir / "blobs").is_dir())

    def test_cli_doctor_runs_truthful_diagnostics(self) -> None:
        """CLI doctor runs and reports diagnostics from installed distribution."""
        # Non-zero exit code is normal when external live keys (e.g. OpenRouter) are unset (fail-closed)
        proc = self._run_cli(["doctor", "--profile", "local"], check=False)
        self.assertIn("Vanguard 0.9.0b1", proc.stdout)
        self.assertIn("workspace", proc.stdout)
        self.assertIn("model_provider:fake", proc.stdout)
        self.assertIn("model_provider:cassette", proc.stdout)
        self.assertIn("READINESS: READY", proc.stdout.upper())

    def test_cli_run_execute_and_query_lifecycle(self) -> None:
        """CLI run executes task out-of-the-box, persisting durable state queryable via status and events."""
        run_id = "run-isolated-test-01"
        proc_run = self._run_cli([
            "run",
            "Inspect sample.py and complete analysis",
            "--profile", "local",
            "--model-port", "fake",
            "--run-id", run_id,
            "--non-interactive",
        ])
        self.assertEqual(proc_run.returncode, 0, f"run failed: {proc_run.stderr}")
        self.assertIn("run_id : run-isolated-test-01", proc_run.stdout)
        self.assertIn("outcome: completed", proc_run.stdout)
        self.assertIn("turns  : 1", proc_run.stdout)

        # Query status
        proc_status = self._run_cli(["status", run_id])
        self.assertEqual(proc_status.returncode, 0)
        self.assertIn("run_id     : run-isolated-test-01", proc_status.stdout)
        self.assertIn("status     : completed", proc_status.stdout)
        self.assertIn("event_count: ", proc_status.stdout)

        # Query events in JSON format
        proc_events = self._run_cli(["events", run_id, "--json"])
        self.assertEqual(proc_events.returncode, 0)
        events_data = json.loads(proc_events.stdout)
        reported_run_id = events_data.get("runId") or events_data.get("run_id")
        self.assertEqual(reported_run_id, run_id)
        self.assertGreater(len(events_data["events"]), 0)

        # Verify strict causal sequence ordering as numeric integers
        seqs = [int(evt.get("seq", 0)) for evt in events_data["events"]]
        self.assertEqual(seqs, sorted(seqs))
        self.assertEqual(len(seqs), len(set(seqs)), "Sequence numbers must be strictly unique")


if __name__ == "__main__":
    unittest.main()
