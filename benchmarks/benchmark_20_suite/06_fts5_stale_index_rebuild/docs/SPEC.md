# Specification: AST Symbol Index Deletion Invariant (IDX-06)

When `delete_file(path)` is executed on `SymbolIndexer`:
1. The record in `files` MUST be removed.
2. All entries in `symbols_fts` associated with `path` MUST be purged completely (`DELETE FROM symbols_fts WHERE file_path = ?`).
3. Subsequent FTS search queries MUST NOT return symbols from the deleted file.
