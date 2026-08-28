#!/usr/bin/env bash
set -euo pipefail

# Release qualification is deliberately explicit about the one fact this
# command cannot establish: clean subject and baseline/tag identity require an
# external Git-capable process.  No Git command is run here.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${AETHER_PYTHON:-python3}"

if [[ "$#" -eq 0 ]]; then
    echo "usage: $0 --subject DIGEST --envelope FILE --git-receipt FILE [--json]" >&2
    exit 2
fi

exec "$PYTHON_BIN" "$ROOT_DIR/tools/release_qualification.py" "$@"
