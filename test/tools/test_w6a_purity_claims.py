"""W6a: domain I/O and subprocess grants must match the stated contract.

Falsifiers red until the linter inspects domain I/O, the allowlist is the
single source of truth, and overstated verification/retrieval claims are gone.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOUNDARIES = ROOT / "tools" / "linters" / "check_boundaries.py"
DOMAIN_BLINDNESS = ROOT / "tools" / "linters" / "check_domain_blindness.py"
WORKSPACE = ROOT / "vanguard" / "packages" / "domain" / "workspace.py"
PLANTED = ROOT / "test" / "broken" / "fixtures" / "domain_io"

# Living claim surfaces in this packet (not docs/execution/main/*).
CLAIM_FILES = (
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "docs" / "architecture" / "boundaries.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "onboarding" / "SKILL_LDA_Docs_atlas.md",
    ROOT / ".agents" / "skills" / "lda-navigator" / "SKILL.md",
    ROOT / "tools" / "007_LLM_DOCS_ATLAS" / "README.md",
    ROOT / ".draft" / "todo" / "aether_vanguard_main_goals.md",
)


def _run(script: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *extra],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class DomainIoGateTests(unittest.TestCase):
    def test_planted_domain_read_text_fails_closed(self) -> None:
        result = _run(BOUNDARIES, "--root", str(PLANTED))
        combined = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, combined)
        self.assertIn("domain I/O", combined)

    def test_domain_blindness_also_flags_planted_io(self) -> None:
        result = _run(DOMAIN_BLINDNESS, "--root", str(PLANTED))
        combined = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, combined)
        self.assertIn("domain I/O", combined)

    def test_workspace_is_the_named_io_exception(self) -> None:
        sys.path.insert(0, str(ROOT / "tools" / "linters"))
        from check_boundaries import DOMAIN_IO_ALLOWLIST

        rel = "vanguard/packages/domain/workspace.py"
        self.assertIn(rel, DOMAIN_IO_ALLOWLIST)
        self.assertTrue(DOMAIN_IO_ALLOWLIST[rel].strip())
        tree = ast.parse(WORKSPACE.read_text(encoding="utf-8"))
        io_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"read_text", "mkdir"}
        ]
        self.assertGreaterEqual(len(io_calls), 1)
        result = _run(BOUNDARIES)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unlisted_domain_io_cannot_hide_behind_stdlib_imports(self) -> None:
        """ALLOWED['domain'] is empty; stdlib specs must still be inspected."""
        source = BOUNDARIES.read_text(encoding="utf-8")
        self.assertIn('"domain": set()', source)
        self.assertIn("DOMAIN_IO_ALLOWLIST", source)


class SubprocessGrantTests(unittest.TestCase):
    def test_allowlist_is_the_subprocess_ssot(self) -> None:
        sys.path.insert(0, str(ROOT / "tools" / "linters"))
        from check_boundaries import SUBPROCESS_ALLOWLIST, SUBPROCESS_HOME

        self.assertEqual(
            SUBPROCESS_HOME,
            ("vanguard", "packages", "adapters", "sandbox"),
        )
        self.assertGreaterEqual(len(SUBPROCESS_ALLOWLIST), 1)
        for path, reason in SUBPROCESS_ALLOWLIST.items():
            self.assertTrue((ROOT / path).is_file(), path)
            self.assertTrue(reason.strip(), path)
        header = BOUNDARIES.read_text(encoding="utf-8")
        self.assertIn("SUBPROCESS_ALLOWLIST", header)
        self.assertNotRegex(
            header,
            r"Process creation belongs to adapters/sandbox/ alone",
        )

    def test_n06_error_names_the_allowlist(self) -> None:
        fixture = ROOT / "test" / "broken" / "fixtures" / "agency_subprocess"
        result = _run(BOUNDARIES, "--root", str(fixture))
        combined = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, combined)
        self.assertIn("SUBPROCESS_ALLOWLIST", combined)


class ClaimReconciliationTests(unittest.TestCase):
    def test_no_mathematically_verified_microkernel_claim(self) -> None:
        hits: list[str] = []
        for path in CLAIM_FILES:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if "mathematically verified" in text.lower():
                hits.append(str(path.relative_to(ROOT)))
            if "mathematically sound, production-ready" in text.lower():
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])

    def test_lda_does_not_claim_universal_sub50ms_retrieval(self) -> None:
        banned = (
            "sub-50ms SQLite-WAL AST fact graph",
            "sub-50ms retrieval",
            "universal sub-50ms",
        )
        hits: list[str] = []
        for path in CLAIM_FILES:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for phrase in banned:
                if phrase.lower() in text.lower():
                    hits.append(f"{path.relative_to(ROOT)}:{phrase}")
        self.assertEqual(hits, [])

    def test_domain_purity_docs_name_the_workspace_exception(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        bounds = (ROOT / "docs" / "architecture" / "boundaries.md").read_text(
            encoding="utf-8"
        )
        for text, label in ((agents, "AGENTS.md"), (bounds, "boundaries.md")):
            self.assertIn("DOMAIN_IO_ALLOWLIST", text, label)
            self.assertIn("workspace.py", text, label)


if __name__ == "__main__":
    unittest.main()
