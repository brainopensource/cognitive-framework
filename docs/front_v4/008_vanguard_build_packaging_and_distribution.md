# Vanguard Build, Packaging & Multi-Platform Distribution

**Document ID:** `VG-FE-008`  
**Version:** `0.4.1-beta`  
**Status:** `Normative / Authoritative`  
**Owner:** `DevOps & Release Engineering Lead`  
**Targets:** `npm`, `PyPI`, `Standalone Shell Installer (curl | sh)`, `Desktop Single-Binary`

---

## 1. Distribution Strategy Overview

To maximize developer adoption while supporting non-technical enterprise users, Vanguard provides three frictionless distribution tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DISTRIBUTION CHANNELS                           │
├──────────────────────────┬───────────────────────┬─────────────────────┤
│ 1. Zero-Prereq One-Liner │ 2. Package Managers   │ 3. Standalone Apps  │
│    curl | sh             │    npm install -g @vg │    Tauri / Desktop  │
│    (Recommended)         │    pip install vg     │    (Enterprise MSI) │
└──────────────────────────┴───────────────────────┴─────────────────────┘
```

---

## 2. Channel 1: The Zero-Prerequisite One-Liner (`curl | sh`)

Users do not need Python or Node pre-installed. The shell installer downloads a self-contained archive containing pre-compiled binaries and embedded runtimes:

```bash
curl -fsSL https://vanguard.ai/install.sh | sh
```

### Complete `install.sh` Reference Implementation
```bash
#!/usr/bin/env bash
set -e

REPO="vanguard-ai/vanguard"
INSTALL_DIR="$HOME/.vanguard"
BIN_DIR="$INSTALL_DIR/bin"
mkdir -p "$BIN_DIR"

OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$ARCH" in
  x86_64) ARCH="x64" ;;
  aarch64|arm64) ARCH="arm64" ;;
  *) echo "Unsupported architecture: $ARCH" && exit 1 ;;
esac

RELEASE_TAG=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
TARBALL_URL="https://github.com/$REPO/releases/download/$RELEASE_TAG/vanguard-${OS}-${ARCH}.tar.gz"

echo "📦 Downloading Vanguard ($RELEASE_TAG) for ${OS}-${ARCH}..."
curl -fsSL "$TARBALL_URL" | tar -xz -C "$INSTALL_DIR"

# Ensure binary is executable
chmod +x "$BIN_DIR/vg"

# Add to PATH
SHELL_CONFIG="$HOME/.bashrc"
if [[ "$SHELL" == */zsh ]]; then
  SHELL_CONFIG="$HOME/.zshrc"
fi

if ! grep -q "$BIN_DIR" "$SHELL_CONFIG"; then
  echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_CONFIG"
  echo "✨ Added $BIN_DIR to $SHELL_CONFIG"
fi

echo "🚀 Vanguard successfully installed! Run 'vg' to start coding."
```

---

## 3. Channel 2: Global NPM Package (`@vanguard/cli`)

Published directly to the public npm registry:

```bash
# Developer installation
npm install -g @vanguard/cli

# Run immediately
vg
```

### Automatic Daemon Management in CLI
When `vg` is invoked, [`daemon-supervisor.ts`](file:///home/rocha/Coding/Aether-D-System/vanguard/clients/cli/src) checks if the local Unix Domain Socket exists. If not:
1. It verifies if `python3` and `vanguard-runtime` are present.
2. If absent, it bootstraps an isolated virtual environment in `~/.vanguard/runtime/` via `uv` or `pip`.
3. Spawns `python3 -m vanguard.packages.runtime.service.server` as a detached daemon process.
4. Connects to the socket within 500ms.

---

## 4. Channel 3: Standalone Windows MSI & Linux AppImage

For non-technical enterprise deployment:
1. **Windows Installer (`vanguard-setup.exe` / `.msi`)**:
   * Uses **Tauri** or **Inno Setup** to package a single installer.
   * Embeds the **Python Windows Embedded Package** (`python-3.11-embed-amd64.zip`) and the compiled Node binary.
   * Registers a Windows Service or background Named Pipe listener.
2. **Linux AppImage**:
   * Self-contained image bundling glibc, embedded python libraries, and the UI binary.
