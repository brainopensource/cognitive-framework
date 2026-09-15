"""Runway & Task Graph Parser (Requirement 1 & Phase 2).

Parses tasks.md and spec.md into structured graph entities:
Task ID, status (READY, IN_PROGRESS, BLOCKED, ACCEPTED), owner,
predecessors (requires:), exclusive write leases, and falsifiers,
without loading 2,500+ lines into agent LLM context.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

TASK_BLOCK_RE = re.compile(
    r"^[ \t]*- \[(?P<checked>[ xX])\] \*\*(?P<id>[A-Za-z0-9._-]+)(?::\s*(?P<title>[^\n]+?))?\*\*(?P<body>.*?)(?=(?:^[ \t]*- \[[ xX]\]|\Z))",
    re.MULTILINE | re.DOTALL,
)

FIELD_RE = re.compile(r"^[ \t]*- \*\*(?P<key>[A-Za-z0-9_ /-]+)\*\*:\s*(?P<val>[^\n]+)", re.MULTILINE)
TABLE_ROW_RE = re.compile(r"^\|[ \t]*(?:\*\*)?(?P<lane>[A-Z0-9._ /-]+)(?:\*\*)?[ \t]*\|[ \t]*(?P<req>[^|]+)[ \t]*\|[ \t]*(?P<desc>[^|]+)[ \t]*\|", re.MULTILINE)


class RunwayParser:
    """Parser and query engine for tasks.md and execution runway."""

    def __init__(self, repo_root: Path) -> None:
        self.root = Path(repo_root)
        self.tasks_path = self.root / "docs" / "execution" / "main" / "tasks.md"

    def parse_tasks(self) -> List[Dict[str, Any]]:
        if not self.tasks_path.is_file():
            return []
        content = self.tasks_path.read_text(encoding="utf-8", errors="replace")
        tasks: List[Dict[str, Any]] = []
        seen_ids: Set[str] = set()

        for match in TASK_BLOCK_RE.finditer(content):
            t_id = match.group("id").strip()
            if t_id in seen_ids:
                continue
            seen_ids.add(t_id)

            checked = match.group("checked").strip().lower() == "x"
            title = (match.group("title") or "").strip()
            body = match.group("body") or ""

            # Extract fields
            fields: Dict[str, str] = {}
            for f_match in FIELD_RE.finditer(body):
                k = f_match.group("key").strip().lower()
                v = f_match.group("val").strip()
                fields[k] = v

            requires_raw = fields.get("requires", "")
            # extract tokens like T-xxx or [T-xxx]
            requires = re.findall(r"\b[A-Za-z0-9_.-]+\b", requires_raw)
            requires = [r for r in requires if r.startswith("T-") or r.startswith("W")]

            owner = fields.get("owner", "unassigned")
            contract = fields.get("contract", "")
            falsifier = fields.get("falsifier / acceptance", fields.get("falsifier", ""))
            lease = fields.get("lease", "")

            status = "ACCEPTED" if checked else "OPEN"
            if "[PROPOSAL]" in title or "[proposal]" in body:
                status = "PROPOSAL"

            tasks.append({
                "id": t_id,
                "title": title,
                "status": status,
                "checked": checked,
                "owner": owner,
                "requires": requires,
                "contract": contract,
                "lease": lease,
                "falsifier": falsifier,
            })

        # Also scan summary tables in tasks.md for unrepresented tasks (e.g. C: T-133, A: T-131.8)
        for row in TABLE_ROW_RE.finditer(content):
            lane = row.group("lane").strip()
            # Check if lane contains task id like "C: T-133" or "T-131.8"
            t_matches = re.findall(r"\b(T-[0-9]+(?:\.[0-9]+)?|[A-Z][0-9]*)\b", lane)
            for tid in t_matches:
                if tid.startswith("T-") and tid not in seen_ids:
                    seen_ids.add(tid)
                    owner_cand = lane.split(":")[0].strip() if ":" in lane else "unassigned"
                    tasks.append({
                        "id": tid,
                        "title": f"Runway Table task {lane}",
                        "status": "READY" if "ready" in row.group("desc").lower() or "active" in row.group("desc").lower() else "OPEN",
                        "checked": False,
                        "owner": owner_cand,
                        "requires": [r for r in re.findall(r"\bT-[0-9]+(?:\.[0-9]+)?\b", row.group("req"))],
                        "contract": "",
                        "lease": row.group("req").strip(),
                        "falsifier": row.group("desc").strip(),
                    })

        # Compute READY status: if not checked and all dependencies in requires are checked/ACCEPTED
        accepted_ids = {t["id"] for t in tasks if t["checked"] or t["status"] == "ACCEPTED"}
        for t in tasks:
            if t["status"] not in ("ACCEPTED", "PROPOSAL"):
                if not t["requires"] or all(req in accepted_ids for req in t["requires"]):
                    t["status"] = "READY"
                else:
                    t["status"] = "BLOCKED"

        return tasks

    def query(
        self,
        task_id: Optional[str] = None,
        owner: Optional[str] = None,
        ready_only: bool = False,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        all_tasks = self.parse_tasks()
        results: List[Dict[str, Any]] = []
        for t in all_tasks:
            if task_id and t["id"].lower() != task_id.lower():
                continue
            if owner and owner.lower() not in t["owner"].lower():
                continue
            if ready_only and t["status"] != "READY":
                continue
            results.append(t)
            if len(results) >= limit:
                break
        return results
