"""S-M3-B-01: anchored AST patch + structural diff."""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"


class AstPatchTests(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(PACK))
        from load import load_declared_entry
        from vanguard.packages.domain.wire.types_gen import EffectContext, EffectRequest, Reservation, SinkClass

        self.tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmpdir.name)
        Toolkit = load_declared_entry("mhf.toolkit.ast-patch")
        self.toolkit = Toolkit(self.workspace)
        self.ctx = EffectContext(principal="t", run_id="r1")
        self._req = EffectRequest
        self._res = Reservation
        self._sink = SinkClass

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _request(self, **args: object):
        return self._req(
            verb="patch.apply",
            args=args,
            selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
            sink=self._sink.PRIVILEGED,
            reservation=self._res(0, 0, 0, 0, 1, 1),
        )

    def test_anchored_edit_replaces_function(self) -> None:
        import ast

        target = self.workspace / "mod.py"
        source = "def foo():\n    return 1\n"
        target.write_text(source, encoding="utf-8")
        node = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef) and n.name == "foo")
        segment = ast.get_source_segment(source, node) or ""
        digest = "sha256:" + hashlib.sha256(segment.encode("utf-8")).hexdigest()
        result = self.toolkit.execute(
            self._request(
                path="mod.py",
                node_kind="FunctionDef",
                qualified_name="foo",
                anchor_digest=digest,
                replacement="def foo():\n    return 2\n",
            ),
            self.ctx,
        )
        from vanguard.packages.domain.wire.result import Ok
        self.assertIsInstance(result, Ok)
        self.assertEqual(result.value.outcome, "completed")
        self.assertIn("return 2", target.read_text(encoding="utf-8"))
        self.assertTrue(result.value.artifacts)

    def test_search_replace_fallback(self) -> None:
        (self.workspace / "a.py").write_text("x = 1\n", encoding="utf-8")
        result = self.toolkit.execute(
            self._request(path="a.py", old="x = 1", new="x = 2"),
            self.ctx,
        )
        self.assertEqual(result.value.outcome, "completed")
        self.assertEqual((self.workspace / "a.py").read_text(encoding="utf-8"), "x = 2\n")

    def test_structural_diff_reports_added_symbol(self) -> None:
        sys.path.insert(0, str(PACK / "toolkits"))
        from ast_patch import structural_diff

        diff = structural_diff("def a():\n    return 0\n", "def a():\n    return 0\n\ndef b():\n    return 1\n", "m.py")
        self.assertIn("function:b", diff["added"])


if __name__ == "__main__":
    unittest.main()
