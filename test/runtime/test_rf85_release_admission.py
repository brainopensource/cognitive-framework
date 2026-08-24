"""RF-85 lane-A release admission and immutable run identity contracts."""

from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.evidence import Preregistration
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.root import _validate_release_inputs
from vanguard.packages.runtime.run_plan import RunPlan
from vanguard.packages.runtime.session import HarnessSession
from vanguard.packages.kernel.model import FailurePath, Occurrence


class _LiveModel:
    provider = "openrouter"
    mode = "live"


def _ports(*, model: object | None = None, report: object | None = None) -> object:
    environment = SimpleNamespace(containment_report=report)
    return SimpleNamespace(model=model or _LiveModel(), environment=environment)


def _report() -> object:
    return SimpleNamespace(
        verified=True, contained=True, runtime="bubblewrap-rootless",
        syscall_profile="deny-probed", resource_limits={}, startup_probes=(),
        attested_at="2026-08-24T00:00:00Z", visibility_mark="verified")


class TestRF85ReleaseAdmission(unittest.TestCase):
    def setUp(self) -> None:
        self.task = TaskContext(brief="fix it", repo_path=".")
        self.preregistration = dict(Preregistration(
            task_digest=digest_of({"task": self.task.brief}),
            oracle_id="oracle-v1", oracle_digest="sha256:oracle",
            evaluator_key_id="key-v1", evaluator_public_key="cHVibGlj",
            protocol="pytest-v1", subject_digest="sha256:subject",
            created_at="2026-08-24T00:00:00Z",
        ).to_wire())

    def test_release_requires_preregistration_before_first_event(self) -> None:
        with self.assertRaisesRegex(ValueError, "preregistration"):
            _validate_release_inputs(_ports(report=_report()), self.task, {})

    def test_release_rejects_task_changed_after_preregistration(self) -> None:
        changed = {**self.preregistration, "task_digest": "sha256:other"}
        with self.assertRaisesRegex(ValueError, "does not bind"):
            _validate_release_inputs(
                _ports(report=_report()), self.task, changed,
                expected_oracle="oracle-v1")

    def test_release_rejects_self_attested_preregistration_digest(self) -> None:
        changed = {**self.preregistration, "oracle_digest": "sha256:changed"}
        with self.assertRaisesRegex(ValueError, "digest does not match"):
            _validate_release_inputs(
                _ports(report=_report()), self.task, changed,
                expected_oracle="oracle-v1")

    def test_release_rejects_cassette_and_host_fallback(self) -> None:
        cassette = SimpleNamespace(provider="openrouter", mode="replay")
        with self.assertRaisesRegex(ValueError, "live non-fake"):
            _validate_release_inputs(
                _ports(model=cassette, report=_report()), self.task,
                self.preregistration, expected_oracle="oracle-v1")
        host = SimpleNamespace(verified=True, contained=True, runtime="host")
        with self.assertRaisesRegex(ValueError, "host sandbox fallback"):
            _validate_release_inputs(
                _ports(report=host), self.task, self.preregistration,
                expected_oracle="oracle-v1")

    def test_run_digest_binds_preregistration_but_not_correlation_ids(self) -> None:
        common = dict(
            composition_digest="sha256:dh", activation_digest="sha256:da",
            project_id="project", task_digest="sha256:task",
            preregistration_digest="sha256:pre", oracle="oracle-v1")
        first = RunPlan(run_id="run-a", episode_id="ep-a", **common)
        second = RunPlan(run_id="run-b", episode_id="ep-b", **common)
        altered = RunPlan(
            run_id="run-a", episode_id="ep-a",
            **{**common, "preregistration_digest": "sha256:changed"})
        self.assertEqual(first.run_digest, second.run_digest)
        self.assertNotEqual(first.run_digest, altered.run_digest)

    def test_undeterminable_recovery_never_becomes_success(self) -> None:
        session = object.__new__(HarnessSession)
        session.ports = SimpleNamespace(store=object())
        session.calls = []
        session.kernel = SimpleNamespace(
            dispatch=lambda *_args, **_kwargs: self.fail("physical effect repeated"))
        request = SimpleNamespace(idempotency_key="intent-open")
        recovered = SimpleNamespace(payload={
            "kind": "EffectReconciled", "status": "undeterminable",
            "occurrence": "undeterminable", "descriptorDigest": "sha256:d",
        })
        with patch(
            "vanguard.packages.runtime.session.RecoveryScanner.settled_effect",
            return_value=recovered,
        ):
            result = session.dispatch(request)
        self.assertEqual(result.failure, FailurePath.UNDETERMINABLE)
        self.assertEqual(result.outcome.occurrence, Occurrence.UNDETERMINABLE)
        self.assertNotEqual(result.outcome.status, "ok")


if __name__ == "__main__":
    unittest.main()
