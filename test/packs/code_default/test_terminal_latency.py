"""S-M4-A-04: sub-second first-failure mandate measured as p95, not an anecdote."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"

_TRIALS = 20
_P95_MS = 300.0


def _percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, int(round((pct / 100.0) * (len(ordered) - 1))))
    return ordered[index]


class TerminalLatencyTests(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(PACK))
        from load import load_declared_entry
        from vanguard.packages.domain.wire.types_gen import EffectContext, EffectRequest, Reservation, SinkClass

        self.tmpdir = tempfile.TemporaryDirectory()
        Toolkit = load_declared_entry("mhf.toolkit.terminal")
        self.toolkit = Toolkit(self.tmpdir.name, timeout_seconds=8.0)
        self.ctx = EffectContext(principal="t", run_id="r1")
        self._req = EffectRequest
        self._res = Reservation
        self._sink = SinkClass

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_first_failure_p95_under_300ms(self) -> None:
        samples: list[float] = []
        for _ in range(_TRIALS):
            request = self._req(
                verb="proc.exec",
                args={"argv": ["python3", "-u", "-c",
                                "import sys; print('FAILED', flush=True); sys.exit(1)"]},
                selector={"kind": "generic", "uriPattern": "proc://exec/allow/git,pytest,ruff,python3"},
                sink=self._sink.PRIVILEGED,
                reservation=self._res(0, 8000, 0, 0, 1, 1),
            )
            result = self.toolkit.execute(request, self.ctx)
            self.assertEqual(result.value.outcome, "failed")
            self.assertIsNotNone(self.toolkit.last_first_failure_ms)
            samples.append(self.toolkit.last_first_failure_ms)
        p95 = _percentile(samples, 95)
        self.assertLess(p95, _P95_MS, f"p95={p95}ms over {len(samples)} trials: {samples}")


if __name__ == "__main__":
    unittest.main()
