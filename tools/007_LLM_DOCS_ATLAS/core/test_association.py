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

        symbol_by_id = {s.get("id") or s.get("symbol_id"): s for s in all_symbols if (s.get("id") or s.get("symbol_id"))}
        touched_files_set = {str(Path(f)).replace("\\", "/") for f in touched_files}
        touched_sym_set = set(touched_symbols or [])

        # Find symbols in touched files
        for s in all_symbols:
            s_file = str(Path(s.get("file_path", ""))).replace("\\", "/")
            if s_file in touched_files_set:
                sym_id = s.get("id") or s.get("symbol_id")
                if sym_id:
                    touched_sym_set.add(sym_id)

        # Traverse relations for 'tests', 'falsifies', and 'calls'
        matched_test_files: Set[str] = set()
        matched_test_symbols: List[Dict[str, Any]] = []

        seen_sym_ids: Set[str] = set()
        for rel in all_relations:
            src = rel.get("source_id") or rel.get("source")
            tgt = rel.get("target_id") or rel.get("target")
            kind = rel.get("kind", "")
            src_path = rel.get("source_path") or ""

            is_test_rel = "test" in src_path.lower() or src_path.startswith("test")

            if kind in ("tests", "falsifies", "calls"):
                if tgt in touched_sym_set:
                    if is_test_rel:
                        if src_path:
                            matched_test_files.add(src_path)
                        test_sym = symbol_by_id.get(src)
                        if test_sym:
                            s_id = test_sym.get("id") or test_sym.get("symbol_id")
                            if s_id and s_id not in seen_sym_ids:
                                seen_sym_ids.add(s_id)
                                matched_test_symbols.append(test_sym)
                            if test_sym.get("file_path"):
                                matched_test_files.add(test_sym.get("file_path"))
                elif src in touched_sym_set and kind in ("tests", "falsifies"):
                    test_sym = symbol_by_id.get(tgt)
                    if test_sym:
                        s_id = test_sym.get("id") or test_sym.get("symbol_id")
                        if s_id and s_id not in seen_sym_ids:
                            seen_sym_ids.add(s_id)
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
