"""BETA Wave 0: ApprovalResolved, Heartbeat, EvaluationListener on RuntimeService.

Write scope: `test/runtime/test_evaluation_*`. REQ-LEDGER-002, REQ-TRUST-001.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.domain.primitives.primitives import uuidv7
from vanguard.packages.runtime.governance.approvals import (
    ApprovalAuthority,
    ApprovalChallenge,
    OperatorSigner,
)
from vanguard.packages.runtime.service import RuntimeService, ServiceInboxStore


class RuntimeServiceLedgerWriter(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.inbox = ServiceInboxStore(Path(self._tempdir.name) / "service.db")
        self.signer = OperatorSigner(key_id="op-test")
        self.authority = ApprovalAuthority({"op-test": self.signer.public_bytes})
        self.service = RuntimeService(self.inbox, authority=self.authority)

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
        """A decision is recorded only when it verifies against its challenge.

        The decision is signed by the operator over the *issued* challenge.
        A placeholder signature -- which this test previously used -- now
        appends nothing, which is the point of the approval spine.
        """
        self._start("run-appr")
        challenge = ApprovalChallenge(
            approval_id="appr-1",
            process_id="proc-1",
            action="patch.apply",
            normalized_diff="--- a/x\n+++ b/x\n@@ -0,0 +1 @@\n+y\n",
            args_digest="sha256:" + "a" * 64,
            descriptor_digest="sha256:" + "b" * 64,
            principal="operator",
            expires_at="2099-08-18T12:00:00.000Z",
        )
        self.service.publish_event(
            "run-appr",
            {
                "eventId": uuidv7(),
                "runId": "run-appr",
                "principal": "runtime",
                "payload": {"kind": "ApprovalRequested", **challenge.payload()},
            },
        )
        before = len(self.service._load_events("run-appr"))

        # A forged signature must append nothing at all.
        forged = dict(self.signer.approve(challenge, reviewer="operator").payload())
        forged["signature"] = "00" * 64
        res = self.service.execute_command(self._resolve_frame("cmd-forged", forged))
        self.assertEqual(res["receipt"]["error"]["code"], "permission_denied")
        self.assertEqual(len(self.service._load_events("run-appr")), before)

        # The genuine decision is recorded.
        decision = self.signer.approve(challenge, reviewer="operator")
        res = self.service.execute_command(
            self._resolve_frame("cmd-appr-1", dict(decision.payload()))
        )
        self.assertEqual(res.get("frameType"), "receipt", res)
        self.assertEqual(res["receipt"]["status"], "completed")

        events = [
            evt
            for evt in self.service._load_events("run-appr")
            if evt.get("payload", {}).get("kind") == "ApprovalResolved"
        ]
        self.assertEqual(len(events), 1)
        recorded = events[0]["payload"]["decision"]
        self.assertEqual(recorded["approvalId"], "appr-1")
        self.assertEqual(recorded["resolution"], "approved")
        self.assertEqual(recorded["signature"], decision.signature)

    def _resolve_frame(self, command_id: str, decision: dict) -> dict:
        return {
            "version": "vg.4",
            "frameType": "command",
            "frameId": uuidv7(),
            "command": {
                "name": "ResolveApproval",
                "commandId": command_id,
                "idempotencyKey": f"idem-{command_id}",
                "runId": "run-appr",
                "actor": "operator",
                "payload": {"decision": decision},
            },
        }

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
