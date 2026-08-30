from dataclasses import dataclass
from pathlib import Path
from .paths import find_root

@dataclass(frozen=True)
class AtlasContext:
    root: Path
    knowledge: Path
    cache: Path
    include_research: bool = False

    @classmethod
    def discover(cls, root: Path | None = None, include_research: bool = False) -> "AtlasContext":
        base = find_root(root)
        return cls(base, base / ".generated" / "knowledge", base / ".generated" / "lda-cache", include_research)
