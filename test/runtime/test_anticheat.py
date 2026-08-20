"""Anti-cheat: seven ways a coding harness reports a score it did not earn.

`REQ-TRUST-001`, `W15-A` item 11. Each of these has a plausible-looking
implementation that produces better numbers, which is exactly why they are
asserted rather than trusted to review. The suite fails if any fire.

Scope note: these check the code *this lane owns and the drivers it ships*.
They are a ratchet against reintroduction, not a claim that the whole tree has
been audited.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

from vanguard.packages.runtime.repair import StopReason
from vanguard.packages.runtime.scoring import score_arm

PACKAGES = Path(__file__).resolve().parents[2] / "vanguard" / "packages"
RUNTIME = PACKAGES / "runtime"

#: The modules this lane ships as the measurement path.
DRIVERS = ("repair.py", "dogfood.py", "lab_driver.py", "scoring.py",
           "session_log.py", "model_selection.py")


def _code(path: Path) -> str:
    """Source with comments and docstrings stripped.

    A rule that its own explanatory comment can satisfy is not a rule.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef, ast.Module)):
            body = getattr(node, "body", [])
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                body.pop(0)
    return ast.unparse(tree)


class NoHostSideOracle(unittest.TestCase):
    """Cheat 1: run the suite on the host, outside the `proc.exec` allowlist.

    A pass produced by the harness shelling out itself is a pass the sandbox
    never mediated and the ledger never saw.
    """

    def test_no_driver_shells_out_to_a_test_runner(self) -> None:
        for name in DRIVERS:
            with self.subTest(module=name):
                code = _code(RUNTIME / name)
                for forbidden in ("subprocess", "os.system", "os.popen",
                                  "pytest", "unittest.main"):
                    self.assertNotIn(forbidden, code)


class NoGoldPatchInTheWorkspace(unittest.TestCase):
    """Cheat 2: copy the reference solution in and call it a repair."""

    def test_no_driver_copies_a_reference_solution(self) -> None:
        for name in DRIVERS:
            with self.subTest(module=name):
                code = _code(RUNTIME / name).lower()
                # The invariant is "no reference solution enters the
                # workspace", not "no copy call exists". Banning `shutil.copy`
                # outright flagged the per-run workspace *isolation* copy,
                # which is the opposite of a gold patch -- it stops one run
                # inheriting another's edits.
                for forbidden in ("gold_patch", "goldpatch", "reference_solution",
                                  "solution.py", "/solution", "expected_output"):
                    self.assertNotIn(forbidden, code)


class NoModelJudgesTheSameArtifact(unittest.TestCase):
    """Cheat 3: `A-05`. A component that grades its own work is a second judge."""

    def test_no_driver_reaches_a_model_to_score(self) -> None:
        for name in ("repair.py", "dogfood.py", "scoring.py", "session_log.py"):
            with self.subTest(module=name):
                code = _code(RUNTIME / name)
                for forbidden in ("propose(", "ModelPort", "OpenRouterModel",
                                  "OllamaModel", "judge"):
                    self.assertNotIn(forbidden, code)

    def test_the_scorer_reaches_no_evaluator(self) -> None:
        code = _code(RUNTIME / "scoring.py")
        for forbidden in ("evaluate(", "Verdict", "evaluator"):
            self.assertNotIn(forbidden, code)


class NoDroppingTasksFromTheDenominator(unittest.TestCase):
    """Cheat 4: the most tempting one, because it improves every rate."""

    REPORTS = (
        {"taskId": "a", "outcome": StopReason.ORACLE_GREEN, "turns": 3},
        {"taskId": "b", "outcome": "inconclusive:workspace_missing"},
        {"taskId": "c", "outcome": StopReason.INSTRUMENT_ERROR},
        {"taskId": "d", "outcome": StopReason.ATTEMPTS_EXHAUSTED, "turns": 8},
    )

    def test_inconclusive_tasks_stay_in_the_denominator(self) -> None:
        score = score_arm("mock", self.REPORTS)
        self.assertEqual(score.denominator, 4)
        self.assertEqual(score.resolved, 1)

    def test_inconclusive_tasks_are_named_not_merely_counted(self) -> None:
        score = score_arm("mock", self.REPORTS)
        self.assertEqual(set(score.inconclusive), {"b", "c"})

    def test_a_rate_never_prints_without_its_denominator(self) -> None:
        """`1/4` alone invites the reader to assume 4 tasks could run."""

        text = score_arm("mock", self.REPORTS).rate_text()
        self.assertIn("1/4", text)
        self.assertIn("inconclusive", text)

    def test_an_all_inconclusive_arm_scores_zero_not_undefined(self) -> None:
        score = score_arm("mock", [{"taskId": "x",
                                    "outcome": "inconclusive:workspace_missing"}])
        self.assertEqual((score.resolved, score.denominator), (0, 1))


class NoMockLabelledAsLive(unittest.TestCase):
    """Cheat 5: a MOCK run quoted as a live result, or as Q2."""

    def test_the_selected_port_is_always_labelled(self) -> None:
        from vanguard.packages.runtime.model_selection import select_model

        self.assertEqual(select_model("mock").to_dict()["modelPort"], "mock")

    def test_no_driver_claims_a_gate(self) -> None:
        for name in DRIVERS:
            with self.subTest(module=name):
                code = _code(RUNTIME / name)
                for forbidden in ("Q2", "gate_passed", "lift", "p_value"):
                    self.assertNotIn(forbidden, code)


