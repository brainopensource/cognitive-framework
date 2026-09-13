"""T-94 / T-26a: false-completion veto, Wilson on LIVE-* rows, publication admission."""

from __future__ import annotations

import unittest

from benchmarks.ladder.control import ControlNotFrozen, load_preregistration
from benchmarks.ladder.evidence import EvidenceError
from benchmarks.ladder.metrics import (
    MetricVeto,
    canary_disposition,
    publish_control_report,
    score_metrics,
)
from test.benchmarks.test_evidence_row_schema import _row
from test.benchmarks.test_preregistration import FROZEN_SUBJECT, TASK_IDS, frozen_manifest


def _bound_row(manifest: dict, task_id: str, **overrides: object) -> dict:
    """One evidence row fully bound to ``manifest``."""
    arm = manifest["arm"]
    row = _row(
        identity={
            "subject_sha": manifest["subject_sha"],
            "suite_digest": manifest["suite_digest"],
            "n": len(manifest["suite"]["tasks"]),
            "task_id": task_id,
            "task_digest": manifest["suite"]["task_digests"][task_id],
            "oracle_digest": manifest["suite"]["oracle_digests"][task_id],
        },
        arm={
            "manifest_digest": arm["manifest_digest"],
            "preset": arm["preset"],
            "model_id": manifest["model_id"],
            "provider": arm["provider"],
            "sampling_digest": arm["sampling_digest"],
            "prompt_digest": arm["prompt_digest"],
            "tool_schema_digest": arm["tool_schema_digest"],
        },
        execution={"evidence_label": "LIVE-LOCAL"},
        settlement={"terminal_status": "abandoned", "disposition": "passed"},
    )
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(row.get(key), dict):
            row[key] = {**row[key], **value}
        else:
            row[key] = value
    return row


def _population(manifest: dict) -> list[dict]:
    return [_bound_row(manifest, task) for task in manifest["suite"]["tasks"]]


class TestMetricVeto(unittest.TestCase):
    def test_nonzero_false_completion_vetoes_the_gate(self) -> None:
        rows = [
            _row(settlement={"terminal_status": "completed", "disposition": "failed"},
                 change={"patch_digest": None}, verification={"tests_executed": 0}),
        ]
        with self.assertRaises(MetricVeto):
            score_metrics(rows)

    def test_wilson_excludes_replay_rows(self) -> None:
        live = _row(execution={"evidence_label": "LIVE-LOCAL"},
                    settlement={"disposition": "passed"})
        replay = _row(execution={"evidence_label": "REPLAY"},
                      settlement={"disposition": "passed"})
        metrics = score_metrics([live, replay])
        self.assertEqual(metrics["n_live_evaluated"], 1)
        self.assertEqual(metrics["n_live_passed"], 1)
        self.assertIsNotNone(metrics["wilson"])

    def test_zero_live_observations_do_not_claim_zero_risk(self) -> None:
        replay = _row(execution={"evidence_label": "REPLAY"},
                      settlement={"disposition": "passed"})
        metrics = score_metrics([replay])
        self.assertEqual(metrics["n_live_evaluated"], 0)
        self.assertIsNone(metrics["wilson"])
        self.assertEqual(
            canary_disposition(metrics=metrics, n_evaluable=0, record=frozen_manifest()),
            "UNDETERMINABLE",
        )

    def test_fixture_diagnostics_need_no_frozen_record(self) -> None:
        """RUN-02: pure metrics stay usable on replay data with no manifest."""
        rows = [_row(execution={"evidence_label": "REPLAY"}) for _ in range(3)]
        metrics = score_metrics(rows)
        self.assertEqual(metrics["n_rows"], 3)
        self.assertEqual(metrics["false_completion_rate"], 0.0)


class TestCanaryAdmission(unittest.TestCase):
    """A disposition is never derived from a caller-asserted freeze flag."""

    def test_unfrozen_control_is_invalid(self) -> None:
        self.assertEqual(
            canary_disposition(metrics=None, n_evaluable=30, record=load_preregistration()),
            "INVALID",
        )
        self.assertEqual(
            canary_disposition(metrics=None, n_evaluable=30, record=None),
            "INVALID",
        )

    def test_a_forged_freeze_cannot_buy_a_positive(self) -> None:
        manifest = frozen_manifest()
        metrics = score_metrics(_population(manifest))
        self.assertEqual(
            canary_disposition(metrics=metrics, n_evaluable=30, record=manifest),
            "POSITIVE",
        )
        for forgery in ({"subject_sha": None}, {"arm": {"workers": 8}}, {"model_id": None}):
            with self.subTest(str(forgery)):
                self.assertEqual(
                    canary_disposition(
                        metrics=metrics, n_evaluable=30, record=frozen_manifest(**forgery)),
                    "INVALID",
                )


