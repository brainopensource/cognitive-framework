from pathlib import Path

def find_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "justfile").exists() and (candidate / "docs").exists(): return candidate
    raise FileNotFoundError("could not discover repository root (expected justfile and docs/)")
