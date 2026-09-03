"""LDA multi-language, standardizer, and health check tests (P2 increment).

Covers: standardizer (language/kind/tokens), TS/Rust/Go/Python extraction with
import edges, honest health check on empty/mixed indexes, and rebuild purge
hygiene for stale/deleted-file symbols.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from importlib import import_module
from pathlib import Path

atlas_mod = import_module("tools.007_LLM_DOCS_ATLAS.atlas")
config_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.config")
healthcheck_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.healthcheck")
standardizer_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.standardizer")
code_ast_mod = import_module("tools.007_LLM_DOCS_ATLAS.providers.code_ast")

AtlasContext = config_mod.AtlasContext
CodeASTProvider = code_ast_mod.CodeASTProvider


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _mkrepo(**files: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="lda-langs-"))
    for rel, content in files.items():
        _write(tmp, rel, content)
    return tmp


def _rm(repo: Path) -> None:
    shutil.rmtree(repo, ignore_errors=True)


_TS = """\
import { Event } from "@aether/contracts";
import "./polyfill.js";
export interface FrontendPersistencePort { save(): void; }
export type RunSummary = { id: string };
export const enum EventKind { START, STOP }
export function reduceRunSnapshot(state: RunSummary): RunSummary { return state; }
export class AppController { run(): void {} }
export const dispatch = (action: string) => action;
const SERVER_URL: string = "http://localhost";
"""

_RS = """\
use std::collections::HashMap;
pub use crate::util::spawn;
pub struct Sandbox { pid: u32 }
pub enum Verdict { One, Zero }
pub trait Evaluator { fn grade(&self) -> bool; }
pub fn grade_once(e: &dyn Evaluator) -> bool { e.grade() }
impl Sandbox { pub fn new() -> Self { Sandbox { pid: 0 } } }
pub const MAX_TURNS: usize = 64;
pub mod tools;
"""

_GO = """\
package sandbox

import (
  "fmt"
  _ "embed"
)

