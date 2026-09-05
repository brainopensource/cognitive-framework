"""T-93: evidence row schema and L1 twelve-task freeze."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from benchmarks.ladder.evidence import EvidenceError, append_row, suite_digest

ROOT = Path(__file__).resolve().parents[2]
L1 = ROOT / "benchmarks" / "ladder" / "l1_twelve" / "suite.json"


def _row(**overrides: object) -> dict:
    row = {
        "identity": {
            "subject_sha": "abc" * 8 + "0" * 16,
            "dirty_flag": False,
            "suite_digest": "sha256:" + "ab" * 32,
            "n": 12,
            "task_id": "L1-GF-01",
            "task_digest": "sha256:" + "cd" * 32,
            "oracle_digest": "sha256:" + "ef" * 32,
            "run_id": "run-1",
        },
        "arm": {
            "manifest_digest": "sha256:" + "11" * 32,
            "preset": "balanced",
            "model_id": "fake",
            "provider": "fake",
            "server_build": None,
            "gguf_digest": None,
            "quantization": None,
            "context_size": None,
            "sampling_digest": "sha256:" + "22" * 32,
            "prompt_digest": "sha256:" + "33" * 32,
            "tool_schema_digest": "sha256:" + "44" * 32,
        },
        "execution": {
            "evidence_label": "LIVE-LOCAL",
            "raw_response_digest": None,
            "valid_tool_calls": 1,
            "malformed_tool_calls": 0,
            "recovery_attempts": 0,
            "turns": 3,
            "time_to_first_valid_action_s": 0.4,
            "latency_s": 1.2,
        },
        "change": {
            "patch_digest": "sha256:" + "55" * 32,
            "postimage_digest": "sha256:" + "66" * 32,
            "files_changed": 1,
            "no_op": False,
        },
        "verification": {
            "tests_discovered": 3,
            "tests_executed": 3,
            "tests_passed": 3,
            "tests_failed": 0,
            "tamper_digest": "sha256:" + "77" * 32,
            "tamper_verdict": "clean",
        },
        "settlement": {
            "terminal_status": "abandoned",
            "disposition": "passed",
            "undeterminable_reason": None,
        },
        "economics": {
            "prompt_tokens": 10,
            "completion_tokens": 4,
            "cache_read_tokens": None,
            "cache_write_tokens": None,
            "cost_usd_micros": 12,
            "local_time_proxy_s": None,
        },
        "provenance": {
            "hypothesis_id": "control",
            "control_digest": None,
            "varied_dimension": None,
        },
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(row.get(key), dict):
            row[key] = {**row[key], **value}
        else:
            row[key] = value
    return row


class TestEvidenceRowSchema(unittest.TestCase):
    def test_l1_freezes_twelve_tasks_across_three_classes(self) -> None:
        suite = json.loads(L1.read_text(encoding="utf-8"))
        ids = [item for group in suite["classes"].values() for item in group]
        self.assertEqual(len(ids), 12)
        self.assertEqual(len(set(ids)), 12)
        self.assertEqual(len(suite["classes"]["greenfield"]), 4)
        self.assertEqual(len(suite["classes"]["single_file_bug"]), 4)
        self.assertEqual(len(suite["classes"]["data_cli"]), 4)
        self.assertTrue(suite_digest(ids).startswith("sha256:"))

    def test_incomplete_row_is_refused(self) -> None:
        row = _row()
        del row["identity"]["oracle_digest"]
        with self.assertRaises(EvidenceError):
            append_row([], row)

    def test_completed_without_patch_is_refused(self) -> None:
        row = _row(settlement={"terminal_status": "completed"}, change={"patch_digest": None})
        with self.assertRaises(EvidenceError):
            append_row([], row)

    def test_mixed_replay_and_live_table_is_refused(self) -> None:
        table = append_row([], _row())
        replay = _row(execution={"evidence_label": "REPLAY"})
        with self.assertRaises(EvidenceError):
            append_row(table, replay)

    def test_undeterminable_requires_a_reason(self) -> None:
        row = _row(settlement={"disposition": "undeterminable", "undeterminable_reason": None})
        with self.assertRaises(EvidenceError):
            append_row([], row)


if __name__ == "__main__":
    unittest.main()
