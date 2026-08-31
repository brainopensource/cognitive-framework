"""Auditing and Falsifier Tests for Wave 1 Implementation Review.

These tests independently verify the architectural invariants, contract completeness,
and defects identified in the Wave 1 review without modifying any existing production code or tests.
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from vanguard.packages.agency.episode.admission_gate import AdmissionGate, VerificationReceipt
from vanguard.packages.agency.episode.engine import EpisodeEngine
from vanguard.packages.agency.manifests.loader import ManifestLoader
from vanguard.packages.ports.index import DependencyEdge, IndexPort, RepositoryMap, Symbol, TestAssociation
from vanguard.packages.runtime.app_service import ApplicationService
from vanguard.packages.runtime.session import HarnessSession
from vanguard.packages.runtime.task_state import CodingTaskState


class TestWave1AuditFalsifiers(unittest.TestCase):
    """Independent falsifiers for Wave 1 architecture, contracts, and seams."""

    def test_completion_admitter_is_wired_for_coding_max_presets(self) -> None:
        """Falsifier: Coding Max can terminate without the pack admission gate."""
        session_source = inspect.getsource(HarnessSession)
        self.assertIn(
            "completion_admitter=",
            session_source,
        )

    def test_coding_max_presets_are_registered_in_manifests(self) -> None:
        """Falsifier: preset identities disappear from the production registry."""
        packs = ManifestLoader().list_available_packs()
        has_fast = "vg-code-fast" in packs
        has_balanced = "vg-code-balanced" in packs
        has_max = "vg-code-max" in packs

        self.assertTrue(
            has_fast and has_balanced and has_max,
        )

    def test_verify_index_port_and_adapter_contract(self) -> None:
        """Verify: IndexPort interface specifies dependencies, tests, and repo_map."""
        methods = {name for name, _ in inspect.getmembers(IndexPort, predicate=inspect.isfunction)}
        self.assertIn("index", methods)
        self.assertIn("files", methods)
        self.assertIn("symbols", methods)
        self.assertIn("dependencies", methods)
        self.assertIn("tests", methods)
        self.assertIn("repo_map", methods)

    def test_repo_map_toolkit_delegates_to_index_port(self) -> None:
        """Falsifier: pack-local repository scanning becomes a second index authority."""
        repo_map_path = Path("packs/code-default/toolkits/repo_map.py")
        self.assertTrue(repo_map_path.is_file())
        content = repo_map_path.read_text(encoding="utf-8")
        self.assertIn("FileRepoIndex", content)
        self.assertNotIn("_DEFINITIONS", content)
        self.assertNotIn("text[:budget]", content)

    def test_falsify_app_service_resume_clobbers_brief(self) -> None:
        """Falsifier: ApplicationService.resume overwrites brief and does not restore CodingTaskState."""
        app_service_source = inspect.getsource(ApplicationService.resume)
        self.assertIn('brief=f"Resume run {run_id}"', app_service_source)
        self.assertNotIn("CodingTaskState", app_service_source)

    def test_coding_task_state_invariants(self) -> None:
        """Verify CodingTaskState validation and digest determinism."""
        state = CodingTaskState(
            objective="fix buffer overflow",
            constraints=("no stdlib modifications",),
            plan=("localize bug", "apply patch", "run tests"),
            inspected_files=("src/buffer.py",),
            modified_files=("src/buffer.py",),
            verification_plan=("pytest test/test_buffer.py",),
            last_verification={"exit_code": 0, "executed_test_count": 5},
            next_action="complete",
            settled_effects=("patch.apply:src/buffer.py",),
            remaining_budgets={"usd_micros": 50000, "turns": 10},
        )
        data = state.to_canonical_dict()
        restored = CodingTaskState.from_mapping(data)
        self.assertEqual(state, restored)
        self.assertEqual(state.digest(), restored.digest())

        with self.assertRaises(ValueError):
            CodingTaskState("")

        with self.assertRaises(ValueError):
            CodingTaskState("test", remaining_budgets={"tokens": -1})


if __name__ == "__main__":
    unittest.main()
