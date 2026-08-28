#!/usr/bin/env bash
set -euo pipefail

# Verifies Python >= 3.10 is installed
PYTHON_BIN="${VANGUARD_PYTHON:-python3}"
if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo "python3 could not be found. Please install python3 (>=3.10)."
    exit 1
fi

PY_VERSION=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if ! "$PYTHON_BIN" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then
    echo "Python >= 3.10 is required. Found $PY_VERSION."
    exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_ROOT="${VANGUARD_INSTALL_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/vanguard}"
VENV_DIR="$INSTALL_ROOT/venv"
BIN_DIR="${VANGUARD_BIN_DIR:-$HOME/.local/bin}"
BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/vanguard-wheel.XXXXXX")"
trap 'rm -rf "$BUILD_DIR"' EXIT

if ! "$PYTHON_BIN" -m venv "$VENV_DIR"; then
    echo "Unable to create an isolated Python environment. Install the Python venv module and retry." >&2
    exit 1
fi

echo "Building Vanguard wheel..."
"$PYTHON_BIN" -m pip wheel --no-deps "$REPO_DIR" --wheel-dir "$BUILD_DIR"
WHEEL_PATH="$(find "$BUILD_DIR" -maxdepth 1 -type f -name 'vanguard_runtime-*.whl' -print -quit)"
if [[ -z "$WHEEL_PATH" ]]; then
    echo "Wheel build produced no vanguard-runtime artifact." >&2
    exit 1
fi

echo "Installing Vanguard wheel into $VENV_DIR..."
"$VENV_DIR/bin/python" -m pip install --upgrade "$WHEEL_PATH"
mkdir -p "$BIN_DIR"
for executable in vanguard vanguard-evaluator vanguard-daemon vanguard-studio; do
    ln -sfn "$VENV_DIR/bin/$executable" "$BIN_DIR/$executable"
done

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
echo "    vanguard --help"
echo ""
echo "Uninstall with: $VENV_DIR/bin/python -m pip uninstall vanguard-runtime"
