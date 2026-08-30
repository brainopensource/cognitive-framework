#!/usr/bin/env python3
"""AETHER — Release Candidate & Native Installer Builder.

Compiles and packages AETHER into a self-contained, private, production-ready
distribution tarball and installer that runs cleanly on desktops without
development dependencies, Git checkouts, or repository access.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tarfile
from pathlib import Path

VERSION = "0.9.1-rc1"
PRODUCT_NAME = "aether"
DIST_NAME = f"{PRODUCT_NAME}-{VERSION}"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print(f"[build_rc] Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=cwd, check=True)


def build_rc() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    dist_root = repo_root / "dist"
    target_dir = dist_root / DIST_NAME

    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"[build_rc] Building AETHER version {VERSION} into {target_dir}...")

    # 1. Build all frontend packages
    print("[build_rc] Compiling TypeScript workspaces...")
    run(["npm", "run", "build"], cwd=repo_root)

    # 2. Copy Python Runtime (pure production code)
    print("[build_rc] Bundling Python runtime...")
    runtime_dest = target_dir / "lib" / "vanguard" / "packages"
    runtime_dest.mkdir(parents=True, exist_ok=True)

    packages_src = repo_root / "vanguard" / "packages"
    for pkg in ["domain", "ports", "kernel", "agency", "runtime", "adapters"]:
        src = packages_src / pkg
        if src.exists():
            shutil.copytree(src, runtime_dest / pkg, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "test*", "tests*"))

    # Copy vanguard __init__.py
    vanguard_init_src = repo_root / "vanguard" / "__init__.py"
    vanguard_init_dest = target_dir / "lib" / "vanguard" / "__init__.py"
    vanguard_init_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(vanguard_init_src, vanguard_init_dest)

    # 3. Copy Compiled Client Packages & node_modules
    print("[build_rc] Bundling compiled JS/UI packages...")
    clients_dest = target_dir / "lib" / "vanguard" / "clients"
    clients_dest.mkdir(parents=True, exist_ok=True)

    clients_src = repo_root / "vanguard" / "clients"
    for client in ["contracts", "client", "projections", "ui-web", "cli", "tui", "desktop", "lab", "client-core", "studio"]:
        src = clients_src / client
        if src.exists():
            dest = clients_dest / client
            dest.mkdir(parents=True, exist_ok=True)
            # Copy package.json
            shutil.copy2(src / "package.json", dest / "package.json")
            # Copy dist/
            if (src / "dist").exists():
                shutil.copytree(src / "dist", dest / "dist")
            # Copy fixtures/
            if (src / "fixtures").exists():
                shutil.copytree(src / "fixtures", dest / "fixtures")
            # Copy HTML files if present
            for html in src.glob("*.html"):
                shutil.copy2(html, dest / html.name)

    # Copy root node_modules needed for runtime (ink, react, etc.)
    if (repo_root / "node_modules").exists():
        print("[build_rc] Bundling runtime node_modules...")
        shutil.copytree(
            repo_root / "node_modules",
            target_dir / "lib" / "node_modules",
            ignore=shutil.ignore_patterns(".cache", "*.ts", "*.map"),
            symlinks=True,
        )

    # 4. Copy Schemas
    print("[build_rc] Bundling canonical schemas...")
    schemas_src = repo_root / "schemas"
    if schemas_src.exists():
        shutil.copytree(schemas_src, target_dir / "schemas")

    # 5. Generate Production Binaries
    print("[build_rc] Generating binary wrappers...")
    bin_dest = target_dir / "bin"
    bin_dest.mkdir(parents=True, exist_ok=True)

    # aether CLI wrapper
    aether_cli_content = """#!/usr/bin/env node
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const appRoot = resolve(__dirname, "..");
process.env.AETHER_HOME = appRoot;
process.env.NODE_PATH = resolve(appRoot, "lib", "node_modules");

const cliMain = resolve(appRoot, "lib", "vanguard", "clients", "cli", "dist", "src", "main.js");
import(cliMain).catch((err) => {
  console.error("[AETHER CLI] Fatal initialization error:", err);
  process.exit(1);
});
"""
    cli_file = bin_dest / "aether"
    cli_file.write_text(aether_cli_content, encoding="utf-8")
    cli_file.chmod(cli_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # aether-tui wrapper
    aether_tui_content = """#!/usr/bin/env node
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const appRoot = resolve(__dirname, "..");
process.env.AETHER_HOME = appRoot;
process.env.NODE_PATH = resolve(appRoot, "lib", "node_modules");

