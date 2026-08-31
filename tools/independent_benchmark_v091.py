#!/usr/bin/env python3
"""Independent five-case evaluation for the Wave-2 agent stack.

The evaluator owns the baseline and the oracle.  Neither is materialised in
the agent workspace or supplied to the model.  Cases 1--3 execute a real
``Runtime`` episode with the deterministic LAM ModelPort; case 4 probes the
fail-closed completion policies directly; case 5 exercises LAM persistence
and LDA health through their public interfaces.

Run:
    python3 tools/independent_benchmark_v091.py
    python3 tools/independent_benchmark_v091.py --out /tmp/report.json
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"
LAM_SCENARIOS = ROOT / "tools/002_LLM_API_MOCK/scenarios"
DEFAULT_OUT = ROOT / "benchmarks/independent_v091/artifacts/report.json"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools/002_LLM_API_MOCK"))

from engine import LamEngine  # noqa: E402
from recorder import MockRecorder  # noqa: E402
from mcp_server import LamMCPServer  # noqa: E402
from vanguard.packages.adapters.models.lam import LamModelAdapter  # noqa: E402
from vanguard.packages.adapters.stores.blob_store import FileBlobStore  # noqa: E402
from vanguard.packages.adapters.stores.event_store import SqliteEventStore  # noqa: E402
from vanguard.packages.domain.canonicalisation.digest import digest_of  # noqa: E402
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict  # noqa: E402
from vanguard.packages.ports.event_store import Result  # noqa: E402
from vanguard.packages.runtime.governance.approvals import OperatorSigner  # noqa: E402
from vanguard.packages.runtime.root import Runtime, TaskContext  # noqa: E402


def _write(root: Path, files: Mapping[str, str]) -> None:
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _run_command(root: Path, argv: list[str]) -> bool:
    result = subprocess.run(
        argv,
        cwd=root,
        env={**os.environ, "PYTHONPATH": str(root)},
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return result.returncode == 0


def _diff(old: str, new: str, path: str) -> str:
    return "".join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}",
    ))


class _IndependentVerifier:
    """Permit the runtime episode to settle; scoring remains external."""

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        return Result.success(Verdict(
            outcome="claims",
            claims=({"claim": "episode_settled", "holds": True},),
            reason=f"independent:{run_ref.run_id}:{protocol.name}",
        ))


def _scenario(path: Path, scenario_id: str, title: str, turns: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps({
        "id": scenario_id,
        "tier": 1,
        "title": title,
        "workspace": {},
        "turns": turns,
    }, sort_keys=True), encoding="utf-8")


def _call(name: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
    return {"type": "function", "function": {
        "name": name, "arguments": dict(arguments),
    }}


def _agent_case(
    case_id: str,
    brief: str,
    files: Mapping[str, str],
    turns: list[dict[str, Any]],
    oracle: Callable[[Path], bool],
    *,
    baseline: Callable[[Path], bool] | None = None,
    pre_agent: Callable[[Path], None] | None = None,
    post_agent: Callable[[Path], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix=f"independent-{case_id}-") as temp:
        workspace = Path(temp)
        _write(workspace, files)
        baseline_passed = baseline(workspace) if baseline else oracle(workspace)
        if baseline_passed:
            return {
                "id": case_id, "passed": False, "terminal": "DATASET_INVALID",
                "reason": "baseline_already_passes", "baseline_passed": True,
            }
        if pre_agent is not None:
            pre_agent(workspace)

        with tempfile.TemporaryDirectory(prefix="independent-state-") as state_temp:
            state = Path(state_temp)
            scenario_dir = state / "scenarios"
            scenario_dir.mkdir()
            scenario_id = f"t1-independent-{case_id}"
            _scenario(scenario_dir / f"{scenario_id}.json", scenario_id, case_id, turns)
            store = SqliteEventStore(state / "events.sqlite3")
            blobs = FileBlobStore(state / "blobs")
            model = LamModelAdapter(model_name=scenario_id, scenario_dir=scenario_dir)
            # The runtime's byte-key authority registers the supplied public
            # key under its default key id; keep the signer id aligned so the
            # approval is cryptographically verifiable rather than merely
            # syntactically present.
            signer = OperatorSigner(hashlib.sha256(case_id.encode()).digest())
            run_id = f"independent-{case_id}"
            result = Runtime.execute_harness(
                MANIFEST,
                TaskContext(
                    brief=brief, repo_path=workspace, run_id=run_id,
                    episode_id=f"episode-{case_id}", max_turns=8,
                ),
                model=model,
                approver=lambda challenge: signer.approve(challenge, reviewer="independent-evaluator"),
                approval_key=signer.public_bytes,
                verifier=_IndependentVerifier(),
                store=store,
                blobs=blobs,
                sandbox_mode="host-dev",
            )
            oracle_passed = oracle(workspace)
            with sqlite3.connect(state / "events.sqlite3") as connection:
                event_count = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
                proposal_count = connection.execute(
                    "SELECT COUNT(*) FROM events WHERE envelope_json LIKE '%ProposalProduced%'"
                ).fetchone()[0]
            terminal = getattr(result.terminal, "value", str(result.terminal))
            passed = bool(oracle_passed and terminal == "completed")
            facts: dict[str, Any] = {
                "id": case_id,
                "passed": passed,
                "terminal": terminal,
                "reason": "external_oracle_passed" if passed else "external_oracle_failed",
                "baseline_passed": False,
                "oracle_passed": oracle_passed,
                "receipts": len(getattr(result, "receipts", ())),
                "events": event_count,
                "proposal_events": proposal_count,
                "trajectory_digest": digest_of(getattr(result, "trajectory", {})),
                "detail": str(getattr(result, "detail", "")),
                "receipt_verbs": [str(getattr(receipt, "verb", "")) for receipt in getattr(result, "receipts", ())],
                "event_reasons": [str(getattr(event, "reason", "")) for event in getattr(result, "events", ())[-8:]],
            }
            if post_agent is not None:
                facts.update(dict(post_agent(workspace)))
                facts["passed"] = bool(facts["passed"] and facts.get("admissible", False))
            return facts
    # The return above is inside the temporary state scope; only public facts
    # are retained, never the evaluator's oracle or disposable workspace.


def _basic_agent_case() -> dict[str, Any]:
    source = "def value():\n    return 1\n"
    fixed = "def value():\n    return 2\n"
    files = {
        "src/value.py": source,
        "test_value.py": (
            "import unittest\nfrom src.value import value\n\n"
            "class TestValue(unittest.TestCase):\n"
            "    def test_value(self): self.assertEqual(value(), 2)\n"
        ),
    }
    return _agent_case(
        "agent_basic",
        "Repair src/value.py so the declared unittest passes.",
        files,
        [
            {"tool_messages": 0, "finish_reason": "tool_calls", "tool_calls": [_call("read", {"path": "src/value.py"})]},
            {"tool_messages": 1, "finish_reason": "tool_calls", "tool_calls": [_call("patch", {"path": "src/value.py", "diff": _diff(source, fixed, "src/value.py")})]},
            {"tool_messages": 2, "finish_reason": "tool_calls", "tool_calls": [_call("test", {"argv": ["python3", "-m", "unittest", "-q"]})]},
            {"tool_messages": 3, "finish_reason": "stop", "content": "verified", "tool_calls": []},
        ],
        lambda root: _run_command(root, ["python3", "-m", "unittest", "-q"]),
    )


def _multifile_agent_case() -> dict[str, Any]:
    api_old = "def public_name():\n    return 'old'\n"
    api_new = "def public_name():\n    return 'new'\n"
    client_old = "from .api import public_name\n\ndef render():\n    return public_name()\n"
    client_new = "from .api import public_name\n\ndef render() -> str:\n    return public_name()\n"
    files = {
        "pkg/__init__.py": "",
        "pkg/api.py": api_old,
        "pkg/client.py": client_old,
        "test_contract.py": (
            "import unittest\nfrom pkg.client import render\n\n"
            "class TestContract(unittest.TestCase):\n"
            "    def test_public_contract(self): self.assertEqual(render(), 'new')\n"
        ),
    }
    patch = _diff(api_old, api_new, "pkg/api.py") + _diff(client_old, client_new, "pkg/client.py")
    return _agent_case(
        "agent_multifile",
        "Update the public name contract across pkg/api.py and pkg/client.py and pass the declared unittest.",
        files,
        [
            {"tool_messages": 0, "finish_reason": "tool_calls", "tool_calls": [_call("read", {"path": "pkg/api.py"})]},
            {"tool_messages": 1, "finish_reason": "tool_calls", "tool_calls": [_call("read", {"path": "pkg/client.py"})]},
            {"tool_messages": 2, "finish_reason": "tool_calls", "tool_calls": [_call("patch", {"path": "pkg/api.py", "diff": patch})]},
            {"tool_messages": 3, "finish_reason": "tool_calls", "tool_calls": [_call("test", {"argv": ["python3", "-m", "unittest", "-q"]})]},
            {"tool_messages": 4, "finish_reason": "stop", "content": "verified", "tool_calls": []},
        ],
        lambda root: (
            "-> str" in (root / "pkg/client.py").read_text(encoding="utf-8")
            and _run_command(root, ["python3", "-m", "unittest", "-q"])
        ),
    )


def _greenfield_agent_case() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "packs/code-default"))
    from middleware.repository.greenfield import GreenfieldPolicy

    files: dict[str, str] = {}
    app = "def greet(name: str) -> str:\n    return f'Hello, {name}!'\n"
    smoke = (
        "import unittest\nfrom app import greet\n\n"
        "class TestSmoke(unittest.TestCase):\n"
        "    def test_greet(self): self.assertEqual(greet('Ada'), 'Hello, Ada!')\n"
    )

    def oracle(root: Path) -> bool:
        return _run_command(root, ["python3", "-m", "unittest", "-q"])

    policy_box: dict[str, Any] = {}

    def pre_agent(root: Path) -> None:
        policy = GreenfieldPolicy(root)
        assessment = policy.assess()
        baseline = policy.record_scaffold_baseline()
        policy_box.update(policy=policy, assessment=assessment, baseline=baseline)

    def post_agent(root: Path) -> Mapping[str, Any]:
        policy = policy_box["policy"]
        baseline = policy_box["baseline"]
        structural = _run_command(root, ["python3", "-m", "py_compile", "app.py"])
        behavioral = oracle(root)
        decision = policy.evaluate(
            structural_passed=structural,
            behavioral_passed=behavioral,
            smoke_test_created=(root / "test_app.py").is_file(),
            created_files=("app.py", "test_app.py"),
            baseline=baseline,
        )
        return {
            "workspace_effectively_empty": policy_box["assessment"].effectively_empty,
            "baseline_recorded": baseline.decision == "scaffold_baseline_recorded",
            "structural_passed": structural,
            "behavioral_passed": behavioral,
            "greenfield_admitted": decision.admissible,
            "admissible": decision.admissible,
            "greenfield_reason": decision.reason,
        }

    return _agent_case(
            "agent_greenfield",
            "Create app.py with greet(name) and a generated smoke test test_app.py; run the test.",
            files,
            [
                {"tool_messages": 0, "finish_reason": "tool_calls", "tool_calls": [_call("patch", {"path": "app.py", "content": app})]},
                {"tool_messages": 1, "finish_reason": "tool_calls", "tool_calls": [_call("patch", {"path": "test_app.py", "content": smoke})]},
                {"tool_messages": 2, "finish_reason": "tool_calls", "tool_calls": [_call("test", {"argv": ["python3", "-m", "unittest", "-q"]})]},
                {"tool_messages": 3, "finish_reason": "stop", "content": "verified", "tool_calls": []},
            ],
            oracle,
            baseline=lambda root: False,
            pre_agent=pre_agent,
            post_agent=post_agent,
        )


def _framework_case() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "packs/code-default"))
    from middleware.repository.multi_file_completeness import check_multi_file_completeness

    incomplete = check_multi_file_completeness(
        ("pkg/api.py",), ("pkg/api.py",), ("pkg/api.py",),
        changed_public_symbols=("public_name",),
        callers_by_symbol={"public_name": ("pkg/client.py",)},
    )
    truncated = check_multi_file_completeness(
        ("pkg/api.py", "pkg/client.py"), ("pkg/api.py",), ("pkg/api.py",),
        truncated=True,
    )
    empty = check_multi_file_completeness((), (), (),)
    migration = check_multi_file_completeness(
        ("migration.py",), ("migration.py",), ("migration.py",),
        migration_required=True, compatibility_evidence=True,
    )
    passed = all(
        not report.is_complete and report.rejections
        for report in (incomplete, truncated, empty, migration)
    )
    return {
        "id": "framework_fail_closed",
        "passed": passed,
        "incomplete_rejections": list(incomplete.rejections),
        "truncated_rejections": list(truncated.rejections),
        "empty_rejections": list(empty.rejections),
        "migration_rejections": list(migration.rejections),
    }


def _lam_lda_case() -> dict[str, Any]:
    engine = LamEngine.from_directory(LAM_SCENARIOS)
    body = {"model": "t0-vanguard-vertical", "messages": [{"role": "user", "content": "read src/value.py"}]}
    first = engine.complete(body)
    second = engine.complete(body)
    deterministic = first == second
    with tempfile.TemporaryDirectory(prefix="independent-lam-") as temp:
        db = Path(temp) / "lam.sqlite"
        recorder = MockRecorder(db)
        encoded = json.dumps(first, sort_keys=True)
        digest = hashlib.sha256(encoded.encode()).hexdigest()
        recorder.record_call(
            request_sha256=hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest(),
            scenario_key="t0-vanguard-vertical", tier=1, requested_turn=0,
            returned_turn=0, reply_sha256=digest, source_label="independent-v091",
            run_id="independent-lam-lda", prompt=json.dumps(body), response=encoded,
            evidence_label="independent", tokens=first["usage"]["total_tokens"],
            prompt_tokens=first["usage"]["prompt_tokens"],
            completion_tokens=first["usage"]["completion_tokens"],
        )
        with sqlite3.connect(db) as connection:
            call_count = connection.execute("SELECT COUNT(*) FROM mock_calls").fetchone()[0]
        mcp = LamMCPServer()
        listed = mcp.handle_tool_call("lam_list_scenarios", {"limit": 5})

    doctor = subprocess.run(
        ["uv", "run", "lda", "doctor", "--json"],
        cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
    )
    try:
        doctor_json = json.loads(doctor.stdout)
    except json.JSONDecodeError:
        doctor_json = {}
    lda_healthy = doctor.returncode == 0 and doctor_json.get("index_healthy") is True
    passed = deterministic and call_count == 1 and listed.get("total", 0) > 0 and lda_healthy
    return {
        "id": "lam_lda_contract",
        "passed": passed,
        "lam_deterministic": deterministic,
        "lam_sqlite_calls": call_count,
        "lam_scenarios_listed": listed.get("total", 0),
        "lda_index_healthy": lda_healthy,
        "lda_head": doctor_json.get("head_sha"),
    }


def run() -> dict[str, Any]:
    cases = [
        _basic_agent_case(),
        _multifile_agent_case(),
        _greenfield_agent_case(),
        _framework_case(),
        _lam_lda_case(),
    ]
    return {
        "schema": "aether.independent-benchmark/1",
        "evaluator": "independent-v091",
        "non_empirical": False,
        "cases": cases,
        "passed": sum(bool(case.get("passed")) for case in cases),
        "total": len(cases),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    report = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"INDEPENDENT_BENCHMARK_V091: {report['passed']}/{report['total']} PASS")
    print(f"saved report to {args.out}")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
