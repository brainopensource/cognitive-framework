"""AST and Code Intelligence Provider for Python and multi-language repositories."""
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
from .base import BaseProvider


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
        skip_dirs = {".git", ".venv", "node_modules", "__pycache__"} | (
            set(profile.excluded_dirs) if profile else set()
        )
        symbols: List[IRSymbol] = []
        relations: List[IRRelation] = []
        legacy_entities: List[Entity] = []
        legacy_relations: List[Relation] = []

        code_files = [
            p for p in root.rglob("*")
            if p.is_file() and p.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go"}
            and not any(x in p.parts for x in skip_dirs)
        ]

        for fpath in code_files:
            rel_path = str(fpath.relative_to(root)).replace("\\", "/")
            ext = fpath.suffix.lower()

            try:
                content = fpath.read_text(errors="replace")
                if ext == ".py":
                    syms, rels = self._parse_python(rel_path, content)
                else:
                    syms, rels = self._parse_generic_code(rel_path, content, ext)

                symbols.extend(syms)
                relations.extend(rels)

                for s in syms:
                    legacy_entities.append(
                        Entity(
                            id=s.symbol_id,
                            kind="symbol",
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
            return self._parse_generic_code(file_path, source, ".py")

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

    def _parse_generic_code(self, file_path: str, source: str, ext: str) -> tuple[List[IRSymbol], List[IRRelation]]:
        symbols: List[IRSymbol] = []
        relations: List[IRRelation] = []
        lang_map = {".ts": "typescript", ".tsx": "typescript", ".js": "javascript", ".rs": "rust", ".go": "go", ".py": "python"}
        lang = lang_map.get(ext, "unknown")
        pkg = file_path.rsplit(".", 1)[0].replace("/", ".")

        patterns = [
            (r"^(?:pub\s+)?(?:async\s+)?fn\s+([a-zA-Z0-9_]+)\s*\(", "function"),
            (r"^(?:pub\s+)?struct\s+([a-zA-Z0-9_]+)\b", "struct"),
            (r"^(?:pub\s+)?enum\s+([a-zA-Z0-9_]+)\b", "enum"),
            (r"^(?:pub\s+)?trait\s+([a-zA-Z0-9_]+)\b", "interface"),
            (r"^(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z0-9_]+)\s*\(", "function"),
            (r"^(?:export\s+)?class\s+([a-zA-Z0-9_]+)\b", "class"),
            (r"^(?:export\s+)?interface\s+([a-zA-Z0-9_]+)\b", "interface"),
            (r"^(?:export\s+)?const\s+([a-zA-Z0-9_]+)\s*=\s*(?:\([^)]*\)|[a-zA-Z0-9_]+)\s*=>", "function"),
            (r"^func\s+(?:\([^)]+\)\s+)?([a-zA-Z0-9_]+)\s*\(", "function"),
            (r"^type\s+([a-zA-Z0-9_]+)\s+struct\b", "struct"),
            (r"^type\s+([a-zA-Z0-9_]+)\s+interface\b", "interface"),
        ]

        lines = source.splitlines()
        for idx, line in enumerate(lines, 1):
            trimmed = line.strip()
            for pat, kind in patterns:
                m = re.match(pat, trimmed)
                if m:
                    sym_name = m.group(1)
                    sym_id = compute_symbol_id("repo", lang, pkg, sym_name, kind)
                    loc = SourceLocation(file_path, idx, idx)
                    symbols.append(
                        IRSymbol(
                            symbol_id=sym_id,
                            name=sym_name,
                            qualified_name=f"{pkg}.{sym_name}",
                            kind=kind,
                            language=lang,
                            file_path=file_path,
                            signature=trimmed[:120],
                            location=loc
                        )
                    )
                    break

        return symbols, relations
