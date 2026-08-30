"""Code skeletonization and representation generator.

Produces compact structural outlines (FULL, SKELETON, SIGNATURE, SUMMARY, REFERENCE)
to maximize evidence density per token in agent context windows.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Optional


def skeletonize_python(source_code: str) -> str:
    """Generate a Python structural skeleton replacing function bodies with '...'."""
    try:
        tree = ast.parse(source_code)
    except Exception:
        # Fallback to line-based heuristic if AST parse fails
        return _fallback_skeleton(source_code)

    lines = source_code.splitlines()
    out: list[str] = []

    def format_args(args: ast.arguments) -> str:
        # Format arguments with type hints where available
        parts = []
        for a in args.posonlyargs:
            ann = f": {ast.unparse(a.annotation)}" if a.annotation else ""
            parts.append(f"{a.arg}{ann}")
        if args.posonlyargs:
            parts.append("/")
        for a in args.args:
            ann = f": {ast.unparse(a.annotation)}" if a.annotation else ""
            parts.append(f"{a.arg}{ann}")
        if args.vararg:
            ann = f": {ast.unparse(args.vararg.annotation)}" if args.vararg.annotation else ""
            parts.append(f"*{args.vararg.arg}{ann}")
        for a in args.kwonlyargs:
            ann = f": {ast.unparse(a.annotation)}" if a.annotation else ""
            parts.append(f"{a.arg}{ann}")
        if args.kwarg:
            ann = f": {ast.unparse(args.kwarg.annotation)}" if args.kwarg.annotation else ""
            parts.append(f"**{args.kwarg.arg}{ann}")
        return ", ".join(parts)

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases]
            bases_str = f"({', '.join(bases)})" if bases else ""
            out.append(f"class {node.name}{bases_str}:")
            doc = ast.get_docstring(node)
            if doc:
                out.append(f'    """{doc.splitlines()[0]}"""')
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    prefix = "async def" if isinstance(item, ast.AsyncFunctionDef) else "def"
                    ret = f" -> {ast.unparse(item.returns)}" if item.returns else ""
                    args_str = format_args(item.args)
                    out.append(f"    {prefix} {item.name}({args_str}){ret}: ...")
                elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    out.append(f"    {item.target.id}: {ast.unparse(item.annotation)}")
            out.append("")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
            args_str = format_args(node.args)
            doc = ast.get_docstring(node)
            doc_str = f' """{doc.splitlines()[0]}"""' if doc else ' ...'
            out.append(f"{prefix} {node.name}({args_str}){ret}:{doc_str}")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            out.append(ast.unparse(node))

    res = "\n".join(out).strip()
    return res if res else source_code[:500]


def _fallback_skeleton(source: str) -> str:
    """Regex-based multi-language signature skeletonizer."""
    out = []
    for line in source.splitlines():
        trimmed = line.strip()
        if re.match(r"^(pub\s+)?(fn|def|class|interface|type|struct|function|export\s+(const|function|class))\b", trimmed):
            out.append(line.rstrip("{:") + " { ... }")
        elif trimmed.startswith(("#", "//", "/*", "*")):
            if len(out) < 20 and ("@" in trimmed or "TODO" in trimmed or len(trimmed) > 5):
                out.append(line)
    return "\n".join(out) if out else source[:500]


def skeletonize(file_path: Path | str, source_code: Optional[str] = None) -> str:
    """Produce a language-aware skeleton for a file."""
    path = Path(file_path)
    if source_code is None:
        try:
            source_code = path.read_text(errors="replace")
        except Exception:
            return ""

    suffix = path.suffix.lower()
    if suffix == ".py":
        return skeletonize_python(source_code)
    return _fallback_skeleton(source_code)
