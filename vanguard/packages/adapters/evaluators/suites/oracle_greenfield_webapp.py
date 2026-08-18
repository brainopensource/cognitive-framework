"""Sealed behavioral oracle for Greenfield Task Management Web Application (S34-A-01).

Behaviorally tests HTTP API endpoints (GET /api/tasks, POST /api/tasks) and static UI
without subprocess invocations, keeping N-06 isolation strictly intact.
"""

import http.client
import importlib.util
import json
import socket
import sys
import threading
import time
import unittest
from pathlib import Path


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class GreenfieldWebappOracle(unittest.TestCase):
    """Behavioral evaluation of the greenfield web application."""

    def test_static_ui_exists(self) -> None:
        """Verify static HTML exists in workspace."""
        root = Path(".").resolve()
        html_files = [
            p for p in root.rglob("*.html")
            if ".git" not in p.parts
            and "node_modules" not in p.parts
            and "docs" not in p.parts
        ]
        if not html_files and not (root / "TASK.md").is_file():
            raise unittest.SkipTest("Not in greenfield workspace")

        self.assertTrue(
            len(html_files) > 0,
            f"No HTML file found in workspace: {list(root.iterdir())}",
        )
        content = html_files[0].read_text(encoding="utf-8")
        self.assertTrue(len(content) > 20, "HTML file is empty or trivial")

    def test_api_behavioral_contract(self) -> None:
        """Import the server entrypoint and test GET/POST /api/tasks endpoints."""
        root = Path(".").resolve()
        candidates = []
        for name in ("server.py", "app.py", "main.py", "app/server.py", "src/server.py"):
            p = root / name
            if p.is_file():
                candidates.append(p)

        if not candidates:
            if not (root / "TASK.md").is_file():
                raise unittest.SkipTest("Not in greenfield workspace")
            self.fail(f"No server Python implementation found in workspace: {list(root.iterdir())}")

        server_script = candidates[0]
        port = find_free_port()

        # Dynamically load the server module
        spec = importlib.util.spec_from_file_location("greenfield_app_module", str(server_script))
        if spec is None or spec.loader is None:
            self.fail(f"Failed to load module spec from {server_script}")

        module = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(root))
        try:
            # Execute module in thread or instantiate server if main / handler exposed
            orig_argv = sys.argv
            sys.argv = [str(server_script), str(port)]
            server_obj = None
            stop_event = threading.Event()

            def run_server() -> None:
                nonlocal server_obj
                try:
                    spec.loader.exec_module(module)
                    if hasattr(module, "main"):
                        module.main()
                except Exception:
                    pass

            t = threading.Thread(target=run_server, daemon=True)
            t.start()

            # Wait for server to respond on the assigned port
            connected = False
            for _ in range(30):
                time.sleep(0.1)
                try:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1.0)
                    conn.request("GET", "/api/tasks")
                    resp = conn.getresponse()
                    if resp.status in (200, 201):
                        connected = True
                        data = json.loads(resp.read().decode("utf-8"))
                        self.assertIsInstance(data, (list, dict))
                        break
                except Exception:
                    continue

            self.assertTrue(connected, "Server failed to respond to GET /api/tasks within timeout")

            # Test POST /api/tasks
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2.0)
            headers = {"Content-Type": "application/json"}
            payload = json.dumps({"title": "Test Greenfield Task"})
            conn.request("POST", "/api/tasks", body=payload, headers=headers)
            post_resp = conn.getresponse()
            self.assertIn(post_resp.status, (200, 201))

            # Test GET /api/tasks contains created task
            conn.request("GET", "/api/tasks")
            get_resp = conn.getresponse()
            get_data = json.loads(get_resp.read().decode("utf-8"))
            tasks_list = get_data if isinstance(get_data, list) else get_data.get("tasks", [])
            titles = [t.get("title") if isinstance(t, dict) else str(t) for t in tasks_list]
            self.assertTrue(
                any("Test Greenfield Task" in t for t in titles if t),
                f"Created task not found in GET response: {tasks_list}",
            )

        finally:
            sys.argv = orig_argv
            if str(root) in sys.path:
                sys.path.remove(str(root))


if __name__ == "__main__":
    unittest.main()
