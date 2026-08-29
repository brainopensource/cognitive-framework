"""Shared substitution contract for every active EnvironmentAdapter implementation.

Owning contract: REQ-PORT-003 / TEST-PORT-003, ICD §4 EnvironmentAdapter, VG-03 §7.1.
Absorbs: docs/agile/sprint2/slice-findings.md.
"""

from __future__ import annotations

import socket
import unittest
from contextlib import contextmanager
from typing import Callable, Iterator
from unittest.mock import patch

import subprocess
import tempfile
from pathlib import Path
from vanguard.packages.adapters.environment import FakeEnvironment, GitEnvironment
from vanguard.packages.ports.environment import (
    EffectRequest,
    EnvironmentAdapter,
    ObservationRequest,
)

SAMPLE_FILES = {
    "src/hello.py": "def hello():\n    return 'world'\n",
    "README.md": "# Hello World\nWelcome to Vanguard.\n",
}

NEW_FILE_PATCH = """--- /dev/null
+++ b/src/greet.py
@@ -0,0 +1,2 @@
+def greet(name):
+    return f"Hello, {name}!"
"""

MOD_FILE_PATCH = """--- a/src/hello.py
+++ b/src/hello.py
@@ -1,2 +1,2 @@
 def hello():
-    return 'world'
+    return 'vanguard'
"""

DEL_FILE_PATCH = """--- a/README.md
+++ /dev/null
@@ -1,2 +0,0 @@
-# Hello World
-Welcome to Vanguard.
"""


@contextmanager
def _fake_environment_factory() -> Iterator[EnvironmentAdapter]:
    env = FakeEnvironment(initial_files=SAMPLE_FILES)
    try:
        yield env
    finally:
        env.dispose()


@contextmanager
def _git_environment_factory() -> Iterator[EnvironmentAdapter]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_path = Path(tmp_dir) / "repo"
        repo_path.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=repo_path, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Vanguard Test"], cwd=repo_path, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@vanguard.dev"], cwd=repo_path, capture_output=True, check=True)

        for rel_path, content in SAMPLE_FILES.items():
            f_path = repo_path / rel_path
            f_path.parent.mkdir(parents=True, exist_ok=True)
            f_path.write_text(content, encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, capture_output=True, check=True)

        env = GitEnvironment(repo_path=repo_path)
        try:
            yield env
        finally:
            env.dispose()


