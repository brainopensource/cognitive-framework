import unittest
import sys
from src.sandbox_runner import SandboxRunner

class TestSandboxTimeout(unittest.TestCase):
    def test_timeout_reports_proper_status_and_code(self):
        # Run a command that sleeps for 5 seconds with 0.5s timeout
        cmd = [sys.executable, "-c", "import time; time.sleep(5.0)"]
        result = SandboxRunner.run_command(cmd, timeout_seconds=0.5)

        # Falsifier Assertion: status MUST be TIMEOUT and return_code MUST be -1
        self.assertEqual(
            result.status,
            "TIMEOUT",
            f"Falsifier failed: Expected status TIMEOUT, got {result.status}"
        )
        self.assertEqual(
            result.return_code,
            -1,
            f"Falsifier failed: Expected return_code -1, got {result.return_code}"
        )

if __name__ == "__main__":
    unittest.main()
