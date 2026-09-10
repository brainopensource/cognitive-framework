"""D6: the patch applier locates a hunk by context, as patch(1) does.

Every diff here is one deepseek actually emitted during the failed RF-95
attempt, or a variation of it. The applier previously demanded that a hunk sit
at the exact line its header claimed, so a correct fix with an absent or wrong
offset was rejected as a context mismatch -- stricter than git apply, and the
proximate cause of the RF-95 failure. Anchoring must not become guessing: the
last test proves a hunk matching nothing is still refused and the file is left
byte-identical."""

"""D6: the patch applier locates a hunk by context, as patch(1) does.

Every diff here is one deepseek actually emitted during the failed RF-95
attempt, or a variation of it. The applier previously demanded that a hunk sit
at the exact line its header claimed, so a correct fix with an absent or wrong
offset was rejected as a context mismatch -- stricter than git apply, and the
proximate cause of the RF-95 failure. Anchoring must not become guessing: the
last test proves a hunk matching nothing is still refused and the file is left
byte-identical."""

import os
import stat
import tempfile
import subprocess
import unittest
from pathlib import Path
from vanguard.packages.adapters.environment.git import GitEnvironmentAdapter
from vanguard.packages.domain.canonicalisation.digest import digest_bytes
from vanguard.packages.ports.environment import EffectRequest

SRC = "def add(a: int, b: int) -> int:\n    return a + b\n\ndef multiply(a: int, b: int) -> int:\n    return 0  # BUG: should multiply\n"

# The literal diff deepseek emitted in the failed RF-95 run.
BARE = "--- a/src/calc.py\n+++ b/src/calc.py\n@@\n def multiply(a: int, b: int) -> int:\n-    return 0  # BUG: should multiply\n+    return a * b"
NOHDR = "@@\n def multiply(a: int, b: int) -> int:\n-    return 0  # BUG: should multiply\n+    return a * b"
WRONGLINE = "--- a/src/calc.py\n+++ b/src/calc.py\n@@ -1,2 +1,2 @@\n def multiply(a: int, b: int) -> int:\n-    return 0  # BUG: should multiply\n+    return a * b"
GOOD = "--- a/src/calc.py\n+++ b/src/calc.py\n@@ -4,2 +4,2 @@\n def multiply(a: int, b: int) -> int:\n-    return 0  # BUG: should multiply\n+    return a * b"
NOMATCH = "--- a/src/calc.py\n+++ b/src/calc.py\n@@\n def nonexistent(x):\n-    return 1\n+    return 2"

class T(unittest.TestCase):
    def _apply(self, diff):
        d = tempfile.mkdtemp()
        repo = Path(d)
        subprocess.run(["git","init","-b","main"],cwd=repo,capture_output=True)
        (repo/"src").mkdir()
        (repo/"src"/"calc.py").write_text(SRC)
        env = GitEnvironmentAdapter(repo)
        r = env.apply(EffectRequest(verb="patch.apply", action="patch",
                                    args={"path":"src/calc.py","diff":diff},
                                    patch=diff))
        return r, (repo/"src"/"calc.py").read_text()

    def test_bare_header_with_full_file_markers(self):
        r, txt = self._apply(BARE)
        self.assertTrue(r.ok, r.error and r.error.message)
        self.assertIn("return a * b", txt)

    def test_bare_header_without_file_markers(self):
        r, txt = self._apply(NOHDR)
        self.assertTrue(r.ok, r.error and r.error.message)
        self.assertIn("return a * b", txt)

    def test_wrong_line_numbers_still_anchor_on_context(self):
        r, txt = self._apply(WRONGLINE)
        self.assertTrue(r.ok, r.error and r.error.message)
        self.assertIn("return a * b", txt)

    def test_correct_header_still_works(self):
        r, txt = self._apply(GOOD)
        self.assertTrue(r.ok, r.error and r.error.message)
        self.assertIn("return a * b", txt)

    def test_context_that_matches_nothing_is_still_refused(self):
        r, txt = self._apply(NOMATCH)
        self.assertFalse(r.ok)
        self.assertEqual(r.error.kind, "conflict")
        self.assertEqual(txt, SRC)  # untouched

    def test_add_is_untouched(self):
        r, txt = self._apply(BARE)
        self.assertIn("return a + b", txt)

if __name__ == "__main__":
    unittest.main(verbosity=2)


AMBIG_SRC = "def a():\n    pass\n\ndef b():\n    pass\n"
# Context that occurs twice, with no line numbers to disambiguate.
AMBIG = "--- a/src/calc.py\n+++ b/src/calc.py\n@@\n     pass\n+    # touched"


