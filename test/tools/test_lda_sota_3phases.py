"""Unit and Contract Tests for LDA SOTA 3-Phase Engine.

Verifies:
- Phase 1: One-Shot Task Bundle (lda plan)
- Phase 2: Ephemeral Incremental Delta Indexing (lda index --delta)
- Phase 3: Semantic Intent Symbol Resolution (lda resolve)
"""
from __future__ import annotations

import importlib
import tempfile
import time
import unittest
from pathlib import Path

atlas_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.atlas")
delta_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.delta")
resolve_mod = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.resolve")

compile_task_plan = atlas_mod.compile_task_plan
get_storage = atlas_mod.get_storage
index_delta = atlas_mod.index_delta
resolve_symbol_intent = atlas_mod.resolve_symbol_intent
detect_dirty_files = delta_mod.detect_dirty_files
_stem = resolve_mod._stem
_tokenize_query = resolve_mod._tokenize_query


class TestLDASota3Phases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path.cwd().resolve()
        cls.storage = get_storage(cls.repo_root)

    # --------------------------------------------------------------------------
    # Phase 2: Ephemeral Incremental Delta Indexing
    # --------------------------------------------------------------------------
    def test_stemmer_and_tokenizer(self):
        self.assertEqual(_stem("attenuation"), "attenua")
        self.assertEqual(_stem("running"), "runn")
        self.assertEqual(_stem("reservations"), "reserva")

        terms = _tokenize_query("Monotonic capability attenuation in kernel")
        self.assertIn("monotonic", terms)
        self.assertIn("capability", terms)
        self.assertIn("attenuation", terms)
        self.assertIn("kernel", terms)
        self.assertNotIn("in", terms)

    def test_delta_up_to_date_when_clean(self):
        # When no dirty files exist or after sync, delta returns UP_TO_DATE in <100ms
        res = index_delta(self.repo_root)
        self.assertIn(res["status"], ("SUCCESS", "UP_TO_DATE"))
        self.assertTrue(res["delta"])
        self.assertLess(res["duration_ms"], 2000.0)

    def test_delta_index_single_file_lifecycle(self):
        # Create a temporary scratch Python file
        test_file = self.repo_root / "test_scratch_delta_temp.py"
        try:
            test_file.write_text(
                'class DeltaScratchTest:\n'
                '    """A scratch class for testing delta indexing."""\n'
                '    def delta_scratch_method(self):\n'
                '        return "hello"\n'
            )
            t0 = time.perf_counter()
            res = index_delta(self.repo_root, files=["test_scratch_delta_temp.py"])
            duration_ms = (time.perf_counter() - t0) * 1000

            self.assertEqual(res["status"], "SUCCESS")
            self.assertEqual(res["files_indexed"], 1)
            self.assertIn("test_scratch_delta_temp.py", res["modified_files"])
            self.assertLess(duration_ms, 2000.0)

            # Verify the symbol was added to the database
            syms = self.storage.get_symbol("DeltaScratchTest", exact=True)
            self.assertTrue(len(syms) >= 1)
            self.assertEqual(syms[0]["name"], "DeltaScratchTest")
            self.assertEqual(syms[0]["file_path"], "test_scratch_delta_temp.py")

        finally:
            if test_file.exists():
                test_file.unlink()

            # Now run delta on the deleted file to ensure purge works
            res_del = index_delta(self.repo_root, files=["test_scratch_delta_temp.py"])
            self.assertEqual(res_del["status"], "SUCCESS")
            self.assertIn("test_scratch_delta_temp.py", res_del["deleted_files"])

            # Verify the symbol was purged
            syms_after = self.storage.get_symbol("DeltaScratchTest", exact=True)
            self.assertEqual(len(syms_after), 0)

    # --------------------------------------------------------------------------
    # Phase 3: Semantic Intent Symbol Resolution
    # --------------------------------------------------------------------------
    def test_resolve_symbol_exact_name(self):
        results = resolve_symbol_intent(self.repo_root, "Reservation", top_k=3)
        self.assertTrue(len(results) >= 1)
        top = results[0]
        self.assertEqual(top["name"], "Reservation")
        self.assertTrue(top["confidence_score"] >= 0.7)
        self.assertIn("vanguard/packages/", top["file_path"])

    def test_resolve_symbol_intent_natural_language(self):
        # Resolving "bubblewrap execution runner" should find RootlessSandboxRunner in adapters
        results = resolve_symbol_intent(self.repo_root, "bubblewrap execution runner", top_k=5)
        self.assertTrue(len(results) >= 1)
        runner_found = any("SandboxRunner" in r["name"] or "sandbox" in r["file_path"] for r in results)
        self.assertTrue(runner_found)
        top = results[0]
        self.assertTrue(top["confidence_score"] > 0.5)
        self.assertIn("file_path", top)
        self.assertIn("start_line", top)
        self.assertIn("signature", top)

    def test_resolve_monotonic_capability_attenuation(self):
        results = resolve_symbol_intent(self.repo_root, "monotonic capability attenuation", top_k=5)
        self.assertTrue(len(results) >= 1)
        # Should identify symbols in attenuation.py or domain manifest
        attenuation_found = any("attenuation.py" in r["file_path"] or "attenuat" in r["name"].lower() for r in results)
        self.assertTrue(attenuation_found)

    # --------------------------------------------------------------------------
    # Phase 1: One-Shot Task Bundle (lda plan)
    # --------------------------------------------------------------------------
    def test_compile_task_plan_bundle_completeness(self):
        plan = compile_task_plan(
            self.repo_root,
            task="budget reservation and commitment",
            budget=4000,
            top_symbols=3,
            auto_delta=False,
        )
        # Verify top-level contract keys
        for key in (
            "task",
            "intent",
            "strategy",
            "budget",
            "duration_ms",
            "freshness",
            "primary_symbols",
            "blast_radius",
            "test_falsifiers",
            "doc_obligations",
            "context_packet",
            "plan_markdown",
        ):
            self.assertIn(key, plan)

        # Primary symbols
        self.assertTrue(len(plan["primary_symbols"]) >= 1)
        s0 = plan["primary_symbols"][0]
        self.assertIn("name", s0)
        self.assertIn("file_path", s0)
        self.assertIn("start_line", s0)

        # Blast radius
        self.assertIn("callers", plan["blast_radius"])
        self.assertIn("affected_files", plan["blast_radius"])

        # Test falsifiers
        self.assertIn("suggested_commands", plan["test_falsifiers"])
        self.assertTrue(len(plan["test_falsifiers"]["suggested_commands"]) >= 1)

        # Documentation obligations
        self.assertTrue(len(plan["doc_obligations"]) >= 1)
        self.assertEqual(plan["doc_obligations"][0]["document"], "docs/execution/spec.md")

        # Markdown output formatting
        md = plan["plan_markdown"]
        self.assertIn("# LDA Task Plan:", md)
        self.assertIn("## 1. Primary Target Symbols", md)
        self.assertIn("## 2. Blast Radius", md)
        self.assertIn("## 3. Canonical Documentation Obligations", md)
        self.assertIn("## 4. Targeted Test Falsifiers", md)
        self.assertIn("```bash", md)


if __name__ == "__main__":
    unittest.main()
