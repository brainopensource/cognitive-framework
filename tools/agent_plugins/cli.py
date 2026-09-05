#!/usr/bin/env python3
"""Unified CLI for Vanguard / AETHER Agent Capabilities.

Provides developer and agent ergonomics to inspect, compose, and execute:
- Skills (Atomic)
- Techniques (Open-loop composition)
- Proficiencies (Closed-loop SWE feedback engines)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import subprocess
from typing import Sequence

from vanguard.packages.runtime.agent_plugins import (
    PluginSpec,
    build_plugin_index,
    filter_plugins,
    load_agent_plugins,
)


def execute_plugin(
    plugin: PluginSpec,
    args: Sequence[str],
    *,
    cwd: Path | str | None = None,
    timeout: float = 60.0,
) -> subprocess.CompletedProcess[str]:
    """Executes the plugin runner script in an isolated process with timeout protection."""
    if not plugin.runner_path:
        raise ValueError(f"Plugin '{plugin.name}' does not have an executable runner script.")

    runner_file = Path(plugin.runner_path)
    if not runner_file.is_absolute():
        root = Path(cwd) if cwd else REPO_ROOT
        runner_file = root / runner_file

    cmd = ["python3", str(runner_file)] + list(args)
    return subprocess.run(
        cmd,
        cwd=str(cwd or runner_file.parents[2]),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def cmd_list(args: argparse.Namespace) -> int:
    plugins = load_agent_plugins(REPO_ROOT)
    if args.category:
        plugins = filter_plugins(plugins, categories=[args.category])

    if args.json:
        data = [
            {
                "name": p.name,
                "category": p.category,
                "mode": p.mode,
                "description": p.description,
                "doc_path": p.doc_path,
                "runner_path": p.runner_path,
                "composes_skills": p.composes_skills,
                "composes_techniques": p.composes_techniques,
            }
            for p in plugins
        ]
        print(json.dumps(data, indent=2))
        return 0

    print("=" * 80)
    print(f"VANGUARD / AETHER AGENT CAPABILITY CATALOG ({len(plugins)} registered)")
    print("=" * 80)
    print(f"| {'Name':<24} | {'Category':<12} | {'Mode':<12} | {'Runner':<8} |")
    print(f"|{'-'*26}|{'-'*14}|{'-'*14}|{'-'*10}|")
    for p in plugins:
        runner_sym = "YES ✔" if p.runner_path else "NO ○"
        print(f"| {p.name:<24} | {p.category.upper():<12} | {p.mode:<12} | {runner_sym:<8} |")
    print("=" * 80)
    return 0


def cmd_prefix(args: argparse.Namespace) -> int:
    plugins = load_agent_plugins(REPO_ROOT)
    if args.category:
        plugins = filter_plugins(plugins, categories=[args.category])
    index = build_plugin_index(plugins, budget_chars=args.budget)

    if args.json:
        print(json.dumps({
            "size_chars": index.size_chars,
            "budget_chars": index.budget_chars,
            "dropped": index.dropped,
            "rendered": index.render(),
        }, indent=2))
    else:
        print(f"=== Frozen Prompt Prefix ({index.size_chars}/{index.budget_chars} chars) ===")
        if index.dropped:
            print(f"Dropped due to ceiling: {index.dropped}")
        print("\n" + index.render())
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    plugins = load_agent_plugins(REPO_ROOT)
    matched = filter_plugins(plugins, names=[args.plugin])
    if not matched:
        print(f"Error: Plugin '{args.plugin}' not found.", file=sys.stderr)
        return 1

    plugin = matched[0]
    if not plugin.runner_path:
        print(f"Error: Plugin '{plugin.name}' has no executable runner.", file=sys.stderr)
        return 1

    proc = execute_plugin(plugin, args.plugin_args, cwd=REPO_ROOT, timeout=args.timeout)
    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    return proc.returncode


def cmd_autofix(args: argparse.Namespace) -> int:
    plugins = load_agent_plugins(REPO_ROOT)
    matched = filter_plugins(plugins, names=["autofix-swe-loop"])
    if not matched:
        print("Error: autofix-swe-loop proficiency not found.", file=sys.stderr)
        return 1

    autofix_args = ["--task", args.task, "--target-file", args.target_file, "--max-turns", str(args.max_turns)]
    if args.test_cmd:
        autofix_args.extend(["--test-cmd", args.test_cmd])
    if args.json:
        autofix_args.append("--json")

    proc = execute_plugin(matched[0], autofix_args, cwd=REPO_ROOT, timeout=args.timeout)
    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    return proc.returncode


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified CLI for Vanguard / AETHER Agent Capabilities",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = subparsers.add_parser("list", help="List all skills, techniques, and proficiencies")
    p_list.add_argument("--category", choices=["skill", "technique", "proficiency"], help="Filter by category")
    p_list.add_argument("--json", action="store_true", help="Output as JSON")
    p_list.set_defaults(func=cmd_list)

    # prefix
    p_prefix = subparsers.add_parser("prefix", help="Compile frozen prefix index within character budget")
    p_prefix.add_argument("--category", choices=["skill", "technique", "proficiency"], help="Filter by category")
    p_prefix.add_argument("--budget", type=int, default=4096, help="Character ceiling (default: 4096)")
    p_prefix.add_argument("--json", action="store_true", help="Output as JSON")
    p_prefix.set_defaults(func=cmd_prefix)

    # run
    p_run = subparsers.add_parser("run", help="Execute runner for a specific capability")
    p_run.add_argument("plugin", help="Name of plugin to execute")
    p_run.add_argument("--timeout", type=float, default=60.0, help="Execution timeout in seconds")
    p_run.add_argument("plugin_args", nargs=argparse.REMAINDER, help="Arguments passed to runner")
    p_run.set_defaults(func=cmd_run)

    # autofix shortcut
    p_fix = subparsers.add_parser("autofix", help="Execute autonomous closed-loop SWE repair")
    p_fix.add_argument("--task", required=True, help="Task or defect explanation")
    p_fix.add_argument("--target-file", required=True, help="Target file path to repair")
    p_fix.add_argument("--test-cmd", help="Explicit test command")
    p_fix.add_argument("--max-turns", type=int, default=3, help="Max repair iterations")
    p_fix.add_argument("--timeout", type=float, default=60.0, help="Per-turn timeout")
    p_fix.add_argument("--json", action="store_true", help="Output as JSON")
    p_fix.set_defaults(func=cmd_autofix)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
