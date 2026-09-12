"""T-131 row 6 (RUN-09 defect 6): evidence identity must equal the submitted
product candidate.

RUN-09 names as `BLOCK-T27` the defect "evidence identity can diverge from the
submitted product candidate". `vanguard/packages/runtime/session.py` carries the
*mechanism*: `_observe_completion_dispatch` stamps every verification receipt
with the workspace digest observed at verification time, and `_admit_completion`
re-derives the digest of the tree the `finish` claim is being made about. A
mechanism that exists is not a mechanism that is qualified, so this module runs
the **product route** — the real `HarnessSession` capture site and the real
completion admitter that `EpisodeEngine` is handed at
`session.py` `completion_admitter=` — and asks the only question that matters:
does evidence bound to anything other than the exact submitted candidate tree
red?

Candidate identity here is **not invented by the test**. It is produced by the
product's own `SandboxedEnvironmentAdapter.snapshot`, which digests the real
file bytes of the workspace; `snapshot()` touches neither the worker nor the
sandbox, so the product's identity function runs unmodified over a temp tree.
The stock `FakeEnvironment` returns a constant digest and therefore *cannot*
express drift — a suite built on it can only prove the happy path.

RUN-12: zero provider calls, zero USD, zero tokens. `FakeModel([])` is never
proposed to; the episode loop is not entered.
"""

from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.environment.sandboxed import SandboxedEnvironmentAdapter
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.kernel import FailurePath
from vanguard.packages.runtime.entrypoint import _completion_policy, _manifest
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext

STUB = "def fibonacci(n):\n    pass\n"
REAL = "def fibonacci(n):\n    return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)\n"
ORACLE = "def test_fibonacci():\n    assert fibonacci(7) == 13\n"

TEST_REQUEST = SimpleNamespace(
    action="proc.exec",
    args={"argv": ["python3", "-m", "unittest", "test_app.py"]},
)


def _result(exit_code: int, tests: int = 1):
    return SimpleNamespace(
        failure=FailurePath.OK,
        outcome=SimpleNamespace(
            status="ok" if exit_code == 0 else "failed",
            detail=f"[exit {exit_code}] Ran {tests} test{'s' if tests != 1 else ''}",
            result_digest=f"sha256:result-{exit_code}",
        ),
    )


class ContentBoundEnvironment(FakeEnvironment):
    """`FakeEnvironment`, except identity comes from the product's own digest.

    Everything the session needs for dispatch stays doubled; `snapshot` is the
    unmodified `SandboxedEnvironmentAdapter.snapshot`, so the candidate tree
    digest is a function of the real bytes on disk and drifts exactly when the
    submitted candidate drifts.
    """

    def __init__(self, root: Path) -> None:
        super().__init__()
        self._identity = SandboxedEnvironmentAdapter(
            worker=None, workspace=root, environment_id="t131-row6")

    def snapshot(self):  # type: ignore[override]
        return self._identity.snapshot()


def _tree_digest(root: Path) -> str:
    """The product's candidate identity for `root`, read independently."""
    snapshot = SandboxedEnvironmentAdapter(
        worker=None, workspace=root, environment_id="t131-row6-probe").snapshot()
    assert snapshot.ok and snapshot.value is not None
    return snapshot.value.digest


def _session(root: Path, suffix: str) -> HarnessSession:
    return HarnessSession(
        Runtime.compose("vg-code-default", episode_id=f"ep-t131-row6-{suffix}"),
        SessionPorts(
            model=FakeModel([]),
            environment=ContentBoundEnvironment(root),
            clock=FakeClock(),
            store=SqliteEventStore(":memory:"),
            interactive=False,
            completion_policy=_completion_policy(_manifest("code")),
        ),
        TaskContext(
            brief="Create a greenfield project from scratch",
            repo_path=root,
            run_id=f"run-t131-row6-{suffix}",
            episode_id=f"ep-t131-row6-{suffix}",
        ),
    )


def _submit_candidate(session: HarnessSession, root: Path) -> None:
    """Drive the product route to a verified, admissible candidate.

    Red on the stub, then green on the implementation, both observed at the
    mediated dispatch boundary exactly as `EpisodeEngine` observes them.
    """
    (root / "app.py").write_text(STUB, encoding="utf-8")
    (root / "test_app.py").write_text(ORACLE, encoding="utf-8")
    for relative in ("app.py", "test_app.py"):
        session._observe_completion_dispatch(
            SimpleNamespace(action="patch.apply", args={"path": relative}), _result(0))
    session._observe_completion_dispatch(TEST_REQUEST, _result(1))
    (root / "app.py").write_text(REAL, encoding="utf-8")
    session._observe_completion_dispatch(
        SimpleNamespace(action="patch.apply", args={"path": "app.py"}), _result(0))
    session._observe_completion_dispatch(TEST_REQUEST, _result(0))


