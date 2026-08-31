import sqlite3
from typing import List, Dict, Any

class SymbolIndexer:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL
            );
        """)
        self.conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS symbols_fts USING fts5 (
                file_path,
                symbol_name,
                docstring
            );
        """)
        self.conn.commit()

    def index_file(self, path: str, symbols: List[Dict[str, str]]):
        self.conn.execute("INSERT OR REPLACE INTO files (path) VALUES (?)", (path,))
        for s in symbols:
            self.conn.execute(
                "INSERT INTO symbols_fts (file_path, symbol_name, docstring) VALUES (?, ?, ?)",
                (path, s["name"], s.get("docstring", ""))
            )
        self.conn.commit()

    def delete_file(self, path: str):
        # BUG: Deletes file from files table, but forgets to purge
        # matching records from symbols_fts table!
        self.conn.execute("DELETE FROM files WHERE path = ?", (path,))
        self.conn.commit()

    def search(self, query: str) -> List[Dict[str, str]]:
        cur = self.conn.execute(
            "SELECT file_path, symbol_name, docstring FROM symbols_fts WHERE symbols_fts MATCH ?",
            (query,)
        )
        return [{"file_path": r[0], "symbol_name": r[1], "docstring": r[2]} for r in cur.fetchall()]
