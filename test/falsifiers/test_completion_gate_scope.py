"""Completion-gate scope falsifiers (T-04 / T-05 successor baseline).

Successor to the frozen W-092-2 assertion, which pinned the shape this file
now forbids: a name allowlist (``ADMISSION_GATED_HARNESSES``) that nothing
read, beside a name exemption (``ADMISSION_GATE_EXEMPT``) that bought
``vg-code-default`` and ``vg-code-lex`` a permanent product-default bypass.

The successor contract is capability-derived and has exactly one decider:
``admission_required``.  A preset is gated because it declares ``patch.apply``,
never because of what it is called, so the scope cannot drift as presets are
added and no name set can disagree with the predicate.
"""

from __future__ import annotations

import inspect
import unittest
from dataclasses import dataclass
from pathlib import Path

import vanguard.packages.runtime.session as session_module
from vanguard.packages.agency.episode.admission_gate import VerificationReceipt
from vanguard.packages.ports.child_runtime import ChildRunPlan
from vanguard.packages.runtime.app_service import (
    ApplicationService,
    project_terminal_outcome,
)
from vanguard.packages.runtime.child_runtime import TERMINAL_OUTCOMES, RuntimeChildRunner
from vanguard.packages.runtime.root import Runtime
from vanguard.packages.runtime.session import admission_required

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class _Harness:
    """The duck type ``admission_required`` reads: a name and its verbs."""

    harness: str
    verbs: tuple[str, ...]


class TestCompletionGateScope(unittest.TestCase):
    def test_the_product_default_is_no_longer_exempt(self) -> None:
        """T-04. The frozen exemption is gone, not renamed or narrowed."""
        self.assertTrue(
            admission_required(
                _Harness("vg-code-default", ("fs.read", "patch.apply", "proc.exec"))))
        self.assertTrue(
            admission_required(
                _Harness("vg-code-lex", ("fs.read", "patch.apply", "proc.exec"))))

    def test_no_exemption_or_allowlist_constant_survives(self) -> None:
        """T-05. Two name sets could disagree with the predicate; both are gone."""
        self.assertFalse(hasattr(session_module, "ADMISSION_GATE_EXEMPT"))
        self.assertFalse(hasattr(session_module, "ADMISSION_GATED_HARNESSES"))

    def test_gating_is_decided_by_declared_capability_alone(self) -> None:
        """A preset nobody has heard of is gated by what it declares."""
        self.assertTrue(
            admission_required(_Harness("vg-code-invented-tomorrow", ("patch.apply",))))
        self.assertFalse(
            admission_required(_Harness("vg-research-minimal", ("fs.read", "fs.search"))))

    def test_the_name_cannot_change_the_verdict(self) -> None:
        """The gate is a function of the verbs; renaming a preset moves nothing."""
        verbs = ("fs.read", "patch.apply")
        self.assertEqual(
            admission_required(_Harness("vg-code-default", verbs)),
            admission_required(_Harness("anything-at-all", verbs)),
        )

    def test_one_function_decides_gating(self) -> None:
        """No inline set at the wiring site, and no second decider beside it."""
        source = inspect.getsource(session_module)
        self.assertNotIn(
            "harness.harness in {",
            source,
            "inline gate-scope set reintroduced; admission_required is the one decider",
        )
        self.assertEqual(source.count("def admission_required"), 1)

    def test_the_composed_product_presets_are_gated(self) -> None:
        """Read through real composition, not a hand-maintained name list."""
        for preset in ("vg-code-default", "vg-code-lex", "vg-code-max"):
            with self.subTest(preset=preset):
                harness = Runtime.compose(preset, episode_id="ep-gate-scope")
                self.assertIn("patch.apply", harness.verbs)
                self.assertTrue(admission_required(harness))

    def test_a_composed_read_only_preset_is_not_gated(self) -> None:
        """Gating follows the declared capability down as well as up."""
        harness = Runtime.compose("vg-research-minimal", episode_id="ep-gate-scope")
        self.assertNotIn("patch.apply", harness.verbs)
        self.assertFalse(admission_required(harness))


class _StubRunResult:
    """The subset of ``RunResult`` the child projection reads."""

    def __init__(self, terminal: str) -> None:
        self.terminal = terminal
        self.receipts = ()
        self.events = ()
        self.run_digest = "sha256:" + "1" * 64
        self.activation_digest = ""
        self.state_digest = "sha256:" + "2" * 64
        self.detail = "child refused"
        self.trajectory = None


def _plan() -> ChildRunPlan:
    return ChildRunPlan(
        child_episode_id="ep-child-1", parent_episode_id="ep-parent-1",
        run_id="run-1", project_id="project-1", principal="agent-child",
        composition_digest="sha256:" + "3" * 64,
        goal_digest="sha256:" + "4" * 64,
        authority=("fs.read",), resources=(), depth=1, max_depth=2, max_turns=4,
        budget={}, lineage=("ep-parent-1",), idempotency_key="idem-1",
    )


