"""Phase D/E falsifiers: MCP resources/prompts, SKILL.md presence, and the
deterministic retrieval benchmark."""
from __future__ import annotations

import json
import unittest
from importlib import import_module
from pathlib import Path

server_mod = import_module("tools.007_LLM_DOCS_ATLAS.server_mcp")
bench_mod = import_module("tools.007_LLM_DOCS_ATLAS.core.bench")

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestMcpResourcesPrompts(unittest.TestCase):
    def setUp(self):
        self.server = server_mod.LDAMCPServer(REPO_ROOT)

    def test_resources_list_and_map_read(self):
        resp = self.server.handle_request({"method": "resources/list", "id": 1})
        uris = {r["uri"] for r in resp["result"]["resources"]}
        self.assertIn("lda://map", uris)
        read = self.server.handle_request({"method": "resources/read", "id": 2, "params": {"uri": "lda://map"}})
        payload = json.loads(read["result"]["contents"][0]["text"])
        self.assertIn("languages", payload)

    def test_unknown_resource_fails_closed(self):
        resp = self.server.handle_request({
            "method": "resources/read", "id": 3, "params": {"uri": "lda://docs/does-not-exist"},
        })
        self.assertIn("error", resp)

    def test_prompts_list_and_get(self):
        listing = self.server.handle_request({"method": "prompts/list", "id": 4})
        names = {p["name"] for p in listing["result"]["prompts"]}
        self.assertIn("lda_task_briefing", names)
        got = self.server.handle_request({
            "method": "prompts/get", "id": 5,
            "params": {"name": "lda_task_briefing", "arguments": {"task": "fix budget"}},
        })
        self.assertIn("lda_brief", got["result"]["messages"][0]["content"]["text"])

    def test_initialize_advertises_capabilities(self):
        resp = self.server.handle_request({"method": "initialize", "id": 6})
        caps = resp["result"]["capabilities"]
        self.assertIn("resources", caps)
        self.assertIn("prompts", caps)


class TestSkillManifest(unittest.TestCase):
    def test_skill_md_declares_workflow_and_mcp_tools(self):
        skill = (REPO_ROOT / ".agents" / "skills" / "lda-navigator" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: lda-navigator", skill)
        for token in ("lda doctor", "lda context", "lda brief", "lda drift", "lda_brief"):
            self.assertIn(token, skill)


class TestBench(unittest.TestCase):
    def test_bench_runs_and_meets_floor(self):
        results = bench_mod.run_bench(budget=2000, k=5)
        for strategy in ("fts5_bm25", "ppr_submodular", "hybrid_rrf"):
            self.assertIn(strategy, results)
            # Retrieval floor: at least half the gold set must be hit in top-5.
            self.assertGreaterEqual(results[strategy]["recall@5"], 0.5, strategy)
            self.assertGreater(results[strategy]["mean_latency_ms"], 0.0)

    def test_bench_is_deterministic_in_ranking(self):
        first = bench_mod.run_bench(budget=2000, k=5)
        second = bench_mod.run_bench(budget=2000, k=5)
        for strategy in ("fts5_bm25", "ppr_submodular", "hybrid_rrf"):
            self.assertEqual(first[strategy]["recall@5"], second[strategy]["recall@5"])
            self.assertEqual(first[strategy]["mrr"], second[strategy]["mrr"])


if __name__ == "__main__":
    unittest.main()
