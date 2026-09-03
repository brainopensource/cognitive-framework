"""
test/contracts/test_mcp_server.py
Automated contract tests validating the full suite of LDA MCP JSON-RPC 2.0 tools.
"""

import importlib
import json
import unittest
from pathlib import Path

server_module = importlib.import_module("tools.007_LLM_DOCS_ATLAS.server_mcp")
LDAMCPServer = server_module.LDAMCPServer


class TestLDAMCPServer(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        self.server = LDAMCPServer(self.root)

    def test_initialize_handshake(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        resp = self.server.handle_request(req)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["id"], 1)
        self.assertEqual(resp["result"]["serverInfo"]["name"], "lda-repository-intelligence")
        self.assertEqual(resp["result"]["protocolVersion"], "2024-11-05")

    def test_tools_list_enumeration(self):
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        resp = self.server.handle_request(req)
        self.assertIsNotNone(resp)
        tools = resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        expected_tools = [
            "lda_context", "lda_symbol", "lda_callers", "lda_callees",
            "lda_references", "lda_tests_for_symbol", "lda_docs_for_symbol",
            "lda_fts_search", "lda_map", "lda_doctor"
        ]
        for t in expected_tools:
            self.assertIn(t, tool_names)

    def test_lda_context_tool_call(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "lda_context",
                "arguments": {"query": "kernel dispatch", "budget": 4000}
            }
        }
        resp = self.server.handle_request(req)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["id"], 3)
        content_text = resp["result"]["content"][0]["text"]
        payload = json.loads(content_text)
        self.assertIn("bounded_context", payload)

    def test_lda_symbol_tool_call(self):
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "lda_symbol",
                "arguments": {"symbol_name": "Kernel"}
            }
        }
        resp = self.server.handle_request(req)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["id"], 4)
        content_text = resp["result"]["content"][0]["text"]
        payload = json.loads(content_text)
        self.assertEqual(payload["symbol"], "Kernel")
        self.assertGreater(payload["count"], 0)

    def test_lda_doctor_tool_call(self):
        req = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "lda_doctor", "arguments": {}}
        }
        resp = self.server.handle_request(req)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["id"], 5)
        content_text = resp["result"]["content"][0]["text"]
        payload = json.loads(content_text)
        self.assertEqual(payload["status"], "HEALTHY")

    def test_lda_fts_search_tool_call(self):
        req = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "lda_fts_search",
                "arguments": {"query": "dispatch", "limit": 5}
            }
        }
        resp = self.server.handle_request(req)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["id"], 6)
        content_text = resp["result"]["content"][0]["text"]
        payload = json.loads(content_text)
        self.assertIn("results", payload)

    def test_lda_map_tool_call(self):
        req = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {"name": "lda_map", "arguments": {}}
        }
        resp = self.server.handle_request(req)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["id"], 7)
        content_text = resp["result"]["content"][0]["text"]
        payload = json.loads(content_text)
        self.assertIn("topology_map", payload)


class TestLDAMCPServerInvariants(unittest.TestCase):
    """P1.5 invariants: truthful health, HEAD binding, profile-aware fallback."""

    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        self.server = LDAMCPServer(self.root)

    def _make_repo(self) -> Path:
        import tempfile

        tmp = Path(tempfile.mkdtemp(prefix="lda-mcp-"))
        (tmp / "docs").mkdir(parents=True, exist_ok=True)
        (tmp / "docs" / "guide.md").write_text("# Guide\n\nBudget algebra.\n", encoding="utf-8")
        (tmp / "src").mkdir(parents=True, exist_ok=True)
        (tmp / "src" / "app.py").write_text("def spawn():\n    ...\n", encoding="utf-8")
        return tmp

    def test_lda_doctor_truthful_on_empty_index(self):
        repo = self._make_repo()
        try:
            server = LDAMCPServer(repo)
            resp = server.handle_request({
                "jsonrpc": "2.0", "id": 20, "method": "tools/call",
                "params": {"name": "lda_doctor", "arguments": {}},
            })
            payload = json.loads(resp["result"]["content"][0]["text"])
            # An empty index must NEVER report HEALTHY.
            self.assertEqual(payload["status"], "DEGRADED_EMPTY_INDEX")
            self.assertFalse(payload["index_healthy"])
            self.assertIn("EMPTY or cold", payload["index_hint"])
        finally:
            import shutil

            shutil.rmtree(repo, ignore_errors=True)

    def test_lda_context_includes_head_binding_and_profile(self):
        resp = self.server.handle_request({
            "jsonrpc": "2.0", "id": 21, "method": "tools/call",
            "params": {"name": "lda_context", "arguments": {"query": "kernel dispatch", "budget": 4000}},
        })
        payload = json.loads(resp["result"]["content"][0]["text"])
        self.assertIn("source_head_sha", payload)
        self.assertIn("profile", payload)
        self.assertIn("index_healthy", payload)
        # Backwards-compatible bounded_context view is preserved.
        self.assertIn("bounded_context", payload)

    def test_lda_context_falls_back_when_index_cold(self):
        repo = self._make_repo()
        try:
            server = LDAMCPServer(repo)
            resp = server.handle_request({
                "jsonrpc": "2.0", "id": 22, "method": "tools/call",
                "params": {"name": "lda_context", "arguments": {"query": "budget", "budget": 2000}},
            })
            payload = json.loads(resp["result"]["content"][0]["text"])
            self.assertFalse(payload["index_healthy"])
            self.assertIn("bounded_context", payload, "cold index must fail open to docs_rag_v0, not serve empty facts")
        finally:
            import shutil

            shutil.rmtree(repo, ignore_errors=True)

    def test_lda_symbol_fallback_is_profile_aware(self):
        import shutil
        import tempfile

        tmp = Path(tempfile.mkdtemp(prefix="lda-mcp-"))
        try:
            symbols_file = tmp / ".generated" / "knowledge" / "symbols.jsonl"
            symbols_file.parent.mkdir(parents=True, exist_ok=True)
            symbols_file.write_text(
                '{"symbol": "MyThing", "defined_in": "src/x.py", "canonical_owner": "docs/x.md"}\n',
                encoding="utf-8",
            )
            server = LDAMCPServer(tmp)
            resp = server.handle_request({
                "jsonrpc": "2.0", "id": 23, "method": "tools/call",
                "params": {"name": "lda_symbol", "arguments": {"symbol_name": "mything"}},
            })
            payload = json.loads(resp["result"]["content"][0]["text"])
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["matches"][0]["defined_in"], "src/x.py")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_unknown_tool_returns_jsonrpc_error(self):
        resp = self.server.handle_request({
            "jsonrpc": "2.0", "id": 24, "method": "tools/call",
            "params": {"name": "lda_nonexistent", "arguments": {}},
        })
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32603)

    def test_root_argument_is_respected(self):
        import shutil
        import tempfile

        tmp = Path(tempfile.mkdtemp(prefix="lda-mcp-"))
        try:
            server = LDAMCPServer(tmp)
            # Profile resolved from the explicit workspace root, not the package location.
            self.assertEqual(server._root, tmp.resolve())
            self.assertEqual(server._ctx.profile.name, "generic")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
