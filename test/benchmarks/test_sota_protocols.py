import unittest

from benchmarks.protocols import BenchmarkReceipt, BenchmarkSubmission, BenchmarkTask
from benchmarks.statistics import PairedResult, mcnemar_exact, wilson_interval
from vanguard.packages.agency.context import (
    ContextPacketError, SectionAddress, build_context_packet, validate_resume_identity,
)


class SotaProtocolTests(unittest.TestCase):
    def test_wilson_and_missingness_are_explicit(self):
        self.assertAlmostEqual(wilson_interval(20, 20)[0], 0.8388698745, places=9)
        self.assertEqual(wilson_interval(20, 20)[1], 1.0)
        result = PairedResult(20, 20, missing=2)
        self.assertEqual(result.rate, 1.0)
        self.assertEqual(result.missing, 2)

    def test_mcnemar_excludes_missing_pairs(self):
        result = mcnemar_exact([True, False, None], [True, True, False])
        self.assertEqual((result["b"], result["c"], result["n_evaluated"], result["n_missing"]), (0, 1, 2, 1))

    def test_receipt_is_bound_to_split_and_exact_subject(self):
        task = BenchmarkTask("t1", "SWE-Bench Pro", "dev")
        submission = BenchmarkSubmission(task.digest, "diff --git a/x b/x", "m", "h")
        receipt = BenchmarkReceipt("SWE-Bench Pro", task.digest, submission.digest,
                                   "h", "m", "e", outcome=None,
                                   reason="dry run", split="dev",
                                   subject_sha="86142175fcab03ff93727ad1f5b336b22e01c66b")
        receipt.validate_subject(task, submission)
        with self.assertRaises(ValueError):
            BenchmarkReceipt("SWE-Bench Pro", task.digest, submission.digest,
                             "h", "m", "e", outcome="PASS", split="held-out",
                             subject_sha="86142175fcab03ff93727ad1f5b336b22e01c66b",
                             patch_digest="sha256:" + ("ab" * 32)).validate_subject(task, submission)

    def test_missing_subject_sha_refuses_receipt(self):
        task = BenchmarkTask("t1", "SWE-Bench Pro", "dev")
        submission = BenchmarkSubmission(task.digest, "diff --git a/x b/x", "m", "h")
        with self.assertRaises(ValueError) as ctx:
            BenchmarkReceipt("SWE-Bench Pro", task.digest, submission.digest,
                             "h", "m", "e", outcome=None, reason="dry run",
                             split="dev", subject_sha="")
        self.assertIn("subject_sha", str(ctx.exception).lower())

    def test_section_and_resume_identity_fail_closed(self):
        section = SectionAddress("big.py", 40, 40, "sha256:pre")
        self.assertTrue(section.digest().startswith("sha256:"))
        packet = build_context_packet(task_digest="sha256:t", repository_snapshot="sha256:r",
                                      provider="index", provider_version="1", query_digest="sha256:q",
                                      budget_tokens=100, repository_identity="sha256:repo",
                                      selection_policy_identity={"policy": "stable"})
        validate_resume_identity(packet, repository_identity="sha256:repo",
                                 index_snapshot_digest=None,
                                 selection_policy_identity={"policy": "stable"})
        with self.assertRaises(ContextPacketError):
            validate_resume_identity(packet, repository_identity="sha256:other",
                                     index_snapshot_digest=None,
                                     selection_policy_identity={"policy": "stable"})


if __name__ == "__main__":
    unittest.main()
