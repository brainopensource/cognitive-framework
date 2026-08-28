"""Contract tests for the checkout-independent SWE benchmark harness."""

from __future__ import annotations

import tempfile
import unittest
import hashlib
from pathlib import Path

from tools.runners.run_swe_challenge import (
    _benchmark_identity,
    _changed_files,
    _snapshot_digest,
    get_diff_size,
    setup_challenge,
)


class SweChallengeRunnerTests(unittest.TestCase):
    def test_subject_snapshot_is_stable_and_patch_accounting_is_content_based(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = setup_challenge("tier1_ring_buffer_stream", root)
            digest = _snapshot_digest(baseline)

            (root / "ring" / "buffer.py").write_text(
                (root / "ring" / "buffer.py").read_text() + "\n# evaluated change\n",
                encoding="utf-8",
            )
            # Harness-generated oracle material is not part of the submitted
            # patch and therefore cannot contaminate the changed-file list.
            (root / "oracle_test.py").write_text("oracle", encoding="utf-8")

            self.assertEqual(digest, _snapshot_digest(dict(reversed(list(baseline.items())))))
            self.assertEqual(_changed_files(root, baseline), ["ring/buffer.py"])
            self.assertGreater(get_diff_size(root, baseline), 0)
            self.assertFalse((root / ".git").exists())

            identity = _benchmark_identity(
                "tier1_ring_buffer_stream", root, baseline, "provider/model",
            )
            self.assertEqual(identity["subject_digest"], digest)
            self.assertEqual(identity["provider"], "openrouter")
            self.assertEqual(identity["source_manifest"]["ring/buffer.py"],
                             hashlib.sha256(baseline["ring/buffer.py"]).hexdigest())


if __name__ == "__main__":
    unittest.main()