class TestTerminalProjectionIsLossless(unittest.TestCase):
    """NT-B04. Refusal is a terminal, never a disposition, and never success."""

    def test_the_shared_rule_relabels_no_terminal(self) -> None:
        for terminal in ("completed", "abstained", "escalated", "cancelled",
                         "budget_exhausted", "instrument_error", "runtime_error",
                         "abandoned"):
            with self.subTest(terminal=terminal):
                self.assertEqual(project_terminal_outcome(terminal), terminal)

    def test_abstention_is_not_completion(self) -> None:
        """The mutation this task exists to forbid, stated directly."""
        self.assertNotEqual(project_terminal_outcome("abstained"), "completed")

    def test_the_rule_never_synthesises_a_disposition(self) -> None:
        """EW-9.1. Only `passed` satisfies acceptance, and it lives elsewhere."""
        source = inspect.getsource(project_terminal_outcome)
        for disposition in ("TaskDisposition", "passed", "failed_acceptance"):
            with self.subTest(token=disposition):
                self.assertNotIn(f"{disposition}", source.split('"""')[-1])

    # -- child adapter -------------------------------------------------

    def test_the_child_adapter_never_reports_abstention_as_ok(self) -> None:
        """A refused child arrives as a refusal, with its terminal intact."""
        runner = RuntimeChildRunner.__new__(RuntimeChildRunner)
        result = RuntimeChildRunner._project(runner, _plan(), _StubRunResult("abstained"))
        self.assertFalse(result.ok)
        self.assertEqual(result.outcome, "abandoned")
        self.assertEqual(result.terminal, "ABSTAINED")

    def test_the_constrained_delegation_vocabulary_is_preserved(self) -> None:
        """`abstained -> abandoned` is deliberate and stays (T-99 contract)."""
        self.assertEqual(TERMINAL_OUTCOMES["abstained"], "abandoned")
        self.assertEqual(TERMINAL_OUTCOMES["completed"], "completed")

    def test_a_completed_child_is_still_ok(self) -> None:
        runner = RuntimeChildRunner.__new__(RuntimeChildRunner)
        result = RuntimeChildRunner._project(runner, _plan(), _StubRunResult("completed"))
        self.assertTrue(result.ok)
        self.assertEqual(result.outcome, "completed")
        self.assertEqual(result.terminal, "COMPLETED")


class TestApplicableVerificationStillAdmits(unittest.TestCase):
    """TC-E-058. The repair must not weaken admission, and must not tighten it.

    These read the *production* policy binding — the same object
    ``ApplicationService`` hands the runtime — so a fixture cannot pass by
    consulting a friendlier gate than the product does.
    """

    def setUp(self) -> None:
        manifest = (ROOT / "vanguard" / "packages" / "agency" / "manifests"
                    / "vg-code-balanced" / "manifest.json")
        self.policy = ApplicationService._pack_completion_policy(manifest)
        self.assertIsNotNone(self.policy, "the product preset must bind a policy")
        self.workspace_digest = "sha256:" + "a" * 64

    def _receipt(self, *, exit_code: int = 0, tests: int = 7) -> VerificationReceipt:
        return VerificationReceipt(
            exit_code=exit_code, executed_test_count=tests,
            workspace_digest=self.workspace_digest,
            verification_command="python3 -m unittest test.widget -v",
        )

    def _evaluate(self, **overrides: object) -> dict:
        kwargs: dict = {
            "preset_name": "vg-code-balanced",
            "changed_files": ("widget.py",),
            "proposal": {"kind": "finish"},
            "verification": self._receipt(),
            "current_workspace_digest": self.workspace_digest,
            "inspected_files": ("widget.py",),
            "task_text": "refactor widget.py so the adder shares one helper",
            "implicated_files": ("widget.py",),
            "primary_files": ("widget.py",),
        }
        kwargs.update(overrides)
        return dict(self.policy.evaluate(**kwargs))

    def test_real_applicable_verification_is_admitted(self) -> None:
        """The positive fixture: a patch plus a fresh, applicable test run."""
        verdict = self._evaluate()
        self.assertTrue(verdict["admissible"], verdict)
        self.assertEqual(verdict["reason"], "completion_admissible")

    def test_a_bare_finish_is_not_sufficient(self) -> None:
        """No patch at all on a change task is not a completion."""
        verdict = self._evaluate(changed_files=(), implicated_files=(),
                                 primary_files=(), inspected_files=())
        self.assertFalse(verdict["admissible"], verdict)
        self.assertEqual(verdict["reason"], "MISSING_SOURCE_PATCH")

    def test_a_patch_without_verification_is_not_sufficient(self) -> None:
        verdict = self._evaluate(verification=None)
        self.assertFalse(verdict["admissible"], verdict)
        self.assertEqual(verdict["reason"], "VERIFICATION_REQUIRED")

    def test_a_failing_verification_is_not_sufficient(self) -> None:
        verdict = self._evaluate(verification=self._receipt(exit_code=1))
        self.assertFalse(verdict["admissible"], verdict)
        self.assertEqual(verdict["reason"], "VERIFICATION_FAILED")

    def test_a_stale_verification_is_not_applicable(self) -> None:
        """Fresh means bound to the postimage the claim is about."""
        verdict = self._evaluate(current_workspace_digest="sha256:" + "b" * 64)
        self.assertFalse(verdict["admissible"], verdict)
        self.assertEqual(verdict["reason"], "VERIFICATION_STALE")


if __name__ == "__main__":
    unittest.main()
