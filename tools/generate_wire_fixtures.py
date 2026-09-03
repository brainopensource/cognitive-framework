#!/usr/bin/env python3
"""Generate Canonical Golden Wire Contract Fixtures for Python & TypeScript tests.

Produces:
1. Valid command frames for all 11 RuntimeService commands.
2. Malformed / negative command frames (testing invalid_request, incompatible_version, etc.).
3. Receipt and Event envelope samples.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "test" / "fixtures" / "wire_contracts"


def create_fixtures():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    valid_dir = FIXTURES_DIR / "valid"
    invalid_dir = FIXTURES_DIR / "invalid"
    valid_dir.mkdir(parents=True, exist_ok=True)
    invalid_dir.mkdir(parents=True, exist_ok=True)

    # 1. Valid Commands
    valid_commands = {
        "StartRun": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-001",
            "command": {
                "name": "StartRun",
                "commandId": "cmd-001",
                "idempotencyKey": "idem-001",
                "runId": "run-001",
                "actor": "operator",
                "payload": {
                    "manifestPath": "agency/manifests/vg-code-default",
                    "repoPath": "/tmp/workspace",
                    "brief": "Fix issue #42",
                    "profileId": "prof-default",
                },
            },
        },
        "GetRun": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-002",
            "command": {
                "name": "GetRun",
                "commandId": "cmd-002",
                "idempotencyKey": "idem-002",
                "runId": "run-001",
                "actor": "operator",
                "payload": {"expectedSeq": 5},
            },
        },
        "ListRuns": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-003",
            "command": {
                "name": "ListRuns",
                "commandId": "cmd-003",
                "idempotencyKey": "idem-003",
                "actor": "operator",
                "payload": {"limit": 10, "offset": 0},
            },
        },
        "StreamEvents": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-004",
            "command": {
                "name": "StreamEvents",
                "commandId": "cmd-004",
                "idempotencyKey": "idem-004",
                "runId": "run-001",
                "actor": "operator",
                "payload": {"afterSeq": 10},
            },
        },
        "Cancel": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-005",
            "command": {
                "name": "Cancel",
                "commandId": "cmd-005",
                "idempotencyKey": "idem-005",
                "runId": "run-001",
                "actor": "operator",
                "payload": {"reason": "User requested abort", "expectedSeq": 12},
            },
        },
        "Checkpoint": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-006",
            "command": {
                "name": "Checkpoint",
                "commandId": "cmd-006",
                "idempotencyKey": "idem-006",
                "runId": "run-001",
                "actor": "operator",
                "payload": {"reason": "Manual safety checkpoint"},
            },
        },
        "Resume": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-007",
            "command": {
                "name": "Resume",
                "commandId": "cmd-007",
                "idempotencyKey": "idem-007",
                "runId": "run-001",
                "actor": "operator",
                "payload": {"checkpointId": "chk-001", "expectedSeq": 15},
            },
        },
        "ResolveApproval": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-008",
            "command": {
                "name": "ResolveApproval",
                "commandId": "cmd-008",
                "idempotencyKey": "idem-008",
                "runId": "run-001",
                "actor": "operator",
                "payload": {
                    "decision": {
                        "approvalId": "app-001",
                        "resolution": "approved",
                        "reviewer": "operator-01",
                        "argsDigest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "descriptorDigest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "expiresAt": "2026-12-31T23:59:59Z",
                        "keyId": "key-operator-01",
                        "signature": "a" * 128,
                    }
                },
            },
        },
        "RecordCorrection": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-009",
            "command": {
                "name": "RecordCorrection",
                "commandId": "cmd-009",
                "idempotencyKey": "idem-009",
                "runId": "run-001",
                "actor": "operator",
                "payload": {
                    "correction": {
                        "correctionId": "corr-001",
                        "runId": "run-001",
                        "reasonCode": "logic_bug",
                        "scope": "local",
                        "author": "operator",
                        "recordedAt": "2026-08-31T20:00:00Z",
                    }
                },
            },
        },
        "ExplainArtifact": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-010",
            "command": {
                "name": "ExplainArtifact",
                "commandId": "cmd-010",
                "idempotencyKey": "idem-010",
                "runId": "run-001",
                "actor": "operator",
                "payload": {"artifactId": "art-001", "substrateProfile": "standard"},
            },
        },
        "GetCapabilities": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-011",
            "command": {
                "name": "GetCapabilities",
                "commandId": "cmd-011",
                "idempotencyKey": "idem-011",
                "actor": "operator",
                "payload": {},
            },
        },
    }

    for name, frame in valid_commands.items():
        p = valid_dir / f"{name.lower()}_command.json"
        p.write_text(json.dumps(frame, indent=2), encoding="utf-8")

    # 2. Invalid Negative Frames
    invalid_frames = {
        "bad_version": {
            "version": "0.1",
            "frameType": "command",
            "frameId": "frame-bad-1",
            "command": valid_commands["GetCapabilities"]["command"],
        },
        "unknown_command": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-bad-2",
            "command": {
                "name": "DeleteDatabase",
                "commandId": "cmd-bad",
                "idempotencyKey": "idem-bad",
                "actor": "operator",
                "payload": {},
            },
        },
        "missing_run_id": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-bad-3",
            "command": {
                "name": "StartRun",
                "commandId": "cmd-bad-3",
                "idempotencyKey": "idem-bad-3",
                "actor": "operator",
                "payload": {"manifestPath": "a", "repoPath": "b", "brief": "c"},
            },
        },
        "forbidden_run_id": {
            "version": "vg.4",
            "frameType": "command",
            "frameId": "frame-bad-4",
            "command": {
                "name": "ListRuns",
                "commandId": "cmd-bad-4",
                "idempotencyKey": "idem-bad-4",
                "runId": "should-not-be-here",
                "actor": "operator",
                "payload": {},
            },
        },
    }

    for name, frame in invalid_frames.items():
        p = invalid_dir / f"{name}.json"
        p.write_text(json.dumps(frame, indent=2), encoding="utf-8")

    print(f"Generated {len(valid_commands)} valid golden vectors in {valid_dir}")
    print(f"Generated {len(invalid_frames)} invalid negative vectors in {invalid_dir}")


if __name__ == "__main__":
    create_fixtures()
