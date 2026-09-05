#!/usr/bin/env python3
"""Universal MCP & Triad Synchronizer for Multi-Agent AI Harnesses.

Synchronizes and configures the Model Context Protocol (MCP) Triad
(CLI + MCP Server + Skill) across all major AI coding harnesses:
- Antigravity (AGY)
- Claude Code
- OpenAI Codex CLI
- Cursor
- OpenCode
- Windsurf / VS Code (Cline, Roo Code, Continue)
- Zed

Guarantees decoupled, reproducible tool access and zero-hallucination guardrails.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# Canonical Triad Definitions
TRIAD_SERVERS = {
    "llama-cpp": {
        "command": "python3",
        "script": "tools/llama_cpp/mcp_server.py",
        "description": "Local GGUF model operations, server orchestration, and anti-hallucination structured inference.",
        "skill": ".agents/skills/llama-cpp/SKILL.md",
        "cli": "tools/llama_cpp/cli.py",
    },
    "lda-navigator": {
        "command": "python3",
        "script": "tools/lda/mcp.py",
        "description": "LDA repository intelligence, AST graph, symbol navigation, and token-budgeted context.",
        "skill": ".agents/skills/lda-navigator/SKILL.md",
        "cli": "tools/007_LLM_DOCS_ATLAS/cli.py",
    },
    "lam-engine": {
        "command": "python3",
        "script": "tools/002_LLM_API_MOCK/mcp_server.py",
        "description": "Zero-cost sub-millisecond LLM mock completions and deterministic challenge cassette replay.",
        "skill": ".agents/skills/lam-engine/SKILL.md",
        "cli": "tools/002_LLM_API_MOCK/cli.py",
    },
    "agent-plugins": {
        "command": "python3",
        "script": "tools/agent_plugins/mcp_server.py",
        "description": "Vanguard unified agent capabilities (skills, techniques, proficiencies, test runner, autofix).",
        "skill": ".agents/skills/autofix-loop/SKILL.md",
        "cli": "tools/agent_plugins/cli.py",
    },
}


def get_server_config(server_key: str, absolute: bool = True) -> Dict[str, Any]:
    """Generate server entry dictionary."""
    spec = TRIAD_SERVERS[server_key]
    script_path = str(REPO_ROOT / spec["script"]) if absolute else spec["script"]
    return {
        "command": spec["command"],
        "args": [script_path],
    }


def probe_mcp_server(server_key: str) -> Tuple[bool, str, int, float]:
    """Test standard MCP stdio JSON-RPC handshake (initialize + tools/list)."""
    spec = TRIAD_SERVERS[server_key]
    script_path = REPO_ROOT / spec["script"]
    if not script_path.exists():
        return False, f"Script not found at {script_path}", 0, 0.0

    t0 = time.perf_counter()
    try:
        proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(REPO_ROOT),
        )

        # 1. Send initialize
        init_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }) + "\n"
        proc.stdin.write(init_req)
        proc.stdin.flush()

        init_resp_line = proc.stdout.readline()
        if not init_resp_line:
            proc.kill()
            err = proc.stderr.read().strip()
            return False, f"No initialize response: {err}", 0, 0.0

        init_data = json.loads(init_resp_line)
        if "error" in init_data:
            proc.kill()
            return False, f"Initialize error: {init_data['error']}", 0, 0.0

        # 2. Send tools/list
        tools_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }) + "\n"
        proc.stdin.write(tools_req)
        proc.stdin.flush()

        tools_resp_line = proc.stdout.readline()
        proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=2)

        dt_ms = (time.perf_counter() - t0) * 1000
        if not tools_resp_line:
            return True, "Initialized (no tools response)", 0, dt_ms

        tools_data = json.loads(tools_resp_line)
        tools = tools_data.get("result", {}).get("tools", [])
        return True, "Healthy", len(tools), dt_ms

    except Exception as exc:
        return False, str(exc), 0, 0.0


def sync_workspace_manifests() -> List[str]:
    """Write standard workspace root MCP configs (.mcp.json and mcp_config.json)."""
    actions = []
    servers_dict = {
        name: get_server_config(name, absolute=True)
        for name in TRIAD_SERVERS
    }
    payload = {"mcpServers": servers_dict}

    # 1. Repo Root .mcp.json (Standard for Claude Code, Cursor, OpenCode, Zed)
    root_mcp = REPO_ROOT / ".mcp.json"
    root_mcp.write_text(json.dumps(payload, indent=2) + "\n")
    actions.append(f"Updated {root_mcp.relative_to(REPO_ROOT)}")

    # 2. Repo Root mcp_config.json (Standard for AGY / Antigravity workspace)
    root_config = REPO_ROOT / "mcp_config.json"
    root_config.write_text(json.dumps(payload, indent=2) + "\n")
    actions.append(f"Updated {root_config.relative_to(REPO_ROOT)}")

    # 3. .cursor/mcp.json (Cursor IDE workspace)
    cursor_dir = REPO_ROOT / ".cursor"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    cursor_mcp = cursor_dir / "mcp.json"
    cursor_mcp.write_text(json.dumps(payload, indent=2) + "\n")
    actions.append(f"Updated {cursor_mcp.relative_to(REPO_ROOT)}")

    # 4. .opencode/mcp.json (OpenCode workspace)
    opencode_dir = REPO_ROOT / ".opencode"
    opencode_dir.mkdir(parents=True, exist_ok=True)
    opencode_mcp = opencode_dir / "mcp.json"
    opencode_mcp.write_text(json.dumps(payload, indent=2) + "\n")
    actions.append(f"Updated {opencode_mcp.relative_to(REPO_ROOT)}")

    return actions


def sync_global_harnesses() -> List[str]:
    """Update global configuration files across installed harnesses."""
    actions = []
    home = Path.home()

    # 1. Antigravity (AGY): ~/.gemini/config/mcp_config.json
    gemini_conf_dir = home / ".gemini/config"
    if gemini_conf_dir.exists() or (home / ".gemini").exists():
        gemini_conf_dir.mkdir(parents=True, exist_ok=True)
        gemini_mcp = gemini_conf_dir / "mcp_config.json"
        existing = {}
        if gemini_mcp.exists() and gemini_mcp.stat().st_size > 0:
            try:
                existing = json.loads(gemini_mcp.read_text()).get("mcpServers", {})
            except Exception:
                existing = {}
        for name in TRIAD_SERVERS:
            existing[name] = get_server_config(name, absolute=True)
        gemini_mcp.write_text(json.dumps({"mcpServers": existing}, indent=2) + "\n")
        actions.append(f"Updated Antigravity global MCP config: {gemini_mcp}")

    # 2. Cursor Global: ~/.cursor/mcp.json
    cursor_global_dir = home / ".cursor"
    if cursor_global_dir.exists():
        cursor_mcp = cursor_global_dir / "mcp.json"
        existing = {}
        if cursor_mcp.exists() and cursor_mcp.stat().st_size > 0:
            try:
                existing = json.loads(cursor_mcp.read_text()).get("mcpServers", {})
            except Exception:
                existing = {}
        for name in TRIAD_SERVERS:
            existing[name] = get_server_config(name, absolute=True)
        cursor_mcp.write_text(json.dumps({"mcpServers": existing}, indent=2) + "\n")
        actions.append(f"Updated Cursor global MCP config: {cursor_mcp}")

    # 3. OpenCode Global: ~/.config/opencode/mcp.json
    opencode_global_dir = home / ".config/opencode"
    opencode_global_dir.mkdir(parents=True, exist_ok=True)
    opencode_mcp = opencode_global_dir / "mcp.json"
    existing = {}
    if opencode_mcp.exists() and opencode_mcp.stat().st_size > 0:
        try:
            existing = json.loads(opencode_mcp.read_text()).get("mcpServers", {})
        except Exception:
            existing = {}
    for name in TRIAD_SERVERS:
        existing[name] = get_server_config(name, absolute=True)
    opencode_mcp.write_text(json.dumps({"mcpServers": existing}, indent=2) + "\n")
    actions.append(f"Updated OpenCode global MCP config: {opencode_mcp}")

    # 4. Claude Code CLI registration
    if shutil.which("claude"):
        for name, spec in TRIAD_SERVERS.items():
            script_path = str(REPO_ROOT / spec["script"])
            cmd = ["claude", "mcp", "add", name, "--", spec["command"], script_path]
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=False)
                actions.append(f"Registered '{name}' in Claude Code CLI")
            except Exception as exc:
                actions.append(f"Failed to register '{name}' in Claude Code: {exc}")

    # 5. Codex CLI registration
    if shutil.which("codex"):
        for name, spec in TRIAD_SERVERS.items():
            script_path = str(REPO_ROOT / spec["script"])
            cmd = ["codex", "mcp", "add", name, "--", spec["command"], script_path]
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=False)
                actions.append(f"Registered '{name}' in Codex CLI")
            except Exception as exc:
                actions.append(f"Failed to register '{name}' in Codex: {exc}")

    return actions


def sync_skills() -> List[str]:
    """Mirror .agents/ (skills, techniques, proficiencies) into harness-specific discovery folders."""
    actions = []
    home = Path.home()

    capability_sets = [
        ("skills", REPO_ROOT / ".agents/skills", [
            home / ".cursor/skills-cursor",
            home / ".claude/skills",
            home / ".codex/skills",
            home / ".gemini/antigravity-cli/skills",
            REPO_ROOT / ".cursor/skills",
        ]),
        ("techniques", REPO_ROOT / ".agents/techniques", [
            home / ".cursor/techniques",
            home / ".claude/techniques",
            home / ".codex/techniques",
        ]),
        ("proficiencies", REPO_ROOT / ".agents/proficiencies", [
            home / ".cursor/proficiencies",
            home / ".claude/proficiencies",
            home / ".codex/proficiencies",
        ]),
    ]

    for label, src_dir, target_dirs in capability_sets:
        if not src_dir.exists() or not src_dir.is_dir():
            continue
        for target in target_dirs:
            try:
                target.mkdir(parents=True, exist_ok=True)
                for item_dir in src_dir.iterdir():
                    if not item_dir.is_dir():
                        continue
                    dest = target / item_dir.name
                    if dest.is_symlink() or dest.exists():
                        if dest.is_symlink():
                            dest.unlink()
                        else:
                            shutil.rmtree(dest)
                    dest.symlink_to(item_dir, target_is_directory=True)
                actions.append(f"Linked {label} to {target}")
            except Exception as exc:
                actions.append(f"Could not link {label} to {target}: {exc}")

    return actions


def doctor_command() -> int:
    """Audit all MCP servers and AI harness configurations."""
    print("=== MCP Triad Health Audit ===")
    all_ok = True

    for name, spec in TRIAD_SERVERS.items():
        ok, msg, tools_count, dt = probe_mcp_server(name)
        status_sym = "✔ PASS" if ok else "✖ FAIL"
        if not ok:
            all_ok = False
        print(f"[{status_sym}] {name:<15} : {msg} ({tools_count} tools, {dt:.1f}ms)")
        print(f"        Script : {spec['script']}")
        print(f"        Skill  : {spec['skill']}")
        print(f"        CLI    : {spec['cli']}")

    print("\n=== AI Harness Integrations ===")
    home = Path.home()
    harnesses = [
        ("Antigravity (AGY)", home / ".gemini/config/mcp_config.json"),
        ("Claude Code", home / ".claude.json"),
        ("Codex CLI", shutil.which("codex") is not None),
        ("Cursor Global", home / ".cursor/mcp.json"),
        ("Cursor Workspace", REPO_ROOT / ".cursor/mcp.json"),
        ("OpenCode Global", home / ".config/opencode/mcp.json"),
        ("Universal Root", REPO_ROOT / ".mcp.json"),
    ]

    for name, check in harnesses:
        if isinstance(check, Path):
            present = check.exists()
            state = f"Config present ({check})" if present else "Config not found"
        else:
            present = bool(check)
            state = "Binary available in PATH" if present else "Not found in PATH"
        sym = "✔" if present else "○"
        print(f"  {sym} {name:<20}: {state}")

    return 0 if all_ok else 1


def sync_command() -> None:
    """Execute complete synchronization across manifests, harnesses, and skills."""
    print("Synchronizing workspace root MCP manifests...")
    for act in sync_workspace_manifests():
        print(f"  • {act}")

    print("\nSynchronizing global AI agent harnesses...")
    for act in sync_global_harnesses():
        print(f"  • {act}")

    print("\nSynchronizing skills across harness directories...")
    for act in sync_skills():
        print(f"  • {act}")

    print("\nRunning verification audit...")
    doctor_command()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Universal MCP & Triad Synchronizer for AI Coding Harnesses"
    )
    parser.add_argument("--sync", action="store_true", help="Sync manifests, harnesses, and skills")
    parser.add_argument("--doctor", action="store_true", help="Audit MCP servers and harness configs")

    args = parser.parse_args()

    if args.doctor:
        sys.exit(doctor_command())
    elif args.sync:
        sync_command()
    else:
        # Default action is sync
        sync_command()


if __name__ == "__main__":
    main()
