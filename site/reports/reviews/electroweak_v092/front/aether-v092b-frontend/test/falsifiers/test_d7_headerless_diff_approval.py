"""D7: a headerless hunk must survive approval *and* application identically.

The RF-95 attempts failed here, twice, and the second failure hid behind the
first. `deepseek` proposed the correct fix as a bare `@@` hunk carrying its
target in `args["path"]`. Two layers rejected it for opposite-looking reasons:

* `normalise_unified_diff` refused to build an approval challenge at all --
  correctly, because a signature over a diff with no filename is a signature
  over an ambiguity -- so `_resolve` returned `None` and the episode escalated
  before any effect started;
* the applier could not tell which file to open.

The fix normalises once at the runtime seam (`HarnessSession.dispatch`), so
the descriptor
digest, the bytes the approver signs, and the bytes written to disk are all
computed over the same text. Normalising in either layer alone would leave the
human approving one thing and the environment applying another -- exactly the
binding `K-15` re-verifies at resumption.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.blob_store import FileBlobStore
from vanguard.packages.runtime.session import _with_diff_headers
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.governance.approvals import (
    ApprovalFormatError,
    OperatorSigner,
    normalise_unified_diff,
)
from vanguard.packages.runtime.root import Runtime

from test.agency.doubles import ScriptedModel, finish

MANIFEST = "vanguard/packages/agency/manifests/vg-code-default/manifest.json"
#: Byte-for-byte what the model emitted during the failed RF-95 attempt.
BARE_DIFF = ("@@\n def multiply(a, b):\n-    return 0\n+    return a * b")


class IngressNormalisation(unittest.TestCase):
    @staticmethod
    def _req(args):
        from vanguard.packages.kernel.model import EffectRequest
        return EffectRequest(action="patch.apply", resource={}, args=args,
                             principal="p", run_id="r")

    def test_a_headerless_hunk_gains_the_path_it_was_addressed_to(self) -> None:
        out = _with_diff_headers(self._req({"path": "src/calc.py", "diff": BARE_DIFF}))
        self.assertTrue(
            out.args["diff"].startswith("--- a/src/calc.py\n+++ b/src/calc.py\n"))

    def test_a_diff_that_names_its_files_is_untouched(self) -> None:
        named = "--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-a\n+b"
        out = _with_diff_headers(self._req({"path": "y.py", "diff": named}))
        self.assertEqual(out.args["diff"], named)

    def test_a_non_diff_argument_set_is_untouched(self) -> None:
        args = {"path": "src/calc.py", "bytes": "12"}
        self.assertEqual(_with_diff_headers(self._req(args)).args, args)

    def test_the_raw_hunk_could_not_even_be_put_in_front_of_a_human(self) -> None:
        # The precondition that made this a silent escalation rather than an error.
        with self.assertRaises(ApprovalFormatError):
            normalise_unified_diff(BARE_DIFF)

    def test_the_normalised_hunk_can_be(self) -> None:
        headed = _with_diff_headers(
            self._req({"path": "src/calc.py", "diff": BARE_DIFF})).args["diff"]
        self.assertIn("--- a/src/calc.py", normalise_unified_diff(headed))


class ApprovedAndAppliedEndToEnd(unittest.TestCase):
    def test_a_headerless_patch_is_approved_and_lands_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            for argv in (["git", "init", "-b", "main"],
                         ["git", "config", "user.email", "d7@test"],
                         ["git", "config", "user.name", "d7"]):
                subprocess.run(argv, cwd=repo, capture_output=True, check=True)
            (repo / "src").mkdir()
            (repo / "src" / "calc.py").write_text("def multiply(a, b):\n    return 0\n")
            subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=repo,
                           capture_output=True, check=True)

            signer = OperatorSigner(b"vanguard-autonomous-operator-seed-key")
            script = [
                {"kind": "effect", "action": "patch.apply",
                 "resource": {"kind": "fs", "root": str(repo),
                              "paths": [str(repo / "src/calc.py")]},
                 "args": {"path": "src/calc.py", "diff": BARE_DIFF}, "text": ""},
                finish("fixed"),
            ]
            result = Runtime.execute_profiled(
                MANIFEST,
                TaskContext(brief="fix multiply", repo_path=repo, run_id="r-d7",
                            episode_id="e-d7", principal="agent-1", max_turns=4),
                profile_id="product",
                model=ScriptedModel(script),
                store_path=str(repo / ".vanguard" / "e.sqlite3"),
                blobs=FileBlobStore(repo / ".vanguard" / "blobs"),
                interactive=True,
                approver=lambda c: signer.approve(c, reviewer="autonomous-operator"),
                approval_key=signer.public_bytes,
            )
            applied = (repo / "src" / "calc.py").read_text()

        self.assertIn(("patch.apply", "ok"),
                      [(r.verb, r.outcome) for r in (result.receipts or ())],
                      f"terminal={result.terminal} detail={result.detail}")
        self.assertIn("return a * b", applied)

    def test_an_unsigned_run_still_refuses_the_same_patch(self) -> None:
        # The fix must not have turned approval into a formality.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            subprocess.run(["git", "init", "-b", "main"], cwd=repo,
                           capture_output=True, check=True)
            (repo / "src").mkdir()
            (repo / "src" / "calc.py").write_text("def multiply(a, b):\n    return 0\n")
            script = [
                {"kind": "effect", "action": "patch.apply",
                 "resource": {"kind": "fs", "root": str(repo),
                              "paths": [str(repo / "src/calc.py")]},
                 "args": {"path": "src/calc.py", "diff": BARE_DIFF}, "text": ""},
                finish("fixed"),
            ]
            Runtime.execute_profiled(
                MANIFEST,
                TaskContext(brief="fix multiply", repo_path=repo, run_id="r-d7b",
                            episode_id="e-d7b", principal="agent-1", max_turns=4),
                profile_id="product",
                model=ScriptedModel(script),
                store_path=str(repo / ".vanguard" / "e.sqlite3"),
                blobs=FileBlobStore(repo / ".vanguard" / "blobs"),
                interactive=True,
                approver=None,
            )
            self.assertNotIn("return a * b", (repo / "src" / "calc.py").read_text())


if __name__ == "__main__":
    unittest.main()
