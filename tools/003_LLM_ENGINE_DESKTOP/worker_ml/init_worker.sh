#!/usr/bin/env bash
# ==============================================================================
# LED ML Worker Isolated Environment Initializer
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

echo "=== [LED ML Worker] Initializing Isolated Python Environment ==="

# Check for uv or python3
if command -v /home/rocha/.local/bin/uv >/dev/null 2>&1; then
    UV_BIN="/home/rocha/.local/bin/uv"
elif command -v uv >/dev/null 2>&1; then
    UV_BIN="uv"
else
    UV_BIN=""
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    if [ -n "$UV_BIN" ]; then
        "$UV_BIN" venv "$VENV_DIR"
    else
        python3 -m venv "$VENV_DIR"
    fi
fi

PYTHON_BIN="$VENV_DIR/bin/python3"

echo "Installing requirements from $SCRIPT_DIR/requirements.txt..."
if [ -n "$UV_BIN" ]; then
    "$UV_BIN" pip install --python "$PYTHON_BIN" -r "$SCRIPT_DIR/requirements.txt"
else
    "$PYTHON_BIN" -m pip install -r "$SCRIPT_DIR/requirements.txt"
fi

echo "Verifying ML packages..."
"$PYTHON_BIN" -c "
import sys
import sklearn
import pandas
import numpy
import ast
import json
print(json.dumps({
    'status': 'ready',
    'python_version': sys.version.split()[0],
    'sklearn_version': sklearn.__version__,
    'pandas_version': pandas.__version__,
    'numpy_version': numpy.__version__
}, indent=2))
"

echo "=== [LED ML Worker] Setup Complete & Verified ==="
