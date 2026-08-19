"""Run the preregistered Chapter 10 Q2 tasks through the production path.

This runner is evidence-producing code, not a synthetic benchmark shortcut:
the LAM proposal enters ``Runtime.execute_harness``, privileged changes cross
the approval flow and Bubblewrap worker, and the verdict comes from a separate
UID 10002 evaluator container over signed Unix-socket IPC.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import repo_paths
from vanguard.packages.adapters.evaluators.signing import VerdictSigner
from vanguard.packages.adapters.models.lam import LamModelAdapter
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.root import Runtime, TaskContext
from vanguard.packages.agency import RunTermination


MANIFEST = ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"
ORACLE_MANIFEST = repo_paths.preregistered_oracles()
SUITE_ROOT = ROOT / "vanguard/packages/adapters/evaluators/suites"


@dataclass(frozen=True)
class DogfoodTask:
    task_id: str
    title: str
    model: str
    files: Mapping[str, str]
    oracle: str
    expected_receipts: tuple[str, ...]


TASKS = (
    DogfoodTask(
        "bug-001-single-file",
        "Single-file calculator formula repair",
        "lam/t0-dogfood-bug-001",
        {"src/calculator.py": "def calculate(A, B):\n    return (A + B) * A\n"},
        "vanguard/packages/adapters/evaluators/suites/bug-001-single-file/test_oracle.py",
        ("fs.read", "patch.apply", "proc.exec"),
    ),
    DogfoodTask(
        "bug-002-multi-file",
        "Multi-file import-cycle repair",
        "lam/t0-dogfood-bug-002",
        {
            "db.py": "from models import User\n\ndef load():\n    return User()\n",
            "models.py": "from db import User\n",
        },
        "vanguard/packages/adapters/evaluators/suites/bug-002-multi-file/test_oracle.py",
        ("fs.read", "patch.apply", "patch.apply", "proc.exec"),
    ),
    DogfoodTask(
        "bug-003-test-reaction",
        "Parser repair retaining regression coverage",
        "lam/t0-dogfood-bug-003",
        {
            "src/parser.py": "def parse(text):\n    return list(text.split())\n",
            "test_parser.py": "def test_parser():\n    return None\n",
        },
        "vanguard/packages/adapters/evaluators/suites/bug-003-test-reaction/test_oracle.py",
        ("fs.read", "patch.apply", "patch.apply", "proc.exec"),
    ),
)


@contextmanager
def _environment(values: Mapping[str, str]) -> Iterator[None]:
    previous = {key: os.environ.get(key) for key in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True,
                   capture_output=True, text=True)


def _prepare_repo(root: Path, task: DogfoodTask) -> Path:
    repo = root / "repo"
    repo.mkdir()
    os.chmod(repo, 0o755)
    for relative, content in task.files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(path.parent, 0o755)
        path.write_text(content, encoding="utf-8")
    _git(repo, "init")
    _git(repo, "config", "user.name", "Dogfood Operator")
    _git(repo, "config", "user.email", "operator@vanguard.dev")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", f"initial broken state for {task.task_id}")
    return repo


def _evaluator_process(root: Path, repo: Path, task: DogfoodTask, image: str,
                       image_digest: str, key: bytes) -> tuple[subprocess.Popen[str], Path]:
    socket_dir = root / "run"
    socket_dir.mkdir()
    os.chmod(socket_dir, 0o1777)
    sealed = root / "sealed-oracle"
    (sealed / "vanguard/packages/adapters/evaluators").mkdir(parents=True)
    shutil.copy2(ORACLE_MANIFEST, sealed / "preregistered_oracles.json")
    shutil.copytree(SUITE_ROOT,
                    sealed / "vanguard/packages/adapters/evaluators/suites")
    for path in sealed.rglob("*"):
        os.chmod(path, 0o555 if path.is_dir() else 0o444)
    oracle_dir = f"/sealed-oracle/{task.oracle.rsplit('/', 1)[0]}"
    command = ["python3", "-m", "unittest", "discover", "-s", oracle_dir,
               "-p", "test_oracle.py"]
    args = [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--cap-drop=ALL", "--security-opt", "no-new-privileges",
        "--tmpfs", "/tmp:rw,nosuid,nodev",
        "--user", "10002:10002",
        "-w", "/workspace",
        "-e", "PYTHONPATH=/workspace",
        "-e", "PYTHONDONTWRITEBYTECODE=1",
        "-v", f"{repo}:/workspace:ro",
        "-v", f"{socket_dir}:/run/evaluator:rw",
        "-v", f"{sealed}:/sealed-oracle:ro",
        "-e", f"VANGUARD_EVALUATOR_PRIVATE_KEY_B64={base64.b64encode(key).decode('ascii')}",
        "-e", "VANGUARD_EVALUATOR_VERDICT_KEY_ID=dogfood-evaluator-key",
        image,
        "--socket", "/run/evaluator/eval.sock",
        "--workspace", "/workspace",
        "--oracle-manifest", "/sealed-oracle/preregistered_oracles.json",
        "--image-digest", image_digest,
        "--expected-client-uid", str(os.getuid()),
        "--command", *command,
    ]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
    return process, socket_dir / "eval.sock"


def _wait_for_socket(process: subprocess.Popen[str], socket_path: Path, timeout: float = 20.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if socket_path.exists():
            return
        if process.poll() is not None:
            stderr = process.stderr.read() if process.stderr is not None else ""
            raise RuntimeError(f"evaluator exited before handshake: {stderr[-2000:]}")
        time.sleep(0.1)
    raise TimeoutError(f"evaluator socket did not appear: {socket_path}")


def _stop(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _process_output(process: subprocess.Popen[str]) -> str:
    chunks = []
    if process.stdout is not None:
        chunks.append(process.stdout.read())
    if process.stderr is not None:
        chunks.append(process.stderr.read())
    return "\\n".join(chunk for chunk in chunks if chunk)[-2000:]


def run_task(task: DogfoodTask, evaluator_image: str, evaluator_digest: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix=f"vg-dogfood-{task.task_id}-") as directory:
        root = Path(directory)
        repo = _prepare_repo(root, task)
        evaluator_key = os.urandom(32)
        evaluator_signer = VerdictSigner(evaluator_key, "dogfood-evaluator-key")
        operator_signer = OperatorSigner(b"dogfood-operator-signing-key")
        process, socket_path = _evaluator_process(
            root, repo, task, evaluator_image, evaluator_digest, evaluator_key)
        try:
            _wait_for_socket(process, socket_path)
            env = {
                "VANGUARD_EVALUATOR_SOCKET": str(socket_path),
                "VANGUARD_EVALUATOR_IMAGE_DIGEST": evaluator_digest,
                "VANGUARD_EVALUATOR_VERDICT_KEY_ID": evaluator_signer.key_id,
                "VANGUARD_EVALUATOR_VERDICT_PUBLIC_KEY": base64.b64encode(
                    evaluator_signer.public_bytes).decode("ascii"),
            }
            with _environment(env):
                result = Runtime.execute_harness(
                    MANIFEST,
                    TaskContext(
                        brief=f"Repair the preregistered bug in {task.task_id} and verify it.",
                        repo_path=repo,
                        run_id=f"dogfood-{task.task_id}",
                        episode_id=f"dogfood-episode-{task.task_id}",
                        principal="dogfood-agent",
                        max_turns=8,
                    ),
                    model=LamModelAdapter(model_name=task.model),
                    approver=lambda challenge: operator_signer.approve(
                        challenge, reviewer="dogfood-operator"),
                    approval_key=operator_signer.public_bytes,
                )
            claims = tuple(result.verdict.claims) if result.verdict is not None else ()
            passed = (
                result.terminal is RunTermination.COMPLETED
                and tuple(receipt.verb for receipt in result.receipts) == task.expected_receipts
                and result.verdict is not None
                and result.verdict.outcome == "claims"
                and any(claim.get("event") == "EvaluationCompleted"
                        and claim.get("status") == "passed" for claim in claims
                        if isinstance(claim, Mapping))
            )
            diff = subprocess.run(["git", "diff", "--binary"], cwd=repo,
                                  check=True, capture_output=True).stdout
            _stop(process)
            process_output = _process_output(process)
            return {
                "task_id": task.task_id,
                "title": task.title,
                "status": "PASS" if passed else "FAIL",
                "turns": len(result.receipts) + 1,
                "hand_patches": 0,
                "restarts": 0,
                "oracle": task.oracle,
                "oracle_signed": bool(result.verdict and result.verdict.signature),
                "diff_digest": "sha256:" + hashlib.sha256(diff).hexdigest(),
                "operator_q2_reach_for_it": "YES" if passed else "NO",
                "terminal": result.terminal.value,
                "verdict": result.verdict.outcome if result.verdict else "missing",
                "verdict_reason": result.verdict.reason if result.verdict else "missing",
                "claims": claims,
                "evaluator_output": process_output,
                "detail": result.detail,
            }
        finally:
            _stop(process)


def _load_release_image() -> tuple[str, str]:
    manifest = json.loads((ROOT / "containers/manifest.json").read_text(encoding="utf-8"))
    evaluator = manifest["evaluator"]
    return str(evaluator["imageName"]), str(evaluator["imageDigest"])


def _write_log(results: list[dict[str, object]]) -> None:
    path = ROOT / "docs/03_sprints/evidence/dogfood-log.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Gate R9 — Q2 Dogfood Execution Log",
        "",
        f"**Execution Timestamp:** `{now}`  ",
        "**Harness:** `Runtime.execute_harness` + LAM + Bubblewrap worker  ",
        "**Evaluator:** UID `10002`, sealed oracle mount, signed Unix-socket verdict  ",
        "",
        "| Task | Turns | Hand Patches | Restarts | Oracle | Signed Verdict | Result | Q2 |",
        "|---|---:|---:|---:|---|---|---|---|",
    ]
    for result in results:
        lines.append(
            f"| `{result['task_id']}` | {result['turns']} | {result['hand_patches']} | "
            f"{result['restarts']} | `{result['oracle']}` | "
            f"{result['oracle_signed']} | **{result['status']}** | "
            f"**{result['operator_q2_reach_for_it']}** |"
        )
    lines.extend(["", "## Evidence", ""])
    for result in results:
        lines.extend([
            f"### {result['task_id']}",
            f"- Oracle: `{result['oracle']}`",
            f"- Diff digest: `{result['diff_digest']}`",
            f"- Terminal: `{result['terminal']}`; verdict: `{result['verdict']}`",
            f"- Verdict reason: `{result.get('verdict_reason', 'unknown')}`",
            f"- Claims: `{result.get('claims', ())}`",
            f"- Detail: {result['detail'] or 'none'}",
            "",
        ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    image, digest = _load_release_image()
    results: list[dict[str, object]] = []
    print("=== Gate R9: production dogfood ===")
    for task in TASKS:
        print(f"Running {task.task_id}...")
        try:
            result = run_task(task, image, digest)
        except Exception as exc:
            result = {
                "task_id": task.task_id,
                "title": task.title,
                "status": "FAIL",
                "turns": 0,
                "hand_patches": 0,
                "restarts": 0,
                "oracle": task.oracle,
                "oracle_signed": False,
                "diff_digest": "",
                "operator_q2_reach_for_it": "NO",
                "terminal": "error",
                "verdict": "inconclusive",
                "verdict_reason": "runner_error",
                "detail": str(exc),
            }
        results.append(result)
        print(f"  -> {result['status']} ({result['detail'] or result['terminal']})")
    _write_log(results)
    return 0 if all(result["status"] == "PASS" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