class EvidenceIdentityEqualsTheSubmittedCandidate(unittest.TestCase):
    """POSITIVE falsifier, on the product route."""

    def test_the_receipt_is_stamped_with_the_submitted_candidate_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = _session(root, "positive")
            _submit_candidate(session, root)

            submitted = _tree_digest(root)
            receipt = session._completion_verification
            self.assertIsNotNone(receipt)
            # Evidence identity == submitted candidate, measured three ways:
            # the receipt, the session's own re-derivation, and an independent
            # read of the tree through the product's digest function.
            self.assertEqual(receipt.workspace_digest, submitted)
            self.assertEqual(session._workspace_digest(), submitted)
            self.assertEqual(
                session._completion_verification_subject.workspace_digest, submitted)

            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertTrue(verdict.admissible, verdict.reason)

    def test_identity_is_content_bound_not_a_constant(self) -> None:
        """Control: the instrument can tell two candidate trees apart.

        Without this, every red below could be a digest that is simply never
        equal to anything.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text(STUB, encoding="utf-8")
            before = _tree_digest(root)
            self.assertEqual(before, _tree_digest(root))  # stable when unchanged
            (root / "app.py").write_text(REAL, encoding="utf-8")
            self.assertNotEqual(before, _tree_digest(root))
            (root / "app.py").write_text(STUB, encoding="utf-8")
            self.assertEqual(before, _tree_digest(root))  # and returns


class DriftedEvidenceIdentityIsRefused(unittest.TestCase):
    """ADVERSARIAL falsifier. Each case must RED on drifted identity."""

    def test_a_candidate_that_moved_after_verification_cannot_complete(self) -> None:
        """A stale tree digest: the evidence describes a tree no longer submitted."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = _session(root, "stale")
            _submit_candidate(session, root)
            verified = _tree_digest(root)

            # The candidate tree moves under the standing evidence. No new
            # verification is observed; this is precisely RUN-09 defect 6.
            (root / "app.py").write_text(REAL + "\n# unverified edit\n", encoding="utf-8")
            drifted = _tree_digest(root)
            self.assertNotEqual(verified, drifted, "drift was not actually induced")
            self.assertEqual(session._completion_verification.workspace_digest, verified)
            self.assertEqual(session._workspace_digest(), drifted)

            # Refuse the cheap red. An agent that edits and then refreshes its
            # context packet clears the epoch gate; without that refresh this
            # case would be answered by `PACKET_EPOCH_STALE` and would prove
            # nothing about evidence identity. The refresh puts the identity
            # check itself on trial.
            session.refresh_context_packet()
            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertFalse(
                verdict.admissible,
                "evidence bound to a superseded candidate tree was admitted")
            self.assertEqual(verdict.reason, "VERIFICATION_STALE")

            # Negative control: restore the exact submitted candidate and the
            # same session admits again. The red above is caused by identity
            # drift, not by the edit mechanics or by an exhausted session.
            (root / "app.py").write_text(REAL, encoding="utf-8")
            self.assertEqual(_tree_digest(root), verified)
            session.refresh_context_packet()
            restored = session._admit_completion(None, {"kind": "finish"})
            self.assertTrue(restored.admissible, restored.reason)

    def test_a_receipt_carrying_a_foreign_tree_digest_cannot_complete(self) -> None:
        """A substituted tree digest: real green evidence, wrong candidate."""
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as other:
            root, foreign_root = Path(tmp), Path(other)
            session = _session(root, "substituted")
            _submit_candidate(session, root)
            self.assertTrue(
                session._admit_completion(None, {"kind": "finish"}).admissible)

            # A different candidate tree that also verifies green. Only the
            # identity stamped on the evidence is swapped; exit code, executed
            # test count, task, composition and command are untouched.
            foreign_root.joinpath("app.py").write_text(
                REAL.replace("n < 2", "n <= 1"), encoding="utf-8")
            foreign_root.joinpath("test_app.py").write_text(ORACLE, encoding="utf-8")
            foreign = _tree_digest(foreign_root)
            self.assertNotEqual(foreign, _tree_digest(root))

            session._completion_verification = replace(
                session._completion_verification, workspace_digest=foreign)
            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertFalse(
                verdict.admissible,
                "a passing receipt stamped with a foreign candidate was admitted")
            self.assertEqual(verdict.reason, "VERIFICATION_STALE")

    def test_a_receipt_with_no_candidate_identity_cannot_complete(self) -> None:
        """Unbound identity is drift's degenerate case and must not read green."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = _session(root, "unbound")
            _submit_candidate(session, root)
            session._completion_verification = replace(
                session._completion_verification, workspace_digest="")
            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertFalse(
                verdict.admissible, "evidence with no candidate identity was admitted")

    def test_a_verification_subject_bound_to_another_tree_cannot_complete(self) -> None:
        """T-07 subject binding: the argv's postimage is part of identity."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = _session(root, "subject")
            _submit_candidate(session, root)
            stale_subject = replace(
                session._completion_verification_subject,
                workspace_digest="sha256:" + "0" * 64)
            session._completion_verification = replace(
                session._completion_verification,
                verification_subject_digest=stale_subject.digest())
            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertFalse(
                verdict.admissible,
                "a verification subject bound to another tree was admitted")


if __name__ == "__main__":
    unittest.main()
