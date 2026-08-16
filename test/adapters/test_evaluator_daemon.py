"""S6B-MD-007: Daemon and Client for evaluator."""

import json
import os
import socket
import struct
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from vanguard.packages.adapters.evaluators.client import EvaluatorClient
from vanguard.packages.adapters.evaluators.daemon import DaemonConfig, EvaluatorDaemon
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef


class EvaluatorDaemonContract(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.socket_path = os.path.join(self.tmp.name, "evaluator.sock")
        self.workspace = Path(self.tmp.name) / "workspace"
        self.workspace.mkdir()
        import subprocess
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        
        self.config = DaemonConfig(
            socket_path=self.socket_path,
            image_digest="sha256:" + "a" * 64,
            workspace=str(self.workspace),
            oracle_digests={},
            command=("python3", "-c", "print('ok')"),
            expected_uid=os.getuid(),
            timeout_seconds=5.0
        )
        self.daemon = EvaluatorDaemon(self.config)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _start_daemon(self):
        t = threading.Thread(target=self.daemon.serve_once, daemon=True)
        t.start()
        for _ in range(50):
            if os.path.exists(self.socket_path):
                break
            time.sleep(0.01)
        return t

    @patch("socket.socket.getsockopt")
    def test_successful_evaluation(self, mock_getsockopt):
        mock_getsockopt.return_value = struct.pack("3i", os.getpid(), os.getuid(), os.getgid())
        self._start_daemon()
        
        client = EvaluatorClient(
            socket_path=self.socket_path,
            expected_uid=os.getuid(),
            expected_image_digest="sha256:" + "a" * 64,
            timeout_seconds=2.0
        )
        
        result = client.evaluate(RunRef("run1", episode_id="ep1"), EvaluationProtocol("test"))
        self.assertTrue(result.ok)
        if result.value.outcome != "claims":
            print(f"FAILED REASON: {result.value.reason}")
        self.assertEqual(result.value.outcome, "claims")

    @patch("socket.socket.getsockopt")
    def test_wrong_uid(self, mock_getsockopt):
        mock_getsockopt.return_value = struct.pack("3i", os.getpid(), 9999, os.getgid())
        self._start_daemon()
        
        client = EvaluatorClient(
            socket_path=self.socket_path,
            expected_uid=os.getuid(),
            expected_image_digest="sha256:" + "a" * 64,
            timeout_seconds=2.0
        )
        
        result = client.evaluate(RunRef("run1", episode_id="ep1"), EvaluationProtocol("test"))
        self.assertEqual(result.value.outcome, "inconclusive")
        self.assertEqual(result.value.reason, "evaluator_identity_unverified")

    @patch("socket.socket.getsockopt")
    def test_wrong_image_digest(self, mock_getsockopt):
        mock_getsockopt.return_value = struct.pack("3i", os.getpid(), os.getuid(), os.getgid())
        self._start_daemon()
        
        client = EvaluatorClient(
            socket_path=self.socket_path,
            expected_uid=os.getuid(),
            expected_image_digest="sha256:" + "b" * 64,
            timeout_seconds=2.0
        )
        
        result = client.evaluate(RunRef("run1", episode_id="ep1"), EvaluationProtocol("test"))
        self.assertEqual(result.value.outcome, "inconclusive")
        self.assertEqual(result.value.reason, "evaluator_image_unverified")

    @patch("socket.socket.getsockopt")
    def test_timeout(self, mock_getsockopt):
        mock_getsockopt.return_value = struct.pack("3i", os.getpid(), os.getuid(), os.getgid())
        # Start a dummy server that sleeps
        def slow_server():
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.bind(self.socket_path)
                s.listen(1)
                conn, _ = s.accept()
                with conn:
                    time.sleep(2)
        
        threading.Thread(target=slow_server, daemon=True).start()
        time.sleep(0.1)

        client = EvaluatorClient(self.socket_path, os.getuid(), "sha256:" + "a" * 64, 0.1)
        result = client.evaluate(RunRef("run1", episode_id="ep1"), EvaluationProtocol("test"))
        self.assertEqual(result.value.outcome, "inconclusive")
        self.assertEqual(result.value.reason, "evaluator_timeout")

    @patch("socket.socket.getsockopt")
    def test_socket_truncation(self, mock_getsockopt):
        mock_getsockopt.return_value = struct.pack("3i", os.getpid(), os.getuid(), os.getgid())
        def drop_server():
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.bind(self.socket_path)
                s.listen(1)
                conn, _ = s.accept()
                with conn:
                    pass # Drops immediately
        
        threading.Thread(target=drop_server, daemon=True).start()
        time.sleep(0.1)

        client = EvaluatorClient(self.socket_path, os.getuid(), "sha256:" + "a" * 64, 2.0)
        result = client.evaluate(RunRef("run1", episode_id="ep1"), EvaluationProtocol("test"))
        self.assertEqual(result.value.outcome, "inconclusive")
        self.assertEqual(result.value.reason, "evaluator_truncation")

if __name__ == "__main__":
    unittest.main()
