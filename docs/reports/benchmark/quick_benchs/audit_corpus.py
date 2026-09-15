#!/usr/bin/env python3
"""Non-destructive corpus gate: poisoning, leaked solutions, baseline oracle color."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "evidence"
TRIVIAL_ASSERT = re.compile(r"assert\s+True\b")
SOLUTION_LEAK = re.compile(
    r"(the\s+fix\s+is|correct\s+implementation\s+is|solution:|answer\s+key)",
    re.I,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _count_files(path: Path) -> list[str]:
    return sorted(str(p.relative_to(path)) for p in path.rglob("*") if p.is_file())


def _scan_text(path: Path) -> dict:
    trivial = 0
    leaks = 0
    snippets: list[str] = []
    for p in path.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in {".py", ".md", ".txt", ".yaml", ".yml"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        trivial += len(TRIVIAL_ASSERT.findall(text))
        if SOLUTION_LEAK.search(text) and p.name.lower() in {"task.md", "readme.md", "spec.md"}:
            leaks += 1
            snippets.append(str(p.relative_to(path)))
        if p.suffix == ".py":
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Assert) and isinstance(node.test, ast.Constant) and node.test.value is True:
                    trivial += 1
    return {"trivial_assert_true": trivial, "task_leak_hits": leaks, "leak_files": snippets}


def _run(cmd: str, cwd: Path, timeout: float) -> dict:
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONPATH": f"{cwd}:{cwd / 'src'}",
            },
        )
        return {
            "exit_code": proc.returncode,
            "timed_out": False,
            "duration_s": round(time.perf_counter() - t0, 3),
            "stdout_tail": (proc.stdout or "")[-800:],
            "stderr_tail": (proc.stderr or "")[-800:],
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": 124,
            "timed_out": True,
            "duration_s": round(time.perf_counter() - t0, 3),
            "stdout_tail": "",
            "stderr_tail": "TIMEOUT",
        }


def audit_baac() -> list[dict]:
    rows = []
    base = ROOT / "benchmarks" / "baac" / "challenges"
    for challenge in sorted(p for p in base.glob("*/*") if p.is_dir() and (p / "challenge.yaml").is_file()):
        files = _count_files(challenge)
        scan = _scan_text(challenge)
        manifest = challenge / "manifest.sha256"
        oracle = challenge / "oracle" / "verify.py"
        with tempfile.TemporaryDirectory(prefix="gate-baac-") as td:
            scratch = Path(td)
            src = challenge / "src"
            if src.is_dir():
                subprocess.run(["cp", "-a", str(src), str(scratch / "src")], check=False)
            else:
                subprocess.run(["cp", "-a", str(challenge), str(scratch / "copy")], check=False)
            cmd = f"python3 {oracle} --workspace {scratch}"
            if not oracle.is_file():
                result = {"exit_code": 127, "timed_out": False, "duration_s": 0, "stderr_tail": "missing oracle"}
            else:
                result = _run(cmd, scratch, 20.0)
        color = "TIMEOUT" if result["timed_out"] else ("GREEN" if result["exit_code"] == 0 else "RED")
        gate = "PASS"
        notes = []
        if scan["trivial_assert_true"]:
            gate = "WARN"
            notes.append("trivial assert True")
        if scan["task_leak_hits"]:
            gate = "WARN"
            notes.append("possible solution leak in task prose")
        if not manifest.is_file():
            gate = "WARN"
            notes.append("missing manifest.sha256")
        if color == "GREEN":
            notes.append("baseline already passes (premature green / toothless oracle risk)")
            if gate == "PASS":
                gate = "WARN"
        rows.append({
            "id": challenge.name,
            "suite": "baac",
            "stratum": challenge.parent.name,
            "files": len(files),
            "file_list": files,
            "gate_check": gate,
            "notes": notes,
            "poison_scan": scan,
            "manifest_present": manifest.is_file(),
            "oracle_present": oracle.is_file(),
            "initial_falsifier": color,
            "oracle_run": result,
        })
    return rows


def audit_b20() -> list[dict]:
    rows = []
    base = ROOT / "benchmarks" / "benchmark_20_suite"
    for challenge in sorted(p for p in base.iterdir() if p.is_dir() and p.name[:2].isdigit()):
        files = _count_files(challenge)
        scan = _scan_text(challenge)
        tests = list(challenge.glob("test/test_*.py"))
        if tests:
            rel = tests[0].relative_to(challenge)
            cmd = f"PYTHONPATH=. python3 -m unittest {rel.as_posix()} -v"
        else:
            cmd = "PYTHONPATH=. python3 -m unittest discover -s . -p 'test*.py' -v"
        timeout = 8.0 if "timeout" not in challenge.name and "subprocess" not in challenge.name else 4.0
        result = _run(cmd, challenge, timeout)
        color = "TIMEOUT" if result["timed_out"] else ("GREEN" if result["exit_code"] == 0 else "RED")
        gate = "PASS"
        notes = []
        if scan["trivial_assert_true"]:
            gate = "WARN"
            notes.append("trivial assert True")
        if color == "GREEN":
            notes.append("baseline already passes (premature green / toothless oracle risk)")
            gate = "WARN"
        if color == "TIMEOUT":
            notes.append("oracle hung; timeout protection required")
        rows.append({
            "id": challenge.name,
            "suite": "benchmark_20_suite",
            "stratum": "brownfield" if challenge.name[:2] <= "10" else "greenfield",
            "files": len(files),
            "file_list": files,
            "gate_check": gate,
            "notes": notes,
            "poison_scan": scan,
            "oracle_present": bool(tests),
            "initial_falsifier": color,
            "oracle_run": result,
            "falsifier_command": cmd,
        })
    return rows


def audit_greenfield() -> list[dict]:
    rows = []
    base = ROOT / "benchmarks" / "greenfield"
    for challenge in sorted(p for p in base.iterdir() if p.is_dir()):
        files = _count_files(challenge)
        scan = _scan_text(challenge)
        tests = list(challenge.glob("test*.py")) + list(challenge.glob("test/test_*.py"))
        if not tests:
            rows.append({
                "id": challenge.name,
                "suite": "greenfield",
                "stratum": "greenfield",
                "files": len(files),
                "file_list": files,
                "gate_check": "STATIC",
                "notes": ["no executable oracle in-tree"],
                "poison_scan": scan,
                "oracle_present": False,
                "initial_falsifier": "NO_ORACLE",
                "oracle_run": None,
            })
            continue
        cmd = "python3 -m unittest discover -s . -p 'test*.py' -v"
        timeout = 4.0 if "timeout" in challenge.name or "subprocess" in challenge.name else 15.0
        result = _run(cmd, challenge, timeout)
        color = "TIMEOUT" if result["timed_out"] else ("GREEN" if result["exit_code"] == 0 else "RED")
        gate = "PASS"
        notes = []
        if scan["trivial_assert_true"]:
            gate = "WARN"
            notes.append("trivial assert True")
        if color == "GREEN":
            notes.append("baseline already passes")
            gate = "WARN"
        if color == "TIMEOUT":
            notes.append("designed hang or unbounded loop suspected")
        rows.append({
            "id": challenge.name,
            "suite": "greenfield",
            "stratum": "greenfield",
            "files": len(files),
            "file_list": files,
            "gate_check": gate,
            "notes": notes,
            "poison_scan": scan,
            "oracle_present": True,
            "initial_falsifier": color,
            "oracle_run": result,
            "falsifier_command": cmd,
        })
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    rows = audit_baac() + audit_b20() + audit_greenfield()
    summary = {
        "total": len(rows),
        "by_suite": {},
        "by_color": {},
        "by_gate": {},
        "duration_s": round(time.perf_counter() - t0, 3),
    }
    for row in rows:
        summary["by_suite"][row["suite"]] = summary["by_suite"].get(row["suite"], 0) + 1
        summary["by_color"][row["initial_falsifier"]] = summary["by_color"].get(row["initial_falsifier"], 0) + 1
        summary["by_gate"][row["gate_check"]] = summary["by_gate"].get(row["gate_check"], 0) + 1
    payload = {"summary": summary, "challenges": rows}
    (OUT / "corpus_gate.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
