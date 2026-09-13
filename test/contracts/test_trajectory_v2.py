"""Contract tests and golden vectors for mhf.trajectory/1 and /2 (B-M4-03).

Validates:
1. Strict schema validation for /1 (frozen) and /2.
2. Golden vectors for /1 and /2.
3. Default emission of /2 by assemble_trajectory.
4. Conforming /1 emission on explicit request.
5. Dual-read in TrajectoryReader without synthesizing fake evidence.
6. Diffing across /2 variables (artifacts, provenance, reproducibility, capture).
7. Capture degradation handling.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

from test.fixtures.artifact_provenance_fixtures import (
    build_trajectory_v2_fixture,
    sample_artifact_index_entry,
    sample_cache_provenance,
    sample_capture_incomplete_state,
    sample_compaction_provenance,
    sample_complete_capture_state,
    sample_conforming_trajectory_v1,
    sample_conforming_trajectory_v2,
    sample_context_selection_provenance,
)
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.kernel.model import Event
from vanguard.packages.runtime.root import TaskContext
from vanguard.packages.agency.episode.state import RunTermination
from vanguard.packages.runtime.trajectory import (
    TRAJECTORY_OUTCOME_VALUES,
    assemble_trajectory,
    project_trajectory_outcome,
)
from vanguard.packages.runtime.trajectory_reader import (
    TrajectoryReader,
    diff_trajectories,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_V1 = json.loads((ROOT / "schemas" / "mhf" / "trajectory.schema.json").read_text(encoding="utf-8"))
SCHEMA_V2 = json.loads((ROOT / "schemas" / "mhf" / "trajectory_v2.schema.json").read_text(encoding="utf-8"))


def _validate_schema(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = []
    for req in schema.get("required", []):
        if req not in data:
            errors.append(f"missing required property: {req}")
    if schema.get("additionalProperties") is False:
        props = schema.get("properties", {})
        for k in data:
            if k not in props:
                errors.append(f"unexpected property: {k}")
    return errors


class TestTrajectoryV2Contract(unittest.TestCase):
    def test_historical_v1_golden_vector_conforms_to_strict_v1_schema(self) -> None:
        v1 = sample_conforming_trajectory_v1()
        self.assertEqual(v1["schema"], "mhf.trajectory/1")
        errs = _validate_schema(v1, SCHEMA_V1)
        self.assertEqual(errs, [])
        self.assertNotIn("artifacts", v1)
        self.assertNotIn("provenance", v1)
        self.assertNotIn("reproducibility_at_run_close", v1)

    def test_v2_golden_vector_conforms_to_v2_schema(self) -> None:
        v2 = sample_conforming_trajectory_v2()
        self.assertEqual(v2["schema"], "mhf.trajectory/2")
        errs = _validate_schema(v2, SCHEMA_V2)
        self.assertEqual(errs, [], f"v2 vector failed schema: {errs}")
        self.assertIn("artifacts", v2)
        self.assertIn("provenance", v2)
        self.assertIn("reproducibility_at_run_close", v2)
        self.assertIn("capture", v2)

    def test_assemble_trajectory_default_emits_v2(self) -> None:
        task = TaskContext(brief="run test", repo_path=ROOT, run_id="run-001", episode_id="ep-001")
        traj = assemble_trajectory(
            task=task,
            harness_digest="sha256:" + "0" * 64,
            terminal="completed",
            receipts=(),
            contexts=(),
            events=(),
            verdict=None,
        )
        self.assertEqual(traj["schema"], "mhf.trajectory/2")
        errs = _validate_schema(traj, SCHEMA_V2)
        self.assertEqual(errs, [])
        self.assertIn("artifacts", traj)
        self.assertIn("provenance", traj)
        self.assertIn("reproducibility_at_run_close", traj)

    def test_assemble_trajectory_with_explicit_v1_emits_conforming_v1(self) -> None:
        task = TaskContext(brief="run test", repo_path=ROOT, run_id="run-001", episode_id="ep-001")
        traj = assemble_trajectory(
            task=task,
            harness_digest="sha256:" + "0" * 64,
            terminal="completed",
            receipts=(),
            contexts=(),
            events=(),
            verdict=None,
            schema_version="mhf.trajectory/1",
        )
        self.assertEqual(traj["schema"], "mhf.trajectory/1")
        errs = _validate_schema(traj, SCHEMA_V1)
        self.assertEqual(errs, [])

    def test_trajectory_reader_dual_read(self) -> None:
        # Load /1
        t1_raw = sample_conforming_trajectory_v1()
        t1_loaded = TrajectoryReader.load(t1_raw)
        v1_vars = TrajectoryReader.extract_variables(t1_loaded)
        self.assertEqual(v1_vars["schema"], "mhf.trajectory/1")
        self.assertEqual(v1_vars["artifacts"], ())
        self.assertIsNone(v1_vars["provenance"])
        self.assertIsNone(v1_vars["reproducibility_at_run_close"])

        # Load /2
        t2_raw = sample_conforming_trajectory_v2()
        t2_loaded = TrajectoryReader.load(t2_raw)
        v2_vars = TrajectoryReader.extract_variables(t2_loaded)
        self.assertEqual(v2_vars["schema"], "mhf.trajectory/2")
        self.assertIsInstance(v2_vars["artifacts"], list)
        self.assertIsInstance(v2_vars["provenance"], dict)
        self.assertIsInstance(v2_vars["reproducibility_at_run_close"], dict)

    def test_diff_trajectories_detects_provenance_and_reproducibility_differences(self) -> None:
        t1 = build_trajectory_v2_fixture(run_id="run-1")
        t2 = build_trajectory_v2_fixture(run_id="run-2")
        diff_same = diff_trajectories(t1, t2)
        self.assertTrue(diff_same.match)

        # Mutate artifact index in t2
        t2_mut = dict(t2)
        t2_mut["artifacts"] = [sample_artifact_index_entry(artifact_id="diff-art", role="workspace_snapshot").to_dict()]
        diff_art = diff_trajectories(t1, t2_mut)
        self.assertFalse(diff_art.match)
        self.assertIn("artifacts", diff_art.differing_variables)

        # Mutate reproducibility in t2
        t2_repro = dict(t1)
        t2_repro["reproducibility_at_run_close"] = {
            **t1["reproducibility_at_run_close"],
            "values": {
                **t1["reproducibility_at_run_close"]["values"],
                "state_reconstruction": {"capability": "none", "verification": "unverified"},
            },
        }
        diff_rep = diff_trajectories(t1, t2_repro)
        self.assertFalse(diff_rep.match)
        self.assertIn("reproducibility_at_run_close", diff_rep.differing_variables)

    def test_capture_degradation_state(self) -> None:
        degraded = sample_conforming_trajectory_v2(
            capture_state=sample_capture_incomplete_state(reason="storage_disk_full")
        )
        self.assertEqual(degraded["capture"]["status"], "incomplete")
        self.assertFalse(degraded["capture"]["required"])
        self.assertEqual(degraded["capture"]["degradation_reason"], "storage_disk_full")


class TestTrajectoryOutcomeIsNeverFabricatedSuccess(unittest.TestCase):
    """NT-B04 / EW-9.1 on the benchmark writer axis, for /1 and /2 alike.

    Trajectories are what benchmark rows, evidence bundles and convergence
    baselines are folded from. `abstained` used to be written into this axis
    as `completed`, so a refusal read as a success everywhere downstream --
    the surface NT-B04 names explicitly beside the facade and the CLI mapper.

    Every assertion below is behavioural: it calls `assemble_trajectory` and
    reads the emitted payload. Restoring `"abstained": "completed"` in
    `_TRAJECTORY_OUTCOMES` fails these outright, at both schema versions and
    independently of each other.
    """

    def _assemble(self, terminal: object, schema_version: str) -> dict[str, Any]:
        task = TaskContext(brief="refusal probe", repo_path=ROOT,
                           run_id="run-abstain", episode_id="ep-abstain")
        return assemble_trajectory(
            task=task,
            harness_digest="sha256:" + "0" * 64,
            terminal=terminal,
            receipts=(),
            contexts=(),
            events=(),
            verdict=None,
            schema_version=schema_version,
        )

    # -- /1 -------------------------------------------------------------

    def test_v1_never_writes_abstention_as_completion(self) -> None:
        traj = self._assemble(RunTermination.ABSTAINED, "mhf.trajectory/1")
        self.assertEqual(traj["schema"], "mhf.trajectory/1")
        self.assertNotEqual(traj["outcome"], "completed")
        self.assertEqual(traj["outcome"], "aborted")
        self.assertEqual(_validate_schema(traj, SCHEMA_V1), [])

    def test_v1_still_writes_a_real_completion_as_completed(self) -> None:
        traj = self._assemble(RunTermination.COMPLETED, "mhf.trajectory/1")
        self.assertEqual(traj["outcome"], "completed")
        self.assertEqual(_validate_schema(traj, SCHEMA_V1), [])

    # -- /2 -------------------------------------------------------------

    def test_v2_never_writes_abstention_as_completion(self) -> None:
        traj = self._assemble(RunTermination.ABSTAINED, "mhf.trajectory/2")
        self.assertEqual(traj["schema"], "mhf.trajectory/2")
        self.assertNotEqual(traj["outcome"], "completed")
        self.assertEqual(traj["outcome"], "aborted")
        self.assertEqual(_validate_schema(traj, SCHEMA_V2), [])

    def test_v2_still_writes_a_real_completion_as_completed(self) -> None:
        traj = self._assemble(RunTermination.COMPLETED, "mhf.trajectory/2")
        self.assertEqual(traj["outcome"], "completed")
        self.assertEqual(_validate_schema(traj, SCHEMA_V2), [])

    # -- both, and the string form the ledger actually carries -----------

    def test_the_two_schemas_agree_on_every_termination(self) -> None:
        """A refusal cannot be a success in one schema and not the other."""
        for terminal in RunTermination:
            with self.subTest(terminal=terminal.value):
                v1 = self._assemble(terminal, "mhf.trajectory/1")["outcome"]
                v2 = self._assemble(terminal, "mhf.trajectory/2")["outcome"]
                self.assertEqual(v1, v2)
                self.assertIn(v1, TRAJECTORY_OUTCOME_VALUES)
                if terminal is not RunTermination.COMPLETED:
                    self.assertNotEqual(v1, "completed", terminal.value)

    def test_a_bare_terminal_string_projects_identically_to_the_enum(self) -> None:
        """Writers hand this axis both forms; neither may be the lenient one."""
        for terminal in RunTermination:
            with self.subTest(terminal=terminal.value):
                self.assertEqual(
                    project_trajectory_outcome(terminal),
                    project_trajectory_outcome(terminal.value),
                )
        self.assertEqual(project_trajectory_outcome("ABSTAINED"), "aborted")

    def test_only_completed_reaches_the_success_value(self) -> None:
        """The success value has exactly one preimage in the whole vocabulary."""
        preimages = [t.value for t in RunTermination
                     if project_trajectory_outcome(t) == "completed"]
        self.assertEqual(preimages, ["completed"])

    def test_an_unknown_termination_is_aborted_not_completed(self) -> None:
        self.assertEqual(project_trajectory_outcome("a-terminal-from-2030"), "aborted")

    def test_no_disposition_is_synthesised_onto_the_trajectory(self) -> None:
        """EW-9.1: acceptance travels on `verdict`, never on `outcome`."""
        traj = self._assemble(RunTermination.ABSTAINED, "mhf.trajectory/2")
        self.assertIsNone(traj["verdict"])
        self.assertEqual(traj["verdict_absence_reason"], "no_evaluator_bound")
        self.assertNotIn("disposition", traj)


if __name__ == "__main__":
    unittest.main()
