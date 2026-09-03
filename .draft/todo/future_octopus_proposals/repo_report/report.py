"""Small dependency-free deterministic repository report compiler.

This module deliberately delegates indexing and ranking to LDA. It only adds
the missing report projection: snapshot, inventory, contracts, graph summary,
freshness, incremental state and a compact Markdown view.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from ...atlas import get_storage, index_repository
from ...core.config import AtlasContext
from ...providers.filesystem import FilesystemProvider

VERSION = "0.1.0"
DEFAULT_EXCLUDES = {".git", ".venv", "node_modules", "__pycache__", ".lda", ".generated", "site", "dist", "build"}


def _git(root: Path, *args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True)
    except OSError:
        return 127, ""
    return proc.returncode, proc.stdout.strip()


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _lines(path: Path) -> int:
    try:
        with path.open("rb") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def _inventory(root: Path, ctx: AtlasContext) -> tuple[list[dict[str, Any]], int]:
    """Use LDA's existing filesystem provider; fallback is intentionally tiny."""
    try:
        result = FilesystemProvider().collect(ctx)
        rows = list(result.metadata.get("discovered_files", []))
        if rows:
            for row in rows:
                row.setdefault("lines", _lines(root / str(row["path"])))
            return rows, len(rows)
    except Exception:
        pass
    rows: list[dict[str, Any]] = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDES and not d.startswith(".")]
        for name in files:
            path = Path(base) / name
            rel = path.relative_to(root).as_posix()
            try:
                stat = path.stat()
                rows.append({"path": rel, "size_bytes": stat.st_size, "mtime": stat.st_mtime, "content_hash": _sha(path), "language": path.suffix.lower().lstrip(".") or "unknown"})
            except OSError:
                continue
    return rows, len(rows)


def _contracts(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidates = set()
    for base in ("schemas", "schema", "contracts", "vanguard", "packs"):
        folder = root / base
        if folder.exists():
            candidates.update(p for p in folder.rglob("*") if p.is_file())
    candidates.update(root.glob("*.json"))
    candidates.update(root.glob("*.toml"))
    for path in sorted(candidates):
        if path.name.startswith(".") or any(x in DEFAULT_EXCLUDES for x in path.parts):
            continue
        suffix = path.suffix.lower()
        if suffix not in {".json", ".jsonl", ".yaml", ".yml", ".toml", ".proto"}:
            continue
        rel = path.relative_to(root).as_posix()
        row: dict[str, Any] = {"path": rel, "format": suffix[1:], "bytes": path.stat().st_size}
        if suffix == ".json":
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(value, dict):
                    row["keys"] = sorted(str(k) for k in value.keys())[:40]
                    row["api"] = value.get("api") or value.get("$schema")
            except (OSError, json.JSONDecodeError):
                row["parse"] = "invalid_or_binary"
        rows.append(row)
    return rows


def _graph(root: Path) -> dict[str, Any]:
    db = root / ".lda" / "index.db"
    if not db.exists():
        return {"status": "NO_INDEX", "entities": 0, "relations": 0, "by_kind": {}, "by_relation": {}}
    try:
        storage = get_storage(root)
        stats = storage.get_stats()
        topo = storage.get_topology_map()
        return {
            "status": "READY",
            "entities": stats.get("entities", 0),
            "relations": stats.get("relations", 0),
            "symbols": stats.get("symbols", 0),
            "documents": stats.get("documents", 0),
            "by_kind": {str(r["kind"]): int(r["count"]) for r in topo.get("entities", [])},
            "by_relation": {str(r["kind"]): int(r["count"]) for r in topo.get("relations", [])},
        }
    except Exception as exc:
        return {"status": "INVALID", "reason": str(exc), "entities": 0, "relations": 0, "by_kind": {}, "by_relation": {}}


def _freshness(root: Path, ctx: AtlasContext, inventory: list[dict[str, Any]]) -> dict[str, Any]:
    code, head = _git(root, "rev-parse", "HEAD")
    current = head if code == 0 else None
    report = root / ".generated" / "knowledge" / "report.json"
    knowledge_status = None
    if report.exists():
        try:
            knowledge_status = json.loads(report.read_text(encoding="utf-8")).get("status")
        except (OSError, json.JSONDecodeError):
            knowledge_status = "INVALID"
    if ctx.head_sha and current and ctx.head_sha != current:
        return {"status": "STALE", "reason": "Atlas context HEAD differs from current HEAD", "context_head": ctx.head_sha, "current_head": current, "knowledge_status": knowledge_status}
    return {"status": "FRESH", "reason": "snapshot and Atlas context use the current HEAD", "context_head": ctx.head_sha or current, "current_head": current, "knowledge_status": knowledge_status, "files_observed": len(inventory)}


def _metrics(inventory: list[dict[str, Any]], contracts: list[dict[str, Any]], graph: dict[str, Any]) -> dict[str, Any]:
    suffixes = Counter(Path(str(r.get("path", ""))).suffix.lower() or "[none]" for r in inventory)
    code_ext = {".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".java", ".c", ".cpp", ".h", ".hpp", ".sh"}
    docs = sum(Path(str(r.get("path", ""))).suffix.lower() in {".md", ".rst", ".adoc"} for r in inventory)
    code = sum(Path(str(r.get("path", ""))).suffix.lower() in code_ext for r in inventory)
    bytes_total = sum(int(r.get("size_bytes", 0) or 0) for r in inventory)
    return {
        "files": len(inventory),
        "code_files": code,
        "document_files": docs,
        "bytes": bytes_total,
        "estimated_lines": sum(_safe_int(r.get("lines")) for r in inventory),
        "contracts": len(contracts),
        "symbols": int(graph.get("symbols", 0)),
        "relations": int(graph.get("relations", 0)),
        "languages_or_suffixes": len(suffixes),
    }


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _incremental(root: Path, inventory: list[dict[str, Any]], version: str) -> dict[str, Any]:
    state_path = root / ".lda" / "repo-report" / "state.json"
    previous: dict[str, Any] = {}
    if state_path.exists():
        try:
            previous = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
    old = previous.get("files", {})
    current = {str(row["path"]): str(row.get("content_hash", "")) for row in inventory}
    changed = [path for path, digest in current.items() if old.get(path) != digest]
    deleted = sorted(set(old) - set(current))
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"version": version, "head": _git(root, "rev-parse", "HEAD")[1], "files": current}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"changed_files": len(changed), "deleted_files": len(deleted), "unchanged_files": max(0, len(current) - len(changed)), "state": str(state_path.relative_to(root))}


