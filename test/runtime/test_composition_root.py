"""`TEST-DOG-001` / `REQ-DOG-001` — the runtime composition root and the
Beta Dogfood Milestone Gate (`GTS-13C Ch.10 Q1+Q2`, `ADR-0057`, `ADR-0058`).

**What is real here.** A real git repository with a real single-file bug, a
real `GitEnvironment`, the real `Kernel`, a real `SqliteEventStore`, the real
descriptor-bound approval flow, and a real `python3 -m unittest` subprocess as
the verifier. The *only* doubled seam is the provider, and that is the point:
`REQ-DOG-001`'s margin is **zero human source code edits during the dogfood
run**, which is a claim about who edits the file, not about who sampled the
tokens. A test that stubbed the kernel, the environment or the test runner
would prove the harness can narrate a repair rather than perform one.

The live-provider leg is the same composition with `OpenRouterModel` in place
of the cassette, skipped when `OPENROUTER_API_KEY` is unset — the convention
`test/adapters/test_openrouter.py` already established for `REQ-PORT-006`.

**What the gate must show, and each assertion below maps to one:**

1. Composition is *declarative*. Two manifests produce two different harnesses
   with no branch in `root.py`; an unbound verb fails at composition, not at
   dispatch (`ADR-0060` / `M11`: adding a domain edits no engine line).
2. The agent *diagnoses* — it reads the file before it patches it.
3. The agent *patches* — the file on disk changes, and only through
   `Kernel.dispatch` (`AT-01`).
4. A human *approves the exact descriptor* — an approval for a different diff
   does not authorise this one (`REQ-APP-001`, `ADR-0057`).
5. The tests *pass*, verified by running them, not by asking the model.
6. Every step is on the ledger, and the competence prior is on it first
   (`REQ-CTX-001` / `S5-SA-002`).
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.agency import RunTermination
from vanguard.packages.adapters.evaluators.fake import FakeEvaluator
from vanguard.packages.adapters.evaluators.isolated import IsolatedEvaluator
from vanguard.packages.ports.evaluator import RunRef, Verdict
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.governance.approvals import ApprovalAuthority
from vanguard.packages.runtime.root import (
    DEFAULT_BINDINGS,
    EVALUATOR_BINDINGS,
    CompositionError,
    RunResult,
    Runtime,
    TaskContext,
    _environment_effector,
    _sandbox_effector,
)

OPERATOR_KEY = b"test-operator-held-approval-key"


def sign_challenge(challenge):
    """Operator-side signature. The runtime only verifies (`GOV-01`)."""
    return ApprovalAuthority(OPERATOR_KEY).approve(challenge, reviewer="agent-1")

ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "vanguard" / "packages" / "agency" / "manifests"
CODE_DEFAULT = MANIFESTS / "vg-code-default" / "manifest.json"
SHELL_ONLY = MANIFESTS / "vg-shell-only" / "manifest.json"

#: The bug. `total` starts at one, so every sum is off by one. One file, one
#: line, and a test that already fails — the shape `GTS-13C Ch.10 Q2` asks for.
BUGGY_SOURCE = '''"""A tiny summing helper."""


def total(values):
    result = 1
    for value in values:
        result += value
    return result
'''

FIXED_SOURCE = BUGGY_SOURCE.replace("result = 1", "result = 0")

TEST_SOURCE = '''import unittest

from calc import total


class Total(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(total([]), 0)

    def test_sums(self):
        self.assertEqual(total([1, 2, 3]), 6)


if __name__ == "__main__":
    unittest.main()
'''


def build_repo() -> Path:
    """A real git repository containing a real failing test."""
    path = Path(tempfile.mkdtemp(prefix="vg-dogfood-"))
    (path / "calc.py").write_text(BUGGY_SOURCE, encoding="utf-8")
    (path / "test_calc.py").write_text(TEST_SOURCE, encoding="utf-8")
    for argv in (["git", "init", "-q"],
                 ["git", "config", "user.email", "dogfood@vanguard.test"],
                 ["git", "config", "user.name", "dogfood"],
                 ["git", "add", "-A"],
                 ["git", "commit", "-q", "-m", "seed"]):
        subprocess.run(argv, cwd=path, check=True, capture_output=True)
    return path


def tests_pass(repo: Path) -> bool:
    """Run the repository's own tests. The verifier is a process, not a claim."""
    completed = subprocess.run(
        ["python3", "-m", "unittest", "discover", "-s", str(repo), "-t", str(repo)],
        capture_output=True, text=True, cwd=repo)
    return completed.returncode == 0


