from __future__ import annotations

import sys
from pathlib import Path
from importlib import import_module

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def main(argv=None):
    return import_module("tools.007_LLM_DOCS_ATLAS.server_mcp").main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