class Ambiguity(unittest.TestCase):
    def test_an_ambiguous_headerless_hunk_is_refused_not_guessed(self) -> None:
        d = tempfile.mkdtemp()
        repo = Path(d)
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, capture_output=True)
        (repo / "src").mkdir()
        (repo / "src" / "calc.py").write_text(AMBIG_SRC)
        env = GitEnvironmentAdapter(repo)
        r = env.apply(EffectRequest(verb="patch.apply", action="patch",
                                    args={"path": "src/calc.py", "diff": AMBIG},
                                    patch=AMBIG))
        self.assertFalse(r.ok)
        self.assertIn("ambiguous", r.error.message)
        # Anchoring must never silently edit the wrong location.
        self.assertEqual((repo / "src" / "calc.py").read_text(), AMBIG_SRC)


INCOMPLETE = "--- a/src/calc.py\n+++ b/src/calc.py\n@@\n"
TRUNCATED = (
    "--- a/src/calc.py\n+++ b/src/calc.py\n"
    "@@\n def multiply(a: int, b: int) -> int:\n"
)
BAD_COUNTS = (
    "--- a/src/calc.py\n+++ b/src/calc.py\n"
    "@@ -4,99 +4,98 @@\n"
    " def multiply(a: int, b: int) -> int:\n"
    "-    return 0  # BUG: should multiply\n"
    "+    return a * b"
)


class FaultMutation(unittest.TestCase):
    def _repo(self, source: str = SRC) -> tuple[Path, Path, GitEnvironmentAdapter]:
        d = tempfile.mkdtemp()
        repo = Path(d)
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, capture_output=True)
        (repo / "src").mkdir()
        target = repo / "src" / "calc.py"
        target.write_text(source)
        os.chmod(target, 0o640)
        return repo, target, GitEnvironmentAdapter(repo)

    def test_changed_preimage_is_rejected(self) -> None:
        repo, target, env = self._repo()
        stale = digest_bytes(SRC.encode("utf-8"))
        mutated = SRC.replace("def add", "def sum")
        target.write_text(mutated)
        os.chmod(target, 0o640)
        result = env.apply(
            EffectRequest(
                verb="patch.apply",
                action="patch",
                args={
                    "path": "src/calc.py",
                    "diff": BARE,
                    "expected_preimage": stale,
                },
                patch=BARE,
            )
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "conflict")
        self.assertIn("stale preimage", result.error.message)
        self.assertEqual(target.read_text(), mutated)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)

    def test_ambiguous_anchoring_is_rejected(self) -> None:
        repo, target, env = self._repo(AMBIG_SRC)
        result = env.apply(
            EffectRequest(
                verb="patch.apply",
                action="patch",
                args={"path": "src/calc.py", "diff": AMBIG},
                patch=AMBIG,
            )
        )
        self.assertFalse(result.ok)
        self.assertIn("ambiguous", result.error.message)
        self.assertEqual(target.read_text(), AMBIG_SRC)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)

    def test_incomplete_hunk_is_rejected_and_preserves_mode(self) -> None:
        repo, target, env = self._repo()
        result = env.apply(
            EffectRequest(
                verb="patch.apply",
                action="patch",
                args={"path": "src/calc.py", "diff": INCOMPLETE},
                patch=INCOMPLETE,
            )
        )
        self.assertFalse(result.ok)
        self.assertIn("incomplete", result.error.message)
        self.assertEqual(target.read_text(), SRC)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)

    def test_truncated_hunk_without_edits_is_rejected(self) -> None:
        repo, target, env = self._repo()
        result = env.apply(
            EffectRequest(
                verb="patch.apply",
                action="patch",
                args={"path": "src/calc.py", "diff": TRUNCATED},
                patch=TRUNCATED,
            )
        )
        self.assertFalse(result.ok)
        self.assertIn("incomplete", result.error.message)
        self.assertEqual(target.read_text(), SRC)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)

    def test_declared_hunk_counts_must_match_the_body(self) -> None:
        repo, target, env = self._repo()
        result = env.apply(
            EffectRequest(
                verb="patch.apply",
                action="patch",
                args={"path": "src/calc.py", "diff": BAD_COUNTS},
                patch=BAD_COUNTS,
            )
        )
        self.assertFalse(result.ok)
        self.assertIn("hunk line count mismatch", result.error.message)
        self.assertEqual(target.read_text(), SRC)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)

    def test_prefixed_blank_context_line_is_part_of_a_complete_hunk(self) -> None:
        repo, target, env = self._repo()
        diff = (
            "--- a/src/calc.py\n+++ b/src/calc.py\n@@ -3,3 +3,3 @@\n"
            " \n"
            " def multiply(a: int, b: int) -> int:\n"
            "-    return 0  # BUG: should multiply\n"
            "+    return a * b"
        )
        result = env.apply(
            EffectRequest(
                verb="patch.apply", action="patch",
                args={"path": "src/calc.py", "diff": diff}, patch=diff,
            )
        )
        self.assertTrue(result.ok)
        self.assertIn("return a * b", target.read_text())