def unified_diff(repo: Path) -> str:
    """The patch the operator proposes.

    Produced from the two known states via `git diff` so the cassette is a real
    unified diff rather than a hand-rolled approximation, then the working tree
    is restored: the agent still has to get it applied, and the assertion that
    the file changed means nothing if this helper is what changed it.
    """
    (repo / "calc.py").write_text(FIXED_SOURCE, encoding="utf-8")
    completed = subprocess.run(["git", "diff", "--", "calc.py"],
                               cwd=repo, capture_output=True, text=True, check=True)
    (repo / "calc.py").write_text(BUGGY_SOURCE, encoding="utf-8")
    return completed.stdout


class ScriptedOperator:
    """A recorded three-turn trajectory: read, patch, verify, finish.

    It is a cassette, not a decision procedure — it cannot see the repository
    and cannot adapt. Everything it proposes still has to survive the kernel,
    the approval flow and the real test run, which is where the gate lives.
    """

    def __init__(self, diff: str, repo: Path) -> None:
        self._diff = diff
        self.repo = repo
        self.contexts: list[dict] = []
        self._turn = 0

    def propose(self, context, tools, sampling):
        self.contexts.append(dict(context))
        turn, self._turn = self._turn, self._turn + 1
        resource = {"kind": "fs", "root": str(self.repo), "paths": [str(self.repo)]}
        script = [
            {"kind": "effect", "action": "fs.read", "resource": resource,
             "args": {"path": "calc.py"},
             "reservation": {"usd_micros": 100, "millis": 500}},
            {"kind": "effect", "action": "patch.apply", "resource": resource,
             "args": {"diff": self._diff},
             "reservation": {"usd_micros": 100, "millis": 500}},
            {"kind": "finish", "note": "off-by-one corrected"},
        ]
        if turn >= len(script):
            return _Failed("cassette exhausted")
        return _Ok(script[turn])


class SuiteVerifier:
    """The exterior evaluator (`ICD §3`, `M5`).

    It runs the repository's own tests in a subprocess. It is not OS-isolated —
    that is `REQ-EVAL-001`'s claim and `IsolatedEvaluator`'s test, and the live
    leg below composes that one instead. What matters to `REQ-DOG-001` is that
    the verdict is produced *outside* the episode, from running the tests
    rather than from asking the model whether it succeeded.
    """

    def __init__(self, repo: Path) -> None:
        self._repo = repo
        self.calls: list[RunRef] = []

    def evaluate(self, run_ref, protocol):
        self.calls.append(run_ref)
        green = tests_pass(self._repo)
        return Result.success(Verdict(
            outcome="claims",
            claims=({"claim": "tests_green", "holds": green,
                     "protocol": protocol.name},)))


class _Ok:
    def __init__(self, value):
        self.ok, self.value, self.error = True, value, None


class _Failed:
    def __init__(self, message):
        self.ok, self.value = False, None
        self.error = type("E", (), {"kind": "instrument_error", "message": message})()


