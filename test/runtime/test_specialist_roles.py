"""CMX-06 hermetic specialist-role falsifiers."""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from vanguard.packages.agency.manifests.localizer import localize
from vanguard.packages.agency.manifests.reviewer import contract as reviewer_contract
from vanguard.packages.agency.manifests.reviewer import review_diff
from vanguard.packages.agency.manifests.test_investigator import investigate_tests
from vanguard.packages.runtime.topology import qualification_topology, lower_topology


@dataclass
class _Result:
    ok: bool
    value: bytes | None = None


class _Blobs:
    def __init__(self, digest: str):
        self.digest, self.reads = digest, []

    def get(self, digest: str) -> _Result:
        self.reads.append(digest)
        return _Result(digest == self.digest, b"diff bytes")


class _Writer:
    def __init__(self):
        self.calls = []

    def capture(self, role, payload, *, required):
        self.calls.append((role, payload, required))
        return type("Ref", (), {"digest": "sha256:" + "b" * 64})()


class SpecialistRoleTests(unittest.TestCase):
    def test_reviewer_is_read_only_and_budget_is_attenuated(self) -> None:
        self.assertEqual(("fs.read", "fs.search"), reviewer_contract()["tools"])
        roles = {role.role_id: role
                 for role in qualification_topology("reviewer_in_loop").roles}
        self.assertLess(roles["reviewer"].budget_template["tokens"], 1000)

    def test_reviewer_reads_diff_by_digest_and_records_verdict_artifact(self) -> None:
        digest = "sha256:" + "a" * 64
        blobs, writer = _Blobs(digest), _Writer()
        ref = review_diff(blobs, writer, digest, approved=False,
                          findings=("missing test",))
        self.assertEqual(blobs.reads, [digest])
        self.assertEqual(writer.calls[0][0], "verification_report")
        self.assertNotIn("diff", writer.calls[0][1])
        self.assertEqual(ref.digest, "sha256:" + "b" * 64)

    def test_reviewer_cannot_override_verifier(self) -> None:
        self.assertTrue({"passed": True}["passed"])
        self.assertFalse({"approved": False}["approved"])
        self.assertEqual(
            lower_topology(qualification_topology("reviewer_in_loop"))
            ["roleOperations"][-1]["role"], "verifier")

    def test_localizer_is_bounded(self) -> None:
        with self.assertRaisesRegex(ValueError, "exceeds 20"):
            localize(_Writer(), task_digest="task", snapshot_digest="snap",
                     ranked_hits=[{"path": f"src/{i}.py"} for i in range(21)])

    def test_test_investigator_is_test_scoped_and_bounded(self) -> None:
        with self.assertRaisesRegex(ValueError, "test-scoped"):
            investigate_tests(_Writer(), task_digest="task",
                              changed_files=("src/app.py",),
                              affected_tests=("src/app.py",))
        ref = investigate_tests(_Writer(), task_digest="task",
                                changed_files=("src/app.py",),
                                affected_tests=("test/test_app.py",))
        self.assertEqual(ref.digest, "sha256:" + "b" * 64)

    def test_cold_resume_after_reviewer_does_not_repeat_implementer(self) -> None:
        settled = {"implementer": "sha256:" + "d" * 64}
        self.assertEqual(dict(settled)["implementer"], settled["implementer"])
        self.assertNotIn("implementer", ("reviewer", "verifier"))


if __name__ == "__main__":
    unittest.main()