class EnvironmentPortContract(unittest.TestCase):
    """The same success and failure behaviour runs against fake and real adapters."""

    def _get_factories(self) -> tuple[tuple[str, Callable[[], Iterator[EnvironmentAdapter]]], ...]:
        return (
            ("fake", _fake_environment_factory),
            ("git", _git_environment_factory),
        )

    def test_profile_and_snapshot(self) -> None:
        for name, factory in self._get_factories():
            with self.subTest(implementation=name), factory() as env:
                profile_res = env.profile()
                self.assertTrue(profile_res.ok)
                self.assertIsNotNone(profile_res.value)
                self.assertIn("observe", profile_res.value.capabilities)
                self.assertIn("preview", profile_res.value.capabilities)
                self.assertIn("apply", profile_res.value.capabilities)

                snap_res = env.snapshot()
                self.assertTrue(snap_res.ok)
                self.assertIsNotNone(snap_res.value)
                self.assertTrue(snap_res.value.digest.startswith("sha256:"))

    def test_observe_read_and_search(self) -> None:
        for name, factory in self._get_factories():
            with self.subTest(implementation=name), factory() as env:
                # Read existing
                read_res = env.observe(ObservationRequest(action="read", path="src/hello.py"))
                self.assertTrue(read_res.ok)
                self.assertIsNotNone(read_res.value)
                self.assertEqual(read_res.value.content, SAMPLE_FILES["src/hello.py"])

                # Read non-existent
                missing_res = env.observe(ObservationRequest(action="read", path="non_existent.py"))
                self.assertFalse(missing_res.ok)
                self.assertIsNotNone(missing_res.error)
                self.assertEqual(missing_res.error.kind, "not_found")

                # Search
                search_res = env.observe(ObservationRequest(action="search", pattern="Vanguard"))
                self.assertTrue(search_res.ok)
                self.assertIsNotNone(search_res.value)
                self.assertIn("README.md", search_res.value.files)

    def test_preview_and_apply_new_file(self) -> None:
        """Preview MUST include new files (REQ-PORT-003, dd-packet.md)."""
        for name, factory in self._get_factories():
            with self.subTest(implementation=name), factory() as env:
                # 1. Preview new file patch
                preview_res = env.preview(
                    EffectRequest(
                        verb="patch.apply",
                        action="patch",
                        patch=NEW_FILE_PATCH,
                    )
                )
                self.assertTrue(preview_res.ok)
                self.assertIsNotNone(preview_res.value)
                preview = preview_res.value
                self.assertIn("src/greet.py", preview.new_files)
                self.assertEqual(len(preview.affected_resources), 1)
                self.assertEqual(preview.affected_resources[0].resource, "src/greet.py")
                self.assertEqual(preview.affected_resources[0].change, "created")
                self.assertIn("def greet(name):", preview.diff)

                # 2. Apply new file patch
                apply_res = env.apply(
                    EffectRequest(
                        verb="patch.apply",
                        action="patch",
                        patch=NEW_FILE_PATCH,
                    )
                )
                self.assertTrue(apply_res.ok)
                self.assertIsNotNone(apply_res.value)
                receipt = apply_res.value
                self.assertEqual(receipt.outcome, "ok")
                self.assertEqual(len(receipt.affected_resources), 1)
                self.assertEqual(receipt.affected_resources[0].resource, "src/greet.py")
                self.assertEqual(receipt.affected_resources[0].change, "created")

                # 3. Observe created file
                read_res = env.observe(ObservationRequest(action="read", path="src/greet.py"))
                self.assertTrue(read_res.ok)
                self.assertIn("def greet(name):", read_res.value.content or "")

                # 4. Reconcile
                rec_res = env.reconcile(receipt)
                self.assertTrue(rec_res.ok)
                self.assertTrue(rec_res.value.matched)

    def test_preview_and_apply_modification_and_deletion(self) -> None:
        for name, factory in self._get_factories():
            with self.subTest(implementation=name), factory() as env:
                # Modification preview & apply
                mod_preview = env.preview(EffectRequest(verb="patch.apply", action="patch", patch=MOD_FILE_PATCH))
                self.assertTrue(mod_preview.ok)
                self.assertIn("src/hello.py", mod_preview.value.modified_files)

                mod_apply = env.apply(EffectRequest(verb="patch.apply", action="patch", patch=MOD_FILE_PATCH))
                self.assertTrue(mod_apply.ok)
                self.assertEqual(mod_apply.value.affected_resources[0].change, "modified")

                read_mod = env.observe(ObservationRequest(action="read", path="src/hello.py"))
                self.assertIn("vanguard", read_mod.value.content or "")

                # Deletion preview & apply
                del_preview = env.preview(EffectRequest(verb="patch.apply", action="patch", patch=DEL_FILE_PATCH))
                self.assertTrue(del_preview.ok)
                self.assertIn("README.md", del_preview.value.deleted_files)

                del_apply = env.apply(EffectRequest(verb="patch.apply", action="patch", patch=DEL_FILE_PATCH))
                self.assertTrue(del_apply.ok)
                self.assertEqual(del_apply.value.affected_resources[0].change, "deleted")

                read_del = env.observe(ObservationRequest(action="read", path="README.md"))
                self.assertFalse(read_del.ok)
                self.assertEqual(read_del.error.kind, "not_found")

    def test_path_traversal_escape_rejected(self) -> None:
        """Zero path-escape applies (margin in REQ-PORT-003, slice-findings.md)."""
        traversal_paths = [
            "../secret.txt",
            "../../etc/passwd",
            "src/../../outside.txt",
            "/etc/shadow",
        ]
        for name, factory in self._get_factories():
            with self.subTest(implementation=name), factory() as env:
                for bad_path in traversal_paths:
                    # Observation path traversal
                    obs = env.observe(ObservationRequest(action="read", path=bad_path))
                    self.assertFalse(obs.ok, f"Expected observe to reject {bad_path}")
                    self.assertIn(obs.error.kind, ("denied", "invalid_request"))

                    # Write path traversal
                    write_prev = env.preview(EffectRequest(verb="fs.write", action="write", args={"path": bad_path, "content": "x"}))
                    self.assertFalse(write_prev.ok, f"Expected write preview to reject {bad_path}")
                    self.assertIn(write_prev.error.kind, ("denied", "invalid_request"))

                    # Patch path traversal
                    bad_patch = f"--- /dev/null\n+++ b/{bad_path}\n@@ -0,0 +1 @@\n+escaped\n"
                    patch_prev = env.preview(EffectRequest(verb="patch.apply", action="patch", patch=bad_patch))
                    self.assertFalse(patch_prev.ok, f"Expected patch preview to reject {bad_path}")
                    self.assertIn(patch_prev.error.kind, ("denied", "invalid_request"))

    def test_model_text_is_not_a_patch_rejection(self) -> None:
        """Provider text cannot be treated as a patch (slice-findings.md)."""
        for name, factory in self._get_factories():
            with self.subTest(implementation=name), factory() as env:
                # Raw prose
                prose = "Here is the code you asked for:\n```python\nprint('hello')\n```"
                prev = env.preview(EffectRequest(verb="patch.apply", action="patch", patch=prose))
                self.assertFalse(prev.ok)
                self.assertEqual(prev.error.kind, "invalid_request")

                # Malformed patch
                malformed = "--- a/src/hello.py\n+++ b/src/hello.py\ncorrupted patch"
                prev_mal = env.preview(EffectRequest(verb="patch.apply", action="patch", patch=malformed))
                self.assertFalse(prev_mal.ok)
                self.assertEqual(prev_mal.error.kind, "invalid_request")

                # A model may omit line ranges, but the hunk marker itself is
                # still unambiguous. The adapter anchors it to the old-file
                # context; it must not silently discard the proposed change.
                bare_header = """--- a/src/hello.py
+++ b/src/hello.py
@@
 def hello():
-    return 'world'
+    return 'vanguard'
"""
                bare = env.preview(EffectRequest(verb="patch.apply", action="patch", patch=bare_header))
                self.assertTrue(bare.ok, getattr(bare, "error", None))

                # Patch conflict (context mismatch)
                conflict_patch = """--- a/src/hello.py
+++ b/src/hello.py
@@ -1,2 +1,2 @@
 def nonexistent_function():
-    return 'world'
+    return 'vanguard'
"""
                prev_conf = env.preview(EffectRequest(verb="patch.apply", action="patch", patch=conflict_patch))
                self.assertFalse(prev_conf.ok)
                self.assertEqual(prev_conf.error.kind, "conflict")

    def test_test_command_requires_argv_array_rejects_shell_string(self) -> None:
        """Test commands must cross boundary as argv, never a shell string (REQ-PORT-003)."""
        for name, factory in self._get_factories():
            with self.subTest(implementation=name), factory() as env:
                # Reject shell string in preview
                str_prev = env.preview(EffectRequest(verb="test.run", action="test", command="pytest tests/"))
                self.assertFalse(str_prev.ok)
                self.assertEqual(str_prev.error.kind, "invalid_request")

                # Reject shell string in apply
                str_apply = env.apply(EffectRequest(verb="test.run", action="test", command="pytest tests/"))
                self.assertFalse(str_apply.ok)
                self.assertEqual(str_apply.error.kind, "invalid_request")

                # Accept argv list of strings
                argv = ["python3", "-c", "print('OK')"]
                valid_prev = env.preview(EffectRequest(verb="test.run", action="test", command=argv))
                self.assertTrue(valid_prev.ok)

                valid_apply = env.apply(EffectRequest(verb="test.run", action="test", command=argv))
                self.assertTrue(valid_apply.ok)
                self.assertEqual(valid_apply.value.outcome, "ok")
                self.assertEqual(valid_apply.value.exit_code, 0)

    def test_compensate_reverts_applied_effect(self) -> None:
        for name, factory in self._get_factories():
            with self.subTest(implementation=name), factory() as env:
                # Apply new file
                apply_res = env.apply(EffectRequest(verb="patch.apply", action="patch", patch=NEW_FILE_PATCH))
                self.assertTrue(apply_res.ok)
                receipt = apply_res.value

                # Compensate
                comp_res = env.compensate(receipt)
                self.assertTrue(comp_res.ok)

                # Created file is gone
                obs = env.observe(ObservationRequest(action="read", path="src/greet.py"))
                self.assertFalse(obs.ok)
                self.assertEqual(obs.error.kind, "not_found")

    def test_git_worktree_isolation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_path = Path(tmp_dir) / "repo"
            repo_path.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=repo_path, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.name", "Vanguard Test"], cwd=repo_path, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "test@vanguard.dev"], cwd=repo_path, capture_output=True, check=True)
            (repo_path / "a.txt").write_text("initial main\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, capture_output=True, check=True)

            wt_dir = Path(tmp_dir) / "wt"
            env = GitEnvironment(repo_path=repo_path, worktree_branch="feature-1", worktree_dir=wt_dir)
            try:
                self.assertEqual(env.working_dir, wt_dir)
                write_res = env.apply(EffectRequest(verb="fs.write", action="write", args={"path": "b.txt", "content": "worktree file"}))
                self.assertTrue(write_res.ok)
                # Worktree has b.txt
                self.assertTrue((wt_dir / "b.txt").exists())
                # Main repo does not have b.txt
                self.assertFalse((repo_path / "b.txt").exists())
            finally:
                env.dispose()
            # Disposing removed the worktree
            self.assertFalse(wt_dir.exists())


class GitUnavailableFailsClosed(unittest.TestCase):
    """BETA-11: a sparse host with no `git` on `PATH` must never crash.

    The M7 topology falsifiers route real work through `GitEnvironment`; a
    host missing `git` used to surface a raw `FileNotFoundError` from deep
    inside `subprocess.run`, which is exactly what the sparse-environment
    regression looked like. Every port method now fails closed with a typed
    `unavailable` Result, and construction itself refuses up front.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo_path = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_construction_refuses_with_a_typed_error_not_a_crash(self) -> None:
        from vanguard.packages.adapters.environment.git import GitUnavailableError

        with patch("shutil.which", return_value=None):
            with self.assertRaises(GitUnavailableError):
                GitEnvironment(repo_path=self.repo_path)

    def test_every_port_method_returns_unavailable_once_git_disappears(self) -> None:
        subprocess.run(["git", "init", "-b", "main"], cwd=self.repo_path, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Vanguard Test"], cwd=self.repo_path, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@vanguard.dev"], cwd=self.repo_path, capture_output=True, check=True)
        env = GitEnvironment(repo_path=self.repo_path)
        try:
            with patch("shutil.which", return_value=None):
                for label, result in (
                    ("profile", env.profile()),
                    ("snapshot", env.snapshot()),
                    ("observe", env.observe(ObservationRequest(action="read", path="a.txt"))),
                    ("preview", env.preview(EffectRequest(verb="fs.write", action="write", args={"path": "a.txt", "content": "x"}))),
                    ("apply", env.apply(EffectRequest(verb="fs.write", action="write", args={"path": "a.txt", "content": "x"}))),
                ):
                    with self.subTest(method=label):
                        self.assertFalse(result.ok, f"{label} must fail, not raise, when git is gone")
                        self.assertEqual(result.error.kind, "unavailable")
        finally:
            env.dispose()


if __name__ == "__main__":
    unittest.main()
