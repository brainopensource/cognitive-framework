"""W2a: candidate identity is not content-addressed.

`GitEnvironment.snapshot` digests `{"head": <rev-parse HEAD>, "status": <status
--porcelain>}`. `git status --porcelain` emits status codes and paths, never
content -- so two different edits to the same tracked file both render
` M module.py` and hash identically.

`test/adapters/test_git_snapshot_identity.py` appears to cover this but does
not: its final assertion moves the tree from *clean* to *dirty*, so the status
text changes from `""` to ` M module.py` and the digest changes for that reason
alone. The dirty-to-dirty transition below is the one that collides.

These are reproduction falsifiers only (packet W2a). They must red against the
current implementation. The fix is W2b and is gated on the C6 ruling.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.environment.git import GitEnvironment

_SEED = "VALUE = 1\n"


def _git(root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *argv], cwd=root, check=True, capture_output=True, text=True
    )


def _seed_repo(root: Path) -> None:
    (root / "module.py").write_text(_SEED, encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "w2a@example.test")
    _git(root, "config", "user.name", "w2a-test")
    _git(root, "add", "module.py")
    _git(root, "commit", "-q", "-m", "seed")


class TestCandidateIdentityCollision(unittest.TestCase):
    """A -- two distinct dirty trees share one digest."""

    def test_distinct_content_at_same_status_yields_distinct_digest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _seed_repo(root)
            environment = GitEnvironment(repo_path=root)

            # Both writes leave the tree dirty with the identical porcelain
            # line ` M module.py`; only the bytes differ.
            (root / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
            first = environment.snapshot().value

            (root / "module.py").write_text("VALUE = 3\n", encoding="utf-8")
            second = environment.snapshot().value

            self.assertNotEqual(
                first.digest,
                second.digest,
                "two different candidate trees produced one digest: identity is "
                "derived from status codes, not content",
            )

    def test_untracked_file_content_is_not_in_the_digest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _seed_repo(root)
            environment = GitEnvironment(repo_path=root)

            (root / "added.py").write_text("HELPER = 1\n", encoding="utf-8")
            first = environment.snapshot().value

            (root / "added.py").write_text("HELPER = 2\n", encoding="utf-8")
            second = environment.snapshot().value

            self.assertNotEqual(
                first.digest,
                second.digest,
                "untracked content changed but the digest did not: `?? added.py` "
                "is the whole contribution",
            )


class TestCandidateIdentityDegradation(unittest.TestCase):
    """B -- a failing git yields a valid-looking constant digest."""

    def test_enumeration_failure_is_reported_not_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # A real directory that is not a repository: `git` is on PATH so the
            # constructor admits it, but `rev-parse` and `status` both exit
            # non-zero. The adapter substitutes "unknown" and "" and returns a
            # well-formed digest over that substitution.
            environment = GitEnvironment(repo_path=root)

            result = environment.snapshot()

            self.assertFalse(
                result.ok,
                "snapshot over an unreadable tree returned success; an "
                "enumeration failure must produce a failed Result, never a "
                "degraded-but-plausible digest",
            )

    def test_two_unreadable_trees_do_not_share_one_digest(self) -> None:
        with tempfile.TemporaryDirectory() as first_td, tempfile.TemporaryDirectory() as second_td:
            first_root = Path(first_td)
            second_root = Path(second_td)
            (first_root / "a.py").write_text("A = 1\n", encoding="utf-8")
            (second_root / "b.py").write_text("B = 2\n", encoding="utf-8")

            first = GitEnvironment(repo_path=first_root).snapshot()
            second = GitEnvironment(repo_path=second_root).snapshot()

            if first.ok and second.ok:
                self.assertNotEqual(
                    first.value.digest,
                    second.value.digest,
                    "two unrelated trees degraded to the same constant digest "
                    'over {"head": "unknown", "status": ""}',
                )


class TestCandidateIdentityAcrossWorkspaces(unittest.TestCase):
    """C -- the live observation: distinct workspaces, one digest."""

    def test_distinct_workspaces_at_same_head_yield_distinct_digests(self) -> None:
        with tempfile.TemporaryDirectory() as origin_td, tempfile.TemporaryDirectory() as clone_td:
            origin = Path(origin_td)
            _seed_repo(origin)

            clone = Path(clone_td) / "clone"
            subprocess.run(
                ["git", "clone", "-q", str(origin), str(clone)],
                check=True,
                capture_output=True,
            )

            # Same commit, same modified path, different candidate content --
            # the shape the evaluation reported as identical candidate digests
            # for different workspaces.
            (origin / "module.py").write_text("VALUE = 'origin'\n", encoding="utf-8")
            (clone / "module.py").write_text("VALUE = 'clone'\n", encoding="utf-8")

            origin_snapshot = GitEnvironment(repo_path=origin).snapshot().value
            clone_snapshot = GitEnvironment(repo_path=clone).snapshot().value

            self.assertEqual(
                origin_snapshot.metadata["head_commit"],
                clone_snapshot.metadata["head_commit"],
                "precondition: both workspaces must sit at the same HEAD",
            )
            self.assertNotEqual(
                origin_snapshot.digest,
                clone_snapshot.digest,
                "two different workspaces produced one candidate digest",
            )


if __name__ == "__main__":
    unittest.main()
