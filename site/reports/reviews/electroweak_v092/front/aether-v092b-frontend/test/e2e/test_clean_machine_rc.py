"""AETHER — Clean-Machine End-to-End Acceptance Test.

Verifies that the packaged Release Candidate (v0.9.1-rc1) can be installed
and used on a clean machine with zero source repository access, zero
development environment variables, and zero pre-existing configuration.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


class TestCleanMachineReleaseCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parent.parent.parent
        cls.dist_dir = cls.repo_root / "dist" / "aether-0.9.1-rc1"
        if not cls.dist_dir.exists():
            from tools.packaging.build_rc import build_rc

            build_rc()

    def setUp(self) -> None:
        # Create an isolated clean-machine environment
        self.test_dir = tempfile.mkdtemp(prefix="aether-clean-machine-")
        self.clean_home = Path(self.test_dir) / "home" / "testuser"
        self.install_prefix = Path(self.test_dir) / "opt" / "aether-install"
        self.clean_home.mkdir(parents=True, exist_ok=True)
        self.install_prefix.mkdir(parents=True, exist_ok=True)

        # Isolated clean environment variables
        self.clean_env = {
            "HOME": str(self.clean_home),
            "PATH": f"{self.install_prefix}/bin:{os.environ.get('PATH', '/usr/bin:/bin')}",
            "XDG_CONFIG_HOME": str(self.clean_home / ".config"),
            "XDG_DATA_HOME": str(self.clean_home / ".local" / "share"),
            "XDG_STATE_HOME": str(self.clean_home / ".local" / "state"),
            "AETHER_RUNTIME_SOCK": str(self.clean_home / ".local" / "state" / "runtime.sock"),
            "NODE_ENV": "production",
        }

    def tearDown(self) -> None:
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def run_cmd(self, cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd,
            cwd=cwd or self.clean_home,
            env=self.clean_env,
            capture_output=True,
            text=True,
        )

    def test_01_clean_installation(self) -> None:
        """Step 1: Install from packaged Release Candidate into clean prefix."""
        install_script = self.dist_dir / "install.sh"
        self.assertTrue(install_script.exists())

        res = self.run_cmd(["bash", str(install_script), str(self.install_prefix)])
        self.assertEqual(res.returncode, 0, f"Install failed: {res.stderr}\n{res.stdout}")

        # Check installed binaries and symlinks
        installed_cli = self.install_prefix / "bin" / "aether"
        installed_tui = self.install_prefix / "bin" / "aether-tui"
        self.assertTrue(installed_cli.exists())
        self.assertTrue(installed_tui.exists())

        # Check .desktop entry
        desktop_entry = self.install_prefix / "share" / "applications" / "aether.desktop"
        self.assertTrue(desktop_entry.exists())

    def test_02_first_run_diagnostics_and_catalogs(self) -> None:
        """Step 2: Run CLI commands on clean machine without daemon running."""
        self.run_cmd(["bash", str(self.dist_dir / "install.sh"), str(self.install_prefix)])

        # aether doctor (fails closed cleanly with daemon offline)
        res_doc = self.run_cmd(["aether", "doctor", "--json"])
        self.assertEqual(res_doc.returncode, 6)  # DAEMON_UNAVAILABLE = 6
        data_doc = json.loads(res_doc.stdout)
        self.assertEqual(data_doc["status"], "error")
        self.assertFalse(data_doc["data"]["healthy"])

        # aether provider list
        res_prov = self.run_cmd(["aether", "provider", "list", "--json"])
        self.assertEqual(res_prov.returncode, 0)
        data_prov = json.loads(res_prov.stdout)
        self.assertEqual(data_prov["status"], "success")
        self.assertTrue(len(data_prov["data"]["providers"]) > 0)

        # aether agent list
        res_agent = self.run_cmd(["aether", "agent", "list", "--json"])
        self.assertEqual(res_agent.returncode, 0)
        data_agent = json.loads(res_agent.stdout)
        self.assertEqual(data_agent["status"], "success")
        self.assertTrue(any(a["id"] == "coding-agent" for a in data_agent["data"]["agents"]))

        # aether workflow list
        res_wf = self.run_cmd(["aether", "workflow", "list", "--json"])
        self.assertEqual(res_wf.returncode, 0)
        data_wf = json.loads(res_wf.stdout)
        self.assertEqual(data_wf["status"], "success")
        self.assertTrue(any(w["id"] == "default-turn-loop" for w in data_wf["data"]["workflows"]))

    def test_03_managed_runtime_startup_and_coding_task(self) -> None:
        """Step 3: Test managed daemon startup, healthy doctor, and headless replay run."""
        self.run_cmd(["bash", str(self.dist_dir / "install.sh"), str(self.install_prefix)])

        # Start standalone daemon from installed Python runtime
        daemon_entry = self.install_prefix / "lib" / "aether" / "lib" / "vanguard" / "packages" / "runtime" / "standalone_daemon.py"
        self.assertTrue(daemon_entry.exists())

        daemon_proc = subprocess.Popen(
            [
                "python3",
                str(daemon_entry),
                "--socket",
                self.clean_env["AETHER_RUNTIME_SOCK"],
                "--state-dir",
                str(self.clean_home / ".local" / "state"),
                "--data-dir",
                str(self.clean_home / ".local" / "share"),
                "--json",
            ],
            env=self.clean_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Wait for daemon ready
            time.sleep(1.0)
            if daemon_proc.poll() is not None:
                out, err = daemon_proc.communicate()
                self.fail(f"Daemon exited prematurely with code {daemon_proc.returncode}.\nStdout: {out}\nStderr: {err}")

            # Check aether doctor (should now report healthy: true)
            res_doc = self.run_cmd(["aether", "doctor", "--json"])
            self.assertEqual(res_doc.returncode, 0, f"Doctor output: {res_doc.stdout}\nErr: {res_doc.stderr}")
            data_doc = json.loads(res_doc.stdout)
            self.assertEqual(data_doc["status"], "success")
            self.assertTrue(data_doc["data"]["healthy"])
            self.assertEqual(data_doc["data"]["daemon"]["status"], "running")

            # Execute headless coding run with demo replay fixture
            res_run = self.run_cmd(
                [
                    "aether",
                    "run",
                    "--demo",
                    "successful-episode",
                    "--headless",
                ]
            )
            self.assertEqual(res_run.returncode, 0, f"Demo run failed: {res_run.stderr}\n{res_run.stdout}")
            self.assertTrue("Outcome: satisfied" in res_run.stdout or "satisfied" in res_run.stdout)

            # Test history inspection command from CLI
            res_hist = self.run_cmd(["aether", "history", "--json"])
            self.assertEqual(res_hist.returncode, 0)

            # Test workspace command from CLI
            res_ws = self.run_cmd(["aether", "workspace", "current", "--json"])
            self.assertEqual(res_ws.returncode, 0)

        finally:
            daemon_proc.terminate()
            try:
                daemon_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                daemon_proc.kill()

    def test_04_uninstall_preserves_user_data_and_reinstall_restores(self) -> None:
        """Step 4: Verify uninstaller cleans application while preserving user data, and reinstallation restores continuity."""
        self.run_cmd(["bash", str(self.dist_dir / "install.sh"), str(self.install_prefix)])

        # Create user configuration & workspace history
        user_config = self.clean_home / ".config" / "aether" / "config.json"
        user_config.parent.mkdir(parents=True, exist_ok=True)
        user_config.write_text(
            json.dumps(
                {
                    "general": {
                        "defaultAgent": "coding-agent",
                        "defaultWorkspace": "/tmp/my-persisted-ws",
                    },
                    "workspace": {
                        "recentWorkspaces": ["/tmp/my-persisted-ws"],
                    },
                }
            ),
            encoding="utf-8",
        )

        # Run uninstaller
        uninstall_script = self.dist_dir / "uninstall.sh"
        res_un = self.run_cmd(["bash", str(uninstall_script), str(self.install_prefix)])
        self.assertEqual(res_un.returncode, 0)

        # Application directory should be removed
        self.assertFalse((self.install_prefix / "lib" / "aether").exists())
        self.assertFalse((self.install_prefix / "bin" / "aether").exists())

        # User data must still exist!
        self.assertTrue(user_config.exists())

        # Re-install over existing user state
        res_reinstall = self.run_cmd(["bash", str(self.dist_dir / "install.sh"), str(self.install_prefix)])
        self.assertEqual(res_reinstall.returncode, 0)

        # Check config show via reinstalled CLI
        res_cfg = self.run_cmd(["aether", "config", "show", "--json"])
        self.assertEqual(res_cfg.returncode, 0)
        data_cfg = json.loads(res_cfg.stdout)
        self.assertEqual(data_cfg["data"]["settings"]["general"]["defaultAgent"], "coding-agent")
        self.assertEqual(data_cfg["data"]["settings"]["general"]["defaultWorkspace"], "/tmp/my-persisted-ws")


if __name__ == "__main__":
    unittest.main()