class Composition(unittest.TestCase):
    """Claim 1: the root composes from data, and refuses to guess."""

    def test_two_manifests_compose_two_different_harnesses(self) -> None:
        """`M11` / `ADR-0060`: a harness is a manifest, not a code path."""
        code = Runtime.compose(CODE_DEFAULT)
        shell = Runtime.compose(SHELL_ONLY)

        self.assertNotEqual(code.composition_digest, shell.composition_digest)
        self.assertEqual(code.harness, "vg-code-default")
        self.assertEqual(sorted(code.verbs), ["fs.read", "fs.search", "patch.apply", "proc.exec"])
        self.assertEqual(sorted(shell.verbs), ["proc.exec"])

    def test_composition_is_deterministic_for_one_episode(self) -> None:
        self.assertEqual(Runtime.compose(CODE_DEFAULT, episode_id="e-1").composition_digest,
                         Runtime.compose(CODE_DEFAULT, episode_id="e-1").composition_digest)

    def test_sink_classes_come_from_the_manifest_not_from_root(self) -> None:
        """`ADR-0057` binds human approval to the privileged sink. If `root.py`
        decided which verb was privileged, the manifest would be decoration."""
        code = Runtime.compose(CODE_DEFAULT)

        self.assertEqual(code.sink_class_of("fs.read").value, "observation")
        self.assertEqual(code.sink_class_of("patch.apply").value, "privileged")

    def test_a_verb_with_no_bound_adapter_fails_at_composition(self) -> None:
        """`M6`/`M9`: an unwireable harness is discovered while composing, not
        three turns into a run against a real repository."""
        with self.assertRaises(CompositionError):
            Runtime.compose(CODE_DEFAULT, bindings={})

    def test_proc_exec_is_bound_to_the_sandbox_not_the_host_environment(self) -> None:
        """`SBOX-01`: command verbs must not inherit GitEnvironment.apply."""
        self.assertIs(DEFAULT_BINDINGS["proc.exec"].factory, _sandbox_effector)
        self.assertIsNot(DEFAULT_BINDINGS["proc.exec"].factory, _environment_effector)

    def test_a_manifest_that_does_not_resolve_fails_closed(self) -> None:
        with self.assertRaises(CompositionError):
            Runtime.compose(MANIFESTS / "does-not-exist" / "manifest.json")