const tuiMain = resolve(appRoot, "lib", "vanguard", "clients", "tui", "dist", "src", "main.js");
import(tuiMain).catch((err) => {
  console.error("[AETHER TUI] Fatal initialization error:", err);
  process.exit(1);
});
"""
    tui_file = bin_dest / "aether-tui"
    tui_file.write_text(aether_tui_content, encoding="utf-8")
    tui_file.chmod(tui_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # 6. Generate Desktop Application Launcher (.desktop file)
    print("[build_rc] Generating freedesktop launcher entry...")
    apps_dest = target_dir / "share" / "applications"
    apps_dest.mkdir(parents=True, exist_ok=True)
    desktop_entry = f"""[Desktop Entry]
Name=AETHER
Comment=Self-Contained Recursive Agent Cockpit & Execution Environment
Exec=/opt/aether/bin/aether-desktop
Terminal=false
Type=Application
Categories=Development;IDE;
Icon=aether
StartupWMClass=aether-desktop
"""
    (apps_dest / "aether.desktop").write_text(desktop_entry, encoding="utf-8")

    # 7. Generate Installer script (install.sh)
    print("[build_rc] Creating native install script...")
    install_script = """#!/usr/bin/env bash
set -euo pipefail

PREFIX="${1:-$HOME/.local}"
INSTALL_DIR="$PREFIX/lib/aether"
BIN_DIR="$PREFIX/bin"
DESKTOP_DIR="$PREFIX/share/applications"

echo "==> Installing AETHER 0.9.1-rc1 to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$DESKTOP_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy files
cp -r "$SCRIPT_DIR/bin" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/lib" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/schemas" "$INSTALL_DIR/"

# Symlink binaries
ln -sf "$INSTALL_DIR/bin/aether" "$BIN_DIR/aether"
ln -sf "$INSTALL_DIR/bin/aether-tui" "$BIN_DIR/aether-tui"

# Install .desktop launcher
if [ -d "$SCRIPT_DIR/share/applications" ]; then
  cp "$SCRIPT_DIR/share/applications/aether.desktop" "$DESKTOP_DIR/"
fi

# Ensure user data directories exist with 0700 permissions
mkdir -p "$HOME/.config/aether" "$HOME/.local/share/aether" "$HOME/.local/state/aether"
chmod 700 "$HOME/.config/aether" "$HOME/.local/share/aether" "$HOME/.local/state/aether"

echo "==> AETHER 0.9.1-rc1 installed successfully!"
echo "    CLI: $BIN_DIR/aether"
echo "    TUI: $BIN_DIR/aether-tui"
"""
    install_file = target_dir / "install.sh"
    install_file.write_text(install_script, encoding="utf-8")
    install_file.chmod(install_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # 8. Generate Uninstaller script (uninstall.sh)
    print("[build_rc] Creating clean uninstaller script...")
    uninstall_script = """#!/usr/bin/env bash
set -euo pipefail

PREFIX="${1:-$HOME/.local}"
INSTALL_DIR="$PREFIX/lib/aether"
BIN_DIR="$PREFIX/bin"
DESKTOP_DIR="$PREFIX/share/applications"

echo "==> Uninstalling AETHER from $INSTALL_DIR..."
rm -rf "$INSTALL_DIR"
rm -f "$BIN_DIR/aether"
rm -f "$BIN_DIR/aether-tui"
rm -f "$DESKTOP_DIR/aether.desktop"

echo "==> AETHER application removed."
echo "    Note: User configuration and data in ~/.config/aether and ~/.local/share/aether were preserved."
echo "    To delete user data as well, run: rm -rf ~/.config/aether ~/.local/share/aether ~/.local/state/aether"
"""
    uninstall_file = target_dir / "uninstall.sh"
    uninstall_file.write_text(uninstall_script, encoding="utf-8")
    uninstall_file.chmod(uninstall_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # 9. Package Release Candidate Tarball
    print(f"[build_rc] Creating tarball: dist/{DIST_NAME}.tar.gz...")
    tar_path = dist_root / f"{DIST_NAME}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(target_dir, arcname=DIST_NAME)

    print(f"[build_rc] Release candidate build completed: {tar_path} ({tar_path.stat().st_size} bytes)")
    return tar_path


if __name__ == "__main__":
    build_rc()
