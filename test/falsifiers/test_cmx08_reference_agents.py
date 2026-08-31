"""CMX-08: Reference Agent Portfolio (Reviewer, Tutor, Research) falsifiers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.agency.episode.admission_gate import AdmissionGate, VerificationReceipt
from vanguard.packages.runtime.app_service import ApplicationService
from vanguard.packages.runtime.compose import Runtime

ROOT = Path(__file__).resolve().parents[2]
MANIFESTS_DIR = ROOT / "vanguard/packages/agency/manifests"


class TestCMX08ReferenceAgents(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        (self.workspace / "README.md").write_text("# Project\nDocumentation here.\n")
        (self.workspace / "src").mkdir()
        (self.workspace / "src/calc.py").write_text("def add(a, b):\n    return a + b\n")
        (self.workspace / "tests").mkdir()
        (self.workspace / "tests/test_calc.py").write_text(
            "import unittest\nfrom src.calc import add\n\nclass TestCalc(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(1, 2), 3)\n\nif __name__ == '__main__':\n    unittest.main()\n"
        )
        self.service = ApplicationService(workspace=self.workspace)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_all_reference_manifests_exist_in_registry(self) -> None:
        registry_data = json.loads((MANIFESTS_DIR / "registry.json").read_text(encoding="utf-8"))
        names = {entry["name"] for entry in registry_data["manifests"]}
        required = {
            "vg-code-default",
            "vg-code-fast",
            "vg-code-balanced",
            "vg-code-max",
            "vg-code-critic-reviser",
            "vg-tutor-v090-v1-read-search",
            "vg-research-minimal",
        }
        self.assertTrue(required.issubset(names), f"Missing manifests: {required - names}")

    def test_tutor_agent_is_strictly_read_only(self) -> None:
        tutor_manifest_path = MANIFESTS_DIR / "vg-tutor-v090-v1-read-search/manifest.json"
        manifest_data = json.loads(tutor_manifest_path.read_text(encoding="utf-8"))
        verbs = {cap["verb"] for cap in manifest_data["capabilities"]}
        self.assertEqual(verbs, {"fs.read", "fs.search"})
        self.assertNotIn("patch.apply", verbs)
        self.assertNotIn("fs.write", verbs)
        self.assertNotIn("proc.exec", verbs)

    def test_tutor_admission_uses_read_only_policy(self) -> None:
        gate = AdmissionGate()
        verdict = gate.evaluate(
            preset_name="vg-tutor-v090-v1-read-search",
            changed_files=(),
            proposal={"kind": "finish"},
            task_requirements_satisfied=True,
        )
        self.assertTrue(verdict.admissible)

    def test_tutor_admission_rejects_unsatisfied_requirements(self) -> None:
        gate = AdmissionGate()
        verdict = gate.evaluate(
            preset_name="vg-tutor-v090-v1-read-search",
            changed_files=(),
            proposal={"kind": "finish"},
            task_requirements_satisfied=False,
        )
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "TASK_REQUIREMENTS_UNSATISFIED")

    def test_code_reviewer_cannot_approve_own_suggestions(self) -> None:
        reviewer_manifest_path = MANIFESTS_DIR / "vg-code-critic-reviser/manifest.json"
        self.assertTrue(reviewer_manifest_path.is_file())
        gate = AdmissionGate()
        # Reviewer attempting finish on a write task without valid test receipt fails
        verdict = gate.evaluate(
            preset_name="vg-code-critic-reviser",
            changed_files=["src/calc.py"],
            proposal={"kind": "finish"},
            inspected_files=["src/calc.py"],
            verification=None,
        )
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, "VERIFICATION_REQUIRED")

    def test_research_agent_is_read_only_and_contained(self) -> None:
        research_manifest_path = MANIFESTS_DIR / "vg-research-minimal/manifest.json"
        manifest_data = json.loads(research_manifest_path.read_text(encoding="utf-8"))
        verbs = {cap["verb"] for cap in manifest_data["capabilities"]}
        self.assertTrue(verbs.issubset({"fs.read", "fs.search", "research.read", "research.search"}))

    def test_reference_agents_execute_via_same_application_service(self) -> None:
        agents = [
            ("tutor", MANIFESTS_DIR / "vg-tutor-v090-v1-read-search/manifest.json"),
            ("research", MANIFESTS_DIR / "vg-research-minimal/manifest.json"),
            ("reviewer", MANIFESTS_DIR / "vg-code-critic-reviser/manifest.json"),
        ]
        for name, manifest_path in agents:
            result = self.service.run(
                brief=f"Run {name} task",
                manifest_path=manifest_path,
                profile_id="local",
                run_id=f"test-{name}-run",
                model_port="fake",
                max_turns=2,
            )
            self.assertEqual(result.run_id, f"test-{name}-run")
            self.assertTrue(result.outcome in ("completed", "incomplete", "abandoned", "complete"))
            status = self.service.status(f"test-{name}-run")
            self.assertEqual(status.run_id, f"test-{name}-run")


if __name__ == "__main__":
    unittest.main()
