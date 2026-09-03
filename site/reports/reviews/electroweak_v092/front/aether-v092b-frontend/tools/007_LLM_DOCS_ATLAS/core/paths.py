from pathlib import Path

def find_root(start: Path | None = None) -> Path:
    if start is not None:
        return start.resolve()
    here = Path.cwd().resolve()
    markers = (".git", "pyproject.toml", "package.json", "Cargo.toml", "go.mod", "pom.xml", "build.gradle")
    for candidate in (here, *here.parents):
        if any((candidate / marker).exists() for marker in markers): return candidate
    return here
