"""S060-B-11 / TSK-SEC-001: AT-12 compensating control on the kernel tree.

Kernel source must not import the evaluator adapter. The isolated evaluator
remains a separate identity (inverted K-40). REQ-TRUST-001.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class AT12KernelDoesNotReachEvaluator(unittest.TestCase):
    def test_kernel_sources_do_not_name_evaluator_adapters(self) -> None:
        root = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "kernel"
        offenders: list[str] = []
        for path in root.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            if "adapters.evaluators" in text or "IsolatedEvaluator" in text:
                offenders.append(str(path.relative_to(root.parent.parent.parent)))
        self.assertEqual(offenders, [])
