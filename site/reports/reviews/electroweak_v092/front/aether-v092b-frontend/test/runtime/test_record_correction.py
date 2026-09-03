"""`RecordCorrection` is bound to its wire contract.

S8-A-04. `_cmd_RecordCorrection` appended whatever it was handed and never
called `parse_wire("CorrectionRecord", ...)`, so the corpus could accept
corrections the normative reader rejects. The contract already carries the
rules -- the reason-code enum, and `D-07`'s rule that a `style` or
`architecture_preference` correction may not be scoped wider than the people it
came from. Nothing was enforcing them.

Open since the Beta audit. `009 §3.1`, `D-07`, `MEM-1`.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.runtime.service import RuntimeService, ServiceInboxStore

DIGEST_A = "sha256:" + "a" * 64
DIGEST_B = "sha256:" + "b" * 64


def correction(**overrides: object) -> dict:
    base = {
        "episodeId": "01890000-0000-7000-8000-000000000001",
        "proposedPatchDigest": DIGEST_A,
        "acceptedPatchDigest": DIGEST_B,
        "reasonCodes": ["functional_defect"],
        "magnitude": "minor",
        "scope": "repo",
        "correctingPrincipalRole": "user",
    }
    base.update(overrides)
    return base


class RecordCorrectionParsesItsWire(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.inbox = ServiceInboxStore(Path(self._tempdir.name) / "service.db")
        self.service = RuntimeService(self.inbox)

    def tearDown(self) -> None:
        self.inbox.close()
        self._tempdir.cleanup()

    def _record(self, payload: dict) -> dict:
        return self.service._cmd_RecordCorrection(
            "run-1", payload, "operator", "cmd-1")

    def test_a_style_correction_scoped_general_is_rejected(self) -> None:
        """`D-07`: a taste correction may not become a global rule."""

        with self.assertRaises(ValueError) as caught:
            self._record({"correction": correction(
                reasonCodes=["style"], scope="general")})
        self.assertIn("scope", str(caught.exception))

    def test_an_architecture_preference_scoped_domain_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._record({"correction": correction(
                reasonCodes=["architecture_preference"], scope="domain")})

    def test_a_style_correction_scoped_to_a_team_is_accepted(self) -> None:
        result = self._record({"correction": correction(
            reasonCodes=["style"], scope="team")})
        self.assertEqual(result["status"], "recorded")

    def test_an_unknown_reason_code_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._record({"correction": correction(reasonCodes=["vibes"])})

    def test_an_empty_reason_code_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._record({"correction": correction(reasonCodes=[])})

    def test_an_unknown_magnitude_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._record({"correction": correction(magnitude="catastrophic")})

    def test_a_missing_field_is_rejected(self) -> None:
        payload = correction()
        del payload["acceptedPatchDigest"]
        with self.assertRaises(ValueError):
            self._record({"correction": payload})

    def test_a_loosely_typed_payload_is_rejected(self) -> None:
        """The exact shape the old code accepted without complaint."""

        with self.assertRaises(ValueError):
            self._record({"correction": {"reason": "style", "feedback": "use snake_case"}})

    def test_an_absent_correction_is_rejected_rather_than_recorded_empty(self) -> None:
        with self.assertRaises(ValueError):
            self._record({})

    def test_a_valid_correction_round_trips_onto_the_ledger(self) -> None:
        result = self._record({"correction": correction()})
        self.assertEqual(result["status"], "recorded")
        events = self.inbox.get_events("run-1")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["payload"]["kind"], "CorrectionRecorded")
        self.assertEqual(events[0]["payload"]["correction"], correction())


class NoPromotionPathFromACorrection(unittest.TestCase):
    """`MEM-1` / `D-07`: a correction is evidence, never an artifact."""

    def test_the_command_emits_a_record_and_nothing_else(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            inbox = ServiceInboxStore(Path(tmp) / "service.db")
            service = RuntimeService(inbox)
            service._cmd_RecordCorrection(
                "run-2", {"correction": correction()}, "operator", "cmd-2")
            kinds = [e["payload"]["kind"] for e in inbox.get_events("run-2")]
            self.assertEqual(kinds, ["CorrectionRecorded"])
            for forbidden in ("ArtifactCreated", "ActivationChanged", "ArtifactPromoted"):
                self.assertNotIn(forbidden, kinds)
            inbox.close()

    def test_the_source_names_no_promotion_call(self) -> None:
        import inspect

        source = inspect.getsource(RuntimeService._cmd_RecordCorrection)
        for forbidden in ("promote", "ArtifactCreated", "activate"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
