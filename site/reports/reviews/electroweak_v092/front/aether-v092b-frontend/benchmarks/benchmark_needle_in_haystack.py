"""Standalone Needle-In-A-Haystack Context Pollution Benchmark.

This benchmark evaluates an agent harness's resilience against massive context
pollution and decoy specifications. It constructs a workspace containing a large
multi-chapter markdown specification (50KB+ / hundreds of sections) filled with
plausible legacy algorithms, decoy formulas, and misleading state machine rules.

A single canonical 'Needle' specification is buried deep in the document. The
agent must locate the authentic specification, ignore the decoys, implement the
exact multi-file protocol, and pass the hidden oracle test.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import traceback
import unittest
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

env_file = ROOT / ".env"
if env_file.is_file():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if k in {"OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "VANGUARD_ALLOW_PAID"}:
                os.environ[k] = v

from vanguard.packages.runtime.root import (
    application_service,
    Cassette,
    CassetteRecorder,
    OpenRouterModel,
)

OUT_DIR = ROOT / "benchmarks/artifacts/needle"

NEEDLE_CHAPTER = 37
NEEDLE_SECTION = "37.4.2"
NEEDLE_SALT = "VANGUARD_LUNA_SALT_99"
NEEDLE_MAGIC_BYTE = 0x5A


def generate_haystack_markdown(total_chapters: int = 55) -> str:
    """Generate a massive markdown specification with decoys and one embedded needle."""
    lines = [
        "# Enterprise Protocol Specification & System Architecture Guide (RFC-9982)",
        "",
        "## Abstract",
        "This specification documents the enterprise distributed payload protocol.",
        "NOTICE: Multiple historical revisions (v1.0 - v3.9) are retained for backward",
        "compatibility. Implementers MUST follow the active canonical specification",
        "designated in Section 37.4.2 (Protocol Revision 4.2-STABLE). All other sections",
        "represent deprecated or experimental protocols and must not be used.",
        "",
    ]

    for ch in range(1, total_chapters + 1):
        lines.append(f"## Chapter {ch}: Protocol Subsystem {ch}")
        lines.append("")
        lines.append(f"### Section {ch}.1: Overview and Scope")
        lines.append(f"This section discusses architectural considerations for subsystem {ch}.")
        lines.append("Payload integrity and serialization considerations are detailed below.")
        lines.append("")

        for sec in range(2, 6):
            sec_id = f"{ch}.{sec}"
            lines.append(f"### Section {sec_id}: Implementation Variance {sec_id}")
            if ch == NEEDLE_CHAPTER and sec == 4:
                # Embedded Canonical Needle
                lines.extend([
                    f"#### Subsection {NEEDLE_SECTION}: Canonical Active Protocol Spec (MANDATORY)",
                    "",
                    "> [!IMPORTANT]",
                    "> **CANONICAL ACTIVE PROTOCOL SPECIFICATION (v4.2-STABLE)**",
                    "> This subsection is the SOLE AUTHORITATIVE specification for `core/codec.py`.",
                    "",
                    "##### 1. Packet Encoding Algorithm (`encode_packet`):",
                    "- Input: `packet_id: int`, `payload: str`, `priority: int = 1`",
                    f"- Secret Salt Constant: `SALT = {NEEDLE_SALT!r}`",
                    f"- Magic Prefix: A single byte with value `0x{NEEDLE_MAGIC_BYTE:02X}` (`{bytes([NEEDLE_MAGIC_BYTE])!r}`).",
                    "- Checksum Formula: `sha256(f'{SALT}:{packet_id}:{priority}:{payload}'.encode('utf-8')).hexdigest()[:16]`",
                    "- Wire Format Structure (JSON payload followed by delimiter and checksum):",
                    "  `0x5A` + `utf-8 bytes of json_dict` + `b'::CHECKSUM::'` + `checksum.encode('ascii')`",
                    "  where `json_dict` contains exact keys: `{'id': packet_id, 'p': priority, 'data': payload}`.",
                    "",
                    "##### 2. Packet Decoding Algorithm (`decode_packet`):",
                    "- Input: `raw_bytes: bytes`",
                    "- Validation Rules:",
                    f"  1. Must start with magic byte `0x{NEEDLE_MAGIC_BYTE:02X}`. If missing, raise `InvalidMagicError('invalid magic header')`.",
                    "  2. Must contain `b'::CHECKSUM::'` delimiter. If missing, raise `CorruptFrameError('missing checksum delimiter')`.",
                    "  3. Extract payload JSON and checksum token.",
                    "  4. Recompute checksum using the exact canonical formula. If mismatch, raise `ChecksumMismatchError(f'checksum mismatch: expected {expected}, got {received}')`.",
                    "  5. Return a `Packet` instance with attributes `(packet_id=int, payload=str, priority=int, checksum=str)`.",
                    "",
                    "##### 3. Exponential Backoff Policy (`calculate_retry_delay`):",
                    "- Formula: `delay = (base_ms * (3 ** attempt)) + (packet_id % 17)`",
                    "- Max delay cap: `min(delay, max_ms)`",
                    "",
                ])
            else:
                # Decoy Specifications
                decoy_salt = f"DECOY_SALT_REV_{ch}_{sec}"
                decoy_magic = (ch * 7 + sec) % 256
                lines.extend([
                    f"Historical draft {sec_id}: Use `SALT = {decoy_salt!r}` with magic prefix `0x{decoy_magic:02X}`.",
                    f"Checksum: `md5(payload + {decoy_salt!r})` or `sha1(f'{ch}:{sec}')`.",
                    f"Backoff delay formula: `delay = base_ms * (2 ** attempt) + {sec}`.",
                    "Legacy error handling: Raise generic `ValueError` or `RuntimeError` on corruption.",
                    "",
                    "```python",
                    f"# Deprecated draft {sec_id} prototype",
                    f"def legacy_decode_{ch}_{sec}(data):",
                    f"    return data.split(b':')[0]",
                    "```",
                    "",
                ])

    return "\n".join(lines)


STARTER_CODEC = '''"""Core Protocol Codec (Incomplete / Deprecated Draft)."""

from __future__ import annotations
from dataclasses import dataclass

class ProtocolError(Exception):
    """Base protocol exception."""

class InvalidMagicError(ProtocolError):
    pass

class CorruptFrameError(ProtocolError):
    pass

class ChecksumMismatchError(ProtocolError):
    pass

@dataclass(frozen=True)
class Packet:
    packet_id: int
    payload: str
    priority: int
    checksum: str

def encode_packet(packet_id: int, payload: str, priority: int = 1) -> bytes:
    # BUG / STUB: Needs implementation according to the Canonical Active Protocol Spec (Section 37.4.2)
    raise NotImplementedError("Implement encode_packet per SPECIFICATION.md Section 37.4.2")

def decode_packet(raw_bytes: bytes) -> Packet:
    # BUG / STUB: Needs implementation according to the Canonical Active Protocol Spec (Section 37.4.2)
    raise NotImplementedError("Implement decode_packet per SPECIFICATION.md Section 37.4.2")

def calculate_retry_delay(base_ms: int, attempt: int, packet_id: int, max_ms: int = 10000) -> int:
    # BUG / STUB: Needs implementation according to the Canonical Active Protocol Spec (Section 37.4.2)
    raise NotImplementedError("Implement calculate_retry_delay per SPECIFICATION.md Section 37.4.2")
'''

STARTER_PUBLIC_TEST = '''import unittest
from core.codec import Packet, ProtocolError, InvalidMagicError, CorruptFrameError, ChecksumMismatchError

class TestPublicInterface(unittest.TestCase):
    def test_packet_dataclass(self):
        p = Packet(packet_id=1, payload="hello", priority=1, checksum="abc")
        self.assertEqual(p.packet_id, 1)
        self.assertEqual(p.payload, "hello")
        self.assertEqual(p.priority, 1)

    def test_exception_hierarchy(self):
        self.assertTrue(issubclass(InvalidMagicError, ProtocolError))
        self.assertTrue(issubclass(CorruptFrameError, ProtocolError))
        self.assertTrue(issubclass(ChecksumMismatchError, ProtocolError))

if __name__ == "__main__":
    unittest.main()
'''

TASK_BRIEF = """Implement the Enterprise Protocol Codec in `core/codec.py`.

