#!/usr/bin/env python3
"""I-6: proc.exec plugins must declare container or subprocess isolation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import repo_root
from simple_yaml import YamlError, load

_ALLOWED_ISOLATION = {"container", "subprocess"}


def _has_proc_exec(capabilities: object) -> bool:
    if not isinstance(capabilities, list):
        return False
    for item in capabilities:
        if isinstance(item, dict) and str(item.get("verb")) == "proc.exec":
            return True
    return False


def scan(packs_root: Path) -> list[str]:
    errors: list[str] = []
    if not packs_root.is_dir():
        return [f"missing packs directory: {packs_root}"]
    for path in sorted(packs_root.rglob("*.yaml")):
        try:
            data = load(path.read_text(encoding="utf-8"))
        except (OSError, YamlError) as exc:
            errors.append(f"{path}: cannot parse plugin.yaml ({exc})")
            continue
        if not isinstance(data, dict) or data.get("api") != "mhf.plugin/1":
            continue
        if not _has_proc_exec(data.get("capabilities")):
            continue
        isolation = data.get("isolation")
        if isolation not in _ALLOWED_ISOLATION:
            rel = path.as_posix()
            errors.append(
                f"{rel}: proc.exec requires isolation in {_ALLOWED_ISOLATION}, got {isolation!r}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--expect-fail", action="store_true")
    args = parser.parse_args()
    repo = args.root.resolve() if args.root is not None else repo_root()
    errors = scan(repo / "packs")
    if args.expect_fail:
        if errors:
            print(f"ISOLATION POLICY FIXTURE FAIL-CLOSED: {len(errors)} violation(s)")
            return 0
        print("ISOLATION POLICY FIXTURE MISS: expected a violation, found none")
        return 1
    if errors:
        for error in errors:
            print(f"ISOLATION POLICY FAIL: {error}")
        return 1
    print("ISOLATION POLICY PASS: proc.exec plugins declare container/subprocess")
    return 0


if __name__ == "__main__":
    sys.exit(main())
