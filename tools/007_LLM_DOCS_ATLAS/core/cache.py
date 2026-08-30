import hashlib, json
from pathlib import Path
from typing import Any

class FileCache:
    def __init__(self, directory: Path) -> None: self.directory = directory
    def key(self, *parts: object) -> str: return hashlib.sha256("\0".join(map(str, parts)).encode()).hexdigest()
    def read(self, key: str) -> Any | None:
        path = self.directory / f"{key}.json"
        try: return json.loads(path.read_text())
        except FileNotFoundError: return None
    def write(self, key: str, value: Any) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        (self.directory / f"{key}.json").write_text(json.dumps(value, sort_keys=True))