type Budget struct { tokens int }
type Gate interface { Approve() bool }
func NewBudget(tokens int) *Budget { return &Budget{tokens: tokens} }
func (b *Budget) Spend(n int) bool { return n <= b.tokens }
const MaxTurns = 64
var DefaultBudget = NewBudget(MaxTurns)
"""


class StandardizerTests(unittest.TestCase):
    def test_detect_language(self):
        cases = {
            "src/app.py": "python",
            "src/component.ts": "typescript",
            "src/component.tsx": "typescript",
            "lib/mod.rs": "rust",
            "cmd/main.go": "go",
            "README.md": "markdown",
            "NOTES.txt": "text",
        }
        for path, expected in cases.items():
            self.assertEqual(standardizer_mod.detect_language(path), expected)

    def test_file_kind_by_extensions(self):
        self.assertEqual(standardizer_mod.file_kind("a.md"), "document")
        self.assertEqual(standardizer_mod.file_kind("a.py"), "code")
        self.assertEqual(standardizer_mod.file_kind("logo.svg"), "file")
        self.assertEqual(standardizer_mod.file_kind("a.xyz", code_exts=(".xyz",)), "code")

    def test_normalize_kind_synonyms(self):
        self.assertEqual(standardizer_mod.normalize_kind("fn"), "function")
        self.assertEqual(standardizer_mod.normalize_kind("func"), "function")
        self.assertEqual(standardizer_mod.normalize_kind("trait"), "interface")
        self.assertEqual(standardizer_mod.normalize_kind("EntityKind.SYMBOL"), "symbol")
        self.assertEqual(standardizer_mod.normalize_kind("TypeAlias"), "type")
        self.assertEqual(standardizer_mod.normalize_kind("bogus_thing"), "symbol")

    def test_split_identifiers_camel_and_paths(self):
        tokens = standardizer_mod.split_identifiers("FrontendPersistencePort")
        self.assertIn("frontend", tokens)
        self.assertIn("persistence", tokens)
        self.assertIn("port", tokens)
        self.assertIn("frontendpersistenceport", tokens)
        tokens2 = standardizer_mod.split_identifiers("reduce_run_snapshot")
        self.assertIn("reduce", tokens2)
        self.assertIn("run", tokens2)
        self.assertIn("snapshot", tokens2)


class LanguageExtractionTests(unittest.TestCase):
    def setUp(self):
        self.provider = CodeASTProvider()

    def test_typescript(self):
        syms, rels = self.provider._parse_tsjs("src/ui/app.ts", _TS)
        names = {s.name for s in syms}
        self.assertIn("FrontendPersistencePort", names)
        self.assertIn("reduceRunSnapshot", names)
        self.assertIn("AppController", names)
        self.assertIn("dispatch", names)
        self.assertIn("EventKind", names)
        kinds = {s.kind for s in syms}
        self.assertTrue({"interface", "type", "enum", "function", "class", "const"} <= kinds)
        import_targets = {r.target_id for r in rels if r.kind.value == "imports"}
        self.assertIn("@aether/contracts", import_targets)

    def test_rust(self):
        syms, rels = self.provider._parse_rust("src/lib.rs", _RS)
        names = {s.name for s in syms}
        self.assertIn("Sandbox", names)
        self.assertIn("Verdict", names)
        self.assertIn("Evaluator", names)
        self.assertIn("grade_once", names)
        self.assertIn("MAX_TURNS", names)
        self.assertIn("tools", names)
        self.assertTrue({"struct", "enum", "interface", "function", "const", "module"} <= {s.kind for s in syms})
        import_targets = {r.target_id for r in rels if r.kind.value == "imports"}
        self.assertIn("std::collections::HashMap", import_targets)

    def test_go(self):
        syms, rels = self.provider._parse_go("pkg/sandbox/sandbox.go", _GO)
        by_name = {s.name: s.kind for s in syms}
        self.assertEqual(by_name.get("Budget"), "struct")
        self.assertEqual(by_name.get("Gate"), "interface")
        self.assertEqual(by_name.get("NewBudget"), "function")
        self.assertEqual(by_name.get("Spend"), "method")
        self.assertEqual(by_name.get("MaxTurns"), "const")
        self.assertEqual(by_name.get("DefaultBudget"), "var")
        import_targets = {r.target_id for r in rels if r.kind.value == "imports"}
        self.assertIn("fmt", import_targets)
        self.assertIn("embed", import_targets)


class PipelineTests(unittest.TestCase):
    def test_mixed_language_index_and_healthcheck(self):
        repo = _mkrepo(
            **{"src/app.py": "class Kernel:\n    def dispatch(self): ...\n",
                "src/ui/app.ts": _TS,
                "src/lib.rs": _RS,
                "pkg/sandbox.go": _GO,
                "docs/guide.md": "# Guide\n\nBudget algebra.\n"}
        )
        try:
            result = atlas_mod.index_repository(repo, incremental=False)
            self.assertEqual(result["status"], "SUCCESS")

            ctx = AtlasContext.discover(repo)
            storage = atlas_mod.get_storage(repo)
            files_by_lang = storage.coverage_by_language()["files"]
            self.assertGreaterEqual(files_by_lang.get("python", 0), 1)
            self.assertGreaterEqual(files_by_lang.get("typescript", 0), 1)
            self.assertGreaterEqual(files_by_lang.get("rust", 0), 1)
            self.assertGreaterEqual(files_by_lang.get("go", 0), 1)
            self.assertGreaterEqual(files_by_lang.get("markdown", 0), 1)
            kinds = {r["kind"] for r in storage.get_topology_map()["entities"] if r["kind"] != "file"}
            self.assertIn("interface", kinds)

            health = healthcheck_mod.run_healthcheck(ctx, storage)
            self.assertEqual(health["status"], "HEALTHY")
            self.assertTrue(health["index_healthy"])
            self.assertTrue(any(c["id"] == "index.coverage" and c["status"] == "ok" for c in health["checks"]))
        finally:
            _rm(repo)

    def test_healthcheck_degrades_on_empty_index(self):
        repo = _mkrepo(**{"src/app.py": "def f():\n    ...\n"})
        try:
            ctx = AtlasContext.discover(repo)
            health = healthcheck_mod.run_healthcheck(ctx, atlas_mod.get_storage(repo))
            self.assertEqual(health["status"], "DEGRADED")
            self.assertFalse(health["index_healthy"])
            self.assertTrue(any(c["id"] == "index.graph" and c["status"] == "error" for c in health["checks"]))
        finally:
            _rm(repo)

    def test_rebuild_purges_deleted_file_symbols(self):
        repo = _mkrepo(
            **{"src/app.py": "class Kernel:\n    pass\n",
                "src/gone.py": "class Gone:\n    pass\n"}
        )
        try:
            atlas_mod.index_repository(repo, incremental=False)
            storage = atlas_mod.get_storage(repo)
            self.assertEqual(storage.get_stats()["symbols"], 2)

            (repo / "src/gone.py").unlink()
            atlas_mod.index_repository(repo, incremental=False, rebuild=True)
            remaining = {r[0] for r in storage.get_connection().execute("SELECT name FROM symbols")}
            self.assertNotIn("Gone", remaining)
            self.assertLessEqual(storage.get_stats()["symbols"], 1)
        finally:
            _rm(repo)


if __name__ == "__main__":
    unittest.main()
    unittest.main()