"""AST and Code Intelligence Provider for multi-language repositories.

Supports Python (stdlib AST), TypeScript/JavaScript, Rust, and Go via
deterministic line/block scanning, plus generic fallback for any other code
extension declared in the active profile. All kinds are normalized through
`core.standardizer.normalize_kind` so FTS, ranking, packets, and health checks
speak one canonical vocabulary.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.ir import (
    ConfidenceTier,
    EntityKind,
    IREntity,
    IRRelation,
    IRSymbol,
    Provenance,
    RelationKind,
    SourceLocation,
    compute_symbol_id,
)
from ..core.models import Entity, ProviderResult, Relation
from ..core.standardizer import detect_language, normalize_kind
from .base import BaseProvider

#: Languages with a dedicated extractor below.
_NATIVE = {".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go"}


class CodeASTProvider(BaseProvider):
    """Extracts code symbols, signatures, calls, imports, and inheritance."""

    name = "code_ast"
    confidence_tier = ConfidenceTier.TREE_SITTER

    def collect(
        self,
        repo_root: Path | Any,
        incremental: bool = False,
        file_states: Optional[Dict[str, Dict[str, Any]]] = None,
        target_files: Optional[Sequence[Path | str]] = None,
        storage: Optional[Any] = None,
    ) -> ProviderResult:
        root = Path(repo_root.root) if (hasattr(repo_root, "root") and not isinstance(repo_root, Path)) else Path(repo_root)
        profile = getattr(repo_root, "profile", None)
        skip_dirs = {".git", ".venv", "node_modules", "__pycache__", "dist", "build", "site", "runs"} | (
            set(profile.excluded_dirs) if profile else set()
        )
        code_exts = set(profile.code_extensions) if profile else set(
            {".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".java", ".kt", ".cs", ".c", ".h", ".cpp", ".hpp", ".sh", ".rb", ".php", ".sql"}
        )
        symbols: List[IRSymbol] = []
        relations: List[IRRelation] = []
        legacy_entities: List[Entity] = []
        legacy_relations: List[Relation] = []

        if target_files is not None:
            resolved_targets = []
            for f in target_files:
                p = Path(f) if Path(f).is_absolute() else (root / f)
                if p.is_file() and p.suffix.lower() in code_exts and not any(x in p.parts for x in skip_dirs):
                    resolved_targets.append(p)
            code_files = resolved_targets
        else:
            code_files = [
                p for p in root.rglob("*")
                if p.is_file() and p.suffix.lower() in code_exts
                and not any(x in p.parts for x in skip_dirs)
            ]

        # Intermediate structures for Two-Pass AST resolution
        parsed_py_files: Dict[str, tuple[ast.AST, str]] = {}
        parsed_ts_files: Dict[str, tuple[str, List[IRSymbol]]] = {}
        file_symbols: Dict[str, List[IRSymbol]] = {}
        file_imports: Dict[str, Dict[str, str]] = {}
        symbol_by_id: Dict[str, IRSymbol] = {}
        symbol_by_qualname: Dict[str, IRSymbol] = {}
        symbols_by_name: Dict[str, List[IRSymbol]] = {}

        # =====================================================================
        # PASS 1: Symbol, Import, and Definition Collection
        # =====================================================================
        for fpath in code_files:
            rel_path = str(fpath.relative_to(root)).replace("\\", "/")
            ext = fpath.suffix.lower()

            try:
                content = fpath.read_text(errors="replace")
                lang = detect_language(rel_path)
                file_syms: List[IRSymbol] = []
                file_rels: List[IRRelation] = []

                if ext == ".py":
                    file_syms, file_rels, py_ast, py_imps = self._parse_python_pass1(rel_path, content)
                    if py_ast is not None:
                        parsed_py_files[rel_path] = (py_ast, content)
                        file_imports[rel_path] = py_imps
                elif ext in (".ts", ".tsx", ".js", ".jsx"):
                    file_syms, file_rels, ts_imps = self._parse_tsjs_pass1(rel_path, content)
                    parsed_ts_files[rel_path] = (content, file_syms)
                    file_imports[rel_path] = ts_imps
                elif ext == ".rs":
                    file_syms, file_rels = self._parse_rust(rel_path, content)
                elif ext == ".go":
                    file_syms, file_rels = self._parse_go(rel_path, content)
                elif lang == "text":
                    file_syms, file_rels = [], []
                else:
                    file_syms, file_rels = self._parse_generic(rel_path, content, lang)

                symbols.extend(file_syms)
                relations.extend(file_rels)
                file_symbols[rel_path] = file_syms

                for s in file_syms:
                    symbol_by_id[s.symbol_id] = s
                    symbol_by_qualname[s.qualified_name] = s
                    symbols_by_name.setdefault(s.name, []).append(s)

            except Exception:
                pass

        # =====================================================================
        # PASS 2: Calls & Targeted Tests Edge Resolution
        # =====================================================================
        # Python Pass 2
        for rel_path, (py_ast, content) in parsed_py_files.items():
            try:
                call_rels = self._extract_python_calls_pass2(
                    rel_path,
                    py_ast,
                    file_symbols.get(rel_path, []),
                    file_imports.get(rel_path, {}),
                    symbol_by_id,
                    symbol_by_qualname,
                    symbols_by_name,
                    storage=storage,
                )
                relations.extend(call_rels)
            except Exception:
                pass

        # TypeScript Pass 2
        for rel_path, (content, ts_syms) in parsed_ts_files.items():
            try:
                call_rels = self._extract_ts_calls_pass2(
                    rel_path,
                    content,
                    ts_syms,
                    file_imports.get(rel_path, {}),
                    symbol_by_qualname,
                    symbols_by_name,
                    storage=storage,
                )
                relations.extend(call_rels)
            except Exception:
                pass

        # Build legacy representations for backward compatibility
        for s in symbols:
            legacy_entities.append(
                Entity(
                    id=s.symbol_id,
                    kind=s.kind,
                    locator=f"{s.file_path}#L{s.location.start_line if s.location else 1}",
                    metadata={
                        "name": s.name,
                        "qualified_name": s.qualified_name,
                        "kind": s.kind,
                        "language": s.language,
                        "file_path": s.file_path,
                        "signature": s.signature,
                        "docstring": s.docstring
                    }
                )
            )

        for r in relations:
            legacy_relations.append(
                Relation(
                    source=r.source_id,
                    target=r.target_id,
                    kind=r.kind.value if isinstance(r.kind, RelationKind) else str(r.kind),
                    evidence=r.evidence
                )
            )

        res = ProviderResult(provider=self.name, entities=legacy_entities, relations=legacy_relations)
        res.metadata["ir_symbols"] = symbols
        res.metadata["ir_relations"] = relations
        return res

    def _parse_python_pass1(
        self, file_path: str, source: str
    ) -> tuple[List[IRSymbol], List[IRRelation], Optional[ast.AST], Dict[str, str]]:
        symbols: List[IRSymbol] = []
        relations: List[IRRelation] = []
        imports_map: Dict[str, str] = {}
        pkg = file_path.rsplit(".", 1)[0].replace("/", ".")

        try:
            tree = ast.parse(source)
        except Exception:
            syms, rels = self._parse_generic(file_path, source, "python")
            return syms, rels, None, imports_map

        def format_args(args: ast.arguments) -> str:
            res = [a.arg for a in args.args]
            return ", ".join(res)

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                sym_id = compute_symbol_id("repo", "python", pkg, node.name, "class")
                doc = ast.get_docstring(node)
                bases = []
                for b in node.bases:
                    try:
                        bases.append(ast.unparse(b))
                    except Exception:
                        if isinstance(b, ast.Name):
                            bases.append(b.id)
                sig = f"class {node.name}({', '.join(bases)}):" if bases else f"class {node.name}:"
                loc = SourceLocation(file_path, node.lineno, getattr(node, "end_lineno", node.lineno))

                sym = IRSymbol(
                    symbol_id=sym_id,
                    name=node.name,
                    qualified_name=f"{pkg}.{node.name}",
                    kind="class",
                    language="python",
                    file_path=file_path,
                    signature=sig,
                    docstring=doc,
                    location=loc
                )
                symbols.append(sym)

                # Inheritance relations
                for base_name in bases:
                    base_id = compute_symbol_id("repo", "python", "", base_name, "class")
                    relations.append(
                        IRRelation(
                            id=f"{sym_id}:inherits:{base_name}",
                            source_id=sym_id,
                            target_id=base_id,
                            kind=RelationKind.INHERITS,
                            confidence_tier=ConfidenceTier.COMPILER,
                            source_path=file_path
                        )
                    )

                # Methods
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        m_name = f"{node.name}.{item.name}"
                        m_id = compute_symbol_id("repo", "python", pkg, m_name, "method")
                        m_doc = ast.get_docstring(item)
                        m_sig = f"def {item.name}({format_args(item.args)}):"
                        m_loc = SourceLocation(file_path, item.lineno, getattr(item, "end_lineno", item.lineno))

                        m_sym = IRSymbol(
                            symbol_id=m_id,
                            name=item.name,
                            qualified_name=f"{pkg}.{m_name}",
                            kind="method",
                            language="python",
                            file_path=file_path,
                            signature=m_sig,
                            docstring=m_doc,
                            location=m_loc
                        )
                        symbols.append(m_sym)

                        relations.append(
                            IRRelation(
                                id=f"{sym_id}:defines:{m_id}",
                                source_id=sym_id,
                                target_id=m_id,
                                kind=RelationKind.DEFINES,
                                confidence_tier=ConfidenceTier.COMPILER,
                                source_path=file_path
                            )
                        )

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_id = compute_symbol_id("repo", "python", pkg, node.name, "function")
                doc = ast.get_docstring(node)
                sig = f"def {node.name}({format_args(node.args)}):"
                loc = SourceLocation(file_path, node.lineno, getattr(node, "end_lineno", node.lineno))

                sym = IRSymbol(
                    symbol_id=fn_id,
                    name=node.name,
                    qualified_name=f"{pkg}.{node.name}",
                    kind="function",
                    language="python",
                    file_path=file_path,
                    signature=sig,
                    docstring=doc,
                    location=loc
                )
                symbols.append(sym)

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom):
                    mod_name = node.module or ""
                    if mod_name:
                        relations.append(
                            IRRelation(
                                id=f"{file_path}:imports:{mod_name}",
                                source_id=file_path,
                                target_id=mod_name,
                                kind=RelationKind.IMPORTS,
                                confidence_tier=ConfidenceTier.COMPILER,
                                source_path=file_path
                            )
                        )
                    for alias in node.names:
                        local_name = alias.asname or alias.name
                        if local_name:
                            full_target = f"{mod_name}.{alias.name}" if mod_name else alias.name
                            imports_map[local_name] = full_target
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        local_name = alias.asname or alias.name
                        if local_name and alias.name:
                            imports_map[local_name] = alias.name
                            relations.append(
                                IRRelation(
                                    id=f"{file_path}:imports:{alias.name}",
                                    source_id=file_path,
                                    target_id=alias.name,
                                    kind=RelationKind.IMPORTS,
                                    confidence_tier=ConfidenceTier.COMPILER,
                                    source_path=file_path
                                )
                            )

        return symbols, relations, tree, imports_map

    def _extract_python_calls_pass2(
        self,
        file_path: str,
        tree: ast.AST,
        local_symbols: List[IRSymbol],
        imports_map: Dict[str, str],
        symbol_by_id: Dict[str, IRSymbol],
        symbol_by_qualname: Dict[str, IRSymbol],
        symbols_by_name: Dict[str, List[IRSymbol]],
        storage: Optional[Any] = None,
    ) -> List[IRRelation]:
        relations: List[IRRelation] = []
        pkg = file_path.rsplit(".", 1)[0].replace("/", ".")
        is_test_file = "test" in file_path.lower() or file_path.startswith("test")

        local_sym_map = {s.name: s for s in local_symbols}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_qualname = f"{pkg}.{class_name}.{item.name}"
                        m_sym = symbol_by_qualname.get(method_qualname)
                        if not m_sym:
                            continue
                        self._collect_calls_in_function(
                            m_sym.symbol_id,
                            item,
                            file_path,
                            class_name,
                            local_sym_map,
                            imports_map,
                            symbol_by_qualname,
                            symbols_by_name,
                            relations,
                            is_test_file,
                            storage=storage,
                        )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_qualname = f"{pkg}.{node.name}"
                fn_sym = symbol_by_qualname.get(fn_qualname)
                if not fn_sym:
                    continue
                self._collect_calls_in_function(
                    fn_sym.symbol_id,
                    node,
                    file_path,
                    None,
                    local_sym_map,
                    imports_map,
                    symbol_by_qualname,
                    symbols_by_name,
                    relations,
                    is_test_file,
                    storage=storage,
                )

        return relations

    def _collect_calls_in_function(
        self,
        enclosing_id: str,
        func_node: ast.AST,
        file_path: str,
        current_class: Optional[str],
        local_sym_map: Dict[str, IRSymbol],
        imports_map: Dict[str, str],
        symbol_by_qualname: Dict[str, IRSymbol],
        symbols_by_name: Dict[str, List[IRSymbol]],
        relations: List[IRRelation],
        is_test_file: bool,
        storage: Optional[Any] = None,
    ) -> None:
        seen_calls: Set[str] = set()

        for child in ast.walk(func_node):
            if isinstance(child, ast.Call):
                target_id = None
                confidence = ConfidenceTier.HEURISTIC
                call_name = ""

                if isinstance(child.func, ast.Name):
                    call_name = child.func.id
                    # 1. Check local file symbols
                    if call_name in local_sym_map:
                        target_id = local_sym_map[call_name].symbol_id
                        confidence = ConfidenceTier.COMPILER
                    # 2. Check imported symbols
                    elif call_name in imports_map:
                        imp_qual = imports_map[call_name]
                        if imp_qual in symbol_by_qualname:
                            target_id = symbol_by_qualname[imp_qual].symbol_id
                            confidence = ConfidenceTier.COMPILER
                        elif call_name in symbols_by_name:
                            target_id = symbols_by_name[call_name][0].symbol_id
                            confidence = ConfidenceTier.STRUCTURED_DOC
                    # 3. Check globally unique name
                    elif call_name in symbols_by_name and len(symbols_by_name[call_name]) == 1:
                        target_id = symbols_by_name[call_name][0].symbol_id
                        confidence = ConfidenceTier.STRUCTURED_DOC
                    else:
                        target_id = f"name:{call_name}"

                elif isinstance(child.func, ast.Attribute):
                    attr_name = child.func.attr
                    val_str = ""
                    try:
                        val_str = ast.unparse(child.func.value)
                    except Exception:
                        if isinstance(child.func.value, ast.Name):
                            val_str = child.func.value.id

                    call_name = f"{val_str}.{attr_name}" if val_str else attr_name

                    # self.method() in class
                    if val_str == "self" and current_class:
                        pkg = file_path.rsplit(".", 1)[0].replace("/", ".")
                        target_qual = f"{pkg}.{current_class}.{attr_name}"
                        if target_qual in symbol_by_qualname:
                            target_id = symbol_by_qualname[target_qual].symbol_id
                            confidence = ConfidenceTier.COMPILER
                        elif attr_name in local_sym_map:
                            target_id = local_sym_map[attr_name].symbol_id
                            confidence = ConfidenceTier.COMPILER
                    elif val_str in imports_map:
                        imp_qual = f"{imports_map[val_str]}.{attr_name}"
                        if imp_qual in symbol_by_qualname:
                            target_id = symbol_by_qualname[imp_qual].symbol_id
                            confidence = ConfidenceTier.COMPILER
                        elif attr_name in symbols_by_name:
                            target_id = symbols_by_name[attr_name][0].symbol_id
                            confidence = ConfidenceTier.STRUCTURED_DOC
                    elif f"{val_str}.{attr_name}" in symbols_by_name:
                        target_id = symbols_by_name[f"{val_str}.{attr_name}"][0].symbol_id
                        confidence = ConfidenceTier.STRUCTURED_DOC
                    elif attr_name in symbols_by_name:
                        # Match method on class if val_str is a known class name
                        candidates = [s for s in symbols_by_name[attr_name] if val_str in s.qualified_name]
                        if candidates:
                            target_id = candidates[0].symbol_id
                            confidence = ConfidenceTier.STRUCTURED_DOC
                        else:
                            target_id = symbols_by_name[attr_name][0].symbol_id
                            confidence = ConfidenceTier.HEURISTIC
                    else:
                        target_id = f"name:{call_name}"

                if target_id and target_id.startswith("name:") and storage is not None:
                    lookup_name = target_id[5:]
                    db_syms = storage.get_symbol(lookup_name, exact=True)
                    if not db_syms and "." in lookup_name:
                        db_syms = storage.get_symbol(lookup_name.split(".")[-1], exact=True)
                    if db_syms:
                        target_id = db_syms[0]["id"]
                        confidence = ConfidenceTier.STRUCTURED_DOC

                if not target_id:
                    continue

                call_key = f"{enclosing_id}:{target_id}:{getattr(child, 'lineno', 1)}"
                if call_key in seen_calls:
                    continue
                seen_calls.add(call_key)

                loc = SourceLocation(
                    file_path,
                    getattr(child, "lineno", 1),
                    getattr(child, "end_lineno", getattr(child, "lineno", 1)),
                    getattr(child, "col_offset", 0),
                )

                relations.append(
                    IRRelation(
                        id=f"{enclosing_id}:calls:{target_id}:{getattr(child, 'lineno', 1)}",
                        source_id=enclosing_id,
                        target_id=target_id,
                        kind=RelationKind.CALLS,
                        confidence_tier=confidence,
                        source_path=file_path,
                        location=loc,
                    )
                )

                if is_test_file and target_id.startswith("sym:"):
                    relations.append(
                        IRRelation(
                            id=f"{enclosing_id}:tests:{target_id}",
                            source_id=enclosing_id,
                            target_id=target_id,
                            kind=RelationKind.TESTS,
                            confidence_tier=confidence,
                            source_path=file_path,
                            location=loc,
                        )
                    )

    def _parse_tsjs_pass1(
        self, file_path: str, source: str
    ) -> tuple[List[IRSymbol], List[IRRelation], Dict[str, str]]:
        lang = detect_language(file_path)
        pkg = file_path.rsplit(".", 1)[0].replace("/", ".")
        symbols: List[IRSymbol] = []
        relations: List[IRRelation] = []
        imports_map: Dict[str, str] = {}
        patterns = [
            (r"^(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)", "class"),
            (r"^(?:export\s+)?(?:default\s+)?(?:declare\s+)?interface\s+([A-Za-z_$][\w$]*)", "interface"),
            (r"^(?:export\s+)?(?:default\s+)?type\s+([A-Za-z_$][\w$]*)\s*=", "type"),
            (r"^(?:export\s+)?(?:const\s+)?enum\s+([A-Za-z_$][\w$]*)", "enum"),
            (r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(", "function"),
            (r"^(?:export\s+)?(?:default\s+)?const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>", "function"),
            (r"^(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*:", "const"),
        ]
        for idx, line in enumerate(source.splitlines(), 1):
            trimmed = line.strip()
            m_import = re.match(
                r"^import\s+(?:type\s+)?(?:\{([^}]+)\}|([A-Za-z_$][\w$]*))\s+from\s+['\"]([^'\"]+)['\"]", trimmed)
            if m_import:
                mod_path = m_import.group(3)
                self._add_import(relations, file_path, lang, mod_path)
                if m_import.group(1):
                    for item in m_import.group(1).split(","):
                        item = item.strip()
                        if " as " in item:
                            orig, alias = item.split(" as ")
                            imports_map[alias.strip()] = f"{mod_path}.{orig.strip()}"
                        elif item:
                            imports_map[item] = f"{mod_path}.{item}"
                elif m_import.group(2):
                    imports_map[m_import.group(2)] = mod_path
                continue

            for pat, kind in patterns:
                m = re.match(pat, trimmed)
                if m:
                    symbols.append(self._mk_symbol(
                        file_path, lang, pkg, m.group(1), kind, idx, trimmed))
                    break
        return symbols, relations, imports_map

    def _extract_ts_calls_pass2(
        self,
        file_path: str,
        source: str,
        symbols: List[IRSymbol],
        imports_map: Dict[str, str],
        symbol_by_qualname: Dict[str, IRSymbol],
        symbols_by_name: Dict[str, List[IRSymbol]],
        storage: Optional[Any] = None,
    ) -> List[IRRelation]:
        relations: List[IRRelation] = []
        is_test_file = "test" in file_path.lower() or file_path.endswith((".test.ts", ".spec.ts"))
        local_sym_map = {s.name: s for s in symbols}

        # Simple line-by-line call scanner for TS
        current_sym = symbols[0] if symbols else None
        call_pattern = re.compile(r"\b([A-Za-z_$][\w$]*)(?:\.([A-Za-z_$][\w$]*))?\s*\(")

        for idx, line in enumerate(source.splitlines(), 1):
            trimmed = line.strip()
            # Update current enclosing symbol if line matches a symbol location
            for s in symbols:
                if s.location and s.location.start_line <= idx <= s.location.end_line:
                    current_sym = s
                    break

            if not current_sym:
                continue

            for m in call_pattern.finditer(trimmed):
                base_name = m.group(1)
                attr_name = m.group(2)
                if base_name in ("if", "for", "while", "switch", "catch", "import", "require", "super"):
                    continue

                call_expr = f"{base_name}.{attr_name}" if attr_name else base_name
                target_id = None
                conf = ConfidenceTier.HEURISTIC

                if not attr_name:
                    if base_name in local_sym_map:
                        target_id = local_sym_map[base_name].symbol_id
                        conf = ConfidenceTier.COMPILER
                    elif base_name in imports_map:
                        imp = imports_map[base_name]
                        if imp in symbol_by_qualname:
                            target_id = symbol_by_qualname[imp].symbol_id
                            conf = ConfidenceTier.COMPILER
                        elif base_name in symbols_by_name:
                            target_id = symbols_by_name[base_name][0].symbol_id
                            conf = ConfidenceTier.STRUCTURED_DOC
                    elif base_name in symbols_by_name and len(symbols_by_name[base_name]) == 1:
                        target_id = symbols_by_name[base_name][0].symbol_id
                        conf = ConfidenceTier.STRUCTURED_DOC
                    else:
                        target_id = f"name:{base_name}"
                else:
                    if attr_name in symbols_by_name:
                        target_id = symbols_by_name[attr_name][0].symbol_id
                        conf = ConfidenceTier.STRUCTURED_DOC
                    else:
                        target_id = f"name:{call_expr}"

                if target_id and target_id.startswith("name:") and storage is not None:
                    lookup_name = target_id[5:]
                    db_syms = storage.get_symbol(lookup_name, exact=True)
                    if not db_syms and "." in lookup_name:
                        db_syms = storage.get_symbol(lookup_name.split(".")[-1], exact=True)
                    if db_syms:
                        target_id = db_syms[0]["id"]
                        conf = ConfidenceTier.STRUCTURED_DOC

                loc = SourceLocation(file_path, idx, idx)
                relations.append(
                    IRRelation(
                        id=f"{current_sym.symbol_id}:calls:{target_id}:{idx}",
                        source_id=current_sym.symbol_id,
                        target_id=target_id,
                        kind=RelationKind.CALLS,
                        confidence_tier=conf,
                        source_path=file_path,
                        location=loc,
                    )
                )
                if is_test_file and target_id.startswith("sym:"):
                    relations.append(
                        IRRelation(
                            id=f"{current_sym.symbol_id}:tests:{target_id}",
                            source_id=current_sym.symbol_id,
                            target_id=target_id,
                            kind=RelationKind.TESTS,
                            confidence_tier=conf,
                            source_path=file_path,
                            location=loc,
                        )
                    )

        return relations

        return symbols, relations

    def _parse_generic_code(self, file_path: str, source: str, ext: str):  # pragma: no cover - deprecated
        """Deprecated: superseded by _parse_generic / per-language extractors."""
        return self._parse_generic(file_path, source, detect_language(file_path))
# ------------------------------------------------------------------
    # Shared symbol factory + import edge helper
    # ------------------------------------------------------------------

    def _mk_symbol(
        self,
        file_path: str,
        lang: str,
        pkg: str,
        name: str,
        kind: str,
        line: int,
        signature: str,
        doc: str | None = None,
        end_line: int | None = None,
    ) -> IRSymbol:
        return IRSymbol(
            symbol_id=compute_symbol_id("repo", lang, pkg, name, kind),
            name=name,
            qualified_name=f"{pkg}.{name}",
            kind=normalize_kind(kind),
            language=lang,
            file_path=file_path,
            signature=(signature or "")[:220],
            docstring=doc,
            location=SourceLocation(file_path, line, end_line or line),
        )

    def _add_import(
        self,
        relations: list[IRRelation],
        file_path: str,
        lang: str,
        module: str,
    ) -> None:
        module = (module or "").strip().strip("'\"")
        if not module:
            return
        relations.append(IRRelation(
            id=f"{file_path}:imports:{module}",
            source_id=file_path,
            target_id=module,
            kind=RelationKind.IMPORTS,
            confidence_tier=ConfidenceTier.HEURISTIC,
            source_path=file_path,
        ))

    def _parse_python(self, file_path: str, source: str) -> tuple[list[IRSymbol], list[IRRelation]]:
        syms, rels, _, _ = self._parse_python_pass1(file_path, source)
        return syms, rels

    # ------------------------------------------------------------------
    # TypeScript / JavaScript
    # ------------------------------------------------------------------

    def _parse_tsjs(self, file_path: str, source: str) -> tuple[list[IRSymbol], list[IRRelation]]:
        lang = detect_language(file_path)
        pkg = file_path.rsplit(".", 1)[0].replace("/", ".")
        symbols: list[IRSymbol] = []
        relations: list[IRRelation] = []
        patterns = [
            (r"^(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)", "class"),
            (r"^(?:export\s+)?(?:default\s+)?(?:declare\s+)?interface\s+([A-Za-z_$][\w$]*)", "interface"),
            (r"^(?:export\s+)?(?:default\s+)?type\s+([A-Za-z_$][\w$]*)\s*=", "type"),
            (r"^(?:export\s+)?(?:const\s+)?enum\s+([A-Za-z_$][\w$]*)", "enum"),
            (r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(", "function"),
            (r"^(?:export\s+)?(?:default\s+)?const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>", "function"),
            (r"^(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*:", "const"),
        ]
        for idx, line in enumerate(source.splitlines(), 1):
            trimmed = line.strip()
            m_import = re.match(
                r"^import\s+(?:type\s+)?(?:[\w*{}\s,]+?\s+from\s+)?['\"]([^'\"]+)['\"]", trimmed)
            if m_import:
                self._add_import(relations, file_path, lang, m_import.group(1))
                continue
            m_require = re.match(
                r"^(?:const|let|var)\s+[\w$]+\s*=\s*require\(\s*['\"]([^'\"]+)['\"]\s*\)", trimmed)
            if m_require:
                self._add_import(relations, file_path, lang, m_require.group(1))
                continue
            for pat, kind in patterns:
                m = re.match(pat, trimmed)
                if m:
                    symbols.append(self._mk_symbol(
                        file_path, lang, pkg, m.group(1), kind, idx, trimmed))
                    break
        return symbols, relations
# ------------------------------------------------------------------
    # Rust
    # ------------------------------------------------------------------

    def _parse_rust(self, file_path: str, source: str) -> tuple[list[IRSymbol], list[IRRelation]]:
        lang = "rust"
        pkg = file_path.rsplit(".", 1)[0].replace("/", ".")
        symbols: list[IRSymbol] = []
        relations: list[IRRelation] = []
        patterns = [
            (r"^(?:pub\s+)?(?:async\s+)?(?:unsafe\s+)?fn\s+([a-zA-Z0-9_]+)\s*\(", "function"),
            (r"^(?:pub\s+)?struct\s+([A-Za-z0-9_]+)\b", "struct"),
            (r"^(?:pub\s+)?enum\s+([A-Za-z0-9_]+)\b", "enum"),
            (r"^(?:pub\s+)?trait\s+([A-Za-z0-9_]+)\b", "interface"),
            (r"^(?:pub\s+)?type\s+([A-Za-z0-9_]+)\s*=", "type"),
            (r"^(?:pub\s+)?const\s+([A-Za-z0-9_]+)\s*:", "const"),
            (r"^(?:pub\s+)?mod\s+([a-zA-Z0-9_]+)\b", "module"),
        ]
        for idx, line in enumerate(source.splitlines(), 1):
            trimmed = line.strip()
            m_use = re.match(r"^(?:pub\s+)?use\s+([a-zA-Z0-9_:]+)", trimmed)
            if m_use:
                self._add_import(relations, file_path, lang, m_use.group(1))
                continue
            m_impl = re.match(r"^impl\s*(?:<[^>]+>)?\s+([A-Za-z0-9_]+)", trimmed)
            if m_impl:
                relations.append(IRRelation(
                    id=f"{file_path}:implements:{m_impl.group(1)}",
                    source_id=compute_symbol_id("repo", lang, pkg, "impl", "class"),
                    target_id=compute_symbol_id("repo", lang, pkg, m_impl.group(1), "interface"),
                    kind=RelationKind.IMPLEMENTS,
                    confidence_tier=ConfidenceTier.HEURISTIC,
                    source_path=file_path,
                ))
                continue
            for pat, kind in patterns:
                m = re.match(pat, trimmed)
                if m:
                    symbols.append(self._mk_symbol(
                        file_path, lang, pkg, m.group(1), kind, idx, trimmed))
                    break
        return symbols, relations
# ------------------------------------------------------------------
    # Go
    # ------------------------------------------------------------------

    def _parse_go(self, file_path: str, source: str) -> tuple[list[IRSymbol], list[IRRelation]]:
        lang = "go"
        pkg = file_path.rsplit(".", 1)[0].replace("/", ".")
        symbols: list[IRSymbol] = []
        relations: list[IRRelation] = []
        in_import_block = False
        for idx, line in enumerate(source.splitlines(), 1):
            trimmed = line.strip()
            if re.match(r"^import\s*\($", trimmed):
                in_import_block = True
                continue
            if in_import_block:
                if trimmed == ")":
                    in_import_block = False
                    continue
                m_block = re.match(r"^(?:[a-zA-Z0-9_]+\s+)?[\"']?([^\"']+)[\"']?", trimmed)
                if m_block:
                    self._add_import(relations, file_path, lang, m_block.group(1))
                continue
            m_import = re.match(r"^import\s+[\"']?([^\"']+)[\"']?\s*$", trimmed)
            if m_import:
                self._add_import(relations, file_path, lang, m_import.group(1))
                continue
            m_package = re.match(r"^package\s+([A-Za-z0-9_]+)", trimmed)
            if m_package:
                symbols.append(self._mk_symbol(
                    file_path, lang, pkg, m_package.group(1), "module", idx, trimmed))
                continue
            m_func = re.match(r"^func\s+(?:\(([^)]*)\)\s+)?([A-Za-z0-9_]+)\s*\(", trimmed)
            if m_func:
                receiver, name = m_func.group(1), m_func.group(2)
                kind = "method" if receiver else "function"
                symbols.append(self._mk_symbol(
                    file_path, lang, pkg, name, kind, idx, trimmed))
                continue
            m_struct = re.match(r"^type\s+([A-Za-z0-9_]+)\s+struct\s*\{?", trimmed)
            if m_struct:
                symbols.append(self._mk_symbol(
                    file_path, lang, pkg, m_struct.group(1), "struct", idx, trimmed))
                continue
            m_iface = re.match(r"^type\s+([A-Za-z0-9_]+)\s+interface\s*\{?", trimmed)
            if m_iface:
                symbols.append(self._mk_symbol(
                    file_path, lang, pkg, m_iface.group(1), "interface", idx, trimmed))
                continue
            m_alias = re.match(r"^type\s+([A-Za-z0-9_]+)\s+=", trimmed)
            if m_alias:
                symbols.append(self._mk_symbol(
                    file_path, lang, pkg, m_alias.group(1), "type", idx, trimmed))
                continue
            m_const = re.match(r"^const\s+([A-Za-z0-9_]+)\s*=?", trimmed)
            if m_const:
                symbols.append(self._mk_symbol(
                    file_path, lang, pkg, m_const.group(1), "const", idx, trimmed))
                continue
            m_var = re.match(r"^var\s+([A-Za-z0-9_]+)\s*=?", trimmed)
            if m_var:
                symbols.append(self._mk_symbol(
                    file_path, lang, pkg, m_var.group(1), "var", idx, trimmed))
        return symbols, relations
# ------------------------------------------------------------------
    # Generic fallback (Java, Kotlin, C#, C/C++, Ruby, PHP, bash, ...)
    # ------------------------------------------------------------------

    def _parse_generic(self, file_path: str, source: str, lang: str) -> tuple[list[IRSymbol], list[IRRelation]]:
        pkg = file_path.rsplit(".", 1)[0].replace("/", ".")
        symbols: list[IRSymbol] = []
        relations: list[IRRelation] = []
        patterns = [
            (r"^(?:public\s+|private\s+|protected\s+|internal\s+|export\s+)*(?:abstract\s+|final\s+|sealed\s+)*class\s+([A-Za-z_$][\w$]*)", "class"),
            (r"^(?:public\s+|private\s+|internal\s+|export\s+)*(?:abstract\s+|final\s+|sealed\s+)*interface\s+([A-Za-z_$][\w$]*)", "interface"),
            (r"^(?:public\s+|private\s+|internal\s+|export\s+)*enum\s+([A-Za-z_$][\w$]*)", "enum"),
            (r"^(?:public\s+|private\s+|internal\s+|export\s+)*(?:abstract\s+)?struct\s+([A-Za-z_$][\w$]*)", "struct"),
            (r"^(?:def\s+|function\s+|fun\s+|fn\s+)([A-Za-z_$][\w$]*)\s*\(", "function"),
            (r"^(?:public\s+|private\s+|protected\s+|internal\s+)*(?:static\s+)?(?:async\s+)?(?:function\s+)?([A-Za-z_$][\w$]*)\s*\(", "function"),
            (r"^(?:public\s+|private\s+|protected\s+|internal\s+)*(?:static\s+)?(?:final\s+)?const\s+([A-Za-z_$][\w$]*)\s*=", "const"),
        ]
        for idx, line in enumerate(source.splitlines(), 1):
            trimmed = line.strip()
            for pat, kind in patterns:
                m = re.match(pat, trimmed)
                if m and m.group(1):
                    symbols.append(self._mk_symbol(
                        file_path, lang, pkg, m.group(1), kind, idx, trimmed))
                    break
        return symbols, relations
