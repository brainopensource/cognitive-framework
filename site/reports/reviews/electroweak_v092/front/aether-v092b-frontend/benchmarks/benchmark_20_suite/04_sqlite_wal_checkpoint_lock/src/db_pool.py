from pathlib import Path
from .event_store import SqliteEventStore

def get_store(path: Path | str) -> SqliteEventStore:
    return SqliteEventStore(path)