CONTEXT & WORKSPACE INFORMATION:
The workspace contains a comprehensive multi-chapter reference manual `SPECIFICATION.md`.
It contains dozens of legacy/deprecated protocol revisions, but ONLY ONE canonical active
specification: **Section 37.4.2 (Protocol Revision 4.2-STABLE)**.

YOUR OBJECTIVE:
1. Locate Section 37.4.2 in `SPECIFICATION.md` to find the authoritative encoding, decoding,
   and retry delay specifications. Do NOT use deprecated decoy formulas from other sections.
2. Implement `encode_packet`, `decode_packet`, and `calculate_retry_delay` in `core/codec.py`.
3. Verify your implementation using `test` with `{"argv": ["python3", "-m", "unittest", "discover", "-s", "."]}`.
4. Once tests pass, call `finish` with a summary.
"""

ORACLE_TEST_CODE = f'''import unittest
import hashlib
import json
from core.codec import (
    Packet,
    encode_packet,
    decode_packet,
    calculate_retry_delay,
    InvalidMagicError,
    CorruptFrameError,
    ChecksumMismatchError,
)

class HiddenNeedleOracleTest(unittest.TestCase):
    SALT = {NEEDLE_SALT!r}
    MAGIC = bytes([{NEEDLE_MAGIC_BYTE}])

    def test_canonical_encoding_and_decoding_roundtrip(self):
        raw = encode_packet(42, "telemetry_payload_alpha", priority=3)
        self.assertTrue(raw.startswith(self.MAGIC), "Encoded frame must start with 0x5A magic byte")
        self.assertIn(b"::CHECKSUM::", raw, "Encoded frame must contain ::CHECKSUM:: delimiter")

        packet = decode_packet(raw)
        self.assertEqual(packet.packet_id, 42)
        self.assertEqual(packet.payload, "telemetry_payload_alpha")
        self.assertEqual(packet.priority, 3)

        expected_checksum = hashlib.sha256(f"{{self.SALT}}:42:3:telemetry_payload_alpha".encode("utf-8")).hexdigest()[:16]
        self.assertEqual(packet.checksum, expected_checksum)

    def test_magic_byte_validation(self):
        valid = encode_packet(1, "test")
        corrupted = b"\\x00" + valid[1:]
        with self.assertRaises(InvalidMagicError):
            decode_packet(corrupted)

    def test_delimiter_validation(self):
        with self.assertRaises(CorruptFrameError):
            decode_packet(self.MAGIC + b"invalid_json_without_delimiter")

    def test_checksum_mismatch_validation(self):
        valid = encode_packet(10, "data_val", priority=2)
        body, sep, _ = valid.partition(b"::CHECKSUM::")
        tampered = body + sep + b"badchecksum00000"
        with self.assertRaises(ChecksumMismatchError):
            decode_packet(tampered)

    def test_retry_delay_exponential_base3_plus_modulo17(self):
        # Formula: (base_ms * (3 ** attempt)) + (packet_id % 17)
        # attempt 0: (100 * 1) + (35 % 17 = 1) = 101
        self.assertEqual(calculate_retry_delay(100, 0, 35, max_ms=5000), 101)
        # attempt 2: (100 * 9) + (35 % 17 = 1) = 901
        self.assertEqual(calculate_retry_delay(100, 2, 35, max_ms=5000), 901)
        # attempt 4: (100 * 81) + 1 = 8101 -> capped at 5000
        self.assertEqual(calculate_retry_delay(100, 4, 35, max_ms=5000), 5000)

if __name__ == "__main__":
    unittest.main()
'''


def run_oracle_test(ws: Path) -> tuple[bool, str]:
    oracle_file = ws / "_oracle_test.py"
    oracle_file.write_text(ORACLE_TEST_CODE, encoding="utf-8")
    import subprocess
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "_oracle_test.py"],
        cwd=str(ws),
        capture_output=True,
        text=True,
        timeout=30,
    )
    passed = proc.returncode == 0
    output = f"{proc.stdout}\n{proc.stderr}".strip()
    return passed, output


def setup_workspace(ws: Path) -> None:
    (ws / "core").mkdir(parents=True, exist_ok=True)
    (ws / "tests").mkdir(parents=True, exist_ok=True)
    (ws / "core/__init__.py").write_text("", encoding="utf-8")
    (ws / "core/codec.py").write_text(STARTER_CODEC, encoding="utf-8")
    (ws / "tests/test_public.py").write_text(STARTER_PUBLIC_TEST, encoding="utf-8")

    spec_content = generate_haystack_markdown(total_chapters=55)
    (ws / "SPECIFICATION.md").write_text(spec_content, encoding="utf-8")


def run_needle_benchmark(
    *,
    manifest: str = "vg-code-max-v3luna",
    model: str = "deepseek/deepseek-v4-flash-0731",
    max_turns: int = 15,
    tag: str = "needle_run",
    budget_usd: float = 0.05,
    max_calls: int = 30,
) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_tag = re.sub(r"[^A-Za-z0-9_.-]+", "_", tag).strip("._") or "run"
    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", model)
    stem = f"{safe_tag}__needle_context_pollution__{safe_model}"
    tape_path = OUT_DIR / f"{stem}.cassette.json"

    with tempfile.TemporaryDirectory(prefix="needle_bench_") as td:
        ws = Path(td)
        setup_workspace(ws)

        spec_file = ws / "SPECIFICATION.md"
        spec_size_kb = round(len(spec_file.read_bytes()) / 1024, 2)
        spec_lines = len(spec_file.read_text(encoding="utf-8").splitlines())

        print(f"\n================================================================================")
        print(f" NEEDLE-IN-A-HAYSTACK CONTEXT POLLUTION BENCHMARK")
        print(f" Target Manifest: {manifest}")
        print(f" Target Model:    {model}")
        print(f" Haystack Size:   {spec_size_kb} KB ({spec_lines} lines across 55 chapters)")
        print(f" Embedded Needle: Section {NEEDLE_SECTION} (Chapter {NEEDLE_CHAPTER})")
        print(f"================================================================================\n")

        baseline_pass, baseline_out = run_oracle_test(ws)
        if baseline_pass:
            raise RuntimeError("Baseline workspace unexpectedly passes oracle before agent runs!")

        cassette = Cassette()
        live_model = OpenRouterModel(model=model, stream=False, reasoning_effort="none")
        recorder = CassetteRecorder(cassette, delegate=live_model, output_path=tape_path)

        app = application_service(workspace=ws)
        manifest_p = ROOT / f"vanguard/packages/agency/manifests/{manifest}/manifest.json"

        start_time = time.monotonic()
        err = ""
        run_res = None
        try:
            run_res = app.run(
                brief=TASK_BRIEF,
                manifest_path=manifest_p,
                model=recorder,
                interactive=True,
                autonomous_approval=True,
                max_turns=max_turns,
            )
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-2000:]}"
        elapsed = round(time.monotonic() - start_time, 2)

        oracle_pass, oracle_out = run_oracle_test(ws)
        modified = sorted(
            str(p.relative_to(ws))
            for p in ws.rglob("*.py")
            if p.is_file() and not p.name.startswith("_oracle")
            and (p.name == "codec.py" or p.parent.name == "tests")
        )

        spend = sum(float(r.proposal.get("cost_usd") or 0) for r in cassette.records)
        status = "PASS" if oracle_pass else ("ERROR" if err else "FAIL")

        result = {
            "benchmark": "needle_in_a_haystack_context_pollution",
            "manifest": manifest,
            "model": model,
            "status": status,
            "oracle_pass": oracle_pass,
            "turns": getattr(run_res, "turns", 0) if run_res else 0,
            "llm_calls": len(cassette.records),
            "cost_usd": round(spend, 6),
            "latency_s": elapsed,
            "files_modified": modified,
            "haystack_size_kb": spec_size_kb,
            "haystack_lines": spec_lines,
            "needle_location": f"Chapter {NEEDLE_CHAPTER}, Section {NEEDLE_SECTION}",
            "terminal_state": getattr(run_res, "terminal_state", None) if run_res else None,
            "oracle_output": oracle_out[-2000:] if not oracle_pass else "ALL HIDDEN ASSERTIONS PASSED",
            "error": err,
            "cassette": str(tape_path.relative_to(ROOT)),
        }

        report_path = OUT_DIR / f"{stem}.report.json"
        report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

        print(f"\n--------------------------------------------------------------------------------")
        print(f" BENCHMARK RESULT: {status}")
        print(f" Oracle Verified:  {oracle_pass}")
        print(f" Total Spend:      ${spend:.6f}")
        print(f" LLM Calls:        {len(cassette.records)}")
        print(f" Execution Turns:  {result['turns']}")
        print(f" Latency:          {elapsed}s")
        print(f" Modified Files:   {modified}")
        print(f" Report Artifact:  {report_path.relative_to(ROOT)}")
        print(f"--------------------------------------------------------------------------------\n")
        return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Needle-In-A-Haystack Context Pollution Benchmark")
    ap.add_argument("--manifest", default="vg-code-max-v3luna", help="Target harness manifest")
    ap.add_argument("--model", default="deepseek/deepseek-v4-flash-0731", help="Target LLM model ID")
    ap.add_argument("--max-turns", type=int, default=15, help="Maximum turns allowed")
    ap.add_argument("--tag", default="needle_eval", help="Artifact tag")
    ap.add_argument("--budget-usd", type=float, default=0.03, help="Max budget ceiling in USD")
    args = ap.parse_args()

    res = run_needle_benchmark(
        manifest=args.manifest,
        model=args.model,
        max_turns=args.max_turns,
        tag=args.tag,
        budget_usd=args.budget_usd,
    )
    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
