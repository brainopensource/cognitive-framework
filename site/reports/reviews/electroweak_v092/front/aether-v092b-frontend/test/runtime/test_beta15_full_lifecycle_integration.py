"""BETA-15: full beta technical integration, against an installed distribution.

Owning contract: VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md BETA-15.

The product backend must support, out of a real installed package (not a
source checkout on `PYTHONPATH`):

    install -> configure -> run -> inspect events -> inspect artifacts
    -> interrupt -> restart -> resume -> verify

`test_isolated_installation_smoke.py` (BETA-06/04/05) already proves
install/configure/run/version work from the sdist. This file starts from
that same installed distribution and completes the remaining half of the
chain: inspecting events and artifacts by content digest, a genuine
process-boundary interruption (real `SIGKILL`, not a voluntary stop), and
resuming to a verified terminal state with no effect replayed.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

import setuptools.build_meta as build_meta

ROOT_DIR = Path(__file__).resolve().parents[2]


class TestBeta15FullLifecycleIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp_build = tempfile.mkdtemp(prefix="vg-b15-sdist-build-")
        cls.tmp_install = tempfile.mkdtemp(prefix="vg-b15-sdist-install-")

        prev_cwd = os.getcwd()
        try:
            os.chdir(str(ROOT_DIR))
            cls.sdist_filename = build_meta.build_sdist(cls.tmp_build)
            cls.sdist_path = Path(cls.tmp_build) / cls.sdist_filename
        finally:
            os.chdir(prev_cwd)

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
        self.tmp_ws = tempfile.mkdtemp(prefix="vg-b15-ws-")
        self.workspace = Path(self.tmp_ws)
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
        return subprocess.run(cmd, cwd=str(self.workspace), env=self.env,
                              capture_output=True, text=True, check=check, timeout=60)

    def test_install_configure_run_inspect_interrupt_restart_resume_verify(self) -> None:
        run_id = "run-beta15-full"
        state_dir = self.workspace / ".vanguard"

        # -- install (setUpClass) + configure --------------------------------
        proc_init = self._run_cli(["init"])
        self.assertEqual(proc_init.returncode, 0)
        self.assertTrue(state_dir.is_dir())

        # -- run, interrupted by a real SIGKILL mid-flight -------------------
        # The CLI's `--model-port fake` has no tape-injection flag (single
        # canned "finish" turn only), so the interruptible run is driven
        # directly against the installed package via a worker script -- the
        # same installed `PYTHONPATH`, a real subprocess, a real SIGKILL.
        worker_script = self.workspace / "_worker.py"
        worker_script.write_text(f"""
import os, signal, threading, time
from pathlib import Path
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.app_service import ApplicationService

state_dir = Path({json.dumps(str(state_dir))})
run_id = {json.dumps(run_id)}
events_db = state_dir / "events.sqlite3"

def _watchdog():
    while not events_db.exists():
        time.sleep(0.001)
    store = SqliteEventStore(str(events_db))
    while True:
        res = store.read(EventRange(run_id=run_id))
        if res.ok:
            for ev in res.value:
                if ev.payload.get("kind") == "EffectCompleted":
                    os.kill(os.getpid(), signal.SIGKILL)
                    return
        time.sleep(0.001)

threading.Thread(target=_watchdog, daemon=True).start()

class _Slow(FakeModel):
    def propose(self, *a, **k):
        if self._cursor > 0:
            time.sleep(0.2)
        return super().propose(*a, **k)

model = _Slow([
    {{"kind": "effect", "action": "fs.read",
      "resource": {{"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},
      "args": {{"path": "sample.py"}}, "note": "inspect before the kill"}},
    {{"kind": "finish", "note": "unreachable before the kill"}},
])
app = ApplicationService(workspace=Path({json.dumps(str(self.workspace))}))
app.run(brief="BETA-15 integration probe", profile_id="local", run_id=run_id,
        model=model, state_dir=state_dir, interactive=False, max_turns=6)
print("UNREACHABLE")
""", encoding="utf-8")
        proc_worker = subprocess.run(
            [sys.executable, str(worker_script)], cwd=str(self.workspace),
            env=self.env, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc_worker.returncode, -9,
                         f"expected a real SIGKILL: {proc_worker.stdout} {proc_worker.stderr}")
        self.assertNotIn("UNREACHABLE", proc_worker.stdout)

        # -- inspect events (mid-run, before resume) -------------------------
        proc_events_mid = self._run_cli(["events", run_id, "--json"], check=False)
        self.assertEqual(proc_events_mid.returncode, 0, proc_events_mid.stderr)
        events_mid = json.loads(proc_events_mid.stdout)["events"]
        self.assertTrue(events_mid, "the interrupted run must have left durable events on disk")
        completed_before = [e for e in events_mid if e["payload"].get("kind") == "EffectCompleted"]
        self.assertEqual(len(completed_before), 1, "exactly the one settled effect before the kill")
        artifact_events = [e for e in events_mid if e["payload"].get("kind") == "ArtifactCreated"]
        self.assertTrue(artifact_events, "the settled effect must have captured at least one artifact")

        # -- inspect artifacts by content digest ------------------------------
        digest = artifact_events[0]["payload"].get("digest") or artifact_events[0]["payload"].get("contentDigest")
        self.assertIsNotNone(digest, f"ArtifactCreated event carries no digest field: {artifact_events[0]['payload']}")
        proc_artifact = self._run_cli(["artifacts", digest], check=False)
        self.assertEqual(proc_artifact.returncode, 0, proc_artifact.stderr)
        self.assertIn("verified : True", proc_artifact.stdout)
        self.assertIn(digest, proc_artifact.stdout)

        # -- restart (fresh process) + resume ---------------------------------
        proc_resume = self._run_cli(["resume", run_id, "--profile", "local"], check=False)
        self.assertEqual(proc_resume.returncode, 0, f"resume failed: {proc_resume.stderr}")
        self.assertIn("outcome: completed", proc_resume.stdout)

        # -- verify: no replay, monotonic sequence, terminal state -----------
        proc_events_final = self._run_cli(["events", run_id, "--json"])
        events_final = json.loads(proc_events_final.stdout)["events"]
        seqs = [int(e["seq"]) for e in events_final]
        self.assertEqual(seqs, sorted(seqs))
        self.assertEqual(len(seqs), len(set(seqs)), "no duplicate sequence numbers across the restart")
        completed_after = [e for e in events_final if e["payload"].get("kind") == "EffectCompleted"]
        self.assertEqual(len(completed_after), 1, "the settled effect must not have been replayed on resume")
        terminal = [e for e in events_final if e["payload"].get("kind") == "EpisodeCompleted"]
        self.assertEqual(len(terminal), 1)

        proc_status = self._run_cli(["status", run_id])
        self.assertEqual(proc_status.returncode, 0)
        self.assertIn("status", proc_status.stdout)


if __name__ == "__main__":
    unittest.main()