class TestPublicationBoundary(unittest.TestCase):
    """T-26a: the entrypoint that would publish a report enforces the freeze."""

    def test_the_checked_in_unfrozen_record_cannot_be_scored(self) -> None:
        manifest = frozen_manifest()
        with self.assertRaises(ControlNotFrozen):
            publish_control_report(record=load_preregistration(), rows=_population(manifest))

    def test_a_missing_record_cannot_be_scored(self) -> None:
        manifest = frozen_manifest()
        with self.assertRaises(ControlNotFrozen):
            publish_control_report(record={}, rows=_population(manifest))

    def test_a_complete_bound_population_publishes(self) -> None:
        manifest = frozen_manifest()
        report = publish_control_report(record=manifest, rows=_population(manifest))
        self.assertEqual(report["disposition"], "POSITIVE")
        self.assertEqual(report["n_scheduled"], 30)
        self.assertEqual(report["n_evaluable"], 30)
        self.assertEqual(report["n_missing"], 0)
        self.assertEqual(report["subject_sha"], FROZEN_SUBJECT)
        self.assertEqual(report["metrics"]["false_completion_rate"], 0.0)

    def test_a_missing_slot_is_never_silently_dropped(self) -> None:
        manifest = frozen_manifest()
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=_population(manifest)[:29])

    def test_a_duplicate_task_attempt_is_refused(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)
        rows[5] = _bound_row(manifest, TASK_IDS[4])
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=rows)

    def test_an_unscheduled_task_cannot_be_topped_up(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)
        rows.append(_bound_row(manifest, TASK_IDS[0]) | {
            "identity": {**rows[0]["identity"], "task_id": "L2-EXTRA"}})
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=rows)

    def test_a_stale_or_mixed_subject_is_refused(self) -> None:
        manifest = frozen_manifest()
        stale = _population(manifest)
        for row in stale:
            row["identity"]["subject_sha"] = "dead" * 10
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=stale)

        mixed = _population(manifest)
        mixed[7]["identity"]["subject_sha"] = "dead" * 10
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=mixed)

    def test_a_mismatched_configuration_identity_is_refused(self) -> None:
        manifest = frozen_manifest()
        for group, field in (
            ("identity", "suite_digest"), ("identity", "task_digest"),
            ("identity", "oracle_digest"), ("arm", "model_id"),
            ("arm", "provider"), ("arm", "preset"), ("arm", "sampling_digest"),
            ("arm", "prompt_digest"), ("arm", "tool_schema_digest"),
            ("arm", "manifest_digest"),
        ):
            with self.subTest(f"{group}.{field}"):
                rows = _population(manifest)
                rows[2][group][field] = "sha256:" + "99" * 32
                with self.assertRaises(EvidenceError):
                    publish_control_report(record=manifest, rows=rows)

    def test_a_mismatched_denominator_is_refused(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)
        rows[3]["identity"]["n"] = 12
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=rows)

    def test_an_unknown_disposition_is_refused(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)
        rows[1]["settlement"]["disposition"] = "probably_fine"
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=rows)

    def test_replay_rows_cannot_publish_a_control_report(self) -> None:
        manifest = frozen_manifest()
        rows = [
            _bound_row(manifest, task, execution={"evidence_label": "REPLAY"})
            for task in manifest["suite"]["tasks"]
        ]
        report = publish_control_report(record=manifest, rows=rows)
        self.assertEqual(report["n_evaluable"], 0)
        self.assertEqual(report["disposition"], "UNDETERMINABLE")

    def test_false_completion_vetoes_a_frozen_population(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)
        rows[9] = _bound_row(
            manifest, TASK_IDS[9],
            settlement={"terminal_status": "completed", "disposition": "failed"},
            verification={"tests_executed": 0},
        )
        with self.assertRaises(MetricVeto):
            publish_control_report(record=manifest, rows=rows)

    def test_retained_missing_slots_yield_undeterminable_not_negative(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)
        for index in range(3):
            rows[index] = _bound_row(
                manifest, TASK_IDS[index],
                settlement={
                    "terminal_status": "abandoned",
                    "disposition": "undeterminable",
                    "undeterminable_reason": "provider timeout",
                },
            )
        report = publish_control_report(record=manifest, rows=rows)
        self.assertEqual(report["n_evaluable"], 27)
        self.assertEqual(report["n_missing"], 3)
        self.assertEqual(report["disposition"], "UNDETERMINABLE")

    def test_a_failing_but_complete_population_is_negative(self) -> None:
        manifest = frozen_manifest()
        rows = [
            _bound_row(manifest, task, settlement={"disposition": "failed"},
                       change={"patch_digest": "sha256:" + "55" * 32})
            for task in manifest["suite"]["tasks"]
        ]
        report = publish_control_report(record=manifest, rows=rows)
        self.assertEqual(report["disposition"], "NEGATIVE")
        self.assertEqual(report["n_evaluable"], 30)


if __name__ == "__main__":
    unittest.main()
