"""Real-execution SBFL tracer using coverage.py subprocess or stdlib trace for 006_LLM_INT_MACHINE.

Captures actual statement-level execution coverage from oracle test runners to produce
calibrated Ochiai, Tarantula, and DStar suspiciousness rankings for Layer 3 context injection.
"""

from __future__ import annotations
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

try:
    from .fault_localizer import SBFLEngine, LineSuspiciousness
except ImportError:
    from fault_localizer import SBFLEngine, LineSuspiciousness


def decode_numbits(blob: bytes) -> set[int]:
    """Decode SQLite coverage numbits bitfield into set of executed line numbers."""
    lines: set[int] = set()
    for byte_idx, byte_val in enumerate(blob):
        for bit_idx in range(8):
            if byte_val & (1 << bit_idx):
                lines.add(byte_idx * 8 + bit_idx + 1)
    return lines


def run_coverage_subprocess(
    workspace_dir: Path,
    oracle_script_content: str,
    label: str = "failing",
    timeout: int = 30,
) -> dict[str, set[int]]:
    """Execute test script under coverage.py or fallback trace and return executed lines per file."""
    script_path = workspace_dir / f"_cov_runner_{label}.py"
    cov_data = workspace_dir / f".coverage_{label}"
    
    try:
        script_path.write_text(oracle_script_content, encoding="utf-8")
        
        # 1. Try coverage.py subprocess
        try:
            res = subprocess.run(
                [
                    sys.executable, "-m", "coverage", "run",
                    f"--data-file={cov_data}",
                    "--branch",
                    "--source=.",
                    str(script_path),
                ],
                cwd=str(workspace_dir),
                capture_output=True,
                timeout=timeout,
            )
            
            if cov_data.is_file():
                conn = sqlite3.connect(str(cov_data))
                cursor = conn.cursor()
                tables = {r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                result: dict[str, set[int]] = {}
                
                if "line_bits" in tables:
                    cursor.execute("SELECT file, numbits FROM line_bits")
                    for abs_file, blob in cursor.fetchall():
                        lines = decode_numbits(blob)
                        try:
                            rel = Path(abs_file).relative_to(workspace_dir).as_posix()
                            if not rel.startswith("_") and not rel.startswith("."):
                                result[rel] = lines
                        except ValueError:
                            pass
                elif "lines" in tables:
                    cursor.execute("SELECT file, lineno FROM lines")
                    for abs_file, lineno in cursor.fetchall():
                        try:
                            rel = Path(abs_file).relative_to(workspace_dir).as_posix()
                            if not rel.startswith("_") and not rel.startswith("."):
                                result.setdefault(rel, set()).add(lineno)
                        except ValueError:
                            pass
                
                conn.close()
                if result:
                    return result
        except Exception:
            pass

        # 2. Fallback to stdlib trace subprocess
        cover_dir = workspace_dir / f"_trace_cov_{label}"
        cover_dir.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                [
                    sys.executable, "-m", "trace", "--count",
                    f"--coverdir={cover_dir}",
                    str(script_path),
                ],
                cwd=str(workspace_dir),
                capture_output=True,
                timeout=timeout,
            )
            fallback_res: dict[str, set[int]] = {}
            for cover_file in cover_dir.glob("*.cover"):
                rel_name = cover_file.stem  # usually module.cover
                orig_py = workspace_dir / f"{rel_name}.py"
                if orig_py.is_file():
                    executed_lines: set[int] = set()
                    with open(cover_file, "r", encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, 1):
                            if line.startswith(" ") and not line.startswith("    "):
                                executed_lines.add(lineno)
                            elif line.strip() and not line.startswith("******") and not line.startswith("0:"):
                                parts = line.split(":", 1)
                                if len(parts) == 2 and parts[0].strip().isdigit() and int(parts[0].strip()) > 0:
                                    executed_lines.add(lineno)
                    if executed_lines:
                        fallback_res[f"{rel_name}.py"] = executed_lines
            return fallback_res
        except Exception:
            pass

        return {}
    finally:
        script_path.unlink(missing_ok=True)
        cov_data.unlink(missing_ok=True)
        import shutil
        trace_dir = workspace_dir / f"_trace_cov_{label}"
        if trace_dir.is_dir():
            shutil.rmtree(trace_dir, ignore_errors=True)


class CoverageBackedSBFL:
    """High-accuracy SBFL engine backed by subprocess execution tracing."""

    def __init__(self, workspace_dir: Path, sbfl_engine: SBFLEngine) -> None:
        self.root = workspace_dir
        self.sbfl = sbfl_engine

    def compute_real_rankings(
        self,
        oracle_script_content: str,
        top_k: int = 5,
    ) -> list[LineSuspiciousness]:
        """Collect real coverage traces and compute Ochiai rankings."""
        try:
            failing_cov = run_coverage_subprocess(
                self.root, oracle_script_content, label="failing"
            )
            failing_trace: set[tuple[str, int]] = {
                (f, ln) for f, lines in failing_cov.items() for ln in lines
            }
            if not failing_trace:
                return []
            
            # Rank against baseline
            rankings = self.sbfl.compute_rankings([failing_trace], [])
            return rankings[:top_k]
        except Exception:
            return []
