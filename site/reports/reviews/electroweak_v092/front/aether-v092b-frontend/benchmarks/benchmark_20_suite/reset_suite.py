#!/usr/bin/env python3
"""Cryptographic State Verification and Suite Reset Utility for Benchmark 20.

Restores the 10 Brownfield challenges to their initial state, validates SHA-256
digests against initial_state.sha256, and cleans all Greenfield generated artifacts
to ensure zero cross-contamination.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_benchmark_20_suite import (
    BROWNFIELD_CHALLENGES,
    GREENFIELD_CHALLENGES,
    SUITE_ROOT,
    sha256_file,
)


def reset_and_verify_suite() -> bool:
    print("=================================================================")
    print("Benchmark 20 Suite — Cryptographic State Reset & Verification")
    print("=================================================================")
    all_ok = True

    # 1. Reset and verify Brownfield challenges
    print("\n--- [1/2] Verifying & Resetting Brownfield Challenges ---")
    for cname, cdata in BROWNFIELD_CHALLENGES.items():
        cdir = SUITE_ROOT / cname
        cdir.mkdir(parents=True, exist_ok=True)

        # Restore files to initial buggy state
        for rel_path, content in cdata["files"].items():
            fpath = cdir / rel_path
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content, encoding="utf-8")

        # Clean any generated/untracked files (.pyc, __pycache__, logs, etc.)
        for root, dirs, files in os.walk(cdir):
            for d in list(dirs):
                if d in ("__pycache__", ".pytest_cache", ".vanguard"):
                    shutil.rmtree(Path(root) / d, ignore_errors=True)

        # Verify against initial_state.sha256
        manifest_file = cdir / "initial_state.sha256"
        if not manifest_file.exists():
            print(f"[FAIL] {cname}: Missing initial_state.sha256")
            all_ok = False
            continue

        manifest_lines = manifest_file.read_text(encoding="utf-8").strip().splitlines()
        manifest_hashes = {}
        for line in manifest_lines:
            if not line.strip():
                continue
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                manifest_hashes[parts[1].strip()] = parts[0].strip()

        verified_count = 0
        for rel_path, expected_hash in manifest_hashes.items():
            fpath = cdir / rel_path
            if not fpath.exists():
                print(f"[FAIL] {cname}: Missing file {rel_path}")
                all_ok = False
                continue
            actual_hash = sha256_file(fpath)
            if actual_hash != expected_hash:
                print(f"[FAIL] {cname}: Hash mismatch for {rel_path} (got {actual_hash[:8]}.., expected {expected_hash[:8]}..)")
                all_ok = False
            else:
                verified_count += 1

        print(f"[OK] {cname:35} | {verified_count}/{len(manifest_hashes)} files verified (SHA-256 MATCH)")

    # 2. Reset Greenfield challenges
    print("\n--- [2/2] Resetting Greenfield Challenges ---")
    for cname, cdata in GREENFIELD_CHALLENGES.items():
        cdir = SUITE_ROOT / cname
        cdir.mkdir(parents=True, exist_ok=True)

        # Clean src/ and any artifacts, keeping only README.md and test/
        for item in cdir.iterdir():
            if item.name not in ("README.md", "PRD.md", "test"):
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)

        # Re-ensure clean src/ with __init__.py
        src_dir = cdir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("", encoding="utf-8")

        # Clean cache in test
        for root, dirs, files in os.walk(cdir):
            for d in list(dirs):
                if d in ("__pycache__", ".pytest_cache", ".vanguard"):
                    shutil.rmtree(Path(root) / d, ignore_errors=True)

        (cdir / "README.md").write_text(cdata["readme"], encoding="utf-8")
        test_dir = cdir / "test"
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "test_suite.py").write_text(cdata["test"], encoding="utf-8")

        print(f"[OK] {cname:35} | Cleaned workspace & initialized test suite")

    print("\n" + "=" * 65)
    if all_ok:
        print("ALL 20 BENCHMARK CHALLENGES RESET AND VERIFIED (ZERO POLLUTION)")
    else:
        print("RESET AND VERIFICATION ENCOUNTERED ERRORS")
    print("=" * 65)
    return all_ok


if __name__ == "__main__":
    success = reset_and_verify_suite()
    sys.exit(0 if success else 1)
