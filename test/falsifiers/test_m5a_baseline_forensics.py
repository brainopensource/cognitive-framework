"""Forensics test fixtures for the contaminated historical ref M-5A-BASE-v2 (ADR-0102).

Proves that:
1. M-5A-BASE-v2 resolves locally to commit 1b4ce1a19e5d6ef2fd0575743fa60ecea0055fdd.
2. M-5A-BASE-v2 is a lightweight tag (points to a 'commit' object, not an annotated 'tag' object).
3. M-5A-BASE-v2 is absent from the configured remote (refs/tags/M-5A-BASE-v2 does not exist on origin).
4. M-5A-BASE-v2 has successor milestone commits in its ancestry (e.g. M-6.5 / P2 feature commits).
5. RF-86 fails closed on 1b4ce1a against HEAD because protected substrate paths were mutated.
6. The disposition is machine-verifiably CONTAMINATED_UNPUBLISHED and cannot serve as an experimental control.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTAMINATED_REF = "M-5A-BASE-v2"
CONTAMINATED_COMMIT = "1b4ce1a19e5d6ef2fd0575743fa60ecea0055fdd"


class ContaminatedBaselineForensicsTests(unittest.TestCase):
    """Machine-verifiable forensics proving ADR-0102 findings on M-5A-BASE-v2."""

    def test_local_tag_resolves_to_expected_contaminated_commit(self) -> None:
        result = subprocess.run(
            ["git", "rev-parse", f"{CONTAMINATED_REF}^{{commit}}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"Local tag {CONTAMINATED_REF} must resolve locally for forensics: {result.stderr}",
        )
        resolved = result.stdout.strip()
        self.assertEqual(
            resolved,
            CONTAMINATED_COMMIT,
            f"Expected {CONTAMINATED_REF} to resolve to {CONTAMINATED_COMMIT}, got {resolved}",
        )

    def test_tag_is_lightweight_not_annotated(self) -> None:
        """A valid baseline control must be an annotated tag object, not a lightweight ref."""
        result = subprocess.run(
            ["git", "cat-file", "-t", CONTAMINATED_REF],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        obj_type = result.stdout.strip()
        # M-5A-BASE-v2 is a lightweight ref pointing directly to a commit
        self.assertEqual(
            obj_type,
            "commit",
            f"Expected {CONTAMINATED_REF} to be a lightweight tag ('commit'), not annotated ('tag')",
        )

    def test_tag_is_absent_from_configured_remote(self) -> None:
        """The tag does not exist on origin and cannot be resolved in clean remote CI."""
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "origin", f"refs/tags/{CONTAMINATED_REF}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            self.assertEqual(
                result.stdout.strip(),
                "",
                f"Tag {CONTAMINATED_REF} should not exist on remote origin per ADR-0102",
            )

    def test_ancestry_contains_successor_treatment_commits(self) -> None:
        """Proves scientific contamination: M-6.5 and later feature commits occur in 1b4ce1a ancestry."""
        result = subprocess.run(
            ["git", "log", "--oneline", "-n", "50", CONTAMINATED_COMMIT],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        log_output = result.stdout

        # Contaminated successor commits present in ancestry
        self.assertIn("feat(m65): add pure progress and controller contracts", log_output)
        self.assertIn("docs(P2-M65)", log_output)

    def test_rf86_frozen_substrate_mutated_since_contaminated_ref(self) -> None:
        """Proves that comparing HEAD to 1b4ce1a yields mutated protected substrate files."""
        frozen_paths = [
            "vanguard/packages/domain",
            "vanguard/packages/kernel",
            "vanguard/packages/ports",
            "vanguard/packages/runtime",
            "vanguard/packages/agency/episode",
        ]
        result = subprocess.run(
            ["git", "diff", "--stat", CONTAMINATED_COMMIT, "HEAD", "--", *frozen_paths],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        diff_stat = result.stdout.strip()
        self.assertTrue(
            len(diff_stat) > 0,
            "Diff against contaminated ref must show substrate changes (proves RF-86 failure)",
        )
        self.assertIn("agent_view.py", diff_stat)

    def test_disposition_is_contaminated_unpublished(self) -> None:
        """ADR-0102 classifies M-5A-BASE-v2 as CONTAMINATED_UNPUBLISHED, not an experimental control."""
        from vanguard.packages.domain.evidence.baseline import (
            BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED,
            classify_ref_disposition,
        )

        disposition = classify_ref_disposition(ROOT, CONTAMINATED_REF)
        self.assertEqual(
            disposition,
            BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED,
        )


if __name__ == "__main__":
    unittest.main()
