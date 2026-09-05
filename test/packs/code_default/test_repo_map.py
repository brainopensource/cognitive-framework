"""S-M3-B-02: Merkle index + receipt-driven dirty set + repo-map budget."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"


class RepoMapTests(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(PACK))
        from load import load_declared_entry

        self.tmpdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmpdir.name)
        (self.workspace / "src").mkdir()
        (self.workspace / "src" / "app.py").write_text("def hello():\n    return 1\n", encoding="utf-8")
        Index = load_declared_entry("mhf.toolkit.index")
        Context = load_declared_entry("mhf.context.repo-map")
        self.index = Index(self.workspace)
        self.context = Context(system_prefix="SYS\n", index=self.index, token_budget=64)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_merkle_changes_when_file_changes(self) -> None:
        first = self.index.scan()
        (self.workspace / "src" / "app.py").write_text("def hello():\n    return 2\n", encoding="utf-8")
        second = self.index.scan()
        self.assertNotEqual(first, second)
        self.assertTrue(any(item["name"] == "hello" for item in self.index._symbols))

    def test_receipt_marks_dirty_subtree(self) -> None:
        from vanguard.packages.domain.wire.types_gen import ArtifactRef, Receipt, Reservation

        self.index.scan()
        receipt = Receipt(
            request_digest="sha256:" + "a" * 64,
            outcome="completed",
            cost=Reservation(0, 0, 0, 0, 1, 1),
            artifacts=(ArtifactRef(digest="sha256:" + "b" * 64, kind="src/app.py"),),
        )
        self.index.ingest((receipt,))
        self.assertIn("src/app.py", self.index._dirty)

    def test_context_compile_respects_token_budget(self) -> None:
        from vanguard.packages.domain.wire.result import Ok
        from vanguard.packages.domain.wire.types_gen import EpisodeView

        compiled = self.context.compile(EpisodeView("r", "e", 1, "goal"), budget_tokens=16)
        self.assertIsInstance(compiled, Ok)
        self.assertLessEqual(len(compiled.value.suffix), 16 * 4)

    def test_index_refresh_includes_new_symbol(self) -> None:
        from vanguard.packages.domain.wire.result import Ok
        from vanguard.packages.domain.wire.types_gen import EffectContext, EffectRequest, Reservation, SinkClass

        self.index.scan()
        rendered_before = self.index.render(4000)
        self.assertIn("hello", rendered_before)
        self.assertNotIn("added_after_write", rendered_before)
        (self.workspace / "src" / "app.py").write_text(
            "def hello():\n    return 1\n\ndef added_after_write():\n    return 2\n",
            encoding="utf-8",
        )
        result = self.index.execute(
            EffectRequest(
                verb="index.refresh",
                args={},
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
                sink=SinkClass.OBSERVATION,
                reservation=Reservation(0, 0, 0, 0, 1, 1),
            ),
            EffectContext(principal="t", run_id="r1", episode_id="e1"),
        )
        self.assertIsInstance(result, Ok)
        rendered = self.index.render(4000)
        self.assertIn("added_after_write", rendered)
        self.assertTrue(any(item["name"] == "added_after_write" for item in self.index._symbols))


if __name__ == "__main__":
    unittest.main()
