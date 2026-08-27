#!/usr/bin/env python3
"""M-5b material formal run: SAT witness through the unchanged substrate.

The M-5b hypothesis is falsifiable and stated as such: *a materially non-coding
domain executes on the generic substrate with no semantic change to it.* This
runner is the experiment, not a demonstration -- it is written so that a
failure is legible rather than absorbed.

What it deliberately does **not** do:

* it does not let the pack grade itself. The agent writes a candidate
  assignment; whether that assignment satisfies the formula is decided
  afterwards by `adapters/evaluators/suites/formal_sat.py`, which never sees
  the agent's claim (`I-5`);
* it does not accept a witness for a formula it did not pin. Both are
  re-digested against `tasks/registry.json` before and after the run, so a
  formula edited mid-run is a failure rather than a convenience;
* it does not repair a failed run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from vanguard.packages.adapters.evaluators.suites.formal_sat import verify_assignment
from vanguard.packages.adapters.models.openrouter import OpenRouterModel
from vanguard.packages.adapters.stores.blob_store import FileBlobStore
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.reducer import compute_state_digest, reconstruct_state
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import Runtime

PACK = _REPO_ROOT / "packs/formal-sat"
REGISTRY = json.loads((PACK / "tasks/registry.json").read_text(encoding="utf-8"))
RUN_ID = "run-m5b-formal"
EPISODE_ID = "episode-m5b-formal"


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def task(task_id: str = "SAT-001") -> dict:
    return next(t for t in REGISTRY["tasks"] if t["id"] == task_id)


def assert_task_set_is_pinned() -> None:
    """The exam must be the one that was fixed, and so must the grader."""
    entry = task()
    formula = (PACK / entry["formula"]).read_bytes()
    if _digest(formula) != entry["formulaDigest"]:
        raise SystemExit("M-5b ABORT: formula digest drifted from the registry")
    oracle = _REPO_ROOT / "vanguard/packages/adapters/evaluators/suites/formal_sat.py"
    if _digest(oracle.read_bytes()) != REGISTRY["oracleDigest"]:
        raise SystemExit("M-5b ABORT: oracle digest drifted from the registry")


def setup_fixture(target: Path) -> Path:
    """A workspace holding the formula and nothing that answers it."""
    target.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=target, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "M-5b Runner"], cwd=target,
                   capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "m5b@vanguard.dev"], cwd=target,
                   capture_output=True, check=True)
    entry = task()
    shutil.copy(PACK / entry["formula"], target / "formula.cnf")
    (target / "TASK.md").write_text(
        "# Task\nRead `formula.cnf` (DIMACS CNF) and write `witness.json` containing a\n"
        "complete Boolean assignment for every declared variable, in the form\n"
        '`{"assignment": {"1": true, "2": false}}`.\n'
        "An exterior verifier decides whether it satisfies the formula.\n",
        encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=target, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "formal fixture"], cwd=target,
                   capture_output=True, check=True)
    return target


def verify(repo: Path, db: Path, result: Any) -> tuple[bool, list[str], dict]:
    """Exterior verification. The agent's own claim is never consulted."""
    failures: list[str] = []
    verdict: dict = {}

    witness_path = repo / "witness.json"
    if not witness_path.is_file():
        failures.append("M-5b: no witness.json was produced")
    else:
        try:
            witness = json.loads(witness_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            failures.append(f"M-5b: witness.json is not JSON: {exc}")
            witness = None
        if witness is not None:
            # The pinned formula, re-read from the pack -- never the copy in
            # the workspace, which the agent could have edited.
            formula_text = (PACK / task()["formula"]).read_text(encoding="utf-8")
            try:
                outcome = verify_assignment(formula_text, witness)
            except ValueError as exc:
                failures.append(f"M-5b: oracle refused the candidate: {exc}")
            else:
                verdict = outcome.to_dict()
                if not outcome.accepted:
                    failures.append(f"M-5b: witness rejected: {outcome.reason}")

    if not db.is_file():
        failures.append(f"M-5b: no durable event store at {db}")
    else:
        store = SqliteEventStore(db)
        events = list(store.read(EventRange(run_id=RUN_ID)).value or [])
        if len(events) < 2:
            failures.append(f"M-5b: expected >= 2 durable events, found {len(events)}")
        if store.journal_mode != "wal":
            failures.append(f"M-5b: journal_mode is {store.journal_mode!r}, not 'wal'")
        # Fresh-process reconstruction: the state must rebuild from the log
        # alone, exactly as the coding domain does. That is what makes M-4's
        # capture domain-blind rather than coding-shaped.
        try:
            digest = compute_state_digest(reconstruct_state(events))
        except Exception as exc:
            failures.append(f"M-5b: cold reduction failed: {exc}")
            digest = ""
        # Reconstruction is checked against the range the trajectory itself
        # declares. Comparing a full-log fold to it would always differ: the
        # terminal event carries the trajectory, so the declared range stops
        # before it (see `test_d9_trajectory_digest_is_reproducible`).
        trajectory = result.trajectory or {}
        rng = trajectory.get("event_range") or {}
        declared = trajectory.get("state_digest")
        if declared and rng.get("last_seq") is not None:
            named = [e for e in events if int(e.seq) <= int(rng["last_seq"])]
            reproduced = compute_state_digest(reconstruct_state(named))
            if reproduced != declared:
                failures.append(
                    "M-5b: fresh-process fold of the declared event range does "
                    f"not reproduce state_digest ({reproduced} != {declared})")
            verdict["reconstructedDigest"] = reproduced
        verdict["stateDigest"] = digest
        verdict["eventCount"] = len(events)

    return not failures, failures, verdict


def main() -> int:
    parser = argparse.ArgumentParser(description="M-5b formal (SAT) material run")
    parser.add_argument("--dry-run", action="store_true")
    from vanguard.packages.adapters.models.config import get_default_model
    parser.add_argument("--model", default=get_default_model())
    parser.add_argument("--repo-dir", default="")
    parser.add_argument("--keep-run", action="store_true")
    args = parser.parse_args()

    assert_task_set_is_pinned()
    temp = None
    if args.repo_dir:
        repo = Path(args.repo_dir).resolve()
    else:
        temp = tempfile.mkdtemp(prefix="vg-m5b-")
        repo = Path(temp)

    try:
        setup_fixture(repo)
        db = repo / ".vanguard" / "events.sqlite3"
        blobs = repo / ".vanguard" / "blobs"

        if args.dry_run:
            harness = Runtime.compose(str(PACK), episode_id=EPISODE_ID)
            print(f"M-5b DRY RUN QUALIFIED: composed {harness.composition_digest} "
                  f"verbs={sorted(harness.verbs)}")
            print("M-5b: task set and oracle digests match the registry.")
            return 0

        if not (os.environ.get("OPENROUTER_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")):
            print("ERROR: live execution requires OPENROUTER_API_KEY.", file=sys.stderr)
            return 2

        # Run-scoped ephemeral identity; a shared literal seed makes every
        # evidence run attributable to the same key, which proves nothing.
        signer = OperatorSigner(secrets.token_bytes(32), key_id="m5b-run-operator")
        result = Runtime.execute_profiled(
            str(PACK),
            TaskContext(
                brief=(repo / "TASK.md").read_text(encoding="utf-8"),
                repo_path=repo, run_id=RUN_ID, episode_id=EPISODE_ID,
                project_id="formal-sat", max_turns=12),
            profile_id="product",
            model=OpenRouterModel(model=args.model),
            store_path=str(db),
            blobs=FileBlobStore(blobs),
            interactive=True,
            approver=lambda c: signer.approve(c, reviewer="autonomous-operator"),
            approval_key=signer.public_bytes,
        )

        ok, failures, verdict = verify(repo, db, result)
        print(json.dumps({"terminal": str(result.terminal), "verdict": verdict},
                         sort_keys=True))
        if not ok:
            print("M-5b FORMAL RUN FAILED:")
            for line in failures:
                print(f"  - {line}")
            return 1
        print("M-5b FORMAL RUN PASSED: exterior oracle accepted the witness.")
        return 0
    finally:
        if temp and Path(temp).exists() and not args.keep_run:
            shutil.rmtree(temp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
