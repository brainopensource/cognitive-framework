from __future__ import annotations

import io
import json
import unittest
from typing import Any

from vanguard.packages.adapters.stores.ledger_jsonl import export_jsonl, import_jsonl
from vanguard.packages.domain.artifacts.skill_index import (
    MAX_SKILL_INDEX_CHARS,
    SkillIndexError,
    format_skill_index,
    parse_skill_card,
)
from vanguard.packages.domain.ledger.coding_session import project_coding_session
from vanguard.packages.domain.ledger.events import parse_event_envelope


def _envelope(seq: str, kind: str, fields: dict[str, Any], event_id: str) -> Any:
    raw = {
        "schemaVersion": "vg.4",
        "eventId": event_id,
        "scope": "episode",
        "runId": "run-001",
        "episodeId": "ep-001",
        "seq": seq,
        "occurredAt": "2026-08-15T00:00:00.000Z",
        "recordedAt": "2026-08-15T00:00:00.000Z",
        "principal": "agent-alpha",
        "principalRole": "episode",
        "tenantId": "tenant-corp",
        "ownerId": "owner-alice",
        "confidentiality": "internal",
        "retentionClass": "standard",
        "trainability": "prohibited",
        "redactionStatus": "none",
        "payload": {"kind": kind, **fields},
    }
    return parse_event_envelope(raw)


class TestCodingSessionProjection(unittest.TestCase):
    def test_projects_turns_verbs_denials_and_optional_cache_miss(self) -> None:
        digest = "sha256:" + ("a" * 64)
        events = [
            _envelope("0", "EpisodeStarted", {"taskSpec": {"name": "fix"}}, "018f1111-1111-7000-8000-000000000001"),
            _envelope(
                "1",
                "ProposalProduced",
                {"operatorId": "op-1", "proposalDigest": digest, "toolCalls": [{"name": "fs.read"}]},
                "018f1111-1111-7000-8000-000000000002",
            ),
            _envelope(
                "2",
                "ProposalProduced",
                {
                    "operatorId": "op-1",
                    "proposalDigest": digest,
                    "toolCalls": [{"name": "patch.apply"}],
                    "cacheMiss": True,
                    "deadEnds": ["tried wrong file"],
                },
                "018f1111-1111-7000-8000-000000000003",
            ),
            _envelope(
                "3",
                "AuthorizationDenied",
                {"reason": "privileged without approval", "action": "proc.exec"},
                "018f1111-1111-7000-8000-000000000004",
            ),
            _envelope("4", "EpisodeCompleted", {"outcome": "abandoned"}, "018f1111-1111-7000-8000-000000000005"),
        ]
        session = project_coding_session(events)
        self.assertEqual(session["schema"], "vg.coding-session.v1")
        self.assertEqual(session["turnCount"], 2)
        self.assertEqual(session["turns"][0]["verbs"], ["fs.read"])
        self.assertEqual(session["turns"][1]["verbs"], ["patch.apply"])
        self.assertEqual(session["denialCount"], 1)
        self.assertEqual(session["cacheMissCount"], 1)
        self.assertEqual(session["deadEnds"], ["tried wrong file"])
        self.assertEqual(session["outcome"], "abandoned")
        self.assertTrue(session["stateDigest"].startswith("sha256:"))

    def test_round_trip_jsonl_does_not_invent_compact_events(self) -> None:
        events = [
            _envelope("0", "EpisodeStarted", {"taskSpec": {"name": "x"}}, "018f1111-1111-7000-8000-000000000011"),
            _envelope("1", "EpisodeCompleted", {"outcome": "resolved"}, "018f1111-1111-7000-8000-000000000012"),
        ]
        buf = io.StringIO()
        export_jsonl(events, buf)
        buf.seek(0)
        session = project_coding_session(import_jsonl(buf))
        self.assertEqual(session["turnCount"], 0)
        self.assertEqual(session["cacheMissCount"], 0)
        self.assertEqual(session["compactCount"], 0)


class TestSkillIndex(unittest.TestCase):
    def test_omits_cards_that_do_not_fit_the_ceiling(self) -> None:
        cards = [
            parse_skill_card({
                "id": "pytest-green",
                "name": "Get pytest green",
                "description": "Run allowlisted pytest.",
                "bodyPath": "skills/pytest-green.md",
            }),
            parse_skill_card({
                "id": "huge",
                "name": "Huge",
                "description": "x" * 200,
                "bodyPath": "skills/huge.md",
            }),
        ]
        text = format_skill_index(cards, ceiling=120)
        self.assertIn("pytest-green", text)
        self.assertNotIn("huge", text)
        self.assertLessEqual(len(text), 120)
        self.assertLessEqual(MAX_SKILL_INDEX_CHARS, 4000)

    def test_rejects_incomplete_cards(self) -> None:
        with self.assertRaises(SkillIndexError):
            parse_skill_card({"id": "x", "name": "n"})


if __name__ == "__main__":
    unittest.main()
