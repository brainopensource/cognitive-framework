"""Tests for Greenfield v0.4.5.0 WebApp task fixture and sealed behavioral oracle (REQ-TRUST-001, S34-A-01)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.evaluators.suites.oracle_greenfield_webapp import (
    GreenfieldWebappOracle,
)


class TestGreenfieldOracleFixtureAndBehavior(unittest.TestCase):
    def test_public_fixture_is_solution_free(self) -> None:
        fixture_dir = Path(__file__).resolve().parents[2] / "lab" / "tasks" / "greenfield-v0450-webapp"
        self.assertTrue(fixture_dir.is_dir(), "Public fixture directory missing")

        # Verify TASK.md exists
        task_md = fixture_dir / "TASK.md"
        self.assertTrue(task_md.is_file(), "TASK.md missing in public fixture")

        # Verify no gold python code or solution html exists in the starting tree
        py_files = list(fixture_dir.glob("*.py"))
        html_files = list(fixture_dir.glob("*.html"))
        self.assertEqual(len(py_files), 0, "Public fixture must not contain pre-baked python implementation files")
        self.assertEqual(len(html_files), 0, "Public fixture must not contain pre-baked HTML files")

    def test_sealed_oracle_fails_on_empty_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "TASK.md").write_text("# Task\n")
            orig_cwd = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)
                oracle_case = GreenfieldWebappOracle()
                with self.assertRaises(AssertionError):
                    oracle_case.test_static_ui_exists()
            finally:
                os.chdir(orig_cwd)

    def test_sealed_oracle_passes_on_valid_sample_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "index.html").write_text("<!DOCTYPE html><html><body><h1>Tasks</h1><div id='tasks'></div></body></html>")
            server_py = """import http.server
import json
import sys

TASKS = []

class TaskHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/tasks':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(TASKS).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/tasks':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode('utf-8'))
            new_task = {"id": str(len(TASKS) + 1), "title": data.get("title", ""), "done": False}
            TASKS.append(new_task)
            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(new_task).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = http.server.HTTPServer(('127.0.0.1', port), TaskHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
"""
            (tmp / "server.py").write_text(server_py)

            orig_cwd = Path.cwd()
            try:
                import os
                os.chdir(tmp)
                oracle_case = GreenfieldWebappOracle()
                oracle_case.test_static_ui_exists()
                oracle_case.test_api_behavioral_contract()
            finally:
                os.chdir(orig_cwd)


if __name__ == "__main__":
    unittest.main()
