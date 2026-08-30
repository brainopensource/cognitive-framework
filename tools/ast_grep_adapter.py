#!/usr/bin/env python3
"""ast-grep evidence adapter for AETHER Code Intelligence.

Executes read-only structural AST queries against vanguard/packages, validates matches,
and enriches the deterministic .generated/knowledge/code-map.jsonl IR.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / ".generated" / "knowledge"


def extract_ast_evidence() -> list[dict[str, str]]:
    """Runs ast-grep queries to discover structural AST relations."""
    evidence: list[dict[str, str]] = []
    
    # Query 1: Find dispatch calls in kernel/agency
    try:
        res = subprocess.run(
            ["npx", "ast-grep", "run", "--pattern", "dispatch($$$)", "vanguard/packages", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            matches = json.loads(res.stdout)
            for m in matches[:10]:
                file_path = m.get("file", "").replace("\\", "/")
                evidence.append({
                    "subsystem": "AST-Grep structural call: dispatch",
                    "package_path": file_path,
                    "canonical_owner": "docs/backend/architecture/microkernel.md",
                    "evidence_type": "ast_match",
                })
    except Exception as e:
        print(f"ast-grep execution note: {e}")
        
    return evidence


def enrich_code_map() -> int:
    code_map_file = KNOWLEDGE_DIR / "code-map.jsonl"
    if not code_map_file.exists():
        return 0

    existing_rows: list[dict[str, str]] = []
    with open(code_map_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                existing_rows.append(json.loads(line))

    evidence_rows = extract_ast_evidence()
    seen_paths = {row.get("package_path") for row in existing_rows}
    
    added = 0
    for ev in evidence_rows:
        if ev["package_path"] not in seen_paths:
            existing_rows.append(ev)
            seen_paths.add(ev["package_path"])
            added += 1

    with open(code_map_file, "w", encoding="utf-8") as f:
        for row in existing_rows:
            f.write(json.dumps(row) + "\n")

    return added


if __name__ == "__main__":
    count = enrich_code_map()
    print(f"AST-GREP ENRICHMENT PASS: Merged {count} structural AST evidence rows into code-map.jsonl")
