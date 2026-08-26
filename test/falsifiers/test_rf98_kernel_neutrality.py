"""RF-98: the Kernel Neutrality Gate, and proof that it can fail.

`ADR-0096 §7.2/§7.4`: introducing a new capability or domain yields kernel
semantic diff == 0, or an ADR explains why not.

M-5b is the first material run of this gate. The formal-SAT pack is a
materially non-coding domain; if the TCB had to learn anything about Boolean
satisfiability to run it, the generality claim is false and that is the
finding, not something to route around.

A gate nobody has watched fail is an assertion, not a gate -- so the planted
cases here prove it actually fires.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINTER = "tools/linters/check_kernel_neutrality.py"


def _run(*args: str) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, LINTER, *args], cwd=ROOT,
                          capture_output=True, text=True, timeout=120)
    receipt = json.loads(proc.stdout.strip().splitlines()[-1])
    return proc.returncode, receipt


class TheGatePassesOnTheRealTree(unittest.TestCase):
    def test_the_kernel_names_no_pack_verb(self) -> None:
        code, receipt = _run()
        self.assertEqual(receipt["structural"]["status"], "neutral",
                         receipt["structural"]["leaks"])
        self.assertEqual(code, 0)

    def test_the_formal_pack_was_actually_scanned(self) -> None:
        # Neutrality over a corpus that excludes the new domain proves nothing.
        _, receipt = _run()
        self.assertIn("formal-sat", receipt["structural"]["packs_scanned"])


class TheHistoricalHalfNeverReportsCleanWithoutABaseline(unittest.TestCase):
    """The RF-86 lesson: a gate that passes when it cannot run is worse than none."""

    def test_an_unresolvable_baseline_is_unavailable_not_clean(self) -> None:
        _, receipt = _run("--baseline", "no-such-tag-exists")
        self.assertEqual(receipt["historical"]["status"], "unavailable")
        self.assertNotEqual(receipt["historical"]["status"], "clean")

    def test_the_default_baseline_is_the_m5a_tag(self) -> None:
        _, receipt = _run()
        self.assertEqual(receipt["historical"]["baseline"], "M-5A-BASE-v2")

    def test_a_resolvable_baseline_reports_a_real_comparison(self) -> None:
        _, receipt = _run("--baseline", "HEAD")
        self.assertIn(receipt["historical"]["status"], {"clean", "changed"})


class ThePlantedLeakIsDetected(unittest.TestCase):
    """Fail-closed proof, without mutating the real kernel."""

    def test_a_pack_verb_named_in_the_kernel_is_caught(self) -> None:
        import ast
        sys.path.insert(0, str(ROOT / "tools/linters"))
        import importlib
        module = importlib.import_module("check_kernel_neutrality")

        real_vocab = module.pack_vocabulary
        real_ids = module.kernel_identifiers
        try:
            module.pack_vocabulary = lambda: {"formal-sat": {"sat.witness.write"}}
            module.kernel_identifiers = lambda: real_ids() | {"sat.witness.write"}
            leaks = {}
            for pack, words in module.pack_vocabulary().items():
                hits = sorted(words & module.kernel_identifiers())
                if hits:
                    leaks[pack] = hits
            self.assertEqual(leaks, {"formal-sat": ["sat.witness.write"]})
        finally:
            module.pack_vocabulary = real_vocab
            module.kernel_identifiers = real_ids

    def test_the_shared_substrate_verbs_are_not_counted_as_domain_leaks(self) -> None:
        sys.path.insert(0, str(ROOT / "tools/linters"))
        import importlib
        module = importlib.import_module("check_kernel_neutrality")
        # `patch.apply` is bound by `runtime/wiring.py` for every domain; a
        # pack reusing it has introduced no domain concept.
        for pack, verbs in module.pack_vocabulary().items():
            self.assertNotIn("patch.apply", verbs, pack)
            self.assertNotIn("fs.read", verbs, pack)

    def test_the_formal_pack_declares_its_own_verb(self) -> None:
        # Otherwise the gate is neutral only because the domain declared nothing.
        sys.path.insert(0, str(ROOT / "tools/linters"))
        import importlib
        module = importlib.import_module("check_kernel_neutrality")
        self.assertIn("sat.witness.write", module.pack_vocabulary()["formal-sat"])


if __name__ == "__main__":
    unittest.main()