def _markdown(data: dict[str, Any]) -> str:
    m = data["metrics"]
    f = data["freshness"]
    g = data["graph"]
    lines = [
        "# Deterministic Repository Report", "", f"- Generated by: `LDA repo_report {VERSION}`", f"- HEAD: `{data['snapshot'].get('head') or 'unknown'}`", f"- Root: `{data['snapshot']['root']}`", f"- Freshness: **{f['status']}** — {f['reason']}", "", "## Metrics", "", "| Metric | Value |", "|---|---:|",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in m.items())
    lines += ["", "## Graph", "", f"- Status: `{g.get('status')}`", f"- Entities: `{g.get('entities', 0)}`", f"- Relations: `{g.get('relations', 0)}`", f"- Symbols: `{g.get('symbols', 0)}`", "", "### Entity kinds", ""]
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(g.get("by_kind", {}).items()))
    lines += ["", "### Relation kinds", ""]
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(g.get("by_relation", {}).items()))
    lines += ["", "## Contracts", ""]
    lines.extend(f"- `{row['path']}` ({row['format']}, {row['bytes']} bytes)" for row in data["contracts"][:200])
    if not data["contracts"]:
        lines.append("- None discovered by the deterministic contract scan.")
    lines += ["", "## Incremental delta", "", f"- Changed: `{data['incremental']['changed_files']}`", f"- Deleted: `{data['incremental']['deleted_files']}`", f"- Unchanged: `{data['incremental']['unchanged_files']}`", "", "## Authority", "", "This report is a rebuildable projection. LDA routing, canonical documentation, source, tests and the ledger remain authoritative.", ""]
    return "\n".join(lines)


def generate_report(root: Path | str, output_dir: Path | str | None = None, refresh_index: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    ctx = AtlasContext.discover(root)
    if refresh_index:
        index_repository(root, incremental=True)
    inventory, _ = _inventory(root, ctx)
    contracts = _contracts(root)
    graph = _graph(root)
    freshness = _freshness(root, ctx, inventory)
    data: dict[str, Any] = {
        "schema": "lda.repo-report/1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "snapshot": {"root": str(root), "head": _git(root, "rev-parse", "HEAD")[1], "branch": _git(root, "branch", "--show-current")[1], "dirty": bool(_git(root, "status", "--porcelain")[1])},
        "freshness": freshness,
        "metrics": _metrics(inventory, contracts, graph),
        "incremental": _incremental(root, inventory, VERSION),
        "graph": graph,
        "contracts": contracts,
        "artifacts": [],
    }
    out = Path(output_dir) if output_dir else root / ".lda" / "repo-report"
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "report.json"
    md_path = out / "report.md"
    data["artifacts"] = [str(json_path), str(md_path)]
    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(data), encoding="utf-8")
    return data


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate an incremental deterministic repository report using LDA")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--refresh-index", action="store_true", help="Ask LDA to incrementally refresh its existing fact graph")
    parser.add_argument("--json", action="store_true", help="Print the generated report metadata as JSON")
    args = parser.parse_args(list(argv) if argv is not None else None)
    data = generate_report(args.root, args.output, args.refresh_index)
    print(json.dumps(data, indent=2, sort_keys=True) if args.json else "\n".join(data["artifacts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
