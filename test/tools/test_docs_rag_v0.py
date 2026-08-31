"""Hermetic falsifiers for the repository-intelligence retrieval layer.

Covers:
  * tools/docs_rag_v0.py: authority ranking, non-canonical exclusion/demotion,
    token-budget packing, and reverse code->doc routing.
  * tools/generate_knowledge_base.py: deterministic AST symbol extraction and
    canonical-owner prefix resolution.
  * tools/007_LLM_DOCS_ATLAS/core/ranking.py: low-signal filtering and the
    canonical-catalog fallback used when the LDA fact graph is empty.

All tests are offline and deterministic; fixture catalogs use paths that do not
resolve in the real tree so no repository content is loaded.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import docs_rag_v0
from tools.generate_knowledge_base import (
    canonical_owner_for_code_path,
    extract_code_symbols,
)
from importlib import import_module

_ranking = import_module("tools.007_LLM_DOCS_ATLAS.core.ranking")
catalog_fallback_candidates = _ranking.catalog_fallback_candidates
is_low_signal = _ranking.is_low_signal


def _write_knowledge_dir(root: Path, catalog: list[dict], code_map: list[dict] | None = None,
                         symbols: list[dict] | None = None) -> Path:
    knowledge = root / ".generated" / "knowledge"
    knowledge.mkdir(parents=True, exist_ok=True)
    (knowledge / "catalog.jsonl").write_text(
        "\n".join(json.dumps(r) for r in catalog) + "\n", encoding="utf-8"
    )
    (knowledge / "code-map.jsonl").write_text(
        "\n".join(json.dumps(r) for r in (code_map or [])) + "\n", encoding="utf-8"
    )
    (knowledge / "symbols.jsonl").write_text(
        "\n".join(json.dumps(r) for r in (symbols or [])) + "\n", encoding="utf-8"
    )
    # Empty auxiliary files keep retrieve() symmetrical with the real layout.
    for name in ("ownership.jsonl", "links.jsonl"):
        (knowledge / name).write_text("", encoding="utf-8")
    return knowledge


FIXTURE_CATALOG = [
    {
        "canonical_id": "kernel.arch",
        "path": "fixture_docs/backend/kernel.md",
        "title": "Kernel Budget Dispatch Architecture",
        "authority": "descriptive",
        "estimated_tokens": "1500",
    },
    {
        "canonical_id": "spec.core",
        "path": "fixture_docs/SPEC.md",
        "title": "AETHER TARGET Specification",
        "authority": "normative",
        "estimated_tokens": "2000",
    },
    {
        "canonical_id": "research.essay",
        "path": "docs/research/coding_harness/essay.md",
        "title": "Research Essay on Budget Dispatch",
        "authority": "descriptive",
        "estimated_tokens": "9000",
    },
    {
        "canonical_id": "noncanon.audit",
        "path": "docs/reports/audit.md",
        "title": "Audit Report",
        "authority": "non-canonical",
        "estimated_tokens": "500",
    },
]

FIXTURE_CODE_MAP = [
    {"subsystem": "SUB-B-03 Kernel Core", "package_path": "vanguard/packages/kernel/", "canonical_owner": "docs/backend/architecture/kernel.md"},
    {"subsystem": "SUB-B-05 Causal State", "package_path": "vanguard/packages/runtime/ledger_emitter.py", "canonical_owner": "docs/backend/architecture/causal-state.md"},
    {"subsystem": "SUB-B-06 Composition", "package_path": "vanguard/packages/runtime/", "canonical_owner": "docs/backend/architecture/runtime-execution.md"},
]

FIXTURE_SYMBOLS = [
    {"symbol": "BudgetDenied", "kind": "class", "defined_in": "vanguard/packages/kernel/budget.py", "canonical_owner": "docs/backend/architecture/kernel.md"},
]

class RetrievalRankingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.knowledge_dir = _write_knowledge_dir(Path(self._tmp.name), FIXTURE_CATALOG)

    def _paths(self, result: dict) -> list[str]:
        return [d["path"] for d in result["bounded_context"]["documents"]]

    def test_non_canonical_excluded_by_default(self) -> None:
        res = docs_rag_v0.retrieve("audit report", knowledge_dir=self.knowledge_dir)
        self.assertNotIn("docs/reports/audit.md", self._paths(res))

    def test_non_canonical_included_when_opted_in(self) -> None:
        res = docs_rag_v0.retrieve(
            "audit report", include_non_canonical=True, knowledge_dir=self.knowledge_dir
        )
        self.assertIn("docs/reports/audit.md", self._paths(res))

    def test_research_location_demoted_below_canonical(self) -> None:
        # Same term ("budget dispatch") hits both; canonical owners must win.
        res = docs_rag_v0.retrieve("budget dispatch", knowledge_dir=self.knowledge_dir)
        paths = self._paths(res)
        self.assertIn("fixture_docs/backend/kernel.md", paths)
        self.assertLess(
            paths.index("fixture_docs/backend/kernel.md"),
            paths.index("docs/research/coding_harness/essay.md"),
        )

    def test_normative_authority_boosted(self) -> None:
        res = docs_rag_v0.retrieve("target specification budget", knowledge_dir=self.knowledge_dir)
        self.assertEqual(self._paths(res)[0], "fixture_docs/SPEC.md")

    def test_budget_packing_keeps_top_hit_and_respects_cap(self) -> None:
        # Budget 1600 tokens: kernel.md (1500) fits after the top hit; SPEC (2000) does not.
        res = docs_rag_v0.retrieve(
            "budget dispatch specification", budget=1600, knowledge_dir=self.knowledge_dir
        )
        docs = res["bounded_context"]["documents"]
        self.assertTrue(docs)
        used = sum(int(d["estimated_tokens"]) for d in docs[1:])
        self.assertLessEqual(used, 1600)

    def test_reverse_file_lookup_resolves_owner_and_symbols(self) -> None:
        knowledge = _write_knowledge_dir(
            Path(self._tmp.name), FIXTURE_CATALOG, FIXTURE_CODE_MAP, FIXTURE_SYMBOLS
        )
        res = docs_rag_v0.lookup_file("vanguard/packages/kernel/budget.py", knowledge_dir=knowledge)
        self.assertEqual(res["subsystem"], "SUB-B-03 Kernel Core")
        self.assertEqual(res["canonical_owner"], "docs/backend/architecture/kernel.md")
        self.assertEqual(
            [s["symbol"] for s in res["symbols_defined_here"]], ["BudgetDenied"]
        )

    def test_reverse_file_lookup_prefers_exact_file_row(self) -> None:
        knowledge = _write_knowledge_dir(
            Path(self._tmp.name), FIXTURE_CATALOG, FIXTURE_CODE_MAP, []
        )
        res = docs_rag_v0.lookup_file(
            "vanguard/packages/runtime/ledger_emitter.py", knowledge_dir=knowledge
        )
        # The exact file row must beat the shorter runtime/ directory row.
        self.assertEqual(res["canonical_owner"], "docs/backend/architecture/causal-state.md")


class CanonicalOwnerResolutionTests(unittest.TestCase):
    def test_longest_prefix_wins(self) -> None:
        rows = [dict(r) for r in FIXTURE_CODE_MAP]
        self.assertEqual(
            canonical_owner_for_code_path("vanguard/packages/runtime/ledger_emitter.py", rows),
            "docs/backend/architecture/causal-state.md",
        )
        self.assertEqual(
            canonical_owner_for_code_path("vanguard/packages/runtime/other.py", rows),
            "docs/backend/architecture/runtime-execution.md",
        )
        self.assertEqual(
            canonical_owner_for_code_path("vanguard/packages/kernel/dispatch.py", rows),
            "docs/backend/architecture/kernel.md",
        )

    def test_symbol_extraction_is_deterministic_and_routed(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        symbols = extract_code_symbols(repo_root, [dict(r) for r in FIXTURE_CODE_MAP])
        self.assertTrue(symbols, "expected a non-empty AST symbol index")
        keys = [(s["symbol"], s["defined_in"]) for s in symbols]
        self.assertEqual(len(keys), len(set(keys)), "symbol index must be deduplicated")
        self.assertEqual(symbols, sorted(symbols, key=lambda r: (r["symbol"], r["defined_in"])))
        for row in symbols:
            self.assertIn(row["kind"], {"class", "protocol"})
            self.assertTrue(row["canonical_owner"].startswith("docs/"))

    def test_real_kernel_symbols_present_in_repo_scan(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        symbols = extract_code_symbols(repo_root, [dict(r) for r in FIXTURE_CODE_MAP])
        by_name = {s["symbol"]: s for s in symbols}
        self.assertIn("Kernel", by_name)
        self.assertEqual(
            by_name["Kernel"]["defined_in"], "vanguard/packages/kernel/dispatch.py"
        )


class LdaFallbackRankingTests(unittest.TestCase):
    def test_low_signal_locators_filtered(self) -> None:
        for locator in (
            "test/broken/fixtures/x.py",
            "benchmarks/frontier_v090/runs/a/b.py",
            "pkg/__init__.py",
            "vanguard/clients/studio/dist-browser/browser.js",
        ):
            self.assertTrue(is_low_signal(locator), locator)
        self.assertFalse(is_low_signal("vanguard/packages/kernel/dispatch.py"))

    def test_catalog_fallback_is_canonical_and_authority_tagged(self) -> None:
        catalog = {row["path"]: row for row in FIXTURE_CATALOG}
        candidates = catalog_fallback_candidates("kernel dispatch budget", catalog)
        self.assertTrue(candidates)
        for candidate in candidates:
            self.assertIsNotNone(candidate.authority)
            self.assertNotEqual(candidate.authority, "non-canonical")
            self.assertFalse(
                candidate.locator.startswith(("docs/research/", "docs/reports/", "docs/theory/"))
            )
        locators = [c.locator for c in candidates]
        self.assertIn("fixture_docs/backend/kernel.md", locators)
        self.assertNotIn("docs/research/coding_harness/essay.md", locators)


if __name__ == "__main__":
    unittest.main()