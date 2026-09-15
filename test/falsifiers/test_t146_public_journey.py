"""T-146 / E5 -- public journey evidence through `entrypoint.execute`.

One greenfield multi-file creation and one brownfield multi-file change,
each with exterior verification of the exact submitted candidate, complete
changed-file attribution and honest cost accounting. Scripted model,
disposable WAL, no provider.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime import entrypoint


def _event_kind(event: Any) -> str:
    """Durable kind as the fold resolves it: payload, then mhf_kind, then kind."""
    payload = getattr(event, "payload", None)
    if not isinstance(payload, Mapping):
        payload = {}
    return str(
        payload.get("kind")
        or getattr(event, "mhf_kind", "")
        or getattr(event, "kind", "")
        or ""
    )


def last_kind_payload(events: list[Any], kind: str) -> dict[str, Any] | None:
    found: dict[str, Any] | None = None
    for event in events:
        if _event_kind(event) != kind:
            continue
        payload = getattr(event, "payload", None)
        if isinstance(payload, Mapping):
            found = dict(payload)
    return found


FS = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
PROC = {
    "kind": "generic",
    "uriPattern": "proc://exec/allow/git,pytest,ruff,python3",
}

ALPHA_SRC = "def alpha(n):\n    return n + 1\n"
BETA_SRC = "def beta(n):\n    return n * 2\n"
PAIR_TEST = (
    "import unittest\n"
    "from pkg.alpha import alpha\n"
    "from pkg.beta import beta\n"
    "\n"
    "class Pair(unittest.TestCase):\n"
    "    def test_alpha(self):\n"
    "        self.assertEqual(alpha(1), 2)\n"
    "    def test_beta(self):\n"
    "        self.assertEqual(beta(3), 6)\n"
    "\n"
    "if __name__ == '__main__':\n"
    "    unittest.main()\n"
)

CALC_BUGGY = "def total(values):\n    result = 1\n    for value in values:\n        result += value\n    return result\n"
CALC_FIXED = CALC_BUGGY.replace("result = 1", "result = 0")
SCALE_BUGGY = "def scale(n):\n    return n + n + 1\n"
SCALE_FIXED = "def scale(n):\n    return n + n\n"
BROWN_TEST = (
    "import unittest\n"
    "from calc import total\n"
    "from scale import scale\n"
    "\n"
    "class Brown(unittest.TestCase):\n"
    "    def test_total(self):\n"
    "        self.assertEqual(total([1, 2, 3]), 6)\n"
    "    def test_scale(self):\n"
    "        self.assertEqual(scale(3), 6)\n"
    "\n"
    "if __name__ == '__main__':\n"
    "    unittest.main()\n"
)


def _git(workspace: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=workspace, check=True, capture_output=True)


def _init_repo(workspace: Path) -> None:
    _git(workspace, "init", "-q")
    _git(workspace, "config", "user.email", "t146@vanguard.test")
    _git(workspace, "config", "user.name", "t146")


def _patch(path: str, content: str) -> dict[str, Any]:
    return {
        "kind": "effect",
        "action": "patch.apply",
        "resource": FS,
        "args": {"path": path, "content": content},
        "note": f"write {path}",
    }


def _exec(argv: list[str], note: str) -> dict[str, Any]:
    return {
        "kind": "effect",
        "action": "proc.exec",
        "resource": PROC,
        "args": {"argv": argv},
        "note": note,
    }


class _PublicJourney(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name).resolve()
        self.workspace = root / "repo"
        self.workspace.mkdir()
        (self.workspace / "pyproject.toml").write_text(
            "[project]\nname='t146'\n", encoding="utf-8")
        _init_repo(self.workspace)
        # Disposable WAL lives *outside* the candidate. Git and sandbox
        # snapshots both rglob the working tree, so a store under
        # ``.vanguard/`` would make later ledger bytes a different tree
        # than the one verification bound -- the identity the journey
        # must keep equal.
        self.store_path = root / "wal" / "events.sqlite3"
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def execute(self, tape: list[dict[str, Any]], **overrides: Any) -> dict[str, Any]:
        request: dict[str, Any] = {
            "command": "code",
            "brief": "create two modules and verify them",
            "workspace": str(self.workspace),
            "storePath": str(self.store_path),
            "injectedModel": FakeModel(tape),
            "interactive": False,
            "profile": "product",
            "maxTurnsPerEpisode": 8,
        }
        request.update(overrides)
        return entrypoint.execute(request)

    def events(self, run_id: str) -> list[Any]:
        store = SqliteEventStore(str(self.store_path))
        try:
            read = store.read(EventRange(run_id=run_id))
        finally:
            store.close()
        return list(read.value or ()) if read.ok else []

    def assert_honest_cost(self, result: Mapping[str, Any]) -> None:
        spent = result.get("spentUsdMicros")
        self.assertTrue(spent in (None, 0), f"scripted run reported paid spend: {spent}")

    def assert_candidate_matches_tree(self, result: Mapping[str, Any], events: list[Any]) -> None:
        """Verification subject digest equals the submitted candidate digest."""
        verification = last_kind_payload(events, "VerificationRecorded")
        self.assertIsNotNone(verification, "the public route recorded no exterior verification")
        assert verification is not None
        subject = (
            verification.get("workspaceDigest") or verification.get("workspace_digest")
        )
        candidate = result.get("candidateDigest")
        identity = result.get("verificationIdentity") or {}
        published = identity.get("workspaceDigest") or candidate
        self.assertTrue(subject, "VerificationRecorded published no workspace digest")
        self.assertTrue(published, "the public receipt published no candidate digest")
        self.assertEqual(
            int(verification.get("exitCode", verification.get("exit_code", 1))), 0,
            "exterior verification of the submitted candidate did not pass")
        self.assertEqual(
            published, subject,
            "verification subject digest is not the submitted candidate "
            f"(receipt={published!r} verification={subject!r} "
            f"outcome={result.get('outcome')!r} detail={result.get('detail')!r})")
        if candidate and identity.get("workspaceDigest"):
            self.assertEqual(
                candidate, identity["workspaceDigest"],
                "candidateDigest and verificationIdentity.workspaceDigest diverged")

    def assert_changed_files(self, events: list[Any], expected: set[str]) -> None:
        surface = last_kind_payload(events, "ChangeSurfaceUpdated")
        self.assertIsNotNone(surface, "the public route recorded no change-surface attribution")
        assert surface is not None
        changed = {
            str(path).replace("\\", "/")
            for path in (surface.get("changeSurface") or surface.get("changedFiles") or ())
        }
        self.assertEqual(
            changed, expected,
            f"changed-file set {changed!r} does not exactly match candidate {expected!r}")


class GreenfieldMultiFileCreation(_PublicJourney):
    def test_public_route_creates_and_verifies_two_modules(self) -> None:
        (self.workspace / "pkg").mkdir()
        (self.workspace / "pkg" / "__init__.py").write_text("", encoding="utf-8")
        (self.workspace / "tests").mkdir()
        (self.workspace / "tests" / "__init__.py").write_text("", encoding="utf-8")
        _git(self.workspace, "add", "-A")
        _git(self.workspace, "commit", "-qm", "scaffold")

        tape = [
            _patch("pkg/alpha.py", ALPHA_SRC),
            _patch("pkg/beta.py", BETA_SRC),
            _patch("tests/test_pair.py", PAIR_TEST),
            _exec(["python3", "-m", "unittest", "tests.test_pair", "-v"],
                 "verify the pair"),
            {"kind": "finish", "note": "greenfield pair created"},
        ]
        frame = self.execute(tape, runId="run-t146-green",
                             brief="Create pkg.alpha and pkg.beta with tests")
        result = frame["result"]
        self.assertEqual(frame["type"], "result")
        self.assertEqual((self.workspace / "pkg" / "alpha.py").read_text(encoding="utf-8"), ALPHA_SRC)
        self.assertEqual((self.workspace / "pkg" / "beta.py").read_text(encoding="utf-8"), BETA_SRC)
        self.assertEqual((self.workspace / "tests" / "test_pair.py").read_text(encoding="utf-8"), PAIR_TEST)
        self.assert_honest_cost(result)
        events = self.events("run-t146-green")
        self.assertTrue(events, "the public route wrote no durable events")
        self.assert_candidate_matches_tree(result, events)
        self.assert_changed_files(events, {"pkg/alpha.py", "pkg/beta.py", "tests/test_pair.py"})


class BrownfieldMultiFileChange(_PublicJourney):
    def test_public_route_changes_and_verifies_two_existing_files(self) -> None:
        (self.workspace / "calc.py").write_text(CALC_BUGGY, encoding="utf-8")
        (self.workspace / "scale.py").write_text(SCALE_BUGGY, encoding="utf-8")
        (self.workspace / "test_brown.py").write_text(BROWN_TEST, encoding="utf-8")
        _git(self.workspace, "add", "-A")
        _git(self.workspace, "commit", "-qm", "buggy pair")

        tape = [
            _exec(["python3", "test_brown.py"], "reproduce"),
            _patch("calc.py", CALC_FIXED),
            _patch("scale.py", SCALE_FIXED),
            _exec(["python3", "test_brown.py"], "verify the fix"),
            {"kind": "finish", "note": "brownfield pair repaired"},
        ]
        frame = self.execute(
            tape, runId="run-t146-brown",
            brief="Fix the off-by-one bugs in calc.total and scale.scale")
        result = frame["result"]
        self.assertEqual(frame["type"], "result")
        self.assertEqual((self.workspace / "calc.py").read_text(encoding="utf-8"), CALC_FIXED)
        self.assertEqual((self.workspace / "scale.py").read_text(encoding="utf-8"), SCALE_FIXED)
        self.assert_honest_cost(result)
        events = self.events("run-t146-brown")
        self.assertTrue(events)
        self.assert_candidate_matches_tree(result, events)
        self.assert_changed_files(events, {"calc.py", "scale.py"})


if __name__ == "__main__":
    unittest.main()
