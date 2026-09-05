"""Tests for unique durable run identity and explicit resume (T-84 / INS-01)."""

from __future__ import annotations

import pathlib
import unittest

from vanguard.packages.runtime import entrypoint


class TestRunIdentity(unittest.TestCase):
    def test_literal_run_cli_absent_from_entrypoint(self) -> None:
        entrypoint_path = pathlib.Path(entrypoint.__file__).resolve()
        content = entrypoint_path.read_text(encoding="utf-8")
        self.assertNotIn("run-cli", content, "Literal 'run-cli' must be absent from entrypoint.py")

    def test_omitted_run_id_produces_distinct_run_ids(self) -> None:
        req1 = {
            "command": "code",
            "brief": "first task",
            "workspace": ".",
            "fakeBackend": "greenfield-adaptive",
            "profile": "product",
        }
        req2 = {
            "command": "code",
            "brief": "second task",
            "workspace": ".",
            "fakeBackend": "greenfield-adaptive",
            "profile": "product",
        }
        frame1 = entrypoint.execute(req1)
        frame2 = entrypoint.execute(req2)

        run_id_1 = frame1["result"]["runId"]
        run_id_2 = frame2["result"]["runId"]

        self.assertTrue(run_id_1, "runId must not be empty")
        self.assertTrue(run_id_2, "runId must not be empty")
        self.assertNotEqual(run_id_1, run_id_2, "Successive requests must produce distinct run IDs")
        self.assertNotEqual(run_id_1, "run-cli")
        self.assertNotEqual(run_id_2, "run-cli")

    def test_run_id_appears_in_both_json_frame_and_receipt(self) -> None:
        req = {
            "command": "code",
            "brief": "verify frame and receipt runId",
            "workspace": ".",
            "fakeBackend": "greenfield-adaptive",
            "profile": "product",
        }
        frame = entrypoint.execute(req)
        self.assertIn("runId", frame, "Top-level frame must carry runId")
        self.assertIn("runId", frame["result"], "Receipt result must carry runId")
        self.assertEqual(frame["runId"], frame["result"]["runId"])
        self.assertTrue(frame["runId"].startswith("run-"))

    def test_explicit_resume_recovers_prior_run_identity(self) -> None:
        target_id = "run-custom-prior-12345"
        req = {
            "command": "code",
            "brief": "resume prior run",
            "resumeFrom": target_id,
            "workspace": ".",
            "fakeBackend": "greenfield-adaptive",
            "profile": "product",
        }
        frame = entrypoint.execute(req)
        self.assertEqual(frame["runId"], target_id)
        self.assertEqual(frame["result"]["runId"], target_id)

    def test_explicit_run_id_is_honored_when_provided(self) -> None:
        custom_id = "run-explicit-67890"
        req = {
            "command": "code",
            "brief": "task with explicit runId",
            "runId": custom_id,
            "workspace": ".",
            "fakeBackend": "greenfield-adaptive",
            "profile": "product",
        }
        frame = entrypoint.execute(req)
        self.assertEqual(frame["runId"], custom_id)
        self.assertEqual(frame["result"]["runId"], custom_id)


if __name__ == "__main__":
    unittest.main()
