"""LDA 2.0 Repository Orchestrator Engine.

Integrates repo-status, code-status, doc-status, and tasks into sub-second
and token-bounded one-shot operational reports.
"""
from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .doc_verifier import verify_doc_health
from .gitinfo import get_repo_status
from .runway_parser import RunwayParser
from .test_association import TestAssociationEngine
from .test_runner_bridge import run_test_isolated

logger = logging.getLogger(__name__)


class RepositoryOrchestrator:
    """Active repository nervous system orchestrator for LDA 2.0."""

    def __init__(self, repo_root: Path, storage: Any = None) -> None:
        self.root = Path(repo_root)
        if storage is None:
            from ..atlas import get_storage
            self.storage = get_storage(self.root)
        else:
            self.storage = storage
        self.test_assoc = TestAssociationEngine(self.storage)
        self.runway = RunwayParser(self.root)

    def repo_status(self) -> Dict[str, Any]:
        """Fast C-git status, HEAD SHA, branch, dirty diffstat (<25ms)."""
        return get_repo_status(self.root)

    def doc_status(self, sample_limit: int = 200) -> Dict[str, Any]:
        """Living documentation verification (<300ms)."""
        return verify_doc_health(self.root, sample_limit=sample_limit)

    def tasks(
        self,
        task_id: Optional[str] = None,
        owner: Optional[str] = None,
        ready_only: bool = False,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Query runway tasks without loading full 2,500-line markdown into LLM context."""
        return self.runway.query(task_id=task_id, owner=owner, ready_only=ready_only, limit=limit)

    def code_status(
        self,
        task_id: Optional[str] = None,
        target_files: Optional[Sequence[str]] = None,
        run_linters: bool = True,
        max_tests: int = 3,
        timeout: float = 15.0,
    ) -> Dict[str, Any]:
        """Runs falsifiers for touched/target files via test-runner skill, plus linters (<2s)."""
        start_time = time.time()
        files_to_check: List[str] = []
        if target_files:
            files_to_check.extend(target_files)
        elif task_id:
            # Query runway for task lease/files
            matching = self.runway.query(task_id=task_id)
            if matching and matching[0].get("lease"):
                lease_text = matching[0]["lease"]
                import re
                candidates = re.findall(r"[\w./-]+\.(?:py|ts|tsx|md|json)", lease_text)
                files_to_check.extend(candidates)
        
        if not files_to_check:
            # Default to dirty files from git
            git_info = self.repo_status()
            files_to_check.extend(git_info.get("dirty_files", []))

        # 1. Boundary & TCB Linters
        linters_result: Dict[str, Any] = {
            "hexagonal_boundaries": "SKIPPED",
            "tcb_budget": {"status": "SKIPPED"},
        }
        if run_linters:
            b_proc = subprocess.run(
                ["python3", "tools/linters/check_boundaries.py"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
            )
            linters_result["hexagonal_boundaries"] = "PASS" if b_proc.returncode == 0 else "FAIL"
            if b_proc.returncode != 0:
                linters_result["boundary_details"] = b_proc.stderr or b_proc.stdout

            tcb_proc = subprocess.run(
                ["python3", "tools/linters/check_tcb_budget.py"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
            )
            linters_result["tcb_budget"]["status"] = "PASS" if tcb_proc.returncode == 0 else "FAIL"
            if tcb_proc.stdout.strip():
                try:
                    for line in tcb_proc.stdout.splitlines():
                        if line.startswith("{") and "current_logical_loc" in line:
                            data = json.loads(line)
                            linters_result["tcb_budget"]["current"] = data.get("current_logical_loc")
                            linters_result["tcb_budget"]["ceiling"] = data.get("threshold", 1438)
                            break
                except Exception:
                    pass

        # 2. Associated Tests
        associated = self.test_assoc.find_associated_tests(files_to_check)
        suggested_cmds = associated.get("suggested_commands", [])
        executed_falsifiers: Dict[str, Any] = {}

        for cmd in suggested_cmds[:max_tests]:
            test_res = run_test_isolated(cmd, timeout=timeout, cwd=self.root)
            test_name = cmd.replace("python3 -m unittest ", "").replace(" -v", "")
            status_str = "PASS" if test_res["success"] else "FAIL"
            executed_falsifiers[test_name] = {
                "command": cmd,
                "status": status_str,
                "exit_code": test_res["exit_code"],
                "duration": test_res["duration_seconds"],
                "failures_count": test_res.get("failures_count", 0) or 0,
                "summary": test_res.get("summary", ""),
            }
            if not test_res["success"] and test_res.get("failures"):
                executed_falsifiers[test_name]["failures"] = test_res["failures"][:3]

        duration = time.time() - start_time
        overall_status = "PASS"
        if linters_result["hexagonal_boundaries"] == "FAIL" or linters_result["tcb_budget"]["status"] == "FAIL":
            overall_status = "FAIL"
        if any(f["status"] == "FAIL" for f in executed_falsifiers.values()):
            overall_status = "FAIL"

        return {
            "status": overall_status,
            "duration_seconds": round(duration, 3),
            "checked_files": files_to_check,
            "linters": linters_result,
            "associated_test_files": associated.get("associated_test_files", [])[:5],
            "falsifiers": executed_falsifiers,
        }

    def sweep(self, budget: int = 4000) -> Dict[str, Any]:
        """Master one-shot sweep combining repo-status, code-status, and doc-status (<2.5s)."""
        start_time = time.time()
        repo = self.repo_status()
        doc = self.doc_status()
        code = self.code_status(target_files=repo.get("dirty_files", []), max_tests=2, timeout=10.0)

        # Active tasks/leases
        ready_tasks = self.tasks(ready_only=True, limit=5)

        total_duration = time.time() - start_time
        return {
            "orchestrator_version": "2.0.0",
            "execution_time_seconds": round(total_duration, 3),
            "repository": {
                "branch": repo.get("branch"),
                "head_sha": repo.get("head_sha"),
                "dirty_files_count": repo.get("dirty_files_count", 0),
                "dirty_summary": repo.get("dirty_summary", []),
                "untracked_files": repo.get("untracked_files", [])[:5],
            },
            "recent_activity": {
                "latest_commits": repo.get("latest_commits", []),
                "ready_tasks": [
                    {"id": t["id"], "owner": t["owner"], "title": t["title"], "lease": t.get("lease", "")}
                    for t in ready_tasks
                ],
            },
            "gates_and_verification": {
                "hexagonal_boundaries": code["linters"]["hexagonal_boundaries"],
                "tcb_budget": code["linters"]["tcb_budget"],
                "target_falsifiers": code.get("falsifiers", {}),
            },
            "documentation_health": {
                "stale_paths": doc.get("stale_paths_count", 0),
                "frontmatter_violations": doc.get("frontmatter_violations_count", 0),
                "broken_links": doc.get("broken_links_count", 0),
                "symbol_implementations": doc.get("symbol_implementations_count", 0),
            },
        }
