import os
import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_WS_ROOT = os.environ.get("AETHER_WORKSPACE_ROOT", "/home/rocha/Coding/Aether-D-System-Workspace")
os.environ["AETHER_WORKSPACE_ROOT"] = _WS_ROOT
_TMP_DIR = Path(_WS_ROOT) / "tmp"
_TMP_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("TMPDIR", str(_TMP_DIR))
os.environ.setdefault("TMP", str(_TMP_DIR))
os.environ.setdefault("TEMP", str(_TMP_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(_WS_ROOT) / "cache"))
os.environ.setdefault("XDG_STATE_HOME", str(Path(_WS_ROOT) / "state"))
os.environ.setdefault("PYTHONPYCACHEPREFIX", str(Path(_WS_ROOT) / "cache" / "python"))
os.environ.setdefault("npm_config_cache", str(Path(_WS_ROOT) / "cache" / "npm"))
