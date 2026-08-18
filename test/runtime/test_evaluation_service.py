"""BETA Wave 0: ApprovalResolved, Heartbeat, EvaluationListener on RuntimeService.

Write scope: `test/runtime/test_evaluation_*`. REQ-LEDGER-002, REQ-TRUST-001.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.domain.primitives.primitives import uuidv7
from vanguard.packages.runtime.service import RuntimeService, ServiceInboxStore


class RuntimeServiceLedgerWriter(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.inbox = ServiceInboxStore(Path(self._tempdir.name) / "service.db")
        self.service = RuntimeService(self.inbox)

    def tearDown(self) -> None:
        self.inbox.close()
        self._tempdir.cleanup()

    def _start(self, run_id: str) -> None:
        frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "StartRun",
                "commandId": f"cmd-{run_id}",
                "idempotencyKey": f"idem-{run_id}",
                "runId": run_id,
                "actor": "operator",
                "payload": {
                    "manifestPath": "manifest.json",
                    "repoPath": ".",
                    "brief": "beta ledger writer",
                },
            },
        }
        res = self.service.execute_command(frame)
        self.assertEqual(res.get("frameType"), "receipt", res)

    def test_start_run_appends_heartbeat(self) -> None:
        self._start("run-hb")
        kinds = [evt["payload"]["kind"] for evt in self.inbox.get_events("run-hb")]
        self.assertIn("Heartbeat", kinds)

    def test_resolve_approval_appends_approval_resolved(self) -> None:
        self._start("run-appr")
        frame = {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "ResolveApproval",
                "commandId": "cmd-appr-1",
                "idempotencyKey": "idem-appr-1",
                "runId": "run-appr",
                "actor": "operator",
                "payload": {
                    "decision": {
                        "approvalId": "appr-1",
                        "resolution": "approved",
                        "reviewer": "operator",
                        "argsDigest": "sha256:" + "a" * 64,
                        "descriptorDigest": "sha256:" + "b" * 64,
                        "expiresAt": "2026-08-18T12:00:00.000Z",
                        "keyId": "op-test",
                        "signature": "sig-placeholder",
                    }
                },
            },
        }
        res = self.service.execute_command(frame)
        self.assertEqual(res.get("frameType"), "receipt", res)
        events = [evt for evt in self.inbox.get_events("run-appr")
                  if evt.get("payload", {}).get("kind") == "ApprovalResolved"]
        self.assertEqual(len(events), 1)
        decision = events[0]["payload"]["decision"]
        self.assertEqual(decision["approvalId"], "appr-1")
        self.assertEqual(decision["resolution"], "approved")

    def test_episode_completed_triggers_evaluation_requested(self) -> None:
        self._start("run-eval")
        now = "2026-08-18T00:00:00.000Z"
        self.service.publish_event(
            "run-eval",
            {
                "schemaVersion": "4.0.0",
                "eventId": "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c",
                "scope": "episode",
                "occurredAt": now,
                "recordedAt": now,
                "principal": "agent-1",
                "principalRole": "episode",
                "tenantId": "tenant-default",
                "ownerId": "owner-platform",
                "confidentiality": "internal",
                "retentionClass": "standard",
                "trainability": "prohibited",
                "redactionStatus": "none",
                "runId": "run-eval",
                "episodeId": "ep-eval-1",
                "traceId": "trace-1",
                "spanId": "span-1",
                "payload": {"kind": "EpisodeCompleted", "outcome": "resolved"},
            },
        )
        kinds = [evt["payload"]["kind"] for evt in self.inbox.get_events("run-eval")]
        self.assertIn("EpisodeCompleted", kinds)
        self.assertIn("EvaluationRequested", kinds)
        # Recursion-safe: EvaluationRequested does not spawn another request.
        self.assertEqual(kinds.count("EvaluationRequested"), 1)
