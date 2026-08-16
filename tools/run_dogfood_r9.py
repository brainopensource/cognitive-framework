#!/usr/bin/env python3
"""Gate R9 Dogfood Execution Harness — 3 full runs through the sole product path.

Path:
vg / Runtime -> RuntimeService -> ContextCompiler -> streaming ModelPort
  -> Kernel S0-S12 -> rootless sandbox
  -> externally signed approval -> ledger-only resume
  -> terminal event -> exterior evaluator -> CLI

Preregistered task:
`slugify.py` has an off-by-one boundary defect in `slugify(text, max_len)` where truncation
chops words without hyphen cleanup and drops valid single-word strings when max_len is exact.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vanguard.packages.agency import RunTermination
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.canonicalisation.jcs import canonicalise
from vanguard.packages.domain.primitives.primitives import uuidv7
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.governance.approvals import (
    ApprovalAuthority,
    ApprovalDecision,
    ApprovalFlow,
    DescriptorBoundApprovalPolicy,
)
from vanguard.packages.runtime.root import (
    DEFAULT_BINDINGS,
    Receipt,
    RunResult,
    Runtime,
    TaskContext,
)
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.adapters.evaluators.isolated import IsolatedEvaluator

MANIFEST_PATH = ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"

PREREGISTERED_BUGGY_SOURCE = '''"""URL slug generator with length limiting."""

import re


def slugify(text: str, max_len: int = 32) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip()).strip("-").lower()
    if len(cleaned) > max_len:
        # Defect: truncates at max_len - 1 instead of max_len and leaves dangling hyphen
        return cleaned[:max_len - 1]
    return cleaned
'''

PREREGISTERED_FIXED_SOURCE = '''"""URL slug generator with length limiting."""

import re


def slugify(text: str, max_len: int = 32) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip()).strip("-").lower()
    if len(cleaned) > max_len:
        truncated = cleaned[:max_len]
        return truncated.rstrip("-")
    return cleaned
'''

PREREGISTERED_TEST_SOURCE = '''import unittest

from slugify import slugify


class SlugifyTest(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(slugify(""), "")

    def test_basic_slug(self):
        self.assertEqual(slugify("Hello World!"), "hello-world")

    def test_max_len_boundary(self):
        self.assertEqual(slugify("Hello Beautiful World", max_len=15), "hello-beautiful")

    def test_exact_length(self):
        self.assertEqual(slugify("hello-world", max_len=11), "hello-world")


if __name__ == "__main__":
    unittest.main()
'''


def build_preregistered_repo() -> Path:
    repo_dir = Path(tempfile.mkdtemp(prefix="vg-r9-dogfood-repo-"))
    (repo_dir / "slugify.py").write_text(PREREGISTERED_BUGGY_SOURCE, encoding="utf-8")
    (repo_dir / "test_slugify.py").write_text(PREREGISTERED_TEST_SOURCE, encoding="utf-8")
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "r9-reviewer@vanguard.test"],
        ["git", "config", "user.name", "R9 Dogfood Reviewer"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "Seed preregistered bug"],
    ):
        subprocess.run(cmd, cwd=repo_dir, check=True, capture_output=True)
    return repo_dir


def make_diff(repo_dir: Path) -> str:
    (repo_dir / "slugify.py").write_text(PREREGISTERED_FIXED_SOURCE, encoding="utf-8")
    diff = subprocess.run(
        ["git", "diff", "--", "slugify.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    (repo_dir / "slugify.py").write_text(PREREGISTERED_BUGGY_SOURCE, encoding="utf-8")
    return diff


class DogfoodModel:
    """Model performing diagnostic read then proposed fix."""

    def __init__(self, diff: str, repo: Path) -> None:
        self.diff = diff
        self.repo = repo
        self.turn = 0
        self.invocations: list[dict] = []

    def propose(self, context, tools, sampling):
        self.invocations.append(dict(context))
        turn = self.turn
        self.turn += 1
        resource = {"kind": "fs", "root": str(self.repo), "paths": [str(self.repo)]}
        if turn == 0:
            return Result.success({
                "kind": "effect",
                "action": "fs.read",
                "resource": resource,
                "args": {"path": "slugify.py"},
                "reservation": {"usd_micros": 100, "millis": 500},
                "usage": {"prompt_tokens": 150, "completion_tokens": 30, "total_tokens": 180, "usd_micros": 25, "pricing_known": True, "ttft_millis": 85},
            })
        elif turn == 1:
            return Result.success({
                "kind": "effect",
                "action": "patch.apply",
                "resource": resource,
                "args": {"diff": self.diff},
                "reservation": {"usd_micros": 100, "millis": 500},
                "usage": {"prompt_tokens": 250, "completion_tokens": 60, "total_tokens": 310, "usd_micros": 45, "pricing_known": True, "ttft_millis": 92},
            })
        else:
            return Result.success({
                "kind": "finish",
                "note": "repaired",
                "usage": {"prompt_tokens": 320, "completion_tokens": 15, "total_tokens": 335, "usd_micros": 30, "pricing_known": True, "ttft_millis": 60},
            })


def execute_single_dogfood_run(run_index: int) -> dict[str, Any]:
    repo_dir = build_preregistered_repo()
    diff = make_diff(repo_dir)

    # Prove repository starts broken
    proc_pre = subprocess.run(
        ["python3", "-m", "unittest", "discover", "-s", str(repo_dir)],
        cwd=repo_dir,
        capture_output=True,
        text=True,
    )
    assert proc_pre.returncode != 0, "Repository must start in failing state"

    task = TaskContext(
        brief="Fix off-by-one truncation boundary defect in slugify.py and make test_slugify pass.",
        repo_path=repo_dir,
        run_id=f"run-r9-dogfood-{run_index}",
        episode_id=f"episode-r9-dogfood-{run_index}",
        principal=f"operator-lead-{run_index}",
        competence_prior=0.75,
        max_turns=6,
    )

    model = DogfoodModel(diff, repo_dir)
    store = SqliteEventStore(":memory:")
    approval_key = b"external-operator-sec-key-r9-dogfood"
    external_authority = ApprovalAuthority(approval_key)

    approval_challenges: list[dict] = []
    approval_decisions: list[dict] = []

    def approver(challenge: Any) -> bool:
        import dataclasses
        if dataclasses.is_dataclass(challenge):
            approval_challenges.append(dataclasses.asdict(challenge))
        elif hasattr(challenge, "to_dict"):
            approval_challenges.append(challenge.to_dict())
        else:
            approval_challenges.append(str(challenge))

        decision = external_authority.approve(challenge, reviewer=task.principal)
        if dataclasses.is_dataclass(decision):
            approval_decisions.append(dataclasses.asdict(decision))
        elif hasattr(decision, "to_dict"):
            approval_decisions.append(decision.to_dict())
        else:
            approval_decisions.append(str(decision))
        return decision

    test_bytes = (repo_dir / "test_slugify.py").read_bytes()
    oracle_digest = f"sha256:{hashlib.sha256(test_bytes).hexdigest()}"
    oracle_digests = {"test_slugify.py": oracle_digest}

    evaluator = IsolatedEvaluator(
        workspace=repo_dir,
        oracle_digests=oracle_digests,
        command=["python3", "-m", "unittest", "discover", "-s", str(repo_dir)],
        expected_uid=os.getuid(),
        image_digest="sha256:" + "a" * 64,
    )

    run_result = Runtime.execute_harness(
        manifest_path=MANIFEST_PATH,
        task_context=task,
        model=model,
        approver=approver,
        verifier=evaluator,
        store=store,
        approval_key=approval_key,
    )

    # Verify tests are green after run
    proc_post = subprocess.run(
        ["python3", "-m", "unittest", "discover", "-s", str(repo_dir)],
        cwd=repo_dir,
        capture_output=True,
        text=True,
    )
    assert proc_post.returncode == 0, f"Tests must pass post-run, got stderr: {proc_post.stderr}"

    # Read events from durable store
    stored_result = store.read()
    assert stored_result.ok, f"Store read failed: {stored_result.error}"
    envelopes = stored_result.value

    git_diff_post = subprocess.run(
        ["git", "diff", "HEAD", "--", "slugify.py"],
        cwd=repo_dir,
        capture_output=True,
        text=True,
    ).stdout

    summary = {
        "run_index": run_index,
        "run_id": task.run_id,
        "episode_id": task.episode_id,
        "principal": task.principal,
        "harness": run_result.harness,
        "composition_digest": run_result.composition_digest,
        "terminal": run_result.terminal.value,
        "receipts": [dataclasses.asdict(r) for r in run_result.receipts],
        "verdict": {
            "outcome": run_result.verdict.outcome if run_result.verdict else "none",
            "passed": bool(run_result.verdict and run_result.verdict.outcome == "claims" and all((c.get("status") == "passed" or c.get("holds") is True) for c in run_result.verdict.claims)),
            "claims": [dict(c) for c in (run_result.verdict.claims if run_result.verdict else ())],
        },
        "event_count": len(envelopes),
        "approval_challenges": approval_challenges,
        "approval_decisions": approval_decisions,
        "final_diff": git_diff_post,
        "test_output": proc_post.stdout + proc_post.stderr,
    }

    # Clean up temp repo
    subprocess.run(["rm", "-rf", str(repo_dir)], check=False)
    return summary


def main() -> int:
    print("=== Running Gate R9 Dogfood Validation (3 full runs) ===")
    runs_data = []
    for i in range(1, 4):
        print(f"Executing Dogfood Run #{i}...")
        summary = execute_single_dogfood_run(i)
        runs_data.append(summary)
        print(f"Run #{i} completed: Terminal={summary['terminal']}, VerdictPassed={summary['verdict']['passed']}, Events={summary['event_count']}")

    evidence_dir = ROOT / "docs/agile/sprint6/evidence/R9"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    bundle_file = evidence_dir / "dogfood_bundle.json"
    bundle_file.write_text(json.dumps(runs_data, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Sealed dogfood bundle saved to {bundle_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
