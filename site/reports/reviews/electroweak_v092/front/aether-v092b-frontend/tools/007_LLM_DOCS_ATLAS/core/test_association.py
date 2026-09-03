"""Test Association & Selection Engine (Requirement R2).

Finds targeted falsifiers and unit tests associated with modified/focused files
or symbols, avoiding full regression suite execution overhead.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set

logger = logging.getLogger(__name__)


class TestAssociationEngine:
    """Discovers targeted falsifiers and tests linked to touched files and symbols."""

    def __init__(self, storage: Any) -> None:
        self.storage = storage

    def find_associated_tests(
        self,
        touched_files: Sequence[str],
        touched_symbols: Sequence[str] | None = None,
    ) -> Dict[str, Any]:
        """
        Maps touched files and symbols to associated test files, test symbols,
        and generated command lines.
        """
        all_relations = self.storage.get_all_relations()
        all_symbols = self.storage.get_all_symbols()

        symbol_by_id = {s.get("symbol_id"): s for s in all_symbols if s.get("symbol_id")}
        touched_files_set = set(touched_files)
        touched_sym_set = set(touched_symbols or [])

        # Find symbols in touched files
        for s in all_symbols:
            if s.get("file_path") in touched_files_set:
                touched_sym_set.add(s.get("symbol_id"))

        # Traverse relations for 'tests' and 'falsifies'
        matched_test_files: Set[str] = set()
        matched_test_symbols: List[Dict[str, Any]] = []

        for rel in all_relations:
            src = rel.get("source_id") or rel.get("source")
            tgt = rel.get("target_id") or rel.get("target")
            kind = rel.get("kind", "")

            if kind in ("tests", "falsifies"):
                # Either src tests tgt, or tgt tests src
                if tgt in touched_sym_set:
                    test_sym = symbol_by_id.get(src)
                    if test_sym:
                        matched_test_symbols.append(test_sym)
                        if test_sym.get("file_path"):
                            matched_test_files.add(test_sym.get("file_path"))
                elif src in touched_sym_set:
                    test_sym = symbol_by_id.get(tgt)
                    if test_sym:
                        matched_test_symbols.append(test_sym)
                        if test_sym.get("file_path"):
                            matched_test_files.add(test_sym.get("file_path"))

        # Fallback: lexical matching if graph is sparse (e.g. test_xyz.py matches xyz.py)
        for fpath in touched_files:
            p = Path(fpath)
            stem = p.stem
            # Check for test_<stem>.py or <stem>_test.go, etc.
            for s in all_symbols:
                sym_file = s.get("file_path", "")
                if "test" in sym_file.lower() and stem.lower() in sym_file.lower():
                    matched_test_files.add(sym_file)
                    matched_test_symbols.append(s)

        # Generate targeted runner commands
        suggested_commands: List[str] = []
        for tf in sorted(matched_test_files):
            if tf.endswith(".py"):
                # Convert file path to unittest module dotted notation
                mod_name = tf.replace("/", ".").replace(".py", "")
                if mod_name.startswith("."):
                    mod_name = mod_name[1:]
                suggested_commands.append(f"python3 -m unittest {mod_name} -v")
            elif tf.endswith((".ts", ".js", ".tsx", ".jsx")):
                suggested_commands.append(f"npm test -- {tf}")
            elif tf.endswith(".rs"):
                suggested_commands.append(f"cargo test --test {Path(tf).stem}")
            elif tf.endswith(".go"):
                suggested_commands.append(f"go test -v ./{Path(tf).parent}")

        return {
            "touched_files": list(touched_files),
            "associated_test_files": sorted(matched_test_files),
            "associated_test_symbols": matched_test_symbols[:20],
            "suggested_commands": suggested_commands,
        }
