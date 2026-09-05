"""MS-INSTRUMENT / T-23 falsifiers: patch identity, missingness, dirty subject, BAAC, arms."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from benchmarks.baac.cli import discover_challenges
from benchmarks.baac.lib.report import ChallengeExecutionResult, classify_attribution
from benchmarks.baac.lib.oracle import OracleResult
from benchmarks.baac.membership import (
    BAAC_CHALLENGE_SCHEMA,
    BAACMembershipError,
    enumerate_baac_challenges,
)
from benchmarks.coding_max_report import (
    CODING_MAX_ARMS,
    CodingMaxArmError,
    write_coding_max_report,
)
from benchmarks.protocols import (
    RESULT_DISPOSITIONS,
    BenchmarkReceipt,
    BenchmarkSubmission,
    BenchmarkTask,
    DirtySubjectError,
    classify_disposition,
    require_clean_subject,
    write_b20_report,
)
from vanguard.packages.apps.coding_max.facade import CodingMaxFacade


_REPO = Path(__file__).resolve().parents[2]
_SUBJECT = "86142175fcab03ff93727ad1f5b336b22e01c66b"
_PATCH = "sha256:" + ("ab" * 32)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "instrument-test",
        "GIT_AUTHOR_EMAIL": "instrument@test.invalid",
        "GIT_COMMITTER_NAME": "instrument-test",
        "GIT_COMMITTER_EMAIL": "instrument@test.invalid",
    }
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )


def _init_clean_repo(root: Path) -> None:
    _git(root, "init")
    (root / "README").write_text("clean\n", encoding="utf-8")
    _git(root, "add", "README")
    _git(root, "commit", "-m", "init")


class TestPatchIdentityT24(unittest.TestCase):
    def test_pass_row_without_patch_digest_is_refused(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            write_b20_report(
                None,
                subject_sha=_SUBJECT,
                results=[{"id": "01_task", "status": "PASS"}],
            )
        self.assertIn("patch", str(ctx.exception).lower())

    def test_pass_receipt_without_patch_digest_is_refused(self) -> None:
        task = BenchmarkTask("t1", "SWE-Bench Pro", "dev")
        submission = BenchmarkSubmission(task.digest, "diff --git a/x b/x", "m", "h")
        with self.assertRaises(ValueError) as ctx:
            BenchmarkReceipt(
                "SWE-Bench Pro", task.digest, submission.digest,
                "h", "m", "e", outcome="PASS", split="dev",
                subject_sha=_SUBJECT,
            )
        self.assertIn("patch", str(ctx.exception).lower())

    def test_pass_row_with_patch_digest_is_admitted(self) -> None:
        payload = write_b20_report(
            None,
            subject_sha=_SUBJECT,
            results=[{"id": "01_task", "status": "PASS", "patch_digest": _PATCH}],
        )
        self.assertEqual(payload["pass"], 1)
        self.assertEqual(payload["results"][0]["patch_digest"], _PATCH)
        self.assertEqual(payload["results"][0]["disposition"], "passed")


class TestMissingnessT25(unittest.TestCase):
    def test_disposition_vocabulary_is_closed(self) -> None:
        self.assertEqual(
            RESULT_DISPOSITIONS,
            frozenset({"passed", "failed", "undeterminable", "not_run"}),
        )

    def test_provider_error_is_not_task_fail(self) -> None:
        self.assertEqual(
            classify_disposition(status="FAIL", diagnosis="provider_error"),
            "undeterminable",
        )
        self.assertEqual(
            classify_disposition(status="FAIL", attribution="HARNESS_ERROR"),
            "undeterminable",
        )
        self.assertEqual(
            classify_disposition(status="FAIL", attribution="DATASET_INVALID"),
            "undeterminable",
        )

    def test_traceback_only_row_is_harness_error_not_fail(self) -> None:
        payload = write_b20_report(
            None,
            subject_sha=_SUBJECT,
            results=[{
                "id": "01_task",
                "status": "FAIL",
                "diagnosis": "Traceback (most recent call last):\n  File harness.py, line 1\nRuntimeError",
            }],
        )
        row = payload["results"][0]
        self.assertEqual(row["disposition"], "undeterminable")
        self.assertEqual(row["diagnosis"], "harness_error")
        self.assertNotEqual(row["status"], "FAIL")
        self.assertNotEqual(row["status"], "PASS")
        self.assertEqual(payload["pass"], 0)
        self.assertEqual(payload["missingness"]["undeterminable"], 1)
        self.assertEqual(payload["missingness"]["failed"], 0)

    def test_dataset_invalid_attribution_is_not_fail(self) -> None:
        missing = OracleResult(False, 1, "", "Oracle script missing", 0.0, error="Oracle script missing")
        attribution = classify_attribution(missing, "COMPLETED", 2, 8)
        self.assertEqual(attribution, "DATASET_INVALID")
        self.assertEqual(
            classify_disposition(status="FAIL", attribution=attribution),
            "undeterminable",
        )
        result = ChallengeExecutionResult(
            challenge_id="c1", tier="tier-1", scope="single", context_bracket="2K",
            preset="vg-code-max", model="m", mode="lam",
            status="UNDETERMINABLE", attribution="DATASET_INVALID",
            turns=0, prompt_tokens=0, completion_tokens=0, total_tokens=0,
            cost_usd=0.0, duration_seconds=0.0,
        )
        self.assertEqual(result.disposition, "undeterminable")
        self.assertNotEqual(result.status, "FAIL")
        self.assertNotEqual(result.status, "PASS")


class TestDirtySubjectT40(unittest.TestCase):
    def test_qualifying_run_on_dirty_tree_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _init_clean_repo(root)
            sha = require_clean_subject(root)
            self.assertTrue(sha)
            (root / "README").write_text("dirty\n", encoding="utf-8")
            with self.assertRaises(DirtySubjectError) as ctx:
                require_clean_subject(root)
            self.assertIn("dirty", str(ctx.exception).lower())


class TestBaacSchemaT41(unittest.TestCase):
    def test_task_md_directory_is_not_a_challenge_without_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            challenge = root / "tier-1" / "looks_like_a_task"
            challenge.mkdir(parents=True)
            (challenge / "TASK.md").write_text("# Task\n", encoding="utf-8")
            (challenge / "__pycache__").mkdir()
            self.assertEqual(enumerate_baac_challenges(root), ())

    def test_invalid_schema_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            challenge = root / "tier-1" / "broken"
            challenge.mkdir(parents=True)
            (challenge / "challenge.yaml").write_text("id: broken\n", encoding="utf-8")
            with self.assertRaises(BAACMembershipError):
                enumerate_baac_challenges(root)

    def test_schema_valid_manifest_is_admitted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            challenge = root / "tier-1" / "bench_ok"
            challenge.mkdir(parents=True)
            (challenge / "TASK.md").write_text("# Task\n", encoding="utf-8")
            (challenge / "challenge.yaml").write_text(
                "\n".join((
                    f"schema: {BAAC_CHALLENGE_SCHEMA}",
                    "id: bench_ok",
                    "name: Ok",
                    "scope: single",
                    "context_bracket: 2K",
                    "tier: tier-1",
                )) + "\n",
                encoding="utf-8",
            )
            found = enumerate_baac_challenges(root)
            self.assertEqual(tuple(path.name for path in found), ("bench_ok",))

    def test_live_baac_catalog_is_schema_valid(self) -> None:
        catalog = discover_challenges()
        self.assertGreaterEqual(len(catalog), 9)
        enumerated = enumerate_baac_challenges(_REPO / "benchmarks" / "baac" / "challenges")
        self.assertEqual({path.name for path in catalog}, {path.name for path in enumerated})


class TestCodingMaxArmsT23(unittest.TestCase):
    def test_product_arms_are_the_three_coding_max_presets(self) -> None:
        self.assertEqual(
            CODING_MAX_ARMS,
            frozenset({"vg-code-fast", "vg-code-balanced", "vg-code-max"}),
        )
        self.assertEqual(
            frozenset(f"vg-code-{preset}" for preset in CodingMaxFacade.PRESETS),
            CODING_MAX_ARMS,
        )

    def test_forge_and_chimera_scores_cannot_enter_coding_max_report(self) -> None:
        with self.assertRaises(CodingMaxArmError):
            write_coding_max_report(
                None,
                subject_sha=_SUBJECT,
                arms=["vg-code-max", "vg-1-forge"],
                results=[{"id": "01_task", "status": "PASS", "patch_digest": _PATCH, "harness": "vg-code-max"}],
            )
        with self.assertRaises(CodingMaxArmError):
            write_coding_max_report(
                None,
                subject_sha=_SUBJECT,
                arms=["vg-code-max"],
                results=[{
                    "id": "01_task",
                    "status": "PASS",
                    "patch_digest": _PATCH,
                    "harness": "vg-chimera-v1",
                }],
            )

    def test_product_arm_report_is_accepted(self) -> None:
        payload = write_coding_max_report(
            None,
            subject_sha=_SUBJECT,
            arms=["fast", "vg-code-balanced", "max"],
            results=[{
                "id": "01_task",
                "status": "PASS",
                "patch_digest": _PATCH,
                "harness": "vg-code-fast",
            }],
        )
        self.assertEqual(payload["arms"], ["vg-code-fast", "vg-code-balanced", "vg-code-max"])
        self.assertEqual(payload["results"][0]["disposition"], "passed")

    def test_historical_sota_prereg_is_not_a_coding_max_report(self) -> None:
        prereg = json.loads((_REPO / "benchmarks" / "sota_preregistration.json").read_text(encoding="utf-8"))
        with self.assertRaises(CodingMaxArmError):
            write_coding_max_report(
                None,
                subject_sha=_SUBJECT,
                arms=prereg["arms"],
                results=[],
            )


if __name__ == "__main__":
    unittest.main()
