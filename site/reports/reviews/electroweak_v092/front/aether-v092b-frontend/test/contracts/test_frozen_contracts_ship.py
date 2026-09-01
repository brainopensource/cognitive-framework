"""B-O6V-01: a frozen contract that does not ship is not frozen.

Order 2 froze the vg.4 schemas and published golden vectors; Order 6 built the
wheel that is meant to carry them. Between the two sits a packaging declaration
nobody was checking, and it silently dropped files.

The concrete loss: `schemas/v4/vectors/canonicalisation/` holds 48 triples --
input, RFC 8785 canonical form, digest -- that `REQ-SCHEMA-001` / `GV-2` /
`SC-7` require to be replayed through both readers byte-for-byte. The `.json`
inputs matched a package-data glob; the `.jcs` and `.digest` halves did not.
An installed wheel therefore carried the questions and none of the answers, so
the canonicalisation contract that guarantees old-byte immutability could not
be verified from the shipped artifact at all.

This module checks the declaration rather than a built wheel: it is hermetic,
needs no build step, and fails at the moment a new vector extension is added
without extending the manifest -- which is when the fix is cheap.
"""

from __future__ import annotations

import fnmatch
import tomllib
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PYPROJECT = _REPO_ROOT / "pyproject.toml"

#: Directories whose contents are build residue, never distribution content.
_IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache"}

#: Trees that carry frozen contract data and must ship whole.
_CONTRACT_TREES = ("schemas", "packs")


def _package_data_globs() -> list[str]:
    config = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    package_data = (
        config.get("tool", {}).get("setuptools", {}).get("package-data", {})
    )
    globs: list[str] = []
    for patterns in package_data.values():
        globs.extend(patterns)
    return globs


def _contract_files() -> list[Path]:
    files: list[Path] = []
    for tree in _CONTRACT_TREES:
        for path in sorted((_REPO_ROOT / tree).rglob("*")):
            if not path.is_file():
                continue
            if _IGNORED_DIRS & set(path.relative_to(_REPO_ROOT).parts):
                continue
            if path.suffix == ".pyc":
                continue
            files.append(path)
    return files


def _is_declared(path: Path, globs: list[str]) -> bool:
    # Python sources ship as modules, not as package data.
    if path.suffix == ".py":
        return True
    return any(fnmatch.fnmatch(path.name, pattern) for pattern in globs)


class FrozenContractDataIsDeclaredForDistribution(unittest.TestCase):
    def test_every_contract_file_matches_a_package_data_glob(self) -> None:
        globs = _package_data_globs()
        self.assertTrue(globs, "pyproject declares no package-data patterns")

        undeclared = [
            path.relative_to(_REPO_ROOT)
            for path in _contract_files()
            if not _is_declared(path, globs)
        ]
        self.assertEqual(
            [],
            undeclared,
            f"{len(undeclared)} frozen contract file(s) match no package-data "
            f"glob and will be dropped from the wheel: "
            f"{sorted({p.suffix for p in undeclared})}. Add the extension to "
            f"[tool.setuptools.package-data] rather than removing the data.",
        )

    def test_canonicalisation_triples_are_complete_and_declared(self) -> None:
        """GV-2: every input has its canonical form and digest, and all three ship."""
        globs = _package_data_globs()
        triples = _REPO_ROOT / "schemas" / "v4" / "vectors" / "canonicalisation" / "canonical"
        inputs = sorted(triples.glob("*.json"))
        self.assertGreaterEqual(
            len(inputs), 40, "REQ-SCHEMA-001 requires at least 40 golden triples"
        )
        for source in inputs:
            with self.subTest(triple=source.stem):
                for part in (source, source.with_suffix(".jcs"),
                             source.with_suffix(".digest")):
                    self.assertTrue(part.is_file(), f"{part.name} is missing")
                    self.assertTrue(
                        _is_declared(part, globs),
                        f"{part.name} would not ship: the canonical form or its "
                        f"digest is undeclared, leaving the wheel with the "
                        f"input and no answer to check it against",
                    )

    def test_schema_catalogs_are_declared_whole(self) -> None:
        globs = _package_data_globs()
        for catalog in ("mhf", "v4"):
            for schema in sorted((_REPO_ROOT / "schemas" / catalog).glob("*.schema.json")):
                with self.subTest(schema=f"{catalog}/{schema.name}"):
                    self.assertTrue(_is_declared(schema, globs))


if __name__ == "__main__":
    unittest.main()
