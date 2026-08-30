from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.app_service import ApplicationService
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.blob_store import FileBlobStore


class TestAppServiceAndCli(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp_dir.name).resolve()
        (self.workspace / "pyproject.toml").touch()
        self.state_dir = self.workspace / ".vanguard"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        (self.state_dir / "blobs").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_app_service_doctor(self) -> None:
        app = ApplicationService(workspace=self.workspace)
        report = app.doctor()
        self.assertIn(report.health, ("healthy", "degraded"))
        self.assertEqual(report.version, "0.9.0b1")
        self.assertTrue(len(report.checks) > 0)

    def test_app_service_run_and_status_and_events(self) -> None:
        app = ApplicationService(workspace=self.workspace)
        fake_model = FakeModel([{"kind": "finish", "note": "smoke test completed"}])

        run_res = app.run(
            brief="test smoke brief",
            profile_id="product",
            model=fake_model,
            run_id="run-test-1",
            state_dir=self.state_dir,
        )
        self.assertEqual(run_res.run_id, "run-test-1")
        self.assertEqual(run_res.outcome, "completed")

        status_res = app.status("run-test-1", state_dir=self.state_dir)
        self.assertEqual(status_res.run_id, "run-test-1")
        self.assertTrue(status_res.event_count > 0)
        self.assertTrue(status_res.as_of_seq > 0)

        events_res = app.events("run-test-1", state_dir=self.state_dir)
        self.assertEqual(events_res.run_id, "run-test-1")
        self.assertEqual(events_res.total, status_res.event_count)
        self.assertTrue(len(events_res.events) > 0)

    def test_artifact_retrieval_and_digest_verification(self) -> None:
        app = ApplicationService(workspace=self.workspace)
        blobs = FileBlobStore(self.state_dir / "blobs")

        content = b"hello aether artifact"
        digest_res = blobs.put(content)
        digest = digest_res.value

        # Retrieve valid artifact
        res = app.artifact(digest=digest, state_dir=self.state_dir)
        self.assertTrue(res.verified)
        self.assertEqual(res.content, content)

        # Retrieve non-existent artifact
        missing_res = app.artifact(digest="sha256:" + "f" * 64, state_dir=self.state_dir)
        self.assertFalse(missing_res.verified)
        self.assertIsNone(missing_res.content)

        # Digest mismatch test
        bad_digest = "sha256:" + hashlib.sha256(b"different content").hexdigest()
        # Put content under bad_digest filename to simulate corruption
        bad_path = blobs._path(bad_digest)
        bad_path.parent.mkdir(parents=True, exist_ok=True)
        bad_path.write_bytes(b"tampered content")

        corrupt_res = app.artifact(digest=bad_digest, state_dir=self.state_dir)
        self.assertFalse(corrupt_res.verified)
        self.assertIn("mismatch", corrupt_res.error or "")

    def test_cli_subcommands_execution(self) -> None:
        # CLI doctor
        res_doc = subprocess.run(
            [sys.executable, "-m", "vanguard.packages.runtime.cli", "doctor", "-w", str(self.workspace)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertIn("Vanguard 0.9.0b1", res_doc.stdout + res_doc.stderr)

        # CLI run with fake model
        res_run = subprocess.run(
            [
                sys.executable,
                "-m",
                "vanguard.packages.runtime.cli",
                "run",
                "smoke task",
                "-w",
                str(self.workspace),
                "--profile",
                "local",
                "--model-port",
                "fake",
                "--run-id",
                "cli-run-1",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_run.returncode, 0)
        self.assertIn("outcome: completed", res_run.stdout)

        # CLI status
        res_status = subprocess.run(
            [sys.executable, "-m", "vanguard.packages.runtime.cli", "status", "cli-run-1", "-w", str(self.workspace)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_status.returncode, 0)
        self.assertIn("run_id     : cli-run-1", res_status.stdout)

        # CLI events
        res_events = subprocess.run(
            [sys.executable, "-m", "vanguard.packages.runtime.cli", "events", "cli-run-1", "-w", str(self.workspace), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_events.returncode, 0)
        events_json = json.loads(res_events.stdout)
        self.assertEqual(events_json["runId"], "cli-run-1")
