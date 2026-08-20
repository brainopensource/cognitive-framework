"""S-M3-B-03: streaming proc.exec with first-failure classification <300ms."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"


class TerminalRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(PACK))
        from load import load_declared_entry
        from layer0.spi.types_gen import EffectContext, EffectRequest, Reservation, SinkClass

        self.tmpdir = tempfile.TemporaryDirectory()
        Toolkit = load_declared_entry("mhf.toolkit.terminal")
        self.toolkit = Toolkit(self.tmpdir.name, timeout_seconds=8.0)
        self.ctx = EffectContext(principal="t", run_id="r1")
        self._req = EffectRequest
        self._res = Reservation
        self._sink = SinkClass

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_first_failure_classified_before_process_exit(self) -> None:
        request = self._req(
            verb="proc.exec",
            args={"argv": ["python3", "-u", "-c", "import time,sys; print('FAILED', flush=True); time.sleep(1.5)"]},
            selector={"kind": "generic", "uriPattern": "proc://exec/allow/git,pytest,ruff,python3"},
            sink=self._sink.PRIVILEGED,
            reservation=self._res(0, 8000, 0, 0, 1, 1),
        )
        result = self.toolkit.execute(request, self.ctx)
        self.assertEqual(result.value.outcome, "completed")
        self.assertIsNotNone(self.toolkit.last_first_failure_ms)
        self.assertLess(self.toolkit.last_first_failure_ms, 300)

    def test_zero_exit_is_completed(self) -> None:
        request = self._req(
            verb="proc.exec",
            args={"argv": ["python3", "-c", "print('ok')"]},
            selector={"kind": "generic", "uriPattern": "proc://exec/allow/git,pytest,ruff,python3"},
            sink=self._sink.PRIVILEGED,
            reservation=self._res(0, 8000, 0, 0, 1, 1),
        )
        result = self.toolkit.execute(request, self.ctx)
        self.assertEqual(result.value.outcome, "completed")


if __name__ == "__main__":
    unittest.main()
