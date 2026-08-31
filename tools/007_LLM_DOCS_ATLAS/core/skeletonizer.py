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


def skeletonize_tsjs(source_code: str) -> str:
    """Generate a TypeScript/JavaScript structural skeleton."""
    lines = source_code.splitlines()
    out: list[str] = []
    in_comment = False
    brace_depth = 0
    class_depth = -1
    interface_depth = -1

    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            continue

        if trimmed.startswith("/*"):
            if "*/" not in trimmed:
                in_comment = True
            continue
        if in_comment:
            if "*/" in trimmed:
                in_comment = False
            continue
        if trimmed.startswith("//"):
            continue

        open_braces = trimmed.count("{")
        close_braces = trimmed.count("}")

        if trimmed.startswith("import ") or trimmed.startswith("require(") or (trimmed.startswith("export ") and " from " in trimmed):
            out.append(trimmed)
            continue

        if re.match(r"^(?:export\s+)?(?:default\s+)?(?:declare\s+)?(?:type|enum)\s+", trimmed):
            out.append(trimmed)
            if "{" in trimmed and "}" not in trimmed:
                brace_depth += open_braces - close_braces
            continue

        if re.match(r"^(?:export\s+)?(?:default\s+)?(?:declare\s+)?interface\s+", trimmed):
            out.append(trimmed.split("{")[0].strip() + " {")
            interface_depth = brace_depth
            brace_depth += open_braces - close_braces
            continue

        if re.match(r"^(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+", trimmed):
            out.append(trimmed.split("{")[0].strip() + " {")
            class_depth = brace_depth
            brace_depth += open_braces - close_braces
            continue

        if class_depth >= 0 or interface_depth >= 0:
            if brace_depth == class_depth + 1 or brace_depth == interface_depth + 1:
                if re.match(r"^(?:public|private|protected|static|readonly|async|get|set|\*)\s+", trimmed) or re.match(r"^[a-zA-Z_$][\w$]*\s*(?:\([^)]*\)|:)", trimmed):
                    sig = trimmed.split("{")[0].rstrip().rstrip(";")
                    if not sig.endswith(";"):
                        sig += ";"
                    out.append("    " + sig)
            
            brace_depth += open_braces - close_braces
            if class_depth >= 0 and brace_depth <= class_depth:
                out.append("}")
                class_depth = -1
            elif interface_depth >= 0 and brace_depth <= interface_depth:
                out.append("}")
                interface_depth = -1
            continue

        if re.match(r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+", trimmed):
            sig = trimmed.split("{")[0].rstrip()
            out.append(sig + " { ... }")
            brace_depth += open_braces - close_braces
            continue

        if re.match(r"^(?:export\s+)?(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*(?::\s*[^=]+)?\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)(?::\s*[^=]+)?\s*=>", trimmed):
            sig = re.split(r"=>", trimmed)[0].rstrip() + " => { ... };"
            out.append(sig)
            brace_depth += open_braces - close_braces
            continue

        if re.match(r"^(?:export\s+)?(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*:", trimmed):
            out.append(trimmed.rstrip(";").split("=")[0].rstrip() + ";")
            continue

        brace_depth += open_braces - close_braces

    return "\n".join(out).strip() if out else source_code[:500]


def skeletonize_rust(source_code: str) -> str:
    """Generate a Rust structural skeleton preserving public interfaces and signatures."""
    lines = source_code.splitlines()
    out: list[str] = []
    in_impl_or_trait = False

    for line in lines:
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("//"):
            continue

        if re.match(r"^(?:pub\s+)?(?:use|mod|extern)\s+", trimmed):
            out.append(trimmed)
            continue

        if re.match(r"^(?:pub(?:\([^)]+\))?\s+)?(?:struct|enum|type|const|static)\s+", trimmed):
            out.append(trimmed)
            continue

        if re.match(r"^(?:pub(?:\([^)]+\))?\s+)?(?:unsafe\s+)?trait\s+", trimmed):
            out.append(trimmed.split("{")[0].strip() + " {")
            in_impl_or_trait = True
            continue

        if re.match(r"^impl\s+", trimmed):
            out.append(trimmed.split("{")[0].strip() + " {")
            in_impl_or_trait = True
            continue

        if re.match(r"^(?:pub(?:\([^)]+\))?\s+)?(?:async\s+)?(?:unsafe\s+)?(?:extern\s+)?fn\s+", trimmed):
            sig = trimmed.split("{")[0].rstrip().rstrip(";")
            indent = "    " if in_impl_or_trait else ""
            if in_impl_or_trait and ";" in trimmed:
                out.append(indent + sig + ";")
            else:
                out.append(indent + sig + " { ... }")
            continue

        if trimmed == "}":
            out.append("}")
            in_impl_or_trait = False

    return "\n".join(out).strip() if out else source_code[:500]


def skeletonize_go(source_code: str) -> str:
    """Generate a Go structural skeleton preserving packages, types, and function signatures."""
    lines = source_code.splitlines()
    out: list[str] = []
    in_import = False

    for line in lines:
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("//"):
            continue

        if trimmed.startswith("package "):
            out.append(trimmed)
            continue

        if trimmed == "import (":
            in_import = True
            out.append(trimmed)
            continue

        if in_import:
            out.append("    " + trimmed)
            if trimmed == ")":
                in_import = False
            continue

        if trimmed.startswith("import "):
            out.append(trimmed)
            continue

        if re.match(r"^type\s+[A-Za-z0-9_]+\s+(?:struct|interface)\s*\{?", trimmed):
            out.append(trimmed)
            continue

        if re.match(r"^type\s+[A-Za-z0-9_]+\s+=", trimmed) or re.match(r"^type\s+[A-Za-z0-9_]+\s+[a-zA-Z]", trimmed):
            out.append(trimmed)
            continue

        if re.match(r"^(?:const|var)\s+", trimmed):
            out.append(trimmed)
            continue

        if re.match(r"^func\s+", trimmed):
            sig = trimmed.split("{")[0].rstrip()
            out.append(sig + " { ... }")
            continue

        if trimmed == "}":
            out.append("}")

    return "\n".join(out).strip() if out else source_code[:500]


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
    if suffix in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts"):
        return skeletonize_tsjs(source_code)
    if suffix == ".rs":
        return skeletonize_rust(source_code)
    if suffix == ".go":
        return skeletonize_go(source_code)
    return _fallback_skeleton(source_code)