class NoOracleTextInThePrompt(unittest.TestCase):
    """Cheat 6: read the oracle into context and let the model pattern-match."""

    def test_the_driver_brief_names_no_oracle_file(self) -> None:
        from vanguard.packages.runtime.lab_driver import DEFAULT_BRIEF

        lowered = DEFAULT_BRIEF.lower()
        for forbidden in ("oracle", "test_oracle", "expected output",
                          "assert", "solution"):
            self.assertNotIn(forbidden, lowered)

    def test_no_driver_reads_an_oracle_path(self) -> None:
        for name in DRIVERS:
            with self.subTest(module=name):
                code = _code(RUNTIME / name).lower()
                for forbidden in ("test_oracle", "/oracle", "oracle/"):
                    self.assertNotIn(forbidden, code)


class NoSecondLoopAndNoSecondDispatchPath(unittest.TestCase):
    """Cheat 7: a private loop or a private way to reach an effect."""

    def test_no_driver_wraps_the_engine(self) -> None:
        for name in DRIVERS:
            with self.subTest(module=name):
                code = _code(RUNTIME / name)
                self.assertNotIn("while True", code)
                self.assertNotIn("EpisodeEngine(", code)

    def test_no_driver_dispatches_an_effect_itself(self) -> None:
        for name in DRIVERS:
            with self.subTest(module=name):
                code = _code(RUNTIME / name)
                for forbidden in ("kernel.dispatch", "Kernel(", ".execute("):
                    self.assertNotIn(forbidden, code)


class TerminationNamesAreNotConflated(unittest.TestCase):
    """W15-A item 12."""

    NAMES = ("oracle_green", "budget_exhausted", "attempts_exhausted",
             "no_progress", "instrument_error")

    def test_every_name_still_exists(self) -> None:
        for name in self.NAMES:
            with self.subTest(name=name):
                self.assertEqual(getattr(StopReason, name.upper()), name)

    def test_budget_and_attempts_remain_distinct(self) -> None:
        self.assertNotEqual(StopReason.BUDGET_EXHAUSTED,
                            StopReason.ATTEMPTS_EXHAUSTED)

    def test_each_termination_is_counted_under_its_own_name(self) -> None:
        score = score_arm("mock", [
            {"taskId": "a", "outcome": StopReason.BUDGET_EXHAUSTED},
            {"taskId": "b", "outcome": StopReason.ATTEMPTS_EXHAUSTED},
        ])
        self.assertEqual(score.terminations,
                         {StopReason.BUDGET_EXHAUSTED: 1,
                          StopReason.ATTEMPTS_EXHAUSTED: 1})


class LarIsReadOnly(unittest.TestCase):
    """W15-A item 10. LAR analyses session logs; it is not in the loop."""

    def test_no_driver_imports_an_optimiser(self) -> None:
        for name in DRIVERS:
            with self.subTest(module=name):
                code = _code(RUNTIME / name).lower()
                # `lar` as a bare substring matches "dec-lar-ed". A rule that
                # fires on an ordinary English word is a rule that will be
                # deleted the first time it cries wolf, so it matches the
                # module the way an import would.
                for forbidden in ("import lar", "from lar", "lar.", "coding_lar",
                                  "optimis", "optimiz", "rewrite_prompt"):
                    self.assertNotIn(forbidden, code)

class AutonomousGrantAndOracleAntiCheat(unittest.TestCase):
    """S32 anti-cheat: ensure agent cannot fake an oracle pass, write in benchmark, or escape bounds."""

    def test_trivial_exit_zero_agent_proc_cannot_authorize_green(self) -> None:
        import sys
        from pathlib import Path

        pack = Path(__file__).resolve().parents[2] / "packs" / "code-default" / "oracles"
        sys.path.insert(0, str(pack))
        from gate import PackOracleGate
        from layer0.spi.types_gen import GateDecision, SignedVerdict

        gate = PackOracleGate()
        decision = gate.gate((SignedVerdict(
            verdict="pass", signature="unsigned", subject_digest="sha256:" + "0" * 64,
            evaluation_request_id="eval-1", oracle_id="oracle-1", nonce="n" * 16,
            key_id="key-1", signed_at="2026-08-20T00:00:00Z"),))
        self.assertEqual(decision, GateDecision.ABANDON)

    def test_benchmark_mode_remains_fail_closed_for_writes(self) -> None:
        from vanguard.packages.kernel import (
            EffectRequest,
            FailurePath,
            HeldAuthority,
            Kernel,
            Mode,
            Outcome,
            StandardClassifier,
            StandardPolicy,
        )
        from vanguard.packages.kernel import Constraints, Scope
        scope = Scope(
            actions=frozenset({"fs.read", "patch.apply"}),
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=100,
                budget_usd_micros=100_000,
            ),
        )
        policy = StandardPolicy(
            parent_scope=scope,
            mode=Mode.BENCHMARK,
            approval_required_above="low",
            risk_of={"patch.apply": "medium"},
        )
        req = EffectRequest(
            action="patch.apply",
            resource={"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
            args={"diff": "--- a\n+++ b\n"},
            principal="agent-1",
            run_id="run-anticheat",
        )
        auth = policy.authorize(req, widens_capability=False, requested_scope=scope)
        self.assertIs(auth.outcome, Outcome.REJECT)
        self.assertIs(auth.failure, FailurePath.DENIED_ASK_FAIL_CLOSED)


if __name__ == "__main__":
    unittest.main()
