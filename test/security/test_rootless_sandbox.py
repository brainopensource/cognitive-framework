from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.sandbox.rootless import RootlessSandboxRunner, _Invocation
from vanguard.packages.ports.sandbox import publication_decision


class ScriptedRunner(RootlessSandboxRunner):
    def __init__(self, workspace: Path, evaluator: Path, outcomes: list[_Invocation]) -> None:
        super().__init__(
            workspace,
            evaluator_bundle=evaluator,
            attested_at="2026-08-15T12:00:00.000Z",
        )
        self.outcomes = outcomes
        self.commands: list[tuple[str, ...]] = []

    def _run_isolated(self, argv):
        self.commands.append(tuple(argv))
        return self.outcomes.pop(0)

    def _runtime_version(self) -> str:
        return "bubblewrap 0.9.0"


class RootlessSandboxTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.workspace = root / "workspace"
        self.evaluator = root / "evaluator" / "bundle"
        self.workspace.mkdir()
        self.evaluator.parent.mkdir()
        self.evaluator.write_text("sealed evaluator instructions", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_probes_record_mount_egress_syscall_and_exclude_evaluator(self) -> None:
        runner = ScriptedRunner(
            self.workspace,
            self.evaluator,
            [
                _Invocation(0, b"", b""),  # evaluator path is unreadable
                _Invocation(1, b"", b"network unreachable"),
                _Invocation(1, b"", b"operation not permitted"),
                _Invocation(0, b"worker output", b""),
            ],
        )
        result = runner.execute(("/bin/sh", "-c", "printf worker"))

        self.assertTrue(result.ok)
        report = result.value.containment
        self.assertTrue(report.verified)
        self.assertEqual([probe.kind for probe in report.startup_probes], ["mount", "egress", "syscall"])
        self.assertTrue(all(probe.verified for probe in report.startup_probes))
        prefix = " ".join(runner._runtime_prefix())
        self.assertNotIn(str(self.evaluator), prefix)
        self.assertIn("/workspace", report.writable_mounts)
        self.assertTrue(publication_decision(report).ok)

    def test_runtime_startup_failure_is_reported_and_blocks_publication(self) -> None:
        failed = _Invocation(126, b"", b"namespace unavailable", started=False)
        runner = ScriptedRunner(self.workspace, self.evaluator, [failed, failed, failed, failed])

        report = runner.execute(("/bin/true",)).value.containment

        self.assertFalse(report.verified)
        self.assertFalse(report.contained)
        self.assertTrue(all(probe.observed == "perimeter-startup-failed" for probe in report.startup_probes))
        decision = publication_decision(report)
        self.assertFalse(decision.ok)
        self.assertEqual(decision.error.kind, "denied")

    def test_host_probe_never_claims_containment_when_bubblewrap_is_denied(self) -> None:
        runner = RootlessSandboxRunner(
            self.workspace,
            evaluator_bundle=self.evaluator,
            timeout_seconds=1,
            attested_at="2026-08-15T12:00:00.000Z",
        )
        result = runner.execute(("/bin/true",))
        self.assertTrue(result.ok)
        if not all(probe.verified for probe in result.value.containment.startup_probes):
            self.assertFalse(result.value.containment.verified)
            self.assertFalse(publication_decision(result.value.containment).ok)


if __name__ == "__main__":
    unittest.main()
