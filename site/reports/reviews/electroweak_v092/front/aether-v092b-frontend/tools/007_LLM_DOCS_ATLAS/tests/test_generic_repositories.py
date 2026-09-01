import importlib, json, tempfile, unittest
from pathlib import Path

cli = importlib.import_module("tools.007_LLM_DOCS_ATLAS.cli")
AtlasContext = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.config").AtlasContext

class TestGenericRepositories(unittest.TestCase):
    def make_repo(self, files):
        temp = tempfile.TemporaryDirectory(); root = Path(temp.name)
        for name, content in files.items():
            path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content)
        return temp, root

    def assert_usable(self, files, query):
        temp, root = self.make_repo(files)
        try:
            ctx = AtlasContext.discover(root)
            status = cli._snapshot(ctx); packet = cli._packet(ctx, query, 2000)
            self.assertGreaterEqual(status["documents"], 0)
            self.assertGreaterEqual(status["estimated_tokens"], 0)
            self.assertIsNotNone(packet)
            self.assertTrue(cli._rows(ctx, "catalog.jsonl") is not None)
        finally:
            temp.cleanup()

    def test_python_without_docs(self):
        self.assert_usable({"src/app.py": "def hello(): return 1\n", "tests/test_app.py": "def test_hello(): pass\n", "README.md": "# Demo\n"}, "hello")

    def test_typescript_project(self):
        self.assert_usable({"src/index.ts": "export const hello = 1;\n", "package.json": "{}\n", "README.md": "# TS\n"}, "hello")

    def test_rust_project(self):
        self.assert_usable({"src/main.rs": "fn main() {}\n", "Cargo.toml": "[package]\nname='demo'\n"}, "main")

    def test_documentation_without_frontmatter(self):
        self.assert_usable({"documentation/guide.md": "# Guide\nPlain documentation.\n"}, "guide")

    def test_empty_project_is_graceful(self):
        self.assert_usable({}, "anything")
