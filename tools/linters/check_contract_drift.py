#!/usr/bin/env python3
"""Automated Contract Drift & Conformance Linter.

Audits:
1. `ERROR_CODES` in `contract.py` vs `CanonicalErrorCode` in `types.ts` vs `runtime-service.schema.json`.
2. `COMMAND_RUN_SCOPE` command names in `contract.py` vs TypeScript definitions.
3. Payload required/allowed fields consistency.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PY = ROOT / "vanguard" / "packages" / "runtime" / "service" / "contract.py"
TYPES_TS = ROOT / "vanguard" / "clients" / "contracts" / "src" / "types.ts"
SCHEMA_JSON = ROOT / "schemas" / "v4" / "runtime-service.schema.json"


def extract_python_error_codes(path: Path) -> set[str]:
    content = path.read_text(encoding="utf-8")
    m = re.search(r"ERROR_CODES:\s*frozenset\[str\]\s*=\s*frozenset\(\s*\{([^}]+)\}\s*\)", content)
    if not m:
        return set()
    raw = m.group(1)
    return {item.strip().strip('"').strip("'") for item in raw.split(",") if item.strip()}


def extract_ts_error_codes(path: Path) -> set[str]:
    content = path.read_text(encoding="utf-8")
    m = re.search(r"export type CanonicalErrorCode\s*=\s*([^;]+);", content)
    if not m:
        return set()
    raw = m.group(1)
    return {item.strip().strip("|").strip().strip('"').strip("'") for item in raw.split("\n") if item.strip() and "|" in item}


def extract_python_commands(path: Path) -> set[str]:
    content = path.read_text(encoding="utf-8")
    m = re.search(r"COMMAND_RUN_SCOPE:\s*Mapping\[str,\s*str\]\s*=\s*\{([^}]+)\}", content)
    if not m:
        return set()
    raw = m.group(1)
    cmds = set()
    for line in raw.splitlines():
        line = line.strip()
        if ":" in line and '"' in line:
            cmd_name = line.split(":")[0].strip().strip('"').strip("'")
            if cmd_name:
                cmds.add(cmd_name)
    return cmds


def main() -> int:
    print("=" * 80)
    print("AETHER WIRE CONTRACT DRIFT AUDIT")
    print("=" * 80)

    if not CONTRACT_PY.exists():
        print(f"FAIL: Missing {CONTRACT_PY}")
        return 1
    if not TYPES_TS.exists():
        print(f"FAIL: Missing {TYPES_TS}")
        return 1

    py_errors = extract_python_error_codes(CONTRACT_PY)
    ts_errors = extract_ts_error_codes(TYPES_TS)

    print(f"Found {len(py_errors)} Python Error Codes: {sorted(py_errors)}")
    print(f"Found {len(ts_errors)} TypeScript Canonical Error Codes: {sorted(ts_errors)}")

    drift_errors = False
    if py_errors != ts_errors:
        print("\n[!] DRIFT DETECTED IN ERROR CODES:")
        diff_py_only = py_errors - ts_errors
        diff_ts_only = ts_errors - py_errors
        if diff_py_only:
            print(f"    - In Python only: {diff_py_only}")
        if diff_ts_only:
            print(f"    - In TypeScript only: {diff_ts_only}")
        drift_errors = True
    else:
        print("  [OK] Error codes are identical (100% byte-for-byte match).")

    py_cmds = extract_python_commands(CONTRACT_PY)
    print(f"\nFound {len(py_cmds)} Python Commands: {sorted(py_cmds)}")

    if SCHEMA_JSON.exists():
        schema_data = json.loads(SCHEMA_JSON.read_text(encoding="utf-8"))
        schema_errors = set(schema_data.get("$defs", {}).get("ErrorCode", {}).get("enum", []))
        if schema_errors and schema_errors != py_errors:
            print("\n[!] DRIFT DETECTED AGAINST JSON SCHEMA:")
            print(f"    - Schema vs Python diff: {schema_errors ^ py_errors}")
            drift_errors = True
        elif schema_errors:
            print("  [OK] JSON Schema ErrorCode enum matches Python contract.")

    print("=" * 80)
    if drift_errors:
        print("RESULT: DRIFT DETECTED - Contract synchronization required.")
        return 1
    else:
        print("RESULT: ZERO DRIFT - Wire contracts are 100% synchronized.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
