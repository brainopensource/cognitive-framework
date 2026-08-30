"""Tests for FsToolkit range reads, search, and list."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from toolkits.fs_toolkit import FsToolkit
from vanguard.packages.domain.wire.result import Err, Ok
from vanguard.packages.domain.wire.types_gen import EffectContext, EffectRequest, Reservation, SinkClass


class FsToolkitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.toolkit = FsToolkit(self.root)
        self.ctx = EffectContext(principal="test", run_id="r1", episode_id="e1")
        self.cost = Reservation(0, 0, 0, 0, 1, 1)
        self.selector = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
        self.sink = SinkClass.OBSERVATION

        # Create sample files
        (self.root / "sample.py").write_text("line1\nline2\nline3\nline4\nline5\n", encoding="utf-8")
        (self.root / "sub").mkdir()
        (self.root / "sub" / "inner.txt").write_text("hello world\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_read_whole_file(self) -> None:
        req = EffectRequest(
            verb="fs.read",
            args={"path": "sample.py"},
            selector=self.selector,
            sink=self.sink,
            reservation=self.cost,
        )
        res = self.toolkit.execute(req, self.ctx)
        self.assertIsInstance(res, Ok)

    def test_read_line_range(self) -> None:
        req = EffectRequest(
            verb="fs.read",
            args={"path": "sample.py", "start_line": 2, "end_line": 4},
            selector=self.selector,
            sink=self.sink,
            reservation=self.cost,
        )
        res = self.toolkit.execute(req, self.ctx)
        self.assertIsInstance(res, Ok)

    def test_search_files(self) -> None:
        req = EffectRequest(
            verb="fs.search",
            args={"pattern": "hello"},
            selector=self.selector,
            sink=self.sink,
            reservation=self.cost,
        )
        res = self.toolkit.execute(req, self.ctx)
        self.assertIsInstance(res, Ok)

    def test_list_files(self) -> None:
        req = EffectRequest(
            verb="fs.list",
            args={"pattern": "*.py"},
            selector=self.selector,
            sink=self.sink,
            reservation=self.cost,
        )
        res = self.toolkit.execute(req, self.ctx)
        self.assertIsInstance(res, Ok)

    def test_escape_rejected_fail_closed(self) -> None:
        req = EffectRequest(
            verb="fs.read",
            args={"path": "../../etc/passwd"},
            selector=self.selector,
            sink=self.sink,
            reservation=self.cost,
        )
        res = self.toolkit.execute(req, self.ctx)
        self.assertIsInstance(res, Err)
        self.assertEqual(res.code, "denied")


if __name__ == "__main__":
    unittest.main()