class DogfoodGate(unittest.TestCase):
    """Claims 2-6: the milestone itself, against a real repository."""

    def setUp(self) -> None:
        self.repo = build_repo()
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(self.repo)], check=False))
        self.diff = unified_diff(self.repo)
        self.operator = ScriptedOperator(self.diff, self.repo)
        self.verifier = SuiteVerifier(self.repo)

    def execute(self, **overrides) -> RunResult:
        task = TaskContext(
            brief="calc.total is off by one for every input; make the suite green.",
            repo_path=self.repo,
            run_id="run-dogfood-1",
            episode_id="episode-dogfood-1",
            principal="agent-1",
            competence_prior=0.6,
        )
        kwargs = {"manifest_path": CODE_DEFAULT, "task_context": task,
                  "model": self.operator, "approver": sign_challenge,
                  "approval_key": OPERATOR_KEY,
                  "verifier": self.verifier}
        kwargs.update(overrides)
        return Runtime.execute_harness(**kwargs)

    # -- claim 2: it reads before it writes ----------------------------

    def test_the_repository_starts_broken(self) -> None:
        """`M6`: a gate that cannot fail is not a gate. If the suite is green
        before the run, every assertion below passes for the wrong reason."""
        self.assertFalse(tests_pass(self.repo))

    def test_the_agent_observes_the_file_before_patching_it(self) -> None:
        result = self.execute()

        verbs = [receipt.verb for receipt in result.receipts]
        self.assertLess(verbs.index("fs.read"), verbs.index("patch.apply"))

    # -- claim 3: it patches, and only through dispatch -----------------

    def test_the_bug_is_fixed_on_disk(self) -> None:
        """`REQ-DOG-001` margin: zero human source code edits during the run."""
        self.execute()

        self.assertIn("result = 0", (self.repo / "calc.py").read_text(encoding="utf-8"))

    def test_every_effect_went_through_kernel_dispatch(self) -> None:
        """`AT-01`, `05 §2.1`. A patch that reached the disk without a durable
        intent in front of it is a second path, whatever else it achieved."""
        result = self.execute()

        kinds = [event.kind for event in result.events]
        self.assertEqual(kinds.count("EffectStarted"), len(result.receipts))
        for receipt in result.receipts:
            self.assertTrue(receipt.descriptor_digest.startswith("sha256:"))

    # -- claim 4: the human approves the exact descriptor ---------------

    def test_the_privileged_patch_requested_human_approval(self) -> None:
        """`ADR-0057`: human approve of the *exact descriptor*."""
        result = self.execute()

        challenges = [event for event in result.events if event.kind == "ApprovalRequested"]
        patch = next(r for r in result.receipts if r.verb == "patch.apply")

        self.assertEqual(len(challenges), 1)
        # `K-15`: the suspension binds the descriptor, so the effect that
        # eventually ran is the one the human was shown — not merely one with
        # the same verb.
        self.assertEqual(challenges[0].payload["descriptorDigest"], patch.descriptor_digest)

    def test_a_boolean_approver_is_not_a_signature(self) -> None:
        """`GOV-01`: a True callback must not mint the HMAC the runtime verifies."""
        result = self.execute(approver=lambda challenge: True)

        self.assertEqual((self.repo / "calc.py").read_text(encoding="utf-8"), BUGGY_SOURCE)
        self.assertIsNot(result.terminal, RunTermination.COMPLETED)

    def test_a_refused_approval_leaves_the_file_untouched(self) -> None:
        """The approval is load-bearing, not ceremonial."""
        result = self.execute(approver=lambda challenge: False)

        self.assertEqual((self.repo / "calc.py").read_text(encoding="utf-8"), BUGGY_SOURCE)
        self.assertFalse(tests_pass(self.repo))
        self.assertIsNot(result.terminal, RunTermination.COMPLETED)

    def test_an_absent_approver_is_a_refusal_not_a_default_allow(self) -> None:
        """An unattended interactive run that silently approved its own
        privileged effects would make `ADR-0057` decorative. Nobody to ask is
        not the same as permission."""
        result = self.execute(approver=None)

        self.assertEqual((self.repo / "calc.py").read_text(encoding="utf-8"), BUGGY_SOURCE)
        self.assertIs(result.terminal, RunTermination.ESCALATED)
        self.assertFalse(result.verdict.claims[0]["holds"])

    def test_benchmark_mode_denies_the_patch_rather_than_suspending(self) -> None:
        """`K-17`: a run that blocks for a human has unbounded wall-clock *and*
        a human contributing to the measured outcome, so `interactive=False`
        fails approval closed. It is not "approve everything"."""
        result = self.execute(interactive=False, approver=None)

        self.assertEqual((self.repo / "calc.py").read_text(encoding="utf-8"), BUGGY_SOURCE)
        self.assertIn("AuthorizationDenied", [event.kind for event in result.events])
        self.assertFalse(result.verdict.claims[0]["holds"])

    # -- claim 5: the tests pass, and something ran them ----------------

    def test_the_suite_is_green_after_the_run(self) -> None:
        self.execute()

        self.assertTrue(tests_pass(self.repo))

    def test_the_verdict_comes_from_outside_the_episode(self) -> None:
        """`ICD §3`, `M5`: the episode terminates; it does not grade itself."""
        result = self.execute()

        self.assertIs(result.terminal, RunTermination.COMPLETED)
        self.assertEqual(result.verdict.outcome, "claims")
        self.assertTrue(result.verdict.claims[0]["holds"])
        self.assertEqual(len(self.verifier.calls), 1)

    def test_unconfigured_evaluator_is_inconclusive_not_success(self) -> None:
        """Wrong UID / unverified image is a real outcome, not a missing verdict
        and not a fake pass (`REQ-EVAL-001`, `M5`)."""
        result = self.execute(verifier=None)

        self.assertIsNotNone(result.verdict)
        self.assertEqual(result.verdict.outcome, "inconclusive")
        self.assertNotEqual(result.verdict.outcome, "claims")

    def test_no_code_path_substitutes_a_fake_evaluator(self) -> None:
        self.assertIs(EVALUATOR_BINDINGS.get("coding-oracle@3"), IsolatedEvaluator)
        self.assertNotIn(FakeEvaluator, EVALUATOR_BINDINGS.values())

    # -- claim 6: it is all on the ledger, prior first ------------------

    def test_the_competence_prior_is_the_first_event_on_the_ledger(self) -> None:
        """`S5-SA-002`: *pre-action*. A prior emitted after the first proposal
        is conditioned on evidence it claims not to have seen."""
        result = self.execute()

        kinds = [event.kind for event in result.events]
        self.assertEqual(kinds[0], "CompetencePriorRecorded")
        self.assertLess(kinds.index("CompetencePriorRecorded"),
                        kinds.index("ProposalProduced"))

    def test_the_prior_binds_the_context_that_was_actually_sent(self) -> None:
        result = self.execute()

        prior = next(e for e in result.events if e.kind == "CompetencePriorRecorded")
        self.assertEqual(prior.payload["promptDigest"],
                         self.operator.contexts[0]["promptDigest"])

    def test_the_context_the_provider_saw_was_layered_and_prefix_stable(self) -> None:
        """`REQ-CTX-001` in situ: the compiler is wired in, and the prefix did
        not move across the turns of a real run."""
        self.execute()

        self.assertGreater(len(self.operator.contexts), 1)
        self.assertEqual({context["prefixDigest"] for context in self.operator.contexts},
                         {self.operator.contexts[0]["prefixDigest"]})
        self.assertEqual([message["layer"] for message in self.operator.contexts[0]["layers"]][:2],
                         ["L1", "L2"])

    def test_events_persist_to_the_store_not_just_to_memory(self) -> None:
        """`REQ-DOG-001`: all events persisted to ledger. An in-process list is
        not a ledger — a crash after the run must leave the trace behind."""
        result = self.execute()

        stored = result.store.read()
        self.assertTrue(stored.ok, stored.error)
        stored_kinds = [envelope.payload["kind"] for envelope in stored.value]
        for event in result.events:
            self.assertIn(event.kind, stored_kinds)
        # `K-47` writes the intent durably *before* the effect and `S12`
        # publishes it afterwards, so each `EffectStarted` is two records. A
        # store that held only one of them could not distinguish "the effect
        # was attempted" from "the effect was reported".
        self.assertEqual(len(stored.value),
                         len(result.events) + stored_kinds.count("EffectStarted") // 2)

    def test_the_run_result_carries_the_composition_it_ran(self) -> None:
        """Attribution (`Ch.11 §2`) needs to know *which* harness produced this."""
        result = self.execute()

        self.assertEqual(result.harness, "vg-code-default")
        self.assertTrue(result.composition_digest.startswith("sha256:"))


class LiveDogfood(unittest.TestCase):
    """The same composition against the real provider (`REQ-PORT-006`)."""

    @unittest.skipUnless(os.environ.get("OPENROUTER_API_KEY"),
                         "live OpenRouter dogfood skipped: key unset")
    def test_optional_live_single_file_repair(self) -> None:
        from vanguard.packages.adapters.models.openrouter import OpenRouterModel

        repo = build_repo()
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(repo)], check=False))
        task = TaskContext(
            brief="calc.total is off by one for every input; make the suite green.",
            repo_path=repo, run_id="run-live-1", episode_id="episode-live-1",
            principal="agent-1", competence_prior=0.5)

        result = Runtime.execute_harness(
            manifest_path=CODE_DEFAULT, task_context=task,
            model=OpenRouterModel(), approver=sign_challenge,
            approval_key=OPERATOR_KEY)

        # A live model may fail to repair the bug; that is a task outcome, not
        # a defect in the composition. What the composition must not do is
        # report success it did not achieve.
        self.assertIsNotNone(result.terminal)
        if result.verdict is not None and result.verdict.passed:
            self.assertTrue(tests_pass(repo))


if __name__ == "__main__":
    unittest.main()
