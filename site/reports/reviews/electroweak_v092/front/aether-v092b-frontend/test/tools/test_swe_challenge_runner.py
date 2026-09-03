"""Contract tests for the checkout-independent SWE benchmark harness."""

from __future__ import annotations

import tempfile
import unittest
import hashlib
import signal
import subprocess
from unittest.mock import patch
import json
from pathlib import Path

from tools.runners.run_swe_challenge import (
    SMOKE_CHALLENGES,
    WORKER_PROTOCOL,
    TaskContext,
    _decode_worker_payload,
    _benchmark_identity,
    _changed_files,
    _diagnose_result,
    _execute_runtime_in_child,
    _execution_deadline,
    _enrich_result,
    _snapshot_digest,
    get_diff_size,
    setup_challenge,
)


class SweChallengeRunnerTests(unittest.TestCase):
    def test_worker_protocol_decodes_runtime_truth(self) -> None:
        payload = {
            "protocol": WORKER_PROTOCOL,
            "terminal": "completed",
            "detail": "done",
            "instrument_error": "",
            "telemetry": {
                "turns": 2,
                "prompt_tokens": 11,
                "completion_tokens": 7,
                "usd_micros": 13,
            },
            "trajectory": {"run_id": "run-1"},
        }
        outcome = _decode_worker_payload(json.dumps(payload))
        self.assertEqual(outcome.terminal, "completed")
        self.assertEqual(outcome.telemetry.total_tokens, 18)
        self.assertEqual(outcome.trajectory, {"run_id": "run-1"})

    def test_worker_protocol_rejects_non_json_output(self) -> None:
        outcome = _decode_worker_payload("provider log, not protocol JSON")
        self.assertEqual(outcome.terminal, "instrument_error")
        self.assertEqual(outcome.instrument_error, "worker_invalid_json")

    def test_parent_kills_hung_worker_and_returns_typed_instrument_error(self) -> None:
        class HangingWorker:
            pid = 123456789
            returncode = None

            def communicate(self, *args: object, **kwargs: object) -> tuple[str, str]:
                if "timeout" in kwargs:
                    raise subprocess.TimeoutExpired("worker", 0.01)
                return "", ""

        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.runners.run_swe_challenge.subprocess.Popen", return_value=HangingWorker()
        ), patch("tools.runners.run_swe_challenge.os.killpg") as killpg:
            task = TaskContext(brief="test", repo_path=Path(temp))
            outcome = _execute_runtime_in_child(
                task, "test/model", Path(temp) / "events.sqlite3", Path(temp) / "blobs", 0.01,
            )
        self.assertEqual(outcome.terminal, "instrument_error")
        self.assertEqual(outcome.instrument_error, "worker_timeout")
        killpg.assert_called_once_with(123456789, signal.SIGKILL)

    def test_execution_deadline_rejects_non_positive_values(self) -> None:
        with self.assertRaises(ValueError):
            with _execution_deadline(0):
                pass

    def test_execution_deadline_interrupts_a_stuck_operation(self) -> None:
        with self.assertRaises(TimeoutError):
            with _execution_deadline(0.01):
                while True:
                    pass

    def test_missing_runtime_result_is_an_instrument_failure(self) -> None:
        row = _enrich_result({"passed": False}, None)
        self.assertEqual(row["terminal"], "instrument_error")
        self.assertEqual(row["instrument_error"], "runtime_result_missing")
        self.assertFalse(row["passed"])

    def test_completed_episode_without_patch_has_explicit_task_diagnosis(self) -> None:
        self.assertEqual(
            _diagnose_result(True, [], True),
            "completed_without_source_patch",
        )

    def test_diagnosis_distinguishes_terminal_and_oracle_failures(self) -> None:
        self.assertEqual(
            _diagnose_result(False, [], False),
            "terminal_not_completed",
        )
        self.assertEqual(
            _diagnose_result(True, ["src/module.py"], False),
            "source_patch_failed_oracle",
        )
        self.assertEqual(
            _diagnose_result(True, ["src/module.py"], True),
            "completed_patch_passed_oracle",
        )

    def test_smoke_set_is_fixed_and_diverse(self) -> None:
        self.assertEqual(len(SMOKE_CHALLENGES), 12)
        self.assertEqual(len(set(SMOKE_CHALLENGES)), 12)
        self.assertEqual(SMOKE_CHALLENGES[0], "tier1_lru_ttl_cache")
        self.assertEqual(SMOKE_CHALLENGES[-1], "tier7_greenfield_kv_lsm_tree")

    def test_subject_snapshot_is_stable_and_patch_accounting_is_content_based(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = setup_challenge("tier1_ring_buffer_stream", root)
            digest = _snapshot_digest(baseline)

            (root / "ring" / "buffer.py").write_text(
                (root / "ring" / "buffer.py").read_text() + "\n# evaluated change\n",
                encoding="utf-8",
            )
            # Harness-generated oracle material is not part of the submitted
            # patch and therefore cannot contaminate the changed-file list.
            (root / "oracle_test.py").write_text("oracle", encoding="utf-8")
            (root / "ring" / "__pycache__").mkdir()
            (root / "ring" / "__pycache__" / "buffer.cpython-312.pyc").write_bytes(b"bytecode")

            self.assertEqual(digest, _snapshot_digest(dict(reversed(list(baseline.items())))))
            self.assertEqual(_changed_files(root, baseline), ["ring/buffer.py"])
            self.assertGreater(get_diff_size(root, baseline), 0)
            self.assertFalse((root / ".git").exists())

            identity = _benchmark_identity(
                "tier1_ring_buffer_stream", root, baseline, "provider/model",
            )
            self.assertEqual(identity["subject_digest"], digest)
            self.assertEqual(identity["provider"], "openrouter")
            self.assertEqual(identity["source_manifest"]["ring/buffer.py"],
                             hashlib.sha256(baseline["ring/buffer.py"]).hexdigest())
            self.assertEqual(identity["runtime_boundary"]["kind"], "child_process")
            self.assertEqual(identity["runtime_boundary"]["deadline_owner"], "parent")
            self.assertEqual(identity["run_timeout_seconds"], 300.0)


if __name__ == "__main__":
    unittest.main()
