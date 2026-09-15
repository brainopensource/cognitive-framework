"""T-137 falsifier — approval-path probe attributes, and does not repair.

DIR-P / RUN-12 / RUN-13. The probe must remain a valid instrument: session-bound
signed approval lands one write, denial/missing/stale/foreign/boolean approval
produce no unauthorized mutation, the unchanged public entrypoint is labeled
separately from the session-bound control, and first-seam attribution is retained.
Zero provider calls, zero USD. No production threshold change.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from benchmarks.diagnostics.approval_path_probe import (
    EXPECTED_WRITE,
    FIXTURE_DIR,
    FIXTURE_ID,
    PATH_PUBLIC,
    PATH_SESSION,
    SEAM_BOOLEAN,
    SEAM_DEFAULT_ALLOW,
    SEAM_EXPLICIT_DENIAL,
    SEAM_FOREIGN,
    SEAM_INSTRUMENT,
    SEAM_MISSING_APPROVER,
    SEAM_STALE,
    SEAM_VALID_SIGNED,
    SEAMS,
    first_seam,
    instrument_controls_passed,
    run_all,
)


PROBE_SOURCE = (
    Path(__file__).resolve().parents[2]
    / "benchmarks" / "diagnostics" / "approval_path_probe.py"
).read_text(encoding="utf-8")


class TestProbeShape(unittest.TestCase):
    def test_fixture_is_synthetic_and_not_a_holdout_member(self) -> None:
        self.assertTrue((FIXTURE_DIR / "TASK.md").is_file())
        self.assertTrue((FIXTURE_DIR / "test_oracle.py").is_file())
        self.assertEqual(FIXTURE_ID, "DX-APPROVAL")
        self.assertIn("diagnostics", FIXTURE_DIR.parts)
        self.assertNotIn("l2_thirty", FIXTURE_DIR.parts)
        self.assertNotIn("m8_heldout", FIXTURE_DIR.parts)

    def test_public_path_drives_unchanged_entrypoint(self) -> None:
        self.assertIn("from benchmarks.product_path import execute_product", PROBE_SOURCE)
        self.assertIn("execute_product(", PROBE_SOURCE)
        self.assertNotIn("ForgeFacade", PROBE_SOURCE)
        self.assertNotIn("baac", PROBE_SOURCE.lower())

    def test_session_bound_control_is_labeled_separately(self) -> None:
        self.assertIn(PATH_PUBLIC, PROBE_SOURCE)
        self.assertIn(PATH_SESSION, PROBE_SOURCE)
        self.assertIn("Runtime.execute_profiled", PROBE_SOURCE)
        self.assertIn("not a claim that the public CLI wires an operator", PROBE_SOURCE)

    def test_seam_vocabulary_is_stable(self) -> None:
        self.assertEqual(len(SEAMS), len(set(SEAMS)))
        for required in (
            SEAM_MISSING_APPROVER, SEAM_EXPLICIT_DENIAL, SEAM_BOOLEAN,
            SEAM_STALE, SEAM_FOREIGN, SEAM_VALID_SIGNED, SEAM_DEFAULT_ALLOW,
            SEAM_INSTRUMENT,
        ):
            self.assertIn(required, SEAMS)

    def test_probe_never_auto_approves_or_lowers_thresholds(self) -> None:
        self.assertNotIn("autonomous_approval=True", PROBE_SOURCE)
        self.assertNotIn("approval_required_above", PROBE_SOURCE)
        self.assertIn('"repairAuthorized": False', PROBE_SOURCE)


class TestApprovalPathMatrix(unittest.TestCase):
    """One matrix run. Product sources stay read-only."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="t137-test-")
        cls.packet = run_all(Path(cls._tmp.name))
        cls.cases = {row["label"]: row for row in cls.packet["traces"]}

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_instrument_controls_pass(self) -> None:
        from benchmarks.diagnostics import approval_path_probe as probe

        reconstructed = [probe.ProbeCase(
            label=row["label"],
            path=row["path"],
            interactive=row["interactive"],
            policy=row["policy"],
            approver_kind=row["approverKind"],
            mutated=row["mutated"],
            changed_files=tuple(row["changedFiles"]),
            preimage_digest=row["preimageDigest"],
            candidate_digest=row["candidateDigest"],
            oracle_digest=row["oracleDigest"],
            write_effects=row["writeEffects"],
            spent_usd_micros=row["spentUsdMicros"],
            terminal_outcome=row["terminalOutcome"],
            terminal_detail=row["terminalDetail"],
            run_id=row["runId"],
            ledger_kinds=tuple(row["ledgerKinds"]),
            seam=row["seam"],
        ) for row in self.packet["traces"]]
        self.assertTrue(instrument_controls_passed(reconstructed), self.packet["unresolved"])
        self.assertTrue(self.packet["controls"]["passed"], self.packet)

    def test_zero_usd_and_zero_provider_calls(self) -> None:
        self.assertEqual(self.packet["infrastructure"]["providerCalls"], 0)
        self.assertEqual(self.packet["infrastructure"]["spentUsdMicros"], 0)
        for row in self.packet["traces"]:
            self.assertIn(row["spentUsdMicros"], (None, 0), row["label"])

    def test_public_require_missing_is_the_cold_seam_and_does_not_mutate(self) -> None:
        row = self.cases["pub-require-missing"]
        self.assertEqual(row["path"], PATH_PUBLIC)
        self.assertTrue(row["interactive"])
        self.assertEqual(row["policy"], "require")
        self.assertEqual(row["approverKind"], "missing")
        self.assertFalse(row["mutated"], row)
        self.assertEqual(row["candidateDigest"], row["preimageDigest"])
        self.assertNotEqual(row["seam"], SEAM_DEFAULT_ALLOW, row)
        self.assertEqual(row["seam"], SEAM_MISSING_APPROVER, row)
        self.assertEqual(self.packet["firstSeam"], SEAM_MISSING_APPROVER)

    def test_session_bound_valid_signed_lands_one_write(self) -> None:
        row = self.cases["sess-require-valid"]
        self.assertEqual(row["path"], PATH_SESSION)
        self.assertTrue(row["mutated"], row)
        self.assertEqual(set(row["changedFiles"]), set(EXPECTED_WRITE), row)
        self.assertEqual(row["candidateDigest"], row["oracleDigest"], row)
        self.assertEqual(row["seam"], SEAM_VALID_SIGNED, row)
        self.assertEqual(len(row["changedFiles"]), 1, row)

    def test_denial_boolean_stale_foreign_and_missing_do_not_mutate(self) -> None:
        expected = {
            "sess-require-missing": SEAM_MISSING_APPROVER,
            "sess-require-deny": SEAM_EXPLICIT_DENIAL,
            "sess-require-boolean": SEAM_BOOLEAN,
            "sess-require-stale": SEAM_STALE,
            "sess-require-foreign": SEAM_FOREIGN,
        }
        for label, seam in expected.items():
            row = self.cases[label]
            self.assertEqual(row["path"], PATH_SESSION, label)
            self.assertFalse(row["mutated"], row)
            self.assertEqual(row["candidateDigest"], row["preimageDigest"], row)
            self.assertEqual(row["seam"], seam, row)

    def test_resume_does_not_duplicate_the_landed_write(self) -> None:
        resume = self.packet["resume"]
        self.assertFalse(resume.get("skipped"), resume)
        self.assertFalse(resume.get("duplicated"), resume)
        if "error" not in resume:
            self.assertEqual(resume["preResumeDigest"], resume["postResumeDigest"], resume)
            self.assertEqual(resume["postResumeDigest"], resume["oracleDigest"], resume)

    def test_packet_retains_subject_config_and_trace_digests(self) -> None:
        for key in ("subjectDigest", "configDigest", "traceDigest", "firstSeam"):
            self.assertTrue(self.packet.get(key), key)
        self.assertTrue(str(self.packet["subjectDigest"]).startswith("sha256:"))
        self.assertEqual(self.packet["config"]["repairAuthorized"], False)
        self.assertIn("entrypoint.execute", self.packet["subject"]["publicRoute"])
        self.assertIn("execute_profiled", self.packet["subject"]["sessionRoute"])

    def test_first_seam_retains_evidence_and_does_not_authorize_repair(self) -> None:
        row = self.cases["pub-require-missing"]
        self.assertTrue(row.get("seamEvidence"), row)
        self.assertEqual(self.packet["firstSeam"], row["seam"])
        self.assertFalse(self.packet["config"]["repairAuthorized"])
        unresolved = " ".join(self.packet.get("unresolved") or []).lower()
        self.assertIn("not a repair", unresolved)
        self.assertNotRegex(
            PROBE_SOURCE,
            r"execute_product\([^)]*approver\s*=",
        )

    def test_first_seam_is_not_overwritten_by_later_cells(self) -> None:
        from benchmarks.diagnostics import approval_path_probe as probe

        reconstructed = []
        for row in self.packet["traces"]:
            reconstructed.append(probe.ProbeCase(
                label=row["label"],
                path=row["path"],
                interactive=row["interactive"],
                policy=row["policy"],
                approver_kind=row["approverKind"],
                mutated=row["mutated"],
                changed_files=tuple(row["changedFiles"]),
                preimage_digest=row["preimageDigest"],
                candidate_digest=row["candidateDigest"],
                oracle_digest=row["oracleDigest"],
                write_effects=row["writeEffects"],
                spent_usd_micros=row["spentUsdMicros"],
                terminal_outcome=row["terminalOutcome"],
                terminal_detail=row["terminalDetail"],
                run_id=row["runId"],
                ledger_kinds=tuple(row["ledgerKinds"]),
                seam=row["seam"],
            ))
        self.assertEqual(
            first_seam(reconstructed, controls_ok=True),
            self.cases["pub-require-missing"]["seam"],
        )


if __name__ == "__main__":
    unittest.main()
