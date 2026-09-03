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
    ) -> ProviderResult:
        root = repo_root.root if hasattr(repo_root, "root") else Path(repo_root)
        profile = getattr(repo_root, "profile", None)
        skip_dirs = {".git", ".venv", "node_modules", "__pycache__", "dist", "build", "site"} | (
            set(profile.excluded_dirs) if profile else set()
        )
        code_exts = set(profile.code_extensions) if profile else set(
            {".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".java", ".kt", ".cs", ".c", ".h", ".cpp", ".hpp", ".sh", ".rb", ".php", ".sql"}
        )
        symbols: List[IRSymbol] = []
        relations: List[IRRelation] = []
        legacy_entities: List[Entity] = []
        legacy_relations: List[Relation] = []

        code_files = [
            p for p in root.rglob("*")
            if p.is_file() and p.suffix.lower() in code_exts
            and not any(x in p.parts for x in skip_dirs)
        ]

        for fpath in code_files:
            rel_path = str(fpath.relative_to(root)).replace("\\", "/")
            ext = fpath.suffix.lower()

            try:
                content = fpath.read_text(errors="replace")
                lang = detect_language(rel_path)
                if ext == ".py":
                    syms, rels = self._parse_python(rel_path, content)
                elif ext in (".ts", ".tsx", ".js", ".jsx"):
                    syms, rels = self._parse_tsjs(rel_path, content)
                elif ext == ".rs":
                    syms, rels = self._parse_rust(rel_path, content)
                elif ext == ".go":
                    syms, rels = self._parse_go(rel_path, content)
                elif lang == "text":
                    syms, rels = [], []
                else:
                    syms, rels = self._parse_generic(rel_path, content, lang)

                symbols.extend(syms)
                relations.extend(rels)

                for s in syms:
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

                for r in rels:
                    legacy_relations.append(
                        Relation(
                            source=r.source_id,
                            target=r.target_id,
                            kind=r.kind.value if isinstance(r.kind, RelationKind) else str(r.kind),
                            evidence=r.evidence
                        )
                    )
            except Exception:
                pass

        res = ProviderResult(provider=self.name, entities=legacy_entities, relations=legacy_relations)
        res.metadata["ir_symbols"] = symbols
        res.metadata["ir_relations"] = relations
        return res

    def _parse_python(self, file_path: str, source: str) -> tuple[List[IRSymbol], List[IRRelation]]:
        symbols: List[IRSymbol] = []
        relations: List[IRRelation] = []
        pkg = file_path.rsplit(".", 1)[0].replace("/", ".")

        try:
            tree = ast.parse(source)
        except Exception:
            return self._parse_generic(file_path, source, "python")

        def format_args(args: ast.arguments) -> str:
            res = [a.arg for a in args.args]
            return ", ".join(res)

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                sym_id = compute_symbol_id("repo", "python", pkg, node.name, "class")
                doc = ast.get_docstring(node)
                bases = [ast.unparse(b) for b in node.bases]
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

                # If this is a test function, link tests
                if node.name.startswith("test_") or "test" in file_path.lower():
                    target_candidate = node.name.replace("test_", "")
                    relations.append(
                        IRRelation(
                            id=f"{fn_id}:tests:{target_candidate}",
                            source_id=fn_id,
                            target_id=target_candidate,
                            kind=RelationKind.TESTS,
                            confidence_tier=ConfidenceTier.STRUCTURED_DOC,
                            source_path=file_path
                        )
                    )

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    relations.append(
                        IRRelation(
                            id=f"{file_path}:imports:{node.module}",
                            source_id=file_path,
                            target_id=node.module,
                            kind=RelationKind.IMPORTS,
                            confidence_tier=ConfidenceTier.COMPILER,
                            source_path=file_path
                        )
                    )

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
