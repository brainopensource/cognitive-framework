"""`vg why <artifact>` is load-bearing (`S10-A-04`).

`_cmd_ExplainArtifact` returned `{"explanation": ""}`. The command existed and
answered nothing, which is worse than absent: a caller cannot tell "no evidence
exists" from "the command is a stub", so an unevidenced artifact looked exactly
like a well-evidenced one.

Three questions, all derived — activation from the ledger, prediction and
demotion from the `Claim` store (`S8-A-05`). Nothing is stored twice, so an
explanation cannot drift from the events it explains (`A-07`).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.domain.evidence.claim import parse_claim
from vanguard.packages.runtime.explain import explain_artifact
from vanguard.packages.runtime.service import RuntimeService, ServiceInboxStore

DIGEST = {c: "sha256:" + c * 64 for c in "abcd"}


def claim_wire(**overrides) -> dict:
    base = {
        "id": "claim-1",
        "subject": "artifact-1",
        "predicate": "repairs.single_file_bug",
        "value": 0.62,
        "protocol": DIGEST["a"],
        "evaluator": {"evaluatorId": "evaluator-suite-1",
                      "class": "mechanically_reproducible",
                      "imageDigest": DIGEST["b"]},
        "environmentProfile": DIGEST["c"],
        "substrateProfile": DIGEST["d"],
        "taskDistribution": DIGEST["a"],
        "uncertainty": {"kind": "interval", "lower": 0.51, "upper": 0.73, "n": 40},
        "validity": {"domains": ["python"]},
        "invalidationConditions": [{"condition": "the oracle suite fails",
                                    "checkKind": "automatic",
                                    "checkRef": "evaluator-suite-1"}],
    }
    base.update(overrides)
    return base


class _Event:
    def __init__(self, kind: str, artifact_id: str, **extra) -> None:
        self.payload = {"kind": kind, "artifactId": artifact_id, **extra}
        self.occurred_at = "2026-08-17T00:00:00.000Z"
        self.seq = "0001"


class TheThreeQuestions(unittest.TestCase):
    def setUp(self) -> None:
        self.claim = parse_claim(claim_wire())
        self.events = [_Event("ArtifactCreated", "artifact-1")]

    def test_it_says_what_activated_the_artifact(self) -> None:
        result = explain_artifact("artifact-1", events=self.events, claims=[self.claim])
        self.assertEqual(result.status, "active")
        self.assertEqual(result.activation[0]["kind"], "ArtifactCreated")

    def test_it_says_what_the_artifact_predicts(self) -> None:
        result = explain_artifact("artifact-1", events=self.events, claims=[self.claim])
        predicts = result.predictions[0]
        self.assertEqual(predicts["predicate"], "repairs.single_file_bug")
        self.assertEqual(predicts["uncertainty"]["lower"], 0.51)
        self.assertEqual(predicts["evaluatorClass"], "mechanically_reproducible")

    def test_it_says_what_would_demote_the_artifact(self) -> None:
        result = explain_artifact("artifact-1", events=self.events, claims=[self.claim])
        demote = result.demotions[0]
        self.assertEqual(demote["condition"], "the oracle suite fails")
        self.assertEqual(demote["checkKind"], "automatic")

    def test_deactivation_moves_the_reported_status(self) -> None:
        events = self.events + [
            _Event("ActivationChanged", "artifact-1", toStatus="quarantined")]
        result = explain_artifact("artifact-1", events=events, claims=[self.claim])
        self.assertEqual(result.status, "quarantined")

    def test_another_artifacts_events_and_claims_are_not_borrowed(self) -> None:
        other = parse_claim(claim_wire(id="claim-2", subject="artifact-2"))
        result = explain_artifact("artifact-1", events=self.events,
                                  claims=[self.claim, other])
        self.assertEqual([p["claimId"] for p in result.predictions], ["claim-1"])


class AbsenceIsReportedNotSmoothed(unittest.TestCase):
    """The load-bearing property: unevidenced must not resemble well-evidenced."""

    def test_an_artifact_with_no_claim_says_so(self) -> None:
        result = explain_artifact("artifact-1",
                                  events=[_Event("ArtifactCreated", "artifact-1")])
        self.assertEqual(result.predictions, ())
        self.assertEqual(result.demotions, ())
        self.assertTrue(any("no evidence claim" in note for note in result.notes))

    def test_an_artifact_with_no_activation_event_says_so(self) -> None:
        result = explain_artifact("artifact-1", events=[], claims=[])
        self.assertEqual(result.status, "unknown")
        self.assertTrue(any("no activation event" in note for note in result.notes))

    def test_the_explanation_is_never_an_empty_string(self) -> None:
        """The exact stub behaviour this row removes."""

        rendered = explain_artifact("artifact-1").to_dict()
        self.assertNotEqual(rendered, "")
        self.assertTrue(rendered["notes"])


class SubstrateDriftSurfacesInTheExplanation(unittest.TestCase):
    def test_a_moved_substrate_marks_the_claim_stale(self) -> None:
        claim = parse_claim(claim_wire())
        result = explain_artifact("artifact-1", claims=[claim],
                                  substrate_profile=DIGEST["a"])
        self.assertEqual(result.stale, ("claim-1",))
        self.assertTrue(any("substrate has moved" in n for n in result.notes))

    def test_an_unchanged_substrate_marks_nothing_stale(self) -> None:
        claim = parse_claim(claim_wire())
        result = explain_artifact("artifact-1", claims=[claim],
                                  substrate_profile=DIGEST["d"])
        self.assertEqual(result.stale, ())


class TheServiceCommandIsBound(unittest.TestCase):
    """`vg why` reaches this through the path the CLI already calls."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.inbox = ServiceInboxStore(Path(self._tmp.name) / "svc.db")
        self.addCleanup(self.inbox.close)
        self.service = RuntimeService(self.inbox, claims=[claim_wire()])

    def test_the_command_returns_a_structured_explanation(self) -> None:
        result = self.service._cmd_ExplainArtifact(
            "run-1", {"artifactId": "artifact-1"}, "operator", "cmd-1")
        explanation = result["explanation"]
        self.assertIsInstance(explanation, dict)
        self.assertEqual(explanation["artifactId"], "artifact-1")
        self.assertEqual(explanation["predicts"][0]["predicate"],
                         "repairs.single_file_bug")
        self.assertTrue(explanation["wouldDemote"])

    def test_the_command_no_longer_returns_an_empty_explanation(self) -> None:
        result = self.service._cmd_ExplainArtifact(
            "run-1", {"artifactId": "artifact-1"}, "operator", "cmd-1")
        self.assertNotEqual(result["explanation"], "")

    def test_a_missing_artifact_id_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            self.service._cmd_ExplainArtifact("run-1", {}, "operator", "cmd-1")

    def test_an_unparseable_claim_is_skipped_not_guessed(self) -> None:
        service = RuntimeService(self.inbox, claims=[{"id": "broken"}, claim_wire()])
        result = service._cmd_ExplainArtifact(
            "run-1", {"artifactId": "artifact-1"}, "operator", "cmd-1")
        self.assertEqual(len(result["explanation"]["predicts"]), 1)


if __name__ == "__main__":
    unittest.main()
