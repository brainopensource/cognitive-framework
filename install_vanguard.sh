#!/usr/bin/env bash
set -e

# Verifies Python >= 3.10 is installed
if ! command -v python3 &> /dev/null; then
    echo "python3 could not be found. Please install python3 (>=3.10)."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then
    echo "Python >= 3.10 is required. Found $PY_VERSION."
    exit 1
fi

echo "Installing Vanguard CLI to ~/.local/bin/vanguard..."
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$HOME/.local/bin"

cat << EOF > "$HOME/.local/bin/vanguard"
#!/usr/bin/env bash
PYTHONPATH="$REPO_DIR:\$PYTHONPATH" exec /usr/bin/python3 -m vanguard.packages.runtime.cli "\$@"
EOF
chmod +x "$HOME/.local/bin/vanguard"

# Ensures ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Warning: ~/.local/bin is not in your PATH."
    echo "Please add 'export PATH=\"\$HOME/.local/bin:\$PATH\"' to your shell profile."
fi

echo ""
echo "=================================================="
echo "    Vanguard CLI successfully installed!          "
echo "=================================================="
echo ""
echo "Verify installation by running:"
echo "    vanguard --version"
echo "    vanguard --help"
echo ""
