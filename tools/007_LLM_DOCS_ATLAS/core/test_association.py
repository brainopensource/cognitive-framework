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
        touched_files_set = {str(Path(f)).replace("\\", "/") for f in touched_files}
        touched_sym_set = set(touched_symbols or [])
        matched_test_files: Set[str] = set()
        matched_test_symbols: List[Dict[str, Any]] = []

        # Fast path: SQLite indexed queries (<3ms)
        is_real_storage = (
            hasattr(self.storage, "db_path")
            and isinstance(getattr(self.storage, "db_path", None), Path)
            and hasattr(self.storage, "get_connection")
        )
        if is_real_storage:
            con = self.storage.get_connection()
            if touched_files:
                placeholders = ",".join("?" for _ in touched_files_set)
                cur = con.execute(
                    f"SELECT id, name, file_path FROM symbols WHERE file_path IN ({placeholders})",
                    list(touched_files_set),
                )
                for r in cur.fetchall():
                    if r["id"]:
                        touched_sym_set.add(r["id"])
                    if r["name"]:
                        touched_sym_set.add(f"name:{r['name']}")

            if touched_sym_set:
                rel_placeholders = ",".join("?" for _ in touched_sym_set)
                cur_rel = con.execute(
                    f"""
                    SELECT r.source_id, r.target_id, r.kind, r.source_path, 
                           s.id as sym_id, s.name, s.file_path as sym_file, s.signature
                    FROM relations r
                    LEFT JOIN symbols s ON r.source_id = s.id
                    WHERE (r.target_id IN ({rel_placeholders}))
                      AND (r.source_path LIKE '%test%' OR r.kind IN ('tests', 'falsifies'))
                    """,
                    list(touched_sym_set),
                )
                for r in cur_rel.fetchall():
                    if r["source_path"]:
                        matched_test_files.add(r["source_path"])
                    if r["sym_file"]:
                        matched_test_files.add(r["sym_file"])
                    if r["name"]:
                        matched_test_symbols.append(dict(r))

            for tf in touched_files_set:
                stem = Path(tf).stem
                cur_lex = con.execute(
                    """
                    SELECT DISTINCT file_path FROM symbols 
                    WHERE (file_path LIKE '%test%' OR file_path LIKE 'test%') AND file_path LIKE ?
                    """,
                    (f"%{stem}%",),
                )
                for r in cur_lex.fetchall():
                    matched_test_files.add(r["file_path"])
        else:
            # Slow fallback for unit mocks
            all_relations = self.storage.get_all_relations()
            all_symbols = self.storage.get_all_symbols()
            symbol_by_id = {s.get("id") or s.get("symbol_id"): s for s in all_symbols if (s.get("id") or s.get("symbol_id"))}

            for s in all_symbols:
                s_file = str(Path(s.get("file_path", ""))).replace("\\", "/")
                if s_file in touched_files_set:
                    sym_id = s.get("id") or s.get("symbol_id")
                    if sym_id:
                        touched_sym_set.add(sym_id)

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

            for fpath in touched_files:
                stem = Path(fpath).stem
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
